# Chapter 10: Amazon Bedrock AgentCore Production Operations Guide - Observability, Cost Optimization, and Disaster Recovery

## Core Idea
Taking an AgentCore agent from PoC to production means answering three problems invisible at PoC scale (non-determinism, cost variance, failure surface) with eight operational disciplines: four-signal observability, cost decomposition, a failure taxonomy, layered resilience, session-based capacity planning, security hardening, quality-gated deployment, and runbooks.

## Frameworks Introduced
- **Four-Signal Observability Model**: metrics + application logs + traces + quality evaluations, together. When: before any other ops work. How: enable CloudWatch Transaction Search (once per account/Region); create `CfnDeliverySource`/`CfnDeliveryDestination`/`CfnDelivery` for `APPLICATION_LOGS`→CloudWatch Logs, `TRACES`→X-Ray, `USAGE_LOGS`→Firehose; add OTel (automatic on Runtime; `aws-opentelemetry-distro` + `opentelemetry-instrument python -m my_agent` elsewhere).
- **Four Cost Buckets, Four Owners**: model tokens / Runtime vCPU+GB-hours / Memory+Gateway ops / observability volume. When: "the agent is too expensive". How: decompose the bill, assign an owner and a lever per bucket.
- **Three-Route Model Routing**: Route 1 trivial (Nova Micro/Lite, Claude Haiku 4.5, <200 output tokens), Route 2 reasoning+tool selection (Claude Sonnet 4.5 / Nova Pro — most tokens), Route 3 hard fallback (Claude Opus 4.x behind a budget guardrail). How: a tiny Nova Micro classification call first, then switch. Typical saving 30–60% vs single large model (measure on your eval set).
- **Failure Taxonomy (7 classes)**: model-side (throttling, content filter, deprecation, long-tail latency), tool-side (timeout, semantic failure → retry storm, quota exhaustion), Runtime-side (cold start, `/ping` health-check failure on 8080, memory extraction lag), cross-cutting (identity/authz, network partition).
- **Layered Resilience (in series, not alternatives)**: adaptive retry with backoff+jitter → per-dependency circuit breaker → pre-validated fallback model → CRIS / multi-Region → graceful degradation.
- **Quality-Gated Deployment**: blue/green via runtime versions+endpoints, canary 5–10% at the front layer, shadow mode, regression evaluation as CI gate.
- **Cost Triage Checklist** (in order): token distribution WoW → tool invocations/session → vCPU-hours/agent → Memory event growth → observability volume itself.

## Key Concepts
- **GenAI Observability dashboard**: CloudWatch surface with a Bedrock AgentCore tab (Preview in 2026) showing traces per session.
- **USAGE_LOGS**: canonical billing dataset (vCPU/GB-seconds per session) delivered to Firehose→S3; never downsample it.
- **`agent.runtime.vcpu.hours.used`**: OTel span attribute for cost; if not a CloudWatch metric in your account, use Athena on USAGE_LOGS or a Metric Filter.
- **Active-consumption billing**: Runtime, Code Interpreter, Browser bill per second at `$0.0895`/vCPU-hour and `$0.00945`/GB-hour (Apr 2026; re-verify); idle I/O wait still accrues GB-hours.
- **Retry storm**: LLM repeatedly retries a tool that returned 200 OK with an ambiguous error payload.
- **Memory extraction lag**: `retrieve_memories` empty right after `create_event`; long-term memory is for the *next* session.
- **CRIS**: Cross-Region Inference via `us.`/`global.` model ID prefixes; smooths throttling and gives intra-profile failover, but breaks data residency.
- **Runtime versions/endpoints**: `CreateAgentRuntimeVersion` / `CreateAgentRuntimeEndpoint`; no Lambda-style aliases — an endpoint routes 100% to its bound version.
- **Shadow mode deployment**: duplicate 100% of traffic to the candidate, return only the current agent's answer, diff offline.
- **Warm standby**: second Region from the same CDK stack, `desiredCount=1`, no traffic; failover swaps DNS (Route 53 / ARC) and scales up.

## Mental Models
- Think of the agent as "can be perfectly available and still wrong" — the evaluation signal is what traditional APM lacks.
- Use concurrent sessions, not RPS, as the capacity unit: 1,000 active users ≈ 1,000 concurrent sessions.
- Treat model-layer defenses (guardrails, system-prompt policies) as filters; treat Cedar tool authorization as the only adversarial-robust security boundary.
- Think of a cost anomaly as a leading indicator of a quality or reliability problem.
- Use CloudWatch GenAI Observability as the default debug surface and your third-party APM (Datadog, Dynatrace, LangSmith, Langfuse, OTLP) as the org-wide alerting/SLO surface; keep `service.name`, `deployment.environment`, `service.version` consistent.

## Anti-patterns
- Porting APM thinking and skipping quality evaluations.
- Telling on-call to "look at CloudWatch" without the exact session-ID → Trace View path.
- Retrying content-filter rejections (same result, wasted tokens).
- One circuit breaker shared across all dependencies.
- Fallback model never run through the evaluation suite (silent quality drop).
- Buying Provisioned Throughput before real traffic data (over-provisions).
- `bedrock:InvokeModel` on `*`; broad S3 read on prod buckets.
- Granting a tool the union of all users' permissions and relying on the prompt to filter.
- Mixing shared and tenant-dedicated log groups in one workload.
- 100% online evaluation (roughly doubles per-session cost).
- Alarming on causes (CPU, log counts) instead of symptoms; alarms without runbooks.

