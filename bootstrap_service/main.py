import os
import subprocess
import tempfile
import time
from pathlib import Path

from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel, Field

# ── Config ─────────────────────────────────────────────────────────────────────

BOOTSTRAP_SECRET          = os.environ["BOOTSTRAP_SECRET"]
GITHUB_TOKEN              = os.environ["GITHUB_TOKEN"]
GITHUB_TEMPLATE_OWNER     = os.environ["GITHUB_TEMPLATE_OWNER"]
GITHUB_DEFAULT_OWNER      = os.environ["GITHUB_DEFAULT_OWNER"]
GITHUB_TEMPLATE_REPO_WEB  = os.getenv("GITHUB_TEMPLATE_REPO_WEB", "python-web-template")
RAILWAY_API_TOKEN         = os.environ["RAILWAY_API_TOKEN"]

# ── Schemas ────────────────────────────────────────────────────────────────────

class CreateAppRequest(BaseModel):
    name: str
    template: str
    product_spec: str
    technical_notes: str = ""
    env_vars: dict[str, str] = Field(default_factory=dict)

class CreateAppResponse(BaseModel):
    repo_url: str
    live_url: str
    deploy_status: str
    github_repo_name: str

# ── Helpers ────────────────────────────────────────────────────────────────────

def run(args: list[str], cwd: str | None = None, extra_env: dict | None = None) -> str:
    env = {**os.environ, **(extra_env or {})}
    return subprocess.run(args, capture_output=True, text=True, env=env, check=True, cwd=cwd).stdout.strip()

def auth_clone_url(repo_full_name: str) -> str:
    return f"https://x-access-token:{GITHUB_TOKEN}@github.com/{repo_full_name}.git"

# ── GitHub ─────────────────────────────────────────────────────────────────────

def create_github_repo(name: str) -> dict:
    full_name = f"{GITHUB_DEFAULT_OWNER}/{name}"
    run([
        "gh", "repo", "create", full_name,
        "--template", f"{GITHUB_TEMPLATE_OWNER}/{GITHUB_TEMPLATE_REPO_WEB}",
        "--private",
    ], extra_env={"GH_TOKEN": GITHUB_TOKEN})
    return {"full_name": full_name, "html_url": f"https://github.com/{full_name}"}

def write_files(repo_full_name: str, files: dict[str, str]) -> None:
    time.sleep(3)  # GitHub needs a moment to finish instantiating the template
    git_env = {"GIT_AUTHOR_NAME": "bootstrap", "GIT_AUTHOR_EMAIL": "bootstrap@local",
               "GIT_COMMITTER_NAME": "bootstrap", "GIT_COMMITTER_EMAIL": "bootstrap@local"}
    with tempfile.TemporaryDirectory() as d:
        run(["git", "clone", auth_clone_url(repo_full_name), d])
        for path, content in files.items():
            dest = Path(d) / path
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_text(content)
        run(["git", "add", "."], cwd=d, extra_env=git_env)
        run(["git", "commit", "-m", "Bootstrap initial files"], cwd=d, extra_env=git_env)
        run(["git", "push"], cwd=d, extra_env=git_env)

# ── Railway ────────────────────────────────────────────────────────────────────

def provision_railway(repo_full_name: str, app_name: str, env_vars: dict[str, str]) -> dict:
    renv = {"RAILWAY_TOKEN": RAILWAY_API_TOKEN}
    with tempfile.TemporaryDirectory() as d:
        run(["git", "clone", auth_clone_url(repo_full_name), d])
        run(["railway", "project", "create", "--name", app_name], cwd=d, extra_env=renv)
        for key, value in env_vars.items():
            run(["railway", "variables", "--set", f"{key}={value}"], cwd=d, extra_env=renv)
        run(["railway", "up", "--detach"], cwd=d, extra_env=renv)
        run(["railway", "domain"], cwd=d, extra_env=renv)
    # NOTE: one-time manual step — connect GitHub repo for auto-redeploy:
    #   Railway dashboard → Service → Settings → Source → GitHub → repo → branch main
    return {"live_url": f"https://{app_name}.up.railway.app", "deploy_status": "deploying"}

# ── Generators ─────────────────────────────────────────────────────────────────

def make_readme(name: str, product_spec: str) -> str:
    return f"# {name}\n\n{product_spec}\n"

def make_tech_spec(name: str, notes: str) -> str:
    return f"""# {name} — Technical Spec

Stack: Python / FastAPI / Railway
Endpoints: GET /healthz, GET /
Deployment: Railway autodeploy from main branch

{notes or ""}
""".strip() + "\n"

# ── App ────────────────────────────────────────────────────────────────────────

app = FastAPI(title="Bootstrap Factory")

@app.get("/healthz")
def healthz() -> dict:
    return {"status": "ok"}

@app.post("/create-app", response_model=CreateAppResponse)
def create_app(payload: CreateAppRequest, authorization: str | None = Header(default=None)):
    if authorization != f"Bearer {BOOTSTRAP_SECRET}":
        raise HTTPException(status_code=401, detail="Unauthorized")
    if payload.template != "python-web":
        raise HTTPException(status_code=400, detail="Unsupported template")

    repo = create_github_repo(payload.name)
    write_files(repo["full_name"], {
        "README.md":   make_readme(payload.name, payload.product_spec),
        "TECH_SPEC.md": make_tech_spec(payload.name, payload.technical_notes),
    })
    railway = provision_railway(repo["full_name"], payload.name, payload.env_vars)

    return CreateAppResponse(
        repo_url=repo["html_url"],
        live_url=railway["live_url"],
        deploy_status=railway["deploy_status"],
        github_repo_name=repo["full_name"],
    )
