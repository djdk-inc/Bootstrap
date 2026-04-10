# Bootstrap

Below is a copy-pastable build spec you can hand to Claude Code or Codex.

````md
# Project: Phone-First App Bootstrap Factory

## Problem Statement

I want a system where I can use Claude Code from my phone to describe an app idea, and have that trigger a private bootstrap system that:

1. Creates a new GitHub repository from a template
2. Generates initial product and technical documentation
3. Generates initial application code
4. Provisions and configures Railway deployment
5. Connects GitHub to Railway for automatic rebuild + redeploy on future commits
6. Returns a live URL and repo URL
7. Lets Claude Code continue iterating on the app by editing the repo, committing changes, and relying on Railway auto-redeploys

This is not true local hot reload. The goal is responsive cloud rebuild + redeploy on commit.

The system must be private-by-default, secure, and designed so that Claude Code does not directly hold raw GitHub or Railway credentials. Instead, a bootstrap service should hold the sensitive credentials and expose a narrow authenticated tool interface.

---

## Desired End State

The development loop should look like this:

Claude Code on phone
-> authenticated call to private bootstrap service
-> bootstrap service creates repo from template
-> bootstrap service generates or writes initial files
-> bootstrap service provisions Railway project/service/env/domain
-> Railway deploys app
-> live URL returned
-> Claude Code continues modifying repo over time
-> each new commit triggers Railway rebuild + redeploy

---

## Core Design Principles

1. Keep the first version simple
   - no Kubernetes
   - no Terraform for v1
   - no GitHub Actions in the main deploy path
   - Railway should watch the repo directly

2. Separate responsibilities cleanly
   - Claude Code: planning, specs, code generation, repo edits
   - Bootstrap service: provisioning, credentials, GitHub/Railway wiring
   - GitHub: source of truth
   - Railway: runtime + deployment engine

3. Private-by-default
   - apps should ship with auth enabled by default
   - bootstrap service should be private and authenticated
   - Claude should never receive raw provider credentials in prompts

4. Prefer delegated identity at user-facing boundaries
   - use OAuth/OIDC between Claude Code and bootstrap service
   - use GitHub App auth for GitHub automation
   - use Railway OAuth or scoped Railway token for Railway automation

---

# Solution Outline

## High-Level Architecture

There are four major parts:

1. Claude Code client workflow
2. Private bootstrap service
3. GitHub template repositories
4. Railway deployment integration

### Full flow

1. User asks Claude Code to create a new app
2. Claude Code prepares product spec, technical spec, and app definition
3. Claude Code calls a private authenticated bootstrap tool
4. Bootstrap service creates a new repo from the appropriate template
5. Bootstrap service writes the generated files into the new repo
6. Bootstrap service provisions Railway and links it to the repo
7. Bootstrap service sets environment variables and auth defaults
8. Bootstrap service returns repo URL, deployment URL, and status
9. Claude Code can then continue editing the repo
10. Railway rebuilds + redeploys on future commits automatically

---

# Technical Outline

## Component 1: Bootstrap Service

### Purpose

The bootstrap service is the secure control plane. It is responsible for all sensitive provider interactions and infrastructure wiring.

### Responsibilities

- authenticate incoming requests from Claude Code
- accept a request to create a new app
- choose the correct template
- create a new GitHub repo from a template
- commit generated files into the new repo
- provision Railway project/service/environment/domain
- set Railway variables
- return status and URLs
- optionally support future update/status actions

### Recommended implementation

- Language: Python
- Framework: FastAPI
- Deploy it on Railway, Fly.io, or another small trusted host
- Expose either:
  - a remote MCP server interface, or
  - a narrow HTTPS API
- Preferred long-term interface: remote MCP server
- Preferred auth between Claude Code and bootstrap service: OAuth/OIDC
- Fast MVP auth option: bearer token
- Long-term GitHub auth: GitHub App
- Railway auth: OAuth token or scoped Railway API token

### Bootstrap service environment variables

At minimum:

