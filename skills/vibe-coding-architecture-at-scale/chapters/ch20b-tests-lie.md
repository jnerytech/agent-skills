# Chapter 20b: Green for the Wrong Reason: When the Tests Lie

## Core Idea
In an AI-speed codebase the test suite is the constitution, the only artifact the generator is actually bound by. A test that passes for the wrong reason is a forged signature on that document, and nobody looks twice because green ends the conversation. Before promoting any guardrail to branch-level law (Ch 21), audit what each green result actually proves: read the red, assert mechanisms, mutation-test, drive full lifecycles, key identity off objects, and distrust the pipeline itself.

## Frameworks Introduced
- **The One Question That Finds This Bug Class**: "If I deliberately broke *only* the mechanism this test's name promises to check, and nothing else, would *this exact test* go red?"
  - When to use: before trusting any test as a merge gate, and especially tests that have never failed.
  - How: if you can't answer with confidence, break the mechanism in one commit and watch. If a *different* test catches it, or nothing does, the test was never wired to that mechanism. Revert. It costs one commit and a revert.
- **The Disciplines That Hold** (the fix isn't more tests, it's disciplines applied to the tests you have):
  - When to use: as a standing audit before Ch 21 promotes gates to law.
  - How: (1) **Failing-test-first, and read the failure.** Confirm the red is red *for the right reason*. `expected 1 SELECT but got 151` (Ch 17b) is right. An unrelated `NullPointerException` means your assertion never ran. (2) **Assert the mechanism, not the outcome.** "This detector fires on this pattern," not "the run fails." Noise can satisfy an outcome assertion. (3) **Mutation-test the tests** (DeMillo, Lipton & Sayward 1978; PIT/pitest for Java): survived mutants show lines nobody would notice running wrong. (4) **Drive full lifecycles, never half**: acquire/release, open/close, wait/wake, start/stop. (5) **Identity from objects, never from prose**: key findings, records and suppressions off stable structural fields. (6) **Audit what green actually proves**: for each gate, know what must be true for it to fail. (7) **Treat "this test has never failed" as a smell, not a compliment**: prefer properties (QuickCheck) over hand-picked examples.
- **Audit First, Promote Second**: a gate that blocks merges on a forged signature is worse than no gate, because it manufactures false confidence just when the team decides to trust automation over judgment.
  - When to use: before any test becomes a merge-blocking CI gate.
  - How: run the disciplines above on the gate's tests, then promote.

## Key Concepts
- **Green for the wrong reason**: a test that has always passed for a reason unrelated to what it claims to verify. It's the most dangerous shape because it survives audits that only check pass rates.
- **Drained evidence**: a two-phase (record → analyze) detector reads a counter after it has legitimately returned to rest. It asks "how many were waiting?" but reads "how many are waiting *now*?", which is always 0, so it gives false negatives.
- **Synthetic half-lifecycle**: a test that acquires but never releases, holding state artificially so the detector fires. It's a different scenario that happens to produce the same reading, and it hides the drained-evidence bug.
- **Identity from prose**: deriving keys by slicing human-readable text (e.g. at the first colon). Collisions merge unrelated findings, and wording changes silently re-key them.
- **Untested headline case**: a unit whose tests cover the empty and disabled paths but never the one input it exists to handle. Coverage of the class isn't coverage of the claim.
- **Untested documented contract**: a stated property (e.g. idempotency) with no test exercising it. It's asserted in a comment and hoped for everywhere else.
- **Pipe exit-code lie**: `run-tests | tail` reports `tail`'s exit code, so a red suite reads green. Check `${PIPESTATUS[0]}` (or `set -o pipefail`).
- **Pesticide paradox (Beizer)**: a suite that keeps killing the same bug class stops finding new ones.
- **Coverage as Goodhart's law**: line and branch coverage correlate only weakly with fault detection (Inozemtseva & Holmes, ICSE 2014).

## Mental Models
- Think of the test suite as a constitution with a forgery problem. Every guardrail cashes out in one boolean, and the boolean is only a fact about the code if the test was built correctly.
- Think of a green-for-the-wrong-reason test as a small defeat device against your own pipeline. Volkswagen's diesels passed for years because tests asserted the outcome on the prescribed cycle, not the mechanism. A WVU team broke the conditions (real roads) and the green verdict didn't follow.
- Coverage tells you the line ran. Mutation testing tells you whether anything would notice if it ran wrong.
- Dijkstra: testing shows the presence of bugs, never their absence. A test that has never been red has never shown that it can be.

