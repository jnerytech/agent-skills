# Chapter 22: The Two-AI Gripe: Adversarial Review Pipelines

## Core Idea
When syntax is free, human review time is the binding constraint, and AI quietly disables the human reviewer through the LGTM reflex. Self-review fails by construction: the generator suffers confirmation bias about its own output. Instead, add structural friction: a second AI, the **Inquisitor**, in a separate process with an opposing objective function. It reads only the diff and the source-resident rules, blocks merges with citation-backed structured gripes, and feeds them back to the Generator machine-to-machine. Humans arbitrate only real disputes about whether a rule should exist.

## Frameworks Introduced
- **The Two-AI Gripe (Generator vs Inquisitor)**: adversarial review modeled on GANs. One agent generates to succeed, and another is "paid to be unhappy" and hunts architectural erosion.
  - When to use: AI-generated PRs exceed what humans can review line by line, and the structural/architectural first pass must be exhaustive.
  - How: install the Inquisitor as the "higher-trust review agent" Ch 21 deferred ("Ch 21 built the courthouse; this chapter installs the prosecutor"). Enforce the **three mandatory separations**, because sharing any one of them inherits the generator's blind spot:
    1. **Separate objective function**: the Generator helps ship the feature. The Inquisitor is rewarded only for finding erosion and violations.
    2. **Separate context window**: it never sees the conversation or the Generator's rationalizations, only the raw Git diff and the rules.
    3. **Separate runtime**: it runs as a blocking CI stage (GitHub Action / GitLab job) on the PR, isolated from the local IDE.
- **Source-Resident Rules as the Inquisitor's Authority**: the Inquisitor never argues from taste. It compares the diff against committed, human-owned, machine-readable artifacts.
  - When to use: always. A reviewer arguing from its own taste is "noise with authority".
  - How: feed it the VibeTags exports (Ch 4, e.g. `<contract_signatures>`), ArchUnit boundary rules and C4/Modulith diagrams (Ch 5, 6), OpenAPI plus migration history (Ch 18), and the @AILocked/@AIRegulation set cross-referenced with Ch 21's provenance signal. A gripe is a citation, not an opinion.
- **Anatomy of a Gripe**: a structured, machine-actionable block output. Target, Violation (with rule citation), Evidence (file:line), Gripe (plain-language why), Remediation (concrete fix).
  - When to use: every block the Inquisitor emits. Never "consider refactoring."
  - How: Evidence makes it falsifiable in seconds, the rule citation makes it non-negotiable, and Remediation turns it into a ready prompt for the next actor.