- `GITHUB_APP_ID`
- `GITHUB_APP_PRIVATE_KEY`
- `GITHUB_INSTALLATION_ID`
- `RAILWAY_API_TOKEN` or Railway OAuth credentials
- `GOOGLE_OIDC_ISSUER` or other IdP config for user auth
- `ALLOWED_USER_EMAIL`
- `TEMPLATE_OWNER`
- `TEMPLATE_WEB_REPO`
- `TEMPLATE_WORKER_REPO`
- `TEMPLATE_TELEGRAM_REPO`
- `DEFAULT_RAILWAY_TEAM_OR_PROJECT`
- `BOOTSTRAP_BASE_DOMAIN` if needed

### Bootstrap service API / tool surface

The system should support at least these operations:

#### `create_app`
Creates a brand-new app end to end.

Input shape:

- `name`: app name / repo name
- `template`: one of `python-web`, `python-worker`, `telegram-bot`
- `product_spec`: user-facing product description
- `technical_notes`: optional constraints
- `env_refs`: optional env var names / placeholders
- `auth_mode`: default app auth strategy
- `visibility`: private internal default
- `railway_config`: optional deployment options

Output shape:

- `repo_url`
- `default_branch`
- `railway_project_id`
- `railway_service_id`
- `live_url`
- `deploy_status`
- `next_steps`

#### `update_app`
Optional but useful later.

- applies code changes or file changes
- commits to the repo
- returns commit SHA and deployment status

#### `get_app_status`
Returns current deployment and repo status.

- latest commit
- latest deployment state
- live URL
- healthcheck result

### Internal bootstrap flow for `create_app`

1. Validate caller auth
2. Validate request payload
3. Select template repo
4. Create new private GitHub repo from template
5. Clone or write files into repo
6. Generate/update:
   - `README.md`
   - `TECH_SPEC.md`
   - app code
   - `.env.example`
   - `railway.toml`
7. Commit and push initial code
8. Create Railway project/service
9. Link Railway service to GitHub repo/branch
10. Set Railway variables
11. Optionally attach domain / volume / cron worker config
12. Trigger first deploy if needed
13. Poll or fetch deployment status
14. Return result

---

## Component 2: Bootstrap Repo Templates

There should be a small catalog of template repositories.

### Recommended initial templates

1. `python-web-template`
2. `python-worker-template`
3. `telegram-bot-template`

These template repos should already contain the structure, conventions, and deployment contract Claude will build on top of.

### Shared template goals

Every template should:

- be deployable on Railway
- be private-by-default
- use env vars only for secrets/config
- include healthcheck support
- include docs skeletons
- have a standard repo contract so Claude can reliably edit them

---

## Component 3: Web App Template

### Repo structure

```text
/
  README.md
  TECH_SPEC.md
  railway.toml
  requirements.txt
  .env.example
  app/
    main.py
    auth.py
    settings.py
````

### Example responsibilities

* simple FastAPI web app
* `/healthz` endpoint
* default authenticated access
* single-service deployment
* explicit start command for Railway

### Suggested file contents

#### `README.md`

Should contain:

* app name
* product overview
* target users
* features
* current scope
* usage notes

#### `TECH_SPEC.md`

Should contain:

* stack
* architecture
* endpoints
* env vars
* deployment assumptions
* auth mode

#### `.env.example`

Should contain placeholders such as:

* `APP_SECRET=`
* `OPENAI_API_KEY=`
* `TELEGRAM_BOT_TOKEN=`

#### `railway.toml`

Should define:

* build system
* start command
* healthcheck path

Example:

```toml
[build]
builder = "NIXPACKS"

[deploy]
startCommand = "uvicorn app.main:app --host 0.0.0.0 --port $PORT"
healthcheckPath = "/healthz"
```

#### `requirements.txt`

```txt
fastapi
uvicorn
```

#### `app/main.py`

Should expose:

* `/healthz`
* `/`
* later app-specific routes

#### `app/auth.py`

Should provide default app-level guardrails.
For v1 this can be a simple secret-based check or basic auth middleware.
Long-term it can evolve to magic link or OAuth.

#### `app/settings.py`

Centralized env var loading.

---

## Component 4: Worker / Script Template

Use this when the app is not primarily a web UI.

### Repo structure

```text
/
  README.md
  TECH_SPEC.md
  railway.toml
  requirements.txt
  .env.example
  worker/
    main.py
