# Chapter 3: Primitives: The Building Blocks of Agentic Development

## Core Idea
Shared agent behavior cannot live in a single chat message; it has to be engineered into small, versioned, composable files called **primitives**: instructions, prompts, agents, skills, hooks, and MCP servers. The *concept* of each primitive is surface-agnostic. Its *implementation* (filenames, folders, schemas) is surface-specific to GitHub Copilot, Claude Code, Cursor, and others. Commit the primitives to the repository, and the runtime composes them around every request, turning prompt "folklore" into reviewable, governed engineering.

## Frameworks Introduced
- **The Six Core Agentic Primitives**: instructions (the always-on rulebook), prompts (reusable task templates), agents (named collaborators with a defined scope), skills (packaged domain knowledge), hooks (automated guardrails), and MCP servers (the connective tissue to external tools and data). They are presented in the order teams typically adopt them.
  - When to use: whenever agentic output must be repeatable across people and sessions rather than depending on who typed which prompt.
  - How: adopt in order. (1) Write a concise global instructions file plus glob-scoped files. (2) Turn recurring tasks into prompt templates with fixed outlines. (3) Define 3–5 named, least-privilege agents. (4) Package 3–5 high-leverage skills with their failure modes. (5) Add a few fast, deterministic hooks at lifecycle events. (6) Connect MCP servers read-only first, with pinned versions and logged calls.
  - Why it works / failure mode: each primitive answers exactly one question: rules (instructions), *what* to produce (prompt), *who* does it (agent), *how* to do it (skill), *what is enforced* (hook), and *what can be reached* (MCP). Splitting the concerns this way keeps each file small and reviewable. The failure mode is collapsing them: an instructions file stuffed with procedures, or an agent brief that grows into a whole workflow.
- **Primitive Anatomy (Frontmatter + Body)**: every primitive except hooks and MCP is a Markdown file. YAML frontmatter carries metadata the runtime reads (applyTo, description, argument-hint, tools, model), and the body is natural-language content: rules, a template, a system prompt, or a procedure. Hooks are *event + action*. MCP is *server + tools + resources + prompts + client configuration*.
  - When to use: when authoring or reviewing any primitive file.
  - How: put routing metadata (the trigger description, the scope glob, the tool allowlist) in frontmatter. Put behavior in the body. Treat the `description` as the trigger the orchestrator matches on.
- **Visibility Layers**: (1) user/workspace level holds personal preferences, permissions, and local tooling; (2) repository level is versioned, shared, reviewable, and inherited by every contributor who clones the repo; (3) enterprise scope holds organization-wide policies, standards, and approved tools across repos and teams.
  - When to use: deciding where a given configuration should live.
  - How: put anything that defines how *the project* works in the repo, because the repository layer is the foundation for shared systems. Keep personal choices at user level (e.g., `settings.local.json`). Raise organization-wide standards to enterprise scope.
- **Macro Orchestrator Composition**: the runtime (Copilot Agent Mode, Claude Code, Copilot CLI) acts as the macro orchestrator. It loads instructions automatically, selects the right prompt or agent, reads the needed skills, and treats hooks as boundaries. Primitives are neither called in a fixed sequence nor isolated, and a single task can use all six within seconds.
  - When to use: designing how primitives should interact for a class of task.
  - How: design each primitive to be discoverable by its description and scope, not hard-wired. Expect one request to activate several layers at once.
  - Why it works / failure mode: one sentence from a developer gets "six layers of governance" composed around it. If the primitives were invoked by hand, governance would depend on someone remembering to do it.
- **Enterprise Platform-Engineering Layer for Agents**: at enterprise scope (e.g., GitHub Enterprise), govern primitives centrally through managed Copilot policies, organization instructions, repository templates, required workflows, approved MCP integrations, and shared automation pipelines, instead of letting each repo evolve isolated conventions.

## Key Concepts
- **Primitive**: a small, reusable file (Markdown or YAML, mostly natural language) that tells an agent how to behave, which tools it may use, what good output looks like, and when to escalate. Primitives are composable.
- **Surface-agnostic vs surface-specific**: the engineering pattern is portable across tools, but the concrete artifacts are not. A primitive file cannot be copied unchanged between Copilot and Claude Code.
- **Instructions**: always-on rules loaded automatically into every interaction. They hold what you would tell a new senior hire on day one: stack, architectural boundaries, security, testing standards, and commit/PR style.
- **Scoped instructions**: instructions that apply only to a glob: `applyTo: "src/auth/**"` in Copilot, or a nested `CLAUDE.md` in a subdirectory for Claude Code.
- **Prompt (slash command)**: a template for recurring work that specifies a structured output (spec sections, PR review checklist, test plan with coverage targets).
- **Agent (subagent)**: a named role with a specific job, allowed tools, and explicit boundaries. "Where a prompt is a recipe, an agent is the cook."
- **Skill**: a detailed procedural guide (`SKILL.md` plus supporting scripts, templates, and references) explaining *how* to do a complex task. Both the macro orchestrator and any custom agent can invoke it.
- **Hook**: a deterministic command or script that runs automatically at a lifecycle event (before or after a tool use, session start, prompt submit) to enforce checks. Hooks make governance operational.
- **MCP (Model Context Protocol)**: an open standard that lets an agent reach any compliant server through one standardized interface, replacing a custom integration per agent. Declaring servers in config and permitted MCP tools in agent frontmatter turns MCP into a governance mechanism.
- **Macro orchestrator**: the runtime that coordinates the primitives around a request.

