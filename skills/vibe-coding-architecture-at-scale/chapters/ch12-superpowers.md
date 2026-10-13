# Chapter 12: Superpowers: The Portable Workflow

## Core Idea
Superpowers (github.com/obra/superpowers) expresses a complete, mandatory development lifecycle as portable agent skills plus initial instructions, so the same methodology runs identically on Claude Code, Codex, Gemini CLI, Cursor, Copilot CLI, OpenCode and Factory Droid. It enforces *how* you develop (plans without placeholders, fresh subagent per task, test-first with deletion) — not *what* you build.

## Frameworks Introduced
- **One Plugin, Every Agent (portability as a design constraint)**: the whole methodology must be expressible as markdown skills, shell commands and step sequences with zero platform-specific calls.
  - When to use: the team has not converged on one harness, or you want the workflow to outlive any single vendor.
  - How: write every instruction so any agent can execute it; persist interfaces (plans) to the filesystem, not in-memory structures; if a skill needs a particular agent's capability, treat that as a sign the instruction was not explicit enough.
- **The Seven-Stage Lifecycle**: Brainstorming → Git Worktrees → Writing Plans → Subagent Execution → Test-Driven Dev → Code Review → Branch Finishing, each backed by a skill that auto-activates on workflow state.
  - When to use: as the default path for every feature, not an opt-in.
  - How: the shipped CLAUDE.md tells the agent to recognize state and fire the matching skill (idea described → brainstorming; spec exists → planning; implementation starts → TDD). "Mandatory workflows, not suggestions."
- **Plans Without Placeholders**: a plan is the executor's instruction set, complete enough that no interpretation is required.
  - When to use: every plan handed to an implementing agent.
  - How: save to `docs/superpowers/plans/YYYY-MM-DD-<name>.md`; split into 2–5 minute tasks with exact files, exact code, exact shell command, and expected output; before hand-off run a two-stage self-review — spec coverage check, then a placeholder scan by name. A task referencing a type/function defined nowhere else in the plan is a plan failure.
- **Subagents as Context Firewalls**: dispatch a fresh agent per task; never let one context accumulate across tasks.
  - When to use: multi-task work where context rot (Ch 3) would otherwise build up.
  - How: implementer subagent receives only the plan step, file paths, test command, expected output; then a spec-reviewer subagent checks compliance with the step and a code-quality reviewer subagent checks the diff — neither inherits the implementer's context. The coordinator's context grows only with review results and checked-off steps.
- **TDD Enforcement That Deletes Code**: "If you didn't watch the test fail, you don't know if it tests the right thing."
  - When to use: all implementation.
  - How: RED first, GREEN second, no exceptions; if implementation appears before a failing test, delete it and restart — not flag, not warn.

## Key Concepts
- **Superpowers**: a cross-platform composable skills library that imposes a full SDLC on whatever agent runs underneath.
- **Auto-activating skill**: a skill triggered by recognized workflow state rather than by the developer remembering a command.
- **Placeholder (plan failure)**: "TBD", "TODO", "implement later", "Add appropriate error handling", "Write tests for the above" without code, "Similar to Task N", or any step describing what without showing how.
- **2–5 minute task**: the plan granularity — failing test, confirm failure, minimal code, run suite, commit, each with exact command and expected output.
- **Context firewall**: task isolation where each completion is a context reset, so implementation details never accumulate in the coordinator.
- **Two-stage review**: spec compliance check first, then code quality check, by separate subagents.
- **Git worktree isolation**: an isolated branch and workspace per feature.
- **Filesystem as universal protocol**: persisted plans are the interface between coordinator and workers — human-inspectable and readable by any agent without special tooling.
- **Process enforcer vs structure enforcer**: Superpowers governs the session; structural guardrails (Ch 4–5) govern the codebase.

## Mental Models
- Think of an unexpanded step like "Implement the retry logic" as handing the agent an **improvisation budget**; a plan with signature, test and command removes it.
- Think of the coordinator session as a manager holding an audit trail, and subagents as isolated workers that cannot contaminate each other.
- Use deletion over warning when a rule's violation is cheap to detect and expensive to defer — the cost is paid at discovery, not at a human review.
- Treat a vendor plugin as the most replaceable artifact; the durable asset is the constraint that shaped it (keep your workflow expressible without binding to one surface).

## Anti-patterns
- **Placeholder plans**: "TBD"/"Similar to Task N" leave interpretation to the executor, which is where drift starts.
- **Single long session across tasks**: the context becomes a palimpsest of every decision; context rot follows.
- **Writing the test against working code**: it can pass while testing nothing — worse than no test, because it occupies the slot a real test would fill.
- **Tests that mock implementation details, duplicate logic, or assert on intermediate state**: named failures in the TDD skill's anti-patterns doc, not style issues.
- **Platform-specific skill instructions**: break portability and signal the instruction was not explicit enough.
- **Treating Superpowers as architecture enforcement**: tested, reviewed code can still be a tangled module graph or a service with no contract test.

