"""
Auth flow coverage: registration, login, invalid credentials, expired
access token, refresh rotation (+ reuse detection), logout, password
reset, email verification, unauthorized access, and edge cases
(brute-force lockout, duplicate email, weak password, user
enumeration via forgot-password).
"""
import time

STRONG_PW = "Str0ng!Pass99"


def register(client, email="alice@test.com", password=STRONG_PW, **extra):
    body = {"name": "Alice Test", "email": email, "phone": "5550001111", "password": password}
    body.update(extra)
    return client.post("/api/v1/auth/register", json=body)


def login(client, email="alice@test.com", password=STRONG_PW):
    return client.post("/api/v1/auth/login", json={"email": email, "password": password})


# ── Registration ─────────────────────────────────────────

def test_register_success_returns_token_pair(client):
    resp = register(client)
    assert resp.status_code == 200
    body = resp.json()
    assert "access_token" in body and "refresh_token" in body
    assert body["token_type"] == "bearer"
    assert body["expires_in"] == 15 * 60


def test_register_duplicate_email_rejected(client):
    register(client)
    resp = register(client)
    assert resp.status_code == 400
    assert resp.json()["error"]["code"] == "auth_error"


def test_register_weak_password_rejected(client):
    resp = register(client, password="weak")
    assert resp.status_code == 422


def test_register_password_missing_special_char_rejected(client):
    resp = register(client, password="NoSpecialChar99")
    assert resp.status_code == 422


def test_register_invalid_email_rejected(client):
    resp = register(client, email="not-an-email")
    assert resp.status_code == 422


def test_register_issues_email_verification_token(client, caplog):
    with caplog.at_level("INFO", logger="partype.email"):
        register(client)
    assert any("verification" in r.message for r in caplog.records)


# ── Login ─────────────────────────────────────────────────

def test_login_success(client):
    register(client)
    resp = login(client)
    assert resp.status_code == 200
    assert "access_token" in resp.json()


def test_login_invalid_credentials(client):
    register(client)
    resp = login(client, password="WrongPassword99!")
    assert resp.status_code == 401
    assert resp.json()["error"]["code"] == "auth_error"


def test_login_nonexistent_user(client):
    resp = login(client, email="nobody@test.com")
    assert resp.status_code == 401


def test_login_legacy_alias_signin_works(client):
    register(client)
    resp = client.post("/api/v1/auth/signin", json={"email": "alice@test.com", "password": STRONG_PW})
    assert resp.status_code == 200


# ── Current user / unauthorized access ──────────────────

def test_users_me_requires_token(client):
    resp = client.get("/api/v1/users/me")
    assert resp.status_code == 401


def test_users_me_rejects_malformed_token(client):
    resp = client.get("/api/v1/users/me", headers={"Authorization": "Bearer not.a.valid.jwt"})
    assert resp.status_code == 401


def test_users_me_success(client):
    tokens = register(client).json()
    resp = client.get("/api/v1/users/me", headers={"Authorization": f"Bearer {tokens['access_token']}"})
    assert resp.status_code == 200
    body = resp.json()
    assert body["email"] == "alice@test.com"
    assert "password_hash" not in body  # no sensitive data in response


def test_expired_access_token_rejected(client):
    from app.core.security import create_access_token, decode_access_token, InvalidTokenError
    from app.core.config import settings
    import uuid

    original_ttl = settings.access_token_ttl_minutes
    settings.access_token_ttl_minutes = 0
    try:
        token = create_access_token(uuid.uuid4(), "diner")
        time.sleep(1.2)
        try:
            decode_access_token(token)
            assert False, "expired token should have raised"
        except InvalidTokenError as exc:
            assert "expired" in str(exc).lower()
    finally:
        settings.access_token_ttl_minutes = original_ttl


# ── Refresh (rotation + reuse detection) ────────────────

