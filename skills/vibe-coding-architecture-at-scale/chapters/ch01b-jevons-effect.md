# Chapter 1b: The Jevons Effect

## Core Idea
Making code cheaper to produce does not drain the backlog — it expands demand (Jevons, *The Coal Question*, 1865), so AI velocity yields more code, harder code, and a widening **enforcement gap** between generation speed and human review speed. The only answer is guardrails that run at AI speed.

## Frameworks Introduced
- **The Jevons Effect (applied to codebases)**: when the cost per unit of output falls, total consumption rises until a new equilibrium at higher output and roughly constant spare capacity.
  - When to use: countering the management fantasy that "2x faster = half the backlog"; planning guardrail investment alongside AI adoption.
  - How: expect (1) the roadmap to expand to fill throughput — stakeholders who chose 3 features now request 7; (2) previously prohibitive features become routine; (3) no spare capacity materializes. Treat this as a structural law, not a dysfunction — nobody is causing it; the system is.
- **Complexity Scales With Appetite**: a team that ships in one week what took a month gets assigned month-sized problems. Architectural surface area grows in two dimensions at once — **volume** and **complexity** (deeper call graphs, more shared state, subtler coupling).
  - When to use: sizing the risk of a team whose demonstrated throughput just jumped.
  - How: assume the next quarter's work is harder, not just bigger; a guardrail system calibrated for human-speed output is "not merely slow. It is invisible."
- **The Enforcement Gap**: the structural gap between the velocity of creation (thousands of lines/hour) and the velocity of enforcement (human reading speed, unchanged). While open, violations accumulate quietly in clean idiomatic code and compound.
  - When to use: deciding where a boundary rule should live.
  - How: ask "at what speed does this rule enforce itself?" A rule in someone's memory enforces at human speed via PR comments — fine when generation ≈ review speed, broken at 10x.
- **Matching Enforcement Velocity to Generation Velocity**: the operating premise of Vibe Architecture.
  - When to use: every category of structural violation AI velocity makes statistically more likely.
  - How: (1) don't slow the AI — that forfeits the Jevons gain while keeping the risk; (2) put each rule in an automated mechanism in the feedback loop the AI already watches (architectural test, package-boundary rule that turns the build red on import, contract check before a PR is opened); (3) return the violation to the assistant as a precise signal; (4) correct it *in the same session* it was introduced. "Not reviewed. Not discussed. Caught."

## Key Concepts
- **Jevons paradox**: efficiency gains increase aggregate consumption rather than reduce it.
- **Backlog equilibrium**: throughput gains are absorbed by product discovery and competitive pressure; the backlog never drains proportionally.
- **Per-line violation probability**: every unit of code carries a non-zero chance of a boundary violation, schema drift, unwanted coupling or concurrency edge case — so risk scales with volume.
- **Human-speed accumulation**: a few hundred production lines per developer per day, which a diligent review cycle can mostly match.
- **Buried violation**: a boundary break in the middle of a 400-line diff that also carries the wanted feature, with no stylistic tell.
- **Load-bearing wrong design**: a violation merged to main becomes part of the next release and then a dependency for future work.
- **Zero review lag**: property of a check that fires before a PR exists (e.g. contract check on payload change).

## Mental Models
- Think of AI velocity as cheaper coal: you will burn more of it, not less — budget for the extra structural load.
- Use "does it run in the loop the AI is already watching?" as the test for whether a guardrail can keep up.
- Think of a build-breaking boundary rule as a reviewer with lower latency than any human.
- Prefer catching over reviewing: reviewers approve buried violations "not out of negligence but because no human can outread a generator."

## Anti-patterns
- **Expecting the backlog to shrink**: the roadmap recalibrates to capability; planning on breathing room fails.
- **Slowing the AI down to stay safe**: surrenders the benefit while keeping the architectural risk.
- **Rules that live in memory**: "payment must not depend on user-profile" enforced only by whoever remembers it in PR review breaks at 10x generation.
- **Relying on PR review for 400-line AI diffs**: violation sits mid-diff in clean, well-tested code and gets approved.
- **Human-speed guardrail systems under AI-speed load**: they become invisible, not just slow.

## Worked Example
**The memory rule that stopped working.** Rule: "the payment module must not depend on the user-profile module." At human speed: a developer notices the import in a PR, comments, author fixes before merge. At AI speed: the PR is 400 lines, the import sits in the middle alongside the requested feature, written in idiomatic, tested code. Reviewer approves. The violation is in main, in the next release, about to become load-bearing. Fix: encode the rule as a package-boundary test that turns the build red the instant the AI imports across it — the AI sees the failure in its own loop and corrects it in-session.

## Why It Works / Failure Mode
- **Works**: automated checks cost nothing in flow when they run inside the AI's existing feedback loop, and their latency is lower than any reviewer's — enforcement speed rises with generation speed.
- **Fails**: when enforcement remains human (review, discussion, memory), its throughput is fixed while generation and complexity both grow; the gap widens and violations compound silently. Jevons does not make erosion inevitable — it makes human-speed enforcement insufficient.

## Key Takeaways
1. AI velocity never drains the backlog; demand expands to a new equilibrium.
2. Volume and complexity grow together: teams get harder problems because they're faster.
3. Every line carries non-zero violation risk, so risk scales with generation rate; review rate doesn't.
4. Don't slow the AI; make guardrails as fast as generation.
5. Catch violations automatically, feed them back as precise signals, fix them in the same session.

## Connects To
- **Ch 1**: the entropy of the prompt is the per-change force; Jevons is the volume multiplier.
- **Ch 2**: reframes the engineer's job around this gap (Shift Left, Guide Right).
- **Ch 5**: architectural unit tests — the canonical AI-speed boundary check.
- **Ch 18 / Ch 21**: contract checks before PRs and CI as branch-level law close the gap at the merge gate.
- **Jevons paradox (W. S. Jevons, *The Coal Question*, 1865)**; **induced demand**; **fitness functions (Ford/Parsons)** as automated architectural checks.
