# Chapter 11: Subagent Models, Capabilities, and Hooks

## Core Idea
A subagent's power comes from what you let it have: which model and effort it runs at, which tools survive the filters, which permission mode applies, which MCP servers, skills and memory it gets, and which hooks police it. Configure these to make a subagent cheap, safe, and focused.

## Frameworks Introduced
- **Subagent model resolution order**: (1) per-invocation `model` parameter Claude passes → (2) frontmatter `model` (`inherit` = main model) → (3) `CLAUDE_CODE_SUBAGENT_MODEL` → (4) main conversation's model. A mod's `agent.spawn` hook model replaces step 1.
  - When to use: predicting or debugging which model a subagent runs on.
  - How: check `/tasks` while it runs (v2.1.242+); the row names the model and any per-subagent effort.
  - Failure mode: assuming `CLAUDE_CODE_SUBAGENT_MODEL` overrides definitions; since v2.1.251 it's only a default. To force it, also set `CLAUDE_CODE_SUBAGENT_MODEL_FORCE=1` (v2.1.257+).
- **Two-filter tool pool**: subagents inherit built-in + MCP tools, then (a) a global filter removes `Agent` (at depth limit), `AskUserQuestion`, `EndConversation`, `EnterPlanMode`, `ExitPlanMode` (unless `permissionMode: plan`), `ScheduleWakeup`, `WaitForMcpServers`, `Workflow`; then (b) background subagents keep all MCP tools but only `Read`, `Grep`, `Glob`, `LSP`, `Bash`, `PowerShell`, `Edit`, `Write`, `NotebookEdit`, `WebFetch`, `WebSearch`, `TodoWrite`, `Skill`, `ToolSearch`, `EnterWorktree`, `ExitWorktree`, `Monitor`, `TaskStop`, `SendMessage`, `Artifact` (+ `SubagentHandback`). Forks skip both filters.
  - When to use: when a subagent "can't" use a tool you listed.
  - Why it matters: the same definition resolves to different tools in foreground vs background, silently (error only if `tools` resolves to nothing).
- **Permission-mode override rule**: if the parent is in `bypassPermissions`, `acceptEdits`, or `auto`, the subagent runs in the parent's mode and your `permissionMode` is ignored. If the parent is in `default`, `dontAsk`, or `plan`, your `permissionMode` applies, except `bypassPermissions` (v2.1.267+) or an unavailable `auto` fall back to the parent's mode.
  - Takeaway: a subagent can never escalate to bypass on its own; `permissionMode` mostly lets you *tighten* or set `plan`/`acceptEdits`/`dontAsk` under a cautious parent.
- **Allowlist vs denylist vs hook**: `tools` (allowlist) → `disallowedTools` (denylist) → `PreToolUse` hook (conditional, per-call) → `permissions.deny` Bash rule (command-level, session-wide).

## Key Concepts
- **Alias pinning to main model**: a family alias (`opus`) in frontmatter or per-invocation resolves to the main conversation's *exact* model (including `[1m]` extended context) when the main model is in that family. An alias in `CLAUDE_CODE_SUBAGENT_MODEL` always resolves to the alias target.
- **`availableModels` substitution**: a blocked family alias runs on the newest allowed version of that family; other blocked values fall back to the inherited model; interactive sessions warn.
- **Thinking inheritance**: since v2.1.198 subagents inherit the main conversation's extended-thinking on/off; there is no per-subagent thinking setting.
- **Effort precedence**: `CLAUDE_CODE_EFFORT_LEVEL` > per-invocation `effort` parameter (non-fork, v2.1.292+, persists on resume) > frontmatter `effort` > session effort.
- **`tools` + `disallowedTools` together**: `disallowedTools` applied first, then `tools` resolved against what remains; a tool in both is removed.
- **MCP patterns**: `mcp__<server>` or `mcp__<server>__*` grant/remove a whole server; `mcp__*` in `disallowedTools` removes all MCP tools.
- **`Agent(worker, researcher)`**: spawn allowlist, honored only for an agent running as main thread via `claude --agent`; in a subagent definition the parenthesized list is ignored (plain `Agent` just enables nesting). `Task(...)` still works as an alias (renamed in 2.1.63).
- **Inline MCP trust**: inline servers in a project or `--add-dir` agent file load only after you trust that exact folder (v2.1.238+); parent-folder trust and `-p` auto-trust don't count. Name references, `~/.claude/agents/`, `--agents`, SDK and managed definitions skip this check.
- **Agent memory**: `memory: user|project|local` gives a persistent dir; the first 200 lines or 25KB of its `MEMORY.md` is injected, and Read/Write/Edit are auto-enabled. Disabled entirely if auto memory is off (`autoMemoryEnabled`, `CLAUDE_CODE_DISABLE_AUTO_MEMORY`).
- **Frontmatter `Stop` → `SubagentStop`**: a `Stop` hook in a subagent's frontmatter is converted at runtime.

