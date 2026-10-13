# Chapter 16: Hook Types (Prompt, Agent, HTTP), Limitations, and Troubleshooting

## Core Idea
Command hooks cover deterministic rules. When a decision needs judgment, use `type: "prompt"`, which makes a single LLM call, or `type: "agent"`, which runs a subagent with tools. When the logic lives in a service, use `type: "http"`. Every type has its own timeout and failure behavior. Most "my hook does nothing" bugs come down to a short list of causes: a matcher mismatch, bad JSON placement, profile noise on stdout, or the Stop-hook loop cap.

## Frameworks Introduced
- **Choosing the hook type**:
  - `command`: a deterministic rule you can express in a script. This is the default and the production-safe choice.
  - `prompt`: judgment based **only on the hook's input data**. One model call that returns `{"ok": ..., "reason": ...}`. Use the `model` field to pick a stronger model.
  - `agent` (experimental): judgment that needs to **inspect real codebase state**, such as reading files or running tests. Default timeout 60 s, up to 50 tool-use turns.
  - `http`: shared or remote logic, for example a team-wide audit service. It POSTs the same JSON a command hook would get on stdin.
  - `mcp_tool`: call a tool on a configured MCP server.
  - Failure mode: agent hooks may change between releases. Prefer command hooks for production workflows.
- **`ok: false` handling by event (prompt hooks)**:
  - `Stop` / `SubagentStop`: `reason` is fed back and Claude keeps working. Add `"impossible": true` to allow the stop when the condition can never be met.
  - `PreToolUse`: the call is denied, the turn **ends** by default, and `reason` shows as a warning line. With `continueOnBlock: true`, `reason` goes back to Claude as the tool error and the turn continues. Before v2.1.210 the turn always continued.
  - `PostToolUse`: the turn ends with a warning by default. `continueOnBlock: true` feeds `reason` back and continues.
  - `PostToolBatch`, `UserPromptSubmit`, `UserPromptExpansion`: the turn ends with a warning line.
  - Agent hooks on `ok: false` behave like a prompt hook with `continueOnBlock: true`, so on `PreToolUse`/`PostToolUse` the turn continues. They have no `continueOnBlock` field and no `impossible` field.
- **Hooks only tighten (permission-mode rule)**: `PreToolUse` fires before any permission-mode check, in every mode including `dontAsk`. A hook `deny` blocks even under `bypassPermissions` / `--dangerously-skip-permissions`. A hook `allow` does **not** override settings deny rules, and it doesn't suppress prompts for network-path reads, `requiresUserInteraction` MCP tools, or connector tools an org set to `ask`. Hooks in settings files and plugin `hooks/hooks.json` can tighten restrictions but never loosen them past the permission rules.
  - Why it works: you get policy that users can't escape by switching mode. Exception: an installed mod handling `tool.check` can approve a call your `PreToolUse` hook blocked, unless that hook lives in **managed settings**.
- **Troubleshooting triage**: decide which symptom you have: (1) not firing, (2) error notice, (3) missing from `/hooks`, (4) Stop loop cap, (5) JSON has no effect. Each has its own fix list (see Reference Tables).

## Key Concepts
- **`ok` / `reason`**: the response contract for prompt and agent hooks.
- **`impossible`**: a prompt-hook-only flag on `Stop`/`SubagentStop` that ends the turn instead of looping.
- **`continueOnBlock`**: a prompt-hook flag. On `PreToolUse`/`PostToolUse`, it returns the block reason to Claude instead of ending the turn.
- **`$ARGUMENTS`**: a placeholder in an agent-hook `prompt` that Claude Code replaces with the hook's JSON input.
- **`allowedEnvVars`**: an HTTP-hook allowlist. Only listed vars are interpolated in `headers` (`$VAR` / `${VAR}`). Any other reference resolves to empty.
- **`onFailure: "block"`**: makes a failed HTTP endpoint (non-2xx or request error) block the action instead of producing a non-blocking error.
- **`stop_hook_active`**: an input field that is `true` when Claude is already continuing because of a Stop hook. Check it to avoid infinite loops.
- **`CLAUDE_CODE_STOP_HOOK_BLOCK_CAP`**: env var that raises the cap of 8 consecutive Stop-hook blocks.
- **`allowManagedHooksOnly`**: managed setting under which only managed hooks run. `/hooks` shows `Only hooks from managed settings run here`.
- **Exec form**: adding `"args": []` spawns the script directly, with no shell and therefore no quoting problems.

