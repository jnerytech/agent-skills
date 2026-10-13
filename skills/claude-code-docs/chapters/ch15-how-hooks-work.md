# Chapter 15: How Hooks Work — Lifecycle, I/O, Exit Codes, Matchers, and Locations

## Core Idea
When an event fires, Claude Code runs **every** matching hook in parallel, waits for all of them, then merges the results. The most restrictive permission decision wins. Each hook gets event JSON on stdin and replies through its exit code, stderr, or a JSON object on stdout. Matchers and the `if` field decide which hooks spawn, and the settings location decides who they apply to.

## Frameworks Introduced
- **Decision precedence across parallel hooks**: for `PreToolUse` permission decisions the most restrictive answer applies, in the order **`deny` > `defer` > `ask` > `allow`**. `additionalContext` from every hook is kept and passed to Claude together.
  - When to use: whenever two or more hooks match the same event, for example a logger plus a guardrail.
  - How: every sibling runs to completion even if one denies. Merge happens afterwards.
  - Why it works / failure mode: deny can't be outvoted, so a guardrail is safe to add next to permissive hooks. The flip side is that one hook's `deny` does **not** stop a sibling's side effects. The logger still logs, so never rely on a deny to suppress work in another hook. When multiple hooks return `updatedInput`, the last to finish wins, which is non-deterministic. Let only one hook rewrite a given tool's input.
- **Exit code vs. JSON: pick one per hook**: use `exit 2` + stderr to block with a message, or `exit 0` + JSON stdout for structured control. Mixing them leads to the per-event rules in the reference's "Exit code output".
  - Why it works: exit codes give only two signals, block or stay silent. JSON can allow, deny with a reason, escalate to `ask`, inject context, or set a title.
- **Two-level filtering: `matcher` then `if`**: `matcher` filters the matcher group by the event's key field (the tool name for tool events). `if` filters an individual handler by tool name **and** arguments using permission-rule syntax, so the process only spawns on a real match.
  - Failure mode: `if` is best-effort. When Claude Code can't parse which commands a Bash input runs, the hook runs anyway. Enforce hard allow/deny with the permission system, not with `if`.
- **Scope by location**: user (`~/.claude/settings.json`) → project (`.claude/settings.json`, committed) → local (`.claude/settings.local.json`) → managed policy → plugin `hooks/hooks.json` → skill/subagent frontmatter (see the table).

## Key Concepts
- **Common input fields**: `session_id`, `cwd`, `hook_event_name`. Tool events add `tool_name` and `tool_input` (for Bash, `tool_input.command`).
- **Event-specific input**: `UserPromptSubmit` gets `prompt`. `SessionStart` gets `source` ∈ `startup`, `resume`, `clear`, `compact`, `fork`.
- **`hookSpecificOutput`**: the wrapper for event-specific JSON output (`hookEventName`, `permissionDecision`, `permissionDecisionReason`, `additionalContext`, …). Fields placed at the top level instead are **silently ignored**.
- **`permissionDecision`** (`PreToolUse`): `allow` skips the prompt, but deny/ask rules and managed deny lists still apply, as do network-path reads, MCP tools marked `requiresUserInteraction`, and connector tools an org set to `ask`. `deny` cancels the call and sends the reason to Claude. `ask` shows the normal prompt. `defer` works only in `-p` mode: it exits with the tool call preserved so an Agent SDK wrapper can resume.
- **`PreModelSwitch` `permissionDecision`**: `allow`/`deny`. `ask` prompts only for interactive `/model`, and everywhere else counts as a refusal.
- **Other decision shapes**: `PostToolUse` and `Stop` use top-level `decision: "block"`. `PermissionRequest` uses `hookSpecificOutput.decision.behavior`.
- **Hook types**: `command` (default), `http`, `mcp_tool`, `prompt`, `agent` (experimental). See ch16.
- **`disableAllHooks`**: `true` turns off hooks after settings precedence, so a project file can override yours. Managed-settings hooks still run unless managed settings also set it.

## Mental Models
- **Think of parallel hooks as a jury where any single "deny" convicts**, though every juror still finishes their own work.
- **Exit 0 means "no objection", not "approve".** On `PreToolUse` the normal permission flow still runs. Approving takes JSON `"allow"`.
- **Use `matcher` to pick the tool and `if` to pick the arguments.** `matcher: "Bash"` + `if: "Bash(git *)"` spawns only for git commands.
- **Matching `Edit|Write` does not mean "every file change".** Claude can write files through shell commands. For full coverage, add a `Stop` hook that scans the tree once per turn, or also match `Bash|PowerShell` and diff with `git status --porcelain`. Use `FileChanged` to react to a specific file whatever wrote it.

## Anti-patterns
- **Relying on one hook's `deny` to prevent another hook's side effect**: the siblings have already run.
- **Several hooks returning `updatedInput` for the same tool**: the last to finish wins, and parallel order is random.
- **Top-level `additionalContext` or `permissionDecision`**: parses fine and is silently dropped. Nest it in `hookSpecificOutput`.
- **Putting `if` on a non-tool event**: the hook never runs. `if` works only on `PreToolUse`, `PostToolUse`, `PostToolUseFailure`, `PermissionRequest` and `PermissionDenied`.
- **Treating `if` as a security boundary**: it is best-effort and fails open.
- **Exit 2 on unblockable events** like `SessionStart`: stderr is shown to the user and execution continues.

