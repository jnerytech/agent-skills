# Chapter 15: Enterprise AI Agent Environment Design Notes Part 3 — Cloud Selection, Cost, and Operations

## Core Idea
No single cloud wins on every dimension, so pick the cloud per workload and connect them with the open protocols MCP (vertical: agent↔tools) and A2A (horizontal: agent↔agent). For M365 organizations: Azure is primary, GCP is a complement for multimodal and cheap high-volume inference, and AWS is a conditional supplement for an existing AWS estate or deep Claude use. Then control TCO with model routing and discounts, reduce lock-in (including **context lock-in**), and run continuous evaluation.

## Frameworks Introduced
- **Use-case → cloud mapping**: see quick-reference table below. Existing data and contracts can override it.
- **Multi-cloud Patterns**:
  - **Pattern A, Azure-led**: the default for M365 organizations that need SharePoint/Teams/Copilot and have no heavy multimodal or high-frequency needs. Simple, with low overhead.
  - **Pattern B, Azure-led + GCP supplement**: Azure for SharePoint RAG, GCP for multimodal and high-frequency inference. Good balance of cost and capability.
  - **Pattern C, Distributed AI inference**: large organizations using each cloud's strengths. Operational complexity is much higher, so it needs a team with multi-cloud experience.
- **ACL Strictness Levels**: L1 department separation → Path B. L2 rapid revocation on role change or departure → Path B + high-frequency indexer + resync API. L3 audit-bound, where leakage is a legal risk → two-layer Path A + Path B.
- **Six Lock-in Mitigations**: (1) framework-neutral agent logic (LangGraph, CrewAI); (2) a model abstraction layer (LiteLLM); (3) containerize everything (Kubernetes); (4) cloud-neutral IaC (Terraform); (5) MCP/A2A for agent communication; (6) neutral experiment tracking (MLflow, Weights & Biases).
- **Agent Evaluation Workflow**: continuous evals to catch **quality drift** from model updates, RAG data changes, and shifting query patterns.

## Key Concepts
- **MCP**: Anthropic → Agentic AI Foundation (Linux Foundation, Dec 2025). Vertical agent↔tool/data integration. GA.
- **A2A (Agent2Agent)**: Google → A2A Protocol Project (Linux Foundation, June 2025). Horizontal agent↔agent integration. v1.0 GA March 2026; AWS, Microsoft, Google, Salesforce, and SAP participate.
- **Context lock-in**: conversation history, preferences, and eval data stored in vendor-proprietary formats that are hard to migrate.
- **Model routing**: send FAQ/routing queries to Gemini 2.5 Flash-Lite and complex reasoning to Claude Sonnet.
- **CUD (Committed Use Discounts)**: GCP discount of up to 55% (70% for select resources). Sustained Use Discounts apply automatically.
- **VPC-SC Service Perimeter**: GCP exfiltration protection against stolen credentials or IAM misconfiguration, at no charge (Private Endpoints and VPC Endpoints are paid).
- **AgentCore Evaluations**: 13 built-in evaluators (Helpfulness, Tool Selection Accuracy, Hallucination Rate). OTEL-compatible tracing to CloudWatch.
- **OpenTelemetry**: supported by all three clouds, which lets you build one observability layer across clouds.
- **BigQuery Omni**: queries data across multiple clouds.

## Mental Models
- Think of MCP as vertical (agent→tools) and A2A as horizontal (agent↔agent). Both are open under the Linux Foundation, so protocol choice never constrains cloud choice.
- Agents collaborate cross-cloud without exposing internals, which preserves IP and data privacy.
- Align the AI platform with your data gravity: BigQuery → GCP, Fabric/Power BI → Azure, Redshift/S3 → AWS.
- Per-token price gaps compound at volume, so routing matters more than picking a single model.
- AI agents aren't "build and forget". Monitor latency, cost, quality, and hallucination rate continuously.

## Anti-patterns
- Choosing Pattern C without multi-cloud operations experience.
- Using one premium model for all traffic.
- Committing to Preview APIs (Azure AI Search ACL) or soon-deprecated models without checking GA and lifecycle dates. `gemini-2.5-flash-lite` stable is scheduled for deprecation in Oct 2026; its successor is Gemini 3.1 Flash-Lite Preview.
- Storing agent context only in proprietary formats.
- Skipping drift detection after launch.

## Reference Tables
**Use-case quick reference**
| Use case | 1st | 2nd | Why |
|---|---|---|---|
| Internal doc RAG (SharePoint) | Azure | — | Native ACL / Purview |
| Customer support bot | AWS | Azure | Claude + low latency (sub-200ms) + AgentCore, 8h sessions |
| Code generation | Azure | AWS | GitHub Copilot + Azure DevOps |
| Data analytics/BI | GCP | Azure | BigQuery/AutoML; Azure if Power BI central |
| Workflow automation | Azure | AWS | Power Automate/Logic Apps 1,400+ connectors |
| Multimodal | GCP | Azure | Gemini Live / Veo / Imagen / Chirp 3 (custom voice from 10-s sample) |
| High-volume inference cost | GCP | AWS | Flash-Lite $0.10/M |
| Governance | Azure | AWS | Purview/Entra/Defender |