## Anti-patterns
- **Outcome assertions** ("the run fails"): any of a hundred unrelated failures can satisfy them.
- **Reading evidence after it drains**: mixing live-captured facts with cold-read state.
- **Half-lifecycle tests**: rigging the room so the bug's state is never entered.
- **Keys sliced from report text**: 14 detectors collapse onto one key, and suppressing one silently suppresses 13.
- **Name-substring heuristics in place of real analysis**: e.g. flagging any method containing `tryLockHelper`.
- **Tests that call `analyze()` exactly once**: idempotency and retry bugs never surface.
- **`| tail` / `| tee` in CI without pipefail**: the pipe lies every run.
- **Trusting the audit tool unchecked**: a mutation that silently failed to apply "proved" a test had teeth by running the original.

## Code Examples
```bash
# Lies: pipeline exit code is tail's, so a red suite reports success
run-tests | tail -n 50

# Honest: check the test runner's own status
run-tests | tail -n 50
exit "${PIPESTATUS[0]}"
# or: set -o pipefail at the top of the CI script
```
- **What it demonstrates**: tooling around the tests can forge green without a single wrong line of test logic.

## Reference Tables
| Failure shape (from async-test-lib, ~140 detectors) | What happened | Discipline that catches it |
|---|---|---|
| Drained evidence | "Waiting" counter read after run completed → always 0 → starvation missed for months | Prove phase-2 evidence still means what it meant in phase 1 |
| Synthetic half-lifecycle | Tests added waiters, never released → detector "proved" | Drive full lifecycles |
| Green for wrong reason | "Run fails" passed via livelock false positive on JVM daemon threads (GC, JIT); fixing that turned the test red | Assert mechanism; break-the-mechanism question |
| Identity from prose | Key = text before first colon; 14 detectors shared one key; one suppression hid 13 | Stable structural keys (detector class, rule ID, location) |
| Untested headline case | Sleep-while-holding-lock detector couldn't see `synchronized(lock){ sleep(); }`; tests covered only empty/disabled paths | Mutation testing; test the class-comment claim |
| Untested contract | `analyze()` documented idempotent but appended to an instance field → duplicates on 2nd call | Test the contract as written (call twice); property tests |
| Pipe lie | `run-tests \| tail` exit 0 on red suite | `PIPESTATUS[0]` / `pipefail` |
| Audit-tool lie | Mutation silently not applied; original test ran and passed | Verify the tool did what you asked |

## Worked Example
An integration test in async-test-lib asserted, in effect, "the run fails," and it was green for its whole life. The real cause was a livelock detector false-positiving on idle JVM daemon threads (GC housekeeping, JIT compiler threads) as starved application threads. A routine fix taught the detector to exclude daemon threads, and the integration test immediately turned red. The failure it had been riding was gone, and the detection path its name promised had never fired once. Applying the One Question beforehand ("break only that detection path; does *this* test go red?") would have exposed it the day it was written. The fix is to rewrite the assertion around the mechanism: the specific detector fires on the specific pattern.

## Why It Works / Failure Mode
- **The break-the-mechanism question and mutation testing** work because they test the *test*: they make the claimed mechanism fail on purpose and check that the specific gate notices. That turns green from an assumption into evidence. They fail when the mutation or break doesn't actually apply (verify the tool), or when only aggregate pass rates are audited.
- **Asserting the mechanism** works because a mechanism assertion can only be satisfied by the thing you meant, while an outcome assertion can be satisfied by noise. It also limits the Inquisitor (Ch 22): reviewing a diff against tests inherits every forged signature already in those tests.

## Key Takeaways
1. The suite is the constitution. A test green for the wrong reason is a forged signature that nobody inspects.
2. Ask of every trusted test: would breaking *only* its promised mechanism turn *this* test red?
3. Read why red is red before making it green. Assert mechanisms, not outcomes.
4. Mutation-test (PIT). Coverage says the line ran, not that anything would notice it running wrong.
5. Drive full lifecycles, key identity off objects not prose, and test documented contracts as written.
6. Distrust the plumbing: pipes (`PIPESTATUS`/`pipefail`) and audit tools need their own verification.
7. "Never failed" is a smell. Audit first, promote to CI law second.

## Connects To
- **Ch 4**: `@AIContract` pins identity to the signature, not the docstring, the same as identity from objects.
- **Ch 5**: architectural tests as executable law, and failing-test-first.
- **Ch 17 / 17b**: async-test-lib as the concurrency answer; the query-count assertion (`expected 1 SELECT but got 151`).
- **Ch 18**: contract tests that also need auditing.
- **Ch 20**: attacker-generated red tests assume green means something, and this chapter is the other half of that.
- **Ch 21**: promotion to branch-level law, valid only after this audit.
- **Ch 22**: the Inquisitor's blind spot, forged signatures in the tests it checks diffs against.
- **Mutation testing (DeMillo/Lipton/Sayward 1978; PIT)**; **QuickCheck (Claessen & Hughes, ICFP 2000)**; **Pesticide paradox (Beizer)**; **Goodhart's law**; **Dijkstra, "The Humble Programmer"**; **Inozemtseva & Holmes, ICSE 2014**; **Volkswagen dieselgate**.
