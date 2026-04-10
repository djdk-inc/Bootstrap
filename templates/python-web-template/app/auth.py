from fastapi import Header, HTTPException
from app.settings import settings


def require_app_secret(x_app_secret: str | None = Header(default=None)) -> None:
    if not settings.app_secret:
        raise HTTPException(status_code=500, detail="APP_SECRET not configured")

    if x_app_secret != settings.app_secret:
        raise HTTPException(status_code=401, detail="Unauthorized")
