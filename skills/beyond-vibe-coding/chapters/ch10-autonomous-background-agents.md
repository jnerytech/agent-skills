# Chapter 10: Autonomous Background Coding Agents

## Core Idea
Background coding agents shift AI use from assisting to *delegating*: you hand off a whole task, the agent plans, edits, tests and reports in an isolated sandbox, and returns a PR. Your job moves from writing code to writing good task descriptions and reviewing the result rigorously. This means new failure modes (compounding errors, environmental drift, coordination, review overload) that need new practices.

## Frameworks Introduced
- **Plan → Execute → Verify → Report**: the shared operating loop of background agents (expanded: understand → plan → code → test → deliver).
  - When to use: as the mental model for what an agent does and where you can step in.
  - How:
    1. **Plan**: the agent parses the task, splits it into substeps (search codebase → change files A, B, C → run tests → commit), and spins up a cloud sandbox (repo clone + dependencies, internet usually cut off after setup). *You review the plan here.*
    2. **Execute**: it locates code (often with plain full-text/grep search), edits and creates files, and streams logs you can watch or step into.
    3. **Verify**: it compiles and runs tests/linters, then loops fix → rerun until they pass. This only works if the sandbox matches the real dev environment.
    4. **Report**: it delivers a PR, diff or chat summary. You "trust but verify", then merge, discard, or send it back with feedback.
  - Why it works: closing the verify/fix loop by actually running the code makes it much more likely the output works. Plausible-looking code becomes tested code.
  - Failure mode: an environment mismatch breaks Verify. In one Codex run, missing tools meant the full suite could not run, and the PR shipped with two failing tests the agent could have fixed.

- **Copilot vs. Autopilot (pair programmer vs. assistant developer)**: in-IDE assistants are synchronous, reactive and micro-scoped, with the human approving each step. Background agents are asynchronous, proactive and project-scoped, and they execute code.
  - When to use: picking the tool for a task.
  - How: keep tight control (inline copilot) for complex core logic. Delegate peripheral, time-consuming, multi-file work (for example, updating every API client for new endpoints) to an agent running in parallel. Use both, chosen by scope.

- **Generator vs. Reviewer Asymmetry**: generating a solution from scratch is hard, but reviewing and refining one is easier. Agents do the bulk generation and you do the faster vetting.
  - When to use: deciding to delegate, and planning your own time.
  - How: put your effort into (a) a precise task description and (b) sharp review. Build up your review and verification skills, because AI code makes different kinds of mistakes than human code.
  - Failure mode: once volume grows, review turns into the bottleneck (see "review bottleneck, amplified").

- **"Overeager Junior Developer" stance**: treat agent-produced code as written by a slightly overeager junior. Assume good intentions and decent competence, verify everything, and request changes or reject without hesitation.

- **Multi-model orchestration ("AI conductor, not just AI prompter")**: route each subtask to the model or tool best at it and chain the outputs.
  - When to use: when you can reach several models or tools, or a subtask has a known specialist (regex, tests, docs, security scan).
  - How:
    1. Split by role: CodeGen, TestGen, Doc, Design and Optimization AIs, plus deterministic tools for arithmetic or algorithms.
    2. Pipe outputs: design → code → tests (or critique) → docs.
    3. For redundancy, have two different models solve the same task, run the tests on both, keep the passing one (or the more readable if both pass), and show the failing model the passing code as a hint.
    4. Wrap specialists in scripts that pre- and post-process (an `ai_regex_generator` that checks the output is a valid regex and tests it on examples).
    5. Automate routing with a classifier front end (`ai_dev_assist`).
    6. Include humans as "highly advanced models": a UX designer judges the AI prototypes, and a colleague reviews AI-written complex code.

- **Agent landscape differentiators**: compare agents on four axes: execution environment (local vs. cloud), integration depth (IDE vs. workflow tools), autonomy level (supervised vs. independent), and target use cases (maintenance vs. feature development).

