---
name: aws-agentcore-guides
description: "Knowledge base from Hidekazu Konishi's 15-article series on Amazon Bedrock AgentCore and enterprise AI agents. Use when building or operating agents on AgentCore (Runtime, Memory, Gateway, Identity, Cedar Policy, Code Interpreter, Browser, Harness, Agent Registry), choosing Strands multi-agent patterns (Agents-as-Tools, Swarm, Graph, Workflow), CDK deployment and observability, cost/DR, WAF prompt-injection defense, SharePoint ACL RAG, or AWS vs Azure vs GCP agent platform selection."
---

<!-- argument-hint: [topic, framework name, or chapter number] -->

# AWS AgentCore Guides (Hidekazu Konishi article series)
**Author**: Hidekazu Konishi | **Sources**: 15 articles (~111k words) | **Chapters**: 15 | **Generated**: 2026-10-06

## How to Use This Skill

- **Without arguments** — load core frameworks below
- **With a topic** — e.g. `cedar policy`, `swarm vs graph`, `memory strategies`, `waf rate limit`; I find and read the relevant chapter
- **With chapter** — ask for `ch08`; I load that chapter file
- **Browse** — "what chapters do you have?"

When a question goes beyond the Core section, read the chapter file before answering. Facts are as of the sources (clipped 2026-10, several "verified against primary sources" Sept 2026) — AgentCore moves fast; confirm limits/prices against current AWS docs before committing.

---

## Core Frameworks & Mental Models

### 1. AgentCore is composable — adopt incrementally (ch01)
Agent = **LLM (brain) + Tools (hands) + Memory (storage) + Planning (strategy)**. AgentCore services map onto this: **Runtime** (microVM per session, 8 h max / 15 min idle, ARM64, `/ping` on 8080), **Memory** (Events short-term + async-extracted long-term Memories), **Gateway** (managed MCP over Lambda/OpenAPI/Smithy), **Identity** (inbound *who may call*, outbound *what may be reached*; Token Vault), **Policy** (Cedar), **Code Interpreter / Browser**, **Observability**, **Evaluations**. Start with Runtime; add each layer only when the need appears.

### 2. Who writes the loop? Harness vs Runtime (ch08)
- **Harness** = AWS-written Strands loop as configuration (`CreateHarness`, only `harnessName` + `executionRoleArn` required). 9 settings override per `InvokeHarness`; any other change creates a new immutable version.
- Use Harness for a standard single loop. Use Runtime + your own code when you need Graph/Workflow, bidi streaming or another framework. **Export-to-code** is one-way and drops the harness's input validation — re-implement it.
- `allowedTools` restricts the *model*, not the *API*: `InvokeAgentRuntimeCommand` runs shell in the microVM regardless — close it with IAM.
- Memory defaults are inverted between API (on) and CLI (off) — always set explicitly.

### 3. Three-layer security, rolled out in phases (ch05)
**Identity** (authn) → **Gateway** (tool exposure, `Target___Tool` names) → **Cedar Policy** (authz: default deny, `forbid` > `permit`, JWT claims as tags). Rollout: SigV4 → JWT (`customJWTAuthorizer`) → `LOG_ONLY` → `ENFORCE` (ENFORCE *hides* tools from `list_tools`). **Token hiding**: outer `@tool` has no token param; inner `@requires_access_token` gets it — the token never reaches the LLM. Take the user from JWT `sub`, never from payload `userId`. Use 3LO (USER_FEDERATION) to act as the user, M2M for the agent itself. Never outbound No Auth.

### 4. Memory is two-layer and asynchronous (ch04)
Events = synchronous history (`create_event`/`list_events`); Memories = Semantic / User Preference / Summary strategies extracted 10–30 s+ later into per-user **namespaces**. Default integration: `AgentCoreMemorySessionManager`; Hooks API when filtering; `AgentCoreMemorySaver` for LangGraph. Don't expect same-turn recall — poll or use prior sessions. `runtimeSessionId` ≥16 chars; same ID shares context, different ID isolates.

### 5. Multi-agent: earn it, then pick by path-knowledge (ch07, ch09)
- Go multi-agent only when you can name why: >~20 tools, specialization, parallelism, blast radius.
- **Strands selection**: Can a better single agent do it? → Is the path known? Known + branches/loops → **Graph**; known + linear deps → **Workflow**; unknown + central owner → **Agents-as-Tools** (docstring = routing rule); unknown + peers → **Swarm** (`handoff_to_agent`).
- Compose **deterministic outside, autonomous inside** (Graph wrapping a Swarm). Bound every cycle (`set_max_node_executions`); turn on repetitive-handoff detection.
- On AgentCore: **Supervisor** = one `invoke_sub_agent` tool over `invoke_agent_runtime`, system prompt as routing table; start with 2–3 subs, caution past 5. Cross-team agents → **A2A** with Agent Cards. Guardrails: Shadow Mode → measure FP → ENFORCE.

