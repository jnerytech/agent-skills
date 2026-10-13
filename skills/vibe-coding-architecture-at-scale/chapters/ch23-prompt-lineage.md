# Chapter 23: Prompt Lineage: Git for Intent

## Core Idea
Git captures every change to the code forever, but the intent that produced it (prompt, spec revision, loosened system rule) evaporates into a chat window. In a prompt-generated codebase, the prompt *is* the "why", so discarding it discards half the version history. Commit load-bearing intent alongside the diff, capture it ambiently via hooks, enforce its presence at the branch, record the model's interpretation and identity, and pin the model like any other dependency.

## Frameworks Introduced
- **Prompts as First-Class Code Citizens**: promote load-bearing prompts to versioned source in `prompts/`, committed in the *same commit* as the diff they produced.
  - When to use: any prompt whose silent change would break something downstream (the same test as for a contract).
  - How: keep three folders: `architecture/` (standing structural prompts), `features/` (per-feature spec prompts) and `system/` (global rules handed to every agent on every run). Promote only load-bearing intent and leave throwaway "fix the import" lines in the session log. The commit becomes "what was asked, and what that produced."
- **Prompt Lineage (bisect the instruction, not the bug)**: diff intent in parallel with code across the regression window.
  - When to use: a regression whose code diff is huge and where every line looks deliberate.
  - How: diff `prompts/` (especially `system/house-rules.md`) between the last-good and first-bad dates. The cause often shows in the left (intent) column before you read the code. The breaking change has a commit, author and date in `prompts/`, not `src/`.
- **Ambient Capture, Human Promotion, Branch Enforcement**: a hook captures, a human curates, CI enforces.
  - When to use: always. Intent that depends on discipline to record is already lost, since engineers do it twice and never again.
  - How: (1) a `SessionEnd` or post-generation hook (Ch 3d) writes the session's load-bearing prompts and the model's plan to a staging file, quietly and without blocking the inner loop. (2) The engineer promotes what matters from staging into `prompts/`. Promotion stays human, because auto-committing everything rebuilds context rot in a directory. (3) A CI check (Ch 21) blocks merge if a change touches a file under an architectural boundary without a corresponding `prompts/` entry ("not because the code is wrong but because the why is missing").
- **Intent → Interpretation → Code chain**: keep the outputs, not only the inputs.
  - When to use: the prompt didn't change but behavior did.
  - How: commit the AI's plan (`plan.md` from Ch 8), its design (`design.md` from Ch 9) and its stated assumptions next to the prompt. This interpretation layer is "the deposition" that most tools treat as disposable.
- **Pin, Record, Gate the Model**: the model is the most influential and least-pinned dependency.
  - When to use: every project consuming a model via an alias ("latest", a bare family name).
  - How: **Pin it** by putting the exact model ID, never an alias, in the project-level harness config (Ch 3d) committed to the repo, so `git log` on one file answers "when did the brain change?". **Record it** by having the capture hook stamp each lineage entry with model ID and harness version, adding a third column: intent, interpreter, output. **Gate the upgrade** by replaying the promoted `prompts/` golden set against the candidate model in a Ch 19 sandbox and running all output through the deterministic gates (Ch 5 arch tests, Ch 18 contracts, Ch 22 Inquisitor). Compare *invariants*, never tokens.

## Key Concepts
- **Intent asymmetry**: a perfect history of what the system became and none of why.
- **Load-bearing intent**: architectural prompts, feature specs and system rules. Something downstream breaks if they change silently.
- **`prompts/` directory**: the repository becomes the system of record for intent, not just code.
- **Intent drift**: a correct instruction quietly softened (e.g. "assume retries WILL occur" → "should be idempotent").
- **Staging file**: hook-written ambient capture of session prompts and plans, awaiting human promotion.
- **Lineage gate**: a CI check that blocks boundary-touching changes lacking a `prompts/` entry.
- **Interpretation layer**: the AI's plan, assumptions and rationale. It is where drift hides when the prompt is unchanged.
- **Unpinned model**: consuming a vendor alias, so the interpreter of every prompt can be swapped overnight with no record.
- **Golden set**: the curated promoted prompts, reused as a regression corpus for model upgrades.

## Mental Models
- Think of git as half a version history in AI-generated code. The other half is the prompt.
- Think of a lineage record without the model ID as "a deposition that never asked who was speaking."
- Use the dependency-pinning instinct (Maven coordinates, lockfiles, frozen signatures and wire contracts) on the model too.
- Think of the guardrail stack as the only layer that holds still when the model moves. Correctness that lives in deterministic gates makes the model swappable like a compiler, and correctness that lives in tuned prompt phrasing starts over at every upgrade.

