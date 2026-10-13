# Patterns & Techniques — Vibe Coding Architecture at Scale

## Write-Once Guardrail (the master pattern)
**When to use**: any boundary an AI could erode. **How**: a human encodes intent once (test, annotation, spec); a machine enforces it in the AI's own feedback loop; the failure is pasted back and the AI fixes it. **Trade-offs**: upfront investment; must enforce at a low-friction moment or humans rip it out (the JPMS lesson). (Ch 1)

## Box-and-Invariant Prompt
**When to use**: any feature/concurrency request. **How**: name target package, forbidden imports, allowed inputs/return types, and the invariant; leave the implementation to the AI. The third time you type the same guidance, move it into source as an annotation. **Trade-offs**: more upfront thought. (Ch 2)

## Cache-Ordered Prompt Assembly
**When to use**: automated agent loops. **How**: static instructions + Tier 1 + signatures first; task, diff and test output as a short suffix; never prepend timestamps. **Trade-offs**: one changed character invalidates everything below it. (Ch 3, 3c)

## Three Depths for One Intent
**When to use**: rules that truly matter. **How**: instruction line (advises) + hook with exit 2 and stderr explanation (blocks locally) + architectural test in CI (blocks merge). **Trade-offs**: three artifacts to maintain. (Ch 3d)

## Instruction Eval Harness
**When to use**: verifying CLAUDE.md rules change behavior. **How**: frozen task bank × 10 headless runs in disposable worktrees under FULL_FILE / RULE_ALONE / BASELINE; deterministic detector; assert coarse floors (0.8). Promote rules that stay under the floor to hooks/tests. **Trade-offs**: tokens and minutes per run; N=10 only separates coarse bands. (Ch 3f)

## Annotation → Generated Config + Check Mode
**When to use**: element-specific intent (lock, contract, thread-safety). **How**: `@AILocked`/`@AIContract` on the element; processor generates per-tool config into a managed block; check mode (regenerate + diff) as a required status check; processor and annotations pinned via one BOM. **Trade-offs**: Java-native; elsewhere hand-written rules. (Ch 4, 4b)

## Architectural Test Loop + Ratchet
**When to use**: module boundaries, legacy adoption. **How**: Define (ArchUnit/Modulith rule) → Violate → Trigger (`mvn test`) → Correct (paste failure back). On legacy, baseline existing violations, fail only on new ones, delete allowances as files are touched. **Trade-offs**: baseline must stay frozen, never regenerated. (Ch 5, 8c)

## Two-Speed Test Topology
**When to use**: agent iteration loops. **How**: `@Tag("fast")` inner loop < 30 s, full < 5 min, tag contract enforced by ArchUnit; isolate before parallelizing (rollback, namespacing, schema-per-test); TestContainers reuse; quarantine flakes immediately. **Trade-offs**: setup effort per suite. (Ch 5b)

## Self-Documenting Exception
**When to use**: self-correcting agent loops. **How**: exception messages carry a resolvable link to a recovery spec (`[[lat.md/troubleshooting.md#…]]`); `lat check` fails on stale links. (Ch 5c)

## Diagram-First Design Prompt
**When to use**: structural features. **How**: ask for a Mermaid design, fix the arrows, "build that", confirm against the build-generated diagram. (Ch 6)

## Log-Assertion Test
**When to use**: paths a green test can't see (retry fired, cache hit, tenant filter). **How**: emit a named contract event, capture output, assert the sequence; ship the missing DEBUG line with every fix. **Trade-offs**: couples tests to strings — only assert contract events. (Ch 6b)

## DocsAreTrueTest
**When to use**: any doc set an agent navigates. **How**: test every doc is indexed, links resolve, numbers in prose match live config; generated regions fenced with BEGIN/END GENERATED. (Ch 6c)

## Plan-Then-Stop
**When to use**: every spec'd feature. **How**: "Read .specs/… Produce plan.md and stop. Do not write code yet." Review, then execute. requirements → design → tasks, each approved before the next. (Ch 7, 8, 9)

## Brownfield Procedure
**When to use**: legacy modernization. **How**: characterize → ratify recovered spec (human) → freeze wire contract → ratchet → annotate landmines → refactor under the net → strangle. Never big-bang. (Ch 8c)

## Supervised Zone
**When to use**: regulated/high-risk code. **How**: Tier 2 context naming the risk + `@AIRegulation` + CI-forced specialist review; crypto via audited libraries only. (Ch 11b)

## Forced-Collision Concurrency Test
**When to use**: any AI code touching shared mutable state. **How**: demand an `@AsyncTest` (≥ 20 threads, ≥ 100 invocations) with detectors; expect red; paste the diagnosis back; run on ARM too. (Ch 17)

## Query Budget (@ExpectSelect)
**When to use**: ORM access in loops. **How**: assert SELECT count; "fix the query, not the test"; time budgets (k6 p95) only nightly on pinned hardware. (Ch 17b)

## Frozen Contract + Expand/Migrate/Contract
**When to use**: any change touching schema or serialized payloads. **How**: openapi.yaml outside agent write scope + contract test; migrations additive only; destructive steps separate and justified; consumer contracts gate removal; Sunset header for v1. (Ch 18)

## Deny-by-Default Dependency Gate
**When to use**: agents that edit build files. **How**: Enforcer allowlist, curated proxy, frozen lockfile installs, cooldown (`minimumReleaseAge`), lockfile sentinel CI; Tier 1 rule "never add a dependency; propose and stop." (Ch 18b)

## Assume-Hijacked Agent Design
**When to use**: agents reading external content. **How**: fence untrusted data; task-scoped read-only tools; microVM sandbox with no secrets inside; human gate on irreversible acts; authorization sidecar (OpenLeash) with signed audit. (Ch 19, 19b)

## Attack → Red Test → Fix → Keep
**When to use**: services with an OpenAPI/Pact contract. **How**: attacker in a disposable sandbox against an ephemeral instance; freeze each break as a failing test before fixing. (Ch 20)

## Break-the-Mechanism Audit
**When to use**: before promoting a test to a merge gate. **How**: break only what the test name promises, confirm that exact test goes red, revert; automate with PIT. (Ch 20b)

## Agent-Authored @AILocked CI Gate
**When to use**: agents commit to a repo with locked code. **How**: files with `@AILocked` ∩ changed files ∩ agent provenance → fail + named human approver; unknown provenance = agent. Enforcer set under CODEOWNERS. (Ch 21)

## Worktree per Writer
**When to use**: parallel agents. **How**: `git worktree add` per writing agent; verification windows own their tree; `set -o pipefail`; audit ports before runs. (Ch 21b, 24)

## Gripe Paste-Back Loop
**When to use**: Inquisitor blocks a PR. **How**: paste the gripe verbatim: "Fix your own layout; do not weaken the rule or the test"; re-run to ALL CLEAR. (Ch 22)

## Model Upgrade Gate / Two-Tier Routing
**When to use**: model bumps; mixed judgment+mechanical work. **How**: pin exact IDs; replay golden `prompts/` set through all gates before re-pinning; strong model writes the work order, cheap model executes, gates verify, escalate on failure. (Ch 23, 23b)

## Save-State Reload
**When to use**: every AI iteration. **How**: commit each verified sub-task; on red, `git reset --hard` and re-prompt from a clean base; squash at PR boundary; risky ideas in a worktree. (Ch 24)