## Mental Models
- Think of `CLAUDE_CODE_SUBAGENT_MODEL` as a default and `CLAUDE_CODE_SUBAGENT_MODEL_FORCE=1` as a mandate: with both, every subagent, teammate and workflow agent runs on that model; frontmatter `model` and Claude's per-call model are ignored. Forks and `context: fork` skills with `model: inherit` still use the main model.
- Use `mcpServers` inline when you want a server's tools *only* in the subagent, so its tool descriptions never cost main-conversation context.
- Think of `skills` as "preload", not "permit": without it the subagent can still invoke skills via the Skill tool; to block skills, remove `Skill` from `tools` or add it to `disallowedTools`.
- Use `project` as the default memory scope: knowledge is shareable via version control.

## Anti-patterns
- **`disallowedTools: Bash(git push *)` to block one command**: removes the whole Bash tool. Put `Bash(git push *)` in `permissions.deny` instead (applies to main and subagents).
- **Setting `permissionMode: bypassPermissions` on a subagent** expecting it to skip prompts: it only runs in bypass when the main conversation does.
- **Preloading a skill with `disable-model-invocation: true`** (including bundled `/verify`): not allowed; missing/disabled skills are skipped with a debug-log warning.
- **Hook script not executable**: on macOS/Linux the hook fails instead of blocking; `chmod +x`.
- **Untrusted project folder**: frontmatter hooks from a project agent are skipped (subagent still runs) until you accept the workspace trust dialog for that folder; a `-p` session doesn't count as trusted (v2.1.218+).

## Code Examples
```json
{
  "env": {
    "CLAUDE_CODE_SUBAGENT_MODEL": "haiku",
    "CLAUDE_CODE_SUBAGENT_MODEL_FORCE": "1"
  }
}
```
- **What it demonstrates**: forcing one model on every subagent; with only `_FORCE` set, subagents run on the main model (Explore keeps its listed model).

```yaml
---
name: browser-tester
description: Tests features in a real browser using Playwright
mcpServers:
  # Inline definition: scoped to this subagent only
  - playwright:
      type: stdio
      command: npx
      args: ["-y", "@playwright/mcp@latest"]
  # Reference by name: reuses an already-configured server
  - github
---
```
- **What it demonstrates**: inline servers (same schema as `.mcp.json`; `stdio`, `http`, `sse`, `ws`) connect at subagent start and disconnect at finish; string references share the parent's connection. `--strict-mcp-config`, `--bare`, managed MCP and `allowedMcpServers`/`deniedMcpServers` still apply (but `--strict-mcp-config` doesn't filter `--agents`/SDK inline servers).

```yaml
---
name: coordinator
description: Coordinates work across specialized agents
tools: Agent(worker, researcher), Read, Bash
---
```
- **What it demonstrates**: spawn allowlist for a `claude --agent coordinator` main thread; omit `Agent` entirely to forbid spawning.

```json
{
  "hooks": {
    "SubagentStart": [
      { "matcher": "db-agent",
        "hooks": [ { "type": "command", "command": "./scripts/setup-db-connection.sh" } ] }
    ],
    "SubagentStop": [
      { "hooks": [ { "type": "command", "command": "./scripts/cleanup-db-connection.sh" } ] }
    ]
  }
}
```
- **What it demonstrates**: session-level lifecycle hooks in `settings.json`; matcher is the agent `name`, or plugin-scoped ID. Scoped IDs contain `:` and are treated as unanchored regex, so write `^my-plugin:db-agent$`.

## Reference Tables

**Permission modes (`permissionMode`)**

