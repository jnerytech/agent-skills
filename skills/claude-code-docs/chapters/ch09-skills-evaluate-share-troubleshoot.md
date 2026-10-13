# Chapter 09: Evaluating, Sharing, and Troubleshooting Skills

## Core Idea
A skill that triggers isn't necessarily working. Measure invocation and output quality separately, against a baseline with the skill off. Share at the scope your audience needs. When a skill misbehaves, the cause is almost always the description, the lifecycle, or the listing budget.

## Frameworks Introduced
- **Baseline comparison eval**: run realistic prompts in **fresh sessions** with the skill on and again with it off, then compare.
  - When to use: before trusting a new skill and after every description or body edit.
  - How: (1) collect a few realistic prompts. (2) Run each in a fresh session, because leftover authoring context hides gaps. (3) Turn the skill off: `skillOverrides` `"off"` for personal/project skills, `claude plugin eval` (no-plugin baseline) for plugin skills. (4) Compare whether it triggered and whether the output matched.
  - Why it works: it separates "Claude found it" from "it improved the result" and puts the token/time overhead next to the pass-rate gain.
- **Two eval tools (formats not interchangeable)**: `claude plugin eval` for plugin skills (isolated sessions with/without the plugin, graders, non-zero exit below a threshold, so you can gate CI) and the **skill-creator** plugin for iterating one skill in-conversation (its own `evals/evals.json`).
- **Drift triage ("Claude stops following a skill")**:
  - Must-hold-every-time rule → move it into a hook, or keep it with the skill via `hooks` frontmatter, which applies from invocation to session end.
  - Judgment guidance → reword it to cover the whole task ("Run the tests after every edit"), because the file isn't re-read.
  - After compaction → re-invoke the skill. Only the start survives, so put the key instructions at the top.

## Key Concepts
- **skill-creator plugin**: `/plugin install skill-creator@claude-plugins-official`. If you get `Marketplace "claude-plugins-official" not found`, run `/plugin marketplace add anthropics/claude-plugins-official` first. Use `/reload-plugins --force` if the reload warns. Then ask, e.g. "evaluate my summarize-changes skill with skill-creator".
- **skill-creator outputs**: test cases in `evals/evals.json` inside the skill dir, a subagent per case (clean context, token + duration), `grading.json` (pass/fail with evidence), `benchmark.json` (with vs without: pass rate, time, tokens), blind A/B between versions, description tuning (should- and should-not-trigger prompts plus hit rate), and an HTML review viewer whose feedback feeds the next iteration.
- **Sharing scopes**: project (commit `.claude/skills/`), plugin (a `skills/` dir in the plugin), managed (org-wide via managed settings).
- **Visual-output pattern**: bundle a script, for example Python stdlib only, that writes self-contained HTML and opens it. Claude orchestrates and the script does the work.
- **Skill listing budget**: names always appear, but descriptions are dropped when the listing overflows **1% of the context window**, least-invoked first. The Skills row in `/context` shows the post-budget size.
- **Malformed YAML**: the body loads with empty metadata. `/skill-name` works but auto-matching on `description` doesn't. Diagnose with `--debug` or `claude plugin validate .claude/skills` (v2.1.233+).
- **`.trash` recovery**: removed or unsynced skills move to `~/.claude/skills/.trash/` (timestamped). The retention sweep deletes them after 30 days by default.

## Mental Models
- Think of the description as a classifier you tune. Too few user keywords and it never triggers. Too broad and it triggers constantly.
- Use `"name-only"` in `skillOverrides` as a budget lever for low-priority skills. They stay discoverable by name and give up description space to the skills that need it.
- Treat `claude plugin eval` with a `tool_used: Skill` grader as a trigger-rate regression test for plugin skills. Run it after every description change.
- Think "script does the work, Claude orchestrates" whenever you'd otherwise ask Claude to hand-generate a large artifact.

## Anti-patterns
- **Testing in the session where you wrote the skill**: authoring context masks missing instructions.
- **Judging success by "it triggered"**: that measures discovery, not output quality.
- **Using `skillOverrides` to baseline a plugin skill**: it doesn't apply to plugins. Use `claude plugin eval`.
- **Piling on skills without pruning**: descriptions get dropped and triggers silently stop. Run `/skill-doctor`.
- **Long preamble in `description`**: the per-entry cap of 1,536 chars cuts the keywords whatever the budget.
- **Relying on a skill for an invariant**: skills drift and hooks don't.

## Code Examples
````yaml
---
name: codebase-visualizer
description: Generate an interactive collapsible tree visualization of your codebase. Use when exploring a new repo, understanding project structure, or identifying large files.
allowed-tools: Bash(python3 *)
---

