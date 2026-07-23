"""
OAuth utilities for Google and Apple ID token verification.
"""
import json
import time

import jwt
import requests
from jwt.algorithms import RSAAlgorithm, ECAlgorithm

from app.core.config import settings

# Cache for JWKS to avoid hitting the network on every request
_JWKS_CACHE: dict[str, tuple[float, dict]] = {}  # {url: (expiry_timestamp, jwks)}
_JWKS_CACHE_TTL = 3600  # 1 hour


def _get_jwks(jwks_uri: str) -> dict:
    """Fetch JWKS from the given URI, with caching."""
    now = time.time()
    if jwks_uri in _JWKS_CACHE:
        expiry, jwks = _JWKS_CACHE[jwks_uri]
        if now < expiry:
            return jwks
    # Fetch fresh
    resp = requests.get(jwks_uri, timeout=5)
    resp.raise_for_status()
    jwks = resp.json()
    _JWKS_CACHE[jwks_uri] = (now + _JWKS_CACHE_TTL, jwks)
    return jwks


def _verify_id_token(
    token: str,
    jwks_uri: str,
    audience: str,
    issuer: str,
) -> dict:
    """
    Verify a signed ID token using the provider's JWKS.
    Returns the decoded claims if valid.
    Raises jwt.PyJWTError on failure.
    """
    # Get the kid from the token header
    header = jwt.get_unverified_header(token)
    kid = header.get("kid")
    if not kid:
        raise jwt.InvalidTokenError("Token missing kid header")

    jwks = _get_jwks(jwks_uri)
    # Find the key with matching kid
    key_dict = None
    for key in jwks.get("keys", []):
        if key.get("kid") == kid:
            key_dict = key
            break
    if not key_dict:
        raise jwt.InvalidTokenError("Unable to find matching key")

    # Construct the public key based on the algorithm
    alg = header.get("alg")
    if alg == "RS256":
        # RSA key
        public_key = RSAAlgorithm.from_jwk(json.dumps(key_dict))
    elif alg == "ES256":
        # EC key
        public_key = ECAlgorithm.from_jwk(json.dumps(key_dict))
    else:
        raise jwt.InvalidTokenError(f"Unsupported algorithm: {alg}")

    # Verify the token
    payload = jwt.decode(
        token,
        key=public_key,
        algorithms=[alg],
        audience=audience,
        issuer=issuer,
    )
    return payload


def verify_google_id_token(id_token: str) -> dict:
    """
    Verify a Google ID token.
    Returns the user's email, name, picture, and sub (Google user ID).
    """
    # Google's OAuth 2.0 certs endpoint
    JWKS_URI = "https://www.googleapis.com/oauth2/v3/certs"
    # For Google, the audience is the client ID (web client ID)
    # We'll expect the frontend to send the client ID? Actually, we can
    # ignore audience verification if we trust that only our app can
    # obtain tokens for our client ID. But we should verify.
    # We'll set the expected audience from settings.
    GOOGLE_CLIENT_ID = getattr(settings, "google_client_id", None)
    if not GOOGLE_CLIENT_ID:
        raise RuntimeError("Google client ID not configured")
    return _verify_id_token(
        id_token,
        jwks_uri=JWKS_URI,
        audience=GOOGLE_CLIENT_ID,
        issuer="https://accounts.google.com",
    )


def verify_apple_id_token(id_token: str) -> dict:
    """
    Verify an Apple ID token.
    Returns the user's email, name, and sub (Apple user ID).
    """
    JWKS_URI = "https://appleid.apple.com/auth/keys"
    # Apple's audience is the client ID (services ID)
    APPLE_CLIENT_ID = getattr(settings, "apple_client_id", None)
    if not APPLE_CLIENT_ID:
        raise RuntimeError("Apple client ID not configured")
    return _verify_id_token(
        id_token,
        jwks_uri=JWKS_URI,
        audience=APPLE_CLIENT_ID,
        issuer="https://appleid.apple.com",
    )