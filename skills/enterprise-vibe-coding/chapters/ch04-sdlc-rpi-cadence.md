# Chapter 4: Reshaping the SDLC: Agentic DevOps and the RPI Cadence in Practice

## Core Idea
The six SDLC phases (Plan, Design, Develop, Test, Release, Maintain) do not change; what changes is who works inside each phase and how artifacts carry meaning across handoffs. Composing the Chapter 3 primitives per phase, under a Research–Plan–Implement cadence with human gates and independent validation, turns the pipeline into a governed "active safety system" — Agentic DevOps.

## Frameworks Introduced
- **RPI cadence (Research, Plan, Implement) applied per SDLC phase**: inside every phase, the agent first researches context, then proposes a reviewable plan, and implements only after a human approves the plan.
  - When to use: any agent-executed task in any phase: spec writing, design, coding, test authoring, release.
  - How: (1) **Research**: the agent reads the governed artifacts already in the repo (spec, architecture record/ADR, related code) and emits a short "assumptions and inputs" note for human review. (2) **Plan**: it writes a change plan that defines diff scope, tests, and rollback approach (in testing, the test plan is the Plan gate). (3) Human approves the plan. (4) **Implement**: small, reviewable PRs carrying evidence (test, lint, scan results). (5) Post-approval validation layers still run: independent tests, policy checks, security scans, staged deployment, runtime monitoring, rollback criteria.
  - Why it works / failure mode: it stops agents drifting beyond approved scope, and hooks, automated checks and policy-as-code make it enforceable rather than aspirational. Failure mode: treating approval as proof of correctness. A human-approved plan can still be wrong and the approver can miss issues. For higher-risk changes, neither the reviewer nor the producing system should be the only source of assurance, so add independent checks or a second reviewer.
- **Agentic DevOps**: traditional DevOps (shared ownership, automation, CI/CD, continuous feedback across build/test/deploy/monitor) extended with bounded reasoning systems in the loop. Pipelines inspect PRs, generate tests, analyze risk, summarize releases, validate architecture constraints, evaluate agent behavior, and escalate uncertainty to humans.
  - When to use: as the through-line connecting all six phases. It augments mature DevOps, and works best where automation, governance and operational discipline are already strong.
  - How: prompts generate structured artifacts → agents execute bounded tasks → hooks enforce local guardrails → MCP servers expose controlled access to enterprise systems → workflows orchestrate CI/CD, approvals, testing, deployment and monitoring.
  - Why it works / failure mode: it stays governed (scoped permissions, approval gates, hooks, workflows, observable audit trails). Without that governance it is just ungoverned autonomy.
- **Five core patterns of Agentic DevOps** (Fig. 4.9):
  1. *Outcome- and intent-driven execution*: define goals and constraints, not every step; agents work out the how from available context.
  2. *Autonomous decision-making within guardrails*: agents plan/execute/optimize independently but inside policies, approvals, audit requirements.
  3. *Context-aware reasoning, not just automation*: agents interpret system state, dependencies, history, and adapt within defined limits (unlike static CI/CD scripts).
  4. *Closed-loop learning and adaptation*: observe → plan → act → incorporate feedback, but improvement happens **only** if the workflow is designed to capture, review, and apply feedback.
  5. *Collaborative systems*: multiple specialized agents (testing, deployment, monitoring…) coordinate across the SDLC alongside humans, not replacing them.
- **Release pipeline as an active safety system**: the pipeline reasons about the change, gathers evidence, and either ships or hands back to a human with a one-paragraph explanation.
  - How: build → full test pyramid + agent evaluation harness → deploy to staging → smoke-test agent → **human approval** → production canary → watch SLOs → promote or roll back. Runs on every merge to `main`.
  - Rule: agents accelerate every step but **never decide to release**. Promotion requires explicit human approval recorded by name in the workflow run.
- **Three-layer agentic test strategy**: unit tests (application code), scenario tests (agent flows, replayable traces against the live agent graph), and end-to-end tests (against a sandboxed backend through MCP). All three run on every PR.
- **Spec-to-test-plan shape**: per user story, the test plan contains the happy path + **3 edge cases + 2 failure modes + 1 security-relevant case**, reviewed by the tech lead before any test code is generated.