- **The Gripe Loop (keeping friction cheap)**: (1) the Generator takes the path of least resistance and crosses a boundary. (2) The local loop is green, because the violation is structural. (3) The Inquisitor blocks the PR with a structured gripe. (4) You paste the gripe verbatim into the Generator: "Fix your own layout; do not weaken the rule or the test." (5) The Generator pushes a fix, and the Inquisitor re-runs and returns ALL CLEAR. The human writes no review feedback.
- **The Consultation Loop (pre-push, advisory)**: before opening a PR, interrogate a fresh agent with five adversarial questions. It is proactive, dev-triggered and non-blocking, unlike the reactive, rule-bound, merge-authoritative Inquisitor.
  - When to use: before every push of non-trivial work, to catch issues before the Inquisitor or production does.
  - How: use a separate context window (diff plus repo only), an explicit adversarial frame per question ("hostile reviewer who assumes this is broken"), and a scope clause ending each prompt ("answer this only; cite a line; do not reassure me; if no evidence, say so"). Ask five questions: **Are we done?** (enumerate the spec's acceptance criteria and check each against the diff), **Is this production ready?** (observability, timeout/error handling, config externalization, fail closed and loud), **Does it scale?** (the model names complexity/N+1 it can see and admits what needs a realistic load test), **Is it secure?** (what new untrusted input, crossing which boundary, and where would you attack), and **Suggestions** (top three changes ranked by risk reduced, each citing a line, because taste gets no vote).

## Key Concepts
- **Collaboration paradox**: asking the generating session to review itself yields confirmation bias by construction. It pronounces its own work "clean and idiomatic."
- **Structural friction**: deliberate adversarial tension between two minds with opposite objectives.
- **Inquisitor**: the adversarial CI review agent. It may block, and it may never merge or approve.
- **LGTM reflex**: a fatigued human skims a large, clean, confident diff, leaves one nit and approves. Scrutiny falls as diff size and polish rise.
- **Automation bias**: the prior shifts to "approve" because the machine is usually right, and fluent prose lowers vigilance.
- **Review as ritual**: "100% of PRs approved" measures a signature, not a safety net (90 seconds against 2,000 lines).
- **Brake clause**: "If you find nothing, say so in one line and stop; do not invent problems." It prevents a nitpicking denial-of-service.
- **Single point of capture**: an Inquisitor that could edit the rules it enforces or approve peers. The prosecutor must not be the judge or rewrite the law.

## Mental Models
- Think of the Inquisitor as a GAN discriminator for architecture: opposing objectives produce fidelity neither side reaches alone.
- Use "bounded by the rules, hostile within them" as the design target. Adversarial does not mean unbounded.
- Think of the human gate and the Inquisitor as guarding different decisions. Humans decide *what gets built* and *what the rules are*. The Inquisitor checks *whether what was built matches the already-approved rules*. When Generator and Inquisitor disagree, they have surfaced a rules gap, and escalating it is correct behavior, not failure.
- Do not ask humans to do what humans predictably fail at. Give the exhaustive first pass to a reviewer that doesn't fatigue or skim, and isn't flattered by clean syntax.

## Anti-patterns
- **Self-review by the generating session**: a mutual admiration society of one.
- **"A human will catch it in PR review"**: no one holds a 2,000-line, 12-file diff in working memory, and reviewer throughput is biologically fixed.
- **Taste-based AI review**: noise with authority that the team learns to rubber-stamp, which rebuilds the problem with extra latency.
- **Inquisitor without a brake**: invents problems and DoSes your own pipeline.
- **Vague gripes ("consider refactoring")**: the low-signal noise that made human review the bottleneck.
- **Letting the Inquisitor merge, approve or edit enforcers**: turns the guard into a capture point.
- **Letting the consultation loop become a second gate**: it rots into a gate nobody trusts. Keep it advisory.
- **Unbounded suggestion requests**: an infinite nitpick spiral. Cap at three, line-cited.

## Code Examples
```text
You are a ruthlessly pedantic software architect. Your only job is to find structural
erosion, hidden technical debt, and compliance violations in the provided Git diff.
Assume the author was rushed and actively hid shortcuts behind clean-looking syntax.
Judge the diff against the project's source-resident rules, not your own taste.
If you find a violation, block the merge and document the gripe in the required
structured form. If you find nothing, say so in one line and stop, and do not
invent problems.
```
- **What it demonstrates**: the Inquisitor system prompt, adversarial by construction, rule-bound and with a brake.

```text
CI Blocked: Architectural Gripe
- Target: com.example.order.OrderService
- Violation: Crossed-boundary reference (ArchUnit rule order-must-not-depend-on-billing)
- Evidence: new import com.example.billing.BillingService; at OrderService.java:14
- Gripe: "The diff compiles and the feature works, but order is a domain module that
  must not depend on billing infrastructure. This is tight coupling disguised behind
  clean syntax."
- Remediation: Remove the direct import. Route the call through the published
  BillingPort interface, or emit an OrderPlaced event for billing to consume.
```
- **What it demonstrates**: a falsifiable, rule-cited, machine-actionable gripe that can be pasted straight into the Generator.

## Reference Tables
| | Inquisitor | Consultation agent |
|---|---|---|
| Trigger | Reactive, CI on PR | Proactive, developer-triggered pre-push |
| Authority | Merge-blocking | Advisory, blocks nothing |
| Speaks in | Citations to committed rules | Opinions, scoped and line-cited |
| Context | Diff + source-resident rules | Diff + repo, fresh window |
| Risk if misused | Nitpick DoS, capture point | Rots into an untrusted second gate |

## Worked Example
**The BigDecimal signature break.** VibeTags exports:
```xml
<contract_signatures>
  <element path="com.example.PricingService.calculatePrice">
    <reason>Signature locked by OpenAPI v2 contract.</reason>
  </element>
</contract_signatures>
```
Asked to "improve precision", the Generator changes `calculatePrice` from `double` to `BigDecimal` and updates every in-repo caller. It compiles, local tests pass, and the assistant reports success in good faith. The Inquisitor diffs the change against `<contract_signatures>` and sees in one step what the local compiler cannot: a signature the outside world binds to was altered. It doesn't need to understand pricing, only to compare a frozen declaration against a diff, a narrow, mechanical, adversarial task LLMs do reliably.

**Consultation-loop exchange.** Prompt: "You are a hostile reviewer. This diff is production-ready; prove it is not. Answer only on error handling. No reassurance." Answer: "`PaymentService.refund()` (line 88) calls the gateway with no timeout and no catch. A gateway hang stalls the request thread indefinitely; no fallback, nothing logged. Not production-ready on this axis." You fix it at your desk in seconds, before the Inquisitor ever sees it.

## Why It Works / Failure Mode
- **Why it works**: confirmation bias is structural, so the cure is structural. Opposing objective, separate context and separate runtime mean the reviewer never hears the rationalizations. Grounding every gripe in committed, human-written rules makes the output falsifiable and non-negotiable, and the Remediation field makes it a prompt, so the loop closes machine-to-machine. "Two agents in opposition catch what one agent in agreement never will."
- **Failure modes**: (a) it only grips on what it is pointed at. Rigorous on the repository's rules, it is blind to erosion no rule describes, so it shrinks human review residue to near zero but not to zero. (b) Without a brake, or with taste-based judgment, it becomes noise the team rubber-stamps. (c) If its scope includes the enforcers, or it can approve, it becomes a single point of capture.

## Key Takeaways
1. Never let the generating session review its own work. Self-review is confirmation bias by construction.
2. The LGTM reflex is structural, not laziness. Large, clean, confident diffs get the least scrutiny.
3. Build the Inquisitor with three mandatory separations: objective, context (diff and rules only) and runtime (blocking CI stage).
4. Ground every gripe in source-resident rules and emit structured Target/Violation/Evidence/Gripe/Remediation blocks.
5. Paste gripes verbatim back to the Generator ("do not weaken the rule or the test"). Humans arbitrate only real rule disputes.
6. Before pushing, run the five-question consultation loop in a fresh context with adversarial frames and scope clauses.
7. The Inquisitor may block, never merge, and its scope excludes the enforcers.

## Connects To
- **Ch 21**: the pipeline as law and the deferred "higher-trust review agent". The block-only, enforcer-excluded rule applies to the Inquisitor too.
- **Ch 4**: VibeTags exports (`<contract_signatures>`), @AILocked/@AIRegulation as the Inquisitor's inputs.
- **Ch 5, 6, 18**: ArchUnit rules, C4/Modulith diagrams, OpenAPI and migrations as citable law.
- **Ch 2**: beautifully deceptive code, now turned on the reviewer.
- **Ch 1, 7**: working-memory limits, and what review looks like when AI wrote the code.
- **Ch 8, 12**: human-gated loops. The human guards what gets built and the Inquisitor guards conformance.
- **Ch 19, 20**: the adversarial security framing pulled forward into the consultation loop.
- **Ch 20d**: the PR as review document. **Ch 23**: the forensic history of intent when a defect still lands.
- **GANs (generator/discriminator)**, **automation bias**.
