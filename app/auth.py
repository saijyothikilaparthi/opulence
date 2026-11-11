"""JWT authentication and admin route protection.

The admin console and admin-only APIs are protected by a signed JWT stored in an
HttpOnly cookie. Tokens are verified on every admin request; no server-side
session store is required.
"""

import os
import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional

import jwt
from fastapi import Request
from fastapi.responses import JSONResponse, RedirectResponse

JWT_ALGORITHM = "HS256"
ADMIN_COOKIE_NAME = "opulence_admin"
ADMIN_LOGIN_PATH = "/admin/login"

# Endpoints that must stay reachable without a session.
PUBLIC_ADMIN_PATHS = {
    "/admin/login",
    "/api/admin/login",
    "/api/admin/logout",
}

# Admin console and order data that is not public.
ADMIN_EXACT_PATHS = {"/admin", "/admin/", "/api/orders", "/api/orders/"}


def _truthy(value: str) -> bool:
    return str(value).strip().lower() in {"1", "true", "yes", "on"}


def admin_auth_enabled() -> bool:
    return _truthy(os.getenv("ADMIN_AUTH_ENABLED", "true"))


def _jwt_secret() -> str:
    secret = os.getenv("JWT_SECRET", "").strip()
    if not secret:
        raise RuntimeError("JWT_SECRET is not set. Add it to .env before using the admin console.")
    return secret


def _token_minutes() -> int:
    try:
        return max(1, int(os.getenv("JWT_EXPIRE_MINUTES", "480")))
    except ValueError:
        return 480


def _cookie_secure() -> bool:
    return _truthy(os.getenv("COOKIE_SECURE", "false"))


def verify_credentials(username: str, password: str) -> bool:
    expected_username = os.getenv("ADMIN_USERNAME", "")
    expected_password = os.getenv("ADMIN_PASSWORD", "")
    if not expected_username or not expected_password:
        return False
    return secrets.compare_digest(
        str(username).encode("utf-8"), expected_username.encode("utf-8")
    ) and secrets.compare_digest(
        str(password).encode("utf-8"), expected_password.encode("utf-8")
    )


def create_access_token(username: str) -> tuple[str, int]:
    minutes = _token_minutes()
    now = datetime.now(timezone.utc)
    payload = {
        "sub": username,
        "role": "admin",
        "iat": now,
        "exp": now + timedelta(minutes=minutes),
    }
    token = jwt.encode(payload, _jwt_secret(), algorithm=JWT_ALGORITHM)
    return token, minutes


def decode_access_token(token: str) -> Optional[str]:
    if not token:
        return None
    try:
        payload = jwt.decode(token, _jwt_secret(), algorithms=[JWT_ALGORITHM])
    except jwt.InvalidTokenError:
        return None
    if payload.get("role") != "admin":
        return None
    username = payload.get("sub")
    return username if isinstance(username, str) and username else None


def set_admin_cookie(response, token: str, minutes: int) -> None:
    response.set_cookie(
        key=ADMIN_COOKIE_NAME,
        value=token,
        max_age=minutes * 60,
        httponly=True,
        secure=_cookie_secure(),
        samesite="strict",
        path="/",
    )


def clear_admin_cookie(response) -> None:
    response.delete_cookie(
        key=ADMIN_COOKIE_NAME,
        path="/",
        secure=_cookie_secure(),
        httponly=True,
        samesite="strict",
    )


def is_admin_path(path: str) -> bool:
    if path in PUBLIC_ADMIN_PATHS:
        return False
    if path in ADMIN_EXACT_PATHS:
        return True
    if path.startswith("/admin/"):
        return True
    if path.startswith("/api/admin/"):
        return True
    # Any API route with an /admin segment (e.g. /api/enquiries/admin, /api/admin/hampers).
    if "/admin" in path:
        return True
    # Creating an order from an enquiry is an admin action even though it is not under /admin.
    if path.startswith("/api/orders/from-enquiry/"):
        return True
    return False


def _wants_html(path: str) -> bool:
    return path == "/admin" or path.startswith("/admin/")


async def admin_auth_middleware(request: Request, call_next):
    if request.method == "OPTIONS" or not admin_auth_enabled() or not is_admin_path(request.url.path):
        return await call_next(request)

    username = decode_access_token(request.cookies.get(ADMIN_COOKIE_NAME, ""))
    if username:
        request.state.admin_username = username
        return await call_next(request)

    if _wants_html(request.url.path):
        return RedirectResponse(url=ADMIN_LOGIN_PATH, status_code=303)
    return JSONResponse(status_code=401, content={"detail": "Authentication required"})
