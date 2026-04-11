import os
from functools import lru_cache

import jwt
import requests
from fastapi import Header, HTTPException

# ── Machine-to-machine ──────────────────────────────────────────────────────────

APP_SECRET = os.environ.get("APP_SECRET", "")


def require_app_secret(x_app_secret: str | None = Header(default=None)) -> None:
    if not APP_SECRET:
        raise HTTPException(status_code=500, detail="APP_SECRET not configured")
    if x_app_secret != APP_SECRET:
        raise HTTPException(status_code=401, detail="Unauthorized")


# ── Human access (Cloudflare Access + Google OAuth) ────────────────────────────

CLOUDFLARE_AUD  = os.environ.get("CLOUDFLARE_AUD", "")
CLOUDFLARE_TEAM = os.environ.get("CLOUDFLARE_TEAM", "")


@lru_cache(maxsize=1)
def _cf_public_keys() -> list:
    url = f"https://{CLOUDFLARE_TEAM}.cloudflareaccess.com/cdn-cgi/access/certs"
    return requests.get(url, timeout=10).json()["keys"]


def require_cf_auth(cf_access_jwt_assertion: str | None = Header(default=None)) -> dict:
    if not CLOUDFLARE_AUD or not CLOUDFLARE_TEAM:
        raise HTTPException(status_code=500, detail="Cloudflare Access not configured")
    if not cf_access_jwt_assertion:
        raise HTTPException(status_code=401, detail="Missing Cloudflare Access token")
    try:
        payload = jwt.decode(
            cf_access_jwt_assertion,
            options={"verify_signature": True},
            algorithms=["RS256"],
            audience=CLOUDFLARE_AUD,
            jwks=_cf_public_keys(),
        )
    except Exception:
        raise HTTPException(status_code=403, detail="Invalid Cloudflare Access token")
    return payload  # contains email, name, etc.