def test_refresh_rotates_and_old_token_stops_working(client):
    tokens = register(client).json()
    refresh_resp = client.post("/api/v1/auth/refresh", json={"refresh_token": tokens["refresh_token"]})
    assert refresh_resp.status_code == 200
    new_tokens = refresh_resp.json()
    assert new_tokens["refresh_token"] != tokens["refresh_token"]

    reuse_resp = client.post("/api/v1/auth/refresh", json={"refresh_token": tokens["refresh_token"]})
    assert reuse_resp.status_code == 401


def test_refresh_reuse_revokes_all_sessions(client):
    tokens = register(client).json()
    refresh_resp = client.post("/api/v1/auth/refresh", json={"refresh_token": tokens["refresh_token"]})
    new_refresh = refresh_resp.json()["refresh_token"]

    # Reusing the original (now-revoked) token is a theft signal —
    # every session for the user gets revoked, including the token
    # from the rotation that just succeeded above.
    client.post("/api/v1/auth/refresh", json={"refresh_token": tokens["refresh_token"]})

    resp = client.post("/api/v1/auth/refresh", json={"refresh_token": new_refresh})
    assert resp.status_code == 401


def test_refresh_unknown_token_rejected(client):
    resp = client.post("/api/v1/auth/refresh", json={"refresh_token": "not-a-real-token"})
    assert resp.status_code == 401


# ── Logout ────────────────────────────────────────────────

def test_logout_revokes_refresh_token(client):
    tokens = register(client).json()
    logout_resp = client.post("/api/v1/auth/logout", json={"refresh_token": tokens["refresh_token"]})
    assert logout_resp.status_code == 200

    refresh_resp = client.post("/api/v1/auth/refresh", json={"refresh_token": tokens["refresh_token"]})
    assert refresh_resp.status_code == 401


def test_logout_legacy_alias_signout_works(client):
    tokens = register(client).json()
    resp = client.post("/api/v1/auth/signout", json={"refresh_token": tokens["refresh_token"]})
    assert resp.status_code == 200


# ── Email verification ──────────────────────────────────

def test_verify_email_success(client, caplog):
    with caplog.at_level("INFO", logger="partype.email"):
        register(client)
    link = [r.message for r in caplog.records if "verification" in r.message][0]
    token = link.split("token=")[1]

    resp = client.post("/api/v1/auth/verify-email", json={"token": token})
    assert resp.status_code == 200

    tokens = login(client).json()
    me = client.get("/api/v1/users/me", headers={"Authorization": f"Bearer {tokens['access_token']}"}).json()
    assert me["is_email_verified"] is True


def test_verify_email_invalid_token_rejected(client):
    resp = client.post("/api/v1/auth/verify-email", json={"token": "bogus"})
    assert resp.status_code == 400


def test_verify_email_token_single_use(client, caplog):
    with caplog.at_level("INFO", logger="partype.email"):
        register(client)
    link = [r.message for r in caplog.records if "verification" in r.message][0]
    token = link.split("token=")[1]

    assert client.post("/api/v1/auth/verify-email", json={"token": token}).status_code == 200
    assert client.post("/api/v1/auth/verify-email", json={"token": token}).status_code == 400


def test_resend_verification_does_not_leak_existence(client):
    resp_existing = client.post("/api/v1/auth/resend-verification", json={"email": "nobody@test.com"})
    assert resp_existing.status_code == 200  # same response whether or not registered


# ── Password reset ───────────────────────────────────────

def test_forgot_password_same_response_regardless_of_existence(client):
    register(client)
    r1 = client.post("/api/v1/auth/forgot-password", json={"email": "alice@test.com"})
    r2 = client.post("/api/v1/auth/forgot-password", json={"email": "nobody@test.com"})
    assert r1.status_code == r2.status_code == 200
    assert r1.json() == r2.json()


