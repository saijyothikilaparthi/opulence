"""Login, logout and session endpoints for the admin console."""

import time
from collections import defaultdict

from fastapi import APIRouter, HTTPException, Request, Response, status
from pydantic import BaseModel

from app.auth import (
    clear_admin_cookie,
    create_access_token,
    set_admin_cookie,
    verify_credentials,
)

router = APIRouter(prefix="/api/admin", tags=["Admin Auth"])

# Simple in-memory brute-force protection for a single-instance deployment.
MAX_FAILED_ATTEMPTS = 5
LOCKOUT_SECONDS = 15 * 60
_failed_attempts: dict[str, list[float]] = defaultdict(list)


class LoginRequest(BaseModel):
    username: str
    password: str


def _client_ip(request: Request) -> str:
    return request.client.host if request.client else "unknown"


def _is_rate_limited(ip: str) -> bool:
    now = time.monotonic()
    recent = [t for t in _failed_attempts[ip] if now - t < LOCKOUT_SECONDS]
    _failed_attempts[ip] = recent
    return len(recent) >= MAX_FAILED_ATTEMPTS


def _record_failure(ip: str) -> None:
    _failed_attempts[ip].append(time.monotonic())


def _clear_failures(ip: str) -> None:
    _failed_attempts.pop(ip, None)


@router.post("/login", status_code=status.HTTP_200_OK)
def login(payload: LoginRequest, request: Request, response: Response):
    ip = _client_ip(request)
    if _is_rate_limited(ip):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many failed attempts. Please try again in 15 minutes.",
        )

    if not verify_credentials(payload.username, payload.password):
        _record_failure(ip)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )

    _clear_failures(ip)
    token, minutes = create_access_token(payload.username)
    set_admin_cookie(response, token, minutes)
    return {
        "success": True,
        "message": "Signed in successfully",
        "user": {"username": payload.username},
    }


@router.post("/logout", status_code=status.HTTP_200_OK)
def logout(response: Response):
    clear_admin_cookie(response)
    return {"success": True, "message": "Signed out successfully"}


@router.get("/me", status_code=status.HTTP_200_OK)
def current_admin(request: Request):
    username = getattr(request.state, "admin_username", None)
    if not username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
        )
    return {"success": True, "user": {"username": username}}
