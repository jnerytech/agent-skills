# Chapter 10: Subagents — Built-ins, Scope, and Writing Subagent Files

## Core Idea
A subagent is a Markdown file with YAML frontmatter that defines a specialized worker running in its own context window, with its own system prompt, tools and permissions; use one when a side task would flood the main conversation with output you won't reference again, and define a custom one when you keep spawning the same kind of worker with the same instructions.

## Frameworks Introduced
- **Description-driven delegation**: Claude reads each subagent's `description` to decide when to delegate; the body (system prompt) loads only when the subagent runs.
  - When to use: every custom subagent.
  - How: keep `description` short and routing-specific ("Use after writing or modifying code"); push detail into the body. Keep the combined descriptions of non-built-in subagents under 15,000 tokens, or Claude Code warns at startup with the total.
  - Why it works / failure mode: descriptions sit in context permanently; bloated descriptions cost context in every session and blur routing between similar agents.
- **Scope precedence (name collision resolution)**: when two subagents share a `name`, the higher-priority location wins: Managed > `--agents` CLI > project `.claude/agents/` > user `~/.claude/agents/` > plugin `agents/`.
  - When to use: overriding a built-in (e.g. your own `Explore` with `model: haiku`), shipping org-wide agents, or testing a variant for one session.
  - How: define a file with the same `name` in a higher-priority scope. Within nested project directories, the `.claude/agents/` closest to the working directory wins. Within one directory tree, duplicates resolve by filesystem read order (undocumented), so keep names unique; `/doctor` reports same-directory duplicates.
  - Failure mode: relying on two same-named files in one tree gives a nondeterministic winner.
- **Built-in restriction ladder**: block one type with `permissions.deny: ["Agent(Explore)"]`; block all delegation by denying `Agent`; drop only Explore/Plan with `CLAUDE_CODE_DISABLE_EXPLORE_PLAN_AGENTS=1` (v2.1.198+); in `-p`/Agent SDK remove all built-ins with `CLAUDE_AGENT_SDK_DISABLE_BUILTIN_AGENTS=1`.

## Key Concepts
- **Explore**: fast read-only built-in (Write/Edit denied) for search and codebase understanding; Claude passes a thoroughness level of **quick**, **medium**, or **very thorough**. Runs on the main model, except under Fable on a subscription/Console/`ANTHROPIC_BASE_URL` gateway, where it runs on whatever `opus` resolves to.
- **Plan**: read-only built-in used in plan mode to gather context; inherits the main model.
- **general-purpose**: built-in with every subagent-available tool, for tasks that both explore and modify; it is the fallback when an Agent call omits `subagent_type` (without it, the call fails with `subagent_type is required`).
- **Other helpers**: `claude` (catch-all, default agent for dispatched background sessions), `statusline-setup` (Sonnet, for `/statusline`), `claude-code-guide` (Haiku, Claude Code questions).
- **CLAUDE.md / git status loading**: Explore and Plan skip CLAUDE.md files and the git status snapshot; every other built-in and custom subagent loads both unless `omitClaudeMd: true`.
- **Identity = `name` field**: subfolders under `.claude/agents/` or `~/.claude/agents/` (both scanned recursively) don't affect identity; in a plugin, subfolders do: `agents/review/security.md` in `my-plugin` registers as `my-plugin:review:security`.
- **CLI-defined subagents**: JSON passed to `--agents`, session-only, never saved to disk; `prompt` replaces the Markdown body. In `-p` mode `--agents` also accepts a path to a JSON file (v2.1.281+); interactive sessions refuse a path.
- **Subagent system prompt**: only the body plus basic environment details (working directory etc.), not the Claude Code system prompt.
- **Live reload**: Claude Code watches `~/.claude/agents/` and `.claude/agents/`; edits apply to the next delegation within seconds.

