# Bootstrap

Spinning up a new app by hand means creating a GitHub repo, writing boilerplate, setting up Railway, wiring Cloudflare Access — before writing a single line of product code. This service does all of that in one call.

## How it works

Call `/create-app` from Claude Code with an app name, template, and product description. The service:

1. Creates a private GitHub repo from the chosen template
2. Writes a generated `README.md` and `IMPLEMENTATION.md` into the repo
3. Provisions a Railway project, injects env vars, and deploys
4. Creates a Cloudflare Access Application — Google OAuth gated, email allowlist in `access.yaml`
5. Returns the repo URL, live URL, and `app_secret` for M2M calls

## Setup

See [INIT.md](INIT.md) for the full one-time setup (GitHub, Railway, Cloudflare, Google OAuth).

```bash
./setup.sh
# fill in bootstrap_service/.env
cd bootstrap_service && source .venv/bin/activate
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
    "allowed_emails": ["you@gmail.com"]
  }'
```

```json
{
  "repo_url": "https://github.com/you/my-tool",
  "live_url": "https://my-tool.up.railway.app",
  "deploy_status": "deploying",
  "github_repo_name": "you/my-tool",
  "app_secret": "<generated>"
}
```

Open `live_url` → Google login → in immediately.

## Environment variables

| Variable | Purpose |
|---|---|
| `GITHUB_TOKEN` | PAT with `repo` scope |
| `RAILWAY_API_TOKEN` | Railway token |
| `CLOUDFLARE_API_TOKEN` | Token with Access: Apps and Policies → Edit |
| `CLOUDFLARE_ACCOUNT_ID` | Cloudflare account ID |
| `CLOUDFLARE_TEAM` | Zero Trust team name |
| `GITHUB_DEFAULT_OWNER` | Optional — defaults to authenticated GitHub user |

## Templates

- `python-web` — FastAPI, Cloudflare JWT + app secret auth, Railway deploy
- `python-task` — Click CLI, cron-friendly, Railway deploy
- `telegram-bot` — python-telegram-bot with `/start` and echo handler