```

### Use cases

* scheduled jobs
* data processing
* background agents
* polling tasks

### Railway deployment modes

Can be configured as:

* long-running worker
* cron job
* HTTP-triggered task service

---

## Component 5: Telegram Bot Template

Use this for a bot-first control surface.

### Repo structure

```text
/
  README.md
  TECH_SPEC.md
  railway.toml
  requirements.txt
  .env.example
  bot/
    main.py
    handlers.py
```

### Use cases

* phone-native control
* alerts
* message-driven workflows
* bot UI

### Default env vars

* `TELEGRAM_BOT_TOKEN`
* `APP_SECRET`
* optional model/provider keys

### Deployment mode

* webhook-based bot on Railway

---

## Component 6: Auth Model

### A. Claude Code -> Bootstrap Service

Preferred:

* remote MCP server with OAuth/OIDC
* login via Google or another trusted identity provider
* bootstrap service validates token and checks allowed identity claims

This is the user-facing trust boundary.

Fast MVP:

* bearer token
* later upgrade to OAuth

### B. Bootstrap Service -> GitHub

Preferred:

* GitHub App
* short-lived installation tokens
* narrow permissions
* better than a broad personal access token

### C. Bootstrap Service -> Railway

Use:

* Railway OAuth if acting on behalf of user, or
* scoped Railway API token for simpler backend automation

### D. Generated App -> User

Private-by-default app auth:

* basic auth
* secret header
* allowlisted email
* Telegram user allowlist
* later evolve to full user auth if needed

---

## Component 7: Railway Integration

### Railway should be the primary deploy engine

Avoid putting GitHub Actions in the middle of the deploy loop for v1.

Desired behavior:

* connect Railway directly to the GitHub repo and branch
* every commit to tracked branch triggers rebuild + redeploy

### Railway provisioning responsibilities

The bootstrap service should handle:

* creating project/service
* connecting repo
* selecting tracked branch
* setting variables
* assigning domain
* optionally configuring volumes/cron/jobs

### Important design note

This is not local hot reload.
This is fast hosted rebuild + redeploy on commit.

---

## Component 8: Claude Code Workflow

Claude Code should be instructed to do two kinds of work:

### A. Bootstrap phase work

Before calling bootstrap:

* write `README.md`
* write `TECH_SPEC.md`
* generate app code
* define env vars
* select the right template
* prepare concise `create_app` payload

### B. Ongoing development work

After bootstrap:

* edit repo files
* add features
* fix bugs
* update docs
* commit changes
* rely on Railway redeploy

### Claude behavior prompt pattern

Claude should follow this general sequence:

1. Understand requested app
2. Decide template
3. Generate/refresh docs first
4. Generate code
5. Call bootstrap
6. Return URLs and status
7. Continue development through repo edits and commits

---

# Solution Fit Together

## End-to-End Lifecycle

### First app creation

1. User describes app in Claude Code on phone
2. Claude produces initial product + technical spec
3. Claude calls bootstrap service
4. Bootstrap service creates repo from template
5. Bootstrap service writes generated content
6. Bootstrap service provisions Railway
7. Railway deploys
8. User receives live URL and repo URL

### Ongoing development

1. User asks Claude to add/change something
2. Claude edits repository contents
3. Claude commits to tracked branch
4. Railway rebuilds and redeploys automatically
5. User sees updated live app

---

# Concrete Requirements for the Implementation

## Build the bootstrap service with:

* Python + FastAPI
* remote MCP or HTTPS API interface
* authenticated access
* GitHub App integration
* Railway integration
* endpoints/tools:

  * `create_app`
  * `update_app`
  * `get_app_status`

## Build at least one repo template:

* `python-web-template`
* FastAPI
* `README.md`
* `TECH_SPEC.md`
* `.env.example`
* `railway.toml`
* `/healthz`
* default auth scaffold

## Ensure these guarantees:

* private repo by default
* secrets never committed
* Railway auto-redeploy on commit
* narrow credential exposure
* Claude only calls bootstrap tool, not raw provider APIs directly

---

# Recommended Initial Scope

## v1

Ship only this:

* one bootstrap service
* one `python-web-template`
* one authenticated bootstrap tool
* GitHub repo creation from template
* Railway project/service setup
* env var injection
* auto-redeploy on commit

## v2

Add:

* worker template
* Telegram bot template
* richer app auth
* status polling
* branch previews
* richer update tool

## v3

Add:

* app registry dashboard
* template catalog
* multi-environment management
* optional GitHub Actions for tests/smoke checks only

---

# Prompt To Give Claude Code / Codex

Build an end-to-end phone-first app bootstrap system with the following properties:

1. A private bootstrap service acts as the secure control plane
2. Claude Code should call the bootstrap service through a narrow authenticated tool interface
3. The bootstrap service must:

   * create private GitHub repos from templates
   * write generated README.md and TECH_SPEC.md
   * write generated application code
   * configure Railway deployment
   * connect GitHub repo to Railway for automatic rebuild + redeploy on future commits
   * set Railway environment variables
   * return repo URL and live URL
4. Start with one template: `python-web-template`
5. The template must include:

   * FastAPI app
   * `/healthz`
   * `README.md`
   * `TECH_SPEC.md`
   * `.env.example`
   * `railway.toml`
   * default auth scaffold
6. Use this architecture:

   * Claude Code = specs + code generation + repo edits
   * Bootstrap service = provisioning + credentials + wiring
   * GitHub = source of truth
   * Railway = deployment engine
7. Use this auth model:

   * Claude Code -> bootstrap service: OAuth/OIDC preferred, bearer token acceptable for MVP
   * bootstrap service -> GitHub: GitHub App
   * bootstrap service -> Railway: Railway OAuth or scoped Railway API token
8. The main deployment loop should be:

   * Claude generates app
   * bootstrap provisions app
   * Railway deploys
   * Claude continues editing repo
   * Railway auto-redeploys on new commits
9. This is not local hot reload. It is fast hosted rebuild + redeploy on commit.
10. Produce:

* bootstrap service code
* template repo contents
* tool/API contract
* example request/response payloads
* instructions for local development and deployment

Prioritize simplicity and end-to-end functionality over overengineering.

````

And here is a shorter version you can paste as the actual implementation brief:

```md
Build a phone-first app bootstrap factory.