## Mental Models
- **Use prompt hooks when the stdin JSON is enough to decide, and agent hooks when you'd have to look at the repo.** "Did Claude finish all tasks?" suits a prompt. "Do the tests pass?" needs an agent.
- **Think of a Stop hook as a while-loop guard.** Without a `stop_hook_active` exit, it loops until the cap of 8 forces a stop.
- **Silence is ambiguous.** A successful hook shows nothing, and so does JSON that was ignored. Confirm by checking the effect, `Ctrl+O`, or the debug log.
- **`PostToolUse` is a reaction, not a gate.** The tool already ran and nothing can undo it.

## Anti-patterns
- **Agent hooks in production workflows**: they are experimental, so use command hooks.
- **A Stop hook without a `stop_hook_active` check**: Claude churns until the 8-block cap ends the turn with a warning.
- **Building JSON by string concatenation**: quotes and backslashes break parsing. Use `jq` or another encoder.
- **Unconditional `echo` in `~/.bashrc`/`~/.zshrc`**: it prepends text to stdout, so output no longer starts with `{` and the JSON is silently treated as plain text (exit 0, no error).
- **Expecting a hook to run `/` commands or tool calls**: command hooks talk only through stdout, stderr and exit codes. `additionalContext` arrives as a system reminder that Claude reads as plain text.
- **Several hooks rewriting the same tool's `updatedInput`**: the last to finish wins, non-deterministically.
- **Using a hook `allow` to grant what permission rules deny**: deny rules still win.

## Code Examples
```json
{ "hooks": { "Stop": [ { "hooks": [ { "type": "prompt",
  "prompt": "Check if all tasks are complete. If not, respond with {\"ok\": false, \"reason\": \"what remains to be done\"}." } ] } ] } }
```
- **What it demonstrates**: a prompt hook as a completion gate. On `ok: false`, `reason` becomes Claude's next instruction.

```json
{ "hooks": { "Stop": [ { "hooks": [ { "type": "agent",
  "prompt": "Verify that all unit tests pass. Run the test suite and check the results. $ARGUMENTS",
  "timeout": 120 } ] } ] } }
```
- **What it demonstrates**: an agent hook that checks real state, with the timeout raised from 60 s to 120 s for the test run.

```json
{ "hooks": { "PostToolUse": [ { "hooks": [ { "type": "http",
  "url": "http://localhost:8080/hooks/tool-use",
  "headers": { "Authorization": "Bearer $MY_TOKEN" },
  "allowedEnvVars": ["MY_TOKEN"] } ] } ] } }
```
- **What it demonstrates**: an HTTP hook with a secret header. 2xx plus `hookSpecificOutput` in the body lets the endpoint block. Any other status or a failed request gives a non-blocking error unless `onFailure: "block"` is set.

```bash
#!/bin/bash
INPUT=$(cat)
if [ "$(echo "$INPUT" | jq -r '.stop_hook_active')" = "true" ]; then
  exit 0  # Allow Claude to stop
fi
# ... rest of your hook logic
```
- **What it demonstrates**: the loop guard every blocking Stop command hook needs.

## Reference Tables
**Default timeouts** (override per hook with `timeout`, in seconds)

| Type | Default |
|---|---|
| `command`, `http`, `mcp_tool` | 10 min. Lowered to 30 s for `UserPromptSubmit`, `PreModelSwitch`, `PostModelSwitch`, and to 10 s for `MessageDisplay` |
| `prompt` | 30 s |
| `agent` | 60 s (max 50 tool-use turns) |
| any type on `SessionEnd` | shared 1.5 s budget, raised to the largest per-hook `timeout`, capped at 60 s |

**Limitations**
- `PostToolUse` can't undo the action.
- `PermissionRequest` fires when Claude Code is about to prompt you, or when it would auto-deny a call that can't prompt. In `-p` mode it still runs (except in `dontAsk` mode). A call that no hook decides and nothing else can answer is denied.
- `Stop` fires whenever Claude finishes responding, not only when a task is done. It doesn't fire on user interrupt, and API errors fire `StopFailure` instead.
- Parallel `updatedInput` writers race, and the last to finish wins.

**Troubleshooting matrix**