## Key Concepts
- **Background (autonomous) coding agent**: an AI coder that takes a high-level goal, works through the whole task in a sandbox (read, write, run, test), and delivers results for review.
- **Supervised coding agent**: an interactive in-IDE helper (Copilot, Cursor inline, Cline) where the human guides every step.
- **Ephemeral sandbox**: an isolated, short-lived cloud VM or container with the repo and dependencies, often with no internet after setup, to prevent data exfiltration.
- **Coherent incorrectness**: code that is internally consistent but fundamentally misaligned with the real needs, because one early misunderstanding was built on through sequential decisions.
- **Environmental drift**: small differences between agent sandboxes (Node version, missing system library, time zone) that show up as subtle bugs only at integration.
- **Async coordination paradox**: the more agents you run in parallel to raise productivity, the harder integrating their work becomes, because agents lack the informal awareness humans have of each other.
- **Review bottleneck, amplified**: agents deliver complete, simultaneous, large PRs whose "reasoning" you must reverse-engineer from the code. Review becomes "an archaeological expedition."
- **Sunk-cost dilemma (AI contributions)**: whether to invest in finishing the last 10–20% of a nearly-right agent PR for a task that was low-value to begin with.
- **Planning phase as quality gate**: proactive review of the agent's plan before it codes, a skill distinct from reactive code review.
- **Headless colleagues**: agents as quasi-team members, which raises ownership, resource-tracking and coordination questions.

## Mental Models
- Think of a **copilot vs. an autopilot**: the copilot sits beside you waiting for input, while the autopilot flies the plane alone for a while. Think of parallel agents as a *multithreaded* workflow that expands your cognitive bandwidth.
- Use agents when the task is **well-defined, encapsulated, measurable and parallelizable**. Keep humans in the lead when it needs architectural decisions, interpretation of complex stakeholder requirements, or novel algorithms.
- Think of running several agents as **managing a distributed team**: scope boundaries, integration order and conflict avoidance matter more than in solo work.
- Think of combining models as **microservices for AI**: each one does one thing well, and redundancy removes single points of failure. Two different models rarely make the exact same mistake, so a second model works as a second opinion.

## Anti-patterns
- **Skipping plan review**: errors compound. A misread requirement becomes an entire wrong architecture across backend, frontend, schema and tests, which costs more to untangle than incremental fixes would have.
- **Under-provisioned agent environment**: without tests, linters and builds the agent cannot self-correct, and you get PRs with failing tests.
- **Overlapping agent scopes**: Agent A refactors a utility while Agent B adds calls to the old version, so conflicts appear at merge.
- **Batch-dumping huge agent PRs**: five 500+ line PRs on Monday morning overload review. Agent PRs carry no real thought process in their messages.
- **Delegating judgment-heavy work**: architecture, ambiguous requirements and novel algorithms do not fit an autonomous run.
- **Granting write and execution access with suggestion-grade controls**: a compromised or misdirected agent commits, and may deploy, bad code. Sandboxing and access control must be stricter than for suggestion tools.
- **Polishing every almost-good PR by reflex**: weigh the value of the task against the cost of finishing the last 20%. Discarding is a valid outcome.
- **Relying on a single model for everything**: you miss specialist strengths and keep a single point of failure.

## Code Examples
```text
# Agent execution plan (the shape to review at the Plan gate)
Step 1: search the codebase for relevant sections
Step 2: make changes in files A, B, C
Step 3: run tests
Step 4: commit changes

# Orchestration flow (multi-model routing)
Step 1: Model A interprets the user request
Step 2: if data analysis -> Model B generates SQL; if text -> Model C ...
Step 3: feed the result to Model D to explain it
```
- **What it demonstrates**: the two delegation structures you oversee. An agent's own substep plan (check it for completeness against your conventions) and a routing pipeline that sends each subtask to a specialist.

