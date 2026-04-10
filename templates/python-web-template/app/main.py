from fastapi import FastAPI, Depends
from app.auth import require_app_secret

app = FastAPI(title="Python Web Template")


@app.get("/healthz")
def healthz() -> dict:
    return {"status": "ok"}


@app.get("/")
def root(_: None = Depends(require_app_secret)) -> dict:
    return {"message": "App is running"}