## Code Examples
```text
1. Brainstorming        → refine the idea; ask before coding; validate in sections
2. Git Worktrees        → create an isolated branch and workspace
3. Writing Plans        → break into 2-5 minute tasks; exact files, exact code
4. Subagent Execution   → dispatch a fresh agent per task; two-stage review after each
5. Test-Driven Dev      → RED first; GREEN second; no exceptions
6. Code Review          → spec compliance check, then code quality check
7. Branch Finishing     → verify, merge or PR, cleanup
```
- **What it demonstrates**: the full mandatory lifecycle, each stage a skill fired by workflow state.

```bash
# Claude Code
/plugin install superpowers@claude-plugins-official
# or via the marketplace
/plugin marketplace add obra/superpowers-marketplace
/plugin install superpowers@superpowers-marketplace
# Gemini CLI
gemini extensions install https://github.com/obra/superpowers
```
- **What it demonstrates**: one-command install per harness; Cursor via marketplace search for "superpowers".

## Reference Tables
| Aspect | Superpowers |
|---|---|
| What | Cross-platform agent workflow methodology plugin |
| Shape | Portable multi-agent lifecycle orchestration |
| Core move | Mandatory skills activate automatically across all harnesses |
| Enforcement | TDD: code written before tests is deleted; plans: no placeholders |
| Subagent model | Fresh agent per 2–5 minute task; two-stage review after each |
| Isolation | Git worktrees per feature; context firewall per task |
| Install | One command on 8+ platforms |
| Limit | Process enforcer, not structure enforcer; tested code ≠ sound code |

Part III's spec-driven cluster, by shape: harness (Spec Kit), environment (Kiro), orchestration graph (Zenflow), context-engineering framework (GSD), portable workflow methodology (Superpowers); the last shape — procedural knowledge forged from your own codebase — is Skill Forge.

## Worked Example
Turning a vague step into a placeholder-free plan task:
- **Before**: "Implement the retry logic. Add appropriate error handling. Write tests for the above."
- **After** (one 2–5 min task, the shape the skill requires): (1) the failing test, with its actual code in the plan; (2) the exact command to run it and the expected output — FAIL; (3) the minimal implementation, function signature and body shown in full; (4) the exact suite command — expected PASS; (5) commit. Self-review before hand-off: spec coverage check, then a placeholder scan by name; every referenced type or function is defined somewhere in the plan.
- Execution: coordinator dispatches a fresh implementer with only this step; spec reviewer checks it against the step; quality reviewer checks the diff. If the implementation appeared before the test was watched failing, the code is deleted and the task restarts.

## Why It Works / Failure Mode
- **Context firewalls**: an agent starting fresh on a bounded task with exact instructions and a known verification step has no accumulated context to drift with — it either passes the two-stage review or it doesn't. This is why multi-hour autonomous runs without plan deviation are a structural property, not a marketing figure. It breaks when the plan itself is loose: the firewall preserves fidelity to the plan, so placeholders reintroduce improvisation.
- **Destructive TDD**: the cost of skipping RED is paid immediately, with no human override negotiation. It breaks at the level of *what* is tested — TDD keeps tests honest, not complete; and the brainstorming validation checks the developer's stated intent, not annotation invariants (Ch 4) or structural tests (Ch 5).

## Key Takeaways
1. Make the workflow mandatory and state-triggered; advice the agent may skip is not enforcement.
2. A plan is an instruction set: 2–5 minute tasks, exact code, exact commands, expected outputs, zero placeholders.
3. Fresh subagent per task plus separate spec and quality reviewers keeps context from rotting.
4. Delete code written before a failing test; a test never seen failing proves nothing.
5. Portability forces explicitness — persist plans to the filesystem as the universal protocol.
6. Superpowers governs the session, not the architecture; pair it with ArchUnit rules, VibeTags and the Inquisitor.

## Connects To
- **Ch 1**: separating intent from enforcement, here applied to the development process itself.
- **Ch 3**: context rot, which the per-task firewall prevents.
- **Ch 4 / Ch 5**: annotations and structural tests that Superpowers does not check.
- **Ch 7**: spec must drive behavior; Superpowers applies it to how you develop.
- **Ch 8–11**: Spec Kit, Kiro, Zenflow, GSD — the other spec-driven shapes.
- **Ch 16**: Skill Forge, the final shape — knowledge forged from your own codebase.
- **Ch 22**: the two-agent Inquisitor that complements the two-stage review.
- **Red-Green-Refactor (Beck)**: TDD enforced destructively.
