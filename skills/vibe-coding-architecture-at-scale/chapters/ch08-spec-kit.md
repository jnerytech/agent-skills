# Chapter 8: Spec Kit in Practice: From Prompt to Merged Code

## Core Idea
GitHub Spec Kit is the reference harness for SDD: it rides on top of whatever agent you use and installs the same gated command loop — constitution, specify, plan, tasks, implement — so the workflow is identical whoever drives it. The asset is the ordered, human-gated shape, not the tool; and the loop orders the spec, it does not enforce it.

## Frameworks Introduced
- **The Spec Kit command loop**: `/speckit.constitution → /speckit.specify → /speckit.plan → /speckit.tasks → /speckit.implement`, a human review gate on every arrow.
  - When to use: driving any feature from intent to merged code with an AI agent, especially across a team using different agents.
  - How: (1) `/speckit.constitution` once per repo — governing principles: code quality, testing standards, UX consistency, performance budgets. (2) `/speckit.specify` — WHAT and WHY only; no library names, no code. (3) `/speckit.plan` — supply stack and architecture; agent plans, then stops; read it against the spec in under a minute. (4) `/speckit.tasks` — ordered, reviewable task list; this list (not the prose) is what implement executes. (5) `/speckit.implement` — execute tasks against the spec until built. Codex CLI in skills mode uses `$speckit-*` instead.
- **The Tool Is the Example (shape over product)**: intent → committed spec → plan → tasks, a human gating each step.
  - When to use: evaluating or replacing spec tooling as CLI verbs drift.
  - How: if Spec Kit disappears, recreate the ordered, gated loop in its successor; nothing is lost.
- **Separate the stable what from the disposable how**: the intent is the expensive artifact; implementations are regenerable.
  - When to use: deciding where to invest effort; changing course mid-project.
  - How: amend the spec, regenerate the plan, re-run the loop — early decisions become editable instead of locked in.

## Key Concepts
- **Spec Kit**: open-source GitHub framework installing a namespaced slash-command loop into Claude Code, Copilot, Gemini CLI, Cursor and others.
- **`specify` CLI**: Spec Kit's installer/scaffolder, installed via `uv`, pinned to a release tag.
- **`--integration`**: init flag selecting the agent (`copilot`, `claude`, `gemini`, …) so the workflow is uniform.
- **`specify init`**: automates the Ch 7.2 repository constitution and Day-One setup — lays down the spec dir and registers slash commands.
- **Constitution**: repo-wide non-negotiables written once, binding every later step.
- **Intent is the source of truth**: AI makes the spec executable, so the spec decides what gets built rather than describing what was built.
- **Requirements location problem**: security, compliance, design system and integration constraints otherwise live in heads, wikis and chat history; here they go into constitution and plan where the agent consumes them.

## Mental Models
- Think of models as **extraordinary at pattern completion, incapable of reading your mind**: "add photo sharing" forces a thousand unwritten decisions (storage, permissions, resizing, moderation, visibility) that surface late, when unwinding is most expensive.
- Think of Spec Kit as **a harness bolted onto a generic agent from outside** — one design point; Ch 9's Kiro is the opposite packaging (spec as substrate).
- Use the loop because **security becomes a clause the implementation is generated against from the first command**, not a bolt-on after the demo.
- The technique is **stack-indifferent**: the hard part is never syntax, it's translating intent into behavior.

## Anti-patterns
- **Tracking `main` for the CLI**: non-reproducible across the team; pin a released tag.
- **Naming frameworks/classes in `/specify`**: reintroduces the guessing the discipline exists to remove.
- **"Describe it and hope" prompting**: wrong assumptions discovered deep in implementation.
- **Spec Kit doc with no architectural test, contract test or annotation behind it**: "a wish, not a guardrail" — the agent satisfies its letter and erodes the structure.
- **Starting to type on greenfield**: without a spec the agent builds the generic average of its training data, not your system.

## Code Examples
```bash
uv tool install specify-cli --from git+https://github.com/github/spec-kit.git@vX.Y.Z
specify init my-project --integration copilot
cd my-project
```
- **What it demonstrates**: pinned, reproducible install and scaffolding with an explicit agent integration.

```text
/speckit.constitution → non-negotiables once: code quality, testing standards, UX consistency, performance
/speckit.specify      → WHAT and WHY for this feature, no library names, no code
/speckit.plan         → tech stack and architecture; the agent plans, then stops
/speckit.tasks        → decompose the plan into an ordered, reviewable task list
/speckit.implement    → execute the tasks against the spec until the feature is built
```
- **What it demonstrates**: Ch 7.5's three-phase workflow wrapped in commands.

## Reference Tables
| Scenario | Why the loop wins |
|---|---|
| Greenfield (zero-to-one) | Small upfront spec+plan makes the agent build *your* system, not the training-data average. Ch 8b: CodeKarta, blank SPEC.md → compiling tested build in under 9 minutes |
| Feature work in existing system (N → N+1) | Highest-value case: spec forces stating exactly how the feature touches what exists; plan encodes architectural constraints so new code reads native. Ch 3 context discipline becomes mandatory |
| Legacy modernization | Original intent is lost; recover business logic into a modern spec, design a clean architecture in the plan, rebuild without carrying inherited debt |

## Worked Example
**Photo organizer.** `/speckit.specify`: "albums grouped by date, re-orderable by drag-and-drop on the main page, never nested, photos shown as tiles within an album" — no framework or class anywhere. `/speckit.plan`: "Vite, as few libraries as possible, vanilla HTML/CSS/JS, images never uploaded, metadata in a local SQLite database" — the agent produces a detailed plan and stops; you check it against the spec in under a minute before any code exists. `/speckit.tasks` produces the concrete ordered list; `/speckit.implement` executes against that list.

## Why It Works / Failure Mode
- **Mechanism**: spec, plan and focused task list remove degrees of freedom up front (Ch 7.4's hallucination suppression, applied to the whole feature) — the model no longer guesses what, how, or in what order. Gates catch misreadings when they're cheapest.
- **Failure mode**: the loop industrializes authoring and sequencing, not enforcement. Without the Ch 4–6 tests, annotations and diagrams behind it, the spec is satisfied in letter while architecture erodes. Spec Kit is open-sourced because the innovation is the process — any team can run it by hand.

## Key Takeaways
1. Spec Kit standardizes one gated loop across every agent — one process, no per-tool dialect.
2. Pin the CLI to a release tag; `specify init --integration <agent>` automates the repo constitution.
3. Keep `/specify` pure intent; supply the how only at `/plan`, and review between every step.
4. The task list, not the prose, is what implementation executes against.
5. Biggest payoff is N → N+1 feature work in existing systems.
6. Intent, not code, is now the source of truth — but only guardrails make the spec true.

## Connects To
- **Ch 7**: the SDD paradigm, three-phase workflow and command shape this chapter runs.
- **Ch 4**: cross-platform consistency (VibeTags) restated for specs.
- **Ch 3 / 5 / 6**: the guardrails that enforce what the loop produces.
- **Ch 8b**: CodeKarta greenfield case study; **Ch 8c**: brownfield inversion.
- **Ch 9**: Kiro — spec-native environment, opposite packaging.
- **Conclusion (Incremental Adoption Roadmap)**: `init` automates the Day-One setup.
