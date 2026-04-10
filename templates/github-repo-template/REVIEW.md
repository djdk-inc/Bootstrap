# Review

Adversarial, external, and strategic review of the product spec. Updated as the project evolves.

---

## General Review

> High-level assessment of the README and spec quality. Note what lands well and what is unclear or incomplete.

**Open cleanup items:**
- [ ] [Inconsistency or outdated reference in README]
- [ ] [Section that conflates two milestones without a bridge]
- [ ] [Duplicate/redundant content that could be merged]
- [ ] [Milestone that feels thin or unfinished]

---

## Adversarial Review

### Product assumptions that need stress-testing

**[Platform / ecosystem assumption].** [Describe the assumption and why it may not hold for a realistic user base. What is the adoption ceiling this creates?]

**[Dependency risk].** [Third-party API, acquisition, or policy change that could kill a core feature. The flag exists — is the risk higher than the framing implies?]

**[Technical quality assumption].** [E.g. OCR, ML model, or data quality assumption that degrades in real conditions. What does "best-effort" look like when it goes badly?]

**[Agent capability overpromise].** [Where does the spec imply autonomous capability that will require significant human input in practice? When will this resolve?]

**[Concurrency / data integrity edge case].** [Scenario under realistic concurrent use where data will be silently lost or corrupted. This is a when, not a maybe.]

**[Messaging platform / market assumption].** [Platform choice that narrows the initial addressable market. Frame it as a constraint, not a preference.]

---

## External Review

Someone landing on this repo cold will:
1. Read the pitch — [assessment of clarity]
2. See the M1 mockup — [assessment]
3. See the agentic mockup — [what clicks, what excites]
4. Hit the Product section — [where detail drops off]
5. Hit the Musings — [length/quality assessment]

**Biggest gap for an outsider:** [What question is unanswered for someone evaluating the project — demo, hosted instance, setup guide, etc.]

---

## 1. Competitors

| Tool | [Feature 1] | [Feature 2] | [Feature 3] | [Differentiator] |
|---|---|---|---|---|
| **[Competitor A]** | ✅ | ✅ | Partial | ❌ |
| **[Competitor B]** | ✅ | ✅ | ✅ | ❌ |
| **[Incumbent]** | Limited | ❌ | ✅ | ❌ |
| **[This project]** | ✅ | ✅ | ✅ | ✅ (M2+) |

**[Closest competitor]** is the most direct M1 competitor. Differentiators: [list what sets this project apart].

**The genuine moat:** [What this project does that no competitor does. Where focus should remain.]

---

## 2. Complexity

**[Milestone]: [assessment of complexity level].** [Number of external dependencies] external API dependencies in [milestone] means [number] surfaces that can fail, change terms, or break auth.

**The [agentic/advanced] vision ([future milestone]): [assessment].** The complexity is justified because [reason]. Don't simplify that away.

---

## 3. Gaps

| Gap | Severity |
|---|---|
| No fallback if [critical dependency] is unavailable or deprecated | High |
| No UX for [catastrophic failure mode] | High |
| [Key resource] population is undefined | Medium |
| [Edge case with external system] | Medium |
| No structured [audit trail / change log] for [edit type] | Medium |
| No answer to "[data exposure scenario]" | Medium |
| No model for what happens after [resource] closes | Low |

---

## 4. Commercialization

**[B2C / B2B framing] is [the obvious / a harder] path because [reason].**

**The more interesting angle is [alternative market].** [Describe the B2B, enterprise, or adjacent market.]

**Realistic commercialization path:**
1. Launch free, build a real user base via [channel]
2. Charge for: [list of premium features]
3. [B2B pivot / enterprise tier] once the core pipeline is proven

---

## 5. Data, Privacy & Integration Concerns

**[Resource] data is [sensitive data type].** [What does this data reveal, and where is it stored?]

**`[contacts/users resource]` stores PII in [format].** [Fields stored and the compliance obligations this triggers.]

**[OAuth scope] is broad.** [What access is granted vs. what is actually needed.]

---

## Summary: What to Address Before [Milestone] Ships

1. Acknowledge [platform gap or exclusion] explicitly
2. Validate [critical external API] access *before* building against it
3. Define the [failure mode] UX
4. Define a minimal privacy model
5. Add a "Getting Started" section once [milestone] is built
