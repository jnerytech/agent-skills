# Chapter 02: CLAUDE.md Loading, Imports, and `.claude/rules/`

## Core Idea
CLAUDE.md content is assembled, not overridden: ancestor files load at launch and concatenate root-down, subdirectory files and path-scoped rules load lazily when Claude touches matching files, and `@path` imports splice extra files in. Use rules and lazy loading to keep always-on context small; imports only organize.

## Frameworks Introduced
- **Concatenation load order**: all discovered files are concatenated, never overridden.
  - How: Claude Code walks from the working directory up to the filesystem root and loads every `CLAUDE.md` and `CLAUDE.local.md`. Order in context is filesystem root → working directory, so files closer to where you launched are read *last*. Within one directory, `CLAUDE.local.md` is appended after `CLAUDE.md`.
  - Subdirectories below the working directory: their `CLAUDE.md`/`CLAUDE.local.md` load on demand, once Claude reads, writes, or edits a file in that subdirectory (including a Bash `cat`/`head` on a single file, which counts as a read).
  - Failure mode: because nothing overrides, a conflicting ancestor instruction still sits in context; fix with `claudeMdExcludes` (ch03) or by removing the conflict.
- **`@path` import rules**:
  - Relative paths resolve relative to the *importing file*, not the working directory; absolute and `~/` paths allowed.
  - Recursive imports up to a maximum depth of **four hops**.
  - Spaces: escape each with a backslash (`@Design\ Docs/api.md`). Unescaped, the path ends at the first space. Quoted paths are never imported.
  - Imports inside Markdown code spans or fenced blocks are skipped — wrap in backticks to mention a path literally.
  - External imports (resolving outside the working directory) in a project-level file trigger a one-time approval dialog; declining disables them permanently for that project. User-scope files (`~/.claude/CLAUDE.md`, `~/.claude/rules/`) load imports without the dialog (except Cowork desktop sessions).
- **Path-scoped rules**: a rule file with `paths` frontmatter loads only when Claude works with matching files.
  - When to use: instructions that matter for one file type or subtree (API conventions, test conventions).
  - How: put one topic per `.md` file in `.claude/rules/` (discovered recursively); add `paths:` globs. Triggers: Read, Write, or Edit tool on a matching file, or a Bash read like `cat`/`head`; symlinked checkout paths match too.
  - Why it works: zero context cost until relevant. Failure mode: rules without `paths` load at launch with the same priority as `.claude/CLAUDE.md`, so an unscoped rule is just a CLAUDE.md split.

## Key Concepts
- **Lazy-loaded CLAUDE.md**: a subdirectory CLAUDE.md that loads when Claude first touches a file in that subdirectory.
- **HTML comment stripping**: block-level `<!-- ... -->` comments are removed before injection — free maintainer notes; comments inside code blocks are preserved; Read tool still shows them.
- **`--add-dir`**: grants access to extra directories; their CLAUDE.md files do *not* load unless `CLAUDE_CODE_ADDITIONAL_DIRECTORIES_CLAUDE_MD=1`.
- **`CLAUDE.local.md` across worktrees**: gitignored, so it exists only in the worktree where you created it; import `@~/.claude/...` instead to share personal notes across worktrees.
- **Rule frontmatter**: `paths` is the only field read; others are ignored silently; frontmatter is stripped before loading.
- **Brace-expansion budget**: a rule's whole `paths` list shares 1,000 expanded patterns and 4 MiB; over-budget patterns are used unexpanded (literal braces match nothing).
- **User-level rules**: `~/.claude/rules/` apply to every project; load before project rules; neither overrides the other.
- **Symlinked rules**: supported; circular links handled; a target outside the working directory is treated as an external import and needs approval — and after approval only rules *without* `paths` load from it.
- **`--setting-sources`**: excluding `project` skips project rules (including on-demand rules since v2.1.211); excluding `local` skips `CLAUDE.local.md` from added dirs.

## Mental Models
- Think of the CLAUDE.md stack as **one long document assembled root-down**, with the most local notes last — "last" means read later, not "wins".
- Use imports when you want **organization or a shared single source** (README, package.json, AGENTS.md); use path-scoped rules when you want **lower context cost**.
- Think of a path-scoped rule as **a CLAUDE.md that only wakes up when Claude opens a matching file**.
- Use `~/.claude/rules/` instead of symlinking shared rules into projects when you want them everywhere without an approval dialog.

## Anti-patterns
- **Expecting a deeper CLAUDE.md to override a parent**: both stay in context; conflicts resolve arbitrarily.
- **Quoting import paths with spaces** (`@"Design Docs/x.md"`): never imported; use backslash escapes.
- **Mentioning a path with a bare `@`**: it gets imported; wrap in backticks to keep it literal.
- **Symlinking rules from a network path** (`\\server\share`, `/net`, `/Network`): not followed, rules silently don't load (`\\wsl$` is fine).
- **Symlinked external rules with `paths`**: even after approval only unscoped ones load.
- **Invalid globs with a bare `[`** (`photos [2024/**`): matches nothing; escape as `photos \[2024/**`.
- **Heavy brace expansion** (`{a,b}/{c,d}/*.{ts,tsx}` = 8 patterns): eats the 1,000-pattern budget; over-budget patterns silently match nothing.
- **Malformed YAML frontmatter**: ignored, rule loads as unscoped (always-on); check with `claude --debug`.

