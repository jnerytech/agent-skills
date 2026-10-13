# Chapter 20d: Anatomy of a Correctness Hunt

## Core Idea
Ch 20b's test-suite audit, run for real: one day, three repositories (VibeTags, async-test-lib, an FHE crypto library), one agent per repo in parallel, all under the same repeatable work order. The hunt produced 15 committed bugs, each with a failing-then-passing test, plus ~12 suspicions reported but deliberately not committed. What the agent refused to touch matters as much as what it fixed.

## Frameworks Introduced
- **The Correctness-Hunt Work Order (7 steps)**: identical instructions for every agent and repo, so the hunt is repeatable rather than "vibes".
  - When to use: pointing autonomous agents at an existing codebase to find and fix correctness bugs.
  - How: (1) Pull latest and create a fresh branch, never the default branch and never a force-push. (2) Baseline the full suite before touching anything and record the result. (3) Hunt using named bug-shape lenses, not "look for bugs". (4) Failing-test-first, or it doesn't count. (5) One commit per bug: failing test and fix together. (6) Run the full suite and lint gates at the end of the branch. (7) Push nothing without human review. The agent's authority ends at "propose".
- **Bug-Shape Lenses (standing, reusable)**: a lens is a yes/no question asked of a specific piece of code. Once named, a bug shape is a standing lens, not a one-time cleanup.
  - When to use: every hunt, and again on later days after earlier instances are fixed.
  - How: keep the six lenses from Ch 20b as a checklist and re-run them across files and repos. The same generator that wrote instance one writes instance seventeen elsewhere, under different names.
- **PR as a Review Document**: each bug is pre-decomposed into File / Defect / Concrete failure scenario / Fix / Commit SHA. Suspicions sit in a separate section, marked unresolved, each with a reason it was held.
  - When to use: any agent-produced branch carrying many findings.
  - How: state each defect as a fact about behavior. Phrase the scenario so a human could reproduce it by hand. Explain why the fix closes the gap rather than patching the symptom. Link the SHA. Pre-triage suspicions so reviewer attention goes to the two or three real judgment calls.
- **Escalate, Don't Override**: hunters obey the same guardrails as generators.
  - When to use: a fix touches @AILocked code or changes the meaning of persisted data.
  - How: write the finding up with a concrete scenario, leave it uncommitted, and hand it to the owner.

## Key Concepts
- **Baseline**: the full-suite result recorded before hunting. Without it you cannot separate your findings from pre-existing breakage, or prove that a fix mattered.
- **Suspicion vs bug**: a suspicion is a hypothesis. It becomes a bug only when a test fails on current code and passes after the fix.
- **Drained evidence**: a counter read after the state it measured has already reset.
- **Re-registration wipe**: registering twice silently discards the first registration's state instead of merging it.
- **Identity-from-prose**: keys sliced out of human-readable text instead of derived from stable structural fields.
- **One-throwing-detector-discards-all**: one detector's exception aborts the whole analysis pass instead of only that detector's contribution.
- **Green-for-the-wrong-reason**: a passing assertion satisfied by an unrelated failure, not by the mechanism it claims to check.
- **Synthetic half-lifecycle**: a test drives a resource to "acquired" and never to "released", hiding the other half of its life.
- **Data-meaning change**: a fix that reinterprets values already on disk. This is a migration and policy decision, not a code fix.

## Mental Models
- Think of a named bug shape as a standing lint rule written in prose: cheap to re-run, and it outlives the bug that prompted it.
- Use "does a red test exist?" as the single admission criterion for the commit history.
- Think of a locked contract as locked against every actor. The guardrail doesn't care whether the agent is generating features or hunting bugs.
- Think of each PR entry as a Knuth check: a small, verifiable certificate of a specific defect (file, defect, scenario, fix, commit), not a tally line.

## Anti-patterns
- **Hunting against a red or unknown suite**: findings blur into pre-existing breakage.
- **Open-ended "find bugs" prompts**: produce noise. Lenses produce checkable answers.
- **Committing suspicions**: inflates the "bugs found" count with unverified hypotheses.
- **Silently reinterpreting stored data**: the agent makes a policy decision it has no authority to make. Persisted values have downstream stakeholders a unit test cannot see.
- **Overriding @AILocked "for a good reason"**: a guardrail an agent can override with a good enough reason was never a guardrail.
- **PR as changelog**: forces the reviewer to rebuild context from a raw diff. Review time is the constraint (Ch 22).
- **Treating a fixed bug shape as done**: new instances appear in other corners of the same library.

## Code Examples
```markdown
## Committed bugs
### 1. <path/to/Class.java#method>
- **Defect**: <1–2 sentences, a fact about behavior>
- **Concrete failure scenario**: <input/timing/call sequence, hand-reproducible>
- **Fix**: <what changed and why it closes the gap>
- **Commit**: <sha>

## Suspicions (unresolved, not committed)
### A. <path>
- **Defect / scenario**: <...>
- **Held back because**: needs owner decision | behind @AILocked | data-meaning change | out of time before a red test
```
- **What it demonstrates**: the PR-as-review-document format that keeps the human gate fast at agent volume.

## Worked Example
**One-day hunt, three repos in parallel.**
- *async-test-lib*: re-ran Ch 20b's six lenses after the earlier instances had long been fixed. They found **new, real instances of the same six shapes** in different corners of the library.
- *Totals*: **15 verified bugs**, each committed with its own failing → passing test, and **~12 suspicions** written up but not committed (some ran out of the day's budget, some needed an owner decision).
- *Two holdouts, data meaning*: the proposed fixes would have changed the meaning of values already on disk, computed under the old logic and possibly relied on downstream. They were reported with concrete scenarios and handed to the human, unresolved on purpose.
- *One holdout, @AILocked*: the agent found the seam and understood the fix, but the code sat behind @AILocked (Ch 4). It did not apply the fix and escalated instead. This is the guardrail governing the hunter just as it governs the generator, and it is what makes delegating hunts on unlocked code to an autonomous agent trustworthy at all.

## Why It Works / Failure Mode
- **Why it works**: failing-test-first turns every claim into evidence. One commit per bug makes each fix independently reviewable and revertible. Named lenses make the hunt repeatable across days and repos. Pre-decomposed PRs leave the human only the one thing they must still do: decide.
- **Failure mode**: without a baseline, lenses or the red-test bar, the hunt degrades into noisy "improvements" that cannot prove they mattered. If agents may override locks or reinterpret data, the hunt itself becomes a source of silent security or semantic regressions.

## Key Takeaways
1. Baseline the suite first, then hunt with named lenses, not open-ended instructions.
2. No red test, no bug. Suspicions stay out of the commit history and get reported separately.
3. One commit per bug, full suite and lint at the end, push nothing without review.
4. Bug shapes are standing lenses: re-run them, because the generator repeats its patterns.
5. Flag data-meaning changes as owner decisions. Respect every lock: escalate instead of override.
6. Write the PR as a review document (file, defect, scenario, fix, commit) so review keeps pace with agent volume.

## Connects To
- **Ch 20b**: source of the six bug-shape lenses and the failing-test-first discipline. This chapter is that audit run live.
- **Ch 4**: VibeTags and @AILocked. The lock held against the bug-hunting agent too.
- **Ch 17**: async-test-lib, the concurrency-testing library that was hunted.
- **Ch 21**: proposal-not-merge discipline. The agent proposes, a human merges.
- **Ch 21b**: running one agent per repo in parallel calls for isolation hygiene.
- **Ch 22**: review time is the constraint, and the PR format serves it.
- **Knuth reward checks / public errata log**: a found bug as a verifiable certificate, not a count.