## Mental Models
- **Think of instructions as rules and skills as recipes.** Instructions say what must always hold. Skills say how to carry out an opinionated procedure (e.g., "our approach to schema migrations"). Don't put recipes in the rulebook.
- **Think of prompt/agent/skill as what/who/how.** A prompt defines what is produced, an agent defines who does it, and a skill defines how it is done. Hooks enforce, MCP connects.
- **Treat every MCP server as a production dependency.** It has a blast radius, a permission scope, and a rollback story, so apply the same rigor as any prod integration.
- **Use hooks for fast inline feedback and CI/CD for expensive validation.** Hooks run inline with the agent, so anything slow belongs in the pipeline.

## Anti-patterns
- **Prompt folklore**: sharing a chat prompt that a colleague can't reproduce and nobody remembers a week later. The output is useful but the process isn't engineering.
- **Bloated global instructions**: long files dilute or hide the non-negotiables. Keep the global file short.
- **Conditional language in instructions** ("If you are editing the auth module…"): this is less reliable than a glob-targeted scoped file.
- **Secrets or customer data in instructions**: instructions are loaded into prompts and visible to any agent that uses them.
- **Stale instructions**: they drift as the codebase evolves. Review them about monthly, like any long-lived artifact.
- **Open-ended style guidance in prompts**: models follow structure far more reliably than style advice.
- **Pasting source material into prompts**: copies go stale. Link to maintained docs instead (context-injection links).
- **Tool-named prompts** (`gpt4-specgenerator`): name prompts by intent (`customer-input-to-spec`) so they stay durable.
- **Oversized agent briefs**: if a brief doesn't fit on one page, it's probably a workflow, so split it.
- **Over-privileged agents**: a test-writer doesn't need production secrets or, probably, shell access.
- **Fifty thin skills**: 3–5 high-leverage skills beat many shallow ones.
- **Skills without failure modes**: "what goes wrong and how to recover" is often the most valuable section, and that knowledge may exist nowhere else.
- **Heavy or opaque hooks**: slow hooks block interactive work, and failures without a fix are obstruction rather than guidance.
- **Write-enabled MCP from day one, unpinned "latest" versions, unlogged MCP calls**: each one leaves governance incomplete.

## Code Examples
```markdown
---
mode: edit
description: "Create a production-ready REST endpoint"
tools:
  - codebase
  - edits
---
# Goal
Create a new FastAPI endpoint.
# Requirements
- Generate route
- Generate request/response models
- Create service layer
- Add unit tests
- Add OpenAPI documentation
# Constraints
Follow repository architecture standards.
```
- **What it demonstrates**: the prompt anatomy. Frontmatter carries a description and tool overrides, and the body is a fixed outline rather than open-ended guidance (`.github/prompts/<name>.prompt.md`; `.claude/commands/<name>.md` in Claude Code).

```json
{
  "version": 1,
  "hooks": {
    "preToolUse": [
      {
        "type": "command",
        "bash": "./.github/hooks/scripts/check-tests.sh",
        "timeoutSec": 30
      }
    ]
  }
}
```
- **What it demonstrates**: a Copilot hook (camelCase event names) runs a deterministic script before a tool executes. The script can allow, deny, or modify the pending call, and its stdout must contain only the decision JSON.

```json
{
  "servers": {
    "hr-backend": {
      "type": "http",
      "url": "https://hr-demo.example.com/mcp"
    }
  }
}
```
- **What it demonstrates**: MCP client configuration in `.vscode/mcp.json`. The top-level `servers` object is keyed by server name. This configuration lives at IDE/workspace level, not under `.github/`. The endpoint is a fictional placeholder.

## Reference Tables

**Primitive locations by surface**