### 6. Production IaC: split by change rate (ch06)
4 CDK stacks — Foundation / Bedrock / Agent (+observability) / ChatApp. ARM64 CodeBuild + **Lambda Waiter** (custom resource polls build; Runtime depends on waiter). Vended Logs = DeliverySource + DeliveryDestination + Delivery per type (APPLICATION_LOGS, USAGE_LOGS, TRACES). ADOT via `opentelemetry-instrument`; tag spans with `user.id`, `session.id`; enable X-Ray **Transaction Search**. Evaluations: local → on-demand CI gate → online sampled.

### 7. Operate on four signals and four cost buckets (ch10)
Signals: metrics, logs, traces **and quality evaluations** (the one teams skip). Cost buckets: tokens, Runtime vCPU/GB-hours (active-consumption billing), Memory+Gateway ops, observability volume. Levers: **model routing** (30–60% savings), prompt caching (breakpoint after tools, before history), batch, Provisioned Throughput only after 1–3 months on-demand + CRIS. Resilience ladder: retry (never content-filter rejects) → per-dependency circuit breaker → *pre-evaluated* fallback model → CRIS / warm standby → graceful degradation. Deploy gated on quality: new Runtime version → shadow → 5–10% canary → regression eval.

### 8. WAF filters bytes, Guardrails filter meaning (ch11)
Two trust boundaries. WAF: rate limits against **Denial of Wallet** (composite key IP + user sub), Bot Control COMMON, size limits with `oversize_handling=MATCH`, JSON content-type, jailbreak regex kept in COUNT. Guardrails selectively via WAF labels; contextual grounding for indirect injection; output filtering with a streaming tail buffer. Graduate COUNT→BLOCK only after ≥14 days, FP <0.1%, rollback <5 min.

### 9. Governance before discovery (ch12)
Agent Registry: **Governance plane** (all states, IAM) vs **Discovery plane** (APPROVED only, `*Discoverable*` APIs, IAM or JWT). Minimize registries; share via RAM with explicit consumer permission (default share exposes drafts); auth type, JWT URL, KMS key are immutable. Search relevance ≠ trust.

### 10. Enterprise platform choice follows the data's home (ch13–15)
Three-tier deployment: local agents for devs (MCP), cloud UI for staff, event automation. RAG first, fine-tune last. **ACL gap is a connector problem, not an IdP problem**: Bedrock KB has no SharePoint ACL fidelity — use Q Business/Kendra GenAI Index on AWS, or Azure Path B (AI Search indexed ACL) / Path A (Copilot Retrieval API OBO). MS365-centric → Azure primary; GCP for multimodal/cost; AWS when estate/Claude/framework freedom matter. Hedge lock-in with OSS frameworks, LiteLLM, Terraform, MCP (vertical) + A2A (horizontal), OTEL.

---

## Chapter Index

| # | Title | Key Frameworks |
|---|-------|----------------|
| [ch01](chapters/ch01-agentcore-beginners-guide.md) | AgentCore Beginner's Guide | 4 agent elements, incremental adoption, Gateway inbound/outbound, observability hierarchy, limits |
| [ch02](chapters/ch02-agent-engineering-glossary.md) | AI Agent Engineering Glossary | 5-layer agent model, ReAct/Plan-and-Execute, memory types, MCP primitives/transports, eval |
| [ch03](chapters/ch03-bedrock-glossary.md) | Amazon Bedrock Glossary | Converse vs InvokeModel, inference profiles, KB/chunking, Guardrails, Agents Classic, lifecycle |
| [ch04](chapters/ch04-impl-runtime-memory-code-interpreter.md) | Impl Pt1: Runtime, Memory, Code Interpreter | entrypoint, deploy ladder, 5 memory integrations, NDJSON→SSE streaming |
| [ch05](chapters/ch05-impl-identity-gateway-policy.md) | Impl Pt2: Identity, Gateway, Policy | token hiding, JWT 5 steps, Cedar, LOG_ONLY→ENFORCE |
| [ch06](chapters/ch06-impl-cdk-4-stack-observability.md) | Impl Pt3: 4-Stack CDK + Observability | Lambda Waiter, Vended Logs, ADOT, Transaction Search, evaluations |
| [ch07](chapters/ch07-impl-multi-agent-orchestration.md) | Impl Pt4: Multi-Agent Orchestration | Supervisor, A2A, boto3 invoke, Skill System, Voice, Browser, Shadow guardrails |
| [ch08](chapters/ch08-harness-managed-loop.md) | Harness: Managed Loop & Export-to-Code | CreateHarness/InvokeHarness, versions, allowedTools vs IAM, export |
| [ch09](chapters/ch09-strands-multi-agent-patterns.md) | Strands Multi-Agent Pattern Selection | Agents-as-Tools, Swarm, Graph, Workflow, selection flowchart, composition |
| [ch10](chapters/ch10-production-ops-observability-cost-dr.md) | Production Ops: Observability, Cost, DR | 4 signals, cost buckets, model routing, resilience ladder, canary |
| [ch11](chapters/ch11-waf-prompt-injection-defense.md) | AWS WAF for GenAI: Prompt Injection | DoW, rate keys, size limits, WAF+Guardrails, COUNT→BLOCK graduation |
| [ch12](chapters/ch12-agent-registry-ards.md) | Agent Registry & ARD Spec | governance vs discovery plane, approval states, RAM sharing, ARD |
| [ch13](chapters/ch13-enterprise-three-clouds-architecture.md) | Enterprise Pt1: Three Clouds & Architecture | 3-tier deployment, phased RAG, cloud home turf |
| [ch14](chapters/ch14-enterprise-sharepoint-acl.md) | Enterprise Pt2: SharePoint ACL | ACL fidelity ranking, Path A/B, mixed license, AWS ACL options |
| [ch15](chapters/ch15-enterprise-cloud-selection-cost-ops.md) | Enterprise Pt3: Cloud Selection, Cost, Ops | Patterns A/B/C, TCO, lock-in mitigation, MCP vs A2A, quality drift |

