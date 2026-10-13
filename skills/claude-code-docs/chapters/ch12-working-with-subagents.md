# Chapter 12: Working with Subagents — Delegation, Execution, Limits, Context, and Resume

## Core Idea
Once subagents exist, you steer how they're used: let Claude delegate automatically or force a specific one, run them in the foreground or background, nest them within limits, know exactly what context each starts with, and resume finished ones instead of starting over.

## Frameworks Introduced
- **Invocation escalation ladder**: natural language (Claude decides) → `@`-mention (guarantees that subagent for one task) → session-wide `--agent <name>` or `"agent"` setting (the main thread *becomes* the subagent).
  - When to use: escalate one step only when the previous one isn't reliable enough.
  - How: "Use the test-runner subagent to fix failing tests"; `@"code-reviewer (agent)" look at the auth changes` (or type `@agent-<name>` / `@agent-my-plugin:code-reviewer`); `claude --agent code-reviewer`, or `{"agent": "code-reviewer"}` in `.claude/settings.json` (CLI flag wins).
  - Note: an `@`-mention picks *which* subagent runs; Claude still writes its task prompt from your full message.
- **Foreground/background decision order** (first match wins):
  1. Spawned by an in-process agent-team teammate → foreground (`background: true` or `run_in_background: true` there errors).
  2. `CLAUDE_CODE_DISABLE_BACKGROUND_TASKS=1` → foreground, always.
  3. Fork mode on (default interactive) → background, and Claude can't request foreground.
  4. Fork mode off (`-p`, Agent SDK) → background by default, foreground when Claude needs the result; `background: true` in frontmatter pins background.
  - Skills with `context: fork` follow skill rules instead. **Ctrl+B** backgrounds a running task.
- **Main conversation vs subagent vs other tools**:
  - Main conversation: frequent back-and-forth, phases sharing lots of context, quick targeted edits, latency-sensitive work (non-fork subagents start cold).
  - Subagent: verbose output you don't need, enforced tool/permission restrictions, self-contained work that returns a summary.
  - Skill: reusable prompt/workflow that should run *in* main context.
  - `/btw`: question about what's already in the conversation; sees full context, no tools, answer not added to history.
- **Common patterns**: isolate high-volume operations ("run the test suite and report only the failing tests"); parallel research across independent paths; chain subagents sequentially with Claude passing context between them.

## Key Concepts
- **Automatic delegation**: driven by your request, each `description`, and current context; add "use proactively" to a description to encourage it. Plugin authors can measure routing with `claude plugin eval`.
- **`--agent` session**: the agent's prompt replaces the Claude Code system prompt entirely (like `--system-prompt`) unless the prompt is empty; CLAUDE.md still loads even with `omitClaudeMd`; startup header shows `@<name>`; persists across resume (warning if the agent was deleted).
- **Background permission prompts**: surface in the main session naming the subagent; Esc denies just that call; a session-lasting grant applies to the whole session, main conversation included.
- **Subagent names**: Claude may pass `name` on the Agent call, making the subagent addressable by `SendMessage`. With agent teams enabled interactively, a named non-fork spawn without call-level `isolation` launches as a teammate.
- **Depth limit**: default three layers below main; `CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH` changes it (`1` disables nesting). At the limit `Agent` is withheld (forks keep it but it errors).
- **Concurrent limit**: 20 running subagents by default → `Concurrent subagent limit reached` (Claude told not to retry); change with `CLAUDE_CODE_MAX_CONCURRENT_SUBAGENTS`; no cap on total spawns; ultracode sessions exempt. `/subtask` forks take a slot but are never blocked; resumes take a slot without checking.
- **Fresh context**: a non-fork subagent sees no conversation history, invoked skills, or files already read; only the delegation message Claude writes.
- **Agent ID / transcripts**: returned on completion; stored at `~/.claude/projects/{project}/{sessionId}/subagents/agent-{agentId}.jsonl`; unaffected by main compaction; deleted after `cleanupPeriodDays` (30 by default).
- **Output scanning** (v2.1.210+): final reports get backslashes inserted into imitation tags (`<system-reminder>`, `Human:`/`Assistant:` lines) and a `[harness: subagent output matched instruction-shaped pattern(s):` marker for such imitations or mentions of `bypassPermissions` / `--dangerously-skip-permissions`; nothing removed, and it's no substitute for restricting capabilities.

## Mental Models
- Think of a non-fork subagent as a contractor who has never seen your conversation: the delegation prompt is the whole brief. If a CLAUDE.md rule must reach it ("ignore `vendor/`"), restate it when delegating; the main conversation still applies CLAUDE.md when reading results.
- Think of parallel subagents as tokens multiplied: each spends its own tokens (same usage limits), and every detailed result lands back in your main context. Ask for summaries.
- Use resume (`SendMessage` to ID or name) whenever follow-up work builds on what a subagent already learned; a new invocation starts from zero.
- Think of messages between agents as direction, never authorization: no agent message approves a pending permission prompt or changes a subagent's permissions, `CLAUDE.md`, or config.