## Key Concepts
- **Handoff loss**: the meaning that is lost when one phase's artifact (ticket, document, PR) is passed to the next and people must reconstruct the intent. Composed primitives reduce it.
- **Governed artifacts as context**: specs, ADRs, diagrams and NFRs committed to the repo, which downstream agents read directly, so context need not be restated in every prompt. This is where primitives "compound".
- **Architecture Decision Record (ADR)**: a record of a significant architectural decision with its context and consequences, which the architecture-reviewer agent checks proposals against.
- **Mermaid / Mermaid MCP**: text-based diagramming (flowcharts, sequence, C4, dependency maps) that is versionable and PR-reviewable. The MCP server lets an agent generate, validate, render and save diagrams.
- **Bill of quantities (BoQ)**: the inferred list of cloud services and sizing assumptions derived from an architecture, used for a back-of-the-envelope cost estimate.
- **Agentic testing**: deterministic tests plus evaluation datasets, replayable conversation traces, groundedness checks, tool-use assertions, and human review of ambiguous outcomes. It covers conversational quality, grounding accuracy, hallucination resistance, tool-calling, memory consistency, and multi-agent orchestration.
- **Workflow (agentic)**: an executable process, triggered by repo events or schedules, that orchestrates prompts, agents, hooks, MCP systems, approvals and deployment stages. In GitHub it is authored as `.github/workflows/release.md`, compiled to `release.lock.yml`, and run via GitHub Actions. It moves teams from "AI as an assistant" to **bounded autonomous execution**.
- **Escalation rule**: an explicit condition in an agent definition that forces it to stop and return control to a human (e.g., changes to authentication, MCP server permissions, or data export).
- **Work IQ**: exposes Microsoft 365 context (meetings, Teams messages, email, documents) via MCP to coding assistants. Agents can work from meeting context without copy-paste, constrained by the user's existing permissions.

## Mental Models
- **Think of the SDLC phases as fixed and the connective tissue as what gets automated.** Pre-agentic CI/CD already automated the mechanics. Agents take on the reasoning between phases: interpreting requirements, resolving ambiguity, judging evidence sufficiency, carrying context.
- **Think of approval as one validation layer, not the last.** Stack independent tests, policy checks, scans, staged rollout, monitoring and rollback criteria after the plan gate.
- **Use least-privilege personas split by environment boundary.** Backend-dev may build containers but not deploy; infra-dev may `az bicep build` but not `az deployment create`; production write access exists only inside the gated workflow.
- **Think of maintenance cost as a function of machine-readable memory.** Conventional codebases get costlier with size and age. In an HVE codebase, specs, designs, tests, runbooks and operational memory stay in the repo and are queryable by agents, so the team maintains the primitives as well as the code.

## Anti-patterns
- **Relying on human approval alone**: approvers miss issues and approved plans can be wrong. Without post-gate validation, errors ship.
- **Over-privileged agents**: giving an agent tools or environments beyond its role. Best practice is to scope tools per role and require human review for authentication, permissions, data export, and production changes.
- **Agents deciding to release**: the speed/trust trade-off is resolved only by keeping the final "go" human and named.
- **Agent applying its own bug fix**: bug-triage proposes a diff but cannot apply it, and the fix goes through a PR with human review.
- **Restating context in every prompt**: put decisions in governed repo artifacts instead, so agents read them.
- **Starting agents from a blank screen**: skipping Research/Plan lets the agent drift beyond approved scope.
- **Unopinionated scaffolding**: leaving choices that add no value. The scaffold prompt is deliberately opinionated.
- **Assuming closed-loop learning happens automatically**: feedback improves the system only if the workflow captures, reviews and applies it (e.g., a *reviewed* learning loop that updates the knowledge base).
- **Linear test-after-development**: in HVE, testing runs alongside and sometimes ahead of development, from the same spec.

## Reference Tables

**Primitives per SDLC phase (FlowDesk)**

| Phase | Goal | Prompts | Agents | Skills / Instructions | Hooks | MCP | Human gate |
|---|---|---|---|---|---|---|---|
| 1 Plan | Vague intent → reviewable specs | `meeting-notes-to-spec`, `spec-to-user-stories` (acceptance criteria + Gherkin) | spec-writer | — | — | Azure DevOps MCP (Boards), Work IQ | PM + tech lead approve scope, success metrics, top risks (recorded in file/Git) |
| 2 Design | Spec → design artifacts ("what and why") | `spec-to-architecture-diagram` (C4 Mermaid, palette, naming), `architecture-to-boq-estimate` | architect, architecture-reviewer (vs ADRs) | — | — | Mermaid MCP | Tech lead PR review; comments → targeted agent revisions |
| 3 Develop | Design → infra, data, app code | `scaffold-microservice` (entry point, health check, settings, telemetry, Dockerfile) | backend-dev, infra-dev | `copilot-instructions.md` / `CLAUDE.md`; `agent-framework-scaffold` (or `langgraph-agent-scaffold`); `deploy-to-aca` | — | GitHub MCP (this repo only, RW) | Plan approval before Implement; PR review with evidence |
| 4 Test | Prove system does what spec said | `spec-to-test-plan` | test-dev, scenario-test-author | Agent Framework testing harness | — | Azure DevOps MCP, GitHub MCP | Tech lead reviews test plan before test code |
| 5 Release | Safe, fast path to production | — | release-captain, smoke-test agent | `deploy-to-aca` | production-readiness hook | GitHub MCP; Azure MCP (prod write only in gated workflow) | Named human approval before canary/promotion |
| 6 Maintain | Keep system healthy/understandable | — | codebase-explorer (read-only), bug-triage, pr-reviewer | — | `pr-review-bot` (runs pr-reviewer on PRs to main) | — | Human PR review of all fixes |

**Agent scoping (permissions vs. prohibitions)**

