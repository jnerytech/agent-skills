# Chapter 07: Skill Invocation, Content Lifecycle, Tool Pre-Approval, and Arguments

## Core Idea
Two frontmatter flags set *who* can invoke a skill. Once invoked, the rendered body stays in the conversation as standing instructions, while `allowed-tools` grants last only one turn. Arguments flow into the body through `$ARGUMENTS`, indexed `$N` and named `$name` placeholders.

## Frameworks Introduced
- **Invocation control matrix**: `disable-model-invocation: true` means user-only. `user-invocable: false` means Claude-only.
  - When to use: anything with side effects or timing you want to control (`/commit`, `/deploy`, `/send-slack-message`) gets `disable-model-invocation: true`. Background knowledge that isn't a meaningful command (`legacy-system-context`) gets `user-invocable: false`.
  - How: set exactly one flag. If Claude tries to invoke a `disable-model-invocation` skill anyway, Claude Code blocks it and tells Claude not to reproduce the steps another way, so Claude suggests you run `/deploy` yourself.
  - Failure mode: assuming `user-invocable: false` stops Claude. It only hides the skill from you. To stop Claude, use `disable-model-invocation: true`.
- **Standing-instructions lifecycle**: the rendered `SKILL.md` enters the conversation once and stays. Claude Code never re-reads the file on later turns.
  - How: write rules that should hold all task long as standing rules ("Run the tests after every edit"), not one-time steps ("Run the tests").
  - Re-invocation: identical rendered content adds only an "already loaded" note. Different content (new args, new `!` output) appends the full body again.
  - Compaction: Claude Code re-attaches the most recent invocation of each skill, keeping its **first 5,000 tokens**, inside a **combined 25,000-token** budget filled from the most recently invoked skill. Older skills may be dropped entirely, so put the critical instructions at the top.
- **Turn-scoped tool grants**: `allowed-tools` pre-approves the listed tools for the invoking turn only. It doesn't restrict other tools. Use permission allow rules for session-wide approval.

## Key Concepts
- **Slash at message start**: `/deploy staging` runs the skill directly.
- **Slash mid-message**: `go ahead and /deploy to staging` runs nothing directly. It counts as permission for that message, and Claude judges from your wording whether to run it. Drop the slash to mention a skill without permitting it.
- **Description in context**: with the default and `user-invocable: false`, the description is always in context. With `disable-model-invocation: true` it isn't, so Claude doesn't know the skill exists.
- **Preloaded skills**: subagents with a `skills` field get the full skill content injected at startup, not only descriptions.
- **Workspace trust doesn't gate `allowed-tools`**: a repo's project skill applies its grants even in a `-p` run in an untrusted folder. Review the `allowed-tools` of checked-in skills.
- **`allowManagedPermissionRulesOnly`** (v2.1.282+): Claude Code ignores `allowed-tools` in project and personal skills, and those tools go through managed rules and the normal prompt. `/status` lists the skills whose grants were ignored.
- **`disallowed-tools`**: removes tools for the active skill until your next message. It can't remove `EndConversation` while other tools remain. Use deny rules to block tools globally.
- **ARGUMENTS fallback**: if no placeholder receives the args, Claude Code appends `ARGUMENTS: <value>` to the body.
- **Skill stacking**: `/write-tests /fix-issue 123` loads both skills and passes `123` to each. That covers the first skill plus up to 5 more. Expansion stops at the first token that isn't an inline user-invocable skill, such as a forked skill like `/code-review` (v2.1.218+) or `/loop`.

## Mental Models
- Think of a skill's **instructions** as sticky and its **permissions** as one-shot. To get the grant again, invoke the skill again.
- Use `$ARGUMENTS` for free-form input, `$0 $1 $2` for fixed positional input, and `arguments: [issue, branch]` + `$issue $branch` when names make the body readable.
- Think of an unmatched indexed placeholder (`$2` with one arg) as a visible bug, because it stays literal. An unmatched named placeholder silently becomes an empty string.
- Quoting is shell-style: `/my-skill "hello world" second` gives `$0` = `hello world` and `$1` = `second`. `$ARGUMENTS` is always the raw string as typed.

## Anti-patterns
- **One-time phrasing for task-long rules**: Claude follows them on the first response and drifts after, because the file isn't re-read.
- **Critical rules at the bottom of a long `SKILL.md`**: after compaction only the first 5,000 tokens survive.
- **Treating `allowed-tools` as a sandbox**: it only pre-approves. Every tool stays callable. Use `disallowed-tools` or deny rules to restrict.
- **Expecting the grant to persist**: the next message clears it even though the instructions remain in context.
- **Trusting cloned repos' skills blindly**: a skill can grant itself broad Bash access with no trust prompt.
- **Writing `$1.00` in prose**: it expands to an argument. Write `\$1.00`.

