# Chapter 13: Forks and Example Subagents

## Core Idea
A fork is a subagent that inherits the whole conversation (same system prompt, tools, model, history and prompt cache) so you can hand off a side task without re-explaining, while its tool calls still stay out of your context. For everything else, a well-designed custom subagent is focused, narrowly tooled, and described precisely enough to route correctly.

## Frameworks Introduced
- **Fork vs fresh subagent choice**: fork when any other subagent would need too much background to be useful, or to try several approaches in parallel from the same starting point; use a defined subagent when you want a different prompt, restricted tools, a different model, or isolation from the conversation's context.
  - How: start a fork yourself with `/subtask <task>` (v2.1.212+; `/fork` on v2.1.161–v2.1.211, or when agent view is off), or let Claude request the `fork` subagent type through the Agent tool when fork mode is on.
  - Why it works: identical system prompt + tool definitions mean the fork's first request reuses the parent's prompt cache, so it's cheaper than a fresh subagent for same-context tasks.
  - Failure mode: forks don't give *input* isolation; they carry the full history into every request, and a fork can't spawn further forks.
- **Fork mode switch**: on by default in interactive sessions (v2.1.232+), off in `-p` and the Agent SDK. `CLAUDE_CODE_FORK_SUBAGENT=1` turns it on everywhere; `0` turns it off everywhere. To keep fork mode but forbid forks, deny `Agent(fork)`.
  - Tells that it's on: Claude can request type `fork`; an Agent call without a type gets `general-purpose`; all spawned subagents run in background and the Agent tool's `run_in_background` parameter is removed.
- **Subagent design checklist** (best practices): one focused job per subagent; descriptions specific enough to single out one subagent (within the 15,000-token combined budget); minimum tools; project subagents checked into version control.

## Key Concepts
- **Fork**: subagent that inherits the conversation at spawn time instead of starting from a definition; only its final result returns.
- **`/subtask`**: user command that forks the conversation with a task; Claude Code names the fork from the task's first words; works whether or not fork mode is on.
- **`/fork` (agent view on)**: copies the whole session into a new background session instead of a subagent.
- **Fork panel**: rows for main and each fork below the prompt; successful forks disappear, failed/stopped ones remain 30s.
- **Viewed-transcript routing**: with a fork's or subagent's transcript open, follow-ups and skills go to that agent; built-in commands go to main. `/compact`, `/clear`, `/rewind` ask for confirmation; `/model` and `/fast` refuse to run from that view.
- **Interrupting send**: `Ctrl+Enter` or `Ctrl+X Ctrl+S` makes the viewed agent read your message before waiting work finishes, moving backgroundable commands/subagents to the background (v2.1.286+).
- **Fork with worktree**: Claude can pass `isolation: "worktree"` when spawning a fork so its edits land in a separate git worktree.
- **Forks and filters**: forks skip both tool filters, keep output style, ignore `CLAUDE_CODE_SUBAGENT_MODEL_FORCE`, and skip `--append-subagent-system-prompt`.
- **Hook as backstop**: in the db-reader example the system prompt tells the agent to refuse writes; the `PreToolUse` hook enforces it if the model tries anyway.

## Mental Models
- Think of a fork as "me, branched": same brain, same memory of the conversation, different scratchpad. Think of a defined subagent as "a specialist I brief".
- Use `/subtask` for side work you'd otherwise interrupt yourself to do ("draft unit tests for the parser changes so far") while you keep implementing.
- Think of the example subagents as a tool-access gradient: reviewer (read + Bash, no Edit/Write) → debugger (adds Edit) → data scientist (adds Write, domain prompt, explicit `model: sonnet`) → db-reader (Bash only, guarded by a hook).
- Use `model: inherit` when the subagent's quality should track whatever the main session runs.

## Anti-patterns
- **Using a fork for a task that needs a restricted toolset or different model**: forks always have the main session's tools and model; define a subagent instead.
- **Running `/model` from an open fork transcript to change the fork's model**: it targets main and is blocked there.
- **Trusting the system prompt alone for safety**: "You cannot modify data" is advisory; enforce with `tools` and a `PreToolUse` hook.
- **Generalist subagents with vague descriptions**: they compete with each other for routing and waste description budget.

## Code Examples
```text
/subtask draft unit tests for the parser changes so far
```
- **What it demonstrates**: user-started fork; runs in the background panel; result arrives as a message in main.

```markdown
---
name: code-reviewer
description: Expert code review specialist. Proactively reviews code for quality, security, and maintainability. Use immediately after writing or modifying code.
tools: Read, Grep, Glob, Bash
model: inherit
---

You are a senior code reviewer ensuring high standards of code quality and security.

When invoked:
1. Run git diff to see recent changes
2. Focus on modified files
3. Begin review immediately

Review checklist:
- Code is clear and readable
- Functions and variables are well-named
- No duplicated code
- Proper error handling
- No exposed secrets or API keys
- Input validation implemented
- Good test coverage
- Performance considerations addressed

Provide feedback organized by priority:
- Critical issues (must fix)
- Warnings (should fix)
- Suggestions (consider improving)

Include specific examples of how to fix issues.
```
- **What it demonstrates**: read-only reviewer (no Edit/Write), proactive description, explicit start procedure, checklist, and prioritized output format.

