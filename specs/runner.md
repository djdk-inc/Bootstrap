# Runner Spec

Two patterns. Choose based on whether a human needs to interact.

---

## Webapp — FastAPI (`python-web`)

Use when:
- Humans need a write path (creating, submitting, approving something)
- Access needs to be distributed to a small set of users
- The action needs to happen without a computer present (phone, async)

Example: reimbursement app, approval workflow, data entry form.

Entry point: `app/main.py`, started by Railway via `railpack.json`.

```
app/
  main.py       # FastAPI app, routes
  auth.py       # require_cf_auth + require_app_secret
railpack.json
requirements.txt
```

The write path is an API endpoint. A lightweight frontend (or Claude Code on mobile) calls it. There is no server-rendered HTML unless the app specifically needs it.

---

## Script — Click (`python-task`)

Use when:
- The task is autonomous — no human input at runtime
- It runs on a schedule (cron) or is triggered by an agent
- It does not need to be distributed to other users

Example: data sync, report generation, cleanup job.

Entry point: `task/main.py`, a Click CLI. Railway runs it on a schedule via cron config in `railpack.json`.

```
task/
  main.py       # Click CLI, one command per logical task
railpack.json
requirements.txt
```

```python
import click

@click.group()
def cli():
    pass

@cli.command()
def run():
    """Main task logic."""
    ...

if __name__ == "__main__":
    cli()
```

Multiple commands are fine. Each command does one thing. The agent or cron calls a specific command; it doesn't prompt for input.

---

## Decision Rule

> If a human needs to interact with it at runtime, or it needs to run from a phone without a laptop present — use the webapp pattern. If it runs autonomously on a schedule or agent trigger — use the script pattern.

The telegram-bot template is a third pattern for async human interaction via a messaging interface rather than a web UI. Use it when the interaction model is conversational rather than form-based.