Goal:
From Claude Code on my phone, I want to describe an app and have a private bootstrap system create a GitHub repo from a template, generate initial docs/code, provision Railway, connect the repo for automatic rebuild + redeploy on future commits, and return a live URL. After that, Claude should continue editing the repo and Railway should redeploy on every commit.

Architecture:
- Claude Code: writes specs/code, edits repo over time
- Bootstrap service: secure control plane for provisioning
- GitHub: source of truth
- Railway: deployment engine

Auth:
- Claude Code -> bootstrap service: OAuth/OIDC preferred; bearer token acceptable for MVP
- bootstrap service -> GitHub: GitHub App
- bootstrap service -> Railway: Railway OAuth or scoped API token

Bootstrap service responsibilities:
- create private repo from template
- generate/write README.md
- generate/write TECH_SPEC.md
- generate/write app code
- configure Railway project/service/env/domain
- connect GitHub repo to Railway tracked branch
- return repo URL and live URL

Initial template:
- python-web-template
- FastAPI app
- /healthz endpoint
- railway.toml
- .env.example
- README.md
- TECH_SPEC.md
- auth scaffold

Key behavior:
- not true hot reload
- fast hosted rebuild + redeploy on commit
- private-by-default
- secrets never committed
- narrow tool interface instead of giving Claude raw provider credentials

Required outputs:
- bootstrap service implementation
- template repo implementation
- API/tool contract
- example payloads
- setup instructions
````

If you want, I can turn this next into a **fully scaffolded file tree with starter code for the bootstrap service and the first template repo**.