```markdown
---
name: debugger
description: Debugging specialist for errors, test failures, and unexpected behavior. Use proactively when encountering any issues.
tools: Read, Edit, Bash, Grep, Glob
---

You are an expert debugger specializing in root cause analysis.

When invoked:
1. Capture error message and stack trace
2. Identify reproduction steps
3. Isolate the failure location
4. Implement minimal fix
5. Verify solution works
```
- **What it demonstrates**: adds `Edit` because fixing requires changes; workflow from diagnosis to verification (full prompt also asks for root cause, evidence, fix, testing approach, prevention).

```markdown
---
name: data-scientist
description: Data analysis expert for SQL queries, BigQuery operations, and data insights. Use proactively for data analysis tasks and queries.
tools: Bash, Read, Write
model: sonnet
---
```
- **What it demonstrates**: a domain subagent outside coding (uses `bq` CLI), pinned to `sonnet`.

## Reference Tables

**Fork vs non-fork subagent**

| | Fork | Non-fork subagent |
|---|---|---|
| Context | Full conversation history | Fresh context with the prompt you pass |
| System prompt and tools | Same as main session | From the definition file, filtered for background runs |
| Model | Same as main session | From the subagent's `model` field |
| Permissions | Prompts surface in your terminal | Prompts surface in main session when in background |
| Prompt cache | Shared with main session | Separate cache |

**Fork panel keys**

| Key | Action |
|---|---|
| `↑` / `↓` | Move between rows |
| `Enter` | Open selected fork's transcript and send follow-ups |
| `x` | Stop running fork / dismiss finished row (types into prompt on main row or the opened fork's row) |
| `Esc` | Return focus to prompt input |

**Fork mode by session type**

| Session | Default | Override |
|---|---|---|
| Interactive | On (v2.1.232+) | `CLAUDE_CODE_FORK_SUBAGENT=0` |
| `-p` / Agent SDK | Off | `CLAUDE_CODE_FORK_SUBAGENT=1` |
| Keep mode, block forks | — | `permissions.deny: ["Agent(fork)"]` |

## Worked Example
Build the read-only database analyst end to end.

`.claude/agents/db-reader.md`:
```markdown
---
name: db-reader
description: Execute read-only database queries. Use when analyzing data or generating reports.
tools: Bash
hooks:
  PreToolUse:
    - matcher: "Bash"
      hooks:
        - type: command
          command: "./scripts/validate-readonly-query.sh"
---

You are a database analyst with read-only access. Execute SELECT queries to answer questions about the data.

You cannot modify data. If asked to INSERT, UPDATE, DELETE, or modify schema, explain that you only have read access.
```
`./scripts/validate-readonly-query.sh`:
```bash
#!/bin/bash
INPUT=$(cat)
COMMAND=$(echo "$INPUT" | jq -r '.tool_input.command // empty')
if [ -z "$COMMAND" ]; then
  exit 0
fi
if echo "$COMMAND" | grep -iE '\b(INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|TRUNCATE|REPLACE|MERGE)\b' > /dev/null; then
  echo "Blocked: Write operations not allowed. Use SELECT queries only." >&2
  exit 2
fi
exit 0
```
Decisions: `tools: Bash` is the minimum that can reach the DB, but Bash can't be narrowed by `tools`, so the hook adds the conditional check. The prompt is the first line of defence (agent refuses writes); the hook is the backstop (exit 2 blocks the command and feeds stderr to the agent). Empty commands pass through. `chmod +x` the script, keep the path matching `command`, and trust the project folder so frontmatter hooks run. The description says when to delegate ("analyzing data or generating reports") so routing is unambiguous next to `data-scientist`.

## Key Takeaways
1. A fork inherits history, system prompt, tools, model and prompt cache; only its final result returns.
2. Start forks with `/subtask` (v2.1.212+); fork mode is on by default interactively, off in `-p`/SDK, controlled by `CLAUDE_CODE_FORK_SUBAGENT`.
3. Forks can't spawn forks; deny `Agent(fork)` to block forks while keeping fork mode.
4. Design subagents for one job, with minimal tools and descriptions that route uniquely.
5. Pair prompt-level rules with hook enforcement for safety-critical restrictions.

## Connects To
- **ch10**: frontmatter fields and scopes used by the example files.
- **ch11**: tool filters and model forcing that forks bypass; hooks in frontmatter.
- **ch12**: background execution, panel housekeeping, and resume that apply to forks too.
- **ch08**: `context: fork` skills, a related way to run work in a subagent.
- **ch15**: exit code 2 and hook input JSON used by the db-reader validator.
