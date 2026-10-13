# Chapter 24: Git as a Save-State Engine

## Core Idea
An AI breaks a working codebase in two seconds with a tangled multi-file change, so replace *untangling* with *reverting*. Commit after every verified sub-task (a save state gated by the guardrails), and when a prompt goes sideways, `git reset --hard` and re-prompt from the last known-good state instead of debugging the wreckage.

## Frameworks Introduced
- **Commits Are Save States** (the game-reload model): a save state is a known-good point you return to instantly and without thought. Reload cost near zero is what makes aggressive experimentation safe.
  - When to use: every vibe-coding session, from Day One.
  - How: (1) after each small verified sub-task, commit; this is not a milestone or reviewed unit, just a reload point; (2) when the next prompt fails, do not study the diff; run `git reset --hard HEAD`; (3) re-prompt from the clean state with a different approach. The AI's second attempt from a clean base usually beats its attempt to patch its own mess.
- **The Three Git Save-State Rules**:
  - **Zero Inter-Prompt Drift**: never trigger a fresh prompt or sub-task until the last successful iteration is captured as a committed state.
  - **Aggressive Discarding**: if a prompt produces compilation errors, complex refactoring proposals, or failing tests, immediately `git reset --hard`. Do not try to guide the AI out of its own mess.
  - **Squash-on-Completion**: reconcile the high-frequency "dirty commits" (private history) by rebasing and squashing into one clean, reviewed commit at the PR boundary.
- **Commit Early, Commit Often, Operationalized**: the unit of commit is the **verified sub-task, not the feature**; the trigger is "a state I would be happy to return to," not "something worth showing."
  - When to use: continuously; three commits in twenty minutes is good.
  - How: commit the moment all three hold: tests pass, Ch 5 architectural tests pass, and the behavior the last prompt targeted is present. Messages like `wip: discount calc green` are fine. Separate the **working history** (dense, disposable, private) from the **published history** (curated at merge via `git rebase -i` or squash-merge).
- **Branch (and Worktree) per Risky Direction**: before an architecturally significant attempt (a cross-module refactor, a new integration), branch first as a sandboxed save-state lineage. Merge if it works and delete if not; main never saw it.
- **Guardrails Define the Save Points (the commit gate)**: "verifiably working" is not vibes. It is green across the book's guardrails, and a red signal is the objective trigger to reload rather than negotiate.

## Key Concepts
- **Two-second catastrophe**: one prompt rewrites five files, changes a signature three depend on, "improves" a fourth; the regression is entangled with legitimate work and there are no intermediate states to bisect.
- **Save state**: a commit that represents a guardrail-certified known-good state, not a milestone.
- **Untangling trap**: hand-repairing a tangled AI change routinely costs more than the feature and often introduces a second bug.
- **Verified sub-task**: the commit unit; the gap between save states bounds what you can lose.
- **Working vs. published history**: dense private wip commits versus curated history at merge.
- **Worktree sandbox**: `git worktree add ../experiment -b <branch>` gives a parallel physical directory for the AI, leaving your IDE and caches untouched; delete it and `git worktree prune` if it goes wrong.
- **Recovery half vs. prevention half**: the guardrails (Parts II–III) prevent; Git save states recover from the one defect that slips through.

## Mental Models
- Think of a bad generation as **a bad game run: reload, don't negotiate**.
- Think of `git reset --hard` as **safe only because the commit exists first**. Without a recent save state it is not a reload; it is data loss.
- Use "would I be happy to return to this state right now?" as the commit trigger.
- Think of a branch or worktree as **making architectural experimentation free**, which matters because the AI is most useful and most dangerous when exploring unfamiliar designs.

## Anti-patterns
- **Debugging the wreckage**: reading a multi-file AI diff to surgically revert the bad part; at vibe velocity it costs more than the feature.
- **Guiding the AI out of its own mess**: its self-patch attempts are usually worse than a clean retry.
- **Letting "commits should be meaningful" suppress frequency**: it removes the safety net; curate later instead.
- **An agent working an hour without a checkpoint**: it hands you one enormous diff and no way back to the last moment it was right.
- **Reset without a save state**: permanent loss of uncommitted work.
- **Experimenting on a branch in your main directory**: AI edits disrupt IDE state and caches; use a worktree.

