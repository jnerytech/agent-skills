# Chapter 8: Amazon Bedrock AgentCore Harness - The Managed Agent Loop and the Export-to-Code Boundary

## Core Idea
The AgentCore harness turns the orchestration loop (and everything under it) into configuration; to use it safely you must know what the declaration holds, what defaults silently fill the gaps, what it cannot express or restrict, and what obligations appear when you exit back to code. (Verified against primary sources 2026-09-14, updated 2026-10-03.)

## Frameworks Introduced
- **Harness vs Runtime = who writes the loop**: same platform underneath. Runtime: you bring code in any framework, wrap with `BedrockAgentCoreApp`, ARM64 container → ECR → deploy; "the orchestration loop is yours". Harness: the loop is provided, powered by Strands Agents. CloudTrail logs harness ops under `AWS::BedrockAgentCore::Runtime`.
- **Two-tier config: defaults at creation, overrides at invocation**: 9 settings override per `InvokeHarness` call; everything else requires `UpdateHarness` → new immutable version. "Test N model/prompt/tool combinations in the time it would take to redeploy once."
- **Three doors, three minimums**: service API vs AgentCore CLI vs Terraform (plus CloudFormation) differ in required fields and defaults — decide which entry point is authoritative.
- **Declarative vs IAM restriction**: `allowedTools` restricts what the model may *select*; only IAM restricts what the API can *execute* (`InvokeAgentRuntimeCommand`).
- **Export harness to code (asymmetric exit)**: `agentcore export harness` → editable Strands Python; carries config items, not the harness's service-side validation. Always read `EXPORT_NOTES.md` before deploying.
- **AWS's own recommendation (quoted)**: "Use the harness unless you have a specific reason to own the loop yourself (for example, an existing agent codebase to migrate, or advanced orchestration the harness does not yet express)." Note the "yet".

## Key Concepts
- **Agent harness (AWS sense)**: the loop plus compute, sandbox, secure tool connections, filesystem, memory, identity, observability. "The loop was never the hard part. The hard part was everything around it."
- **What it absorbs (GA list, 6)**: runs the orchestration loop, executes tools, manages context window, persists state across turns, recovers from failures, isolates each session. (Dev guide counts 5, overview page 4 — same things, different granularity.)
- **`CreateHarness`**: 18 fields, only `harnessName` + `executionRoleArn` required; `model`, `systemPrompt`, `tools`, `skills`, `memory` all optional (defaults fill in).
- **Versions & endpoints**: `V1` auto-created; each update = new immutable version. `DEFAULT` endpoint auto-advances; named endpoints (PROD, STAGING) stay pinned until promoted.
- **Stop conditions**: `maxIterations`, `timeoutSeconds`, `maxTokens` — optional, per-call overridable; defaults and max ranges are NOT documented.
- **Session**: stateful by default, one isolated microVM (Firecracker) per session, with its own filesystem and shell; persistent storage under `/mnt` (managed session storage = no VPC; EFS / S3 Files access points = VPC required).
- **BYO container**: must be `linux/arm64`; harness overrides `ENTRYPOINT`/`CMD` — you bring the environment, not the process.
- **Tools**: 5 types (remote MCP server, AgentCore Gateway, AgentCore Browser, AgentCore Code Interpreter, inline functions) + built-ins `shell` and `file_operations`. Inline functions pause the harness and return control to the caller (human-approval path).
- **Skills**: metadata loaded, full content pulled only when needed; one source per skill: AWS bundled, Git, S3, or container path; materialized onto the session filesystem.
- **`InvokeAgentRuntimeCommand`**: direct deterministic shell into the harness microVM — no model reasoning, no token cost; own IAM action.

## Mental Models
- Think of an unset field as "someone else decides", not "off": unset model = AWS's choice, unset `allowedTools` = all tools open, unset memory (API) = memory provisioned.
- Think of the harness as a single model-driven loop: "a graph-shaped agent reaches it by becoming that loop first."
- Use `InvokeAgentRuntimeCommand` for anything that needs no model judgment (clone repo, install deps, fetch artifacts, inspect during dev).
- Use the JWT auth path when downstream tools must run with per-user identity — SigV4 callers do not propagate per-user identity (planned for future).
- Think of export as leaving with your config but not your bodyguard: the input validation becomes your entrypoint's job.

## Anti-patterns
- Assuming omitting `allowedTools` restricts anything — it opens everything, including `shell` and `file_operations`.
- Assuming removing `shell` from `allowedTools` blocks shell execution — `InvokeAgentRuntimeCommand` still works; withhold `bedrock-agentcore:InvokeAgentRuntimeCommand` in IAM.
- Writing IAM only for harness actions — `InvokeHarness` needs both `bedrock-agentcore:InvokeHarness` and `bedrock-agentcore:InvokeAgentRuntime` on the harness ARN; update/delete need `UpdateAgentRuntime`/`DeleteAgentRuntime`.
- Forwarding caller input straight into `InvokeHarness` — model additional parameters pass through unvalidated (can redirect endpoint, override headers, try another IAM role, switch model/Region) and skill sources are trusted blindly.
- Developing via CLI and deploying via Terraform without reconciling defaults (memory inverted, required fields differ).
- Leaving stop limits unset — you run without knowing what values apply.
- Exporting and deploying to non-harness Runtime without adding prompt/`toolUse` validation.
- Deleting a harness and expecting auto-provisioned memory to survive — `DeleteHarness` deletes it by default.

## Code Examples
```
agentcore export harness
```
What it demonstrates: one CLI command generates equivalent Strands Python (zip by default, or Docker image), mirroring model, tools, skills, memory, execution limits, filesystem mounts, truncation, inbound auth; writes `EXPORT_NOTES.md`.