## Mental Models
- Think of a subagent as a disposable context window with a job description: the `description` is the job posting Claude reads, the body is the onboarding doc the worker reads.
- Use project scope (`.claude/agents/`, checked in) when the agent encodes codebase knowledge; use user scope (`~/.claude/agents/`) for personal tools you want in every repo; use `--agents` for experiments and automation scripts.
- Think of a plugin subagent as sandboxed: `hooks`, `mcpServers`, and `permissionMode` are ignored for security. Copy the file into `.claude/agents/` if you need them, or (as plugin author) ship hooks in `hooks/hooks.json` and servers in `.mcp.json`.

## Anti-patterns
- **Misspelled or snake_case frontmatter keys** (`max_turns`, `disallowed_tools`): unrecognized fields are silently ignored. Multi-word fields are camelCase and must match exactly.
- **Long descriptions**: past 15,000 combined tokens you get a startup warning; everything still loads, but context is wasted.
- **Opening `---` not on line 1, missing `name`, or YAML that doesn't parse**: the file is silently skipped (treated as documentation or logged only to `--debug`).
- **Creating `~/.claude/agents/` mid-session and expecting it to load**: the watcher covers only directories that existed at session start; restart.
- **Relying on `cd` inside a subagent**: `cd` doesn't persist between Bash/PowerShell calls; use `isolation: worktree` for an isolated checkout.

## Code Examples
```markdown
---
name: code-improver
description: Scans files and suggests improvements for readability, performance, and best practices. Use after writing or modifying code.
tools: Read, Grep, Glob
model: sonnet
---

You are a code improvement specialist. For each issue you find, explain
the problem, show the current code, and provide an improved version.
```
- **What it demonstrates**: the minimal real subagent: routing-oriented `description`, read-only `tools` allowlist, cheaper `model`, body as system prompt.

