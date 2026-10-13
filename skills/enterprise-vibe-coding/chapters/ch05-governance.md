# Chapter 5: Governance: From Stochastic to Deterministic Agentic Development

## Core Idea
Treat governance as an engineering problem, not a policy exercise. Push every consequential agent action toward the deterministic end of the stochastic-to-deterministic spectrum. The higher the blast radius, the more deterministic the control. Use five layers to do this: instruction hierarchy, hooks, policy-as-code, scoped parallelism, and the audit trail. Leave only creative work (drafting, suggesting, synthesizing) stochastic.

## Frameworks Introduced
- **The Stochastic-to-Deterministic Spectrum (five bands)**: every part of an agentic system sits in one of five bands:
  1. *Stochastic generation*: an LLM produces output from a prompt, with no guarantee that it is the same twice.
  2. *Stochastic generation under context constraint*: the same generation, but instructions, scoped rules, structured prompts and memory files narrow the range of likely outputs.
  3. *Stochastic generation with deterministic validation*: every output must pass tests, linting, type-checking, SAST, schema validation and golden-set regressions. Outputs that fail are rejected, no exceptions.
  4. *Deterministic procedure invoked by a stochastic decision*: the agent picks which tool to call (stochastic), but the tool is a reproducible script, such as a deploy recipe, migration runner or policy evaluator. The agent dispatches; it does not perform the action itself.
  5. *Fully deterministic*: a scheduled hook, CI gate, policy-as-code rule or signed release, with no model in the loop at execution time.
  - When to use: to decide, for each agent action, how much control it needs. Use it when designing a pipeline or reviewing what an agent may do.
  - How: rank each action by blast radius and place it in a band. A memo is band 1–2. Drafting a DB migration is band 3. Running that migration in prod is band 4 plus explicit human approval. Promoting a release without test evidence is blocked by a band-5 policy rule.
  - Why it works / failure mode: closes the gap between "the model probably did the right thing" and "the system could not have done the wrong thing." It fails when a team is not honest about which band each action really sits in, for example by relying on a band-2 instruction to protect a band-5 action.
- **The Five Layers of Governance Engineering**: the bands describe *where* a behavior sits; the layers are the *mechanisms* that move it toward determinism. In order: (1) Instruction hierarchy, (2) Hooks, (3) Policy-as-code, (4) Parallel-agent coordination, (5) Audit trail.
  - When to use: as the reference architecture for governing any agentic SDLC stack.
  - How: build bottom-up. Short, imperative, scoped instructions → hooks that *require* what instructions *recommend* → central policies that outlive any prompt or model → disjoint-scope parallelism → a tamper-evident causal record of everything.
  - Why it works / failure mode: each layer assumes the one below works. For example, hooks enforce rules that only work if instructions were written imperatively. None of the layers is useful without layer 5, because an action you cannot reconstruct cannot be defended.
- **Three-Tier Instruction Hierarchy (Layer 1)**:
  - *Tier 1, Global/ambient*: `.github/copilot-instructions.md` or the repo-root `CLAUDE.md`. Holds only the non-negotiables: stack choices, security rules, definition of done, prohibited libraries, data-classification matrix. Keep it concise, because long files dilute the guidance.
  - *Tier 2, Scoped/path-targeted*: `.github/instructions/*.instructions.md` with an `applyTo` glob in frontmatter, or nested `CLAUDE.md` files. The closest file wins; later rules override or refine earlier ones. The author calls this "the single most underused governance lever."
  - *Tier 3, Memory files*: `CLAUDE.md`/`CLAUDE.local.md`, Copilot Memory, and versioned repo docs holding decisions, failed approaches and post-incident lessons.
  - How: write rules in imperative form. "Use parameterized queries; never string-concatenate SQL" can be enforced by a hook. "Try to write secure database code" is folklore. Treat memory files like code: version them, review them, and hook-flag any entry with an empty *why* or *how-to-apply*. The rule for all three tiers: **short, imperative, scoped**.