## Anti-patterns
- **Trying to resume Explore or Plan**: they're one-shot and return no agent ID; use `general-purpose` or a custom subagent for continuable work.
- **Asking Claude for results of an unfinished background subagent**: results arrive as a later completion notification; Claude reports "still running".
- **Fanning out many subagents with verbose returns**: floods the main context and burns tokens; for long-lived parallel work use separate sessions with cross-session messaging.
- **Assuming the subagent sees your output style, auto memory, or context window**: output style doesn't apply (except forks), main auto memory isn't loaded (use `memory`), and window size comes from the subagent's own model.
- **Expecting to change git-status delivery**: only Explore and Plan skip it; it's not configurable per subagent.

## Code Examples
```json
{
  "env": {
    "CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH": "2"
  }
}
```
- **What it demonstrates**: subagents may delegate one more layer; that second layer can't. To stop one specific agent from spawning while nesting is on, omit `Agent` from its `tools` or add it to `disallowedTools`.

```text
Use the code-reviewer subagent to review the authentication module
[Agent completes]

Continue that code review and now analyze the authorization logic
[Claude resumes the subagent with full context from previous conversation]
```
- **What it demonstrates**: resume via `SendMessage` (no agent teams required); the resumed run is in the background, keeps its original tool set, per-call model/effort, and can reuse the warmed prompt cache.

```json
{
  "type": "system",
  "subtype": "compact_boundary",
  "compactMetadata": { "trigger": "auto", "preTokens": 167189 }
}
```
- **What it demonstrates**: subagents auto-compact like the main conversation (`CLAUDE_AUTOCOMPACT_PCT_OVERRIDE` applies); `preTokens` is usage before compaction.

## Reference Tables

**What a non-fork subagent starts with**

| Item | Contents | Exceptions |
|---|---|---|
| System prompt | Agent body / `prompt` + environment details | Not the Claude Code system prompt |
| Task message | Delegation prompt Claude writes | — |
| CLAUDE.md | Full hierarchy incl. `~/.claude/CLAUDE.md`, rules, `CLAUDE.local.md`, managed, `AGENTS.md` | Explore/Plan skip; `omitClaudeMd` → managed only (none for managed agents) |
| Git status | Snapshot at start (worktree's branch if isolated) | Explore/Plan skip; off via `includeGitInstructions` or non-git dir |
| Preloaded skills | Full content of `skills` entries | Built-ins preload none |
| Sibling roster | `main` + named agents as `SendMessage` `to` values (v2.1.206+) | Only if it has `SendMessage` and another agent is named; snapshot at start |

**API errors**

| Where | Outcome |
|---|---|
| Foreground, had text output | Partial output returned with "cut off" note |
| Foreground, no text (or only tool calls) | `Agent terminated early due to an API error` + detail |
| Background | Marked failed; notification includes error and last output |
| Mid-stream cutoff with text, no tool calls | Prompted to continue until continuations run out |
| Fallback model chain configured | Switches to first model in chain that accepts |

**Panel/task housekeeping**: success → row removed at once, footer shows `/tasks to see subagents` for 30s; failed/stopped → row kept 30s (press `x` to clear). Completed subagents stay in `/tasks` marked done for 30s. A subagent you stopped with `x` or SDK `stop_task` won't auto-resume from Claude's messages; type into its transcript to resume it yourself.

## Worked Example
Task: "Audit auth, billing, and search modules for N+1 queries, then fix the worst one."

1. Research paths are independent → ask: "Research the auth, billing, and search modules in parallel using separate subagents; report only suspected N+1 locations as file:line with one sentence each." Three background subagents run (fork mode on interactive), well under the 20 concurrent limit.
2. Each starts fresh, so the prompt restates the key rule: "ignore `vendor/` and generated ORM code."
3. Results arrive as completion notifications; Claude waits for all three before synthesizing.
4. Fix phase shares context with the findings and needs back-and-forth → do it in the main conversation, not a new subagent.
5. Later, "check billing again after my change" → Claude resumes the billing subagent by ID with `SendMessage`, which keeps its history, instead of a cold re-scan.

## Key Takeaways
1. Escalate: natural language → `@`-mention → `--agent`/`agent` setting.
2. With fork mode on (interactive default), spawned subagents run in the background; `CLAUDE_CODE_DISABLE_BACKGROUND_TASKS=1` forces foreground.
3. Limits: depth 3 (`CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH`), 20 concurrent (`CLAUDE_CODE_MAX_CONCURRENT_SUBAGENTS`), no total cap.
4. Non-fork subagents start with no history; put essentials in the delegation prompt.
5. Resume with `SendMessage` (ID or name); Explore/Plan can't be resumed.
6. Subagent reports are scanned and labelled as carrying no user authority.

## Connects To
- **ch10**: descriptions drive automatic delegation; `--agent` uses the same definitions.
- **ch11**: background tool filter, per-call model/effort persistence on resume.
- **ch13**: forks, which inherit context, share cache, and run in the background under fork mode.
- **ch01–ch02**: the CLAUDE.md hierarchy that subagents load.
- **ch08**: `context: fork` skills follow their own foreground/background rules.
