# API Reference

Base URL: `/api/v1` (canonical). `/api` serves the identical routes as a legacy alias — see `docs/ARCHITECTURE.md#api-versioning`.

Interactive docs (Swagger UI): `http://localhost:8000/docs`
OpenAPI schema: `http://localhost:8000/openapi.json`

## Auth

Full flow, rationale, and rate limits: `docs/AUTHENTICATION.md`.

| Method | Path | Auth | Description |
|---|---|---|---|
| POST | `/auth/register` (alias: `/auth/signup`) | — | Create account. Returns `{access_token, refresh_token, token_type, expires_in, token}`. |
| POST | `/auth/login` (alias: `/auth/signin`) | — | Same response shape as register. |
| POST | `/auth/logout` (alias: `/auth/signout`) | — | Body: `{refresh_token}`. Revokes it. |
| POST | `/auth/refresh` | — | Body: `{refresh_token}`. Rotates — returns a new pair, revokes the old one. |
| POST | `/auth/verify-email` | — | Body: `{token}`. |
| POST | `/auth/resend-verification` | — | Body: `{email}`. Always the same response regardless of whether the email exists. |
| POST | `/auth/forgot-password` | — | Body: `{email}`. Always the same response regardless of whether the email exists. |
| POST | `/auth/reset-password` | — | Body: `{token, new_password}`. Revokes all of that user's refresh tokens. |
| GET | `/users/me` | Bearer | Current user profile. Never includes `password_hash` or lockout fields. |

`token` (in register/login/refresh responses) is the same value as `access_token` — kept for `frontend/legacy-spa/index.html`, which reads that field name.

Auth is `Authorization: Bearer <access_token>` — a short-lived (15 min) JWT. `/auth/login` and `/auth/register` are rate-limited (5/min/IP); five failed logins for one account locks it for 15 minutes regardless of IP (see `docs/AUTHENTICATION.md`).

## Users

| Method | Path | Auth | Description |
|---|---|---|---|
| PATCH | `/users/me` | Bearer | Body: `{name?, avatar_url?}`. |
| POST | `/users/me/change-password` | Bearer | Body: `{current_password, new_password}`. Revokes all other sessions. |
| POST | `/users/me/deactivate` | Bearer | Sets `is_active=false`, revokes all sessions, blocks login (403). |
| DELETE | `/users/me` | Bearer | Soft delete (`deleted_at`) — see `docs/DATABASE.md` and `docs/AUTHENTICATION.md`. |

## Error responses

Every error (auth failures, validation, not-found, rate-limited, etc.) uses the same envelope:
```json
{"error": {"code": "auth_error", "message": "Invalid credentials"}}
```

## Restaurants

| Method | Path | Auth | Description |
|---|---|---|---|
| GET | `/restaurants?skip=&limit=&cuisine=` | — | List, paginated, optional cuisine filter. |
| GET | `/restaurants/{id}` | — | Detail. |
| GET | `/restaurants/{id}/menu` | — | Available menu items. |
| GET | `/restaurants/{id}/tables` | — | Tables. |

## Dining sessions

| Method | Path | Auth | Description |
|---|---|---|---|
| POST | `/sessions` | — | Create a dining session; host auto-joins as participant. |
| GET | `/sessions/{id}` | — | Detail. |
| POST | `/sessions/join/{code}` | Bearer | Join by session code. |
| GET | `/sessions/{id}/participants` | — | List participants. |

## Orders

| Method | Path | Auth | Description |
|---|---|---|---|
| POST | `/orders` | — | Create an order with nested `order_items`. |
| GET | `/orders/{id}` | — | Detail. |
| GET | `/orders/user/{user_id}` | — | Orders for a user, newest first. |
| PATCH | `/orders/{id}/status` | — | Update status (`pending` → `confirmed` → `preparing` → `ready` → `delivered`, or `cancelled`). |

## Wallet

| Method | Path | Auth | Description |
|---|---|---|---|
| GET | `/wallet` | Bearer | `{balance, transactions}`. |
| POST | `/wallet/topup` | Bearer | Amount must be `0 < amount <= 50000`. |
| POST | `/wallet/pay` | Bearer | Debits if sufficient balance, else 400. |

## Notifications

| Method | Path | Auth | Description |
|---|---|---|---|
| GET | `/notifications` | Bearer | Newest first. |
| POST | `/notifications/read-all` | Bearer | Marks all as read. |

## Merchant

| Method | Path | Auth | Description |
|---|---|---|---|
| GET | `/merchant/orders?restaurant_id=&limit=` | — | Orders for a restaurant. |
| GET | `/merchant/tables?restaurant_id=` | — | Tables for a restaurant. |
| PATCH | `/merchant/tables/{id}/status` | — | Body: `{"status": "available"\|"occupied"\|"reserved"\|"billing"}`. |
| GET | `/merchant/analytics?restaurant_id=` | — | Revenue/order aggregates. |

None of the merchant/waiter routes are role-gated yet at the API layer — see `docs/MIGRATION_PLAN.md` Phase 3.
