# Chapter 06: Skill Content, Frontmatter Reference, and Supporting Files

## Core Idea
A `SKILL.md` is YAML frontmatter that controls *when and how* the skill runs, followed by a Markdown body that says *what to do*. Every frontmatter field is optional and Claude Code ignores misspelled ones without warning. Keep the body short and move bulk into supporting files that load only when needed.

## Frameworks Introduced
- **Reference vs Task content**: decide how the skill will be invoked before writing it.
  - When to use: at the start of every skill.
  - How: *Reference* content (conventions, style guides, domain knowledge) runs inline next to the conversation, so let Claude auto-load it. *Task* content (deploy, commit, codegen) is step-by-step and has side effects, so add `disable-model-invocation: true` and often `context: fork`.
  - Failure mode: putting reference-only content under `context: fork` hands the subagent guidelines but no task, so it returns nothing useful.
- **Progressive disclosure via supporting files**: `SKILL.md` is the overview and navigation. Detail lives in sibling files that the body links to.
  - How: keep `SKILL.md` under 500 lines. Link `reference.md` / `examples.md` with a sentence saying what each holds and when to read it. Put executable helpers in `scripts/`, where they are run rather than loaded.
  - Why it works: the body stays in context across turns once invoked (ch07), so each line is a recurring cost. Linked files cost nothing until Claude reads them.
- **Portable frontmatter subset**: for claude.ai uploads, the Skills API or `package_skill.py`, use only `name`, `description`, `license`, `compatibility`, `metadata` and `allowed-tools`. Any other key is a hard error there. Claude Code accepts all of them.

