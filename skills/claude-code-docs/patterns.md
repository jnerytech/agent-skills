# Patterns — Claude Code Docs

## Advice + Lock
**When to use**: A rule must hold no matter what the model decides, such as never editing `.env` or never pushing to main.
**How**: State the behavior in CLAUDE.md (or managed `claudeMd`). Enforce it separately with `permissions.deny`, a `PreToolUse` hook that exits 2, or sandboxing. (ch01, ch03, ch15)
**Trade-offs**: Two places to maintain. CLAUDE.md alone is advisory because it arrives as context, not configuration.

## Path-Scoped Rules Split
**When to use**: The root CLAUDE.md is over ~200 lines, or holds rules that apply to only one subsystem.
**How**: Move each topic to `.claude/rules/<area>.md` with `paths:` globs. Keep only global facts in the root. (ch02)
**Trade-offs**: A scoped rule costs nothing until a matching file is touched. Rules without `paths` still load at launch, and conflicts between files resolve arbitrarily.

## Shared AGENTS.md via Import
**When to use**: The repo serves several coding agents and also needs Claude-specific lines.
**How**: Create a `CLAUDE.md` containing `@AGENTS.md`, with Claude-only additions below it. (ch03)
**Trade-offs**: The content never loads twice and it works on Windows. A symlink is simpler but cannot hold Claude-only content.

## Index + Topic Files (auto memory)
**When to use**: `MEMORY.md` is approaching 200 lines or 25KB.
**How**: Keep one line per entry in the index and move the detail into topic files that are read on demand. (ch04)
**Trade-offs**: Topic files aren't in context until Claude chooses to open them.

## Progressive Disclosure Skill
**When to use**: A skill carries a large amount of reference material.
**How**: Keep `SKILL.md` as navigation (under 500 lines). Link `reference.md` / `examples.md` with a "what + when to read" note for each. (ch06)
**Trade-offs**: Low recurring cost, but Claude has to decide to open the files.

## Bundled-Script Skill
**When to use**: The work is deterministic or heavy, such as reports, validation or generated HTML.
**How**: Put the script in `scripts/` and call it as `${CLAUDE_SKILL_DIR}/scripts/x.py`. Pre-approve it with a matching `allowed-tools` Bash rule. (ch06, ch09)
**Trade-offs**: Reliable output with no prompts. The script must be portable (stdlib only).

## Live-Context Skill
**When to use**: The skill needs the current diff, PR, branch or environment.
**How**: Inject the data with `` !`cmd` `` and cover the commands in `allowed-tools`. Append `|| true` to checks that exit 1 when they find something. (ch08)
**Trade-offs**: The data is grounded, but any failure or unapproved command aborts the whole invocation.

## Manual-Only Side-Effect Skill
**When to use**: The skill deploys, commits or sends messages.
**How**: Set `disable-model-invocation: true`, add an `argument-hint`, and scope `allowed-tools` narrowly. (ch07)
**Trade-offs**: You control when it runs, but Claude can't discover or suggest it.

## Forked Task (skill or subagent)
**When to use**: Self-contained research, deploys or noisy tool runs that would flood the main context.
**How**: Use `context: fork` + `agent:` in a skill, or delegate to a subagent and ask for only failures or a summary back. (ch08, ch12)
**Trade-offs**: The main context stays clean. A non-fork subagent starts cold with no history, so restate every CLAUDE.md rule it needs in the brief.

## Parallel Research / Chained Subagents
**When to use**: Independent investigation paths (parallel), or multi-step pipelines such as review followed by fix (chained).
**How**: Spawn one subagent per area and let main synthesize. For chains, run the subagents in sequence and have main pass context forward. (ch12)
**Trade-offs**: Each subagent pays its own tokens, and every result lands in main's context. The limits are depth 3 and 20 concurrent.

## Fork for a Side Task
**When to use**: A side task needs the whole conversation as background.
**How**: Use `/subtask` (a fork). It inherits history and shares the prompt cache, and returns only its result. (ch13)
**Trade-offs**: Cheaper than briefing a fresh subagent, but it gets the same tools and model as the parent. Use a defined subagent when you need different ones.

## Prompt Rule + Hook Backstop
**When to use**: A safety-critical restriction inside a broad tool, such as a read-only database query through Bash.
**How**: Narrow `tools`, state the rule in the subagent prompt, and enforce it with a frontmatter `PreToolUse` hook script that exits 2. (ch11, ch13)
**Trade-offs**: Needs an executable script and a trusted folder, and a regex can miss cases.

## Guardrail Hook
**When to use**: Block specific edits or commands deterministically.
**How**: Use `PreToolUse` with a narrow matcher. The script reads stdin JSON and exits 2 with the reason on stderr. (ch14)
**Trade-offs**: Exit codes can only block or stay silent, so use JSON for allow/ask. Bash writes bypass an `Edit|Write` matcher.

## Post-Edit Formatter
**When to use**: Keep formatting consistent after Claude edits files.
**How**: Use `PostToolUse` with matcher `Edit|Write` and run `jq -r '.tool_input.file_path' | xargs npx prettier --write`. (ch14)
**Trade-offs**: Misses files that Bash changes. Use `FileChanged` to catch those.

## Context Re-injection After Compaction
**When to use**: Critical rules must survive `/compact`.
**How**: Add a `SessionStart` hook with matcher `compact` whose stdout becomes context. (ch14)
**Trade-offs**: Only for post-compaction gaps. Context every session needs belongs in CLAUDE.md.

## Completion Gate (Stop hook)
**When to use**: Claude must not stop until tests pass or the work is done.
**How**: Use a Stop hook (command returning `decision: "block"`, or a prompt/agent hook) that exits early when `stop_hook_active` is true. (ch16)
**Trade-offs**: Capped at 8 consecutive blocks (`CLAUDE_CODE_STOP_HOOK_BLOCK_CAP`). Agent hooks are experimental.
