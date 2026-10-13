# Chapter 3d: The Configuration Surface: Memory, Skills, Subagents, and Hooks

## Core Idea
An agent harness exposes a **configuration surface** of four kinds of slot (standing instructions, skills, subagents, hooks) at three levels (global, project, local). Most "model failures" are really configuration failures from cramming all four jobs into one instruction file. Route each piece of intent to the right cell. Only the hook enforces; the other three advise.

## Frameworks Introduced
- **The Four Slots**: each slot answers a different question.
  - When to use: whenever you have intent to install in an agent.
  - How: **Standing instructions** answer "what is always true here?" and load on every turn. **Skills** answer "how do we do this specific thing?" and load only when it comes up. **Subagents** answer "who should do this, with what context and tools?" and run in a separate window. **Hooks** answer "what must happen automatically, whether or not the model agrees?" and run your code, not the model's judgment.
- **Kind × Level Grid** (4 × 3): most configuration mistakes confuse one axis for the other.
  - When to use: deciding *where* a rule, skill, agent, or hook lives, and evaluating a new harness.
  - How: **Global is you. Project is the team. Local is this machine.** Global covers personal ergonomics across all repos and never reaches teammates or CI. Project is version-controlled team law, including for CI agents (the repo as constitution). Local is git-ignored: secrets, machine paths, week-long experiments. Levels stack (concatenate), and on a direct conflict the specific wins over the general (local > project > global). Precedence is the boring part; placement is what matters. When evaluating tools, read the **blank cells**: a harness with no subagent column can't give you an independent reviewer in the loop, and one with no hook column can advise but never enforce.
- **Instruction vs. Skill rule: frequency against specificity**:
  - When to use: deciding whether something goes in CLAUDE.md or a skill.
  - How: if it's always true on every task ("Java 21, no Lombok"), make it an instruction. If it's a specific procedure for some tasks ("how we cut a release," "add an outbox event," "regenerate the OpenAPI client"), make it a skill. The test: if the agent only needs to know it while doing one particular kind of work, it's a skill. Moving it out makes CLAUDE.md leaner and lets the skill afford to be long.
- **Instruction File as Lightweight Router**: cut everything the code already states, keep the *why* the code can't state, and point at the other three slots instead of acting as a wiki that replaces them. Use `@path` imports and nested/directory-scoped files so long-form reasoning sits one hop away and costs nothing until it's relevant.
- **Narrow Subagent design rule**: a subagent earns its keep through narrowness. Its tool allowlist *is* its blast radius.
  - How: give it the minimum tools. A reviewer reads and runs, never writes. A search agent reads only. Give it an objective opposite to the generator's ("you did not write this code").
