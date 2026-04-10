import os
import secrets
import shutil
import subprocess
import tempfile
from pathlib import Path

import requests as http_client
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

# ── Config ─────────────────────────────────────────────────────────────────────

GITHUB_TOKEN          = os.environ["GITHUB_TOKEN"]
RAILWAY_API_TOKEN     = os.environ["RAILWAY_API_TOKEN"]
CLOUDFLARE_API_TOKEN  = os.environ["CLOUDFLARE_API_TOKEN"]
CLOUDFLARE_ACCOUNT_ID = os.environ["CLOUDFLARE_ACCOUNT_ID"]
CLOUDFLARE_TEAM       = os.environ["CLOUDFLARE_TEAM"]
OWNER_EMAIL           = os.environ["OWNER_EMAIL"]

def _resolve_github_owner() -> str:
    override = os.environ.get("GITHUB_DEFAULT_OWNER", "")
    if override:
        return override
    return subprocess.run(
        ["gh", "api", "user", "--jq", ".login"],
        capture_output=True, text=True, check=True,
        env={**os.environ, "GH_TOKEN": GITHUB_TOKEN},
    ).stdout.strip()

GITHUB_DEFAULT_OWNER = _resolve_github_owner()

TEMPLATES_DIR = Path(__file__).parent.parent / "templates"

TEMPLATE_MAP = {
    "python-web":    TEMPLATES_DIR / "python-web-template",
    "python-task":   TEMPLATES_DIR / "python-task-template",
    "telegram-bot":  TEMPLATES_DIR / "telegram-bot-template",
}

# ── Schemas ────────────────────────────────────────────────────────────────────

class CreateAppRequest(BaseModel):
    name: str
    template: str
    product_spec: str
    technical_notes: str = ""
    env_vars: dict[str, str] = Field(default_factory=dict)
    allowed_emails: list[str] = Field(default_factory=list)

class CreateAppResponse(BaseModel):
    repo_url: str
    live_url: str
    deploy_status: str
    github_repo_name: str
    app_secret: str

# ── Helpers ────────────────────────────────────────────────────────────────────

def run(args: list[str], cwd: str | None = None, extra_env: dict | None = None) -> str:
    env = {**os.environ, **(extra_env or {})}
    return subprocess.run(args, capture_output=True, text=True, env=env, check=True, cwd=cwd).stdout.strip()

def auth_clone_url(repo_full_name: str) -> str:
    return f"https://x-access-token:{GITHUB_TOKEN}@github.com/{repo_full_name}.git"

# ── GitHub ─────────────────────────────────────────────────────────────────────

def create_github_repo(name: str) -> dict:
    full_name = f"{GITHUB_DEFAULT_OWNER}/{name}"
    run(["gh", "repo", "create", full_name, "--private"],
        extra_env={"GH_TOKEN": GITHUB_TOKEN})
    return {"full_name": full_name, "html_url": f"https://github.com/{full_name}"}

def delete_github_repo(full_name: str) -> None:
    try:
        run(["gh", "repo", "delete", full_name, "--yes"],
            extra_env={"GH_TOKEN": GITHUB_TOKEN})
    except Exception:
        pass  # best-effort cleanup

def set_github_secrets(repo_full_name: str, repo_secrets: dict[str, str]) -> None:
    for key, value in repo_secrets.items():
        run(["gh", "secret", "set", key, "--body", value, "--repo", repo_full_name],
            extra_env={"GH_TOKEN": GITHUB_TOKEN})

def populate_dir(d: str, template: str, generated_files: dict[str, str]) -> None:
    code_template = TEMPLATE_MAP[template]
    repo_template = TEMPLATES_DIR / "github-repo-template"
    shutil.copytree(str(repo_template), d, dirs_exist_ok=True)
    shutil.copytree(str(code_template), d, dirs_exist_ok=True)
    for path, content in generated_files.items():
        dest = Path(d) / path
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(content)

def push_to_github(d: str, repo_full_name: str) -> None:
    git_env = {"GIT_AUTHOR_NAME": "bootstrap", "GIT_AUTHOR_EMAIL": "bootstrap@local",
               "GIT_COMMITTER_NAME": "bootstrap", "GIT_COMMITTER_EMAIL": "bootstrap@local"}
    run(["git", "init"], cwd=d, extra_env=git_env)
    run(["git", "symbolic-ref", "HEAD", "refs/heads/main"], cwd=d)
    run(["git", "remote", "add", "origin", auth_clone_url(repo_full_name)], cwd=d)
    run(["git", "add", "."], cwd=d, extra_env=git_env)
    run(["git", "commit", "-m", "Bootstrap initial files"], cwd=d, extra_env=git_env)
    run(["git", "push", "-u", "origin", "main"], cwd=d, extra_env=git_env)

# ── Railway ────────────────────────────────────────────────────────────────────