## Anti-patterns
- **Chat window as system of record**: intent nobody can `git log`.
- **Versioning every throwaway prompt**: rebuilds Ch 3/11 context rot in a new directory.
- **Relying on engineers to save prompts by hand**: done twice, then never again.
- **Auto-committing every captured prompt**: removes the human curation that makes `prompts/` useful.
- **Capture that blocks the inner loop**: people will disable it. Stage quietly and gate only at the branch.
- **Keeping inputs only**: losing the plan and assumptions hides interpretation drift.
- **Model aliases ("latest")**: silent interpreter swaps, then a week bisecting prompts that were never the cause.
- **Diffing raw tokens across models**: meaningless under nondeterminism. Test the invariants instead.

## Code Examples
```text
prompts/
├── architecture/              # standing structural prompts: "how this system is shaped"
│   └── module-boundaries.md
├── features/                  # per-feature spec prompts that drove each slice
│   └── 2026-04-session-timeout.md
└── system/                    # global rules handed to every agent, every run
    └── house-rules.md
```
- **What it demonstrates**: the `prompts/` layout for load-bearing intent, committed alongside code.

```text
prompts/system/house-rules.md  @ March → June
- "Treat every payment handler as non-idempotent; assume retries WILL occur."
+ "Payment handlers should be idempotent."
```
- **What it demonstrates**: a one-line intent diff that explains a months-later regression the code diff hides.

## Worked Example
**Double-charging payments.** A payment integration that worked in March double-charges in June. The code diff across those months is enormous and every line looks deliberate. Lineage workflow: diff `prompts/system/house-rules.md` between March and June. The left column shows the cause. A sentence demanding "assume retries WILL occur" was softened into one that *hoped* handlers would be idempotent, three weeks and 200 commits earlier. Every code change faithfully executed the new instruction, which is why code review caught nothing. You bisected the instruction, not the bug.

**Variant with a missing column.** Same symptom, but both columns are clean: the house rules, the feature prompts and the merged code are all unchanged. The vendor re-pointed the model alias. Without the model ID in the lineage record, the breaking change sits in a vendor deployment log you cannot see. With a pinned, recorded model, the upgrade has a commit, an author and a date.

## Why It Works / Failure Mode
- **Why it works**: it applies the book's recurring move (make the ephemeral a versioned artifact, and force a failure next to its cause, as Ch 17 did for interleavings and Ch 18 for wire contracts) to the instruction itself. The hook captures with zero flow tax, the human promotes, and CI makes lineage a repository property instead of a habit.
- **Failure mode**: lineage is *forensic, not preventive*. It is the Ch 6 living diagram of intent, pure telemetry that enforces nothing. It makes drift attributable instead of mythological but won't stop it. It also decays if capture is too costly (it gets disabled), if promotion is automated (rot), or if the model identity isn't recorded (it bisects the wrong layer).

## Key Takeaways
1. Commit the intent, not just the diff: load-bearing prompts live in `prompts/`, in the same commit as the code they produced.
2. When a regression's code diff is unreadable, diff the intent first and bisect the instruction.
3. Capture ambiently via hooks, promote by human judgment, and enforce presence at the branch.
4. Record the AI's plan and assumptions too. The interpretation layer is where unchanged prompts drift.
5. Pin the exact model ID, stamp it on every lineage entry, and gate upgrades by replaying the golden set through the deterministic gates.
6. Deterministic gates make the model swappable, which is a competitive property, not just hygiene.

## Connects To
- **Ch 7**: "intent is the source of truth" (the spec was versioned there, and the prompt and system rules are versioned here).
- **Ch 3, 11**: context rot, the reason only load-bearing intent is promoted.
- **Ch 3d**: hooks as the deterministic primitive and the project-level config layer for pinning.
- **Ch 8, 9**: `plan.md` and `design.md` as the interpretation layer.
- **Ch 4, 18**: frozen signatures and wire contracts as the pinning precedent.
- **Ch 21**: branch enforcement, and the lineage gate shaped like the @AILocked provenance gate.
- **Ch 19, 5, 22**: the sandbox, arch tests and Inquisitor used to gate a model upgrade.
- **Ch 6**: living diagrams as forensic telemetry. **Ch 24**: recovery, the last net.
- **git bisect**, **dependency pinning / lockfiles**.
