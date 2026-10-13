# Chapter 04: Auto Memory, `/memory`, and Troubleshooting Instructions

## Core Idea
Auto memory is Claude's own notebook: a per-repository directory with a `MEMORY.md` index (first 200 lines / 25KB loaded every session) and on-demand topic files. When instructions "aren't followed", the fix is almost always visibility (`/context`, `/memory`), specificity, conflicts, or moving the rule to a hook.

## Frameworks Introduced
- **Four memory types** (recorded as `type` in the memory file's frontmatter):
  - `user`: your role, expertise, working preferences
  - `feedback`: corrections you give and approaches you confirm
  - `project`: ongoing work, deadlines, decisions not derivable from code or git history
  - `reference`: where to find outside info (issue tracker, dashboard)
  - Skipped: anything derivable from the codebase (architecture, file paths, debugging fixes) and anything already in CLAUDE.md. Claude saves only what would help a future conversation — not every session.
- **Index + topic files**: `MEMORY.md` is a one-line-per-entry index loaded at startup; detail lives in topic files read on demand with normal file tools.
  - How: after each write Claude Code measures `MEMORY.md` against 200 lines / 25KB. Near a limit → reminder to shorten (one line per entry, move detail to topic files, merge/drop stale). Over → write succeeds but returns an error telling Claude to rewrite the index, since overflow is dropped on next load.
  - Failure mode: an index that grows past the limit silently loses its tail at session start.
- **"Not following CLAUDE.md" debug ladder**:
  1. `/context` → **Memory files**: is the file actually loaded? If missing, Claude can't see it.
  2. Subdirectory CLAUDE.md won't appear there (on-demand); watch for a `Loaded` line in the terminal. To test a new one, create it from your shell, then ask Claude to read a file in that subdirectory.
  3. Confirm the file is in a loaded location (ch01 table).
  4. Make the instruction specific and verifiable.
  5. Remove conflicts across files.
  6. Check competition with built-in guidance: for commit/PR rules, disable built-ins with `includeGitInstructions` and set text with `attribution`.
  7. Must-happen-at-a-point rules (before every commit, after each edit) → a hook. System-prompt-level text → `--append-system-prompt` at launch.
  - Why it works: CLAUDE.md is delivered as a *user message after the system prompt*, so compliance is probabilistic; each rung either fixes visibility or moves the rule to a stronger mechanism.

## Key Concepts
- **Memory directory**: `~/.claude/projects/<project>/memory/`; `<project>` derived from the git repo, so all worktrees and subdirectories share it; outside git, the project root is used.
- **Machine-local**: not shared across machines or cloud environments.
- **`autoMemoryEnabled`**: on by default locally; `/memory` toggle writes it to `~/.claude/settings.json`; set `false` in a project's settings to disable per project.
- **`CLAUDE_CODE_DISABLE_AUTO_MEMORY=1`**: env-var off switch.
- **`autoMemoryDirectory`**: relocates storage; absolute path or `~/`; readable from any settings scope; project-level values honored under workspace trust rules, and ignored when `permissions.blockReadsOutsideWorkingDirectories` is on and a repository-supplied settings file chose it.
- **`CLAUDE_CODE_PROJECT_DIR_NAME`** (with `CLAUDE_CONFIG_DIR`): fixed `<project>` name, so all launches with that config dir share one memory dir (v2.1.234+).
- **`modified` frontmatter**: ISO 8601 write timestamp Claude Code adds to memory files that already have frontmatter (v2.1.214+); never adds frontmatter to files without it.
- **Retention**: `cleanupPeriodDays` deletes old transcripts but excludes memory files.
- **Subagents**: main auto memory is not loaded into subagents, except forks; a subagent's own memory (`memory` field) is a separate directory.
- **CLAUDE.md size cap**: a CLAUDE.md up to 4 MiB loads in full; larger is skipped. The 200-line/25KB limit is `MEMORY.md` only.

## Mental Models
- Think of `MEMORY.md` as **a table of contents, not a notebook** — one line per memory, pointers to topic files.
- "Remember X" → auto memory; "add this to CLAUDE.md" → CLAUDE.md. Use CLAUDE.md for team-shared rules, auto memory for things about *you* and this repo's live context.
- Think of compaction as **a reload from disk**: project-root CLAUDE.md is re-injected; nested files and path rules return only when re-triggered; conversation-only instructions are gone.
- Use a hook when "Claude should usually" must become "this always happens".

## Anti-patterns
- **Letting `MEMORY.md` hold full notes**: past 200 lines/25KB the rest is dropped at load.
- **Giving durable rules only in chat**: lost after `/compact`; put them in CLAUDE.md.
- **Asking Claude to write a new subdirectory CLAUDE.md to test loading**: its own write muddles the on-demand trigger; create it from the shell.
- **Using imports to fix a large CLAUDE.md**: imported files load at launch too; use path-scoped rules or trim.
- **Expecting to re-enable auto memory from a background session or a Claude-spawned `claude`**: the toggle reads `off · can't be turned on here; use a session started outside Claude Code`.
- **CLAUDE.md commit rules fighting built-in git instructions**: turn off `includeGitInstructions`, use `attribution`.

## Code Examples
```json
{ "autoMemoryEnabled": false }
```
```json
{ "autoMemoryDirectory": "~/my-custom-memory-dir" }
```
- **What it demonstrates**: per-project disable (project settings) and relocating storage (any settings scope; absolute or `~/` path).

```text
~/.claude/projects/<project>/memory/
├── MEMORY.md           # Index, one line per memory, loaded into every session
├── user_role.md        # One memory
├── feedback_testing.md # One memory
└── ...
```
- **What it demonstrates**: index-plus-topic-file layout; topic files load only when Claude reads them.

## Reference Tables

**Load limits**
| File | Limit at session start |
|---|---|
| `MEMORY.md` | First 200 lines or 25KB, whichever comes first |
| Memory topic files | Not loaded at startup; read on demand |
| Each CLAUDE.md | Loaded in full up to 4 MiB; larger skipped; >200 lines warns |

**Commands**
| Command | Use |
|---|---|
| `/memory` | List CLAUDE.md, CLAUDE.local.md, memory locations (incl. not-yet-existing ones, created on select); toggle auto memory; open auto memory folder |
| `/context` | See which CLAUDE.md and rules loaded at launch (**Memory files**) |
| `/status` | Shows over-length instruction-file warnings |
| `/doctor` | Proposes trims for checked-in CLAUDE.md (cuts derivable content, keeps pitfalls/rationale/non-default conventions); v2.1.206+ |
| `claude --debug` | Shows rule frontmatter parse errors |

**What survives `/compact`**
| Instruction source | After compaction |
|---|---|
| Project-root CLAUDE.md | Re-read from disk and re-injected |
| Nested CLAUDE.md | Reloads on demand when its subdirectory is touched again |
| `paths:` rules | Reload when a matching file is touched again |
| Conversation-only instructions | Lost |

**"My AGENTS.md isn't loading" checklist**
| Step | Check |
|---|---|
| 1 | Any `CLAUDE.md`, `.claude/CLAUDE.md`, `CLAUDE.local.md` in cwd or above (not `~/.claude/CLAUDE.md`)? It wins unless `claude-md-and-agents-md` |
| 2 | `claude --version` ≥ v2.1.277 (≥ v2.1.281 for Bedrock / telemetry-off sessions) |
| 3 | `/config` Project instructions not `claude-md` or `managed-only`; absent → unsupported session |
| Verify | `/memory` lists AGENTS.md path (before v2.1.280, ask Claude instead) |

## Worked Example
Problem: Claude keeps forgetting to run `pnpm lint` before commits, and after `/compact` it also forgets "API tests need local Redis".

1. `/context` → **Memory files**: root `CLAUDE.md` is listed, so visibility is fine.
2. Inspect the line: "Make sure code is clean" — vague. Rewrite: "Run `pnpm lint` before committing."
3. It must happen *every* commit → also add a hook (ch14) so it's enforced regardless of Claude's choice.
4. The Redis note was only said in chat → lost at compaction. Say "remember that the API tests require a local Redis instance"; Claude saves it as auto memory (likely `project` type) with a line in `MEMORY.md`. If the team needs it, instead "add this to CLAUDE.md".
5. Check what was saved: `/memory` → open auto memory folder; confirm the topic file and its `modified` timestamp.
6. Months later, Claude Code warns `MEMORY.md` is near 200 lines → let Claude merge stale entries and move details into topic files.
7. Optional: add an `InstructionsLoaded` hook to log which CLAUDE.md/rules load and why when debugging path rules.

## Key Takeaways
1. Auto memory: on by default, per repo, shared across worktrees, machine-local, at `~/.claude/projects/<project>/memory/`.
2. Only the first 200 lines / 25KB of `MEMORY.md` load; keep it an index, details in topic files.
3. Four types: `user`, `feedback`, `project`, `reference`; derivable facts are skipped.
4. Disable with `/memory` toggle, `autoMemoryEnabled: false`, or `CLAUDE_CODE_DISABLE_AUTO_MEMORY=1`; relocate with `autoMemoryDirectory`.
5. CLAUDE.md arrives as a user message after the system prompt — debug with `/context`, specificity, conflict removal, then hooks or `--append-system-prompt`.
6. After `/compact`, only project-root CLAUDE.md is re-injected immediately; chat-only instructions are lost.

## Connects To
- **ch01**: CLAUDE.md vs auto memory split and writing effective instructions.
- **ch02**: on-demand loading and path rules that explain post-compaction behavior.
- **ch03**: AGENTS.md loading rules behind the troubleshooting checklist.
- **ch11**: subagent `memory` field for separate persistent subagent memory.
- **ch13**: forks inherit the parent's auto memory context.
- **ch14**: hooks for rules that must run at fixed points; `InstructionsLoaded` for load logging.
