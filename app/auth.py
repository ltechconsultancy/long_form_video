import os
import secrets
from fastapi import Request, HTTPException
from fastapi.responses import RedirectResponse

# Hardcoded credentials - change these!
AUTH_USERNAME = os.getenv("AUTH_USERNAME", "admin")
AUTH_PASSWORD = os.getenv("AUTH_PASSWORD", "longformvideo123")

# Session token storage (in-memory, resets on restart)
valid_sessions: set[str] = set()


def create_session() -> str:
    token = secrets.token_urlsafe(32)
    valid_sessions.add(token)
    return token


def verify_session(token: str) -> bool:
    return token in valid_sessions


def logout(token: str):
    valid_sessions.discard(token)


def get_current_user(request: Request) -> str | None:
    token = request.cookies.get("session")
    if token and verify_session(token):
        return AUTH_USERNAME
    return None


def require_auth(request: Request):
    if not get_current_user(request):
        raise HTTPException(status_code=401, detail="Not authenticated")