| Mode | Behavior |
|---|---|
| `default` (`manual`) | Prompts for permission |
| `acceptEdits` | Auto-accepts edits and common filesystem commands in working dir / `additionalDirectories` |
| `auto` | Background classifier reviews commands and protected-directory writes |
| `dontAsk` | Auto-denies prompts; explicitly allowed tools work; `AskUserQuestion`, `requiresUserInteraction` MCP tools, network-path reads, org-`ask` connector tools denied even if allowed |
| `bypassPermissions` | Skip prompts — only when main conversation is also in bypass |
| `plan` | Read-only exploration (keeps `ExitPlanMode`) |

**Memory scopes**

| Scope | Location | Use when |
|---|---|---|
| `user` | `~/.claude/agent-memory/<name-of-agent>/` | Learnings apply across all projects |
| `project` | `.claude/agent-memory/<name-of-agent>/` | Project-specific, shared via VCS (recommended default) |
| `local` | `.claude/agent-memory-local/<name-of-agent>/` | Project-specific, not checked in |

**Hooks for subagents**

| Where | Event | Matcher | Fires |
|---|---|---|---|
| Frontmatter | `PreToolUse` | Tool name | Before the subagent uses a tool |
| Frontmatter | `PostToolUse` | Tool name | After the subagent uses a tool |
| Frontmatter | `Stop` | — | When subagent finishes (becomes `SubagentStop`) |
| `settings.json` | `SubagentStart` | Agent type name | Subagent begins |
| `settings.json` | `SubagentStop` | Agent type name | Subagent completes |

Settings, managed-policy and plugin hooks all fire inside subagents too (a `settings.json` `PreToolUse` runs before every subagent tool call). Frontmatter hooks also fire when the agent runs as main session via `--agent`.

## Worked Example
Need: an analyst that may run `psql` but never write. `tools` can't express "Bash but only SELECT", so combine a narrow allowlist with a `PreToolUse` hook:

```yaml
---
name: db-reader
description: Execute read-only database queries
tools: Bash
hooks:
  PreToolUse:
    - matcher: "Bash"
      hooks:
        - type: command
          command: "./scripts/validate-readonly-query.sh"
---
```
```bash
#!/bin/bash
INPUT=$(cat)
COMMAND=$(echo "$INPUT" | jq -r '.tool_input.command // empty')
if echo "$COMMAND" | grep -iE '\b(INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|TRUNCATE)\b' > /dev/null; then
  echo "Blocked: Only SELECT queries are allowed" >&2
  exit 2
fi
exit 0
```
Walk-through: (1) `tools: Bash` strips Edit/Write/MCP. (2) Hook input arrives as JSON on stdin; `tool_input.command` holds the Bash text. (3) Exit code 2 blocks and feeds stderr back to the subagent. (4) `chmod +x` the script, and trust the project folder or the hook is skipped. (5) Test by asking for an `UPDATE`; the subagent sees `Blocked: Only SELECT queries are allowed`. On Windows, write it in PowerShell with `shell: powershell`.

## Key Takeaways
1. Model order: per-call param → frontmatter → `CLAUDE_CODE_SUBAGENT_MODEL` → main; add `CLAUDE_CODE_SUBAGENT_MODEL_FORCE=1` to override everything.
2. Background subagents get a reduced built-in tool set; forks get the parent's exact pool.
3. `disallowedTools` removes whole tools; use `permissions.deny` or a `PreToolUse` hook for command-level control.
4. Parent in `bypassPermissions`/`acceptEdits`/`auto` overrides the subagent's `permissionMode`.
5. Inline `mcpServers` keep tool descriptions out of the main context; project-folder trust is required for them and for frontmatter hooks.
6. `memory` injects up to 200 lines / 25KB of `MEMORY.md`; `skills` injects full skill content (max 32).

## Connects To
- **ch10**: full frontmatter field table and scopes these fields live in.
- **ch12**: foreground vs background decides which tool filter applies; resume keeps per-call model/effort.
- **ch13**: forks bypass tool filters and model settings; the db-reader example.
- **ch04**: auto memory, which subagent `memory` depends on.
- **ch07 / ch08**: skill invocation and `context: fork`, inverse of `skills` preloading.
- **ch15**: hook I/O, exit code 2, matchers.
