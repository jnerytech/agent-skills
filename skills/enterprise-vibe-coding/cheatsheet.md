# Cheatsheet — Enterprise Vibe Coding for Agentic Engineering

## Decision rules
- **Will the software outlive the conversation that made it** (integrated, audited, secured, maintained by others)? → steer it. If not, vibe coding is fine.
- **Before any AI-assisted merge**, ask: who decided? what constraints? what evidence? → any blank = it was vibed; block it.
- **A rule must never be broken** → not an instruction. Use a `PreToolUse` hook; if org-wide, use deny-by-default policy-as-code.
- **Rule applies to one module** → Tier-2 scoped file (`applyTo: "payments/**"` / `payments/CLAUDE.md`), never "be careful in payments" in the global file.
- **Plan approved** → still run independent tests, scans, staged rollout. Approval ≠ correctness.
- **Release decision** → always a named human in the workflow run. Agents accelerate, never decide.
- **Bug fix proposed by an agent** → goes through a PR with human review. Triage agents propose, never apply.
- **Two agents' scopes overlap** → run them sequentially. Shared write → make it idempotent. Handoff → via repo file.
- **Agent states a price, stock or availability** → it must come from a live tool call to the system of record.
- **Checkout, payment, publication** → outside the agentic boundary, in the existing secure/human flow.
- **Loop reply is ambiguous, or silence at Gate 1** → wait and ask. Silence is not consent.
- **Loop is failing checks** → 3 attempts per criterion, then halt. Auth/payments/PII/prod → stop on the first failure.
- **Human returns to a long-running task and must read the transcript** → AX failure. Build the resumable view.

## Band × decision level (raise determinism with blast radius)
| Action | Band | Decision level |
|---|---|---|
| Draft memo, summary, internal doc | 1–2 | 3 autonomous |
| Lint fix, dependency bump in approved range | 3 | 3 autonomous |
| Open draft PR, create non-prod resource | 3 | 2 logged + reviewable |
| Run schema migration / prod deploy | 4 (reproducible script) | 1 human approval |
| Promote release, authorize deploy | 5 (policy, no model) | 1 + policy check |
| Delete prod data, push to `main`, send PII externally unredacted | — | 0 forbidden |

## Which mechanism?
| Need | Use |
|---|---|
| Always-on standard | Tier-1 instructions (short, imperative) |
| Module-specific strictness | Tier-2 scoped instructions |
| Recurring task with fixed output | Prompt (intent-named) |
| A role with limited tools | Agent (≤1 page, least privilege, escalation rule) |
| Opinionated how-to + failure modes | Skill |
| Must-hold check inline, fast | Hook |
| Must-hold org-wide, revocable once | Policy-as-code |
| Reach an external system | MCP (read-only first, pinned, logged) |
| Slow/expensive validation | CI/CD, not hooks |

## Orchestration pattern picker
- Later steps truly depend on earlier → **Sequential**
- Independent specialists on the same input → **Concurrent**
- Iterative refinement in rounds → **Group chat**
- Steps can't be declared upfront → **Magentic**
- One conversation, expertise shifts by topic, one voice → **Handoff**

## Thresholds & defaults
- HVE team: **4–5 people**, multidisciplinary.
- Start with **3–5 agents**, **3–5 skills**, a handful of hooks.
- Review instructions **about monthly**. Agent brief **≤ one page**.
- Test plan per story: **happy + 3 edge + 2 failure + 1 security**.
- Recovery: **3 failed attempts** per criterion, then halt.
- Loop: **one tick = one capability**; **2 human gates** (plan, merge).
- Clarifying questions: **2–3 concrete options**, never a long list.

## Autonomy ramp
Interactive → Autopilot with limited permissions → Autopilot with end-to-end permissions, only for well-defined tasks. Always cap continuations and `MAX_STARTS`.

## Tells & smells
- Seniors are full-time reviewers → review-capacity collapse (Faros: +91% review time).
- Same feature built 3 ways across repos → architectural drift; put rules in repo instructions and skills.
- "Make the planner better" issue → fuzzy contract; the loop can't close.
- "The agent did it" in a postmortem → no identity/audit trail.
- Prompt nobody can reproduce → prompt folklore; make it a primitive.
- Level 3 feels productive → hidden debt; the costliest plateau.
- A rule change means editing a dozen prompts → it should live once in a skill or instruction.
