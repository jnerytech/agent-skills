# Chapter 14: Enterprise AI Agent Environment Design Notes Part 2 — Implementing SharePoint ACL and Permission Controls

## Core Idea
The worst failure for an internal-document agent is surfacing content the user was never allowed to see. Build permission controls in from day one. ACL fidelity depends on whether the cloud's SharePoint **connector** copies ACLs into the index along with content. Azure and GCP do this; AWS Bedrock KB copies only the content. ACL quality and cost/customizability pull in opposite directions.

## Frameworks Introduced
- **ACL Fidelity Ranking**: MS365 Copilot Agent (fully native) ≥ Foundry Path A (equivalent) > Foundry Path B (Entra groups only, ~"80 points automatically") > Gemini Enterprise (~"60 points with extra setup", periodic sync) > Bedrock KB (0, build everything yourself).
  - When to use: matching confidentiality requirements to budget.
- **Foundry Path A (Remote)**: Data stays in SharePoint. At query time the SharePoint Tool calls the M365 Copilot Retrieval API On-Behalf-Of (OBO) the user, so SharePoint enforces permissions itself.
- **Foundry Path B (Indexed)**: Pre-copy into Azure AI Search with per-file ACL metadata, then trim results at query time against the caller's Entra token.
- **Two-tier ACL architecture**: Path B as the baseline, with Path A only for highly sensitive documents.
- **Mixed-License Coexistence**: Concentrate Copilot licenses on roles that use in-app features (executives, planning, legal). Serve SharePoint search and Q&A users through Path B behind one unified chat UI that routes by license status.

## Key Concepts
- **`bedrock:Retrieve` exposure**: Per AWS docs, "All data that you sync from your data source becomes available to anyone with `bedrock:Retrieve` permissions". ACLs are discarded at crawl, by design.
- **Amazon Q Business**: Managed AWS option with SharePoint ACL auto-inheritance; $3–20/user/month (Lite/Pro); fixed LLM.
- **Kendra GenAI Index**: `UserContext` ACL filter; usable as a managed retriever for Bedrock KB (ACL only partial there); 43 connector types.
- **Pseudo-ACL**: Bedrock KB + metadata filter with self-built ACL sync. High cost and leak risk.
- **`indexerPermissionOptions`**: Data-source setting that enables ACL ingestion in Azure AI Search.
- **`x-ms-query-source-authorization`**: Header carrying the user's Entra token for query-time security trimming.
- **Fail-closed trimming**: If ACL evaluation fails, Azure AI Search returns 5xx and never partial results.
- **Workforce Identity Federation**: GCP's Entra ID bridge (OIDC recommended); group mapping up to 100 (expandable to 400); free.
- **Identity sync vs entity sync**: Gemini Enterprise schedules permission and content sync independently.
- **SharePoint native groups**: Unsupported by Path B and Gemini Enterprise. This is the most common gotcha.

## Mental Models
- Think of the ACL gap as a **connector problem, not an IdP problem**.
- Even imperfect ACLs enforced at the platform layer beat custom ACLs that look correct but leak in edge cases.
- Use Path B when cost is the priority; use Path A when ACL strictness is non-negotiable.
- Treat ACL freshness as a design parameter: real-time (Path A) vs indexer-dependent (Path B) vs 30min–7d (GCP).

## Anti-patterns
- Deferring access control to "later" during PoC.
- Pointing Bedrock KB at SharePoint and assuming permissions carry over. Everyone with `bedrock:Retrieve` sees everything.
- Relying on SharePoint-native groups with Path B. Migrate to Entra Security Groups.
- Using a chunking split skill without explicitly mapping ACL properties onto each chunk.
- Creating a Gemini Enterprise data store without ACL. It must be enabled at creation and cannot be changed afterward.
- Deploying AD DS in a VPC to "fix" ACLs. SharePoint ACLs, M365 groups, and Purview labels never live in AD DS.

## Code Examples
Path B configuration essentials (Azure AI Search, `2025-11-01-preview`, still Public Preview as of April 2026):
```
Data source:   indexerPermissionOptions  (enable ACL ingestion)
App perms:     Files.Read.All + Sites.FullControl.All  (or Sites.Selected)
Auth:          managed identity (secretless) recommended
Query header:  x-ms-query-source-authorization: <user Entra token>
```
What it demonstrates: ACLs are computed per file at ingest and stored with the content. At query time the calling Entra principal is matched against them and results are trimmed. ACL evaluation failure returns 5xx and never returns partial results.

