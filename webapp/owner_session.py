"""owner_session.py | UALP 0.4.1 — signed single-owner TEST sessions.

No access key, personal data or answers are carried in the cookie. Rotation of
UALP_ACCESS_KEY invalidates all sessions; logout removes this browser's cookie.
Stateless sessions are not a multi-user/revocable device registry.
"""
import hashlib
import hmac
import secrets
import time

COOKIE_NAME = "__Host-ualp_session"
SESSION_SECONDS = 30 * 24 * 60 * 60


def signature(payload: str, key: str, audience: str) -> str:
    message = "UALP-owner-session-v1\n" + audience + "\n" + payload
    return hmac.new(key.encode(), message.encode(), hashlib.sha256).hexdigest()


def issue_session(key: str, audience: str) -> str:
    payload = f"{int(time.time()) + SESSION_SECONDS}.{secrets.token_hex(24)}"
    return payload + "." + signature(payload, key, audience)


def valid_session(token: str, key: str, audience: str) -> bool:
    if len(token) > 160:
        return False
    try:
        expiry, nonce, mac = token.split(".")
        if len(nonce) != 48 or len(mac) != 64 or not expiry.isascii() or not expiry.isdigit():
            return False
        now = int(time.time())
        if not now < int(expiry) <= now + SESSION_SECONDS:
            return False
        expected = signature(expiry + "." + nonce, key, audience)
        return hmac.compare_digest(mac, expected)
    except (ValueError, TypeError):
        return False
