# Chapter 13: Vibe Coding Prompt Template: Thinking Before Building

## Core Idea
The Vibe Coding Prompt Template (github.com/KhazP/vibe-coding-prompt-template) backs the spec-driven chain up one step: before the IDE opens, it asks "is this worth building, and do you know what it needs to do?" — and makes that thinking so cheap (≈30 minutes collapsed into running prompts) that skipping it stops being attractive. Its key output is a sparse, generated agent context (AGENTS.md + agent_docs/) produced from a PRD and tech design, not hand-written.

## Frameworks Introduced
- **The Five-Phase Pipeline**: Deep Research → Product Requirements → Technical Design → Agent Configuration → Build.
  - When to use: starting a new project and wanting to ship something real without skipping the thinking.
  - How: run phases 1–3 in any chat tool (Claude.ai, ChatGPT, Gemini), each producing a **persisted Markdown artifact**, not a chat history; phase 4 generates agent config from those artifacts; phase 5 runs in the IDE, which loads the artifacts — never the conversation.
- **Meta-Prompt Context Generation (Phase 4)**: feed `part4-notes-for-agent.md` plus your PRD and tech design to an agent; the output is configuration, not code.
  - When to use: instead of hand-writing a generic CLAUDE.md.
  - How: generate AGENTS.md, an `agent_docs/` directory (`tech_stack.md`, `code_patterns.md`, `project_brief.md`, `product_requirements.md`, `testing.md`), and tool-specific configs (CLAUDE.md, GEMINI.md, `.cursor/rules/`) — all from one source of truth. When requirements change, regenerate through the same prompt rather than editing three configs.
- **Progressive Disclosure**: the agent gets the master contract first and reaches into `agent_docs/` only when the task calls for it.
  - When to use: any project whose context would otherwise bloat the root config.
  - How: root config = a few directives + pointers; detail lives in scoped docs. Context fatigue managed by design, not discipline.
- **"Less Is More" for Configs**: do NOT put giant prompt dumps into CLAUDE.md or Cursor rules; put them in `agent_docs/code_patterns.md` or `tech_stack.md` and let the config merely point there.
  - When to use: always — the generator enforces it by construction.
  - How: treat the root config as a routing layer, not a knowledge base.
- **Plan → Execute → Verify with a Human Gate**: "Treat the agent like a junior developer. Ask it to stop after each major feature, explain the diff, and run tests where possible."
  - When to use: every build phase, especially when trust in the agent is still low.
  - How: open with the first command below; approve the plan before any code; one feature at a time.

## Key Concepts
- **Vibe Coding Prompt Template**: a five-phase prompt workflow from research to build, producing persisted artifacts that seed agent context.
- **PRD-[AppName]-MVP.md**: phase 2 output — scope, user stories, must-haves, success metrics.
- **TechDesign-[AppName]-MVP.md**: phase 3 output — stack, architecture, trade-offs, deployment.
- **AGENTS.md**: the generated master contract the agent loads first.
- **agent_docs/**: scoped detail files the root config points to.
- **Saved artifact vs chat history**: artifacts are explicit, portable context; conversations are not.
- **Human gate**: explicit approval required before the agent writes code.
- **Context drift as context-management failure**: ignoring docs, building beyond PRD scope, overcomplicating — fixed by reloading context, returning to the plan, constraining scope.

## Mental Models
- Think of the root config as a **router**: a three-page CLAUDE.md is read loosely and followed inconsistently.
- Use generation over hand-writing when a source of truth (PRD + tech design) exists — the config inherits correctness from it.
- Think of the agent as a junior developer: stop after each feature, explain the diff, run tests.
- Treat context drift as your context-management bug, not the model's.

## Anti-patterns
- **Skipping the "worth building?" question**: yields three weeks of code implementing the wrong thing on an architecture picked for familiarity, not fit.
- **Carrying chat history into the IDE**: context becomes implicit and non-portable; load saved artifacts instead.
- **Giant prompt dumps in CLAUDE.md / Cursor rules**: the model follows them inconsistently.
- **Editing three per-tool configs by hand**: they diverge; regenerate from the one source.
- **Treating generated context as permanent**: agent_docs/ from week one is subtly wrong by week six.

## Code Examples
```text
Phase 1: Deep Research          part1-deepresearch.md
         → market analysis, demand validation, competitive scan
Phase 2: Product Requirements   part2-prd-mvp.md
         → PRD-[AppName]-MVP.md: scope, user stories, must-haves, success metrics
Phase 3: Technical Design       part3-tech-design-mvp.md
         → TechDesign-[AppName]-MVP.md: stack, architecture, tradeoffs, deployment
Phase 4: Agent Configuration    part4-notes-for-agent.md
         → AGENTS.md + agent_docs/ + tool configs (CLAUDE.md, GEMINI.md, .cursor/rules/)
Phase 5: Build                  iterative agent loop
         → Plan → Execute → Verify, one feature at a time
```
- **What it demonstrates**: each phase emits a named, persisted artifact that feeds the next.

```text
Read AGENTS.md, propose a Phase 1 plan, wait for my approval, and then build it step by step.
```
- **What it demonstrates**: the recommended first command encodes load context → produce plan → human gate before code.

## Reference Tables
| Aspect | Vibe Coding Prompt Template |
|---|---|
| What | Five-phase workflow: research → PRD → tech design → agent config → build |
| Core move | Meta-prompt generates AGENTS.md + agent_docs/ from your PRD and tech design |
| Context model | Progressive Disclosure: sparse root config points to scoped agent_docs/ detail |
| Cross-platform | Generates CLAUDE.md, GEMINI.md, .cursor/rules/ from one source of truth |
| Human gate | Plan-first, approval required before each build phase |
| Limit | Setup tool, not an enforcer; generated context files still go stale |
| Use it when | Starting a new project and need to ship something real without skipping the thinking |

## Why It Works / Failure Mode
- **Works** because it lowers the cost of upfront thinking rather than enforcing it, and because context generated from the PRD/tech design is project-specific and sparse by construction.
- **Fails** through staleness: it is a setup tool, not an enforcer. The PRD evolves, the architecture shifts, and a stale AGENTS.md throws no compile error, no failing test, no annotation violation. Monthly maintenance cadences help but cannot make staleness visible — that is why the code-level enforcers of Ch 4–6 must exist.

## Key Takeaways
1. Ask "is this worth building and what must it do?" before choosing a stack.
2. Persist research, PRD and tech design as files; the IDE agent loads artifacts, not chats.
3. Generate agent context from the source of truth; regenerate on change.
4. Keep root configs sparse pointers; detail goes in scoped agent_docs/.
5. Require plan approval before code, one feature at a time.
6. Generated context still goes stale invisibly — pair it with code-level enforcement.

## Connects To
- **Ch 3**: context tiers and Section 3.2's sparse-root-config rule, here enforced by a generator; hand-maintained context as the weak link.
- **Ch 4–6**: enforcers that break when code diverges from intent, which this template cannot provide.
- **Ch 7**: planning-first discipline and the human gate.
- **Ch 11**: GSD's session-level progressive disclosure.
- **Ch 12**: Superpowers, which structures execution once the goal is clear.
