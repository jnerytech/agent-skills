# Chapter 05: Skills — Bundled Skills, Your First Skill, Where Skills Load

## Core Idea
A skill is a `SKILL.md` file (frontmatter + Markdown instructions) that Claude loads on demand or that you run as `/skill-name`. Its body costs context only when used, so a skill is where repeated procedures go. Where you save it decides which sessions see it and which copy wins a name clash.

## Frameworks Introduced
- **Skill vs CLAUDE.md test**: put *facts* in CLAUDE.md and *procedures* in a skill.
  - When to use: you keep pasting the same checklist or multi-step procedure into chat, or a CLAUDE.md section has turned into a procedure.
  - How: move it into `<location>/.claude/skills/<name>/SKILL.md`, write a `description` that names the trigger situations, and keep the body short.
  - Why it works: only the name and description sit in context every turn. The body loads only when the skill is invoked. Failure mode: leaving the procedure in CLAUDE.md, where it costs tokens on every turn.
- **Location ladder (scope decides reach)**: Enterprise → Personal → Project → Nested → Additional dir → Plugin → claude.ai account.
  - When to use: deciding where to save a skill.
  - How: `~/.claude/skills/` for you on every project on this machine. Commit `.claude/skills/` for the team. Use a plugin or managed settings for an org. Enable the skill on claude.ai for Cowork, cloud sessions and routines.
  - Failure mode: a personal-only skill invoked from a routine or cloud session reports "skill not found", because those sessions never read your local `~/.claude/skills/`.
- **Name-collision resolution**: Enterprise beats personal, and personal beats project. A skill beats a `.claude/commands/` file. Your skill replaces a bundled skill or built-in command but **not its aliases**. Plugin skills never collide because they are namespaced. A synced claude.ai skill loses its short name to any other command.

## Key Concepts
- **Bundled skills**: prompt-based skills that ship with Claude Code (`/doctor`, `/code-review`, `/batch`, `/debug`, `/loop`, `/claude-api`, `/run`, `/verify`, `/run-skill-generator`, `/simplify`). Turn them off with `disableBundledSkills`.
- **Custom commands merged into skills**: `.claude/commands/deploy.md` and `.claude/skills/deploy/SKILL.md` both create `/deploy`. Command files still work, but they don't support `name`, `paths` or supporting files.
- **Nested skills**: `<subdir>/.claude/skills/` loads the first time Claude reads or edits a file in that subdir, or right away with `/add-dir` (v2.1.257+). A name clash with a root skill exposes `/apps/web:deploy`.
- **Parent discovery**: Claude Code loads project skills from the start directory up to the repo root. In a git worktree it stops at the worktree root. From v2.1.277, if the worktree has no `.claude/skills`, it falls back to the main checkout's skills.
- **`--add-dir` loading**: an added directory contributes `.claude/skills/`, `.claude/commands/` and `.claude/agents/`. The `permissions.additionalDirectories` setting grants file access only and loads none of them.
- **Synced skills**: claude.ai account skills download to `~/.claude/skills/synced/` (terminal sync needs v2.1.273+). Sync is download-only and checks about every 10 min while active and about every 40 min while idle. `CLAUDE_CODE_SYNC_SKILLS=1` makes a `-p` run wait for the download. `syncClaudeAiSkills: false` stops syncing.
- **Reserved names**: Claude Code skips folders named `synced` (any case) and anything named `anthropic-skills` or `anthropic-skills:*`, apart from plugins.
- **Live change detection**: edits under watched `.claude/skills/` dirs apply mid-session, except in bare mode. A newly created top-level skills dir needs `/reload-skills`. A skill-folder-as-plugin needs `/reload-plugins` for `hooks/`, `.mcp.json`, `agents/` and `output-styles/`.
- **Skill folder as plugin**: adding `.claude-plugin/plugin.json` to a skill folder loads it as plugin `<name>@skills-dir`, which can carry agents, hooks and MCP servers. In a project this requires accepting workspace trust.

