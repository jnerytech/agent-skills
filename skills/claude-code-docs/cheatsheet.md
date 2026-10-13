# Cheatsheet — Claude Code Docs

## Where does this go?
| You want… | Use | Why |
|---|---|---|
| A fact Claude needs every session | CLAUDE.md (<200 lines) | Loads at launch, and the project-root file is re-injected after `/compact` |
| A rule for one subsystem only | `.claude/rules/x.md` + `paths:` | Costs nothing until a matching file is touched |
| A multi-step procedure | Skill | The body costs context only when invoked |
| Noisy or isolated work (tests, logs, research) | Subagent | Its own context window, and only a summary returns |
| A side task needing the full conversation | Fork (`/subtask`) | Inherits history and shares the prompt cache |
| Something that must happen every time | Hook | Deterministic, whereas instructions can drift |
| Something that must never happen | `permissions.deny` / `PreToolUse` exit 2 | A hook deny holds even in `bypassPermissions` |

## Decision rules
- **Same mistake twice** → add it to CLAUDE.md. **CLAUDE.md over 200 lines** → split it into path-scoped rules, not `@imports`, because imports load at launch too. (ch01, ch02)
- **AGENTS.md repo gains a CLAUDE.md** → AGENTS.md stops loading. Add `@AGENTS.md` or switch to `claude-md-and-agents-md`. (ch03)
- **Rule lost after `/compact`** → move it from chat into the root CLAUDE.md. Nested files and `paths` rules return only when triggered again. (ch04)
- **Skill with side effects** → `disable-model-invocation: true`, never `user-invocable: false`, because the latter still lets Claude invoke it. (ch07)
- **Rule a skill must keep all task long** → put it near the top as a standing instruction. The body isn't re-read, and compaction keeps only its first 5,000 tokens. (ch07)
- **Injected `` !`cmd` `` exits 1 on findings** → append `|| true`, or the whole invocation aborts. (ch08)
- **Block one Bash command for a subagent** → `permissions.deny: Bash(git push *)`. `disallowedTools` with a specifier removes all of Bash. (ch11)
- **Follow-up builds on earlier findings** → resume with `SendMessage` (custom or general-purpose). Explore and Plan can't be resumed. (ch12)
- **Want PreToolUse approval** → return JSON `permissionDecision: "allow"`. Exit 0 approves nothing. (ch15)
- **Hard allow/deny** → permission rules, not `if`, because `if` fails open when parsing is uncertain. (ch15)
- **Blocking Stop hook** → exit early when `stop_hook_active` is true. (ch16)

## Hook type
| Decision needs… | Type | Default timeout |
|---|---|---|
| Deterministic logic or a script | `command` | 10 min |
| Judgment from the stdin JSON alone | `prompt` | 30 s |
| Inspecting real repo state | `agent` (experimental, 50 turns) | 60 s |
| An external policy service | `http` | — |

## Precedence & combination
- Parallel `PreToolUse` hooks: **`deny` > `defer` > `ask` > `allow`**. All run to completion first. `additionalContext` concatenates, and for `updatedInput` the last hook to finish wins. (ch15)
- Subagent name clash: **Managed > `--agents` > project > user > plugin**. (ch10)
- Subagent model: **per-call param > frontmatter `model` > `CLAUDE_CODE_SUBAGENT_MODEL` > main model**. `_FORCE=1` makes the env var win. (ch11)
- Parent in `bypassPermissions` / `acceptEdits` / `auto` overrides a subagent's `permissionMode`. (ch11)
- Skill name clash: enterprise > personal > project, and a skill beats a `.claude/commands/` file. (ch05)

## Thresholds & defaults
| Thing | Limit |
|---|---|
| CLAUDE.md target / hard skip | 200 lines / >4 MiB is skipped |
| `@import` depth | 4 hops |
| `MEMORY.md` loaded (auto & agent memory) | first 200 lines or 25KB |
| Skill `description` + `when_to_use` | 1,536 chars |
| Skill listing budget | 1% of context (`skillListingBudgetFraction`) |
| `SKILL.md` body | <500 lines |
| Skill after compaction | 5,000 tokens each, 25,000 total |
| Custom subagent descriptions | warning above 15,000 tokens |
| Subagent nesting / concurrency | 3 layers / 20 running |
| Stop hook consecutive blocks | 8 (`CLAUDE_CODE_STOP_HOOK_BLOCK_CAP`) |

## Tells & smells
- **Valid hook JSON has no effect** → output printed before the `{` (a shell-profile `echo`), or a field outside `hookSpecificOutput`. (ch16)
- **Skill never triggers** → vague `description`, a misspelled frontmatter key (ignored silently), or descriptions dropped by the listing budget. (ch06, ch09)
- **Subagent ignores a project rule** → it never saw the chat. Restate the rule in the delegation prompt. (ch12)
- **A `PermissionRequest` hook with an empty or `.*` matcher** → it auto-approves everything. (ch14)