## Topic Index

- **A2A / Agent Card** → ch02, ch07, ch09, ch15
- **ACL / SharePoint permissions** → ch13, ch14
- **ADOT / OpenTelemetry / tracing** → ch01, ch06, ch10, ch15
- **Agent Registry / ARD** → ch12
- **Agents Classic (Bedrock Agents) / migration** → ch03, ch08
- **Agents-as-Tools** → ch09
- **allowedTools / InvokeAgentRuntimeCommand** → ch08
- **Bot Control / rate limiting / Denial of Wallet** → ch11
- **Browser tool / CDP form fill** → ch01, ch07
- **CDK / Lambda Waiter / L1 vs L2** → ch06
- **Cedar / Policy Engine / NL2Cedar** → ch05
- **Chunking / Knowledge Bases / reranking** → ch02, ch03
- **Circuit breaker / fallback / DR / warm standby** → ch10
- **Cloud comparison (AWS/Azure/GCP) / TCO** → ch13, ch15
- **Code Interpreter** → ch01, ch04
- **Cognito / JWT / customJWTAuthorizer** → ch05, ch08
- **Converse / InvokeModel / inference profiles / CRIS** → ch03, ch10
- **Cost optimization / model routing / prompt caching** → ch03, ch10, ch15
- **Evaluations / LLM-as-a-Judge / regression** → ch02, ch06, ch10, ch15
- **Gateway / MCP targets / semantic tool selection** → ch01, ch05, ch11
- **Graph / GraphBuilder** → ch09
- **Guardrails / Shadow Mode / grounding** → ch03, ch07, ch10, ch11
- **Harness / export to code** → ch08
- **Identity / Token Vault / 3LO / M2M** → ch01, ch05
- **Lock-in mitigation / LiteLLM** → ch15
- **MCP (primitives, transports, roots, sampling)** → ch02, ch05, ch13, ch15
- **Memory (events, strategies, namespaces, session managers)** → ch01, ch02, ch04
- **Multi-agent selection** → ch02, ch07, ch09
- **Path A / Path B** → ch14
- **Prompt injection / jailbreak / output filtering** → ch02, ch11
- **ReAct / Plan-and-Execute / Reflection** → ch02
- **Runtime (microVM, sessions, versions, endpoints)** → ch01, ch04, ch08, ch10
- **Streaming (NDJSON→SSE, ThinkingFilter)** → ch04
- **Supervisor / sub-agents** → ch02, ch07
- **Swarm** → ch02, ch09
- **Vended Logs / USAGE_LOGS / Transaction Search** → ch06, ch10
- **Voice (Nova Sonic)** → ch07
- **WAF** → ch11
- **Workflow (Strands tool)** → ch09

## Supporting Files

- [glossary.md](glossary.md) — key terms with definitions
- [patterns.md](patterns.md) — techniques and design patterns
- [cheatsheet.md](cheatsheet.md) — decision tree, rules, thresholds, trade-off matrices

---

## Scope & Limits

Covers the content of the 15 source articles only (source front matter dates are clipping artifacts; content dates to 2025–Sept 2026). Prices, limits and preview/GA status change frequently — verify against current AWS/Azure/GCP docs. Article diagrams were images and were not read; their content is reconstructed from surrounding text. For general agent engineering beyond AWS, see `huyen-ai-engineering` and `ai-agents-and-applications`.
