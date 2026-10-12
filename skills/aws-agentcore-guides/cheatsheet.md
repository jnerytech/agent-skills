# Cheatsheet — AWS AgentCore Guides

## Decision tree: how should I build this agent?
- Standard single tool-loop, no custom orchestration → **Harness** (ch08); always set `allowedTools`, set memory explicitly
- Need Graph/Workflow/bidi streaming/own framework → **Runtime + Strands/LangGraph code** (ch04) — or export the harness (ch08)
- One agent can't cope (>~20 tools, distinct domains, parallelism, blast radius)?
  - First: can a better single agent do it? (ch09)
  - Path known in advance → branches/loops? **Graph** : **Workflow**
  - Path unknown → central owner? **Agents-as-Tools / Supervisor** : **Swarm**
  - Other team/platform owns the agent → **A2A** (Agent Card) (ch07)
- Discovering agents across teams → **Agent Registry**, governance first (ch12)

## Decision rules
| When | Do | Because |
|---|---|---|
| Work may exceed 8 h | Split into steps, persist state in Memory | Session ends at 8 h / 15 min idle (ch01) |
| Need long-term memory same turn | Poll ≤60 s or use prior session | Extraction is async (ch04) |
| Multi-step tool calls | `read_timeout=900`, `connect_timeout=10` | Defaults too short (ch04, ch07) |
| Just created IAM role / Gateway | Wait ~15 s | IAM propagation → AccessDenied (ch04, ch05) |
| New Cognito pool | Poll OIDC ≤600 s | DNS 5–10 min (ch05) |
| `update_gateway` | Resend every field | Omitted fields reset (ch05) |
| Turning on Cedar | LOG_ONLY first | ENFORCE hides tools, no 403 (ch05) |
| Building images | ARM64 only | x86 crashes on Runtime (ch06) |
| Per-user downstream identity | JWT, not SigV4 | SigV4 doesn't propagate user (ch08) |
| Production IAM | Don't grant `InvokeAgentRuntimeCommand` | Bypasses model and `allowedTools` (ch08) |
| Graph has a cycle | `set_max_node_executions` | Unbounded loop (ch09) |
| Swarm in prod | Enable repetitive-handoff detection | Off (0) by default (ch09) |
| Steps fit a numbered list | Graph/Workflow, not Swarm | Swarm rediscovers path, burns tokens (ch09) |
| Content-filter rejection | Never retry | Same result (ch10) |
| Starting production | On-demand + CRIS 1–3 months, then PT | Avoid over-provisioning (ch10) |
| Changing embedding model | Re-embed whole corpus | Vectors incompatible (ch03) |
| Path B chunking | Map ACL to every chunk | Otherwise not enforced (ch14) |
| Gemini Enterprise data store | Enable ACL at creation | Immutable (ch14) |
| Creating a registry | Decide auth type, JWT URL, KMS key first | Immutable (ch12) |

## Thresholds & defaults
| Item | Value |
|---|---|
| Runtime session | 8 h max, 15 min idle; payload 100 MB; ARM64; `/ping` on 8080 |
| `runtimeSessionId` | ≥16 chars (`{user}_{ts}_{purpose}`) |
| Code Interpreter | 15 min default (3,600 s in SDK), ≤8 h; 100 MB inline, 5 GB via S3 |
| Memory events | retention 7–365 days; CDK seconds vs SDK days |
| Runtime billing | ~$0.0895/vCPU-h, $0.00945/GB-h, per second (ch10) |
| Supervisor | start 2–3 subs, caution >5 |
| Swarm defaults | max_handoffs 20, max_iterations 20, exec 900 s, node 300 s |
| Lambda Waiter | 30 s × 28 polls, 14-min timeout |
| Alerts | error ≥5% for 3×5 min → page; p95 > baseline+50% for 10 min; quota ≥60% |
| Online eval sampling | 100% dev, 10–30% prod; 50–200 regression cases |
| Canary | 5–10% traffic |
| WAF rate limits | chat 60/5 min, expensive agent 10/5 min; body 128 KB, prompt 8 KB |
| WAF graduation | COUNT ≥14 days (regex ≥4 weeks), FP <0.1%, rollback <5 min |
| Guardrails FP | <1% on 50 legit + 50 attack |
| Chunking start | ~300 tokens, ~20% overlap |
| Cost estimate | +20–30% buffer; model routing saves 30–60% |

## Trade-off matrix: multi-agent patterns (ch09)
| | Agents-as-Tools | Swarm | Graph | Workflow |
|---|---|---|---|---|
| Determinism | Medium | Low | High | High |
| Token cost | Medium | Highest | Low–Med | Low |
| Parallelism | Via tools | No | Yes | Auto |
| Loops/branches | LLM-decided | Emergent | Bounded | No |
| Best for | One conversation owner | Open-ended triage | Gated processes | Reports/batch |

## Cloud selection (ch13–15)
| Situation | Pick |
|---|---|
| MS365/SharePoint-centric, strict ACL | Azure primary (Pattern A) |
| + multimodal or high volume/low cost | Azure + GCP (Pattern B) |
| Existing AWS estate, Claude, framework freedom | AWS (AgentCore) |
| Large org, per-workload strengths | Distributed (Pattern C) — highest ops cost |
| SharePoint ACL on AWS | Q Business / Kendra GenAI Index — **not** Bedrock KB (ACL fidelity 0) |

## Tells & smells
- Tool returns 200 OK with error inside → retry storm (ch10)
- `retrieve_memories` empty right after `create_event` → extraction lag, not a bug (ch04, ch10)
- Tools "disappeared" after policy change → ENFORCE trimming (ch05)
- Graph silently skips steps → wording-matching condition functions (ch09)
- Oversized bodies passing WAF → `oversize_handling` left at CONTINUE (ch11)
- Ignored model deprecations → most common Bedrock outage cause (ch03)
- Agent fails tool calls → wrong OpenAPI schema (ch03)
