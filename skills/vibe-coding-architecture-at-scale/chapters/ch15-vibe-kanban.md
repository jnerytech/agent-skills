# Chapter 15: Vibe Kanban: Managing the Human Bottleneck

## Core Idea
When one agent writes a feature in five minutes and three run in parallel, the speed constraint is no longer code generation but the human's time to plan and review — "the bottleneck has migrated from the keyboard to the mind." Vibe Kanban (github.com/BloopAI/vibe-kanban) is a planning-and-review surface built for that bottleneck: every agent works in an isolated workspace behind a human merge gate, and review comments become the agent's next prompt. The product is sunsetting; the two properties it embodies are the durable lesson.

## Frameworks Introduced
- **Workspaces: Isolation as Infrastructure**: each agent gets a branch, a terminal and a dev server; nothing touches main or another workspace until a human merges.
  - When to use: any agent work, by default — not as an advanced practice.
  - How: one click creates branch + environment + agent; human reviews the diff and merges or sends comments back; discarding the workspace removes branch and environment. Git worktree isolation promoted from a script to a UI primitive.
- **Plan → Prompt → Review board**: a kanban board as a router for human attention, not a tracker of agent activity.
  - When to use: running multiple agents in parallel on independent issues.
  - How: **Plan** — define and prioritize issues (parent/sub-issues, priorities, tags, @mentions, filters) with clear scope, explicit acceptance criteria, named constraints; **Prompt** — agent works in a workspace; **Review** — human examines diff and decides. Goal: the human is never idle waiting on an agent and never the thing blocking one.
- **Review Is the Next Prompt (inline comment loop)**: a diff comment ("this function is doing too much, extract the validation logic") is sent straight back as the agent's next instruction.
  - When to use: iterating on agent output.
  - How: review in syntax-highlighted diffs, comment inline, dispatch; verify UI in the built-in browser (devtools, inspect, device emulation); generate PR description and merge from the same interface — no switch to a chat window.
- **Judging the successor** (Ch 11's "How to Judge the Next Tool" applied): ask whether it (1) isolates each agent's execution, (2) makes parallel work manageable, (3) keeps the human in the review loop without making review the bottleneck, (4) treats agent-switching as a config detail, not a migration.

## Key Concepts
- **Human bottleneck**: the rate-limiting step is now describing what to build and deciding whether what was built ships.
- **Workspace**: isolated branch + terminal + dev server per agent.
- **Merge gate**: no output touches shared code until a human explicitly merges.
- **Parallel execution as default**: workspaces are cheap, so several concurrent agents is the natural mode.
- **Issue quality → code quality**: loose issues produce drift; scoped issues with acceptance criteria produce reviewable diffs.
- **Context-switching cost**: leaving the diff to write a chat prompt forces rebuilding the mental model of the change twice.
- **Agent-agnostic infrastructure**: Claude Code, Codex, Gemini CLI, Copilot, Amp, Cursor, OpenCode, Factory Droid, CCR, Qwen Code under one workflow.
- **Pull-not-push context via MCP**: external tools and data connected to workspaces on demand.

## Mental Models
- Think of throughput as bounded by human planning + review time; any tool that shortens that time compounds into shipping velocity.
- Think of the kanban board as an attention router: what needs a human now?
- Use inline review comments as prompts whenever possible — the agent's next pass is then scoped to exactly the code the human looked at.
- Treat a tool as a perishable implementation of durable requirements; evaluate successors against the requirements.

## Anti-patterns
- **Agents working directly on a checked-out branch**: stray commands, half-finished refactors and over-reaching edits land in the working tree and must be untangled.
- **Perfunctory planning**: treating issue writing as a pre-step yields drifting output.
- **Separate chat channel for review feedback**: costs context switches and loosens the agent's instruction scope.
- **Review as the new bottleneck**: running more agents than the human can review just moves the queue.
- **Betting the workflow on one product**: even a well-adopted tool can sunset; hold the principles, not the vendor.

## Code Examples
```bash
npx vibe-kanban
```
- **What it demonstrates**: a local Rust-backend/TypeScript-frontend server with web UI; no separate server, database or credentials beyond what the underlying agent already needs.

## Reference Tables
| Aspect | Vibe Kanban |
|---|---|
| What | Kanban board + workspace orchestrator for parallel AI agent execution |
| Core move | Isolated workspace per agent (branch + terminal + dev server); humans plan and review |
| Parallel model | Multiple workspaces at once; board surfaces what needs human attention |
| Review loop | Inline diff comments sent as agent instructions; built-in browser for UI QA |
| Install | `npx vibe-kanban` |
| Agent support | 10 agents incl. Claude Code, Codex, Gemini CLI, Copilot, Cursor |
| Status | Sunsetting to open-source, community-maintained; principle outlives product |
| Limit | Planning/review accelerator, not structural enforcer; isolates execution, does not enforce architectural correctness |

## Worked Example
A reviewer opens a finished workspace's diff, sees a handler mixing validation and persistence, and comments inline: "this function is doing too much, extract the validation logic." The comment dispatches as the agent's next instruction in the same workspace; the agent's follow-up pass is scoped to that function; the reviewer checks the new diff (and the UI in the built-in browser), then creates the PR with an AI-generated description and merges. Main is untouched until that merge. Meanwhile two other workspaces sit in Prompt, so the reviewer is never idle.

## Why It Works / Failure Mode
- **Works** because isolation makes parallelism safe and cheap, and because collapsing review into prompting removes the context-switch tax on the scarcest resource — human attention. Adoption (≈30,000 active users, ≈100,000 PRs) shows it changed how people work.
- **Fails** where any execution tool does: it isolates execution but does not enforce architectural correctness — a merged, reviewed diff can still violate structure the Ch 4–6 guardrails would catch. Commercially, it shows that good infrastructure tools still die on ecosystem economics; the requirements, not the implementation, are the asset.

## Key Takeaways
1. Optimize the human's planning and review time — that is now the speed limit.
2. Give every agent its own isolated workspace behind a human merge gate, by default.
3. Run agents in parallel and use the board to route human attention.
4. Invest in issue quality: scope, acceptance criteria and named constraints decide diff quality.
5. Make the review comment the next prompt; avoid separate chat loops.
6. Judge successors by isolation, parallel manageability, review-loop efficiency and agent-switching cost.

## Connects To
- **Ch 1**: the entropy argument; this is its companion — the bottleneck moved to the human.
- **Ch 9**: Kiro's pull-not-push context, mirrored by MCP integration.
- **Ch 11**: "How to Judge the Next Tool," applied to the sunsetting.
- **Ch 12**: Superpowers' per-task worktrees and agent portability, here at the infrastructure level.
- **Ch 24**: worktree isolation as save-state.
- **Theory of Constraints (Goldratt)**: throughput is set by the bottleneck — now human review.
