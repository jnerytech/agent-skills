# Chapter 13: Enterprise AI Agent Environment Design Notes Part 1 — Comparing the Three Major Clouds and Designing Your Architecture

## Core Idea
Enterprise AI agents are production infrastructure, not LLM API calls: pick the interface per user tier (local / cloud-hosted / event-driven), build in phases (RAG → two access paths → centralized permissions), and choose among Microsoft Foundry, Amazon Bedrock AgentCore, and Vertex AI by fit with existing infrastructure. For MS365 organizations, "Azure-led with GCP as a complement" tends to be the best-balanced default.

## Frameworks Introduced
- **Three-Tier Agent Deployment Model**: Local agents and cloud-hosted agents are complementary, not competing.
  - When to use: deciding who gets which agent interface.
  - How: (1) Developers/power users → local agents (Claude Code, GitHub Copilot) extended via MCP/Skills; (2) General staff (sales, legal, HR) → cloud-hosted chat UI in browser or Teams; (3) Background processes → event-driven, always-on automation (classify incoming email, answer Slack questions).
- **Phased Deployment (3 Steps)**:
  - When to use: moving from PoC to org-wide rollout.
  - How: **Step 1** Build the RAG foundation (chunk → embed → Azure AI Search / Amazon Kendra / Vertex AI Search / OpenSearch Serverless) as the shared knowledge layer; start with low-sensitivity, measurable content (FAQs, manuals). **Step 2** Build two access paths to the same RAG: cloud-hosted UI (AgentCore / Foundry / Agent Builder) for staff, and an MCP Server for local agents. **Step 3** Centralize permissions (IAM, Entra ID, Workforce Identity Federation) so agent-mediated access obeys the same policies as direct access ("contracts are legal-only", "payroll is HR-only").
- **Resource-Matched Access Method**: Documents → RAG; FAQs → direct load into search/vector DB; wiki → API/crawl → RAG; structured business data (RDS/DynamoDB/BigQuery) → MCP Server → SQL/API; email/chat → API integration with access control. Never force one approach for everything.

## Key Concepts
- **Microsoft Foundry**: Azure's "AI app and agent factory" (formerly Azure AI Studio → Azure AI Foundry; renamed at Ignite Nov 2025); third pillar beside M365 and Fabric.
- **Foundry IQ**: Next-gen RAG knowledge system (Public Preview) on Azure AI Search with OneLake/SharePoint/Blob connectors; OneLake shortcuts reach S3 and Snowflake.
- **Foundry Control Plane**: RBAC, VNET isolation, Purview integration, tracing, evaluation.
- **Amazon Bedrock AgentCore**: GA Oct 2025; "building blocks" platform — Runtime (sessions up to 8 hours), Identity (Entra ID/Okta OIDC federation, JWT validation), Gateway (MCP-compatible, IAM/OAuth), Memory, Policy, Evaluations; Bedrock Knowledge Bases is a separate capability commonly paired.
- **Vertex AI Agent Builder / ADK**: Google's platform; ADK is OSS (Python, Java, Go, TypeScript); Agent Engine is the managed runtime.
- **Agent Identity (GCP)**: Registers agents as Cloud IAM principals for least privilege.
- **Model Armor**: GCP prompt-injection blocking.
- **Gemini Enterprise**: Formerly Google Agentspace; enterprise search + agent platform and GCP's route to SharePoint ACLs.
- **Google Search Grounding / Web Grounding for Enterprise**: Real-time web grounding unique to GCP; the Enterprise variant adds VPC-SC and log control for regulated industries.
- **VPC Service Controls (VPC-SC)**: Free GCP data-exfiltration perimeter.

## Mental Models
- Think of local and cloud agents as serving **different user groups and operating models**, not as substitutes.
- Use one RAG foundation with **multiple access paths** so every tier sees consistent data.
- Think of each cloud as having "home turf": Azure = MS365/SharePoint permissions/governance; GCP = multimodal + cost; AWS = existing AWS estate + Claude + framework flexibility.
- Count fit with requirements, not ◎ marks.
- Use specialized agents ("contract review", "FAQ answering", "proposal drafting") rather than one all-purpose agent, for accuracy and cleaner permissions.