def provision_railway(d: str, app_name: str, env_vars: dict[str, str]) -> dict:
    renv = {"RAILWAY_TOKEN": RAILWAY_API_TOKEN}
    run(["railway", "project", "create", "--name", app_name], cwd=d, extra_env=renv)
    for key, value in env_vars.items():
        run(["railway", "variables", "--set", f"{key}={value}"], cwd=d, extra_env=renv)
    run(["railway", "up", "--detach"], cwd=d, extra_env=renv)
    domain = run(["railway", "domain"], cwd=d, extra_env=renv)
    live_url = (
        domain if domain.startswith("http")
        else f"https://{domain}" if domain
        else f"https://{app_name}.up.railway.app"
    )
    # NOTE: one-time manual step — connect GitHub repo for auto-redeploy:
    #   Railway dashboard → Service → Settings → Source → GitHub → repo → branch main
    return {"live_url": live_url, "deploy_status": "deploying", "renv": renv}

def set_railway_vars(d: str, renv: dict, vars: dict[str, str]) -> None:
    for key, value in vars.items():
        run(["railway", "variables", "--set", f"{key}={value}"], cwd=d, extra_env=renv)

# ── Cloudflare ─────────────────────────────────────────────────────────────────

def provision_cloudflare(app_name: str, live_url: str, allowed_emails: list[str]) -> dict:
    headers = {
        "Authorization": f"Bearer {CLOUDFLARE_API_TOKEN}",
        "Content-Type": "application/json",
    }
    base = f"https://api.cloudflare.com/client/v4/accounts/{CLOUDFLARE_ACCOUNT_ID}"

    resp = http_client.post(f"{base}/access/apps", headers=headers, json={
        "name": app_name,
        "domain": live_url.removeprefix("https://"),
        "type": "self_hosted",
        "session_duration": "24h",
    })
    resp.raise_for_status()
    result = resp.json()["result"]
    app_id = result["id"]
    aud    = result["aud"]

    resp = http_client.post(f"{base}/access/apps/{app_id}/policies", headers=headers, json={
        "name": "Allow list",
        "decision": "allow",
        "include": [{"email": {"email": e}} for e in allowed_emails],
    })
    resp.raise_for_status()
    policy_id = resp.json()["result"]["id"]

    return {"app_id": app_id, "policy_id": policy_id, "aud": aud}

# ── Generators ─────────────────────────────────────────────────────────────────

def make_readme(name: str, product_spec: str) -> str:
    return f"# {name}\n\n{product_spec}\n"

def make_implementation(name: str, notes: str) -> str:
    return f"""# Implementation Spec

Generated by bootstrap. Fill in sections as you build.

## Stack

- Python / Railway
{notes and f'- {notes}' or ''}

## Agent

[Define agent flows here.]

## Data

[Define schemas here.]

## Auth

[Define auth model here.]

## Security

- Secrets in Railway env vars
- Repo is private by default
"""

def make_access_yaml(allowed_emails: list[str]) -> str:
    lines = [
        "# Who can log in to this app.",
        "# Add or remove emails here and push to main — access updates automatically.",
        "allowed_emails:",
    ]
    for email in allowed_emails:
        lines.append(f"  - {email}")
    return "\n".join(lines) + "\n"

# ── App ────────────────────────────────────────────────────────────────────────

app = FastAPI(title="Bootstrap Factory")

@app.get("/healthz")
def healthz() -> dict:
    return {"status": "ok"}

@app.post("/create-app", response_model=CreateAppResponse)
def create_app(payload: CreateAppRequest):
    if payload.template not in TEMPLATE_MAP:
        raise HTTPException(status_code=400, detail=f"Unknown template. Choose from: {list(TEMPLATE_MAP)}")

    app_secret = secrets.token_hex(32)
    allowed    = list({OWNER_EMAIL} | set(payload.allowed_emails))
    repo = create_github_repo(payload.name)
    try:
        with tempfile.TemporaryDirectory() as d:
            populate_dir(d, payload.template, {
                "README.md":         make_readme(payload.name, payload.product_spec),
                "IMPLEMENTATION.md": make_implementation(payload.name, payload.technical_notes),
                "access.yaml":       make_access_yaml(allowed),
            })
            push_to_github(d, repo["full_name"])

            railway = provision_railway(d, payload.name, {
                **payload.env_vars,
                "APP_SECRET": app_secret,
            })

            cf = provision_cloudflare(payload.name, railway["live_url"], allowed)

            set_railway_vars(d, railway["renv"], {
                "CLOUDFLARE_AUD":  cf["aud"],
                "CLOUDFLARE_TEAM": CLOUDFLARE_TEAM,
            })

        set_github_secrets(repo["full_name"], {
            "CLOUDFLARE_API_TOKEN":  CLOUDFLARE_API_TOKEN,
            "CLOUDFLARE_ACCOUNT_ID": CLOUDFLARE_ACCOUNT_ID,
            "CLOUDFLARE_APP_ID":     cf["app_id"],
            "CLOUDFLARE_POLICY_ID":  cf["policy_id"],
        })

    except Exception:
        delete_github_repo(repo["full_name"])
        raise

    return CreateAppResponse(
        repo_url=repo["html_url"],
        live_url=railway["live_url"],
        deploy_status=railway["deploy_status"],
        github_repo_name=repo["full_name"],
        app_secret=app_secret,
    )
