# Patterns — AWS AgentCore Guides

## Incremental AgentCore Adoption (ch01)
**When to use**: Any new agent.
**How**: Runtime → +Memory → +Gateway/Identity → +Observability → +Code Interpreter/Browser → Policy/Evaluations.
**Trade-offs**: Each layer adds cost/config; full stack only for enterprise.

## Memory via SessionManager (ch04)
**When to use**: Default multi-turn memory in Strands.
**How**: `AgentCoreMemorySessionManager` passed as `session_manager=`; strategies + per-user namespace. Use Hooks API when you must filter tool/thinking content; `AgentCoreMemorySaver` for LangGraph.
**Trade-offs**: Long-term extraction is async (10–30 s+) — poll or use prior-session memories.

## Context-managed Code Interpreter (ch04)
**When to use**: Any sandbox computation.
**How**: Fetch data via MCP tools first (sandbox has no outbound net), run code in `code_session`, `stop()` in `finally`.
**Trade-offs**: Session start cost per run.

## Token Hiding (two-layer function) (ch05)
**When to use**: Agent calls OAuth-protected APIs.
**How**: Outer `@tool` with no token param → inner `@requires_access_token` function receives token from Token Vault.
**Trade-offs**: One wrapper per tool; token never reaches the LLM.

## Phased Policy Rollout (ch05)
**When to use**: Moving to production authz.
**How**: SigV4 → JWT (`customJWTAuthorizer`) → Cedar `LOG_ONLY` → `ENFORCE`; user from JWT `sub`, not payload.
**Trade-offs**: ENFORCE silently hides tools — validate in LOG_ONLY first.

## 4-Stack CDK by Change Rate (ch06)
**When to use**: Production IaC.
**How**: Foundation / Bedrock / Agent(+observability) / ChatApp; `CfnOutput` + `Fn.importValue`; ARM64 CodeBuild; Lambda Waiter (30 s × 28, 14 min).
**Trade-offs**: Cross-stack exports lock; slow Agent stack deploy (~8 min).

## Supervisor + Sub-agents (ch07)
**When to use**: >~20 tools or distinct domains, same owner.
**How**: Supervisor has one `invoke_sub_agent` tool wrapping `invoke_agent_runtime`; system prompt = routing table; start with 2–3 subs.
**Trade-offs**: ≥2× tokens; routing degrades past ~5 subs.

## Strands Pattern Selection (ch09)
**When to use**: Choosing multi-agent topology.
**How**: Single agent first → path known? (branches/loops ⇒ Graph, else Workflow) : (central router ⇒ Agents-as-Tools, peers ⇒ Swarm). Compose Graph outside, Swarm inside.
**Trade-offs**: Swarm = most tokens, nondeterministic; Graph cycles need `set_max_node_executions`.

## Harness → Export-to-Code (ch08)
**When to use**: Standard single loop now, custom orchestration later.
**How**: Declare harness, always set `allowedTools`, memory explicitly; export to Strands when you outgrow it; re-implement input validation.
**Trade-offs**: No graph/workflow/bidi streaming in harness; export is one-way.

## Layered Resilience (ch10)
**When to use**: Production reliability.
**How**: Retry (never on content filter) → circuit breaker per dependency → pre-evaluated fallback model → CRIS / warm standby → graceful degradation (reduced capability, read-only).
**Trade-offs**: Fallback quality must be evaluated; DR replication effort.

## Model Routing (ch10, ch15)
**When to use**: Mixed-difficulty traffic.
**How**: Cheap model (Nova Micro/Haiku/Flash-Lite) for FAQ → mid (Sonnet/Nova Pro) → premium with budget cap.
**Trade-offs**: 30–60% savings vs routing-error quality risk.

## Quality-gated Deployment (ch10)
**When to use**: Every release.
**How**: New Runtime version → shadow → 5–10% canary on named endpoint → regression eval (50–200 cases, block on high-severity) → promote.
**Trade-offs**: Manual promotion; eval cost.

## WAF + Guardrails Two-Layer Defense (ch11)
**When to use**: Public GenAI endpoints.
**How**: WAF: rate limit (composite key IP+`x-user-sub`), Bot Control COMMON, size limits (`oversize_handling=MATCH`), JSON content-type, regex in COUNT → Guardrails selective via WAF labels → output filtering with streaming tail buffer.
**Trade-offs**: WCU cost per key; regex false positives; graduate COUNT→BLOCK after ≥14 days, FP <0.1%.

## Registry Governance Before Discovery (ch12)
**When to use**: Many teams publishing agents/MCP servers.
**How**: Few registries (dev auto-approve, prod curated); RAM share with explicit ForConsumer permission; consumers use Discoverable APIs; decide auth type/JWT/KMS upfront.
**Trade-offs**: Each registry split adds a discovery call; immutable settings.

## One RAG, Many Access Paths (ch13)
**When to use**: Enterprise with mixed user tiers.
**How**: Shared index → cloud UI (staff), MCP server (developers), event-driven automation; specialized agents per task.
**Trade-offs**: More surface to secure.

## Two-Tier SharePoint ACL / Mixed License (ch14)
**When to use**: MS365 enterprises needing permission-trimmed RAG.
**How**: Path B (AI Search + per-chunk ACL, fail-closed) baseline; Path A (Copilot Retrieval API OBO) for sensitive docs/Copilot licensees; route by license.
**Trade-offs**: Path B lags indexer, no SharePoint groups; Path A needs per-user license.

## Lock-in Mitigation (ch15)
**When to use**: Multi-cloud or future-proofing.
**How**: OSS frameworks (LangGraph/CrewAI/Strands), LiteLLM, Kubernetes, Terraform, MCP/A2A, MLflow/W&B, OTEL.
**Trade-offs**: Loses some managed-service convenience.