## Anti-patterns
- Rolling out a local tool to all employees, or expecting one cloud service to cover everything.
- Building the "full stack" during PoC, which slows delivery and hides what's working.
- Bulk-ingesting all documents at once instead of FAQs → policies → proposals.
- One all-purpose agent, which brings complex permission management and bloated prompts.
- Fine-tuning first. Start with RAG and fine-tune only if domain accuracy proves insufficient.
- Deploying "Azure AD inside an AWS/GCP VPC" to close the SharePoint gap (see Worked Example).

## Reference Tables
**Series conclusions**
| Dimension | Conclusion |
|---|---|
| SharePoint ACL | Azure most practical (Foundry Path A full / Path B Entra SG only); GCP via Gemini Enterprise with sync lag; AWS has no ACL mechanism |
| LLM choice | Azure 11,000+; AWS Claude/Llama/Nova; GCP 200+ |
| Cost | GCP wins high-frequency inference (Gemini 2.5 Flash-Lite ~$0.10/M tokens) |
| Multimodal | GCP (Gemini Live API, Veo, Imagen, Chirp) |
| Governance | Azure (Purview/Entra/Defender) |
| Architecture | Azure-led + GCP complement |

**Three-platform comparison**
| Axis | Microsoft Foundry | AWS Bedrock AgentCore | GCP Vertex AI |
|---|---|---|---|
| Model count | 11,000+ | Dozens | 200+ |
| Framework | Semantic Kernel + OSS | Any OSS (LangGraph, CrewAI, OpenAI Agents SDK) | ADK (OSS) |
| SharePoint | ◎ Native | △ Connector (no ACL) | ○ Via Gemini Enterprise |
| Entra ID | ◎ Native | ○ AgentCore Identity | ○ Workforce Identity Federation |
| Multimodal | ○ GPT-5.4 | ○ Nova | ◎ Gemini |
| Network isolation | VNET | VPC | VPC-SC (free) |
| Teams | ◎ | ✕ Custom | ✕ Custom |
| Pricing | PAYG + Provisioned | PAYG + Provisioned Throughput | PAYG + CUD (up to 55% off) |

**Early design decisions**
| Decision | Guidance |
|---|---|
| Bedrock vs Foundry vs Vertex vs self-hosted | Align with existing cloud; MS365 → prioritize Azure |
| RAG vs fine-tuning | RAG first |
| Bulk vs phased ingestion | Phased |
| One agent vs fleet | Specialized agents |

**Why cloud-hosted agents for the org**: multi-user provisioning, centralized RBAC/audit, non-technical users (browser/Teams), shared consistent knowledge base, always-on/event-driven, orchestration scalability.

## Worked Example
**"Can't we just stand up Azure AD inside an AWS/GCP VPC?"** No, for three reasons. (1) Entra ID is a global SaaS IdP and cannot be installed in any VPC, not even an Azure VNET. Only classical AD DS can be placed there (self-hosted Windows Server AD, AWS Managed Microsoft AD, Google Cloud Managed Service for Microsoft AD). Entra Domain Services is Azure-only. (2) SharePoint ACLs live in Entra ID + SharePoint Online + M365 security groups + Purview labels, not in AD DS. (3) The identity layer is already solved: AgentCore Identity and Workforce Identity Federation federate with Entra ID directly over OIDC/SAML. The real gap is at the **connector/ingestion layer**, in how ACLs reach the retrieval index.

## Key Takeaways
1. Give each user tier the right interface: local for developers, cloud UI for staff, event-driven for background work.
2. Build RAG first, then the UI and MCP access paths, then permissions. Permissions must be in place before org-wide rollout.
3. Match the access method to the resource type (RAG, SQL/API via MCP, or API).
4. Prefer specialized agents over one all-purpose agent.
5. AgentCore offers framework flexibility and Entra federation, but no platform-level SharePoint ACL.
6. The SharePoint gap is a connector problem, not an IdP problem.

## Connects To
- ch14 (SharePoint ACL deep dive: Path A/B, Bedrock KB limits), ch15 (use-case selection, TCO, lock-in, ops)
- ch04/ch05 (AgentCore Runtime/Memory, Identity/Gateway/Policy), ch12 (Agent Registry), ch09 (multi-agent patterns, specialized agents), ch01 (Beginner's Guide)