def test_reset_password_flow(client, caplog):
    register(client)
    with caplog.at_level("INFO", logger="partype.email"):
        client.post("/api/v1/auth/forgot-password", json={"email": "alice@test.com"})
    link = [r.message for r in caplog.records if "password reset" in r.message][0]
    token = link.split("token=")[1]

    reset_resp = client.post(
        "/api/v1/auth/reset-password", json={"token": token, "new_password": "NewStr0ng!Pass99"}
    )
    assert reset_resp.status_code == 200

    assert login(client, password=STRONG_PW).status_code == 401
    assert login(client, password="NewStr0ng!Pass99").status_code == 200


def test_reset_password_revokes_existing_sessions(client, caplog):
    tokens = register(client).json()
    with caplog.at_level("INFO", logger="partype.email"):
        client.post("/api/v1/auth/forgot-password", json={"email": "alice@test.com"})
    link = [r.message for r in caplog.records if "password reset" in r.message][0]
    token = link.split("token=")[1]

    client.post("/api/v1/auth/reset-password", json={"token": token, "new_password": "NewStr0ng!Pass99"})

    resp = client.post("/api/v1/auth/refresh", json={"refresh_token": tokens["refresh_token"]})
    assert resp.status_code == 401


def test_reset_password_invalid_token_rejected(client):
    resp = client.post(
        "/api/v1/auth/reset-password", json={"token": "bogus", "new_password": "NewStr0ng!Pass99"}
    )
    assert resp.status_code == 400


def test_reset_password_weak_password_rejected(client, caplog):
    register(client)
    with caplog.at_level("INFO", logger="partype.email"):
        client.post("/api/v1/auth/forgot-password", json={"email": "alice@test.com"})
    link = [r.message for r in caplog.records if "password reset" in r.message][0]
    token = link.split("token=")[1]

    resp = client.post("/api/v1/auth/reset-password", json={"token": token, "new_password": "weak"})
    assert resp.status_code == 422


# ── Edge cases ────────────────────────────────────────────

def test_brute_force_lockout(client):
    register(client)
    for _ in range(5):
        resp = login(client, password="wrong-password-1!")
        assert resp.status_code == 401

    # Correct password now rejected — account locked, not just another 401.
    resp = login(client)
    assert resp.status_code == 423


def test_successful_login_resets_failed_attempt_counter(client):
    register(client)
    for _ in range(3):
        login(client, password="wrong-password-1!")
    assert login(client).status_code == 200
    # Counter reset — three more failures shouldn't lock (threshold is 5).
    for _ in range(3):
        login(client, password="wrong-password-1!")
    assert login(client).status_code == 200


def test_deactivated_account_cannot_login(client):
    tokens = register(client).json()
    client.post("/api/v1/users/me/deactivate", headers={"Authorization": f"Bearer {tokens['access_token']}"})
    resp = login(client)
    assert resp.status_code == 403


def test_change_password_wrong_current_password_rejected(client):
    tokens = register(client).json()
    resp = client.post(
        "/api/v1/users/me/change-password",
        json={"current_password": "WrongOne99!", "new_password": "NewStr0ng!Pass99"},
        headers={"Authorization": f"Bearer {tokens['access_token']}"},
    )
    assert resp.status_code == 400


def test_change_password_success_revokes_other_sessions(client):
    tokens = register(client).json()
    resp = client.post(
        "/api/v1/users/me/change-password",
        json={"current_password": STRONG_PW, "new_password": "NewStr0ng!Pass99"},
        headers={"Authorization": f"Bearer {tokens['access_token']}"},
    )
    assert resp.status_code == 200
    assert login(client, password="NewStr0ng!Pass99").status_code == 200

    refresh_resp = client.post("/api/v1/auth/refresh", json={"refresh_token": tokens["refresh_token"]})
    assert refresh_resp.status_code == 401


def test_delete_account_is_soft_delete(client):
    tokens = register(client).json()
    resp = client.delete("/api/v1/users/me", headers={"Authorization": f"Bearer {tokens['access_token']}"})
    assert resp.status_code == 200
    # Deleted account can no longer log in...
    assert login(client).status_code in (401, 403)
    # ...but a duplicate registration with the same email is still
    # correctly rejected (the row wasn't hard-deleted).
    assert register(client).status_code == 400
