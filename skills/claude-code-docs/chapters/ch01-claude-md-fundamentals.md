# Chapter 01: CLAUDE.md Fundamentals — Memory Systems, Locations, and Writing Instructions

## Core Idea
Every session starts with an empty context window; CLAUDE.md files (written by you) and auto memory (written by Claude) are the two mechanisms that carry knowledge forward. Both are loaded as *context, not enforced configuration*, so adherence depends on how concrete, short, and consistent your instructions are.

## Frameworks Introduced
- **CLAUDE.md vs auto memory split**: you write CLAUDE.md for instructions and rules; Claude writes auto memory for learnings and patterns. Both load at the start of every conversation.
  - When to use: CLAUDE.md for coding standards, workflows, project architecture; auto memory for your preferences, corrections, and project context Claude can't derive from the code.
  - How: put anything you want to *guide* behavior into CLAUDE.md; let auto memory capture corrections without manual effort (see ch04).
  - Why it works / failure mode: neither is enforcement. To block an action regardless of what Claude decides, use a `PreToolUse` hook (ch14–ch16), not a CLAUDE.md line.
- **"Write down what you'd otherwise re-explain" trigger list**: add to CLAUDE.md when
  1. Claude makes the same mistake a second time
  2. A code review catches something Claude should have known about this codebase
  3. You type the same correction/clarification you typed last session
  4. A new teammate would need the same context to be productive
  - Filter: keep only facts Claude needs in *every* session (build commands, conventions, project layout, "always do X" rules). Multi-step procedures → a skill (ch05). Rules that matter for one part of the codebase → a path-scoped rule (ch02).
- **Verifiable-instruction rule**: write instructions concrete enough to check.
  - How: replace vague goals with observable actions — "Use 2-space indentation" not "Format code properly"; "Run `npm test` before committing" not "Test your changes"; "API handlers live in `src/api/handlers/`" not "Keep files organized".
  - Why it works: vague or conflicting instructions are where compliance drops; concrete ones are followable and auditable.
- **Size / Structure / Consistency checklist**:
  - **Size**: target under 200 lines per CLAUDE.md. Longer files cost more context and reduce adherence. Imports organize but do *not* reduce cost (imported files load at launch).
  - **Structure**: markdown headers and bullets beat dense paragraphs.
  - **Consistency**: contradictory instructions → Claude may pick one arbitrarily. Periodically review CLAUDE.md, nested CLAUDE.md files, and `.claude/rules/`, or run `/doctor prompt-audit`.

## Key Concepts
- **CLAUDE.md**: plain-markdown instruction file Claude reads at session start; scope can be org, user, project, or local.
- **Auto memory**: notes Claude writes itself, per repository, shared across worktrees; loads first 200 lines or 25KB of `MEMORY.md`.
- **Managed policy CLAUDE.md**: org-wide file at an OS-specific system path, deployed by IT/DevOps; applies to all users on the machine.
- **CLAUDE.local.md**: personal, project-specific instructions; gitignore it.
- **Load order**: broadest to most specific — managed → user → project → local — so project instructions appear *after* user instructions in context.
- **`/init`**: generates a starter CLAUDE.md from codebase analysis; if one exists, suggests improvements instead of overwriting.
- **`CLAUDE_CODE_NEW_INIT=1`**: makes `/init` an interactive multi-phase flow (choose CLAUDE.md files, skills, hooks; subagent exploration; follow-up questions; reviewable proposal before writing).
- **`/context` → Memory files**: where you confirm which CLAUDE.md files loaded at launch.
- **`/doctor prompt-audit`**: report of outdated/conflicting/broken instructions with proposed edits; changes nothing until you ask.

## Mental Models
- Think of CLAUDE.md as **an onboarding note for a teammate with amnesia**: only the facts they'd need every single day, nothing they could read from the code.
- Think of CLAUDE.md as **advice, hooks as law**: if violating it must be impossible, it belongs in a hook or `permissions.deny`, not in prose.
- Use CLAUDE.md when the fact is global and stable; use a path-scoped rule when it only matters for some files; use a skill when it's a procedure you invoke.
- Treat every line as a recurring context tax paid in every session — the 200-line target is a budget, not a suggestion.

## Anti-patterns
- **Vague directives** ("format code nicely"): unverifiable, so Claude can't reliably comply.
- **Encoding hard constraints as prose**: CLAUDE.md is context; a `PreToolUse` hook is what actually blocks.
- **Stuffing procedures and subsystem-specific rules into the root file**: inflates every session; move to skills or path-scoped rules.
- **Splitting a bloated file into imports to "shrink" it**: imports load at launch; context cost is unchanged.
- **Letting contradictions accumulate across root, nested, and rules files**: Claude picks one arbitrarily.
- **Personal preferences in the shared project CLAUDE.md**: it's committed for the team; use `CLAUDE.local.md` or `~/.claude/CLAUDE.md`.