## Code Examples
```text
See @README for project overview and @package.json for available npm commands for this project.

# Additional Instructions
- git workflow @docs/git-instructions.md
- API conventions @Design\ Docs/api-conventions.md

# Individual Preferences
- @~/.claude/my-project-instructions.md
```
- **What it demonstrates**: inline imports, a backslash-escaped space, and a home-directory import (external → approval dialog in a project file) that shares personal notes across worktrees.

```markdown
---
paths:
  - "src/**/*.{ts,tsx}"
  - "lib/**/*.ts"
  - "tests/**/*.test.ts"
---

# API Development Rules
- All API endpoints must include input validation
- Use the standard error response format
```
- **What it demonstrates**: multiple globs plus brace expansion; `paths` also accepts a comma-separated string.

```bash
CLAUDE_CODE_ADDITIONAL_DIRECTORIES_CLAUDE_MD=1 claude --add-dir ../shared-config
ln -s ~/shared-claude-rules .claude/rules/shared
ln -s ~/company-standards/security.md .claude/rules/security.md
```
- **What it demonstrates**: loading memory from an added dir (`CLAUDE.md`, `.claude/CLAUDE.md`, `.claude/rules/*.md`, `CLAUDE.local.md`) and sharing rules via symlinks (directory and single file).

## Reference Tables

**When each file loads**
| File | Loads |
|---|---|
| `CLAUDE.md` / `CLAUDE.local.md` in cwd and ancestors | At launch, root → cwd, local after main per dir |
| `CLAUDE.md` / `CLAUDE.local.md` in subdirectories | On demand when Claude reads/writes/edits a file there |
| `@path` imports | At launch with the importing file (max 4 hops) |
| `.claude/rules/*.md` without `paths` | At launch, same priority as `.claude/CLAUDE.md` |
| `.claude/rules/*.md` with `paths` | When Read/Write/Edit (or Bash read) touches a match |
| `~/.claude/rules/*.md` | Before project rules, every project |
| Added dirs (`--add-dir`) | Only with `CLAUDE_CODE_ADDITIONAL_DIRECTORIES_CLAUDE_MD=1` |

**Glob patterns**
| Pattern | Matches |
|---|---|
| `**/*.ts` | All TypeScript files anywhere |
| `src/**/*` | Everything under `src/` |
| `*.md` | Markdown files in project root |
| `src/components/*.tsx` | Components in one directory |

**Rule frontmatter**
| Field | Required | Description |
|---|---|---|
| `paths` | No | Globs scoping the rule; YAML list or comma-separated string |

## Worked Example
Goal: a 350-line root CLAUDE.md is hurting adherence in a TS monorepo with an API and a React frontend.

1. Classify lines: global facts (build commands, package manager, layout) stay; API conventions (90 lines) and React conventions (80 lines) are subsystem-specific.
2. Create rules:
```text
.claude/
├── CLAUDE.md               # ~120 lines of global facts
└── rules/
    ├── backend/api.md      # paths: "src/api/**/*.ts"
    └── frontend/react.md   # paths: "src/components/**/*.tsx"
```
3. Keep the testing rule unscoped only if it truly applies everywhere; otherwise scope to `"**/*.test.ts"`.
4. Replace a duplicated overview with `See @README for project overview` — accepting that it still loads at launch.
5. Leave reviewer notes as `<!-- why this rule exists: incident 2024-03 -->`; they cost no tokens.
6. Verify: `/context` shows only `CLAUDE.md` under **Memory files** at launch; open `src/api/users.ts` and the API rule loads (log it with an `InstructionsLoaded` hook if unsure).

## Key Takeaways
1. Files concatenate root → cwd; local after main; nothing overrides anything.
2. Subdirectory CLAUDE.md and `paths` rules load lazily on file access — the main tool for cutting context.
3. Imports: relative to the importing file, 4-hop max, escape spaces, backticks to suppress, external ones need one-time approval.
4. Rules without `paths` are always-on; `paths` is the only frontmatter field read.
5. Brace expansion budget: 1,000 patterns / 4 MiB per rule; escape literal `[`.
6. `--add-dir` directories need `CLAUDE_CODE_ADDITIONAL_DIRECTORIES_CLAUDE_MD=1` to contribute memory.

## Connects To
- **ch01**: the size/consistency targets that motivate splitting into rules.
- **ch03**: `claudeMdExcludes` for unwanted ancestor files; AGENTS.md uses the same import mechanics.
- **ch04**: `InstructionsLoaded` hook and `/context` for debugging what loaded; compaction behavior of nested files and rules.
- **ch06**: skills as the on-demand alternative to always-loaded rules.