```bash
claude --agents '{
  "code-reviewer": {
    "description": "Expert code reviewer. Use proactively after code changes.",
    "prompt": "You are a senior code reviewer. Focus on code quality, security, and best practices.",
    "tools": ["Read", "Grep", "Glob", "Bash"],
    "model": "sonnet"
  }
}'
```
- **What it demonstrates**: session-only definitions; top-level key = name (don't start with `-`); `color` and `experimental` are ignored here.

```yaml
---
name: repo-auditor
description: Audits a large repository and reports what it finds
experimental:
  cacheTtl: 1h
---
```
- **What it demonstrates**: `cacheTtl` lives inside `experimental`, never at top level.

## Reference Tables

**Scope and precedence**

| Location | Scope | Priority | How to create |
|---|---|---|---|
| Managed settings (`.claude/agents/` in managed settings dir) | Organization-wide | 1 (highest) | Deployed via managed settings |
| `--agents` CLI flag | Current session | 2 | Pass JSON (or a file path in `-p`) at launch |
| `.claude/agents/` | Current project (walks up from cwd; also `--add-dir` dirs) | 3 | Ask Claude, or create the file |
| `~/.claude/agents/` | All your projects | 4 | Ask Claude, or create the file |
| Plugin `agents/` directory | Where plugin is enabled | 5 (lowest) | Installed with plugins |

**Frontmatter field reference** (only `name` and `description` required; unknown fields silently ignored)

| Field | What it does | Default when omitted |
|---|---|---|
| `name` | Unique ID, ≤256 chars; no `:`; can't start with `-`. Hooks receive it as `agent_type`. Filename needn't match | Required (file skipped if missing) |
| `description` | When Claude should delegate | Required (file skipped if missing) |
| `tools` | Allowlist: comma string or YAML list; supports `mcp__<server>`; `Agent(type,...)` only for `--agent` main thread | Inherits every subagent-available tool |
| `disallowedTools` | Denylist removed from inherited/specified pool; applied before `tools`; a specifier like `Bash(git push *)` still removes the whole tool; `mcp__*` removes all MCP | None |
| `model` | `sonnet`, `opus`, `haiku`, `fable`, full ID (e.g. `claude-opus-5-5`), or `inherit` | Per-invocation param → `CLAUDE_CODE_SUBAGENT_MODEL` → main model |
| `permissionMode` | `default`, `acceptEdits`, `auto`, `dontAsk`, `bypassPermissions`, `plan` (`manual` = `default`). Ignored for plugins | Inherits main conversation's mode |
| `maxTurns` | Max agentic turns; output returned marked partial, resumable (v2.1.246+) | No limit |
| `skills` | Skills whose full content is preloaded at startup (first 32 distinct names) | None preloaded (Skill tool still usable) |
| `mcpServers` | Server-name references or inline server configs scoped to this agent. Ignored for plugins | Inherits session's MCP tools only |
| `hooks` | Lifecycle hooks active only while this agent runs. Ignored for plugins | None |
| `memory` | Persistent memory dir: `user`, `project`, or `local` | No persistent memory |
| `background` | `true` forces background even when Claude wants foreground | Claude/fork mode decides |
| `omitClaudeMd` | `true` skips user/project/local CLAUDE.md (managed policy still loads, except for managed subagents); ignored under `--agent` (v2.1.271+) | CLAUDE.md loaded |
| `effort` | `low`, `medium`, `high`, `xhigh`, `max`; overrides session effort, not `CLAUDE_CODE_EFFORT_LEVEL` | Session effort |
| `isolation` | `worktree`: temporary git worktree branched from default branch; auto-cleaned if no changes | Runs in main cwd |
| `color` | `red`, `blue`, `green`, `yellow`, `purple`, `orange`, `pink`, `cyan` (files only) | Default display |
| `initialPrompt` | First user turn auto-submitted when run as main session (`--agent`/`agent` setting); commands and skills processed. Ignored for plugins | None |
| `experimental` | Map; `cacheTtl: 5m` or `1h` for prompt-cache lifetime; files only (v2.1.248+) | Normal cache TTL precedence |

**Files Claude Code silently skips**: no `name` (treated as docs); `---` not on first line; `name` starting with `-`, containing `:`, or >256 chars; `name` without `description`; unparseable YAML. Check before a session with `claude plugin validate .claude/agents` (v2.1.233+; doesn't flag missing `name`). Plugin agents with no `name` or bad YAML still load under their filename.

## Worked Example
Goal: make codebase exploration cheaper team-wide. Built-in Explore runs on the main model, so override it by scope precedence. Create `.claude/agents/explore.md` in the repo:

```markdown
---
name: Explore
description: Fast read-only codebase search. Use for locating code and answering "where/how" questions without edits.
tools: Read, Grep, Glob
model: haiku
---
You are a read-only search agent. Return file:line references and a short summary.
```

Decision walk-through: (1) A project subagent named `Explore` outranks the built-in and keeps its own `model`, so exploration moves to Haiku. (2) Checked into `.claude/agents/`, the whole team gets it. (3) If `.claude/agents/` didn't exist at session start, restart once; afterwards edits hot-reload. (4) If someone wants it gone for a session, `permissions.deny: ["Agent(Explore)"]` blocks it without deleting the file. (5) To force *every* subagent to Haiku instead, use the env-var approach in ch11.

## Key Takeaways
1. Only `name` and `description` are required; camelCase fields must match exactly or they're silently ignored.
2. Precedence: Managed > `--agents` > project > user > plugin; nearest `.claude/agents/` wins among nested project dirs.
3. Keep descriptions short and routing-specific; the 15,000-token combined budget triggers a startup warning.
4. Explore and Plan skip CLAUDE.md and git status; all others load them unless `omitClaudeMd: true`.
5. Plugin subagents ignore `hooks`, `mcpServers`, `permissionMode` (and `initialPrompt`).
6. Subagents get only their own body as system prompt plus environment details, not Claude Code's system prompt.

## Connects To
- **ch11**: model resolution order, tools/permission modes, MCP, memory, skills and hooks fields in depth.
- **ch12**: how Claude delegates, `@`-mentions, `--agent`, background runs, and what loads at startup.
- **ch13**: fork subagents and full example subagent files.
- **ch08**: skills with `context: fork` run inside a subagent (inverse of the `skills` field).
- **ch14–ch16**: hook mechanics used by subagent `hooks` frontmatter.
