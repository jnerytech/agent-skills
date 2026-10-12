# Chapter 1: Amazon Bedrock AgentCore Beginner's Guide - AI Agent Development from Basics with Detailed Term Explanations

## Core Idea
AgentCore is a framework- and model-agnostic platform of seven loosely coupled services (Runtime, Memory, Gateway, Code Interpreter, Browser Tool, Identity, Observability) that takes over the infrastructure, security, tool-integration and monitoring work of agents. Start with Runtime alone and add services only as requirements appear.

## Frameworks Introduced
- **Four agent elements**: LLM = brain, Tools = hands and feet, Memory = storage, Planning = strategy. *When to use*: decomposing any agent design. *How*: the LLM decides *what* to do, tools *do* it, memory supplies context, planning breaks the goal into ordered steps and re-plans when one fails.
- **Three value propositions**: (1) make agents more effective (Memory, Code Interpreter/Browser, Gateway); (2) scale safely (Runtime serverless + microVM isolation, Identity); (3) operate with confidence (Observability, OpenTelemetry).
- **Composable design / incremental adoption**: Runtime → +Memory → +Gateway → +Observability → +Identity → +Code Interpreter/Browser. Runtime is the foundation, Identity covers security everywhere, Gateway connects inside to outside, Observability watches everything.
- **Two-axis observability**: data type (Metrics / Logs / Spans) × granularity (Session ⊃ Trace ⊃ Span). *How*: debug from coarse to fine: Metrics → Session → Trace → Spans → Logs.
- **Two-stage Gateway authorization**: Inbound = *who* may use the Gateway (JWT or IAM). Outbound = *what* the Gateway may access (IAM SigV4, OAuth 2LO, API Key, No Auth).
- **5-phase development flow**: Design (service selection) → Development (local → Dockerfile → deploy via CLI/SDK) → Integration (Memory strategy, Gateway tools, Identity IdP) → Test & Optimize → Production (a separate prod endpoint, alerts).

## Key Concepts
- **Runtime**: serverless host for agent code. Each session runs in its own **microVM**, which is destroyed and its memory sanitized when the session ends.
- **Runtime version / Endpoint**: versions are immutable, which makes rollback easy. The `DEFAULT` endpoint always points to the latest version, and you create custom endpoints for dev/test/prod.
- **Session**: one user–agent conversation. It ends after a maximum of 8 hours or after 15 minutes idle.
- **Short-term memory**: per-turn **Events** tied to a session ID. They are kept for a configurable period of up to 365 days, even after the session ends.
- **Long-term memory**: extracted asynchronously (Extraction → Consolidation, which can take more than 1 minute). It can be shared per Actor, per Session, or across agents, and is managed with TTL.
- **Memory Strategy**: the rule for turning short-term memory into long-term memory. Options are built-in (Semantic, User Preference, Summary), built-in with overrides (custom prompt/model), or self-managed (your own pipeline).
- **Gateway**: turns OpenAPI, Lambda, Smithy, MCP servers and integration templates into MCP tools behind a single endpoint.
- **Semantic Tool Selection**: Gateway searches thousands of tools and shows the agent only the relevant ones, which keeps prompts smaller and cuts latency.
- **Workload identity**: an agent's own identity (with an ARN) in a hierarchical Workload Identity Directory, used for group-based access control.
- **Token Vault**: KMS-encrypted store for OAuth tokens and API keys. It refreshes tokens automatically, scopes permissions, and logs to CloudTrail.

## Mental Models
- Think of **Bedrock Agent vs AgentCore** as no-code/GUI prototyping vs full code control. They are not mutually exclusive: prototype in Bedrock Agent, then move to AgentCore for production.
- Use **long-term Memory** to answer "who is this user and what happened before". Use **RAG** (Bedrock Knowledge Base) to answer "what do trusted sources currently say". The two complement each other.
- Use **Browser Tool** instead of scraping when pages render with JavaScript, need a login, or need screenshots.
- Use **USER_FEDERATION (3LO)** when acting with the user's permissions, which requires their consent (e.g., their Google Calendar). Use **M2M (2LO)** for the agent's own service-level access.
- Treat agents as **non-deterministic**: the same input can take different reasoning paths and tool choices, so logs alone are not enough. Instrument spans.

## Anti-patterns
- Hardcoding API keys or OAuth tokens in agent code. Use Token Vault instead.
- Outbound **No Auth** to targets (it exists for some MCP servers, but it is not recommended).
- Single sessions that run longer than 8 hours. Split the work into steps, save each step's results in Memory, and use keep-alive or async processing.
- Loading huge datasets at once, which causes OOM. Use smaller batches and streaming instead.
- Unbounded retries and infinite loops, which cause cost spikes. Use CloudWatch cost alarms and resource limits.
- Assuming AWS attestations make a workload compliant (shared responsibility). GDPR is a regulation, not a certification. Check the "Services in Scope" page.

## Reference Tables

