# Bootstrap

## Problem

Spinning up a new app by hand means creating a GitHub repo, writing boilerplate, setting up Railway, wiring them together — before writing a single line of product code. This service does all of that in one call.

## How it works

Call `/create-app` from Claude Code with an app name, template, and product description. The service:

1. Creates a private GitHub repo from the chosen template
2. Writes a generated `README.md` and `TECH_SPEC.md` into the repo
3. Provisions a Railway project, injects env vars, and deploys
4. Returns the repo URL and live URL

After that: edit the repo, push, Railway redeploys automatically.

> **One manual step:** after first deploy, connect the Railway service to the GitHub repo for auto-redeploy.
> Railway dashboard → Service → Settings → Source → GitHub → select repo → branch `main`.

## Setup

```bash
./setup.sh
```

Fill in `bootstrap_service/.env` with your credentials, then:

```bash
cd bootstrap_service
source .venv/bin/activate
uvicorn main:app --reload --port 8000
```

## Usage

```bash
curl -X POST http://localhost:8000/create-app \
  -H "Content-Type: application/json" \
  -d '{
    "name": "my-tool",
    "template": "python-web",
    "product_spec": "Internal dashboard for tracking deployments.",
    "env_vars": {"APP_SECRET": "replace-me"}
  }'
```

```json
{
  "repo_url": "https://github.com/you/my-tool",
  "live_url": "https://my-tool.up.railway.app",
  "deploy_status": "deploying",
  "github_repo_name": "you/my-tool"
}
```

## Environment variables

| Variable | Purpose |
|---|---|
| `GITHUB_TOKEN` | PAT with `repo` scope |
| `GITHUB_DEFAULT_OWNER` | Optional — owner for newly created repos; defaults to the authenticated user |
| `RAILWAY_API_TOKEN` | Railway token |

## Templates

- `python-web` — FastAPI app, `/healthz`, `railway.toml`, auth scaffold (`templates/python-web-template/`)
- `python-task` — Minimal Python script, `railway.toml` with `python task/main.py` start command (`templates/python-task-template/`)
- `telegram-bot` — python-telegram-bot app with `/start` and echo handler, `railway.toml` (`templates/telegram-bot-template/`)
