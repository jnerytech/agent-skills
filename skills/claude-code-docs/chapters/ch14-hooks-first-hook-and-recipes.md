# Chapter 14: Hooks — Your First Hook and Ready-Made Recipes

## Core Idea
Hooks are user-defined shell commands (or HTTP, MCP-tool, prompt, or agent handlers) that Claude Code runs at fixed lifecycle points. They give you deterministic control: the action always happens instead of depending on the model choosing to do it. Use them to enforce project rules, automate repetitive chores, and wire Claude Code into your tools.

## Frameworks Introduced
- **Deterministic vs. judgment automation**: put "must always happen" rules in hooks; put "needs judgment" checks in `type: "prompt"` / `type: "agent"` hooks (ch16); put guidance in CLAUDE.md (ch01) or skills (ch05).
  - When to use: whenever you catch yourself writing "always run X" or "never touch Y" in CLAUDE.md. Hooks enforce it, while CLAUDE.md only asks.
  - How: choose the lifecycle event, narrow it with a `matcher`, then write a command that reads JSON on stdin and signals via exit code or JSON stdout.
  - Why it works / failure mode: a hook runs whether or not the model remembers. The usual failure is a matcher that is too broad, such as an empty matcher on `PermissionRequest` auto-approving everything.
- **The hook config shape**: `hooks` → `<EventName>` → array of matcher groups `{ "matcher": ..., "hooks": [ { "type": ..., "command": ... } ] }`.
  - How: every event is a key inside the single `hooks` object. When adding a new event, add it as a sibling key and leave the existing object in place.
- **Three-step setup loop**: (1) add the block to a settings file, (2) verify with `/hooks`, (3) trigger the event and check the effect.
  - Why it works: a hook that succeeds shows nothing in the conversation, so verification has to be explicit. Check the effect, or open the transcript with `Ctrl+O` (ch16).
- **Exit-code block vs. JSON decision**: simple guards `exit 2` with a reason on stderr. Richer control (allow, set mode, inject context) needs JSON on stdout with exit 0 (full semantics in ch15).

## Key Concepts
- **Hook event**: a named lifecycle point such as `PreToolUse`, `PostToolUse`, `Notification`, `SessionStart`, `ConfigChange`, `CwdChanged`, `FileChanged`, `PermissionRequest`.
- **Matcher**: a string that filters when a matcher group fires. Its meaning depends on the event (tool name, notification type, session source, filename…). `""` or omitted matches everything.
- **`$CLAUDE_PROJECT_DIR`**: env var holding the project root. Quote it in commands: `"\"$CLAUDE_PROJECT_DIR\"/.claude/hooks/x.sh"`.
- **`CLAUDE_ENV_FILE`**: a file that Claude Code runs as a script preamble before each Bash command. Hooks write `export` lines into it to change the Bash tool's environment.
- **`tool_input.file_path`**: the field in the hook's stdin JSON that holds the target path for `Edit`/`Write`. Extract it with `jq -r '.tool_input.file_path'`.
- **`PermissionRequest` decision**: JSON `hookSpecificOutput.decision.behavior: "allow"` answers a permission dialog for you.
- **`updatedPermissions` / `setMode`**: lets a `PermissionRequest` hook switch the permission mode (`default`, `acceptEdits`, `bypassPermissions`) with `destination: "session"`.
- **`/hooks`**: the browser that lists every configured hook, grouped by event.

## Mental Models
- **Think of a hook as a git hook for the agent loop**: it fires on an event and can veto. It cannot think, so keep any judgment out of it.
- **Use `PreToolUse` to prevent and `PostToolUse` to react.** Formatting goes after the edit. Protection goes before it, because `PostToolUse` can't undo anything.
- **Use `SessionStart` with matcher `compact` to restore what compaction drops.** Stdout becomes context. For context you want on every session, CLAUDE.md is the better home.
- **Use `FileChanged` when you care about a file regardless of who wrote it.** `PostToolUse` on `Edit|Write` misses files that `Bash` rewrites.

## Anti-patterns
- **Replacing the whole `hooks` object when adding an event**: it silently deletes your other hooks. Add the event as a sibling key.
- **Empty or `.*` matcher on `PermissionRequest`**: it auto-approves every prompt, including shell commands and file writes. Keep it as narrow as `ExitPlanMode`.
- **Forgetting `chmod +x`** on hook scripts (macOS/Linux): the script never runs.
- **Assuming silence means failure**: a successful hook prints nothing. Check its effect instead.
- **Relying on `osascript` / `notify-send` without testing them first**: Script Editor may lack notification permission (it fails silently). `notify-send` needs a notification daemon, which SSH sessions, headless servers and containers lack (install `libnotify-bin` on Debian/Ubuntu).