- **Agentic Workflows (pinning the whole pipeline)**: one version-controlled definition fixes the trigger, least-privilege permissions, allowed MCP servers/tools, steps, and human gates. This is band 4 made concrete.
  - How (Copilot): GitHub Agentic Workflows are Markdown files in `.github/workflows/` that compile to a locked `.lock.yml`. The frontmatter declares `on:` triggers, a `permissions:` block, the allowed tools/MCP servers, and approval points. The prose body tells the agent what to do; the lock file is what actually runs.
  - How (Claude Code): `anthropics/claude-code-action` or headless `claude -p` is the runner. `.claude/settings.json` pins allow/deny permissions, `allowedTools`, and `--permission-mode`. Subagents, slash commands and skills are checked-in steps, each with its own scoped tool list.
- **Four Properties of a Good Policy**: **declarative** (describes the desired state, not the procedure), **testable** (ships with positive and negative test cases that run in CI), **auditable** (every decision is logged with the policy version, inputs and outcome), **versioned** (changes go through PRs and are signed by an accountable owner).
- **Decision Boundaries (four levels)**: Level 0 Forbidden / Level 1 Human approval required / Level 2 Logged and reviewable / Level 3 Fully autonomous. Every permitted action maps to **exactly one** level, enforced by policy. The spectrum measures how deterministic a *mechanism* is; decision boundaries measure how much *autonomy* an action gets.
- **Three Rules of Deterministic Parallelism (Layer 4)**:
  1. *Parallelize only on disjoint scopes*: file scopes, tool sets and downstream dependencies must be explicitly declared and checked as disjoint. If scopes overlap (e.g., two agents in `services/auth/`), run them sequentially. The team declares scope; the orchestrator enforces it.
  2. *Idempotency where dependencies are unavoidable*: every shared write must be safe to re-run. Examples: re-runnable migrations, a notifier that dedupes by a deterministic key, content-addressed artifact uploads.
  3. *Coordinate via the file system, not via the model*: hand off through repo artifacts such as a spec file, test report or memory note. Do not pass messages between models.
- **Three Properties of a Useful Audit Trail (Layer 5)**: an **unbroken causal chain** (prompt → merged commit, with every step's inputs, outputs and identity, and for each model decision the prompt, model version, tool list and response), **attributable identity** (each agent has a distinct ID and carries the originating user's context), and **tamper-evident storage** (write-only from the runtime, append-only from the pipeline, with retention and integrity controls that meet SOX, HIPAA, GDPR, ISO 27001 or ISO/IEC 42001).

## Key Concepts
- **Governance engineering**: moving the consequential parts of an agentic system to the deterministic end of the spectrum.
- **Blast radius**: how much damage an action can do. It decides how far toward determinism the action must sit.
- **Hook**: a deterministic side-channel (shell command or script) that fires on a defined event. It is the only mechanism that can intervene *between* the model's decision and the action. Anything an instruction recommends, a hook can require.
- **Claude Code hook events**: `PreToolUse`, `PostToolUse`, `UserPromptSubmit`, `Notification`, `Stop`, `SubagentStop`, `SessionStart`, defined in `.claude/settings.json`. A non-zero exit code or a structured JSON response blocks the action. Copilot uses `.github/hooks/` paired with `.github/workflows/`.
- **Policy-as-code**: enterprise rules in machine-evaluable form (e.g., OPA/Rego, Cedar), enforced across teams, pipelines and agents, independent of any prompt or model.
- **Decision boundary**: the explicit line separating autonomous, human-in-the-loop, and forbidden agent actions.
- **Agentic audit trail**: a unified record of every prompt, tool call, retrieved document, policy decision, human approval and model output in a change. It is "the deterministic shadow of a probabilistic system."
- **Agent identity**: a distinct principal per agent (Microsoft Entra Agent ID, AWS IAM role, OAuth principal). The goal is an answer like "Agent A, on behalf of User U, with policy version 12, called Tool T with these arguments."
- **File-mediated coordination**: subagents exchange durable, addressable, reviewable repo artifacts rather than volatile model context. It works like a Unix pipe or a microservice boundary.