## Mental Models
- Think of the skill directory name as the default command name. The frontmatter `name` can override it, and the directory name keeps working as a second name.
- Use `/doctor` to check your **setup** (installs, extensions' context cost, CLAUDE.md duplication, permissions). Use `/doctor prompt-audit` (v2.1.283+) to check your **instructions** for conflicts and staleness. Use `claude doctor` in a shell for read-only diagnostics without a session.
- Think of `/run-skill-generator` as recording the launch recipe once. It writes `.claude/skills/run-<name>/` so `/run`, `/verify` and other agents stop re-inferring how to start your app. Re-run it when the build or launch changes.
- A skill named `verify` or `simplify` at an enterprise/personal/project/add-dir location (v2.1.286+) makes Claude run it before each commit, except docs/test-only commits. This needs Claude to be able to invoke it (no `disable-model-invocation`) and needs `includeGitInstructions` left on. Bundled, plugin and claude.ai copies don't count.

## Anti-patterns
- **Naming a skill `synced` or `anthropic-skills…`**: it silently doesn't load, or a startup notice tells you to rename it.
- **Expecting `/review` to run your `code-review` override**: aliases always run the bundled or built-in command, never your replacement.
- **Editing files under `~/.claude/skills/synced/`**: sync is download-only, so the next sync overwrites or removes your edits. Change the skill on claude.ai instead.
- **Deleting a synced skill's folder by hand**: it re-downloads while the skill stays enabled on claude.ai. Turn it off there.
- **Relying on `permissions.additionalDirectories` to share skills**: it grants file access only. Use `--add-dir` / `/add-dir`.

## Code Examples
```bash
mkdir -p ~/.claude/skills/summarize-changes
```
```yaml
---
description: Summarizes uncommitted changes and flags anything risky. Use when the user asks what changed, wants a commit message, or asks to review their diff.
---

## Current changes

!`git diff HEAD`

## Instructions

Summarize the changes above in two or three bullet points, then list any risks you notice such as missing error handling, hardcoded values, or tests that need updating. If the diff is empty, say there are no uncommitted changes.
```
- **What it demonstrates**: a minimal skill. The description holds the trigger phrases, and `` !`git diff HEAD` `` injects live data before Claude reads the skill (see ch08). No `name` is set, so the directory name gives `/summarize-changes`.

## Reference Tables

| Location | Path | Loads in |
|---|---|---|
| Enterprise | `.claude/skills/<name>/SKILL.md` in managed settings dir (e.g. `/etc/claude-code/`) | All users on that machine |
| Personal | `~/.claude/skills/<name>/SKILL.md` | All your projects on this machine; **not** Cowork/cloud |
| Project | `.claude/skills/<name>/SKILL.md` | This repo (commit it) |
| Nested | `<subdir>/.claude/skills/<name>/SKILL.md` | Sessions in/below subdir, or once Claude touches files there |
| Additional dir | `.claude/skills/...` in an `--add-dir` dir | That session |
| Plugin | `<plugin>/skills/<name>/SKILL.md` | Where plugin enabled, as `/plugin-name:skill-name` |
| claude.ai account | enabled on account | Cowork, cloud, signed-in terminal sessions |

| Same name in | Which runs |
|---|---|
| Enterprise / personal / project | Enterprise > personal > project |
| Your skill + bundled skill | Yours replaces it, but not its aliases (`/review` stays bundled) |
| Your skill + built-in command | Yours replaces it in local terminal, aliases stay built-in (`/cost`) |
| Skill + `.claude/commands/` file | The skill |
| Root + nested | Both load (`/deploy` and `/apps/web:deploy`) |
| Plugin + any | Both (namespaced) |
| Anything + synced short name | The other; synced runs only as `/anthropic-skills:<name>` |

| How to remove | Action |
|---|---|
| Personal/project | Delete the directory (drops from `/skills` live) |
| Enterprise | Admin deletes it from the managed dir |
| Plugin | Disable or `/plugin uninstall <plugin>@<marketplace>` |
| Synced | Turn it off on claude.ai |
| Bundled | `disableBundledSkills: true`, or `skillOverrides` `"off"` |
| Keep but stop auto-use | `disable-model-invocation: true` or `skillOverrides` `"user-invocable-only"` |

`/claude-api` subcommands: `migrate`, `upgrade` (v2.1.236+), `managed-agents-onboard [<url>|<quickstart-name>]`, `prompt-audit` (v2.1.221+), `cost-optimize` (v2.1.247+), `build-eval` / `hillclimb` (v2.1.259+), `preserved-thinking-migration` (v2.1.282+). The skill auto-activates when your code imports `anthropic` or `@anthropic-ai/sdk`.

## Worked Example
Goal: your team needs one launch recipe in a monorepo, plus a personal diff summarizer.
1. Personal helper: create `~/.claude/skills/summarize-changes/SKILL.md` as shown above. Test it by asking "What did I change?" (auto-invoke) and by typing `/summarize-changes` (direct).
2. Team launch recipe: run `/run-skill-generator` once. It brings the app up from a clean env and commits `.claude/skills/run-web/`. From then on, `/verify` follows that recipe. If `/verify` had to work out the launch itself, it writes `.claude/skills/verify/SKILL.md` at the repo root, and that copy replaces the bundled `/verify`. Because it is a project skill named `verify`, Claude now runs it before each commit (v2.1.286+).
3. Package override: `apps/web/.claude/skills/deploy/` collides with the root `deploy`. `/deploy` runs the root skill and `/apps/web:deploy` runs the nested one. Claude is told to pick the variant whose directory holds the files it's editing.
4. Routines: the routine fails with "skill not found" for `summarize-changes`. Fix it by enabling the skill on claude.ai, or by committing it to the repo's `.claude/skills/`.

## Key Takeaways
1. A skill is a directory with `SKILL.md`. The directory name (or `name`) is the command, and `description` drives auto-loading.
2. Personal skills don't reach Cowork, cloud sessions or routines. Commit them to the repo or enable them on claude.ai.
3. Precedence is enterprise > personal > project, and skill > command file. Overrides never capture aliases.
4. Nested skills load lazily. Use `/add-dir` to load them early, and `/reload-skills` for a newly created top-level dir.
5. Synced skills are download-only, run only by their full name when the short name is taken, and land in `~/.claude/skills/.trash/` when removed.
6. `/run-skill-generator` and the `verify` recipe make app launch reproducible, and a `verify`/`simplify` project skill runs before each commit.

## Connects To
- **ch06**: frontmatter fields (`name`, `description`) and how a skill gets its command name.
- **ch07**: `disable-model-invocation` / `user-invocable` and the content lifecycle.
- **ch08**: `` !`cmd` `` injection used in the first skill, and `skillOverrides`.
- **ch09**: evaluating, sharing and troubleshooting skills (missing skills, `.trash`).
- **ch01**: when content belongs in CLAUDE.md rather than a skill.