**Traditional serverless vs AgentCore Runtime**
| Item | Traditional serverless | AgentCore Runtime |
|---|---|---|
| Execution time | minutes to ~15 min | up to 8 h |
| Payload | several MB to ~10 MB | up to 100 MB |
| State | stateless | session state (8 h max / 15 min idle) |
| Billing | requests + duration | actual CPU time; I/O wait such as LLM waits typically excluded |
| Isolation | process-level | microVM per session |

**Gateway auth**
| Direction | Method | Targets / use |
|---|---|---|
| Inbound | JWT (Cognito, Okta, Auth0…) | external users/apps |
| Inbound | IAM | callers inside AWS |
| Outbound | Gateway service role (IAM SigV4) | Lambda, Smithy, AWS services |
| Outbound | OAuth 2.0 2LO (Client Credentials) | OpenAPI, MCP Server |
| Outbound | API Key | OpenAPI |
| Outbound | No Auth (not recommended) | some MCP servers |

**Gateway's six capabilities**: Security Guard (OAuth), Translation (MCP→API/Lambda), Composition (many tools → one MCP endpoint), Secure Credential Exchange, Semantic Tool Selection, Infrastructure Manager (serverless, observability and audit built in).

**Built-in tool limits**
| Tool | Limits / modes |
|---|---|
| Code Interpreter | 15 min default, up to 8 h; inline upload 100 MB, S3 up to 5 GB; Python 3.12 (100+ libs: pandas, numpy, matplotlib, scikit-learn, torch), TypeScript, JavaScript; network modes Sandbox (no internet, S3 OK) / Public / VPC |
| Browser Tool | Chromium in the cloud, microVM per session; Public network mode only; up to 500 concurrent sessions |

**Identity outbound modes**: `USER_FEDERATION` (3LO, Authorization Code Grant), `M2M` (2LO, Client Credentials Grant), AWS Services (IAM roles). Inbound: IAM SigV4 or OAuth 2.0/OIDC bearer tokens.

**Observability provisioning**: Metrics are emitted by default from all services. Logs are automatic for Runtime, while Memory, Gateway and the built-in tools need configuration. Spans need code instrumentation with **ADOT**. Data goes to CloudWatch (GenAI Observability Dashboard: Agent, Session and Trace views, plus resource graphs) and can be exported via OTel to Datadog, New Relic, Prometheus, Grafana and Splunk.

**Platform additions after GA (2025-10-13)**: Policy and Evaluations (preview 2025-12-02), AWS Agent Registry (preview 2026-04-09), Payments (preview 2026-05-07, GA 2026-08-18), Web Search (GA 2026-06-16), managed harness (GA 2026-06-17), runtime on customer-selected EC2 instance types (GA 2026-08-06).

## Worked Example
**Slow responses, debugged coarse to fine:**
1. Metrics: average latency rose from 2s to 5s.
2. Session: the slowdown appears only in one user's sessions.
3. Trace: the "Salesforce information retrieval" trace is slow.
4. Spans: Gateway→Salesforce takes 4500 ms (normally 500 ms).
5. Logs: "Salesforce rate limit exceeded". Fix with retry and caching.

**Customer support agent**: Identity authenticates the user → Memory supplies past tickets → Gateway + Identity call Salesforce via OAuth → Gateway searches the knowledge base → a Zendesk ticket is created → Memory saves the exchange → Observability traces every step.

## Key Takeaways
1. Pick AgentCore when you need code control, any framework (LangGraph, CrewAI, Strands, custom) or any LLM, plus enterprise security. Pick Bedrock Agent for quick no-code standard patterns.
2. Memorize the Runtime limits: 8 h max session, 15 min idle timeout, 100 MB payload, billing by CPU time only.
3. Long-term memory is asynchronous (more than 1 minute), so do not expect a fact to be recallable in the same turn it was stated.
4. Gateway separates *who can call* from *what it can reach*, and one MCP endpoint can front many backends.
5. Debug in the order Metrics → Session → Trace → Span → Logs. Spans require ADOT instrumentation.
6. When estimating cost, Runtime is driven by CPU time, Memory by events and searches, Gateway by calls and payload, Observability by log volume. Add a 20–30% buffer.
7. Separate environments with endpoints that point at immutable versions.

## Connects To
- ch02 Agent Eng Glossary: generic definitions of memory, tools, MCP, A2A and planning.
- ch03 Bedrock Glossary: Knowledge Bases (RAG), Bedrock Agents, model access.
- ch04 Impl Pt1: hands-on Runtime, Memory strategies, Code Interpreter.
- ch05 Impl Pt2: Identity (3LO/2LO, Token Vault), Gateway inbound/outbound, Policy.
- ch06 Impl Pt3 and ch10 Production ops: ADOT/OTel pipeline, CloudWatch, cost.
- ch07 and ch09: A2A and multi-agent. ch08 Harness. ch12 Agent Registry (post-GA additions).
