# Chapter 7: Loop Engineering

## Core Idea
Stop prompting the agent and design the loop that prompts it. A delivery loop is a recurring, verifiable workflow that combines primitives (ch03), the RPI cadence (ch04) and governance boundaries (ch05). It carries context from a trigger to a governed outcome, pausing only at explicit human gates, and it ends only when a machine-checkable definition of done is met.

## Frameworks Introduced
- **Four complementary disciplines (Prompt → Context → Harness → Loop Engineering)**: each one optimizes a different layer, and reliable agentic systems need all four.
  - When to use: to work out which layer is failing (a bad answer, missing knowledge, an unreliable environment, or work that doesn't move forward without a human).
  - How: Prompt Engineering asks "What should I ask the model?" and optimizes *one instruction*. Context Engineering asks "What should the model know before reasoning?" and optimizes *the information for one execution* (retrieved docs, memory, standards, policies, examples). Harness Engineering asks "What environment does the agent need to operate reliably?" and optimizes *the execution environment* (tools, sandboxes, permissions, verification pipelines, observability, memory, guardrails, feedback). Loop Engineering asks "How should work progress autonomously?" and optimizes *the system that repeatedly orchestrates work*: what to prompt, when to act, how to verify, and when the job is truly complete.
  - Why it works: the slogan is "prompts teach models to answer better, context to think better, harness to operate reliably, loops to *work* better." A perfect prompt and perfect context still fail when nobody is driving the work from one step to the next.

- **The loop pattern (Discover → Delegate → Validate → Persist → Decide)**: the minimal autonomous system that every loop repeats.
  - How: (1) discover work (issues, emails, backlog items, events); (2) delegate it to the most appropriate agent; (3) validate through deterministic checks or human review; (4) persist state and learning *outside the current conversation*; (5) decide the next action, then either repeat or terminate.

- **Osmani's loop anatomy: five enabling pieces plus persistent state** (Addy Osmani, "Loop Engineering", 2026). This describes *what enables* a loop. It is not the lifecycle a feature follows.
  - **Automations**: the recurring trigger that discovers and triages work on a schedule.
  - **Worktrees**: isolate parallel streams so agents don't edit the same workspace.
  - **Skills**: reusable project knowledge and methods, so the agent doesn't rediscover them each run.
  - **Plugins/connectors**: links to external systems, including MCP services.
  - **Sub-agents**: split responsibilities, especially *one agent works and another verifies independently*.
  - **Persistent state/memory**: records what happened and what remains across otherwise independent runs.
  - When to use: as a checklist when building a loop on any stack. Every implementation needs some way to trigger, isolate, reuse knowledge, connect, separate execution from verification, and persist state.

- **Five-stage delivery lifecycle: Discover, Plan, Execute, Verify and Recover, Complete**: the book's model for *how work progresses* through a loop.
  - How:
    1. **Discover**: work is detected automatically (new issue, schedule, PR event, repo trigger). The agent turns the informal request into a structured objective with goals, assumptions, constraints and acceptance criteria, so it becomes an *executable contract*.
    2. **Plan**: the agent proposes the files to change, the approach, the validation strategy and any open uncertainties, then **pauses**. This is **GATE 1**, the first and usually most important human decision, because fixing a design is far cheaper than fixing code.
    3. **Execute**: after approval, the loop calls the agent repeatedly in **small iterations**. Each one updates the repo, records progress and sets up the next. The loop orchestrates the prompts; the engineer doesn't.
    4. **Verify and Recover**: every iteration runs the quality controls (tests, lint, security scans, accessibility, policy validation). If they pass, the loop advances. If they fail, *the failure becomes the next input* to the agent. Recovery is built into the loop.
    5. **Complete**: when all acceptance criteria are met and verification passes, the loop assembles evidence, updates the issue/PR and asks for the final human decision. This is **GATE 2**. It terminates only after approval. An existing PR does not mean it is done; meeting the agreed definition of done does.
  - Why it works / failure mode: humans stay where their judgment matters (direction, plan, merge), and everything else runs unattended. If the done-condition isn't machine-checkable, the loop either stops too early or never stops.

- **Autonomy modes (Autopilot vs permissions)**: these are two separate dials. Autopilot controls whether the agent *keeps going* between reasoning steps. Permissions control whether it must *ask before impactful actions* (file edits, shell commands, MCP tool calls).
  - **Interactive**: the loop orchestrates, and the agent asks approval for sensitive actions.
  - **Autopilot with limited permissions**: it runs autonomously but pauses on any action that isn't authorized.
  - **Autopilot with end-to-end permissions**: it runs fully unattended inside the repo's guardrails, policies and verification pipeline.
  - How: start interactive to build confidence, grant permissions for routine operations step by step, and enable full Autopilot only for well-defined delivery tasks. The loop itself stays the same; only the operational autonomy changes. Cap it with a maximum number of autonomous continuations.

- **Recovery boundaries (deliver-feature skill)**: halt and post a diagnostic summary to the thread after **3 failed attempts on the same criterion**, or when a failure pattern repeats despite valid patches. In **sensitive areas (auth, payments, PII, production)**, stop immediately on *any* failure and wait for a human. When retries run out, the engineer chooses one of three options: roll back to the last passing state, revise the plan, or escalate to unblock an external dependency.

- **Loop bounding controls (cost, safety, governance)**: autonomy without bounds is a liability, so encode these into the system instead of leaving them as assumptions.
  - **Continuation limits**: e.g. `--max-autopilot-continues N`.
  - **Dispatch throttling**: e.g. `MAX_STARTS` caps how many loops start per scheduling cycle.
  - **Idempotent triggering**: mark an issue *loop-started* before dispatching it, so overlapping runs don't start the same work twice.
  - **Conflict detection between concurrent loops**: compare target files, branches, worktrees or open PR diffs. On a conflict, pause or block one loop, and decide which continues by explicit policy (priority, age, ownership, or human review if ambiguous).
  - **Least-privilege MCP**: start read-only, scope credentials narrowly, and log tool activity.
  - **Hard governance gates**: sensitive areas need explicit authorization *even when verification passes*. Enforce this through hooks, branch protection, permissions or policy checks, not prompt reminders.
  - **Fast, non-blocking hooks**: hooks sit in the critical path, so set and monitor a latency budget (there's no universal limit).
  - **Observability**: track delivery metrics (lead time, defect escape rate, rollback frequency, review load, execution cost) and loop behavior (waiting time between stages, repeated attempts, tool failures, human interventions, conflict events, runs stopped by continuation or governance limits).

## Key Concepts
- **Loop Engineering**: designing the recurring, verifiable workflow that drives an agent from a trigger to a governed outcome, in short "designing the loop, not the prompt" (Osmani).
- **Delivery loop**: a running system that puts primitives, RPI and governance into operation for software delivery.
- **Tick**: one scheduled firing of the loop. Each tick advances *exactly one* capability and then stops.
- **Engine prompt**: the prompt `/loop` schedules (`deliver-feature.loop.md`). It reconstructs state, invokes the skill, advances one capability and stops.
- **Persisted state / thread-as-memory**: the GitHub issue and PR thread hold everything that lasts. Each tick rebuilds its state from the thread, never from chat history.
- **Executable contract**: an issue with machine-checkable acceptance criteria, which Discover reads and Complete closes on.
- **Done-condition (hard gate)**: a verifier job that refuses to pass while any `- [ ]` acceptance box is unchecked, so the loop physically can't declare itself finished early.
- **Unambiguous approval signal**: an explicit "plan approved" or a thumbs-up from a user with write access. Silence is not consent. An ambiguous reply triggers a clarification request, and comments from non-collaborators are logged but ignored.
- **Slice discipline**: one small, intent-named commit per plan step, each a reviewable diff, with progress written back to the thread.
- **Autopilot**: Copilot's mode for running multiple iterations without user input. It is separate from permissions.

## Mental Models
- Think of the issue as **the start of a loop, not a backlog item**: the pipeline *pulls* the work forward instead of the developer pushing it.
- Think of one tick as a fixed chain: **instructions (law) → prompt (engine) → skill (playbook) → thread (memory) → one capability advanced**. Run that chain on an interval and the five stages unfold.
- Use **Osmani's pieces** when asking "what does my loop need in order to run?", and the **five stages** when asking "where is this feature in its lifecycle?"
- Think of Gate 1 as **reviewing thinking, not typing**. It's the highest-leverage minute you'll spend on the feature.

## Anti-patterns
- **The loop with no done-condition**: if "done" isn't machine-checkable, the loop stops early (PR opened but criteria unmet) or never stops. Wire the acceptance criteria to a hard gate.
- **The unbounded loop**: without continuation limits or dispatch control, a loop that works in a demo creates uncontrolled costs at scale.
- **The fuzzy issue**: "Make the planner better" gives the loop no contract to close on. A loop is only as good as its trigger input, which is why the issue template counts as a primitive.
- **Verification as an afterthought**: if tests aren't inside the loop, quality depends on someone remembering to ask, which is exactly the failure loop engineering removes.
- **Confusing the product loop with the delivery loop**: a user's chat in the product is not a trigger for the build-time loop. Keep the two cleanly separated.
- **Ungoverned autonomy in sensitive areas**: letting the loop touch auth or payments without an explicit gate trades speed for an incident.
- **Manual relay of failures**: copying CI errors into prompts by hand. The loop should read the CI log through MCP itself.

## Code Examples
```text
/loop 15m advance the delivery loop for issue #4 by one capability using @.github/prompts/deliver-feature.loop.md
```
- **What it demonstrates**: a *long-running objective* rather than a task. `/loop` is an alias of `/every`. It is experimental in Copilot CLI (enable it with `/experimental on` or `--experimental`), and it fires only while the interactive session stays open. Run `/every` with no arguments to manage schedules. For unattended runs, use an external scheduler that calls Copilot CLI programmatically.

```markdown
## Goal (one sentence)
Create a simple, self-contained HTML landing page to announce the launch of the book.
## Requirements
- A single self-contained `index.html` (inline CSS, no build step, no external frameworks)
- Above the fold: title, subtitle, author, one-paragraph blurb; cover placeholder `img` with alt
- Primary CTA ("Get the book") linking to a configurable URL; "What you'll learn" with 3-5 bullets
- Responsive layout (no horizontal scroll at 375px width)
## Non-functional requirements
- No external network dependencies; basic accessibility (one <h1>, landmarks, alt, contrast)
## Acceptance criteria (machine-checkable)
- [ ] `index.html` renders title, subtitle, author, blurb, cover, and CTA (happy path)
- [ ] Layout is responsive with no horizontal overflow at 375px and 1280px widths
- [ ] Accessibility checks pass (single h1, landmarks, alt text, contrast)
- [ ] CI green
## Touches a sensitive area? No
```
- **What it demonstrates**: the issue as an executable contract (condensed from issue #4). The checkboxes are what the done-condition gate enforces, and the "sensitive area" flag decides whether the strict recovery rule applies.

## Reference Tables
**Table 7.1: Primitives and mechanisms in the GitHub Copilot delivery loop**

| Primitive / mechanism | Role in the loop | GitHub Copilot example |
|---|---|---|
| Instructions | Standing rules, constraints and governance boundaries for every iteration | `.github/copilot-instructions.md` |
| Prompt | Starts or advances one iteration and tells the agent which objective to pursue | `/loop` command + loop prompt |
| Skill | Encodes the reusable delivery method for performing the current capability | `deliver-feature` skill |
| Agent | Does the reasoning and execution for the current lifecycle stage | GitHub Copilot coding agent |
| Workflow / scheduler | Decides when the loop runs and which event or cadence starts the next iteration | GitHub Actions and/or `/loop` scheduling |
| Hooks / verification pipeline | Enforce deterministic checks and block progress when required controls fail | Repo hooks, CI checks, tests, linting |
| MCP | Controlled access to external systems (GitHub, CI, docs, APIs) | GitHub MCP Server |
| Persisted state | Records decisions, progress, evidence and outstanding work so the next iteration can resume | GitHub Issue + PR thread |

**Table 7.2: Repository artifacts and the capability each steers**

| Role | File | Steers |
|---|---|---|
| Instructions (brain) | `.github/copilot-instructions.md` | Always-on law: the five-capability cadence, two gates, guardrails. Auto-loaded every tick |
| Protocol (brain) | `.github/skills/deliver-feature/SKILL.md` | The playbook: the single source of truth for each capability, plus the "what's next" decision rule |
| Engine (brain) | `.github/prompts/deliver-feature.loop.md` | What `/loop` runs. One tick = one capability, then stop at gates |
| Contract | `.github/ISSUE_TEMPLATE/feature-loop.yml` | Forces a machine-checkable acceptance checklist |
| Verifier | `.github/workflows/verify.yml` | Runs on every push (Verify and Recover). Gates Complete while any box is unchecked |
| Guardrails | `.github/hooks/pre-pr.json`, `.vscode/mcp.json` | Keep Execute off `main`. Least-privilege MCP (read CI / write thread) |

## Worked Example
**Book-launch landing page (issue #4), companion repo `Valentina-Alto/loop-engineering-test`.** The engineer runs the `/loop 15m ...` command above. On every tick, Copilot auto-loads the instructions, runs the engine prompt and invokes the skill, which first reads the issue and PR through GitHub MCP.
1. **Discover**: the agent posts a comment restating the goal, turning the criteria into checkable tests and making its assumptions explicit (inline CSS, placeholder cover with alt text, system font stack, CTA defaulted to a placeholder URL). It also asks questions that would change behavior: a real cover or a placeholder? which store URL? dark-mode toggle? No code is written yet.
2. **Plan (Gate 1)**: the next tick posts a file-level change map (`index.html` + `tests/`), a criterion → test mapping, the verification approach and a rollback note, then stops. The author replies "plan approved", and the following tick acknowledges it.
3. **Execute**: on branch `feature/4-launch-page`, one slice per tick: semantic skeleton + `<h1>`/landmarks → hero → "What you'll learn" + CTA → responsive styles → a11y/responsive tests. The pre-pr hook silently blocks any push to `main`. The final comment summarizes the work and opens the PR.
4. **Verify and Recover**: lint and checks run after every slice, including a fixture-locked test for no horizontal overflow at 375px and 1280px, which turns "responsive" from a hope into a wall. Hypothetical failure: the CTA fails the contrast check. The next tick reads the CI log through MCP, darkens the button in line with the recorded assumptions, and reruns the check.
5. **Complete (Gate 2)**: the PR body lists the four acceptance boxes, each linked to evidence. The done-condition job is skipped on push and enforced on the pull-request event. Once all boxes are checked and CI is green, the loop posts "ready" and stops. The human reviews the branch and the rendered page, then approves and merges. That makes two human interventions in total.

## Key Takeaways
1. Engineer the loop, not the prompt. Humans set the objective, approve the plan and the merge, and improve the loop, while agents do everything in between.
2. Keep state in a durable thread (issue/PR), never in chat history. Every tick should rebuild its state from it.
3. Make "done" a hard, machine-checkable gate (unchecked boxes fail CI), and make the issue template a primitive that forces checkable criteria.
4. Put Gate 1 (the plan) before any code. Require an unambiguous approval from a user with write access, and treat silence as "wait".
5. Feed failures back automatically, but bound recovery: 3 attempts per criterion, stop immediately in sensitive areas, then roll back, replan or escalate.
6. Scale autonomy gradually: interactive, then limited permissions, then full Autopilot, with continuation caps, `MAX_STARTS`, idempotent triggers, conflict detection and least-privilege MCP.
7. Before shipping a loop, make five things explicit: the trigger, how state is reconstructed, which stage runs next, the verification and recovery rules, and where human approval is required.

## Connects To
- **ch03**: the loop is built from the six primitives (instructions = law, prompt = engine, skill = playbook, hooks = guardrails, MCP = connector).
- **ch04**: the five stages operationalize RPI, and Gate 1 is the Plan review.
- **ch05**: bounding controls and hard gates in sensitive areas apply the five-layer governance model.
- **ch02**: loops remove the manual-coordination bottleneck of Phase 1/2 teams and match the move from assistant to orchestrated workflows.
- **ch06**: same primitives, now run continuously instead of invoked one task at a time.
- **ch08**: zooms out to the full HVE operating model and Agent Experience (AX).
- **Addy Osmani, "Loop Engineering" (2026)**: source of "design the loop, not the prompt" and the five pieces plus state.
- **Harness engineering (Zhong & Zhu, 2026)**: the runtime-substrate layer the loop sits on.
- **GitHub Copilot CLI `/loop`/`/every`, Autopilot, `/fleet`**: the reference implementation.
