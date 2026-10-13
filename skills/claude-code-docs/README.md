# claude-code-docs

Agent skill generated from the official Claude Code documentation (Anthropic, code.claude.com/docs) with [book-to-skill](https://github.com/virgiliojr94/book-to-skill). It covers the four extension mechanisms: memory (CLAUDE.md, `.claude/rules/`, AGENTS.md, auto memory), skills (SKILL.md, frontmatter, invocation control, dynamic context, `context: fork`), subagents (scope, tools, models, forks, resume) and hooks (events, matchers, exit codes, JSON decisions, prompt/agent/HTTP hooks). It is organized as rules, chapter summaries, a glossary, patterns and a cheatsheet.

## Install

```
npx skills add jnerytech/agent-skills --skill claude-code-docs
```

## Files

| File | Contents |
|---|---|
| `SKILL.md` | Core rules per mechanism, chapter index, topic index |
| `chapters/ch01…ch16` | 16 chapter summaries (memory, skills, subagents, hooks) with field tables, config/JSON snippets and a worked example |
| `glossary.md` | Key fields, events and terms with chapter references |
| `patterns.md` | Techniques (When / How / Trade-offs) |
| `cheatsheet.md` | "Which mechanism?" table, precedence orders, thresholds, warning signs |

## Source

The content is synthesized summaries, not a copy of the documentation text. Sources are four pages of the Claude Code docs as of 2026-10-13: memory, skills, sub-agents and hooks-guide. This is an unofficial summary. Claude Code changes often, so check https://code.claude.com/docs for current behavior, and for the pages not covered here (hooks reference, settings, MCP, plugins, Agent SDK).
