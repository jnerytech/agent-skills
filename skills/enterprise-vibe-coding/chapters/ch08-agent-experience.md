# Chapter 8: From Steered Delivery to Agent Experience

## Core Idea
HVE is more than a way to ship faster. It is the base layer that makes good **human-agent experience (AX)** possible: once agents keep working for hours or days, the design problem moves from interface design to *relationship design*. Every handoff back to a human must make the goal, the changes, the reasons, the evidence and the next decision clear without anyone rereading a transcript. (Short closing chapter: mostly a recap of ch01–ch07; the genuinely new material is AX and the Five Return Questions.)

## Frameworks Introduced
- **The HVE Journey (Figure 8.1)**: the book's arc read as a single operating model. It runs **challenge → steered operating model → primitives → cadence (RPI + Agentic DevOps) → governance → industry blueprints → delivery loops**.
  - When to use: when explaining HVE as a whole, or when checking that no pillar is missing from a team's adoption.
  - How: (1) *Challenge*: the first draft is now cheap, so the cost and the bottleneck move downstream to review, integration and accountability. Vibe coding fails on production code because the conventions and boundaries nobody wrote down stay unstated. (2) *Paradigm*: "agents execute work inside a steered system", not "AI writes code". There are three phases of human-agent collaboration, the single-UI thesis, the delivery pipeline produces artifacts, and the developer moves from typist to director. (3) *Primitives*: instructions, prompts, agents, skills, hooks and MCP move knowledge out of people's heads and into the repo. (4) *Cadence*: RPI plus Agentic DevOps, where the pipeline acts as a safety system and done is machine-checkable. (5) *Governance*: decision boundaries (alone / sign-off / off-limits), bounded autonomy, policy-as-code, auditability by default. (6) *Blueprints*: three end-to-end proofs. (7) *Loops*: engineering the delivery system itself.
- **Converging principles of the emerging Agentic SDLC discipline**: four principles that independent practitioners keep arriving at: **constrain before you automate; make intent explicit; encode expertise into reusable assets; design systems where autonomy increases without sacrificing accountability.**
  - When to use: when comparing HVE with another framework, such as Meppiel's *Agentic SDLC Handbook*, or when designing your own operating model.
  - How: you don't have to adopt one framework or its vocabulary. Shape the model to your culture, regulatory environment, technology and appetite for autonomy, and then check that it meets all four principles.
