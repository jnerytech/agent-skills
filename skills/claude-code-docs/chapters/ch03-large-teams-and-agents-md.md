# Chapter 03: Large Teams, Managed CLAUDE.md, and AGENTS.md

## Core Idea
Organizations push behavioral guidance through a managed CLAUDE.md (or the `claudeMd` managed setting) and technical enforcement through managed settings; individuals prune irrelevant monorepo files with `claudeMdExcludes`. Separately, Claude Code reads `AGENTS.md` natively, but by default only when no `CLAUDE.md`/`CLAUDE.local.md` exists on the path — a rule that explains most "AGENTS.md isn't loading" surprises.

## Frameworks Introduced
- **Settings for enforcement, CLAUDE.md for behavior**:
  - When to use: deciding where an org-wide requirement goes.
  - How: anything that must hold regardless of Claude's judgment (block tools/paths, sandbox, env, login restrictions) → managed settings. Style, compliance reminders, behavioral instructions → managed CLAUDE.md.
  - Why it works: settings are enforced by the client; CLAUDE.md shapes behavior but isn't a hard enforcement layer.
- **CLAUDE.md-or-AGENTS.md default (`claude-md-or-agents-md`)**:
  - Rule: Claude reads `AGENTS.md` only when no `CLAUDE.md`, `.claude/CLAUDE.md`, or `CLAUDE.local.md` exists in the working directory or above.
  - Doesn't count (still loads alongside AGENTS.md): `~/.claude/CLAUDE.md`, managed CLAUDE.md, `.claude/rules/` files.
  - Failure mode: adding a personal `CLAUDE.local.md` to an AGENTS.md-based repo silently switches Claude off AGENTS.md. Fix: set Project instructions to `claude-md-and-agents-md`.
- **Single shared file via import**: keep `AGENTS.md` as the cross-tool source; add `CLAUDE.md` containing `@AGENTS.md` plus Claude-specific lines below it.
  - When to use: repo also needs a CLAUDE.md, Project instructions is `claude-md`, or the session can't load AGENTS.md directly.
  - Why it works: imports never double-load AGENTS.md under any setting; prefer import over symlink when anyone uses Windows.

## Key Concepts
- **Managed CLAUDE.md**: file at the managed policy path; applies to every session on the machine; cannot be excluded.
- **`claudeMd` managed setting**: CLAUDE.md content inline in `managed-settings.json`; same precedence as the managed file (loads before user and project); ignored in user/project/local settings.
- **`claudeMdExcludes`**: glob list matched against absolute paths to skip CLAUDE.md/rules files; valid at user, project, local, or managed layer; arrays merge across layers.
- **Project instructions setting**: `/config` option choosing `claude-md-or-agents-md` (default), `claude-md-and-agents-md`, `claude-md`, or `managed-only`.
- **`cc-plugin-agents-md@builtin`**: built-in plugin ID that reads AGENTS.md; configure under `pluginConfigs` (was `agents-md@builtin` before v2.1.285).
- **AGENTS.md files read**: every `AGENTS.md` and `.claude/AGENTS.md` in cwd and ancestors at start; subdirectory AGENTS.md when Claude Reads a file there and that subdir has no CLAUDE.md of its own.
- **Not read**: `AGENTS.local.md`, `AGENTS.override.md`, anything under `.agents/`.
- **`/import`**: one-time copy of another agent's config (instruction files appended to matching CLAUDE.md, plus MCP servers, commands, subagents, skills); v2.1.213+.

## Mental Models
- Think of the managed CLAUDE.md as **the org's voice that nobody can mute** — but still only a voice; `permissions.deny` is the lock.
- Think of `CLAUDE.local.md` as **a CLAUDE.md for AGENTS.md-detection purposes**: its mere existence flips the default.
- Use `claudeMdExcludes` in `.claude/settings.local.json` when the noise is your problem only; in project settings when the whole team should skip it.
- Use the import (`@AGENTS.md`) when portability matters; the symlink only when nobody is on Windows and nobody needs Claude-specific additions.

## Anti-patterns
- **Putting enforcement in managed CLAUDE.md** ("never push to main"): advisory only; pair with `permissions.deny` or hooks.
- **Setting `claudeMd` in user/project/local settings**: no effect.
- **Trying to exclude the managed CLAUDE.md**: impossible by design.
- **A CLAUDE.md that says "read AGENTS.md" in words**: Claude sees it only if it chooses to open the file; use `@AGENTS.md` or delete the CLAUDE.md.
- **Keeping a `SessionStart` hook that prints AGENTS.md** after native support: duplicates the content in context.
- **Committing a `CLAUDE.md` → `AGENTS.md` symlink in a Windows-touched repo**: without `core.symlinks`, the clone gets a one-line text file instead of instructions.
- **Setting `pluginConfigs` for AGENTS.md in project/local settings**: ignored; only `~/.claude/settings.json`, `--settings`, or managed settings count.

## Code Examples
```json
{
  "claudeMd": "Always run `make lint` before committing.\nNever push directly to main."
}
```
- **What it demonstrates**: managed behavioral guidance without deploying a file (managed/policy settings only).

```json
{
  "claudeMdExcludes": [
    "**/monorepo/CLAUDE.md",
    "/home/user/monorepo/other-team/.claude/rules/**"
  ]
}
```
- **What it demonstrates**: skipping an ancestor CLAUDE.md and another team's rules; place in `.claude/settings.local.json` to keep it personal. For symlinked rules, a pattern matching either the `.claude/rules/` path or the link target excludes it (v2.1.239+).