## Code Examples
```yaml
---
name: commit
description: Stage and commit the current changes
disable-model-invocation: true
allowed-tools: Bash(git add *) Bash(git commit *) Bash(git status *)
---
```
- **What it demonstrates**: a side-effecting skill that only you can run, with git pre-approved for that turn only.

```yaml
---
name: migrate-component
description: Migrate a component from one language to another
---

Migrate the $0 component from $1 to $2.
Preserve all existing behavior and tests.
```
- **What it demonstrates**: `/migrate-component SearchBar JavaScript TypeScript` maps the arguments by position (`$0` is the same as `$ARGUMENTS[0]`).

## Reference Tables

| Frontmatter | You invoke | Claude invokes | Loaded into context |
|---|---|---|---|
| (default) | Yes | Yes | Description always; full body on invoke |
| `disable-model-invocation: true` | Yes | Not on its own | Description **not** in context; body on invoke |
| `user-invocable: false` | No | Yes | Description always; body on invoke |

| Where you type the name | Example | Effect |
|---|---|---|
| Start of message | `/deploy staging` | Runs directly |
| After plain text, standalone word | `go ahead and /deploy to staging` | Permission only, Claude decides |
| No slash | `the deploy skill` | Neither runs nor permits |

| Placeholder | Unmatched behavior |
|---|---|
| `$ARGUMENTS` | Full raw string |
| `$ARGUMENTS[N]` / `$N` | Stays literal; doesn't count as receiving args |
| `$name` (from `arguments`) | Expands to empty string; counts as receiving |
| Argument value containing `$1`/`$ARGUMENTS` | Inserted literally, not re-expanded (`${CLAUDE_*}` still expanded afterwards) |

| Lifecycle limit | Value |
|---|---|
| Per-skill kept after compaction | first 5,000 tokens |
| Combined re-attach budget | 25,000 tokens, most recent first |
| Stacked skills per message | first + up to 5 more |
| `allowed-tools` / `disallowed-tools` lifetime | until your next message |

## Worked Example
Goal: an issue-fix workflow that only you trigger, which runs git without prompts and survives a long session.
```yaml
---
name: fix-issue
description: Fix a GitHub issue
disable-model-invocation: true
argument-hint: [issue-number]
arguments: [issue]
allowed-tools: Bash(gh issue view *) Bash(git add *) Bash(git commit *)
---

Throughout this task: run the test suite after every edit, and never push.

Fix GitHub issue $issue following our coding standards.
1. Read the issue: `gh issue view $issue`
2. Implement the fix and write tests
3. Create a commit referencing #$issue
```
Walkthrough: `/fix-issue 123` renders the body with `$issue` → `123`, and the `gh`/`git` calls in this turn don't prompt. The standing rule sits at the top, so it applies on every later turn and survives compaction's 5,000-token cut. On your next message the git grant clears. If Claude needs to commit again, it asks, or you re-run `/fix-issue 123`. Because the content is identical, Claude Code adds only an "already loaded" note and re-applies the grant. Claude can't start this skill by itself, since its description isn't even in context.

## Key Takeaways
1. `disable-model-invocation: true` = user-only (description hidden from Claude). `user-invocable: false` = Claude-only (hidden from the `/` menu).
2. Only a name at the very start of a message runs a skill. Mid-message, a slash name only grants permission.
3. The skill body persists across turns and isn't re-read, so write standing instructions and put the critical ones first.
4. Compaction keeps 5,000 tokens per skill within a 25,000 combined budget, filled most-recent-first.
5. `allowed-tools` pre-approves for one turn, restricts nothing, and isn't gated by workspace trust. `allowManagedPermissionRulesOnly` disables it for project and personal skills.
6. Use `$ARGUMENTS` for raw input, `$N` for positions and `arguments` + `$name` for readability. Unconsumed args are appended as `ARGUMENTS: ...`.

## Connects To
- **ch06**: the frontmatter table these fields come from.
- **ch08**: injected-command permission checks rely on `allowed-tools`, and `skillOverrides` `"user-invocable-only"` is the settings-side equivalent of `disable-model-invocation`.
- **ch09**: "Claude stops following a skill" troubleshooting builds on this lifecycle.
- **ch11**: subagent `skills` preloading injects full content at startup.
- **ch16**: move must-always-hold rules into hooks.