## Code Examples
```text
/doctor prompt-audit
/doctor prompt-audit .claude/skills/deploy
```
- **What it demonstrates**: whole-setup audit (CLAUDE.md, CLAUDE.local.md, AGENTS.md, plus rules, skills, commands, subagents, output styles under `.claude/` and `~/.claude/`) vs auditing one path. Runs through the bundled `/claude-api` skill, so it's unavailable if that skill is disabled via `skillOverrides` or `disableBundledSkills`. Requires v2.1.283+.

```json
{
  "env": { "CLAUDE_CODE_NEW_INIT": "1" }
}
```
- **What it demonstrates**: persisting the interactive `/init` flow via a settings `env` block; it only changes how `/init` runs, so it's safe to leave set.

## Reference Tables

**CLAUDE.md vs auto memory**
| | CLAUDE.md files | Auto memory |
|---|---|---|
| Who writes it | You | Claude |
| Contains | Instructions and rules | Learnings and patterns |
| Scope | Project, user, or org | Per repository, shared across worktrees |
| Loaded into | Every session | Every session (first 200 lines or 25KB) |
| Use for | Coding standards, workflows, architecture | Preferences, corrections, context not derivable from code |

**CLAUDE.md locations (load order: broadest → most specific)**
| Scope | Location | Shared with |
|---|---|---|
| Managed policy | macOS `/Library/Application Support/ClaudeCode/CLAUDE.md`; Linux/WSL `/etc/claude-code/CLAUDE.md`; Windows `C:\Program Files\ClaudeCode\CLAUDE.md` | All users in org |
| User | `~/.claude/CLAUDE.md` | Only you, all projects |
| Project | `./CLAUDE.md` or `./.claude/CLAUDE.md` (or `./AGENTS.md`, see ch03) | Team via source control |
| Local | `./CLAUDE.local.md` (add to `.gitignore`) | Only you, this project |

Files in the hierarchy *above* the working directory load at launch; files in subdirectories load on demand (ch02).

**Vague → verifiable**
| Instead of | Write |
|---|---|
| Format code properly | Use 2-space indentation |
| Test your changes | Run `npm test` before committing |
| Keep files organized | API handlers live in `src/api/handlers/` |

## Worked Example
Situation: in two sessions Claude ran `npm install` in a pnpm repo, and a reviewer flagged that a new endpoint skipped the shared error format.

1. Trigger check: same mistake twice + review catch → both qualify for CLAUDE.md.
2. Scope check: the package-manager rule applies everywhere → root CLAUDE.md. The error-format rule only matters under `src/api/` → path-scoped rule (ch02), not the root file.
3. Run `/init` to bootstrap if no file exists, then trim and add:

```markdown
# Build & test
- Use pnpm, never npm or yarn: `pnpm install`, `pnpm test`
- Run `pnpm test` before committing

# Layout
- API handlers live in `src/api/handlers/`
- Shared UI components live in `src/components/`

# Conventions
- Use 2-space indentation
```
4. Commit it as `./CLAUDE.md`. Put your personal sandbox URL in `./CLAUDE.local.md` and gitignore it.
5. Start a new session, run `/context`, confirm `CLAUDE.md` appears under **Memory files**.
6. Monthly: `/doctor prompt-audit` to catch stale commands or contradictions with `.claude/rules/`.

## Key Takeaways
1. CLAUDE.md and auto memory both load every session, but both are context — use hooks for enforcement.
2. Add to CLAUDE.md on repeat mistakes, review catches, repeated corrections, or onboarding needs.
3. Keep each file under ~200 lines; move partial-scope rules to `.claude/rules/` and procedures to skills.
4. Write verifiable instructions; contradictions cause arbitrary choices.
5. Locations load managed → user → project → local; verify with `/context`.
6. Bootstrap with `/init` (or `CLAUDE_CODE_NEW_INIT=1`), audit with `/doctor prompt-audit`.

## Connects To
- **ch02**: imports, exact load mechanics, and `.claude/rules/` path scoping that keep CLAUDE.md small.
- **ch03**: managed CLAUDE.md, `claudeMdExcludes`, and AGENTS.md as an alternative project file.
- **ch04**: the auto memory half of the system and troubleshooting adherence.
- **ch05**: skills as the home for multi-step procedures that don't belong in CLAUDE.md.
- **ch14**: hooks (`PreToolUse`) for rules that must be enforced, not suggested.