## Mental Models
- **Think of governance as a spectrum, not a switch.** Ask "which band does this action live in?" rather than "do we trust the agent?" Let creativity stay stochastic and pin down only the consequences.
- **Use hooks when an instruction must stop being a suggestion.** When a rule matters enough that a violation is unacceptable, move it from Tier-1 prose into a `PreToolUse` hook or a policy. The model never sees a soft "please revise"; the call simply never runs.
- **Think of the policy decision as living outside the agent.** The agent may decide a deploy is needed; an external engine decides whether it is *allowed*. Swapping the model, prompt or agent does not change the rule.
- **Think of the audit log as a data fabric, not insurance.** Every incident becomes a memory entry. Every blocked decision becomes a test case. Every successful run becomes a positive eval example. The trail is how the system gets safer over time.

## Anti-patterns
- **One giant global rulebook with "be extra careful in payments"**: that is a hope, not an instruction. It dilutes Tier 1 and is not enforceable. Use a scoped `payments/CLAUDE.md` or `applyTo: "payments/**"` instead.
- **Aspirational rules ("try to write secure code")**: no hook can check them, so they stay folklore.
- **Unreviewed memory**: lessons that live only in conversations disappear. Memory files that are not versioned or reviewed can inject unsafe behavior into every session.
- **Parallel subagents on overlapping scopes**: produces merge conflicts or silent overwrites, rate-limit flakiness on shared services, and stale-state reads. The output becomes a function of timing, which is a race condition between LLMs.
- **Coordination through model context**: model working memory is volatile, contextual and not auditable.
- **"The agent did it"**: unattributed actions with gaps where "the model decided" fail any audit.
- **Assuming MCP gives you an audit log**: it does not. MCP clients and servers must be instrumented explicitly.
- **Treating framework compliance as the control**: NIST, ISO and the EU AI Act say *what* controls must achieve, not *how* to engineer them.
- **Deploying agents faster than governing them**: Gartner reports that more than 40% of agentic AI projects risk cancellation by 2027 (cost, unclear value, weak risk controls). WEF/Accenture found fewer than 1% of organizations had fully operationalized responsible AI, and 81% were still at the earliest maturity stage.

## Code Examples
```rego
package agent.deployment

default allow := false

allow if {
    input.agent == "release-agent"
    input.action == "deploy"
    input.environment == "production"
}
```
- **What it demonstrates**: deny-by-default policy-as-code. Only the designated release agent may deploy to production, and the agent never makes the authorization decision itself.

```markdown
<!-- payments/CLAUDE.md  (or .github/instructions/payments.instructions.md with applyTo: "payments/**") -->
- Every change in this directory must be reviewed by a security-cleared engineer.
- No agent may complete a change here without writing a tested rollback.
- The only permitted database driver is X.
```
- **What it demonstrates**: a Tier-2 scoped instruction. The strict rules load only inside the module, which keeps the global context lean.

## Reference Tables

**Decision boundaries**

| Level | Name | Who acts / reviews | Examples |
|---|---|---|---|
| 0 | Forbidden | No agent, ever | Delete production data; push directly to `main`; call external services with customer PII without explicit redaction |
| 1 | Human approval required | Agent prepares; a named human approves before execution | Production deploy; schema migration; refund above a threshold |
| 2 | Logged and reviewable | Agent acts; human reviews afterward | Open a draft PR; post a non-customer-facing summary; create a non-prod resource |
| 3 | Fully autonomous | Agent acts; no review unless an incident is raised | Lint fixes; dependency updates in an approved range; internal doc drafts |

**Hooks vs policy-as-code**

| | Hooks | Policy-as-code |
|---|---|---|
| Scope | Local: one repo, session or execution path | Organization-wide: many agents, apps and pipelines |
| Lives in | A repository | A central registry/bundle |
| New repo | Must be added | Inherits the org policy set automatically |
| Revocation | Edit each repo/agent | One change, revoked everywhere |
| Auditor reads | Repo config | Policy bundle + decision logs (no engineer interviews) |

**Engineering layers → external frameworks**