| Symptom | Check / fix |
|---|---|
| Hook never fires | Is it listed under the right event in `/hooks`? Matchers are **case-sensitive** and must match the tool name exactly. Right event? (`PreToolUse` runs before the tool, `PostToolUse` after.) |
| `"<Event> hook error: ..."` | Test manually: `echo '{"tool_name":"Bash","tool_input":{"command":"ls"}}' \| ./my-hook.sh; echo $?`. "command not found": use absolute paths or `${CLAUDE_PROJECT_DIR}`, or exec form `"args": []`. "jq: command not found": install `jq` or parse with Python/Node. Script never runs: `chmod +x`. A JSON validation/parse notice can appear even on exit 0. |
| `/hooks` shows nothing | Wait a few seconds or restart the session (the watcher missed the change). Check for invalid JSON (no trailing commas, no comments) and the right file (`.claude/settings.json` vs `~/.claude/settings.json`). `allowManagedHooksOnly` may be set. |
| Turn ends with "Stop hook blocked too many consecutive times" | Cap is 8 consecutive blocks with no tool call in between. Check `stop_hook_active`, or raise `CLAUDE_CODE_STOP_HOOK_BLOCK_CAP`. |
| Valid JSON, no effect, no error | Profile output before `{` (search the debug log for `Hook output does not start with {`). Fix: `if [[ $- == *i* ]]; then echo ...; fi`. Or a field at the wrong level (search for `Hook JSON output had unrecognized keys`). |

**Reading outcomes in the transcript (`Ctrl+O`)**

| Outcome | What you see |
|---|---|
| Success | Nothing, unless the JSON surfaces `systemMessage` or Stop feedback. Verify by the effect. |
| Blocking error | The block message (e.g. `Blocked: rm commands are not allowed`). `ConfigChange` and `Elicitation` show none. |
| Non-blocking error | `<hook name> hook error` plus the first stderr line after `Failed with non-blocking status code:`, or a JSON validation/parse message. The action proceeded. |

Full logs: `claude --debug-file /tmp/claude.log`, then `tail -f /tmp/claude.log`. Mid-session, run `/debug` to enable logging and find the path.

## Worked Example
Goal: Claude shouldn't stop until tests pass, without looping forever.

Option A (agent hook): the `type: "agent"` Stop hook above, with `timeout: 120`. The subagent runs the suite. If it returns `ok: false`, the reason (e.g. "3 tests failing in auth.spec.ts") goes back to Claude, which keeps working. The 8-block cap still applies as a backstop.

Option B (production command hook): `.claude/hooks/require-tests.sh`:
```bash
#!/bin/bash
INPUT=$(cat)
[ "$(echo "$INPUT" | jq -r '.stop_hook_active')" = "true" ] && exit 0
if ! npm test --silent >/dev/null 2>&1; then
  jq -n '{decision: "block", reason: "Tests are failing. Fix them before finishing."}'
fi
exit 0
```
Walkthrough: `jq -n` builds the JSON safely. `decision: "block"` sits at the top level, which is correct for `Stop`. The `stop_hook_active` guard means Claude gets one extra pass and is then allowed to stop, which avoids the cap warning. If the decision is silently ignored, check `~/.bashrc` for unconditional `echo`s and search the debug log for `Hook output does not start with {`.

## Key Takeaways
1. Use `prompt` for judgment from the input alone, `agent` for judgment that needs the repo (experimental), `http` for central services, and `command` for everything deterministic.
2. Prompt `ok: false` on `PreToolUse`/`PostToolUse` ends the turn unless `continueOnBlock: true` is set. Agent hooks always continue.
3. Timeouts: command/http/mcp_tool 10 min (30 s on prompt-submit and model-switch, 10 s on `MessageDisplay`), prompt 30 s, agent 60 s, and `SessionEnd` gets 1.5 s total.
4. A hook `deny` beats every permission mode, including bypass. A hook `allow` never beats deny rules.
5. Every blocking Stop hook needs a `stop_hook_active` guard because of the cap of 8.
6. "Valid JSON, no effect" almost always means stdout noise before `{` or a field outside `hookSpecificOutput`. `claude --debug` shows which.

## Connects To
- **ch15**: exit-code semantics, decision precedence, and the `hookSpecificOutput` placement rules this chapter debugs.
- **ch14**: the recipes these types extend, such as `PermissionRequest` auto-approve and `setMode`.
- **ch11**: agent hooks run a subagent, and subagents can define their own hooks.
- **ch10**: the built-in subagent types used by `SubagentStart`/`SubagentStop` matchers.