## Code Examples
```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [{ "type": "command", "command": "jq -r '.tool_input.file_path' | xargs npx prettier --write" }]
      }
    ],
    "Notification": [
      {
        "matcher": "",
        "hooks": [{ "type": "command", "command": "osascript -e 'display notification \"Claude Code needs your attention\" with title \"Claude Code\"'" }]
      }
    ]
  }
}
```
- **What it demonstrates**: two events as sibling keys. A formatter runs only after file edits, and a desktop notification fires on every notification type. Linux: `notify-send 'Claude Code' 'Claude Code needs your attention'`. Windows: `powershell.exe` with a `System.Windows.Forms.MessageBox` (a dialog, which may open behind the terminal; under WSL, `powershell.exe` must be on `PATH`).

```json
{
  "hooks": {
    "SessionStart": [
      { "matcher": "compact",
        "hooks": [{ "type": "command", "command": "echo 'Reminder: use Bun, not npm. Run bun test before committing. Current sprint: auth refactor.'" }] }
    ]
  }
}
```
- **What it demonstrates**: re-injecting context after compaction. Swap `echo` for dynamic output such as `git log --oneline -5`.

```json
{
  "hooks": {
    "SessionStart": [{ "hooks": [{ "type": "command", "command": "direnv export bash > \"$CLAUDE_ENV_FILE\"" }] }],
    "CwdChanged":   [{ "hooks": [{ "type": "command", "command": "direnv export bash > \"$CLAUDE_ENV_FILE\"" }] }],
    "FileChanged":  [{ "matcher": ".envrc|.env",
                       "hooks": [{ "type": "command", "command": "direnv export bash > \"$CLAUDE_ENV_FILE\"" }] }]
  }
}
```
- **What it demonstrates**: keeping the Bash tool's environment in sync with direnv. Run `direnv allow` once per directory. For devbox/nix, replace the command with `devbox shellenv`. The `FileChanged` matcher is split on `|` into **literal filenames** (not a regex).

```json
{
  "hooks": {
    "ConfigChange": [
      { "matcher": "",
        "hooks": [{ "type": "command", "command": "jq -c '{timestamp: now | todate, source: .source, file: .file_path}' >> ~/claude-config-audit.log" }] }
    ]
  }
}
```
- **What it demonstrates**: an audit trail for settings and skills changes. The matcher can filter to `user_settings`, `project_settings`, `local_settings`, `policy_settings` or `skills`. Block a change with exit 2 or `{"decision": "block"}`.

```json
{
  "hooks": {
    "PermissionRequest": [
      { "matcher": "ExitPlanMode",
        "hooks": [{ "type": "command",
          "command": "echo '{\"hookSpecificOutput\": {\"hookEventName\": \"PermissionRequest\", \"decision\": {\"behavior\": \"allow\"}}}'" }] }
    ]
  }
}
```
- **What it demonstrates**: auto-approving the plan-mode exit. Claude Code restores the mode that was active before plan mode, and the transcript shows "Allowed by PermissionRequest hook". The hook path always keeps the current conversation and cannot clear context the way the dialog can. To set a mode instead, add `"updatedPermissions": [{ "type": "setMode", "mode": "acceptEdits", "destination": "session" }]` inside `decision`. `bypassPermissions` only takes effect if bypass was already available at launch (`--dangerously-skip-permissions`, `--permission-mode bypassPermissions`, `--allow-dangerously-skip-permissions`, or `permissions.defaultMode: "bypassPermissions"` in user/`--settings`/managed settings). It never applies when `permissions.disableBypassPermissionsMode` is set or in restricted mode, and it is never saved as `defaultMode`.

## Reference Tables
**`Notification` matcher values** (empty matcher = all types)