| Framework | Mapping |
|---|---|
| NIST AI RMF (Govern, Map, Measure, Manage) | Instructions → Govern & Map; hooks + policy-as-code → Manage; eval harnesses, red-teaming, audit trail → Measure. Extended by the 2024 GenAI Profile and the 2026 CSA Agentic Profile |
| ISO/IEC 42001 | Certifiable AI management system: documented policies, defined roles, lifecycle controls, continuous improvement. Policies can encode Annex A controls; integrates with ISO/IEC 27001 |
| EU AI Act | General application 2 Aug 2026; high-risk Art. 6(2)/Annex III from 2 Dec 2027; Art. 6(1)/Annex I from 2 Aug 2028 (timetable amended by Reg. (EU) 2026/1744). Logging, human-oversight, transparency, robustness, cybersecurity and QMS articles map to this chapter's controls |
| Microsoft Responsible AI Standard v2 | Six principles (fairness, reliability & safety, privacy & security, inclusiveness, transparency, accountability) → rules, tests and controls, some evaluable at agent runtime |
| OWASP Top 10 for LLM Apps / MITRE ATLAS | Threat models: prompt injection, insecure output handling, training-data poisoning, over-permissioned agents |

## Worked Example
**One task, "validate a customer record," moved along the spectrum:**
1. *Band 1*: the developer types "Write a Python function to validate a customer record." The output is plausible, but a second run gives different logic, naming and edge-case handling.
2. *Band 2*: the agent also loads repo instructions requiring Pydantic models, explicit type hints, company naming conventions and a fixed error schema. Output still varies, but it is far more likely to conform.
3. *Band 3*: the generated validator must pass unit tests, mypy, linting and a SAST scan. Any implementation may emerge, but only one that passes every gate proceeds.
4. *Band 4*: the agent decides a schema change is needed and calls the approved, version-controlled migration runner. The choice is model-driven, but the migration runs the same operations against the same starting state every time. Because it is a production migration, it is Decision Level 1: a named human approves first.
5. *Band 5*: before deploy, an OPA policy checks that the release artifact is signed, the target environment is approved, and required security checks passed. Same inputs, same verdict, no model involved.

Along the way, a `PreToolUse` hook blocks any AWS call against a production profile unless a human confirms. Subagents work on disjoint scopes (spec-writer → `docs/specs/`, test-author → `tests/`, infra-dev → `infra/`). The spec-writer hands off by writing `docs/specs/auth.md`, which backend-dev then reads. Every step is logged under each agent's own identity, on behalf of the originating user, with the policy version attached.

## Key Takeaways
1. Map every agent action to a band *and* exactly one decision level. Raise determinism in proportion to blast radius.
2. Keep Tier-1 instructions short and imperative. Put module-specific strictness in Tier-2 scoped files, the most underused lever.
3. For any rule that must never be broken, turn the instruction into a hook or policy. Recommending is not requiring.
4. Put authorization in a central, deny-by-default policy engine (OPA/Rego, Cedar via Bedrock AgentCore Policy) that is declarative, testable, auditable and versioned, so it survives model and prompt changes.
5. Parallelize subagents only on declared, disjoint scopes. Make shared writes idempotent. Hand off through repo files.
6. Give every agent its own identity and keep an unbroken, tamper-evident causal trail from prompt to commit. Feed incidents, blocks and successes back into memory, tests and evals.
7. Frameworks agree more than they disagree. Build the five layers once, then map each control to NIST, ISO 42001 or EU AI Act requirements as an evidence pack.

## Connects To
- **ch03**: instructions, hooks, agents, skills and MCP are the primitives that the five layers arrange into a governance stack.
- **ch04**: RPI across the SDLC produced the speed; this chapter makes the resulting changes accountable and auditable.
- **ch06**: the use cases put this governance stack through real customer engagements.
- **ch07**: loops depend on idempotent re-runs, deterministic gates and audit-trail feedback to stay safe.
- **ch02**: the developer acting as a director implies declaring scopes and boundaries rather than writing every line.
- **OPA/Rego, AWS Cedar**: policy-as-code engines for authorization decisions external to the agent.
- **OpenTelemetry LLM/agent semantic conventions**: let the agent audit trail reuse the existing distributed-tracing pipeline.
- **NIST AI RMF, ISO/IEC 42001, EU AI Act, OWASP LLM Top 10, MITRE ATLAS**: the external frameworks the layers implement.
