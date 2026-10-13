# Chapter 08: Advanced Skill Patterns — Dynamic Context, Forked Subagents, Access Control

## Core Idea
Skills can pull live data into their prompt with `` !`cmd` `` before Claude sees the content. They can run as an isolated subagent with `context: fork`. You can control them from outside the file with `Skill(...)` permission rules and `skillOverrides`. Use `/skill-doctor` to prune skills that cost context but are never used.

## Frameworks Introduced
- **Dynamic context injection**: `` !`<command>` `` (inline) or a ```` ```! ```` fenced block (multi-line) runs at render time, and its output replaces the placeholder.
  - When to use: the skill needs current state (diff, PR, env versions) so Claude doesn't guess.
  - How: put `!` at line start or after whitespace (`` KEY=!`cmd` `` stays literal). Use `${CLAUDE_SKILL_DIR}`/`${CLAUDE_PROJECT_DIR}` for stable paths, because commands run in the session's *current* cwd, which `cd` moves. Pre-approve the commands with `allowed-tools`.
  - Failure mode: **any failed command aborts the whole invocation** (`Shell command failed for pattern "..."`) and Claude never sees the skill. Non-zero exit counts as failure, except exit 1 from search/compare commands. Exit ≥ 2 always fails. Append `|| true` to checks that exit 1 on findings.
- **`context: fork` (skill as subagent task)**: Claude Code starts a fresh subagent of type `agent` (default `general-purpose`) with the skill body as its prompt. The subagent has **no conversation history**.
  - When to use: self-contained tasks with explicit instructions (research, PR summary, deploy).
  - How: by default it runs in the background and the result arrives when done. Set `background: false` to block the invoking turn (v2.1.218+).
  - Failure mode: pure guidelines with no task give no useful output. The name is also misleading: this is *not* a fork of the conversation. If the task needs prior discussion, fork the conversation instead.
- **Three layers of skill access control**: deny `Skill` (all skills), use `Skill(name)` / `Skill(name *)` allow/deny rules (specific skills), and `disable-model-invocation` or `skillOverrides` (visibility).

## Key Concepts
- **Single-pass substitution**: command output isn't re-scanned, so output can't inject further `!` placeholders.
- **`disableSkillShellExecution: true`**: replaces each command with `[shell command execution disabled by policy]` for user, project, plugin and add-dir skills. Bundled and managed skills are unaffected. It is best placed in managed settings.
- **Synced skills**: Claude Code never runs their `!` commands on your machine (v2.1.228+).
- **Injected-command execution**: runs via the Bash tool, or PowerShell when `shell: powershell` and the tool is enabled. `shell: bash` without Git Bash on Windows fails before running. Stderr is merged into stdout. The default 2-minute timeout applies, and auto-backgrounded commands still render. Large output arrives as a file path plus preview.
- **Permission checks on injected commands**: they never prompt. A deny match, or (outside auto mode) any non-allow result including "ask", aborts with `Shell command permission check failed for pattern "..."`. In auto mode the skill loads and tells Claude to run the command itself, unless it's a forked skill with `agent` set.
- **Forced foreground**: a fork waits even with `background: true` in `-p`/Agent SDK, with `CLAUDE_CODE_DISABLE_BACKGROUND_TASKS=1`, when a prior invocation of the same skill is still running, and when a scheduled task fires it. A workflow agent receives the result itself (v2.1.295+).
- **Background fork caveats**: it gets the narrower background-subagent tool set (use `background: false` for the full set), and its edits fall outside checkpoints, so `/rewind` won't undo them. Use git.
- **`ultrathink`**: anywhere in the body, it requests deeper reasoning when the skill runs.

## Mental Models
- Think of `` !`cmd` `` as a preprocessor. It runs before Claude reads anything, and it is all-or-nothing.
- Choose between the two skill/subagent directions this way. *Skill + `context: fork`*: you write the task in the skill and borrow an agent's system prompt and tools. *Subagent + `skills` field*: you write the agent's persona and the skills serve as preloaded reference.
- `agent: Explore` and `agent: Plan` skip CLAUDE.md and git status, so the fork sees only the skill body and the agent's prompt. Use `general-purpose` or a custom agent if CLAUDE.md matters.
- Use `skillOverrides` to change visibility of skills whose `SKILL.md` you can't or won't edit (shared repo). Use frontmatter for skills you own.

## Anti-patterns
- **A check script that exits 1 without `|| true`**: aborts the skill.
- **Relative paths in injected commands**: they break after Claude `cd`s.
- **An injected command not covered by allow rules (outside auto mode)**: the invocation aborts instead of prompting.
- **`context: fork` for a task needing chat history**: the subagent starts blank.
- **Background fork for destructive edits you might rewind**: checkpoints don't cover it.
- **`skillOverrides` for plugin skills**: no effect. Manage them via `/plugin`.
- **`Skill(anthropic *)` to approve synced skills**: prefixes don't cross into the `anthropic-skills` namespace. Use `Skill(anthropic-skills *)`.

## Code Examples
```yaml
---
name: pr-summary
description: Summarize changes in a pull request
context: fork
agent: Explore
allowed-tools: Bash(gh *)
---