## Code Examples
```python
model = BedrockModel(
    model_id="us.anthropic.claude-sonnet-4-5-20250929-v1:0",
    boto_client_config=Config(read_timeout=900, connect_timeout=10,
                              retries=dict(max_attempts=3, mode="adaptive")),
)
```
What it demonstrates: SDK adaptive retry instead of handwritten loops; long read timeout for agent calls.

```python
@dataclass
class CircuitBreaker:
    failure_threshold: int = 5
    cooling_seconds: float = 30.0
    failures: int = 0
    opened_at: float = 0.0
    def allow(self) -> bool:
        if self.failures < self.failure_threshold: return True
        if time.monotonic() - self.opened_at > self.cooling_seconds:
            self.failures = 0  # half-open probe
            return True
        return False
```
What it demonstrates: fail-fast per dependency (model client, each `@tool`, MCP Gateway client). Production: single-flight lock on half-open, failure counts in DynamoDB with short TTL. Fallback routing: `PRIMARY` Sonnet → `FALLBACK = "us.amazon.nova-pro-v1:0"` only on `{"ThrottlingException","ServiceUnavailableException","ModelTimeoutException"}`; other errors re-raise.

Tool error contract: `{"status": "error", "message": "..."}`. Tenant isolation in Cedar: `permit(principal, action, resource) when {principal.tenant_id == resource.tenant_id};`

Alarm (CDK): `MathExpression("100 * errors / IF(invocations > 0, invocations, 1)")` over `AWS/BedrockAgentCore` `InvocationErrorCount`/`InvocationCount`, `threshold=5`, `evaluation_periods=3`, `datapoints_to_alarm=3`, `treat_missing_data=NOT_BREACHING`, runbook URL in `alarm_description`.

## Reference Tables
| Indicator | Threshold pattern |
|---|---|
| Session count (5-min) | Trend; sudden drop = upstream auth failure |
| p50/p95/p99 latency per agent | p95 baseline +50% |
| Error rate per class | <1% rolling 1 hr |
| Tokens per session / tool calls per session | Distribution (prompt bloat / retry storms) |
| vCPU-hours per agent | Trend |
| Online eval score | Rolling 24 hr |

| Telemetry | Default |
|---|---|
| APPLICATION_LOGS | 30 days prod, 7 days dev |
| TRACES | 100% dev; adaptive sampling past ~10M spans/month |
| USAGE_LOGS | 100% always |
| Online evaluation | 10–30% sample |

| Throughput mode | Best for | Caveat |
|---|---|---|
| On-demand | Variable/early prod | Quota throttling at peaks |
| Provisioned Throughput | Predictable peak, latency-sensitive | Multi-month commitment |
| CRIS | Regional spike smoothing | Slight latency variance |

| Runbook | Trigger |
|---|---|
| Elevated error rate | ErrorRate ≥5% for 3 consecutive 5-min windows |
| Latency spike | p95 > baseline +50% for 10 min |
| Cost anomaly | AWS Cost Anomaly Detection on Bedrock / bedrock-agentcore |
| Quality regression | Online `Correctness` below baseline 24 h |

## Worked Example
Cost anomaly runbook: alert fires → Athena on `agentcore_usage_logs` (`SUM(billed_vcpu_seconds)/3600.0 AS vcpu_hours ... GROUP BY agent_name, hour`) identifies the agent → walk the triage checklist, stop at the first explanation → token widening: revert prompt; memory blow-up: age out via `event_expiry_days` (Python SDK; `eventExpiryDuration` in seconds via CDK L1); retry storm: force-open the tool's breaker → file postmortem. Error-rate runbook branches similarly: throttling (quota >80% → increase or shift via CRIS), content-filter (guardrail changed in last 24 h), one tool's 5xx (trip breaker), evenly spread (roll endpoint back to prior version).

## Key Takeaways
1. Set up all four signals first; runbooks cannot execute without them. Filter by `deployment.environment` and `agent.name`.
2. Cost control = model routing, prompt caching (breakpoint after system prompt + tools, before history; watch cache-hit-rate drop as invalidation signal), tool-call discipline; Batch Inference ~50% cheaper for non-real-time.
3. Resilience is layered: retry, breaker, validated fallback, CRIS/warm standby, then capability-reduced answers or read-only mode.
4. Start on-demand with `us.` CRIS for 1–3 months; alarm on quotas at 60%.
5. Deploy with a quality gate: 50–200 eval cases (`Builtin.Correctness`, `Builtin.Helpfulness`, custom tool-selection), block on high-severity regressions, grow the suite with every fixed bug.
6. Region-pin tenants under data sovereignty (no CRIS prefix); prefix Memory namespaces `/{tenant_id}/{user_id}/...`; correlate `session.id` with CloudTrail `eventID`.

## Connects To
- ch04 (session ID pattern, Memory, health check), ch05 (Cognito/Cedar baseline), ch06 (Vended Logs/Firehose pipeline, on-demand evaluation), ch07 (supervisor, Shadow Mode guardrails), ch11 (WAF at front door — Runtime hosts none), ch15 (cloud ops/cost).
