# Chapter 23b: Model Routing: The Right Brain for the Job

## Core Idea
Pinning the model (Ch 23) is defense; deciding *which* pinned model runs *which* work is design. Route by **decision density**, not task size: judgment work goes to the strongest model, mechanical work goes to a cheaper one behind a precise **work order**, deterministic gates verify the result, and the cheap tier must always be able to escalate back up.

## Frameworks Introduced
- **The Two-Tier Insight (judgment vs. mechanism)**: work splits into *judgment* (diagnosis, decomposing new problems, reviewing for architectural erosion), where errors are nonlinear and cascade into everything built on them, and *mechanism* (a rename across 40 files, a reference sweep, a formulaic transform, executing a fully specified order), where errors are linear, local, and caught by existing gates.
  - When to use: any harness with more than one model available, which by mid-2026 means every serious one.
  - How: (1) classify each piece of work by how much of it is "decide" versus "execute"; (2) send judgment to the strongest model; (3) send mechanism to a cheaper, faster model; (4) treat the roster like any other capacity decision, the way you would separate hot transactional writes from a cold analytics warehouse.
- **The Work Order Is the Contract**: the artifact that crosses the tier boundary is a brief, not code. The expensive model writes it and the cheap model executes it without re-deriving any of the judgment.
  - When to use: at every handoff from the judgment tier to the mechanism tier.
  - How: include **target state**, **constraints**, and **verification steps**: everything the cheap model needs to act safely and nothing it needs to decide. Treat it as a spec in the sense of Ch 7. If you cannot write it precisely, the work is not yet mechanical.
- **Route by Decision Density, Not Task Size**: the measure of tier is the share of decide-versus-execute work, not how many files the task touches.
  - When to use: when a large-looking task tempts you to use the big model, or a small-looking one tempts you to use the cheap model.
  - How: ask "is there a point after which the remaining work stops requiring judgment?" If yes, split there and write a work order. If no (e.g. bug hunting, where diagnosis *is* the whole task on every suspect), run full judgment mode throughout.
- **Routing as Versioned Config + Escalation Path (cascade with a verifier)**: per-agent model and reasoning-effort declarations live in versioned, reviewed config, and the cheap tier has an explicit, cheap, always-available "this needs judgment" handback.
  - When to use: as soon as routing is more than an ad-hoc per-session choice.
  - How: (1) extend the Ch 3d subagent slot with `model` and reasoning-effort fields; (2) each tier still pins an exact model ID; (3) any tier upgrade goes through the Ch 23.6 golden-prompt replay; (4) wire an escalation route (the Ch 11b stop rule applied by a machine to itself); (5) put the deterministic gates *between* tiers as the verifier (FrugalGPT: cheap first, verify, escalate on failure).

## Key Concepts
- **Judgment work**: work where a wrong call cascades nonlinearly: a wrong diagnosis yields an elegant, tested fix pointed at the wrong problem.
- **Mechanical work**: work with linear, bounded, cheap-to-catch failure cost; the same tests and review that would catch a human's slip catch it.
- **Work order**: precise, self-contained brief (target state, constraints, verification steps) written by the strong model for the cheap one.
- **Decision density**: the proportion of a task that is "decide" versus "execute"; this is the routing signal.
- **LLM cascade / FrugalGPT** (Chen, Zaharia, Zou 2023): try cheap, verify, escalate only on failure. It is safe only because of the verification step, not because the cheap model is trustworthy.
- **Escalation path**: the cheap tier's always-available route to hand work back up instead of producing confident wrong output.
- **Verification budget**: by analogy to an SRE error budget, how much cheap-tier output may be auto-accepted on the gates alone before a human reviews aggregate spend and quality.
- **Token budget per task class**: a running allowance (not a hard per-request ceiling) governing how much of the cascade runs unattended.
- **Context stripping on handoff**: routing tools such as ClaudeCode-Token-Guard send the cheaper model only what it needs, not the full session history.

## Mental Models
- Think of the strong model as **Larrey's surgeon** (Napoleonic triage): spend scarce judgment where a wrong call is fatal to everything downstream, not where the work *looks* important or prestigious.
- Think of the model roster as **a capacity tiering decision**, like row store versus column store, except the tiers are judgment and mechanism.
- Think of a **vague work order handed to a cheap model** as Ch 1's entropy reproduced one level down, with two agents compounding the drift.
- Use **McKinley's innovation tokens** framing: a roster is a budget denominated in judgment. Spend expensive tokens where a wrong call is expensive.

