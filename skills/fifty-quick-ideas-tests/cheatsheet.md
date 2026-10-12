# Cheatsheet — Decision Rules

## When you don't know what to test
| Situation | Do this |
|---|---|
| Quality means different things to different roles | Build the 5-level quality pyramid; quantify each level |
| Exploratory session feels like proving the feature works | Reframe around **capabilities**, not features |
| New/unfamiliar domain | Run **always/never**, then refute each statement |
| Stuck on happy path | Walk **SHADED FIGS** (scary/angry/delinquent/embarrassing/desolate/forgetful/indecisive/greedy/stressful) |
| Hard-to-test quality ("must be fast") | **Quantify anyway** as numbers/intervals + concrete scenarios |
| Cross-cutting concern (look&feel, perf) | Risk **checklist**, 5–9 key risks, Do-Confirm |
| Need durable, prioritisable test plan | **ACC matrix** with per-capability risk scores |
| Single person dominates the workshop | Give **everyone a pen**; split into groups of 3–4 |

## Designing checks — decision rules
- **If the example list is long/complex → the story refinement isn't done.** Find the missing concept; split validation from processing; group by commonality.
- **If an example just restates the rule (formula) → replace it** with ≥2 concrete boundary values. Intervals OK only for *output* equivalence.
- **If acceptance criteria contain clicks/reloads → strip the mechanics.** Describe *what*, not *how*; mechanics go in the automation layer.
- **If inputs and outputs are interleaved and hard to separate → the team doesn't understand the story.** Re-discuss; don't clean up.
- **If a scenario has multiple `When`s or conjunctions → split it.** One test, one topic.
- **If a table keeps growing columns → split per concept** into smaller tables (one rule each).
- **Always pair a key example with counter-examples** varying one input at a time.
- **Write the `Then` / right-hand columns first.**
- **Boundary explosion = modelling smell, not a testing problem.** Try 3–4 models.
- **Who resolves a failure?** programmer → technical test; business → business test; both → split.

## Given-When-Then tenses
| Clause | Tense | Role |
|---|---|---|
| Given | past, passive | parameters / preconditions |
| When | present, active | the *single* action under test |
| Then | future, passive | expected outcomes |

## Testability — flakiness fixes
| Symptom | Fix |
|---|---|
| DB test pollution (sync, 1 process) | Wrap in transaction, **roll back**; set globally |
| Async/distributed data | Consistency in **set-up**, not teardown |
| Time/animation/expiry tests | **Business time** clock; move it instantly |
| `sleep(N)` flakiness | **Wait for an event**; else sample every ~100ms |
| Partial file reads | **Atomic** resource: temp-name → rename/move |
| Test only checks file exists | Add marker file / queue message / write-lock |
| UI tests slow & brittle | **Minimise UI**; set-up below the skin; rephrase as domain |
| Forced to drive via UI | **Three-layer** automation (decisions/workflow/technical) |
| Expensive pre-release measurement | Measure in **production** (only ~⅓ of ideas improve their metric) |

## Managing the suite — defaults
- **Developers automate; whole team decides what to test.** Never a separate automation squad.
- **Organise by business activity**, not work items/stories.
- **Tests live in the same VCS as the code.**
- **Coverage is diagnostic, never a target** — targets get gamed. Low % = useful signal; high % = meaningless. If forced public, use multiple dimensions.
- **Decide purpose first, then minimal coverage area.** Business-oriented unit tests are fine.
- **Optimise for reading, not writing** — 30 min more now saves days later; keep readability over DRY in business tests.
- **Name tests as search keywords**; no conjunctions (and/or/not = unfocused).
- **Explain *why* in the intro**; body handles what/how. No generic user-story templates.
- **Measure half-life** (check-ins/test) → volatile vs weak vs fragile.
- **Chaos monkey periodically** — break critical parts, drive by *risk* not technical code.
- **Split just-in-case tests** from key examples but **reuse the same automation**; primary CI = key examples, secondary = extras.

## Tells & smells
- Multiple `When`s / conjunctions in name → test does too much.
- Formula in a table → hidden type/timezone/boundary assumptions.
- Magic time constant (`ONE_MONTH_AGO`) → leap-year/DST bug waiting.
- Green in-memory DB, prod on Oracle → misleading; "worse than no automation".
- "Run 5×, pass if any" → masks real defects.
- Log/console error *spikes* → early warning of compound failure.
- Generic test name ("simple acceptance test") → duplication factory.
- Clean-up code you depend on → skipped on failure, destroys evidence.