Perfect. Here’s a **copy-pastable scaffold pack** you can hand straight to Claude Code / Codex.

---

# 1) Target file tree

```text
bootstrap-factory/
├── README.md
├── bootstrap_service/
│   ├── requirements.txt
│   ├── main.py
│   ├── config.py
│   ├── schemas.py
│   ├── github_client.py
│   ├── railway_client.py
│   └── generators.py
└── templates/
    └── python-web-template/
        ├── README.md
        ├── TECH_SPEC.md
        ├── railway.toml
        ├── requirements.txt
        ├── .env.example
        └── app/
            ├── main.py
            ├── auth.py
            └── settings.py
```

---

# 2) Implementation brief to give Claude Code / Codex

```md
Build an end-to-end phone-first app bootstrap factory.

The system has two main parts:

1. A private bootstrap service
2. A python-web template repo

The bootstrap service must:
- expose an authenticated API
- accept a request to create a new app
- create a new private GitHub repo from a template
- write generated README.md and TECH_SPEC.md
- write generated application files
- configure Railway deployment
- connect the GitHub repo to Railway for automatic rebuild + redeploy on future commits
- set Railway variables
- return repo URL, live URL, and deployment status

Architecture:
- Claude Code = specs + code generation + ongoing repo edits
- Bootstrap service = provisioning + credentials + wiring
- GitHub = source of truth
- Railway = deployment engine

Important:
- this is not true hot reload
- this is hosted rebuild + redeploy on commit
- apps should be private-by-default
- secrets must never be committed
- Claude Code must not directly hold GitHub or Railway provider credentials

Auth:
- MVP: bearer token between Claude Code and bootstrap service
- Better later: OAuth/OIDC remote MCP server
- GitHub automation: GitHub App preferred
- Railway automation: scoped Railway token or Railway OAuth

The first template must be:
- python-web-template
- FastAPI app
- /healthz endpoint
- railway.toml
- .env.example
- README.md
- TECH_SPEC.md
- default auth scaffold

Produce:
- working bootstrap service scaffold
- working template scaffold
- clear TODO comments where API integration details go
- example request/response payloads
- setup instructions
```

---

# 3) Root README.md

```md
# Bootstrap Factory

A phone-first app bootstrap system.

## Goal

From Claude Code on a phone:

1. Describe an app idea
2. Trigger a private bootstrap service
3. Create a private GitHub repo from a template
4. Generate initial docs and code
5. Provision Railway deployment
6. Return a live URL
7. Continue iterating through Claude Code commits
8. Railway automatically rebuilds + redeploys on each commit

## Architecture

Claude Code
-> Bootstrap Service
-> GitHub Template Repo
-> Railway
-> Live URL

## Components

- `bootstrap_service/` - private control plane
- `templates/python-web-template/` - starter app template

## Notes

This is not local hot reload.
This is fast hosted rebuild + redeploy on commit.

## Security Model

- Claude talks only to bootstrap service
- bootstrap service holds provider credentials
- app secrets live in Railway variables
- repos are private by default
```

---

# 4) bootstrap_service/requirements.txt

```txt
fastapi
uvicorn
httpx
pydantic
python-dotenv
```

---

# 5) bootstrap_service/config.py

```python
from pydantic import BaseModel
import os


class Settings(BaseModel):
    bootstrap_secret: str = os.getenv("BOOTSTRAP_SECRET", "")
    github_token: str = os.getenv("GITHUB_TOKEN", "")
    github_template_owner: str = os.getenv("GITHUB_TEMPLATE_OWNER", "")
    github_template_repo_web: str = os.getenv("GITHUB_TEMPLATE_REPO_WEB", "python-web-template")
    github_default_owner: str = os.getenv("GITHUB_DEFAULT_OWNER", "")
    railway_api_token: str = os.getenv("RAILWAY_API_TOKEN", "")
    railway_team_id: str = os.getenv("RAILWAY_TEAM_ID", "")


settings = Settings()
```

---

# 6) bootstrap_service/schemas.py