## Reference Tables
| Dimension | In-IDE assistant (copilot) | Background agent (autopilot) |
|---|---|---|
| Timing | Synchronous, with you keystroke by keystroke | Asynchronous, hundreds of actions without confirmation |
| Scope | Microtasks: a line, function or snippet in open files | Project level: whole repo, coordinated multi-file changes, multistep plan |
| Initiative | Reactive, does only what you accept | Proactive ("I noticed X, so I fixed it too"), so it needs more oversight |
| Execution | Usually cannot run code | Runs tests, dev server, builds in a sandbox, so it closes the verify/fix loop |
| Integration | Lives in the editor | Issue trackers, GitHub PRs, Slack, CI (e.g. auto-fixing lint) |
| Human role | Programming, faster | Delegation followed by review |
| Best for | Tight control over complex logic | Cross-cutting refactors, upgrades, full-stack features, maintenance backlog |

| Delegate to an agent | Keep human-led (AI-assisted) |
|---|---|
| Test-coverage targets (e.g. 80% for a module) | Significant architectural decisions |
| Systematic dependency updates | Interpreting complex stakeholder requirements |
| Bulk refactoring (logging, error handling) | Designing novel algorithms |
| Standardized features across many components; bugfixes, test additions, linter cleanups | |

## Worked Example
**Delegating "reach 80% test coverage in module X" end to end** (reconstructed from the chapter's examples)
1. **Select**: the task is measurable, encapsulated and repetitive, which is the sweet spot. An assistant would help write *one* test, while the agent works through every untested function.
2. **Environment**: make sure the sandbox config installs the exact runtimes and tools the test suite needs. Otherwise Verify fails, as in the Codex PR that arrived with two trivially fixable failing tests.
3. **Plan gate**: read the proposed plan for correctness, efficiency and fit with conventions. (Same idea as catching a Jules plan to upgrade Next.js that left out the webpack config changes, before any code exists.)
4. **Scope boundaries**: if another agent is updating dependencies at the same time, give each a separate module, and decide the integration order (infrastructure before features).
5. **Monitor occasionally**: check the logs and step in (e.g. enter the Cursor machine) only if the agent is chasing an inefficient route or widening the change unnecessarily.
6. **Review as an overeager junior's PR**: run the agent-specific checklist (correctness, team conventions, architectural patterns, known quirks of this agent).
7. **Decide**: merge; send it back with specific guidance (cheap, with no social cost); or, if it is ~80% right and the task is low-value, explicitly weigh the sunk-cost question before investing in the last 20%.
8. **Capture**: save the prompt that worked as a template for future coverage tasks.

## Key Takeaways
1. Delegate well-defined, measurable, parallelizable tasks to agents. Keep architecture, ambiguous requirements and novel algorithms human-led.
2. Treat the agent's plan as your main quality gate. Fixing a misread plan is far cheaper than untangling coherent incorrectness in a finished PR.
3. Invest in the agent's environment until it can run everything a developer would (tests, linters, builds). Self-correction depends on it.
4. Give concurrent agents non-overlapping scopes (modules or layers) and an integration order. Manage them like a distributed team.
5. Review agent code as an overeager junior's: verify everything, keep agent-specific checklists and a log of quirks, and reject freely.
6. Build agent prompt templates and feedback loops. Sending work back to an agent is cheap.
7. Orchestrate several models, including deterministic tools and humans, by strength, and cross-check outputs with tests.

## Connects To
- **Ch 3**: agents inherit the 70% problem. The sunk-cost "last 20%" of agent PRs is its delegated form.
- **Ch 2**: writing task descriptions and reusable prompt templates for agents extends prompt craft.
- **Ch 5**: review skills for generated code become the main human job under the generator/reviewer asymmetry.
- **Ch 8**: environment configuration, sandboxing and access controls for agents with write and execution rights.
- **Ch 4**: "developers who use AI effectively will replace those who can't". Agents push this further.
- **Ch 11**: the future of agentic AI beyond code generation.
- **CI/CD and bot users**: agents triggered by issue-state changes or pipelines (auto-fixing builds and lint) join the toolchain as bot contributors.
- **LLM-as-judge / ensembles**: one model judging another's output, and N-version programming, as error-reduction strategies.