```json
{
  "pluginConfigs": {
    "cc-plugin-agents-md@builtin": {
      "options": { "instructionFiles": "claude-md-and-agents-md" }
    }
  }
}
```
- **What it demonstrates**: setting Project instructions from a settings file; applies from the next message and in new sessions.

```markdown
@AGENTS.md

## Claude Code

Use plan mode for changes under `src/billing/`.
```
- **What it demonstrates**: a CLAUDE.md that shares AGENTS.md and adds Claude-only guidance (imported content is read first).

## Reference Tables

**Managed settings vs managed CLAUDE.md**
| Concern | Configure in |
|---|---|
| Block tools, commands, file paths | Managed settings: `permissions.deny` |
| Enforce sandbox isolation | Managed settings: `sandbox.enabled` |
| Env vars, API provider routing | Managed settings: `env` |
| Login method / org restriction | Managed settings: `forceLoginMethod`, `forceLoginOrgUUID` |
| Code style, quality guidelines | Managed CLAUDE.md |
| Data handling, compliance reminders | Managed CLAUDE.md |
| Behavioral instructions | Managed CLAUDE.md |

**What Claude reads by default**
| Repository has | Claude reads |
|---|---|
| `AGENTS.md`, no `CLAUDE.md`/`CLAUDE.local.md` in cwd or above | `AGENTS.md` |
| `AGENTS.md` and a `CLAUDE.md`/`CLAUDE.local.md` | `CLAUDE.md` files only |
| `CLAUDE.md` importing `AGENTS.md` | `CLAUDE.md` with `AGENTS.md` via import |

**Project instructions values**
| Value | Reads |
|---|---|
| `claude-md-or-agents-md` (default) | CLAUDE.md files, or AGENTS.md when none exist |
| `claude-md-and-agents-md` | Both; per directory CLAUDE.md first, AGENTS.md after; no double-load |
| `claude-md` | CLAUDE.md only |
| `managed-only` | Managed CLAUDE.md + auto memory at launch; subdirectory CLAUDE.md, subdir rules, path-scoped rules still load on demand |

**AGENTS.md read directly vs CLAUDE.md**
| | CLAUDE.md | AGENTS.md via setting |
|---|---|---|
| `InstructionsLoaded` hooks | Fire | Don't fire (do fire if imported/symlinked from CLAUDE.md) |
| `--add-dir` + `CLAUDE_CODE_ADDITIONAL_DIRECTORIES_CLAUDE_MD` | Loads | Doesn't load |
| External `@path` import | Approval prompt | Loads only if already approved; no prompt |

**AGENTS.md support unavailable when**: version < v2.1.277; built-in plugin disabled via `/plugin`; sometimes the first session after upgrading from ≤ v2.1.276; before v2.1.281, some Bedrock / telemetry-disabled sessions. Then Project instructions is absent from `/config` — use `@AGENTS.md` import.

**Migration**: `/init` reads `.cursor/rules/`, `.cursorrules`, `.github/copilot-instructions.md`; with `CLAUDE_CODE_NEW_INIT=1` also `AGENTS.md`, `.devin/rules/`, `.windsurf/rules/`, `.windsurfrules`, `.clinerules`.

## Worked Example
Situation: a repo uses `AGENTS.md` for Codex and Cursor. A developer adds `CLAUDE.local.md` with sandbox URLs, and Claude suddenly ignores the team conventions.

1. Diagnose: `CLAUDE.local.md` counts as a CLAUDE.md under `claude-md-or-agents-md`, so AGENTS.md stopped loading.
2. Option A (personal): `/config` → Project instructions → `claude-md-and-agents-md`. Each directory's CLAUDE.md files load, then AGENTS.md.
3. Option B (team-wide, robust across versions and Windows): commit a `CLAUDE.md`:
```markdown
@AGENTS.md

## Claude Code
Use plan mode for changes under `src/billing/`.
```
4. Clean up: delete any old `SessionStart` hook that cat'd AGENTS.md (would duplicate it).
5. Verify: `/memory` lists the AGENTS.md path; `/context` shows `CLAUDE.md` under **Memory files**.
6. Org layer: security adds `"permissions": {"deny": [...]}` in managed settings for hard blocks, and a `claudeMd` string for "run `make lint` before committing".

## Key Takeaways
1. Managed CLAUDE.md (or `claudeMd` in managed settings) loads first and can't be excluded; it's behavioral, not enforcement.
2. Use managed settings (`permissions.deny`, `sandbox.enabled`, `env`, `forceLoginMethod`) for anything that must hold.
3. `claudeMdExcludes` takes absolute-path globs, merges across layers, can't touch managed files.
4. AGENTS.md loads natively (v2.1.277+) only when no `CLAUDE.md`, `.claude/CLAUDE.md`, or `CLAUDE.local.md` is on the path, unless set to `claude-md-and-agents-md`.
5. `@AGENTS.md` in CLAUDE.md is the portable, never-double-loaded way to share one file across tools.
6. `/init` and `/import` migrate other tools' instruction files.

## Connects To
- **ch01**: location table and managed policy paths.
- **ch02**: import mechanics and external-import approval reused by AGENTS.md.
- **ch04**: "My AGENTS.md isn't loading" checklist and `managed-only` interplay with auto memory.
- **ch10**: subagents that skip project instructions also skip AGENTS.md.
- **ch14**: hooks (`SessionStart`, `InstructionsLoaded`) referenced in AGENTS.md cleanup and debugging.
