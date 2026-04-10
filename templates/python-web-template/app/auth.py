import os
from fastapi import Header, HTTPException

APP_SECRET = os.environ.get("APP_SECRET", "")


def require_app_secret(x_app_secret: str | None = Header(default=None)) -> None:
    if not APP_SECRET:
        raise HTTPException(status_code=500, detail="APP_SECRET not configured")
    if x_app_secret != APP_SECRET:
        raise HTTPException(status_code=401, detail="Unauthorized")