## Code Examples
```bash
#!/bin/bash
INPUT=$(cat)
COMMAND=$(echo "$INPUT" | jq -r '.tool_input.command')
if echo "$COMMAND" | grep -q "drop table"; then
  echo "Blocked: dropping tables is not allowed" >&2  # stderr becomes Claude's feedback
  exit 2                                               # exit 2 = block the action
fi
exit 0  # no decision; normal permission flow applies
```
- **What it demonstrates**: the exit-code protocol. Read stdin, block with 2 + stderr, otherwise 0.

```json
{ "hookSpecificOutput": { "hookEventName": "PreToolUse",
    "permissionDecision": "deny",
    "permissionDecisionReason": "Use rg instead of grep for better performance" } }
```
```json
{ "hookSpecificOutput": { "hookEventName": "UserPromptSubmit",
    "additionalContext": "Current branch: release-42. Deploy freeze until Friday." } }
```
- **What it demonstrates**: a structured deny with a reason Claude reads, and context injection on every prompt.

```json
{ "hooks": { "PreToolUse": [ { "matcher": "Bash", "hooks": [
  { "type": "command", "if": "Bash(git *)",
    "command": "\"$CLAUDE_PROJECT_DIR\"/.claude/hooks/check-git-policy.sh" } ] } ] } }
```
- **What it demonstrates**: argument-level filtering, so the script spawns only for git commands.

## Reference Tables
**Exit-code semantics**

| Exit | Meaning | Detail |
|---|---|---|
| `0` | No objection | `PreToolUse`: not an approval, the normal permission flow applies. For `UserPromptSubmit`, `UserPromptExpansion`, `SessionStart`, `PostModelSwitch`, plain-text stdout is added to Claude's context. JSON stdout is parsed for decisions. |
| `2` | Block the action | Write the reason to stderr. Depending on the event it reaches Claude (so it can adjust) or the user. `ConfigChange` and `Elicitation` show no message. Unblockable events (e.g. `SessionStart`) show stderr to the user and continue. |
| other | Depends on stdout | Valid, schema-passing JSON: exit code ignored, JSON decides, no error (exception: `WorktreeCreate` fails on any nonzero exit). JSON that fails the schema, or invalid JSON: non-blocking error carrying the validation/parse message. Plain text or empty: action proceeds, transcript shows `<hook name> hook error` + first stderr line after `Failed with non-blocking status code:` (full stderr via `claude --debug` or `/debug`). |

**Matcher field per event**

| Event | Matcher filters | Example values |
|---|---|---|
| `PreToolUse`, `PostToolUse`, `PostToolUseFailure`, `PermissionRequest`, `PermissionDenied` | tool name | `Bash`, `Edit\|Write`, `mcp__.*` |
| `SessionStart` | how session started | `startup`, `resume`, `clear`, `compact`, `fork` |
| `Setup` | CLI flag | `init`, `maintenance` |
| `SessionEnd` | why it ended | `clear`, `resume`, `logout`, `prompt_input_exit`, `other` |
| `Notification` | notification type | `permission_prompt`, `idle_prompt`, `auth_success`, `elicitation_*`, `agent_needs_input`, `agent_completed`, `quota_auto_resume_*` (ch14) |
| `SubagentStart`, `SubagentStop` | agent type | `general-purpose`, `Explore`, `Plan`, custom names |
| `PreCompact`, `PostCompact` | trigger | `manual`, `auto` |
| `PreModelSwitch`, `PostModelSwitch` | canonical target model | `claude-opus-5`, `.*opus.*` |
| `ConfigChange` | config source | `user_settings`, `project_settings`, `local_settings`, `policy_settings`, `skills` |
| `DirectoryAdded` | how added | `slash_command`, `register_repo_root` |
| `StopFailure` | error type | `rate_limit`, `overloaded`, `authentication_failed`, `billing_error`, `invalid_request`, `model_not_found`, `server_error`, `max_output_tokens`, `cloud_credential_error`, `unknown`, … |
| `InstructionsLoaded` | load reason | `session_start`, `nested_traversal`, `path_glob_match`, `include`, `compact` |
| `Elicitation`, `ElicitationResult` | MCP server name | your server names |
| `FileChanged` | literal filenames (split on `\|`, not regex) | `.envrc\|.env` |
| `UserPromptExpansion` | command name | your skill/command names |
| `UserPromptSubmit`, `PostToolBatch`, `Stop`, `TeammateIdle`, `TaskCreated`, `TaskCompleted`, `WorktreeCreate`, `WorktreeRemove`, `CwdChanged`, `MessageDisplay` | **no matcher** | always fire |