- **One Intent, Three Depths (defense in depth)**: install a single architectural rule as an instruction (the agent knows it), a hook (a lapse can't be saved locally), and an architectural test (it holds at the PR even if someone disables the hook).

## Key Concepts
- **Configuration surface**: the set of slots where intent stops being repeated in prompts and becomes something the machine carries for you.
- **Standing instructions**: always-on invariants (layering rule, stack pins, testing policy, do-not-touch list). This is the most expensive real estate on the surface.
- **Skill**: a named bundle (`SKILL.md` + optional scripts/references). Only the one-line description loads every turn, and the body loads when the task matches, so 40 skills cost 40 descriptions per turn.
- **Skill description as trigger**: write it to name the situation ("Use when asked to release, tag, or publish"), not as a title, because that sentence does the retrieval.
- **Subagent**: a separate invocation with a fresh context window, a scoped system prompt, and its own tool allowlist. Only its result returns.
- **Hook**: your code fired on a loop event (`PreToolUse`, `PostToolUse`, `Stop`/`SubagentStop`, `UserPromptSubmit`, `SessionStart`), deterministic, with no model judgment in the path.
- **Exit code as contract**: a blocking hook exits non-zero (exit 2 in Claude Code), and its stderr goes back to the model as the reason, so it both vetoes and teaches.
- **Tool vs. MCP vs. Skill**: a tool is a capability. MCP is how you add tools. A skill adds no capability, only procedural knowledge about combining existing tools your way.
- **Skill provenance**: a skill copied from another stack is a "tourism brochure" (Ch 16). Skill Forge forges skills cited to real `file:line` evidence.

## Mental Models
- Use a tool or MCP server when the agent *can't* do something. Use a skill when it can but does it wrong, inconsistently, or the long way around.
- Think of a subagent as two benefits in one: **context hygiene** (exploration tokens burn in a disposable window, which keeps the orchestrator at 30–40%) and **independent perspective** (it inherits none of the generator's rationalizations).
- Think of hooks as the bridge from "human intent in" to "machine enforcement out": the one place you stop persuading and start enforcing.
- Prefer a directory-scoped rule over the global rule it could have been: it stays invisible until it's relevant.

## Anti-patterns
- **Using only the instruction file** ("a fifth of the tool"): the agent forgets the build command, re-derives fragile codegen, rubber-stamps its own reviews, and edits the forbidden file.
- **Trusting `/init` output**: it records the *what* the agent infers on sight (folder layout, framework, camelCase, Jest, uv), spending the most expensive budget restating the obvious. It's a manual written for an amateur, and the reader is an expert.
- **Bloated instruction file (> 40–50k tokens)**: it dilutes attention (a stray "always use uv" leaks into unrelated tasks), burns tokens every turn (a 5-hour usage window gone on a one-line change), and misleads the planner into spawning explore agents to audit the whole tree for a single-line edit.
- **Team law at a personal level**: a critical hook or boundary rule in global settings works on your machine and protects nothing anywhere else. "The guardrail that only one person has is not a guardrail; it is a coincidence."
- **Personal taste at the project level**: the whole team pays attention-budget rent on your preference, every turn, forever.
- **Reaching for MCP when a skill was missing**: you get a sprawling tool surface and an agent that still does the wrong thing, "now with more buttons to press."
- **Write-capable reviewer subagent**: it can "fix" a violation into invisibility, or be talked into destructive actions by untrusted input.
- **Naive hook scripts**: interpolating an agent-chosen filename into a shell command is command injection. Hooks are production code on a hostile input path.

## Code Examples
```json
{ "hooks": {
  "PreToolUse":  [ { "matcher": "Edit|Write",
    "hooks": [{ "type": "command", "command": ".claude/hooks/deny-locked.sh" }] } ],
  "PostToolUse": [ { "matcher": "Edit|Write",
    "hooks": [{ "type": "command", "command": "scripts/format-changed.sh" }] } ],
  "Stop": [ { "hooks": [{ "type": "command",
    "command": "./gradlew test --tests '*InnerLoop*' -q" }] } ]
} }
```
- **What it demonstrates**: the three canonical project hooks in `.claude/settings.json`: protect frozen files, auto-format every edit, and run inner-loop tests before the agent says "done." `deny-locked.sh` reads the pending tool call as JSON on stdin and greps the target for `@AILocked`. About twenty lines of shell turn a convention into a wall.

```markdown
---
name: boundary-reviewer
description: Reviews a diff for architectural-boundary violations, before a PR is opened.
tools: Read, Grep, Bash
model: sonnet
---
You are a boundary reviewer. You did not write this code, and you do not care whether
the prompt that produced it succeeded. Read the diff and the rules in `CLAUDE.md` and
`architecture/boundaries.md`. Report only violations of stated boundaries, each as
`file:line | rule broken | why it matters`. If there are none, say so in one line.
Do not comment on style. Do not edit files.
```
- **What it demonstrates**: a narrow subagent. A read/run-only allowlist means it can't edit what it judges, and "you did not write this code" states the purpose of the slot.

```markdown
---
name: cut-release
description: How we cut a release. Use when asked to release, tag, or publish a version.
---
# Cutting a Release
1. Confirm `main` is green: `./gradlew check`.
2. Bump the version in `gradle.properties` (semver: a breaking change is a major bump).
3. Regenerate `CHANGELOG.md` from the commits since the last tag.
4. Tag and push: `git tag -s vX.Y.Z -m "vX.Y.Z" && git push --follow-tags`.
5. The `release` workflow publishes the artifact; confirm the GitHub release once CI is green.
```
- **What it demonstrates**: a project skill with a trigger-style description. The body costs nothing until the match fires.

## Reference Tables
**Claude Code files by kind × level**

| Kind | Global (you) | Project (repo) | Local (checkout) |
|---|---|---|---|
| Instructions | `~/.claude/CLAUDE.md` | `./CLAUDE.md` | `./CLAUDE.local.md` |
| Skills | `~/.claude/skills/` | `./.claude/skills/` | (none) |
| Subagents | `~/.claude/agents/` | `./.claude/agents/` | (none) |
| Hooks/settings | `~/.claude/settings.json` | `./.claude/settings.json` | `./.claude/settings.local.json` |

**Cross-harness translation**

| Harness | Instructions | Skills/commands | Subagents | Hooks |
|---|---|---|---|---|
| Claude Code | CLAUDE.md | .claude/skills/* | .claude/agents/* | settings.json hooks |
| Codex CLI | AGENTS.md | .codex/prompts/* | (none) | .codex/config.toml (limited) |
| Cursor | .cursor/rules/*.mdc | saved prompts | background agents | (rules + CI only) |

**Routing table: one intent, the right slot**

| You want… | Slot | Level | Why |
|---|---|---|---|
| "Java 21, no Lombok, web must not import persistence" | Instruction | Project | Invariant, binds everyone |
| "Explain before big refactors; I read diffs" | Instruction | Global | Your ergonomics |
| "How we cut a release / add an outbox event" | Skill | Project | Specific, shared procedure |
| "My scratch-debugging routine" | Skill | Global | Portable, yours |
| "Review this diff adversarially" | Subagent | Project | Isolation + opposite objective (Ch 22) |
| "Search without polluting my window" | Subagent | Either | Disposable context |
| "Run formatter after every edit" | Hook (PostToolUse) | Project | Deterministic, shared |
| "Never write to an @AILocked file" | Hook (PreToolUse) | Project | Enforcement, not advice |
| "Run 30-second tests before done" | Hook (Stop) | Project | Close inner loop (Ch 5b) |
| "Staging port on my box this week" | Instruction | Local | Throwaway, never committed |

## Worked Example
**"The `web` package must not import `persistence`" installed at three depths.**
1. *State it*: in project `./CLAUDE.md`, as a short invariant with a pointer to the rationale:
   ```markdown
   # ./CLAUDE.md: project, checked in, the team's law
   - Java 21, Spring Boot 3.x. No Lombok.
   - The `web` package must not import `persistence` entities.
   - Every logic change ships with its test. Rationale: @architecture/boundaries.md
   ```
2. *Check it*: the `boundary-reviewer` subagent reviews diffs before the PR.
3. *Enforce it locally*: a `PreToolUse` hook vetoes the bad write, exits 2, and explains on stderr, so the agent self-corrects next turn.
4. *Enforce it in CI*: an ArchUnit-style architectural test (Ch 5) holds even if someone disables the hook.
Your global file can say "I read diffs, not prose" at the same time, and both are honored because the levels concatenate.

## Why It Works / Failure Mode
- **Slot/level routing** works because each slot has a different cost profile: always-on (expensive, invariants only), on-demand (free until matched), isolated (its tokens and biases stay out of the main window), deterministic (no judgment to drift). It fails when everything goes in the always-on file, or when team law sits at a personal level and silently doesn't travel to teammates or CI.
- **Hooks** work because they don't depend on the model remembering anything under a full context window, and because stderr feedback turns a veto into teaching. They fail as attack surface: they run with your privileges and fire on agent actions driven by possibly untrusted input (Ch 19). Quote variables, validate the JSON payload, and grant least privilege. Tool-dependent hooks belong in `settings.local.json`.
- **The surface is necessary, not sufficient**: it installs capability, not judgment. Deciding which invariants and boundaries are load-bearing is the architect's job. Configure it by accident and the agent inherits only your omissions.

## Key Takeaways
1. Four slots, each answering a different question: what is always true (instructions), how to do X (skills), who does it in isolation (subagents), what must happen regardless (hooks).
2. Three levels: global is you, project is the team (including CI), local is this machine. Placement matters more than precedence.
3. Keep the instruction file a lean router of invariants and *why*s. Skip what `/init` writes, and push procedures into skills and rationale into `@imports`.
4. Write skill descriptions as triggers. A skill teaches combining existing tools, while MCP adds capabilities.
5. Keep subagents narrow (minimal tools, opposite objective) for context hygiene and independent review.
6. Only hooks enforce. Treat hook scripts as production code on a hostile input path.
7. Install key rules at three depths: instruction, hook, architectural test.

## Connects To
- **Ch 3**: the context diet and on-demand tier, which the surface makes structural.
- **Ch 3b**: the bloated CLAUDE.md that rots.
- **Ch 3c**: the context-compression skill and `ctx_*` MCP tools, plus cheaper models for simple subagents.
- **Ch 3e**: agent memory as the fifth primitive beyond these four.
- **Ch 4**: `@AILocked` and per-tool instruction filenames (4.2).
- **Ch 5 / 5b**: architectural tests and the 30-second inner loop that `Stop` hooks run.
- **Ch 7**: the repo as constitution. **Ch 8, 9, 10**: Spec Kit, Kiro (agent hooks), and Zenflow (SKILL.md contract) as conventions for filling the surface.
- **Ch 11**: the evergreen tool checklist and the main window at 30–40%. **Ch 12**: Superpowers for packaging a portable personal setup.
- **Ch 16**: Skill Forge. **Ch 19**: sandboxing and untrusted input. **Ch 21**: hooks promoted to branch-level law in CI. **Ch 22**: the Two-AI Gripe and Inquisitor as subagents.
- **External**: defense in depth; least privilege; command-injection hygiene.