| Agent | Can | Cannot / must escalate |
|---|---|---|
| backend-dev | Read/edit app files, run tests, local container build | Deploy, access production; stop on auth, MCP permission, or data-export changes |
| infra-dev | Work in `infra/`, read `deploy-to-aca`, write Bicep, `az bicep build` | `az deployment create` (reserved for release workflow) |
| test-dev | Read code, edit tests, run unit/integration tests, local containers, logs, reports | Modify prod infra or business logic outside the scoped PR |
| release-captain | Compose release note (PR titles, spec changes, risk flags), post to Teams, tag on-call | Continue on anomaly (coverage drop, unusual file change, new MCP server): stops pipeline, requests human confirmation |
| bug-triage | Locate code, reproduce, one-paragraph hypothesis + proposed diff | Apply the fix |
| codebase-explorer | Read spec/ADR/code; one-page answer with file paths + line numbers | Any write |

**Production-readiness hook checks (pre-deploy)**: no exposed secrets or confidential data · runbooks are current · on-call contact is reachable.

## Worked Example
**FlowDesk at Northwind Logistics.** Northwind is a midsize European supply-chain company with about 4,000 employees. Its IT desk is swamped by password resets, VPN issues, SAP authorization questions, laptop provisioning, and mailbox quotas. The goal is a six-month build of an agentic copilot in Teams that triages tickets, drafts resolutions, escalates with full context, and writes reviewed summaries to the knowledge base. It integrates with the custom Northwind Service Backend via a dedicated MCP server. Routine cases are resolved end to end with human confirmation, every action is logged, and every escalation carries a rationale. Team: tech lead, 2 engineers, PM, security partner, SRE on-call rotation. HVE from day one.

1. **Plan**: a 40-minute recorded kickoff → `meeting-notes-to-spec` produces a fixed outline (problem, in/out of scope, success metrics, personas, top 5 risks, open questions). The PM edits it instead of writing from scratch. `spec-to-user-stories` adds acceptance criteria and Gherkin. PM + tech lead approve scope/metrics/risks in the file, so the spec-writer regenerates against the Git diff. Azure DevOps MCP creates the stories in Boards. Elapsed: one afternoon instead of weeks of drift.
2. **Design**: the architect agent produces a one-page ADR, a Mermaid C4 context+container diagram, and a BoQ cost estimate. These go through a normal PR, and the approved design lands in the repo as input for development.
3. **Develop**: backend-dev runs RPI. It writes an assumptions note, then a change plan (diff scope, tests, rollback), gets approval, and only then opens small PRs with test/lint/scan evidence.
4. **Test**: each story gets a plan of happy path + 3 edge + 2 failure + 1 security case, which the tech lead reviews before code. By sprint 3, missing tests are the exception, and seniors review only the cases agents could not anticipate.
5. **Release**: a merge to `main` triggers build → tests + eval harness → staging → smoke-test agent → named human approval → canary → SLO watch → promote/rollback. release-captain halts on anomalies.
6. **Maintain**: six months later there are 500,000 tickets and a rotated team. New engineers onboard via codebase-explorer, bug-triage proposes fixes as PRs, and pr-reviewer comments before humans review.

## Key Takeaways
1. Keep the six SDLC phases and automate the reasoning between them by composing prompts, agents, skills, hooks, MCP and workflows per phase.
2. Run every agent task through RPI (assumptions note → change plan with scope/tests/rollback → approval → small evidenced PRs), and enforce it with hooks and policy-as-code.
3. Never treat plan approval as sufficient. Layer independent tests, scans, staged rollout, monitoring and rollback, and use a second reviewer for high-risk changes.
4. Scope each agent persona to least privilege, split by environment, with explicit escalation rules for auth, permissions, data export and production.
5. Keep the final release decision human and named in the workflow run; agents speed every step up to it.
6. Commit specs, ADRs, diagrams, tests and runbooks to the repo so later agents and new engineers can query them, which is what bends the maintenance cost curve.
7. Design closed-loop learning explicitly (capture → review → apply); it does not happen by itself.

## Connects To
- **ch03**: this chapter puts the six primitives (instructions, prompts, agents, skills, hooks, MCP) to work phase by phase.
- **ch05**: it picks up the open question of accountability: decision boundaries, policy-as-code, and the audit trail that make RPI gates defensible.
- **ch06**: further use cases built from the same HVE primitives.
- **ch07**: the closed-loop learning and overnight bounded-workflow patterns lead into loop engineering.
- **ch01**: steered (not vibe) development is what RPI operationalizes.
- **DevOps / CI/CD**: Agentic DevOps augments existing DevOps practice rather than replacing it.
- **C4 model, ADRs, Gherkin/BDD**: standard artifact formats produced by the Plan/Design/Test prompts.
- **GitHub Agentic Workflows (gh-aw), Azure DevOps MCP Server, GitHub MCP Server, Microsoft Agent Framework, Work IQ, Claude Code slash commands/subagents/hooks**: concrete tooling used to implement the cadence. In Claude Code, an `/overnight-prototype-exploration` command can orchestrate a bounded overnight run that ends in a ranked summary.
