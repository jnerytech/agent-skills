# Chapter 11: Get-Shit-Done: Spec-Driven Plus Context Engineering

## Core Idea
Get-Shit-Done (GSD) is the fourth shape of spec-driven tooling and the only one built around context rot: it makes context allocation a runtime invariant the framework enforces (main window held at 30–40%, heavy work in fresh subagents), with durable state in repository files. Across all four tools the lesson is convergence: spec tools author and sequence intent; they never enforce it.

## Frameworks Introduced
- **The Six-Command Loop**: a meta-prompting framework for coding agents (Claude Code, OpenCode, Gemini CLI, others) driven by six sequential commands.
  - When to use: phased feature work where long sessions would otherwise degrade output quality.
  - How: (1) `/gsd-new-project`: questions → research, requirements, ROADMAP (constitution + spec, Ch 7–8). (2) `/gsd-discuss-phase N`: pin layout, API contracts, error handling before planning; forbids reliance on "reasonable defaults". (3) `/gsd-plan-phase N`: atomic, individually verifiable task plans. (4) `/gsd-execute-phase N`: independent plans run in parallel waves, one atomic commit per task (Ch 24 save-state as a byproduct). (5) `/gsd-verify-work N`: manual acceptance; failures yield diagnostic fix plans. (6) `/gsd-ship N`: open a PR from verified work.

- **Context Allocation Invariant**: hold the main context at 30–40% capacity; delegate heavy work to fresh subagents (researchers, planners, executors, verifiers, debuggers), each given only its slice.
  - When to use: whenever context rot is the constraint limiting how large or long-running work can be.
  - How: keep the coordinating session lean by structure, not by habit; spin up isolated contexts born fresh and discarded after the detail-heavy task, so rot never accumulates. This is the Chapter 3 Context Diet stated as an allocation policy.

- **Repo-Resident Spec State**: persist the spec as versioned Markdown that survives sessions.
  - When to use: always; the source of truth is the repository, not the chat window.
  - How: `PROJECT.md` (vision), `REQUIREMENTS.md` (scope), `ROADMAP.md` (milestones → phases), `STATE.md` (current position + decisions made), `CONTEXT.md` (per-phase specifics), `.planning/` (phase artifacts, config). `STATE.md` prevents the AI from re-litigating settled decisions.

- **Six Questions for Judging the Next Tool**: evaluate any new spec tool against properties, not marketing.
  - When to use: a new entrant, rebrand, or acquisition appears.
  - How: ask (1) Is the spec a durable, version-controlled artifact or a nicer chat box? (Ch 7) (2) Is there a human gate between *what*, *how*, and *do*? (§7.5) (3) Does it constrain input (schema, EARS, typed graph) to suppress hallucination? (§7.4) (4) Does it respect the context diet: lean window, on-demand retrieval? (Ch 3, 11) (5) Does it treat external/tool input as untrusted, so a hijacked agent is harmless? (Ch 19) (6) Does it claim to *enforce*, or admit it only *authors and sequences*? Score by yes-count; weight question 6 heavily, since it's the one vendors most want you not to ask.