```python
from typing import Dict, Optional, Literal
from pydantic import BaseModel, Field


TemplateType = Literal["python-web"]


class CreateAppRequest(BaseModel):
    name: str = Field(..., description="Repository and app name")
    template: TemplateType = Field(..., description="Template type")
    product_spec: str = Field(..., description="Human-readable product spec")
    technical_notes: Optional[str] = Field(default="", description="Optional technical constraints")
    env_vars: Dict[str, str] = Field(default_factory=dict, description="Initial Railway env vars")
    auth_mode: str = Field(default="basic", description="App auth mode")


class CreateAppResponse(BaseModel):
    repo_url: str
    live_url: str
    deploy_status: str
    github_repo_name: str
    railway_project_id: Optional[str] = None
    railway_service_id: Optional[str] = None
```

---

# 7) bootstrap_service/generators.py

```python
def generate_readme(app_name: str, product_spec: str) -> str:
    return f"""# {app_name}

## Product Spec
{product_spec}

## Features
- Initial scaffold generated by bootstrap service
- Railway deployment
- FastAPI app
- Private-by-default starter

## Notes
This app is intended to be iterated on by Claude Code after bootstrap.
"""


def generate_tech_spec(app_name: str, technical_notes: str) -> str:
    return f"""# Technical Specification

## App
{app_name}

## Stack
- Python
- FastAPI
- Railway

## Architecture
- Single-service app
- Stateless HTTP service
- Environment-based config

## Endpoints
- GET /healthz
- GET /

## Deployment
- Railway autodeploy from GitHub tracked branch

## Notes
{technical_notes or "No additional technical notes provided."}
"""
```

---

# 8) bootstrap_service/github_client.py

```python
from typing import Dict
import httpx


class GitHubClient:
    def __init__(self, token: str, template_owner: str, default_owner: str):
        self.token = token
        self.template_owner = template_owner
        self.default_owner = default_owner
        self.base_url = "https://api.github.com"

    @property
    def headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }

    async def create_repo_from_template(self, template_repo: str, new_repo_name: str, private: bool = True) -> Dict:
        url = f"{self.base_url}/repos/{self.template_owner}/{template_repo}/generate"
        payload = {
            "owner": self.default_owner,
            "name": new_repo_name,
            "private": private,
            "include_all_branches": False,
        }
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(url, headers=self.headers, json=payload)
            response.raise_for_status()
            return response.json()

    async def create_or_update_file(
        self,
        owner: str,
        repo: str,
        path: str,
        content_b64: str,
        message: str,
        branch: str = "main",
        sha: str | None = None,
    ) -> Dict:
        url = f"{self.base_url}/repos/{owner}/{repo}/contents/{path}"
        payload = {
            "message": message,
            "content": content_b64,
            "branch": branch,
        }
        if sha:
            payload["sha"] = sha

        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.put(url, headers=self.headers, json=payload)
            response.raise_for_status()
            return response.json()

    async def get_file_sha(self, owner: str, repo: str, path: str, branch: str = "main") -> str | None:
        url = f"{self.base_url}/repos/{owner}/{repo}/contents/{path}?ref={branch}"
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(url, headers=self.headers)
            if response.status_code == 404:
                return None
            response.raise_for_status()
            data = response.json()
            return data.get("sha")
```

---

# 9) bootstrap_service/railway_client.py

```python
from typing import Dict, Any
import httpx


class RailwayClient:
    """
    Minimal placeholder GraphQL client.

    Replace the TODO GraphQL documents with the exact mutations/queries
    you want to use for:
    - create project
    - create service from repo
    - set variables
    - fetch deployment status
    """

    def __init__(self, api_token: str, team_id: str):
        self.api_token = api_token
        self.team_id = team_id
        self.url = "https://backboard.railway.com/graphql/v2"

    @property
    def headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json",
        }

    async def gql(self, query: str, variables: Dict[str, Any]) -> Dict[str, Any]:
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(
                self.url,
                headers=self.headers,
                json={"query": query, "variables": variables},
            )
            response.raise_for_status()
            payload = response.json()
            if "errors" in payload:
                raise RuntimeError(payload["errors"])
            return payload["data"]

    async def provision_app(self, repo_full_name: str, app_name: str) -> Dict[str, str]:
        """
        TODO: Replace with real Railway API integration.

        Suggested steps:
        1. Create project
        2. Create service linked to GitHub repo
        3. Set tracked branch = main
        4. Fetch generated live URL / domain
        """
        return {
            "project_id": "railway-project-placeholder",
            "service_id": "railway-service-placeholder",
            "live_url": f"https://{app_name}.up.railway.app",
            "deploy_status": "provisioning",
        }

    async def set_variables(self, project_id: str, environment_id: str, variables: Dict[str, str]) -> None:
        """
        TODO: implement Railway variable-setting mutation.
        """
        return None
```

