"""
OAuth verification utilities.
"""

def verify_google_id_token(id_token: str) -> dict:
    """Verify Google ID token and return user info."""
    # For development, return a dummy user.
    # In production, this should verify the token with Google's servers.
    return {
        "email": "test@example.com",
        "name": "Test User",
        "sub": "1234567890",
    }


def verify_apple_id_token(id_token: str) -> dict:
    """Verify Apple ID token and return user info."""
    # For development, return a dummy user.
    # In production, this should verify the token with Apple's servers.
    return {
        "email": "test@example.com",
        "name": "Test User",
        "sub": "1234567890",
    }