| Primitive | GitHub Copilot | Claude Code |
|---|---|---|
| Instructions (global) | `.github/copilot-instructions.md` | `CLAUDE.md` at repo root |
| Instructions (scoped) | `.github/instructions/` with `applyTo` glob frontmatter | Nested `CLAUDE.md` in subdirectories |
| Prompts | `.github/prompts/<name>.prompt.md` | Slash commands: `.claude/commands/<name>.md` |
| Agents | `.github/agents/<name>.agent.md` | Subagents: `.claude/agents/<name>.md` |
| Skills | `.github/skills/<skill-name>/SKILL.md` (+ scripts/templates) | `.claude/skills/<skill-name>/SKILL.md` |
| Hooks | `.github/hooks/`: `preToolUse`, `postToolUse`, prompt submission | `.claude/settings.json`: `PreToolUse`, `PostToolUse`, `SessionStart`, `UserPromptSubmit` |
| MCP | `.vscode/mcp.json` (or `.mcp.json`) | `.claude/settings.json` (or `.mcp.json`) |

**Primitive anatomy and practical rules**

| Primitive | Anatomy | Key rules |
|---|---|---|
| Instructions | Frontmatter: usually just `applyTo` (global often none). Body: short list of non-negotiables, definition of done | Concise; scoped over conditional; review monthly; no secrets |
| Prompts | Frontmatter: `description`, `argument-hint`, optional agent/model/tools. Body: structured Markdown template with validation gates ("stop and ask the user before proceeding") | Fixed outlines; link, don't paste; name by intent |
| Agents | `description` (one-sentence trigger), `tools` (explicit allowlist), body (persona, rules, procedure, escalation criteria) | One page; least privilege; explicit escalation; start with 3–5 |
| Skills | `name`, `description` (trigger), `argument-hint`. Body: steps, code templates, pitfalls, links to sibling scripts | Treat as internal libraries; 3–5 high-leverage; include failure modes |
| Hooks | Event + Action (secret scan, policy validation, audit log, infra check, context summary) | Few high-value; lightweight; actionable failures |
| MCP | Server, Tools (name/description/input schema), Resources (URI-identified, for grounding), Prompts (server-published templates), Client configuration (endpoint/command, transport, auth) | Production dependency; read-only first; log activity; pin versions |

**Starter sets the chapter recommends**
- Agents: spec-writer, test-author, refactor-assistant, security-reviewer, runbook-author.
- Hooks: a secrets scanner after file edits, a dependency-policy check before commits, a production-readiness check before deployment.

## Worked Example
**Request:** a developer types "Implement secure user authentication." The macro orchestrator composes all six primitives:
1. **Instructions** load automatically: the global coding standards plus a scoped `auth/**` file that adds OWASP guidance.
2. **Prompt** `implement-from-spec` structures the work into stages: specification, testing, implementation, and security review.
3. **Agent** `backend-dev` does the work, with tools limited to the repository and the test runner.
4. **Skill** `oauth-pkce` supplies the procedure for the chosen auth flow.
5. **Hooks** fire on file save and on commit, running the secrets scanner, dependency policy, and SAST checks.
6. **MCP** servers give read-only access to the issue tracker and gated access to the staging deployment tool, which requires human approval.

One sentence of input gets six layers of governance. A smaller example: a `pr-reviewer` agent is about to review a PR, and a `preToolUse` hook runs `check-tests.sh` first. If the PR contains no test file, the review is blocked and the agent receives the reason (Figure 3.1: hook-based PR validation flow).

## Key Takeaways
1. Encode shared rules, tasks, roles, procedures, guardrails, and tool access as repository-committed primitives so every contributor and agent inherits the same definition of done.
2. Keep each primitive to its single job (rules / what / who / how / enforce / connect), and split any file that starts doing two.
3. Prefer structure over prose: scoped globs over conditionals, fixed outlines over style advice, links over pasted content.
4. Apply least privilege and explicit escalation to agents, for example "if the change touches auth, payments, or PII, stop and hand back with a one-paragraph risk note."
5. Start small: 3–5 agents, 3–5 skills, a handful of fast hooks. Push expensive validation to CI/CD.
6. Govern MCP like production infrastructure: read-only first, logged (which agent, which tool, which inputs, when), and version-pinned and rolled forward on a schedule.
7. The pattern is portable but the files are not. Learn the primitive roles once, then map them to each surface's conventions.

## Connects To
- **ch02**: the developer acts as a director, and primitives are the engineered shared understanding that makes direction work.
- **ch04**: the RPI cadence and agentic DevOps apply these composed primitives across the SDLC.
- **ch05**: hooks, scoped tool access, and MCP logging/pinning are the deterministic mechanisms behind the governance model.
- **ch06**: use cases build agentic solutions directly from the HVE primitives.
- **Model Context Protocol (modelcontextprotocol.io)**: the open standard behind the sixth primitive.
- **HVE Core (microsoft/hve-core)**: Microsoft's reference library of reusable prompts and AI workflow artifacts for Hypervelocity Engineering.
- **OWASP**: the standard behind scoped auth instructions and security-review skills.