Matcher syntax: `|` or `,` separate alternatives (`"Edit, Write"` = `"Edit|Write"`). Regex is allowed. Matching is case-sensitive. MCP tools are named `mcp__<server>__<tool>` (plugin servers: `mcp__plugin_<plugin>_<server>__<tool>`). Target one server with `mcp__github__.*` or cross-server with `mcp__.*__write.*`.

**`if` pattern behavior (Bash)**

| `if` | Command | Runs? | Why |
|---|---|---|---|
| `Bash(git *)` | `git push` | yes | name matches |
| `Bash(git *)` | `npm test && git push` | yes | each subcommand checked |
| `Bash(git *)` | `echo $(git log)` | yes | `$()`/backticks checked |
| `Bash(git *)` | `echo $(date)` | no | nothing matches |
| `Bash(git push *)` | `echo $(date)` | yes | patterns more specific than the name run anyway on `$()`, backticks, `$VAR` |

`if` takes one permission-rule pattern (`"Bash(git *)"`, `"Edit(*.ts)"`). For several tools, use separate handlers or pipe alternation in `matcher`.

**Lifecycle events (abridged)**: `SessionStart`, `Setup` (`--init-only`, or `--init`/`--maintenance` in `-p`), `UserPromptSubmit`, `UserPromptExpansion` (can block), `PreToolUse` (can block), `PermissionRequest`, `PermissionDenied` (auto mode; `hookSpecificOutput.retry: true` lets the model retry, ignored without a classifier verdict), `PostToolUse`, `PostToolUseFailure`, `PostToolBatch` (after parallel batch, before next model call), `Notification`, `MessageDisplay`, `SubagentStart`/`SubagentStop`, `TaskCreated`/`TaskCompleted`, `Stop`, `StopFailure` (API error), `TeammateIdle`, `InstructionsLoaded` (CLAUDE.md / `.claude/rules/*.md` loaded, including lazy loads), `ConfigChange`, `CwdChanged`, `DirectoryAdded` (`/add-dir`), `FileChanged`, `WorktreeCreate` (replaces default git behavior), `WorktreeRemove`, `PreCompact`/`PostCompact`, `PreModelSwitch` (can block), `PostModelSwitch`, `Elicitation`/`ElicitationResult`, `SessionEnd`.

**Hook locations**

| Location | Scope | Shareable |
|---|---|---|
| `~/.claude/settings.json` | All your projects | No |
| `.claude/settings.json` | Single project | Yes, commit it |
| `.claude/settings.local.json` | Single project | No (gitignored when Claude Code saves to it) |
| Managed policy settings | Organization | Yes, admin-controlled |
| Plugin `hooks/hooks.json` | While plugin enabled | Yes |
| Skill frontmatter | Rest of session after the skill is invoked | Yes |
| Subagent frontmatter | While that subagent runs | Yes |

Edits to settings files are normally picked up by the file watcher. Browse everything with `/hooks`.

## Worked Example
Two `PreToolUse` hooks on `Bash`: a logger (`jq -r .tool_input.command >> ~/.claude/bash.log`, exits 0) and a guardrail (`"$CLAUDE_PROJECT_DIR"/.claude/hooks/block-rm-rf.sh`, exits 2 on `rm -rf`).

```json
{ "hooks": { "PreToolUse": [ { "matcher": "Bash", "hooks": [
  { "type": "command", "command": "jq -r .tool_input.command >> ~/.claude/bash.log" },
  { "type": "command", "command": "\"$CLAUDE_PROJECT_DIR\"/.claude/hooks/block-rm-rf.sh" } ] } ] } }
```
Claude runs `rm -rf /tmp/build`:
1. Both hooks match `Bash` and start in parallel.
2. The logger appends the command and exits 0, which reports no decision.
3. The guardrail exits 2, which counts as a deny, with its reason on stderr.
4. Merge: deny beats everything else, so the command is blocked and Claude sees the guardrail's stderr.
5. The log line exists anyway, because the logger had already finished. If logging blocked commands is unwanted, move the logger to `PostToolUse`, which fires only after successful execution.

## Key Takeaways
1. All matching hooks run in parallel and to completion. Merging happens afterwards.
2. Precedence: `deny` > `defer` > `ask` > `allow`. All `additionalContext` is concatenated.
3. Exit 0 means no objection, exit 2 means block (reason on stderr). Other codes defer to stdout: valid JSON wins, otherwise a non-blocking error.
4. Use one mechanism per hook: exit 2 + stderr, or exit 0 + JSON in `hookSpecificOutput`.
5. The matcher's meaning depends on the event, and ten events take no matcher at all.
6. `if` narrows by arguments only on the five tool events, and it fails open.
7. Location sets scope. A project's `disableAllHooks` can override yours, but not managed hooks.

## Connects To
- **ch14**: the recipes that apply these rules.
- **ch16**: prompt/agent/HTTP handler semantics, timeouts, permission-mode interaction, debugging bad JSON.
- **ch11**: hooks in subagent frontmatter (`SubagentStart`/`SubagentStop` matchers use agent types).
- **ch02**: `InstructionsLoaded` fires on CLAUDE.md and `.claude/rules/` loads.
