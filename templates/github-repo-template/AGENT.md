# Agent Spec

Defines agentic flows, task boundaries, permissions, and escalation rules for [Milestone]. Each agent does one thing. It reads only what it needs, writes only to draft fields, and escalates rather than guesses.

---

## Design Principles

**Single responsibility.** Each agent owns one outcome. It is not a general-purpose assistant — it is a narrow executor with a defined job.

**Least privilege.** Each agent gets its own scoped credential. It can only call the endpoints and read the fields its task requires. The API enforces this — not convention.

**Draft before commit.** Agents write to `_proposed` fields. A human (or an explicit confirmation step) promotes to `_confirmed`. Agents never overwrite confirmed data.

**Escalate, never guess.** Every task has a confidence threshold. Below it, the agent flags and waits. A wrong silent guess is worse than a visible pause.

**Irreversible actions require human approval.** Any action that is hard to undo — pushing to an external system, deleting data, sending a message — is gated on `finalized: true` or an explicit human trigger. Agents cannot set this flag themselves.

---

## Intended Outcomes

| # | Outcome | Done when… |
|---|---|---|
| 1 | [Outcome 1] | [Measurable completion state] |
| 2 | [Outcome 2] | [Measurable completion state] |
| 3 | [Outcome 3] | [Measurable completion state] |

---

## Agent Roster

| Agent | Outcome | Trigger | Credential scope |
|---|---|---|---|
| `[agent-name]` | [Outcome #] | [cron / webhook / event] | [endpoint list] |
| `[agent-name]` | [Outcome #] | [event] | [endpoint list] |

---

## Agent Contracts

### `[agent-name]`

**Job:** [One sentence — what this agent does and why.]

**Trigger:** [What starts it — cron schedule, event, message, human action]

**Reads:**
- `[resource].[field]` — [why it needs this]

**Writes (draft only):**
- `[resource].[field]_proposed` — [what it sets and how]

**Never touches:**
- Any `_confirmed` field
- `[resource].finalized`

**Blocks (escalation triggers):**
- Confidence < [threshold] on any field → flag, do not write
- [Condition] → escalate to [channel], wait for human response

**Failure mode:** [What happens if this agent fails silently]

---

## Data Permission Model

| Field | Human | `[agent-1]` | `[agent-2]` |
|---|---|---|---|
| `[resource].[field]` | read/write | read | — |
| `[resource].[field]_proposed` | read/write | write | read |
| `[resource].[field]_confirmed` | read/write | — | — |
| `[resource].finalized` | read/write | — | — |

---

## Draft / Confirm Flow

```
Agent writes [field]_proposed
    ↓
Human sees proposal in webapp
    ↓
Human confirms → [field]_confirmed set
    ↓
Agent (or human) may now act on confirmed value
```

---

## Escalation Protocol

1. **Flag** — mark the resource/field with `flagged: true`, `flag_reason: "[description]"`
2. **Notify** — send to [channel / messaging platform / webapp notification]
3. **Wait** — do not proceed with downstream tasks that depend on the flagged item
4. **Timeout** — if no human response within [N hours], re-notify; never auto-resolve

---

## Open Questions

| # | Question | Notes |
|---|---|---|
| 1 | [Agent auth mechanism] | [Scoped API key? Signed token?] |
| 2 | [Confidence threshold values] | [Needs calibration against real data] |
| 3 | [Escalation channel] | [Telegram bot? Webapp notification?] |
| 4 | [Timeout / re-notify cadence] | [How long before a flagged item becomes a reminder] |