## Key Concepts
- **Context rot**: decay of AI output quality as the window fills with accumulated detail (Chapter 3's thesis by another name).
- **Meta-prompting framework**: a layer of commands/prompts orchestrating an existing coding agent.
- **STATE.md**: the durable record of where you are and what you already decided.
- **Fresh subagent context**: an isolated window seeded with only the needed slice, discarded afterward.
- **Verify, don't assume**: verification walks the implementation; broken functionality produces a fix plan that is re-executed rather than hand-debugged.
- **Profiles/modes**: core, standard, quality/balanced/budget model tiers; interactive (confirm each step) vs yolo (auto-approve all).
- **Four shapes**: harness you bolt on, environment you live in, graph you execute, context budget you enforce.

## Mental Models
- Think of GSD as Chapter 3 promoted from a discipline you remember to a mechanism that works whether you remember or not.
- Treat review gates between spec, plan, and execution as where the architect's judgment enters the loop, not friction to optimize away.
- Choose a spec tool by the constraint that binds your team, not by feature list.
- The tool is the example: keep the invariant (context is a budget; durable state in the repo; each unit of work starts fresh and lean) even if GSD disappears.

## Anti-patterns
- **yolo mode**: deletes the human review gate; a spec-driven framework on full auto-approve ships the wrong architecture quickly.
- **"Reasonable defaults"**: undiscussed layout/contracts/error handling invite hallucination.
- **Hand-debugging a failed phase**: re-run execute from a diagnostic fix plan instead (reload, don't untangle).
- **Believing a spec tool enforces architecture**: none of the four runs an architectural test, freezes a wire contract, or fails a build.
- **Installing from look-alike repos**: verify you are using the maintained GSD repository; similarly named packages may be different projects.

## Code Examples
```text
/gsd-new-project     → questions → research, requirements, ROADMAP
/gsd-discuss-phase N → pin the decisions for phase N before any planning
/gsd-plan-phase N    → research + generate atomic, verified task plans
/gsd-execute-phase N → run independent plans in parallel, atomic commit per task
/gsd-verify-work N   → manual acceptance test; failures get diagnostic fix plans
/gsd-ship N          → open a PR from verified work
```
- **What it demonstrates**: the spec loop with a discuss gate before planning and save-state commits during execution.

## Reference Tables
| Tool | Where the spec lives | Distinctive move | Reach for it when |
|---|---|---|---|
| Spec Kit (Ch 8) | Markdown + slash commands on any agent | One ordered command loop, mandatory human gate between phases | Team runs mixed agents and wants the identical loop on all |
| Kiro (Ch 9) | `requirements.md` / `design.md` / `tasks.md`, IDE-native | Requirements constrained to EARS, suppressing hallucination at input | You want the disciplined path to be the default, not opt-in |
| Zenflow (Ch 10) | Declarative YAML DAG, schema-validated | Cycles/bad deps/malformed logic caught before a token is spent | Multi-agent work needing determinism and reproducibility |
| GSD (Ch 11) | Repo files (`STATE.md`, `ROADMAP.md`, …) + lean window | Context allocation: main session at 30–40%, heavy work to fresh subagents | Context rot limits how large or long-running work can be |

Convergence: all four pin intent in version-controlled files before the prompt, gate *what* / *how* / *do*, and keep the chat window from being the source of truth. Differences are ergonomics, not philosophy.

## Why It Works / Failure Mode
- **Context allocation**: jamming everything into one window causes precision collapse akin to human cognitive overload; a structurally capped main window plus disposable subagent contexts means rot cannot accumulate. Fails when users switch to yolo or stuff the main session anyway, and it never covers enforcement: the architecture still needs Ch 4–6 tests, annotations, diagrams and Part IV CI.
- **Six-question rubric**: targets failure modes of generation itself, which don't rebrand, so it stays valid as products churn. Fails if you skip question 6 and buy a tool that claims to make architecture "safe".

## Key Takeaways
1. Treat context as a budget: keep the main window at 30–40% and push heavy work into fresh subagents.
2. Persist vision, scope, roadmap, state, and per-phase context in repo files; `STATE.md` stops re-litigation.
3. Pin decisions in a discuss step before planning; don't accept "reasonable defaults".
4. Execute as atomic per-task commits; on failure, re-execute from a fix plan instead of debugging by hand.
5. Never run spec frameworks in yolo; keep the human gates.
6. Judge new tools with the six questions, weighting "does it admit it doesn't enforce?" heavily.
7. Spec tools author and sequence; guardrails enforce.

## Connects To
- **Ch 3**: Context Diet; context rot; Tier 1/2/3 context files.
- **Ch 7 (§7.4, §7.5)**: spec as source of truth, input constraints, human gates.
- **Ch 8 / 9 / 10**: Spec Kit, Kiro, Zenflow, the other three shapes.
- **Ch 5 / Ch 22**: don't verify by reading; machine-to-machine remediation.
- **Ch 24**: save-state commits; reload, don't untangle.
- **Ch 19**: untrusted tool input; least privilege and sandboxing.
- **Ch 16**: forging skills from your repository, the next input-side instrument.
- **Ch 4–6, Part IV**: where enforcement actually lives.