## Code Examples
```bash
# Save state after a verified sub-task (tests + ArchUnit green, behavior present)
git add -A && git commit -m "wip: discount calc green"

# Prompt went sideways? Reload, don't untangle.
git reset --hard HEAD        # discard the failed attempt entirely

# Risky architectural direction: sandbox it in a parallel directory
git worktree add ../experiment -b experiment
# ...point the AI at ../experiment; if it destroys the project:
rm -rf ../experiment && git worktree prune

# At the PR boundary: squash the save-state noise into a story
git rebase -i main
```
- **What it demonstrates**: the full save/reload/sandbox/squash loop of the chapter.

## Reference Tables
**The commit gate: a save state is allowed only when all are green**

| Guardrail | Chapter | Green means |
|---|---|---|
| Behavioral tests | 5 | Feature does what it should |
| Architectural tests | 5 | No boundary crossed |
| Living architecture diagram | 6 | Regenerated without an unreviewed new dependency edge |
| Spec / BDD scenarios | 7 | Implementation matches the spec, not merely the prompt |
| async-tests | 17 | No concurrency regression |
| Schema & API contract tests | 18 | No breaking migration or payload change |
| Untrusted-input / sandbox checks | 19 | No injection path opened |
| Inquisitor | 22 | ALL CLEAR, no structural gripe on the diff |
| VibeTags compile-time validation | 4 | No contradictory or violated intent |

## Worked Example
A prompt asked for a small change and the AI rewrote five files, altering a method signature three of them depend on. Under the save-state discipline: the last commit (`wip: ... green`) was made when tests, ArchUnit, and the targeted behavior all held. After the prompt, the build is red, which is the objective reload signal. You run `git reset --hard HEAD`, which loses exactly the failed attempt and nothing else, then re-prompt with a different approach (e.g. a narrower scope, or "keep the signature frozen"). The second attempt from the clean base lands. At PR time, `git rebase -i` squashes the six wip commits into one reviewed commit.

## Why It Works / Failure Mode
- **Mechanism**: reloading is near-zero cost and fully reliable, while repair is expensive and error-prone; frequent guardrail-gated commits bound the maximum loss to one sub-task. Re-prompting from a clean base gives the AI an uncontaminated context.
- **Failure mode**: the whole workflow depends on the commit existing *before* the risky prompt. Skip a save state and `reset --hard` destroys good work. Without the guardrails, "commit when it's working" is a guess and save states may capture broken states, so the guardrails are what turn it into a gate.

## Key Takeaways
1. Revert, don't untangle: a failed generation is discarded, not debugged.
2. Commit at every verified sub-task (Zero Inter-Prompt Drift); frequency is the safety net.
3. Aggressive Discarding: compile errors, sprawling refactor proposals, or failing tests mean an immediate `git reset --hard`.
4. Squash-on-Completion keeps published history clean while working history stays dense.
5. Branch, or better a worktree, before any architecturally risky direction.
6. The guardrails define what "known-good" means, and red is the reload trigger.
7. The whole book is one loop: direct structure, diet context, annotate, test, specify, harden, enforce in CI, review adversarially, version intent, and keep Git as the cheap undo.

## Connects To
- **Ch 5 / 6 / 7 / 17 / 18 / 19 / 22 / 4**: each supplies one green check in the commit gate.
- **Ch 23**: lineage answers *where* intent drifted, and Ch 24 answers *how to get back*.
- **Ch 21b**: git worktrees for parallel-agent isolation.
- **Ch 25**: save-state commits are Day One, step 1 of the Incremental Adoption Roadmap; Appendix A item 33 (micro-commit discipline).
- **Ch 24b**: the anti-pattern field guide that follows.
- **Ch 26**: rollback as the self-healing loop's recovery action.
