# Bootstrap — Vision

Spinning up a new app by hand means creating a GitHub repo, writing boilerplate, configuring Railway — before writing a single line of product code. Bootstrap removes that bottleneck: agents call it to create infrastructure, you approve from your phone, they proceed.

The end state is autonomous development you can drive from anywhere. You write a spec; the system builds, deploys, and delivers a live link. You send a Telegram message; the system ships the feature. You are the decision-maker, not the operator.

---

## How It Works (target architecture)

```
You (on phone)
    │  approve / deny
    ▼
Bootstrap MCP Server  ──────────────────── deployed on Railway
    ▲                                       (dogfoods its own infra)
    │  MCP tool calls
    │
Agent (Claude Code — laptop / mobile / server)
    │
    │  hands back:  repo_url · live_url · deploy_status
    ▼
Agent continues working autonomously
```

**Auth at each boundary:**
- Agent → Bootstrap: OAuth 2.0 with per-agent scopes (`create:repo`, `provision:railway`, etc.)
- Bootstrap → You: Telegram push notification per operation — one-tap approve/deny; agent waits
- Bootstrap → GitHub / Railway: long-lived credentials stored in the server's environment

This is not 2FA. It is a human gate on side effects. The agent can plan and prepare; it cannot create external resources without your explicit sign-off.

---

## Milestones

### 1 — Local dev loop *(now)*
Claude Code on a laptop calls Bootstrap locally to spin up new projects without leaving the terminal. No auth, no deployment.

**Done when:** `create_app` works end-to-end from a local Claude Code session.

---

### 2 — Mobile-invocable, HITL-gated
Bootstrap is deployed and reachable from anywhere. Every infrastructure action requires your approval over Telegram before it executes. You can initiate and approve a new project from your phone.

**Done when:** a remote agent bootstraps a project; you approved it from Telegram without touching a laptop.

Key work:
- Deploy Bootstrap to Railway
- Telegram bot for per-operation approve/deny
- Rewrite as MCP server with discrete tools
- OAuth 2.0 for agent authentication

---

### 3 — Spec in, POC out
You send a product idea — one paragraph. The agent bootstraps the infra, writes the implementation, deploys it, and sends back a live link. No code written by hand.

**Done when:** product description → running deployed POC with no manual steps.

Key work:
- Spec-to-implementation agent (writes code into the bootstrapped repo)
- Deploy loop (push → Railway redeploys → agent validates → reports back)

---

### 4 — Telegram-driven iteration
Once a POC is live, you develop it by sending messages. Feature request in, implementation and deploy out. The feature list is the interface, not the codebase.

**Done when:** a feature request sent over Telegram is implemented, deployed, and confirmed — without opening a code editor.

Key work:
- Feature queue: Telegram messages → structured list the agent pulls from
- Agent loop: dequeue → implement → deploy → notify
- Escalation: agent flags ambiguous requests; you clarify before it proceeds

---

## MCP Tool Surface

| Tool | Description |
|---|---|
| `create_github_repo(name)` | Create a private GitHub repo |
| `push_template(repo, template, files)` | Populate repo from a named template + generated files |
| `provision_railway(repo, name, env_vars)` | Create Railway project, set vars, deploy |
| `create_app(name, template, spec)` | Convenience: all three in sequence |
| `list_templates()` | Return available templates |

Each tool that creates external resources requires HITL approval before executing.

---

## Templates

A good template means the agent starts writing product code immediately, not boilerplate.

- `python-web` — FastAPI, auth scaffold, Railway deploy
- `python-task` — Scheduled/one-shot script runner
- `telegram-bot` — Bot with handler scaffold

New templates are added as patterns prove out.