## Anti-patterns
- **Routing by prestige**: everything to the strongest model "to be safe." This is a cost decision dressed as caution: you pay judgment prices for accidental complexity (Brooks). Reserve the strong tier for essential complexity.
- **Routing by parsimony**: everything to the cheapest model because the budget line is the only number measured. This ships confident mediocrity into judgment calls and defers the cost, at a markup, to whoever debugs it.
- **Unpinned routing**: a router that silently reassigns models to tiers, chasing price or the newest release without a commit and review. This is Ch 23.6's unpinned dependency reborn and destroys the provable link between tier and output.
- **Cheap tier with no escape hatch**: a cheap model that cannot say "I'm out of my depth" is "a landmine wearing a discount price tag." Its failures look as confident as its successes, and the gates were calibrated for mechanical slips, not for judgment failures dressed as mechanical output.
- **Cascade without a verifier**: "just hoping the cheap model got it right."

## Code Examples
```yaml
# .claude/agents/rename-sweeper.md (frontmatter): routing policy as versioned config
---
name: rename-sweeper
description: Executes a fully specified work order (renames, reference sweeps). Escalates if any step needs a decision.
model: <cheap-tier exact pinned model ID>     # pinned, never "latest"
tools: Read, Edit, Bash
---
If the work order is ambiguous or a step requires judgment, STOP and return
"ESCALATE: <reason>" instead of guessing.
```
- **What it demonstrates**: a per-agent model declaration as reviewed, versioned routing policy with a built-in escalation path. (Illustrative reconstruction of the Ch 3d subagent slot extended with a `model` field.)

## Worked Example
The author contrasts two sessions from the same week, routed in opposite directions on purpose:
1. **Manuscript reorganization (tiered).** The strong model did pure judgment: it read the structure, diagnosed why the build-order scheme was broken, and decided the target chapter order with reasoning for each placement. This was a one-shot decision every later edit would inherit. With the order pinned as a work order, a cheaper model executed the file renames, the cross-reference sweep, and the rebuild. By then the work needed precision and patience, not diagnosis.
2. **Bug hunt across three repositories (untiered).** One agent per repo ran at full strength on all three. Bug hunting does not split into diagnose-then-execute: on every suspect you must decide whether it is cause or symptom, whether the fix addresses the mechanism, and whether it is safe in place. There was never a point where the remaining work stopped needing judgment, so there was no work order to hand off.

Result: the reorg touched *more* files but cost less judgment per file; the bug hunt touched *fewer* files but needed the strong model on each. Task size is a bad proxy, and decision density is the signal.

## Why It Works / Failure Mode
- **Two-tier + work order**: it works because judgment is paid for once, frozen into a spec, and then executed cheaply; mechanical errors stay linear and are caught by the gates this book already built (architecture tests, contract tests, coverage-on-diff, Inquisitor rules). It breaks first at **brief quality**, not executor competence. A precise order makes a cheap model safe, while a vague prompt does not become safe because the model is expensive. The expensive model is only more likely to notice its vagueness and ask, which is exactly the capability you pay for.
- **Cost governance (Jevons, Ch 1b)**: cheaper units do not shrink the bill. More tasks clear the bar at cheap-tier prices and ambitions recalibrate upward. Govern the aggregate, not the unit cost: set a token or verification budget per task class, a policy decision kept in project-level versioned config, not in one engineer's personal settings.

## Key Takeaways
1. Pinning answers "will the ground move?"; routing answers "which pinned model does this work?" Both belong in versioned config.
2. Route by decision density: judgment to the strongest model, mechanism to a cheap one.
3. The work order (target state, constraints, verification steps) is the contract between tiers, and its quality is what fails first.
4. Every downward route needs an explicit escalation path back up.
5. A cascade is safe only with a verifier in the middle, and the deterministic gates are that verifier.
6. Cheaper routing increases total consumption (Jevons), so budget the aggregate per task class, like an SRE error budget.
7. The Inquisitor (Ch 22) deserves the strongest model in the roster because its errors cascade.

## Connects To
- **Ch 23**: model pinning, golden-prompt replay, lineage records; routing extends the pinned dependency into a roster.
- **Ch 3d**: subagents as the "who does this, with what" slot; the model field is routing policy.
- **Ch 7**: a work order is a spec.
- **Ch 11b**: the stop rule, here applied by the cheap model to itself.
- **Ch 1b**: Jevons Effect at the token-spend layer.
- **Ch 22**: the Inquisitor is the role that deserves the strongest model.
- **Ch 5**: deterministic gates as the cascade verifier.
- **FrugalGPT (Chen/Zaharia/Zou 2023)**, **SRE error budgets**, **Brooks' essential vs. accidental complexity**, **McKinley's innovation tokens**, **Larrey's triage**.
