# Chapter 11: AWS WAF for Generative AI - Prompt Injection Defense Implementation Patterns

## Core Idea
WAF cannot understand a prompt, but it can keep cheap, automated, economically motivated traffic out of the inference path. Layer it: WAF (byte-level, pre-inference) stops volume and obvious payloads; Bedrock Guardrails (semantic, in-path) stops what gets through; output filtering catches leaks; logs tie it together. Every rule starts in `COUNT`.

## Frameworks Introduced
- **Six Defense Patterns** (priority order in the Web ACL):
  1. Rate-based rule + Bot Control against Denial of Wallet (per-identity composite keys).
  2. Input size + Content-Type restrictions (cap prompt bytes before tokenization).
  3. Regex pattern set for known jailbreak phrases (raise cost of automation, not a semantic firewall).
  4. Lambda pre-screening classifier (triage, not adjudication; <30 ms p99).
  5. WAF + Bedrock Guardrails two-layer defense (separate trust boundaries).
  6. Output filtering (Lambda@Edge for short JSON; in-app streaming redaction otherwise).
- **Rule Graduation Checklist** (COUNT → BLOCK, team review gate): ≥14 days in COUNT incl. a Monday peak; FP rate <0.1% by human review of sampled bodies; blast radius calculated and accepted by product owner; rollback to COUNT tested in non-prod, effective within 5 min; `BlockedRequests` alarm firing within 1 min at 2x COUNT baseline; runbook updated.
- **Selective Guardrails (two-tier)**: prompt-attack + denied topics on all requests; full policy (PII, grounding, content filters) only for requests labeled by a COUNT-mode WAF regex (read via `x-amzn-waf-label` header).
- **Penetration Testing Runbook**: isolated account with prod Web ACL → jailbreak corpora (verazuo/jailbreak_llms, garak) in COUNT, map to OWASP LLM Top 10 → synthetic token floods → oversized/malformed/base64 payloads → correlate WAF, Guardrail, redaction logs per request ID → promote at FP <0.1%.

## Key Concepts
- **Denial of Wallet (DoW)**: bots burning inference budget with max-token, legitimate-looking requests; the threat WAF mitigates best.
- **Indirect prompt injection**: instructions hidden in fetched URLs, uploads, RAG chunks; WAF has low leverage — use Guardrails contextual grounding and `apply_guardrail` with `source="INPUT"` on retrieved content.
- **RateBasedStatement**: per-5-min count per aggregate key (IP, header, JA4, `CUSTOM_KEYS`); actions `BLOCK`/`COUNT`/`CHALLENGE`.
- **SizeConstraintStatement / `oversize_handling`**: default `CONTINUE` silently passes bodies beyond the inspection limit; set `MATCH`.
- **Inspection limit**: ALB/AppSync 8 KB fixed; CloudFront, API Gateway, Cognito, App Runner, Verified Access 16 KB default, raisable to 64 KB via `AssociationConfig`.
- **AgentCore Gateway WAF association** (since 2026-06-29): regional web ACL only, same Region, gateway `READY`, one ACL per gateway; `failureMode` defaults to `FAIL_CLOSE`.
- **`Monetize` action** (since 2026-06-15): terminating, returns HTTP 402 and settles payment in-request; requires Bot Control classification first.
- **No AWS "Generative AI" managed rule group** exists (as of 2026-08); Salt Security Marketplace group covers MCP/API security but claims no prompt-injection detection — build-vs-buy decision.
- **`guardrail_intervened`**: stop reason when Guardrails fires; input tokens consumed, no output tokens.

## Mental Models
- Think of WAF as an economic filter and Guardrails as a semantic one; neither substitutes for the other — Guardrails cannot stop a bot from sending the request.
- Use `CHALLENGE` before `BLOCK` when false positives hit shared NAT/corporate proxies or consumer users; add a higher threshold (e.g., 300/5 min) in `BLOCK` for clear abuse.
- Guardrail over-blocking is harder to see than WAF over-blocking: no 403, just a canned refusal.
- Use Lambda@Edge output filtering only for short non-streaming JSON; for LLM responses, redact in the application streaming handler.

