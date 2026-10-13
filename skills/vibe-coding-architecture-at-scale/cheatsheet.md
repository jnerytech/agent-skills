# Cheatsheet — Vibe Architecture decisions

## The one test for any guardrail
Is it **written once**, **enforced by a machine** in the loop the AI already watches, at **zero flow tax**? Can it **fail a build / block a merge**? If not, it is documentation, not a guardrail. ("If a principle cannot fail a build, the agent will eventually violate it.")

## Where does this intent go?
| Intent | Home |
|---|---|
| Project-wide invariant, needed every turn | Tier 1 root file, 10–20 lines (one screen) |
| Applies to one directory/module | Tier 2 scoped rule file (glob) |
| Applies to one class/method | Tier 3 annotation (`@AILocked`, `@AIContract`, `@AIThreadSafe`) |
| Repeated procedure, task-specific | Skill (description loads always, body on demand) |
| Needs isolation / opposite objective | Subagent with tool allowlist |
| Must never happen | Hook (exit 2) **and** CI test |
| Personal, unverified fact | Memory → promote after repeated re-verification |
| Cross-cutting rationale linked to code | lat.md node + `require-code-mention` |

## Decision rules
- Typed the same guidance **3×** → move it into source (annotation / rule file).
- Rule still under its eval floor after an honest rewrite → **promote** to hook / ArchUnit / gate.
- Context file past one screen → **cut, scope, or relocate**.
- Build red after a prompt → **reload** (`git reset --hard`), don't negotiate.
- No save state before a risky prompt → don't send the prompt.
- Refactor requested on untested code → write parameterized behavior tests first.
- Fix changes the meaning of data at rest → breaking change: version encoding, migrate, human merges.
- Agent wants a new dependency → it proposes and stops; human curates.
- Agent reads untrusted content → assume hijacked: no secrets, scoped tools, human gate on irreversible acts.
- "This test has never failed" → smell: break the mechanism and watch it go red.
- Concurrency code from AI → forced-collision test; never accept the agent's own concurrency test.
- Reviewers approving diffs they didn't fully read → add the Inquisitor.
- Implement only one thing → the **adversarial reviewer in CI**.

## Thresholds the author commits to
| What | Number |
|---|---|
| Tipping point | 10th–50th file |
| Tier 1 file | 10–20 lines (≤ 20 in the scorecard) |
| Instruction file | well under 40–50k tokens |
| Inner test loop / full suite | < 30 s / < 5 min |
| Meaningful coverage | ~65%; > 75% after AI pass → check for vacuous tests |
| Suite runtime alert | +10% without matching test growth |
| Instruction evals | 10 trials/cell, coarse floors (0.8) |
| Main agent context | 30–40% capacity (GSD) |
| Plan tasks | 2–5 min each, exact command + expected output |
| Dependency cooldown | `minimumReleaseAge` 4320 (3 days) |
| CPD minimumTokens | 50–100 |
| Concurrency test | ≥ 20 threads, ≥ 100 invocations, ARM in CI |
| Simulation healthy band | e.g. 0.5–1.5; judge aggregates, never one run |
| Health scorecard | 0–16 Foundation · 17–33 Developing · 34–49 Mature · 50–66 Complete |
| Consultation suggestions | top 3, each citing a line |

## Adoption roadmap (add each when its cost starts to bite)
Day One (~20 min): package-private + feature packages, `.specs/` + OpenAPI, ten-invariant CLAUDE.md, one ArchitectureTest, save-state commits → Week 1–2: enforcers (annotations, test topology) → first external consumer: contract tests → first autonomous agent: supply-chain gate + sandbox → second committer: CI law (merge-blocking) → unread approvals: Inquisitor.

## Tells & smells
- Fluent, confident 400-line diff → enforcement gap; trust detectors, not reading.
- Agent re-asks/re-decides settled things → missing STATE.md / Tier 1 / lineage.
- Backlog never shrinks → Jevons; scale enforcement, don't slow generation.
- Coding 10× faster, cycle time −18% → org bottleneck (PCE); fix handoffs.
- Volume ↑ with escaped defects and review-hours ↑ → "bought speed, sold structure."
- Tool claims to make architecture safe → distrust; specs order work, tests enforce.