| Matcher | Fires when |
|---|---|
| `permission_prompt` | A tool use or a sandboxed network request needs approval and the prompt has waited ~6 s (terminal timing; other hosts differ) |
| `idle_prompt` | Claude finished ~60 s ago and you haven't typed |
| `auth_success` | Authentication completes |
| `elicitation_dialog` | An MCP server opens an elicitation form and you've been idle ~6 s |
| `elicitation_url_dialog` | An MCP server asks you to open a URL and you've been idle ~6 s |
| `elicitation_complete` | An MCP server reports a URL-mode elicitation complete |
| `elicitation_response` | An MCP elicitation response is sent back |
| `agent_needs_input` | A background session waits on input while agent view is open (also: a teammate terminal-setup question, or an auto-mode classifier-charges notice, after ~6 s idle) |
| `agent_completed` | A background session finishes or fails (only while agent view is open) |
| `quota_auto_resume_fired` | The task continues after a claude.ai usage limit paused it |
| `quota_auto_resume_stale` | The limit reset while the machine slept >~30 min. Claude Code waits for `Enter` |
| `quota_auto_resume_disabled` | The wait ends without continuing (`autoContinueAtUsageLimit` off, reset >24 h away, repeated limit hits, or continuation blocked). Not fired on `Esc`/`Ctrl+C` |

Version gates: the `quota_auto_resume_*` matchers need v2.1.234+. `permission_prompt` for sandbox network requests in a terminal needs v2.1.246+. `agent_needs_input` for a teammate setup question needs v2.1.248+.

**Recipe index**

| Goal | Event | Matcher | Signal |
|---|---|---|---|
| Desktop alert | `Notification` | `""` | side effect |
| Auto-format | `PostToolUse` | `Edit\|Write` | side effect |
| Protect files | `PreToolUse` | `Edit\|Write` | `exit 2` + stderr |
| Restore context | `SessionStart` | `compact` | stdout → context |
| Audit config | `ConfigChange` | `""` or source | side effect / `exit 2` |
| Env reload | `SessionStart` + `CwdChanged` / `FileChanged` | — / filenames | write `CLAUDE_ENV_FILE` |
| Auto-approve | `PermissionRequest` | `ExitPlanMode` | JSON `behavior: "allow"` |

## Worked Example
Goal: stop Claude from editing `.env`, `package-lock.json` or anything under `.git/`, and tell it why so it can change approach.

1. Script `.claude/hooks/protect-files.sh`:
```bash
#!/bin/bash
INPUT=$(cat)
FILE_PATH=$(echo "$INPUT" | jq -r '.tool_input.file_path // empty')
FILE_PATH="${FILE_PATH//\\//}"   # normalize Windows backslashes
PROTECTED_PATTERNS=(".env" "package-lock.json" ".git/")
for pattern in "${PROTECTED_PATTERNS[@]}"; do
  if [[ "$FILE_PATH" == *"$pattern"* ]]; then
    echo "Blocked: $FILE_PATH matches protected pattern '$pattern'" >&2
    exit 2
  fi
done
exit 0
```
2. Run `chmod +x .claude/hooks/protect-files.sh`.
3. Register it in `.claude/settings.json`, which is committed so the whole team gets it:
```json
{ "hooks": { "PreToolUse": [ { "matcher": "Edit|Write",
  "hooks": [ { "type": "command", "command": "\"$CLAUDE_PROJECT_DIR\"/.claude/hooks/protect-files.sh" } ] } ] } }
```
4. Test by asking Claude to add a comment to `.env`. The `Edit` call is blocked before it runs, and the `Blocked:` stderr line reaches Claude as feedback.

Why these choices: `PreToolUse` because the edit has to be prevented, which `PostToolUse` can't do. Exit 2 because a block with a reason is all you need, so no JSON. `// empty` keeps `jq` from printing `null` on tools without a path. Remaining gap: `Bash` can still write the file (`echo x > .env`). For full coverage, also match `Bash|PowerShell` or add a `Stop` scan (ch15).

## Key Takeaways
1. Hooks guarantee behavior. CLAUDE.md only requests it.
2. Every event is a sibling key under one `hooks` object. Never overwrite the object when adding an event.
3. Exit 2 plus a stderr reason is the simplest guard. JSON on stdout is for decisions such as `allow` or `setMode`.
4. Keep `PermissionRequest` matchers narrow. An empty matcher approves everything.
5. Pair `SessionStart` with `CwdChanged`/`FileChanged` and write `CLAUDE_ENV_FILE` to keep the Bash environment correct.
6. Verify every hook: check `/hooks`, trigger the event, look for the effect.

## Connects To
- **ch15**: exit-code semantics, JSON output, matchers, `if`, and the location table behind these recipes.
- **ch16**: prompt/agent/HTTP hooks, timeouts, and troubleshooting when a recipe doesn't fire.
- **ch01**: CLAUDE.md is the better home for context you want injected on every session.
- **ch11**: hooks defined in subagent frontmatter.
- **ch06**: the skill frontmatter reference, where skill-scoped `hooks` are declared.
