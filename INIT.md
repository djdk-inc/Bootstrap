# Bootstrap — Initial Setup

Everything you need to do once before Bootstrap can provision apps end-to-end.

---

## 1. Prerequisites

Install the required CLI tools:

```bash
# GitHub CLI
brew install gh

# Railway CLI
npm install -g @railway/cli

# Python 3.11+
brew install python
```

Authenticate each:

```bash
gh auth login
railway login
```

---

## 2. GitHub

Create a Personal Access Token with `repo` scope:

1. GitHub → Settings → Developer Settings → Personal Access Tokens → Fine-grained tokens
2. Permissions: **Contents** (read/write), **Metadata** (read), **Administration** (read/write)
3. Copy the token → `GITHUB_TOKEN` in `.env`

---

## 3. Railway

1. Create a Railway account at [railway.app](https://railway.app)
2. Railway dashboard → Account Settings → Tokens → New Token
3. Copy the token → `RAILWAY_API_TOKEN` in `.env`

---

## 4. Cloudflare — one-time setup

This is the only step that requires manual UI work. Do it once; after this Bootstrap handles everything via API.

### 4a. Cloudflare account

Create or log into a Cloudflare account at [cloudflare.com](https://cloudflare.com).

### 4b. Enable Zero Trust

Cloudflare dashboard → Zero Trust → Get started. Choose a team name (e.g. `yourname`). This becomes `CLOUDFLARE_TEAM` in `.env`.

Free plan covers up to 50 users — sufficient for personal use.

### 4c. Connect Google as identity provider

**Cloudflare IdP settings:** https://dash.cloudflare.com/ced7308a086c99e265bda33237acbaca/one/integrations/identity-providers/edit/dfc447b5-93b0-462e-862a-8c44a4ab9516

Integrations → Identity providers → Add → Google.

You will need a Google OAuth client for this step only:

1. **Google Cloud Console credentials:** https://console.cloud.google.com/auth/clients?project=djdk-inc
2. Create Credentials → OAuth 2.0 Client ID → Web application
3. Authorized redirect URI: `https://djdk-inc.cloudflareaccess.com/cdn-cgi/access/callback`
4. Copy the **Client ID** (ends in `.apps.googleusercontent.com`) and **Client Secret** → paste into Cloudflare App ID + Client secret fields

Note: Google credentials can take up to a few hours to propagate after creation.

This is the only time you touch Google Cloud Console. All future apps authenticate through Cloudflare; Google never sees them individually.

### 4d. Create a Cloudflare API token

Cloudflare dashboard → My Profile → API Tokens → Create Token.

Use the **Edit Cloudflare Workers** template as a starting point, then:
- Add permission: **Access: Apps and Policies** → Edit
- Scope: your account

Copy the token → `CLOUDFLARE_API_TOKEN` in `.env`.

Also copy your **Account ID** from the right sidebar of any Cloudflare dashboard page → `CLOUDFLARE_ACCOUNT_ID` in `.env`.

---

## 5. Fill in `.env`

Run `./setup.sh` to create the file, then fill it in:

```bash
GITHUB_TOKEN=
RAILWAY_API_TOKEN=
CLOUDFLARE_API_TOKEN=
CLOUDFLARE_ACCOUNT_ID=
CLOUDFLARE_TEAM=
# GITHUB_DEFAULT_OWNER=   # optional: defaults to authenticated GitHub user
```

---

## 6. Start the service

```bash
cd bootstrap_service
source .venv/bin/activate
uvicorn main:app --reload --port 8000
```

---

## 7. Verify

```bash
curl http://localhost:8000/healthz
# {"status": "ok"}
```

Then test a full provision:

```bash
curl -X POST http://localhost:8000/create-app \
  -H "Content-Type: application/json" \
  -d '{
    "name": "test-app",
    "template": "python-web",
    "product_spec": "Test app to verify Bootstrap provisioning."
  }'
```

Expected response: `repo_url`, `live_url` (Cloudflare-protected), `deploy_status: "deploying"`.

Open `live_url` → Google login prompt → you're in.