---

# 10) bootstrap_service/main.py

```python
import base64
from fastapi import FastAPI, Header, HTTPException
from config import settings
from schemas import CreateAppRequest, CreateAppResponse
from github_client import GitHubClient
from railway_client import RailwayClient
from generators import generate_readme, generate_tech_spec

app = FastAPI(title="Bootstrap Factory")


def require_auth(authorization: str | None) -> None:
    expected = f"Bearer {settings.bootstrap_secret}"
    if not authorization or authorization != expected:
        raise HTTPException(status_code=401, detail="Unauthorized")


@app.get("/healthz")
async def healthz() -> dict:
    return {"status": "ok"}


@app.post("/create-app", response_model=CreateAppResponse)
async def create_app(payload: CreateAppRequest, authorization: str | None = Header(default=None)):
    require_auth(authorization)

    if payload.template != "python-web":
        raise HTTPException(status_code=400, detail="Unsupported template")

    github = GitHubClient(
        token=settings.github_token,
        template_owner=settings.github_template_owner,
        default_owner=settings.github_default_owner,
    )
    railway = RailwayClient(
        api_token=settings.railway_api_token,
        team_id=settings.railway_team_id,
    )

    template_repo = settings.github_template_repo_web
    repo_data = await github.create_repo_from_template(
        template_repo=template_repo,
        new_repo_name=payload.name,
        private=True,
    )

    owner = repo_data["owner"]["login"]
    repo = repo_data["name"]
    repo_url = repo_data["html_url"]
    repo_full_name = repo_data["full_name"]

    readme = generate_readme(payload.name, payload.product_spec)
    tech_spec = generate_tech_spec(payload.name, payload.technical_notes or "")

    for path, content in {
        "README.md": readme,
        "TECH_SPEC.md": tech_spec,
    }.items():
        sha = await github.get_file_sha(owner, repo, path)
        encoded = base64.b64encode(content.encode("utf-8")).decode("utf-8")
        await github.create_or_update_file(
            owner=owner,
            repo=repo,
            path=path,
            content_b64=encoded,
            message=f"Bootstrap {path}",
            branch="main",
            sha=sha,
        )

    railway_info = await railway.provision_app(
        repo_full_name=repo_full_name,
        app_name=payload.name,
    )

    return CreateAppResponse(
        repo_url=repo_url,
        live_url=railway_info["live_url"],
        deploy_status=railway_info["deploy_status"],
        github_repo_name=repo_full_name,
        railway_project_id=railway_info["project_id"],
        railway_service_id=railway_info["service_id"],
    )
```

---

# 11) templates/python-web-template/README.md

```md
# {{APP_NAME}}

## Product Spec
{{PRODUCT_SPEC}}

## Features
- FastAPI starter app
- Railway deployment
- Healthcheck endpoint
- Private-by-default scaffold

## Usage
Update this file during bootstrap and ongoing development.
```

---

# 12) templates/python-web-template/TECH_SPEC.md

```md
# Technical Specification

## Stack
- Python
- FastAPI
- Railway

## Architecture
- Single service
- Stateless HTTP app
- Env-driven configuration

## Endpoints
- GET /healthz
- GET /

## Notes
Update this file during bootstrap and ongoing development.
```

---

# 13) templates/python-web-template/railway.toml