- **AX (human-agent experience, this book's sense)**: the experience of working with autonomous agents across time, tools and artifacts. It is judged by whether work done with the agent stays **understandable, steerable, auditable and accountable**.
  - When to use: when agents act asynchronously, keep state between sessions, or run for hours or days while the human is elsewhere.
  - How: answer the four relationship-design questions. (1) Can the human understand what happened while they were away? (2) Are the agent's decisions visible and auditable? (3) Does context persist across sessions? (4) Is responsibility clear?
  - Why it works: you can't trust an agent whose decisions you can't see. Observability, audit and checkpoints are what keep a human accountable for work that continues while they look away, and HVE already produces those artifacts.
- **The Five Return Questions (AX starter rule)**: when a person comes back to a long-running task, the system must answer five questions without making them reread the conversation: **What was the goal? What changed? Why did it change? What evidence supports the result? What decision is required from me now?**
  - When to use: as the first AX improvement, before any larger interface redesign.
  - How: don't redesign the whole agent interface. Pick **one long-running workflow** and make the handoff back to the human explicit. If HVE already produces plans, diffs, tests, logs and approvals, the first step is usually just to gather those artifacts into **one coherent view the person can resume from**.
  - Failure mode: a long transcript as the only record. The human has to rebuild context from scratch, which breaks both trust and accountability.
- **UX → Agent UX → Human-agent collaboration progression (Figure 8.2)**: UX is a person using software. Agent UX is interacting effectively with an intelligent agent. Human-agent collaboration is coordinating work with agents that keep state, act asynchronously and take part in workflows over time.

## Key Concepts
- **Steered development**: humans own the decisions, constraints and risk tolerance, and agents execute quickly inside those boundaries.
- **Developer as director**: the developer's most valuable work becomes setting intent, defining constraints and accepting risk, not typing code.
- **Single-UI thesis**: one surface from which a human delegates to, and oversees, many specialized agents.
- **AX (Biilmann/Netlify sense)**: introduced by Mathias Biilmann in 2025. It is the experience *an AI agent has* when using a product or platform: can it discover capabilities, reach suitable APIs and docs, act reliably and recover from failure?
- **AX (this book's sense)**: the *human's* experience of working with persistent agents. Is the work understandable, steerable, auditable and accountable? Both meanings matter as agents become persistent participants in delivery.
- **Relationship design**: the design focus once agents persist. It covers continuity, visibility, context persistence and clear ownership, instead of friction on a single screen.
- **Resumable view**: one place that brings together goal, diff, assumptions, evidence and the pending decision, so the human picks up without reconstructing anything.
- **Agent-native tool**: a tool where work starts from a real artifact such as an issue or PR, not from a blank prompt. The agent proposes a plan before acting and runs in an isolated workspace and branch. Parallel sessions sit under one surface (e.g., the GitHub Copilot app's "My Work") with a history you can query.
- **Implementation-independent operating model**: HVE's requirements outlast any one tool, much as REST outlasts its implementations. They are standards an agent can interpret, a cadence that puts human judgment in the right places, and guardrails that make autonomy safe.

## Mental Models
- **Think of HVE as the substrate for AX.** Each pillar already answers part of the AX problem. Primitives write down the standards an agent would otherwise guess at. RPI makes intent legible by requiring a plan before action. Agentic DevOps leaves evidence in every PR. Governance supplies the audit trail, bounded autonomy and checkpoints.
- **Use the "return after an hour" test** to judge any agentic workflow. Assign a feature, leave, and come back. If the intent, evidence, state and next decision are clear right away, the AX is good. If you have to read the transcript, it is not.
- **Think of the industry trends as confirmation, not a new method.** Anthropic's eight 2026 trends each map to an HVE pillar, so treat them as a coverage check.
- **Use vendor-neutrality as a design test.** If a practice only works inside one product's UI, it is a feature, not part of the operating model.

## Anti-patterns
- **Vibe coding a production codebase**: it works on a blank prototype, but in a real repo the hidden conventions and boundaries go unstated, and the quick results turn into rework.
- **The transcript as the handoff**: making the human rebuild context from a long conversation breaks resumability and accountability.
- **Redesigning the entire agent interface first**: it is too big to land. Start with one workflow's handoff.
- **Adopting one framework's vocabulary wholesale**: the four shared principles matter, not the names. Fit the model to your own regulatory environment and appetite for autonomy.
- **Treating powerful models as sufficient**: reliable delivery needs explicit structures, reusable patterns, governance mechanisms, and human knowledge turned into repeatable systems.
- **Opaque autonomy**: an agent whose decisions are invisible can't be trusted, however capable it is.

## Reference Tables

**Table 8.1: Human-agent experience in practice and the HVE mechanisms that support it**

| What the person needs to know | What the system should expose | HVE mechanism |
|---|---|---|
| What was the agent trying to achieve? | Goal, issue, acceptance criteria, current stage | Instructions + RPI |
| What changed while I was away? | Diff, artifacts, commits, activity history | Persisted state + Agentic DevOps |
| Why did the agent make that decision? | Plan, assumptions, decision record | RPI + observable reasoning artifacts |
| Did the work pass validation? | Tests, scans, policy checks, CI evidence | Hooks + verification pipeline |
| What failed or was retried? | Tool failures, retries, recovery actions | Observability + loop state |
| What needs my attention now? | Explicit approval, escalation, or unresolved choice | Governance boundary |
| Who owns the outcome? | Named approver and audit trail | Accountability + governance |

**Anthropic 2026 Agentic Coding Trends mapped to HVE**

| # | Trend | Where HVE covers it |
|---|---|---|
| 1 | SDLC changes dramatically: agents take over implementation, engineers move to architecture, direction and evaluation | Ch 1–4 |
| 2 | Single agents evolve into coordinated teams: orchestration becomes an engineering problem | Ch 2 |
| 3 | Long-running agents build complete systems: work persists beyond one synchronous interaction | Ch 7 + AX |
| 4 | Human oversight scales through intelligent collaboration | Ch 5 |
| 5 | Agentic coding expands to new surfaces and users | Ch 2, 6 |
| 6 | Productivity gains reshape development economics | Ch 1, 2 |
| 7 | Non-technical use cases expand across organizations | Ch 6 |
| 8 | Dual-use risk requires security-first architecture | Ch 5 |

## Worked Example
**Feature assigned before a meeting.** An engineer gives an agent a feature in an agent-native tool. The session starts from the issue, the agent proposes a plan, and it runs in its own isolated branch. The engineer then goes to a meeting. An hour later they come back to the shared surface. They don't scroll the transcript. The resumable view answers the Five Return Questions:
1. *Goal*: the issue, its acceptance criteria and the current RPI stage (from instructions + RPI).
2. *What changed*: the diff, commits and new artifacts (from persisted state + Agentic DevOps).
3. *Why*: the plan, the assumptions the agent made and its decision record.
4. *Evidence*: test, scan, policy-check and CI results (from hooks + the verification pipeline), plus any tool failures, retries and recovery steps (from observability + loop state).
5. *Decision now*: an explicit approval or escalation where the agent hit a governance boundary or an unresolved choice, with a named approver.

The engineer checks the evidence, then approves or redirects the next step, and work continues without rebuilding context. The author's closing exercise follows the same path. Take one Chapter 6 blueprint, encode its primitives, run a real RPI cycle, put its decision boundaries into hooks and approvals, and then see what it is like to return after the agent has been working without you.

## Key Takeaways
1. Pick one long-running workflow, make its handoff explicit, and make it answer the Five Return Questions before you redesign anything bigger.
2. Usually the first AX improvement is just gathering artifacts HVE already produces (plans, diffs, tests, logs, approvals) into one resumable view.
3. Use Table 8.1 as a checklist: every "need to know" row needs a matching exposed artifact and an HVE mechanism behind it.
4. Keep the term AX clear. Biilmann/Netlify AX means the agent's experience of using your platform, while this book's AX means the human's experience of working with persistent agents. Both apply.
5. Build your operating model on the four converging principles, not on any one framework's vocabulary or vendor's UI.
6. The book's goal is higher-confidence delivery at higher speed, not more AI output.

## Connects To
- **ch01**: the challenge statement (cheap first draft, downstream bottleneck), steered development and the maturity self-assessment.
- **ch02**: the three collaboration phases, the single-UI thesis, the agent pipeline and developer-as-director. Agent-native tools put these into practice.
- **ch03**: primitives write down the standards behind "what was the agent trying to achieve".
- **ch04**: RPI makes intent legible, and Agentic DevOps puts evidence in every PR.
- **ch05**: governance supplies the decision boundaries, audit trail and named approver in Table 8.1.
- **ch06**: the blueprints are the starting point for the closing exercise.
- **ch07**: long-running delivery loops create the persistent-agent AX problem, and loop state shows up as retry/recovery visibility.
- **Agentic SDLC Handbook (Daniel Meppiel)**: a parallel framework built with its own methodology, which shows the discipline converging.
- **Anthropic 2026 Agentic Coding Trends Report**: eight trends, each mapped to an HVE pillar.
- **AX (Mathias Biilmann, 2025; Netlify)**: the original agent-centric meaning of Agent Experience.
- **REST**: the analogy for implementation-independent architectural principles that outlast tools.