**Protocol support**: Foundry has MCP and A2A (via Copilot Studio), with Semantic Kernel. AgentCore has MCP (MCP Gateway, IAM-authenticated) and A2A, with LangGraph, CrewAI, etc. Vertex has MCP and A2A (it originated A2A), with ADK.

**Token pricing (per 1M, input/output)**
| Model | Platform | In | Out |
|---|---|---|---|
| GPT-4o | Foundry | $2.50 | $10.00 |
| Claude Sonnet 4.6 | Foundry/Bedrock | $3.00 | $15.00 (>200K input on Bedrock: $6.00/$22.50) |
| Claude Haiku 4.5 | Foundry/Bedrock | $1.00 | $5.00 |
| Gemini 2.5 Flash | Vertex | $0.30 | $2.50 |
| Gemini 2.5 Flash-Lite | Vertex | $0.10 | $0.40 |
| Gemini 2.5 Pro | Vertex | $1.25 | $10.00 (>200K: $2.50/$15.00) |
GPT-5.4 output is $15.00.

**Annual TCO, 1,000 employees**: Azure-centric $300K–600K. AWS-centric $350K–700K. GCP-centric $200K–450K. Azure + GCP $250K–550K.
**Discounts**: Azure EA/Hybrid Benefit up to 40–42%. AWS is pure PAYG (best for variable load). GCP CUD up to 55% (70%), plus automatic SUD.

**Governance and ops**
| | Azure | AWS | GCP |
|---|---|---|---|
| Regions | 70+ | 39+ | 40+ |
| Agent logs | Azure Monitor + Foundry Observability | CloudWatch + AgentCore Observability | Cloud Audit Logs + Vertex AI Experiments |
| Data access logs | Purview Audit | CloudTrail Data Events | Cloud Audit Logs (Data Access) |
| Log retention | 2 yrs + Sentinel | 10 yrs | 10 yrs |
| SIEM | Sentinel (native) | Security Hub / external | Chronicle / external |
| Tracing | Application Insights | OTEL, CloudWatch | Cloud Trace |
| Quality metrics | Groundedness, Coherence, Fluency | Helpfulness, Tool Selection Accuracy, Hallucination Rate | Trajectory Evaluation, Tool Use Accuracy |
Certifications (SOC 1/2/3, ISO 27001/27017/27018, FedRAMP High) are at parity across all three.

**Third-party observability**: LangSmith (trace clustering; LangChain/LangGraph teams). Langfuse (OSS; cost, latency, and errors; in-house control). Arize AX ("evaluator committee" of multiple models). Datadog (existing infrastructure monitoring).

## Worked Example
**500M tokens/month, 70/30 split (350M in / 150M out).** Flash-Lite: 350×$0.10 + 150×$0.40 = **$95**. Flash $480. Haiku 4.5 $1,100. Gemini 2.5 Pro $1,938. GPT-4o $2,375. Sonnet 4.6 $3,300. Flash-Lite is about 25–35× cheaper but lower quality on hard tasks, so route FAQ traffic to Flash-Lite and send reasoning to Sonnet.

**Pre-deployment checklist (abridged)**: audit SharePoint grants (Entra SG vs native groups) and plan migration to Entra SGs; define a company-wide chat UI and the license allocation. Azure: AI Search cost, indexer frequency and resync for personnel changes, Preview GA timelines. GCP: WIF validation, Gemini quality evaluation, VPC-SC perimeter, CUD sizing. Governance: residency and cross-border rules, log retention and SIEM, eval workflow, framework-neutral strategy.

## Key Takeaways
1. Choose a cloud per workload: Azure is primary in M365 organizations, GCP complements, and AWS is conditional.
2. MCP and A2A are open and supported everywhere, so use them to make cross-cloud hybrids practical.
3. Model routing is the biggest cost lever (about 25–35× spread); then add CUD or EA discounts.
4. Pick the ACL level (L1–L3) based on revocation speed and legal risk.
5. Guard against context lock-in with OSS frameworks, LiteLLM, Kubernetes, Terraform, and MLflow.
6. Standardize on OTEL and run continuous evals to catch quality drift.

## Connects To
- ch13 (platform comparison, phased build), ch14 (Path A/B, mixed licenses)
- ch10 (production ops/cost/DR), ch06 (CDK + observability), ch07/ch09 (multi-agent orchestration, A2A), ch05 (Gateway/MCP), ch12 (Agent Registry), ch08 (export-to-code portability)