## Anti-patterns
- BLOCK without COUNT bake-in.
- Rate-limiting on IP alone (mobile carriers, proxies).
- Scope mismatch: CLOUDFRONT-scope ACL must be in `us-east-1`; regional for API Gateway/ALB/AppSync/AgentCore Gateway.
- Treating Guardrails as input validation.
- Ignoring SSE/chunked responses in output filters.
- Leaving `oversize_handling` default, or setting `MATCH` on size rule but not on the regex rule on the same JSON path.
- Long regex lists (FP driver); matching the whole body instead of `/messages/*/content`.
- Heavy ML models inline in the pre-screen Lambda.

## Code Examples
Rate limit per authenticated subject (CloudFormation):
```yaml
RateBasedStatement:
  Limit: 60                # requests per 5 minutes
  EvaluationWindowSec: 300
  AggregateKeyType: CUSTOM_KEYS
  CustomKeys:
    - IP: {}
    - Header: { Name: x-user-sub, TextTransformations: [{ Priority: 0, Type: NONE }] }
```
What it demonstrates: composite-key DoW cap; 2 + 30×2 = 62 WCU.

Prompt field cap (Terraform): `json_body { match_pattern { included_paths = ["/messages/*/content"] } match_scope = "VALUE" invalid_fallback_behavior = "MATCH" oversize_handling = "MATCH" }`, `comparison_operator = "GT"`, `size = 8192`; body cap `size = 131072`.

Jailbreak regex rule: `RegexPatternSetReferenceStatement` on `/messages/*/content`, `InvalidFallbackBehavior: NO_MATCH`, transformations `LOWERCASE` + `COMPRESS_WHITE_SPACE`, `Action: { Count: {} }`. Pattern set holds four case-insensitive regexes covering the classes: instruction-override ("ignore previous instructions"), persona switch (DAN/developer mode), disregard-system/safety-prompt, and verbatim system-prompt extraction.

Pre-screen scoring: regex heuristics +1 each; base64 runs `[A-Za-z0-9+/]{200,}={0,2}` decoded and rechecked +2; `verdict = "BLOCK" if score >= 2 else "CHALLENGE" if score == 1 else "ALLOW"` (first sprint: BLOCK at ≥3, CHALLENGE/log at 2).

Guardrail in Converse + offline test:
```python
client.converse(modelId="us.anthropic.claude-sonnet-4-5-20250929-v1:0",
    guardrailConfig={"guardrailIdentifier": "abcd1234", "guardrailVersion": "DRAFT", "trace": "enabled"}, ...)
bedrock.apply_guardrail(guardrailIdentifier="abcd1234", guardrailVersion="DRAFT",
    source="INPUT", content=[{"text": {"text": "..."}}])  # action: GUARDRAIL_INTERVENED | NONE
```
Streaming redaction: keep a `tail` buffer of `MAX_PATTERN_LEN` (≥ longest match, e.g. 20 for `AKIA[0-9A-Z]{16}`) across `contentBlockDelta` chunks; emit `buf[:-MAX_PATTERN_LEN]`, flush redacted tail at end. Semantic PII → `comprehend.detect_pii_entities` after stream completes.

Early-warning metric filter: `{ ($.action = "ALLOW") && ($.terminatingRuleId = "Default_Action") }` → `GenAI/WAF` `AllowedToDefaultAction`; alarm at p99 baseline + 3σ over 10 min.

