# Appendix A: The Vibe Architecture Health Scorecard

## Core Idea
A 33-row, 0–2 audit of how completely a codebase implements the book's disciplines (max 66). Rows follow the book's four parts, so a low-scoring section points straight at what to reread. It is the audit companion to the Incremental Adoption Roadmap (Ch 25).

## Frameworks Introduced
- **The Health Scorecard (0/1/2 scoring)**:
  - When to use: baseline audit of an existing codebase, periodic (annual) re-audit, prioritizing the next guardrail.
  - How: score each row **0** = not implemented (exposure open); **1** = partial, manual, or team-dependent (relies on someone remembering); **2** = automated, consistent, merge-blocking where applicable (runs without human attention). Sum, interpret via the Scoring Guide, and if below 27 follow the Priority Order.
- **Priority Order for Teams Starting From Zero**: five steps, each a prerequisite for the next (see table).

## Key Concepts
- **Score 2**: the guardrail runs without human attention.
- **Score 1**: it exists but depends on a person remembering.
- **Score 0**: open exposure.
- **"Isolated chaos"**: a sandboxed agent that still crosses package boundaries freely is not safer, just isolated.
- **Maturity bands**: Foundation (0–16), Developing (17–33), Mature (34–49), Complete stack (50–66).

## Mental Models
- Think of a 1 as **a 2 waiting for automation**: the work is to remove the human memory dependency.
- Use the lowest-scoring part as **the part of the book to reread**.
- At the top band, **maintain, don't add process for its own sake**.

## Anti-patterns
- **Sandboxing (items 22–23) before boundary tests (items 7–8)**: isolated chaos.
- **Architectural tests run weekly or optionally**: they must be in the default test run (item 8).
- **Piling on tooling before Part I and items 1–8 are solid** (Foundation band).

## Reference Tables
**Part I: Foundation**

| # | Discipline |
|---|---|
| 1 | Context diet: Tier 1 invariant file ≤ 20 lines, non-contradictory |
| 2 | Tier 2 scoping: directory-level rules exist for high-risk modules |
| 3 | Build/test commands documented in root context file |
| 4 | AI not used for prohibited-category code (crypto, regulated outputs, safety-critical paths) |

**Part II: Engineering the Guardrails**

| # | Discipline |
|---|---|
| 5 | Source annotations (`@AIContract`, `@AILocked`) on frozen public APIs |
| 6 | Guardrail regeneration enforced: platform files regenerate from annotations every build; drift fails the build |
| 7 | ArchUnit boundary rules: ≥ 3 layer/domain rules active in test suite |
| 8 | Architectural tests in default test run (not weekly, not optional) |
| 9 | Living architecture diagram regenerates from code every build |
| 10 | Spec directory (`.specs/` or `docs/`) version-controlled and AI-readable |
| 11 | BDD feature files for core domain flows |
| 12 | `@AITestDriven` on critical domain classes (failing test before implementation) |
| 13 | Instruction-layer evals: task bank measures whether standing rules bind; runs on any change to instruction files |

**Part III: The Practice**

| # | Discipline |
|---|---|
| 14 | Skills forged from your codebase (evidence-cited to real files), not borrowed generic ones |
| 15 | Context engineered as a runtime invariant: main window lean, heavy work delegated to fresh, scoped subagent contexts |

**Part IV: Handling the Hard Stuff**

| # | Discipline |
|---|---|
| 16 | Concurrency detector (async-test-lib or equivalent) on shared-state classes |
| 17 | Performance contract: operation-count budgets asserted in the inner loop; latency vs. baseline in the nightly ring |
| 18 | Expand-contract migration discipline for all schema changes |
| 19 | Contract tests for every external API dependency |
| 20 | OpenAPI document version-controlled and consumer-registered |
| 21 | Supply-chain gate: frozen lockfile, CI build-file diff gate (age, license, known CVEs), agent proposes rather than installs dependencies |
| 22 | Sandbox isolation for autonomous agent runs (no ambient secrets, allowlisted egress) |
| 23 | Untrusted-context handling on all external sources (issues, web content, tool output) |
| 24 | Attacker agent: generator's edge-case talent pointed at your own contracts, in a sandbox, before production |
| 25 | Tests audited for passing for the wrong reason: mechanism assertions and mutation testing on critical suites (plus a simulation harness for emergent behavior) |
| 26 | All guardrails in CI: architectural and contract tests merge-blocking |
| 27 | Agent provenance: AI-authored commits identifiable in git history |
| 28 | `@AILocked` checks merge-blocking in CI |
| 29 | Inquisitor: adversarial reviewer configured and running on PRs |
| 30 | Consultation loop: pre-push adversarial checklist in team workflow |
| 31 | Prompt lineage: system prompts and context files version-controlled |
| 32 | Model pinning and routing: exact model IDs pinned in versioned config, upgrades gated by golden-prompt replay, work routed by decision density |
| 33 | Micro-commit discipline: commits at each verified sub-task boundary |

**Scoring Guide** (33 rows × 2 = max 66)

| Total | Interpretation |
|---|---|
| 0–16 | **Foundation phase.** Focus on Part I and the architectural tests (items 1–8) before adding more tooling. |
| 17–33 | **Developing.** Core guardrails exist; harden CI enforcement and fill the Part IV gaps. |
| 34–49 | **Mature.** Most exposure covered; audit annually and adjust for codebase changes. |
| 50–66 | **Vibe Architecture complete stack.** Maintain; don't add process for its own sake. |

**Priority Order for teams scoring below 27** (each step is a prerequisite for the next)

| Step | Items | What | Why |
|---|---|---|---|
| 1 | 3, 7, 8 | ArchUnit in the default test run with layer rules | Highest ROI, lowest effort |
| 2 | 1, 2 | Context diet | Stops context rot immediately |
| 3 | 5, 6 | Source annotations on frozen APIs, regeneration enforced | Prevents the most expensive category of breakage |
| 4 | 26, 28 | Move enforcement to CI | Guardrails become team-wide, not individual |
| 5 | 29, 30 | Inquisitor and consultation loop | Closes the review gap |

Rule: don't implement items 22–23 (sandbox / untrusted context) before items 7–8.

## Worked Example
*Illustrative application of the author's rules:* a team audits itself: CLAUDE.md is 60 lines (item 1 = 0), ArchUnit exists but runs only in a weekly job (7 = 1, 8 = 0), contract tests exist for two of five external APIs (19 = 1), wip commits happen by habit (33 = 1), and nothing else is in place. The total lands in the Foundation band (0–16) and below 27, so the next moves are, in order: put ArchUnit with layer rules into the default run (items 3, 7, 8), trim the context file to ≤ 20 non-contradictory lines (1, 2), then annotate frozen APIs with enforced regeneration (5, 6). They resist the urge to set up a sandbox first.

## Key Takeaways
1. Score 0/1/2; a 2 means it runs without human attention.
2. Maximum 66; bands at 16 / 33 / 49 tell you where to focus.
3. Below 27, follow the five-step priority order: ArchUnit → context diet → annotations → CI enforcement → Inquisitor.
4. Boundaries before sandboxes.
5. Mature teams re-audit annually; complete-stack teams maintain rather than add process.

## Connects To
- **Ch 25**: Incremental Adoption Roadmap (the scorecard audits it).
- **Ch 3 / 3f / 4 / 4b / 5 / 6 / 7 / 16 / 17 / 17b / 18 / 18b / 19 / 20 / 20b / 21 / 22 / 23 / 23b / 24**: each row's source chapter.
- **App B**: per-language implementations for each scored discipline.
