# Implementation Spec

Technical decisions and contracts for [Milestone]. Items marked **[WIP]** are proposals — review before building.

---

## Agent

[Describe the agent's role in the system — what it does autonomously, what it escalates to humans.]

**Triggers:**
- [Cron / webhook / message — M2+]
- [Human-initiated fallback — M1]

**Actions:**
- [What the agent reads and writes]
- [How it calls the same API as the human-facing client]
- [How it handles ambiguity — escalation path]

**[WIP]** [Open question about agent auth, scope, or capability boundary]

---

## Data

[Describe the data store — format, location, how it is shared between the agent and the human-facing client.]

### `[resource].json`

```json
{
  "id": "",
  "field_one": "",
  "field_two": null,
  "created_at": ""
}
```

### `[parent]/[sub-resource].json`

```json
{
  "id": "",
  "nested": {
    "field": ""
  },
  "list_field": [],
  "finalized": false
}
```

**[WIP]** [Open question about field, concurrency model, or data lifecycle]

---

## Auth

[Describe the authentication model — who can access what, at which level.]

- [Per-resource auth — e.g. password per trip, signed cookie, session]
- [Agent auth — e.g. shared secret header, service account]
- [No user identity in M1 — describe what changes in M2+]

**[WIP]** Session mechanism — [default choice]; review before deploy.
**[WIP]** [Open question about OAuth flow, token storage, or scope]

---

## Security

[Describe the threat model — what data is sensitive, where it lives, who can reach it.]

- **PII exposure** — [what personal data is stored and where]
- **Data persistence** — [how deletions work; what survives in history/logs]
- **OAuth scope** — [what access is granted vs. what is actually needed]
- **[Integration] access** — [what a bot/integration can read beyond what users expect]
- **Credentials in prod** — [how the deployed system authenticates to external services]

**[WIP]** [Open question about threat model, compliance obligations, or access controls]