## Pull request context
- PR diff: !`gh pr diff`
- PR comments: !`gh pr view --comments`
- Changed files: !`gh pr diff --name-only`

## Your task
Summarize this pull request...
```
- **What it demonstrates**: injection + fork + pre-approval together. `allowed-tools: Bash(gh *)` keeps the injected `gh` commands from aborting on a permission check.

````markdown
## Environment
```!
node --version
git status --short
```
````

```text
# Allow only specific skills
Skill(commit)
Skill(review-pr *)

# Deny specific skills
Skill(deploy *)
```

```json
{
  "skillOverrides": {
    "legacy-context": "name-only",
    "deploy": "off"
  }
}
```

## Reference Tables

| Approach | System prompt | Task | Also loads |
|---|---|---|---|
| Skill with `context: fork` | From agent type | SKILL.md content | CLAUDE.md per agent startup context (not Explore/Plan) |
| Subagent with `skills` field | Subagent's body | Claude's delegation message | Preloaded skills + CLAUDE.md |

| `skillOverrides` value | Listed to Claude | In `/` menu |
|---|---|---|
| `"on"` (default when absent) | Name + description | Yes |
| `"name-only"` | Name only | Yes |
| `"user-invocable-only"` (menu label `user-only`) | Hidden | Yes |
| `"off"` | Hidden | Hidden (also from Remote Control & SDK lists; full-name invoke errors) |

| Deny rule names | Example | Also blocks |
|---|---|---|
| Alias | `Skill(review)` | Bundled `/code-review` via `/review` |
| Unqualified name | `Skill(deploy)` | Nested `apps/web:deploy` (v2.1.260+) |
| Synced skill | `Skill(anthropic-skills:deploy)` | Same skill delivered as plugin by Desktop |
| Plugin form of synced | `Skill(deploy:deploy)` | The synced skill |
| Parameter form | `Skill(skill:deploy)` | Every name/alias/display name |

Allow rules match only the skill's own name and the invoked name. A `skillOverrides` entry under an alias applies only from managed settings or `--settings`, and only restricts. In user, project and local settings, entries match skill names only. `/skills`: `Space` cycles the state and `Esc` saves to `.claude/settings.local.json`. Built-ins reachable via the Skill tool include `/init` and `/security-review`, but not `/compact`.

## Worked Example
Goal: a `lint-report` skill that injects current lint findings and summarizes them in a blocking fork.
```yaml
---
name: lint-report
description: Summarize current lint problems by severity. Use when asked about lint, code quality, or before a PR.
context: fork
agent: general-purpose
background: false
allowed-tools: Bash(${CLAUDE_PROJECT_DIR}/scripts/lint.sh *)
---

## Findings
!`${CLAUDE_PROJECT_DIR}/scripts/lint.sh --json || true`

## Task
Group the findings above by severity, list the top 5 files, and propose fixes for errors only.
```
Decisions: `lint.sh` exits 1 when it finds problems, so `|| true` prevents an abort. `${CLAUDE_PROJECT_DIR}` survives any `cd`. The `allowed-tools` rule uses the same expanded path, so the injected command passes its permission check outside auto mode. `general-purpose` keeps CLAUDE.md context (Explore would skip it). `background: false` returns the summary in the same turn and keeps the full tool set. To stop teammates' Claude from auto-running it without editing the file, add `"lint-report": "user-invocable-only"` to `skillOverrides`. Later, `/skill-doctor` (v2.1.252+) shows whether it earns its listing cost.

## Key Takeaways
1. `` !`cmd` `` and ```` ```! ```` run before Claude sees the skill. Any failure (exit ≥ 1, except exit 1 from search tools) aborts the invocation, so use `|| true`.
2. Injected commands never prompt. Pre-approve them with `allowed-tools` or they abort outside auto mode. `disableSkillShellExecution` turns them off by policy.
3. `context: fork` starts a blank subagent (default `general-purpose`) that runs in the background by default. `background: false` blocks the turn and keeps the full tool set.
4. Explore/Plan forks skip CLAUDE.md, and background forks aren't covered by `/rewind`.
5. Gate skills with a `Skill` deny, `Skill(name)` / `Skill(name *)` rules, `disable-model-invocation`, or `skillOverrides` (`on`/`name-only`/`user-invocable-only`/`off`). None of these apply to plugin skills.
6. Run `/skill-doctor` to find never-invoked skills and turn off the most expensive first.

## Connects To
- **ch06**: `shell`, `context`, `agent`, `background`, `${CLAUDE_*}` fields.
- **ch07**: `allowed-tools` turn scope and `disable-model-invocation`.
- **ch09**: listing budget, `"name-only"` to free description budget.
- **ch11**: subagent `skills` preloading, the inverse direction.
- **ch12**: foreground vs background subagents and the background tool set.
- **ch13**: conversation forks vs `context: fork`.