Post-export entrypoint obligation (from AWS security docs): for non-harness Runtime, "Your agent entrypoint must validate that the prompt field is a string and reject or strip toolUse content blocks before passing input to the agent framework." (The harness itself rejects a `toolUse` block in the final message of an `InvokeHarness` request.)

## Reference Tables
**Entry points**
| Door | Required | Memory when omitted |
| --- | --- | --- |
| Service API (`CreateHarness`) | `harnessName`, `executionRoleArn` | Managed memory provisioned (SEMANTIC + SUMMARIZATION, 30-day event retention, AWS-owned keys, `actorId`-keyed namespace) |
| AgentCore CLI | — | Disabled unless you select managed or existing memory |
| Terraform `aws_bedrockagentcore_harness` | `harness_name`, `execution_role_arn`, `model`, `system_prompt` | — |
| CloudFormation | `AWS::BedrockAgentCore::Harness`, `AWS::BedrockAgentCore::HarnessEndpoint` | — |

**Per-call (9) vs version-level**
| Per `InvokeHarness` | New version via `UpdateHarness` |
| --- | --- |
| `model`, `systemPrompt`, `tools`, `skills`, `allowedTools`, `maxIterations`, `maxTokens`, `timeoutSeconds`, `actorId` (caller-only) | environment, container image, environment variables, execution role, inbound authorization, memory, truncation |

16 optional `CreateHarness` fields: `allowedTools`, `authorizerConfiguration`, `clientToken`, `environment`, `environmentArtifact`, `environmentVariables`, `maxIterations`, `maxTokens`, `memory`, `model`, `skills`, `systemPrompt`, `tags`, `timeoutSeconds`, `tools`, `truncation` (a `hooks` field appeared by 2026-10-03).

**Defaults and numbers**
| Item | Value |
| --- | --- |
| Built-in tool overhead | ~900 input tokens per model request (`shell` + `file_operations`, approximate) |
| Long-term memory search default | `topK` 10, `relevanceScore` 0.2 |
| Memory strategies (listed) | `SEMANTIC`, `SUMMARIZATION`, `USER_PREFERENCE`, `EPISODIC` |
| Truncation | `sliding_window` (default, last N msgs), `summarization`, `none` |
| Network | Public by default; VPC needs endpoints (private ECR image pull) else "image pull timeouts" |
| Export runtime | Python 3.12+; Strands only; Python only |

**Not supported by harness (as of 2026-10-03)**: agent framework selection, bidirectional streaming, non-agent-loop patterns (graph, workflow style). Lifecycle hooks: config enables, code required. Migration guide adds: stage-specific prompt overrides not replicated; routing-mode multi-agent not straightforward (agents-as-tools OK); custom orchestrators Runtime-only.

**Export destinations**: AgentCore Runtime (`agentcore deploy`, default — compute, observability, identity unchanged) or self-hosted anywhere with Python 3.12+: Lambda, ECS/Fargate, EC2, Kubernetes, on-prem, any container. No documented path back from code to harness.

**Shared responsibility — your 9 items**: agent code/dependency security; IAM access control & resource policies; security of commands run in a session; session↔user mapping; input validation & prompt-injection prevention; model config validation; trusting skill/instruction sources; container image updates; network configuration. "The harness validates the structure of the request it accepts, but it does not inspect the meaning of prompts."

**Seven source disagreements**: API call count (2 vs "as few as three"); GA vs FAQ "(preview)"; `maxTokens` = cumulative per invocation (`CreateHarness`) vs per iteration (`InvokeHarness`) — 10x difference over 10 iterations; truncation per-call override (guide yes, API no field); export output-dir option; "Claude Agent SDK" vs "Claude Agents SDK"; required fields 2 (API) vs 4 (Terraform). The `maxTokens` and truncation ones matter most for design.

## Worked Example
Migrating off Bedrock Agents Classic (closed to new customers 2026-07-30; maintenance mode, no EOL, models frozen, no migration deadline). Two destinations: harness or code-defined Runtime agent (gives per-stage prompt overrides, supervisor/multi-agent, custom orchestration, broader OpenAI-compatible endpoints, any framework). AWS migration article: handing the loop to the harness moves 6 of 10 operational burdens (vs 5 at stage 2) — "documented rather than measured"; dependency updates is the newly moved one. IAM policies, VPC config, WAF rules, and secrets rotation stay yours at every stage (Identity refreshes tokens, doesn't rotate secrets).

## Key Takeaways
1. Harness = Runtime + AWS-written Strands loop; not a starter tool ("the agent declared on day one is the agent that runs at the thousandth").
2. Only name + role are required; every omission is a default someone else picked — declare model, prompt, `allowedTools`, memory, and stop limits explicitly.
3. 9 knobs move per call; everything else is a new immutable version; pin PROD to a named endpoint, not `DEFAULT`.
4. Lock down `InvokeAgentRuntimeCommand` with IAM, and grant both harness and Runtime actions.
5. Don't pass raw caller input to model params or skill sources; use JWT for per-user downstream identity.
6. Graph/workflow/bidi-streaming/framework choice → own the loop on Runtime (or export).
7. Export is open but asymmetric: add prompt-string and `toolUse` validation at your entrypoint; read `EXPORT_NOTES.md`.

## Connects To
- ch04 (Runtime, Memory strategies, Code Interpreter), ch05 (Identity JWT vs SigV4, Gateway tools), ch06 (IaC/CDK, observability)
- ch07 (cross-Runtime multi-agent — what the harness can't express), ch09 (Strands patterns to use after export)
- ch10 (production ops/cost/DR), ch11 (prompt-injection defense = your responsibility), ch01/ch03 (term definitions)