## Key Concepts
- **Frontmatter parse rule**: the opening `---` must be the file's first line. Otherwise the whole file, markers included, becomes content. If the YAML doesn't parse, the skill still loads, but with **no** fields set.
- **Field-name strictness**: names are lowercase and hyphenated (except `when_to_use`). Claude Code ignores an unknown or misspelled key without an error.
- **Booleans**: `true/false/yes/no/on/off/1/0` in any case are accepted (v2.1.218+).
- **1,536-char listing cap**: the combined `description` + `when_to_use` is truncated at 1,536 chars in the skill listing (configurable via `skillListingMaxDescChars`). Put the key use case first.
- **Command name source**: the `name` field or the directory name. Both invoke a personal/project skill. Plugin skills are `/plugin:name`. For command files, the path's `/` becomes `:`.
- **String substitutions**: `$ARGUMENTS`, `$ARGUMENTS[N]`, `$N`, `$name` and `${CLAUDE_*}` variables are expanded at render time (details in ch07).
- **`${CLAUDE_SKILL_DIR}`**: the directory holding `SKILL.md` (for plugin skills, the skill's subdir, not the plugin root). Claude Code expands it in the body **and** in `allowed-tools` Bash rules.
- **Escape**: `\$1.00` keeps a literal `$` before a digit, `ARGUMENTS` or a declared name. `\\$1` still expands. A backslash never stops `${CLAUDE_*}` substitution.

## Mental Models
- Think of `description` as the skill's search index entry. It is the only text Claude matches requests against, so write the phrases users actually say.
- Use `allowed-tools` with `${CLAUDE_SKILL_DIR}` when a skill runs its own script. The same variable expands in both places, so the rule matches the exact command and no permission prompt appears.
- Think of `metadata` as your tooling's private map. Claude Code never acts on it, and it drops a value that isn't a map.
- Treat `.claude/commands/*.md` as legacy. It takes the same fields except `name` and `paths`, and it has no supporting files.

## Anti-patterns
- **Leading text before `---`**: the frontmatter is ignored and appears as content.
- **Typos such as `disable_model_invocation`**: silently ignored, so the skill auto-invokes anyway.
- **Description buried after preamble**: truncation at 1,536 chars (or description dropping under listing-budget pressure, ch09) cuts the trigger keywords.
- **Claude Code-only fields in a claude.ai upload**: `Unexpected key(s) in SKILL.md frontmatter: argument-hint...` is a hard failure.
- **Narrating why in the body**: state what to do. Every line is re-paid on every turn after the skill is invoked.
- **Reusing frontmatter names (e.g. `paths`) as `metadata` keys**: this confuses tooling. The docs say not to do it.

## Code Examples
```yaml
---
name: render-chart
description: Render a chart from a CSV file
allowed-tools: Bash(${CLAUDE_SKILL_DIR}/scripts/render.sh *)
---

Run `${CLAUDE_SKILL_DIR}/scripts/render.sh <csv-file>` to render the chart.
```
- **What it demonstrates**: the same variable in body and `allowed-tools`, so the bundled script runs without a prompt wherever the skill is installed.

```text
my-skill/
├── SKILL.md (required - overview and navigation)
├── reference.md (detailed API docs - loaded when needed)
├── examples.md (usage examples - loaded when needed)
└── scripts/
    └── helper.py (utility script - executed, not loaded)
```
```markdown
## Additional resources

- For complete API details, see [reference.md](reference.md)
- For usage examples, see [examples.md](examples.md)
```

## Reference Tables

**Frontmatter fields (all optional; `description` recommended)**

| Field | What it does | Default |
|---|---|---|
| `name` | Command name shown in the `/` menu. In a plugin it sets the last segment. A `name` that already carries the plugin prefix isn't doubled (v2.1.246+). Not allowed in command files | Directory name (plugin root `SKILL.md`: plugin dir name) |
| `description` | What the skill does and when to use it. Claude matches requests against it. Combined with `when_to_use` it is capped at 1,536 chars in the listing | First non-empty line of the body |
| `when_to_use` | Extra trigger context (phrases, example requests), appended to `description`, counts toward the 1,536 cap | none |
| `argument-hint` | Autocomplete hint, e.g. `[issue-number]` or `[filename] [format]` | none |
| `arguments` | Named positional args for `$name` substitution. Space-separated string or YAML list, mapped to positions in order | none |
| `disable-model-invocation` | `true` = Claude can't auto-load it. Its description leaves context, it can't be preloaded into subagents, and it won't run when a scheduled task fires with it as the prompt | `false` |
| `user-invocable` | `false` = hidden from the `/` menu and typing `/name` doesn't run it. Only Claude invokes it | `true` |
| `allowed-tools` | Tools pre-approved for the **turn** that invokes the skill. Clears on your next message. Space/comma string or YAML list. Doesn't restrict other tools | none |
| `disallowed-tools` | Tools removed from the pool while the skill is active. Clears on your next message. Can't remove `EndConversation` while other tools remain | none |
| `model` | Model for the rest of the current turn (not saved). Takes `/model` values or `inherit`. A model excluded by `availableModels` or unsupported in auto mode is ignored. With `context: fork`, it sets the subagent's model | session model |
| `effort` | `low`/`medium`/`high`/`xhigh`/`max` while active, overriding the session level. Available levels depend on the model | effort resolution order |
| `context` | `fork` = run in a forked subagent (ch08) | inline |
| `agent` | Subagent type for `context: fork` (`Explore`, `Plan`, `general-purpose`, or a custom one from `.claude/agents/`) | `general-purpose` |
| `background` | With `context: fork` only. `false` = wait for the result in the invoking turn (v2.1.218+) | `true` |
| `hooks` | Hooks registered when the skill is invoked. They persist for the rest of the session (supports `once`) | none |
| `paths` | Globs (comma string or YAML list) that limit auto-activation to matching files. Same format as path-specific rules. Not allowed in command files | none (always eligible) |
| `shell` | Shell for `` !`cmd` `` and ```` ```! ```` blocks: `bash` or `powershell` (needs the PowerShell tool enabled) | `bash` |
| `metadata` | Free-form YAML map for your own tooling. Ignored by Claude Code, and a non-map value is dropped | none |
| `license` | Agent Skills spec field. Accepted but not acted on | none |
| `compatibility` | Spec field for environment requirements, string ≤ 500 chars. Accepted but not acted on | none |

**Where the frontmatter works**

| Distribution path | Allowed fields |
|---|---|
| Claude Code (any level, incl. plugins) | All of the above |
| claude.ai upload, Skills API, `package_skill.py` | `name`, `description`, `license`, `compatibility`, `metadata`, `allowed-tools` |

**Command name by layout**

| Location | Source | Example |
|---|---|---|
| `~/.claude/skills/` or `.claude/skills/` dir | `name` or dir name | `deploy-staging/` → `/deploy-staging`, or `/deploy` with `name: deploy` |
| Nested, clashing | subdir path + dir name | `apps/web/.claude/skills/deploy/` → `/apps/web:deploy` |
| `.claude/commands/x.md` | file name | `/deploy` |
| `.claude/commands/frontend/component.md` | path with `:` | `/frontend:component` |
| Plugin `skills/` | `name` or dir, namespaced | `/my-plugin:review`, or `/my-plugin:fancy` with `name: fancy` (bare `/fancy` also works if free) |
| Plugin root `SKILL.md` | `name`, falling back to plugin dir name | `/my-plugin:review` |
| Synced from claude.ai | account name | `/anthropic-skills:deploy`, or `/deploy` if free |

**Substitution variables**: `$ARGUMENTS`, `$ARGUMENTS[N]`, `$N`, `$name`, `${CLAUDE_SESSION_ID}`, `${CLAUDE_EFFORT}`, `${CLAUDE_SKILL_DIR}`, `${CLAUDE_PROJECT_DIR}`, and in plugin skills only `${CLAUDE_PLUGIN_ROOT}` and `${CLAUDE_PLUGIN_DATA}` (persistent across updates). The `${CLAUDE_*}` path variables also expand inside `allowed-tools` Bash rules.

## Worked Example
Goal: an API-review skill that ships to both Claude Code and claude.ai.
```yaml
---
name: api-review
description: Reviews REST endpoint changes against our API conventions. Use when adding or changing endpoints, error formats, or request validation.
allowed-tools: Read Grep
metadata:
  owner: platform-team
---

When reviewing endpoints:
- Check RESTful naming, consistent error format, request validation
- For the full style guide, read [conventions.md](conventions.md)
- For good/bad examples, read [examples.md](examples.md)
```
Decisions: this is reference content, so it runs inline and Claude may auto-load it. The trigger words come first in `description`. Only portable fields are used, so a claude.ai upload won't fail. If it were Claude Code-only, `paths: "src/api/**"` would limit auto-activation to API files. Adding `argument-hint` would break the claude.ai upload. The bulk sits in `conventions.md`, which keeps `SKILL.md` far below 500 lines.

## Key Takeaways
1. Only `description` is effectively required. Make its first sentence carry the trigger keywords, because it is truncated at 1,536 chars together with `when_to_use`.
2. Unknown or misspelled fields and broken YAML fail silently. The skill loads with fields missing or empty.
3. `allowed-tools` and `disallowed-tools` last one turn. `hooks` last the rest of the session. `model` lasts the current turn.
4. `context`, `agent` and `background` control subagent execution, and `background` applies only with `fork`.
5. Keep `SKILL.md` under 500 lines and link supporting files with "what + when" pointers.
6. Pair `${CLAUDE_SKILL_DIR}` in the body and in `allowed-tools` for prompt-free bundled scripts.
7. Portable skills use just the six spec fields.

## Connects To
- **ch05**: where skills live and name collisions.
- **ch07**: `disable-model-invocation`/`user-invocable`, `allowed-tools` lifetime, `$ARGUMENTS`.
- **ch08**: `context: fork`, `agent`, `background`, `shell`, `` !`cmd` ``.
- **ch09**: description truncation and the listing budget, `claude plugin validate`.
- **ch02**: `paths` uses the same globs as `.claude/rules/` path-specific rules.
- **ch11**: preloading skills into subagents (`skills` field), which `disable-model-invocation` blocks.