## Reference Tables
**ACL support across four services**
| Aspect | MS365 Copilot Agent | Foundry | Bedrock AgentCore | GCP Gemini Enterprise |
|---|---|---|---|---|
| ACL auto-inherit | ◎ | ○ Path A / △ Path B | ✕ | △ periodic sync |
| SharePoint groups | ◎ | ○ A / ✕ B | ✕ | ✕ |
| Entra auth | Native | Native (OBO) | ○ AgentCore Identity | ○ WIF |
| LLM choice | ✕ GPT only | ◎ 11,000+ | ◎ | ◎ 200+ |
| Teams | ◎ | ✕ with SharePoint Tool | ✕ | ✕ |
| VNET/VPC | ✕ | ○ | ○ | ○ VPC-SC free |
| Cost | $30/user/mo | PAYG (+Copilot for Path A) | PAYG | PAYG |
| ACL freshness | Real-time | A real-time / B indexer | N/A | ID 30min–7d / entity 3h–7d |

**AWS ACL options**
| Approach | ACL | Cost | Constraint |
|---|---|---|---|
| Amazon Q Business | ○ auto | Low | $3–20/user/mo, fixed LLM |
| Kendra GenAI Index → Bedrock | ○ `UserContext` (partial via KB) | Medium | Use Retrieve API directly or Q Business for reliable filtering |
| Bedrock KB + metadata filter | △ pseudo | High | Self-built sync, leak risk |
| Bedrock KB as-is | ✕ | Low | All docs visible to all |

**Path A vs Path B**
| Dimension | Path A | Path B |
|---|---|---|
| Data | Stays in SharePoint | Copied to Azure AI Search |
| Freshness | Real-time | Indexer schedule |
| ACL | SharePoint native (complete) | Entra groups only (Entra SG, M365, mail-enabled SG; not SP groups) |
| Sensitivity labels | As-is | Preview |
| Copilot license | Per user (PAYG Preview needs ≥1 in tenant, no OneDrive) | Not required |
| Limits | No Teams publishing (OBO vs managed identity conflict); 1 SharePoint tool/agent; same tenant | 1,000 ACL entries/file; map ACL to chunks |
| Complexity | Low | High |

**Gemini Enterprise sync options**: Identity: 30min/1h/3h/6h/12h/1d/3d/5d/7d. Entity: 3h/6h/12h/1d/3d/5d/7d. Webhook real-time sync is in Public Preview.

**Copilot gaps**: Bridgeable through Path B: SharePoint search (small gap), knowledge Q&A, summarization (none), LLM quality (Path B may win with Claude). Unbridgeable: Copilot in Word/Excel/PPT, Outlook drafting, Teams meeting recap, and agents inside Teams (only workaround is a separate UI).

## Worked Example
**1,000-person org licensing.** All-Copilot: 1,000 × $30 = **$30,000/month** ($360,000/yr). Mixed: 200 Copilot ($6,000) + 800 on Path B (Azure AI Search + LLM) ≈ **$6,500–8,000/month**. Savings are $22,000–23,500/month, about **$270,000/year**. Also note M365 base price increases from July 1, 2026 (E3 $36→$39, E5 $57→$60). Operational caveats: Copilot and Path B users may get different answers, so raise indexer frequency or resync manually when key documents change.

## Key Takeaways
1. Design permissions in from the start; leaking HR or M&A documents is a compliance violation.
2. Bedrock KB drops SharePoint ACLs by design. On AWS, use Q Business or Kendra GenAI Index.
3. Path B is about 80% of the ACL coverage at pay-as-you-go cost; Path A is complete but needs Copilot licenses.
4. Path B ACL trimming is fail-closed (5xx), but still Preview, so re-evaluate at GA.
5. GCP is best as a complement: WIF setup, sync lag, 100/400 group cap, no SharePoint groups.
6. Mixed licensing saves about $270K/yr for 1,000 users, but in-app Copilot features can't be replaced.

## Connects To
- ch13 (platform overview, VPC-AD sidebar), ch15 (ACL strictness levels L1–L3, hybrid patterns, checklist)
- ch05 (AgentCore Identity/Gateway/Policy: OBO, federation), ch11 (WAF/prompt injection, defense in depth), ch04 (Memory/Runtime)
