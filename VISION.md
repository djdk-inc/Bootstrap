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
- Bootstrap → You: in-session approval (Claude Code on mobile) early on; async Telegram notifications once agents run in the background without an active session
- Bootstrap → GitHub / Railway: long-lived credentials stored in the server's environment

This is not 2FA. It is a human gate on side effects. The agent can plan and prepare; it cannot create external resources without your explicit sign-off.

---

## Milestones

### 1 — Local dev loop *(now)*
Claude Code on a laptop calls Bootstrap locally to spin up new projects without leaving the terminal. No auth, no deployment.

**Done when:** `create_app` works end-to-end from a local Claude Code session.

---

### 2 — Claude Code on mobile
Bootstrap is deployed and reachable over the network. You open Claude Code on your phone, describe what you want to build, and the agent calls Bootstrap to create the infrastructure. You are the HITL natively — you're in the conversation, you see what the agent is doing, you let it proceed.

**Done when:** a new project is bootstrapped end-to-end from Claude Code on a phone.

Key work:
- Deploy Bootstrap to Railway
- Rewrite as MCP server with discrete tools
- OAuth 2.0 so Claude Code can authenticate to Bootstrap without a hardcoded token

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

## Constraints and Trade-offs

**Single developer.** Replit, Lovable, and similar tools have full teams building product polish, error handling, onboarding, and edge cases. Building a competing platform from scratch is not the goal and not viable. The goal is a thin integration layer — own the glue, own the specs, let best-of-breed tools do the heavy lifting underneath.

**Integration over fragmentation.** The risk of building piecemeal is ending up with a patchwork of disconnected tools that can't evolve together. The mitigation is to treat each external tool (GitHub, Railway, Telegram, Claude) as a swappable dependency behind a clean interface. The durable layer is the specs and the agent configuration — not the tools themselves. If Railway gets expensive, swap it. If Telegram is the wrong channel, swap it. The conventions and heuristics are what compound over time.

**Use platforms where they're strong.** Replit and similar tools are genuinely good for rapid exploration. The right answer isn't "never use Replit" — it's "use Replit for throwaway exploration, use Bootstrap for things you intend to maintain and evolve." They serve different moments in the development lifecycle and can coexist.

**The bet.** A single developer with strong specs and a well-configured agent can punch above their weight, because the leverage comes from the specs compounding — not from headcount. The product power of these platforms is real; the goal is to capture it at the exploration phase and then bring the output into an environment you control for the long term.

**The kill switch.** If Bootstrap starts growing into a general-purpose build platform — handling its own IDE, its own runtime, its own error UI — that's a signal it has converged to Replit. At that point, stop and use Replit. Invest the saved effort into whatever thin integrations are actually missing (spec injection, infra ownership, async loop). Never compete with a platform on its own terms.

---

## Alternatives

Replit Agent is the closest analogue: describe an app, get a deployed link. The overlap is real. But the model is fundamentally different in ways that matter.

**Replit owns the output.** Code lives on Replit's platform, deployed on Replit's infrastructure. If Replit changes pricing, deprecates a feature, or goes away, your apps go with it. Bootstrap provisions into GitHub and Railway — infrastructure you already own and control independently.

**Replit uses its own opinions.** When Replit Agent builds something, it builds it Replit's way. You have no meaningful input into how it handles security, auth, error handling, code structure, or deployment configuration. For throwaway prototypes that's fine. For anything you intend to maintain or hand off, it's a problem.

This system is built to run on *your* specs. CLAUDE.md, heuristics, conventions, templates — the agent builds the way you've decided things should be built. Security posture, auth patterns, code structure, deployment config: all of it is yours to define and refine over time. The specs compound; Replit's opinions don't.

**Replit requires you to be present.** It's a synchronous IDE session. You're in the interface, watching it work, nudging it forward. The Telegram-driven iteration model here is explicitly async — you send a message, the agent works, you get a notification when it's done. Development happens while you're doing something else.

**Other tools in this space** — Lovable, Bolt, v0 — have similar constraints: opinionated platforms, locked infrastructure, synchronous interfaces. GitHub Copilot Workspace is closer to the agent-on-your-terms model but doesn't handle deployment.

The bet here is that the right long-term approach is a thin automation layer over infrastructure you control, driven by specs you author, callable from wherever you are. You trade some out-of-the-box convenience for full ownership of how things get built.

---

## Templates

A good template means the agent starts writing product code immediately, not boilerplate.

- `python-web` — FastAPI, auth scaffold, Railway deploy
- `python-task` — Scheduled/one-shot script runner
- `telegram-bot` — Bot with handler scaffold

New templates are added as patterns prove out.