# Codebase Visualizer

Run the visualization script from your project root:

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/visualize.py .
```

This creates `codebase-map.html` in the current directory and opens it in your default browser.
````
- **What it demonstrates**: the bundled-script pattern. `${CLAUDE_SKILL_DIR}` resolves at any install level, and `allowed-tools` lets `python3` run without a prompt. The script (`scripts/visualize.py`, stdlib only) scans the tree while ignoring `.git`, `node_modules`, `__pycache__`, `.venv`, `venv`, `dist` and `build`. It writes a sidebar summary, a top-8 file-type bar chart and a collapsible tree, then prints `Generated /path/to/codebase-map.html`. That printed path confirms success in headless environments.

```bash
claude plugin validate ~/.claude/skills
```

## Reference Tables

| Symptom | Fix |
|---|---|
| Skill not triggering | Add natural user keywords to `description`. Check that it appears in "What skills are available?". Rephrase the request. Invoke `/skill-name`. Run `--debug` for YAML errors, and `claude plugin validate` |
| Triggers too often | Make `description` more specific, or add `disable-model-invocation: true` |
| Stops following midway | Invariant → hook (or `hooks` frontmatter). Judgment → whole-task wording. Compaction → re-invoke and put key rules first |
| Descriptions cut short | Raise `skillListingBudgetFraction` (e.g. `0.02` = 2%) or `SLASH_COMMAND_TOOL_CHAR_BUDGET` (fixed chars). Set low-priority skills to `"name-only"`. Trim at the source (`skillListingMaxDescChars` sets the 1,536 cap). Check `/doctor` and `/skill-doctor` |
| Personal skills disappeared | Look in `~/.claude/skills/.trash/` and move the folder back within 30 days. Before v2.1.280 a `manifest.json` in `~/.claude/skills/` could trash listed folders |

| Eval tool | Scope | Format | Output |
|---|---|---|---|
| `claude plugin eval` | Plugin skills | its own suite format; graders such as `tool_used: Skill` | Pass/fail; non-zero exit below threshold (CI gate) |
| skill-creator plugin | Any single skill, in-conversation | `evals/evals.json` | `grading.json`, `benchmark.json`, A/B, HTML viewer |

| Share with | How |
|---|---|
| Repo collaborators | Commit `.claude/skills/` (also loads in cloud sessions and Claude Tag channels) |
| Any users of a plugin | `skills/` directory in the plugin |
| Whole org | Managed settings |

## Worked Example
Situation: `summarize-changes` (ch05) rarely triggers on "write me a commit message", and the team has 60 skills.
1. **Measure**: install skill-creator and ask it to evaluate `summarize-changes`. It writes 6 should-trigger prompts ("what changed?", "commit message please") and 4 should-not prompts to `evals/evals.json`, then runs each in a subagent.
2. **Read results**: `benchmark.json` shows the with-skill pass rate up 40 points for +1.2k tokens, which is worth it. Description tuning reports a 50% hit rate on commit-message prompts.
3. **Diagnose**: `/context` shows the Skills row at the budget. `/skill-doctor` flags 12 never-invoked skills, and `summarize-changes` is lightly used, so its description was among the first dropped.
4. **Fix**: turn off the 3 most expensive unused skills, set 6 others to `"name-only"`, and move "commit message" to the front of the description.
5. **Verify**: re-run the blind A/B between old and new description, confirm the hit rate rose, then commit.
6. **Harden**: the team needs "never commit secrets" every time, so that rule goes into a `PreToolUse` hook rather than the skill body.

## Key Takeaways
1. Evaluate trigger rate and output quality separately, in fresh sessions, against a skill-off baseline.
2. Use `claude plugin eval` for plugin skills (gates CI) and skill-creator for iterating one skill. Their formats differ.
3. Skills are shared via project commit, plugin or managed settings. Personal skills don't travel.
4. The skill listing gets 1% of the context window and drops the least-used descriptions first. Manage it with `skillListingBudgetFraction`, `"name-only"` and `/skill-doctor`.
5. Malformed frontmatter fails quietly. Use `--debug` and `claude plugin validate <dir>`.
6. For drift, put invariants in hooks, judgment in whole-task wording, and re-invoke after compaction.
7. Lost personal skills are in `~/.claude/skills/.trash/` for 30 days.

## Connects To
- **ch05**: sharing locations and synced-skill `.trash` behavior.
- **ch06**: `description`/`when_to_use` 1,536-char cap and YAML parse rules.
- **ch07**: the lifecycle and compaction budget behind "stops following".
- **ch08**: `skillOverrides` and `/skill-doctor`.
- **ch14 / ch15**: hooks for rules that must hold every time.
