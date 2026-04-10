# [Project Name]

[One sentence: what the app does and its primary mechanism.]

---

## The Problem

[Set the scene. Describe the situation your target user is in — specific, grounded, human. Name the pain points that accumulate. End with the failure state: what does life look like when this problem is unsolved?]

## Why Current Tools Fall Short

[Name the incumbent tools. Describe what they do well.] [Name and bold the core failure mode of existing tools.]

The fundamental problem is that **[root cause framing — e.g. "you are the agent"]**. [Expand: what does that mean in practice? What steps still require a human that shouldn't?]

This means the actual experience is: [list the specific failure modes — bad UX moments, errors, friction, frustration].

The tools haven't failed at [surface-level function]. They've failed at [the deeper job to be done]. [One-sentence summary of where automation stops and the human picks up.]

[Project Name] [core value proposition in one sentence — what gets automated, and what the human's new job is].

## The Solution

[Project Name] [describe the end-to-end flow from input to output in concrete terms].

[Walk through the user journey: what does the person do, what does the system do, what is the result.] Done.

[Three-sentence version: no X, no Y, no "wait, who had the Z?"]

## Vision

[Describe the near-term state (what ships).] The future version is [describe the long-term state — infrastructure, background automation, invisible system].

[How does the user interact with it in the future? What changes about their behavior?] [What remains as the human touchpoint — HITL, dashboard, exception handler?]

The end state: [one sentence that captures the ideal user experience when everything is working].

---

## Mockups

### Milestone 1 — [Name] ([description, e.g. "HITL fallback"])

[Describe what this view is and its role in the system.]

![M1 mockup](mocks/m1-mock.png)

### Future Milestones — [Name] ([description, e.g. "primary interface"])

[Describe what changes in the future state and what the interface becomes.]

![Future mockup](mocks/future-mock.png)

---

## Product

### Milestone 1 — Core Features

#### [Feature Area 1: Ingestion / Input]
- [How source data enters the system — URL, upload, API, integration]
- [How the primary action is triggered — manual button, script, etc.]
- [Idempotency rule — what gets skipped on re-run]
- [Best-effort / failure posture — what always produces output even if imperfect]
- [What is NOT in scope for this milestone]

#### [Feature Area 2: Primary View]
- [Access model — URL structure, auth, who can read/write]
- [Top-level navigation — tabs, pages, sections]
- [What each section shows — embedded content, computed data, editable fields]
- [Data storage model — where data lives, format, concurrency behavior]

#### [Feature Area 3: Content / Data Model]
- [How content is stored — original format, translated/normalized, user overrides]
- [Describe the key data object and its fields]

#### [Item / Record Schema]
Each record has:
- `field_one` — [description]
- `field_two` — [description]
- `field_three` — [description, including how it is computed]
- `field_four` — [description, default behavior, future consideration]

#### [Feature Area 4: People / Identity]
- [How people/users are represented across the system]
- [Cross-platform identity mapping — what fields, what platforms]
- [How this enables downstream operations]

#### [Feature Area 5: Setup / Initialization]
- [How a new [resource] is created — CLI, script, control plane]
- **TODO:** this is the MVP path; better UX options to explore:
  - [Option A — web-based flow]
  - [Option B — agent/messaging-triggered flow]

#### [Feature Area 6: External Integration]
- [How [resource] maps to [external system]]
- [When and how data is pushed to [external system]]
- **TODO:** validate [external API] availability and third-party access terms before building

### Milestone 2 — Agentic *(tentative)*

#### [Capability: Agent / Automation]
- [Natural language query capability]
- [Natural language input / injection capability]

#### [Capability: Automated Notifications]
- [Detect and surface unresolved state — what triggers a notification]
- [Periodic summary notifications — cadence, content]
- [Downstream action triggered once state is complete]
- Primary interface via [messaging platform] — [how to get started]
- Start with [primary platform]; design to support [additional platforms] later
- **Dependency risk ([platform]):** [describe business/technical risk]

---

## Specification

See [IMPLEMENTATION.md](IMPLEMENTATION.md) for architecture, schemas, routes, env vars, acceptance criteria, and musings.

See [REVIEW.md](REVIEW.md) for adversarial, external, and strategic product review — competitors, gaps, commercialization, and privacy concerns.