```toml
[build]
builder = "NIXPACKS"

[deploy]
startCommand = "uvicorn app.main:app --host 0.0.0.0 --port $PORT"
healthcheckPath = "/healthz"
```

---

# 14) templates/python-web-template/requirements.txt

```txt
fastapi
uvicorn
```

---

# 15) templates/python-web-template/.env.example

```env
APP_SECRET=
OPENAI_API_KEY=
```

---

# 16) templates/python-web-template/app/settings.py

```python
import os


class Settings:
    app_secret: str = os.getenv("APP_SECRET", "")


settings = Settings()
```

---

# 17) templates/python-web-template/app/auth.py

```python
from fastapi import Header, HTTPException
from app.settings import settings


def require_app_secret(x_app_secret: str | None = Header(default=None)) -> None:
    if not settings.app_secret:
        raise HTTPException(status_code=500, detail="APP_SECRET not configured")

    if x_app_secret != settings.app_secret:
        raise HTTPException(status_code=401, detail="Unauthorized")
```

---

# 18) templates/python-web-template/app/main.py

```python
from fastapi import FastAPI, Depends
from app.auth import require_app_secret

app = FastAPI(title="Python Web Template")


@app.get("/healthz")
def healthz() -> dict:
    return {"status": "ok"}


@app.get("/")
def root(_: None = Depends(require_app_secret)) -> dict:
    return {"message": "App is running"}
```

---

# 19) Local run commands

## Bootstrap service

```bash
cd bootstrap_service
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export BOOTSTRAP_SECRET=supersecret
export GITHUB_TOKEN=ghp_xxx
export GITHUB_TEMPLATE_OWNER=YOUR_GITHUB_USERNAME_OR_ORG
export GITHUB_DEFAULT_OWNER=YOUR_GITHUB_USERNAME_OR_ORG
export GITHUB_TEMPLATE_REPO_WEB=python-web-template
export RAILWAY_API_TOKEN=railway_xxx
export RAILWAY_TEAM_ID=team_xxx
uvicorn main:app --reload --port 8000
```

## Test the bootstrap service

```bash
curl -X POST http://localhost:8000/create-app \
  -H "Authorization: Bearer supersecret" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "demo-internal-tool",
    "template": "python-web",
    "product_spec": "A small internal tool with a protected homepage.",
    "technical_notes": "Keep it single-service and simple.",
    "env_vars": {
      "APP_SECRET": "replace-me"
    },
    "auth_mode": "basic"
  }'
```

---

# 20) Claude prompt to generate the rest

```md
Take the following scaffold and turn it into a working end-to-end system.

Goals:
- Complete the Railway GraphQL integration in railway_client.py
- Upgrade GitHub auth from token to GitHub App if practical
- Optionally expose the bootstrap service as an MCP server
- Make repo bootstrap update template placeholders
- Add robust error handling, logging, and idempotency
- Add support for env var injection into Railway
- Return deployment status and live URL accurately
- Keep the architecture simple and production-sane

Constraints:
- Do not overengineer
- Keep v1 focused on one template: python-web
- Use Railway as the primary deploy engine
- Use GitHub as the source of truth
- Preserve private-by-default behavior
- Never commit secrets into repos
```

---

# 21) What to tell Claude Code after bootstrap exists

```md
Create a new internal tool using the bootstrap service.

Steps:
1. Write README.md product spec
2. Write TECH_SPEC.md
3. Choose template = python-web
4. Keep it single-service
5. Add /healthz
6. Use env vars only
7. Default to protected access
8. Call create_app with the generated app name, product spec, and template
9. Return repo URL and live URL
10. Continue future development by editing the GitHub repo and committing changes so Railway auto-redeploys
```

---

# 22) Final build order

1. Create the `python-web-template` repo on GitHub
2. Mark it as a template repo
3. Run the bootstrap service locally first
4. Verify GitHub repo generation works
5. Fill in Railway GraphQL integration
6. Verify first deploy works
7. Move bootstrap service onto Railway or Fly
8. Later: wrap it as MCP + OAuth

If you want, next I can give you the **Railway GraphQL mutations/queries skeleton** and a **GitHub App version** of the auth layer.