## Reference Tables
| Threat | WAF leverage |
|---|---|
| Direct prompt injection | Partial (phrases, oversized input) |
| Indirect prompt injection | Low (Guardrails, tool sandboxing) |
| Jailbreak / persona override | Medium (regex + Lambda pre-screen) |
| Data exfiltration | Output filtering + Guardrails sensitive-info |
| Denial of Wallet | High (rate rules, size, Bot Control) |
| Model DoS | Medium (size/structure limits, app concurrency caps) |
OWASP LLM 2025 mapping: LLM01 Prompt Injection, LLM02 Sensitive Info Disclosure, LLM04 Data/Model Poisoning, LLM07 System-Prompt Leakage, LLM10 Unbounded Consumption.

| Cost item | Number |
|---|---|
| WCU limit per Web ACL | 5,000 |
| Rate rule | 2 WCU + 30/custom key |
| Regex rule | 25 base, 50 on JSON body, +10/transformation (per rule, not per pattern) |
| Size rule | 1 WCU; CommonRuleSet 700, KnownBadInputs 200, BotControl COMMON 50, AnonymousIpList 50 |
| WAF price | $5/ACL/mo + $1/rule + $0.60/M requests (5-rule stack @5M req ≈ $13/mo) |
| Bot Control | $10/mo; COMMON $1/M (10M free); TARGETED +$10/M (1M free) — start COMMON |
| Guardrails | per 1,000-char text unit, in/out separate: content filters $0.15/1K TU, sensitive info $0.10/1K TU (~$3,000/mo @100K req/day) |
| Lambda pre-screen | ~$30–40/mo @100K req/day; alarm Duration p99 at 25 ms |
| Lambda@Edge | viewer 40 KB / origin 1 MB body; 5 s viewer-response; 128 MB; +20–50 ms; author in `us-east-1` |

| Gateway block surface | Response |
|---|---|
| MCP target blocked | JSON-RPC `-32002` "Authorization error - Request forbidden" |
| HTTP/passthrough blocked | HTTP 403 |
| WAF 5xx to MCP | JSON-RPC `-32603` |

## Worked Example
Cost Anomaly alert: Bedrock spend up 8x in 6 h. (1) WAF Logs Insights: per-IP `count_if(action="ALLOW")` vs blocked — high allowed/low blocked means traffic is reaching Bedrock. (2) Guardrail interventions per hour from Model Invocation Logging (`output.outputBodyJson.trace.guardrail.*`) or app-emitted logs — high interventions + low WAF blocks = paying input tokens for every attack. (3) Suspect-IP volume vs 7-day baseline pinpoints start hour; inspect sampled requests. (4) Confirm `RateLimitAuthenticatedUser` never fired → attacker stayed under threshold; lower it and re-validate in COUNT. (5) Add the `AllowedToDefaultAction` metric filter + alarm. Extend with EMF `InputTokens`/`OutputTokens` per `requestId` to chart spend vs WAF pass-through; alarm at 3σ over rolling 7-day p95. Join key: `x-amz-cf-id`, or a UUID minted at the first hop when CloudFront is bypassed.

## Key Takeaways
1. DoW is the highest-leverage WAF use: per-identity composite keys; size to a normal user's worst day (60/5 min chat, 10/5 min expensive agent).
2. Cap body (128 KB) and prompt field (8 KB) with `oversize_handling = MATCH`; pin `application/json` — can go straight to BLOCK.
3. Regex catches the lazy tier only; keep it short, scoped, in COUNT ≥4 weeks; refresh quarterly.
4. Guardrails: target FP <1% on 50 legit + 50 attack inputs via `ApplyGuardrail`; contextual grounding/relevance thresholds start at 0.7, tune in 0.05 steps.
5. For AgentCore Gateway, one regional ACL covers every downstream tool; keep `FAIL_CLOSE` unless availability truly outranks security.
6. Log WAF → Firehose → S3 + CloudWatch (30-day retention), enable Bedrock Model Invocation Logging, alarm at >1% block rate per 10 min.

## Connects To
- ch05 (Gateway, Cedar policy as the true boundary), ch10 (prompt-injection layering, WAF at front door, cost anomaly runbook), ch12 (MCP/agent governance), ch13 (enterprise identity/gateway design).
