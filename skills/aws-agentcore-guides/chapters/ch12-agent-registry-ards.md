# Chapter 12: AWS Agent Registry and the Agentic Resource Discovery Specification - Governance Before Discovery

## Core Idea
In AWS Agent Registry, unapproved records are not filtered out of consumer results — they are never in scope of the consumer APIs. Approval doesn't move a record; it switches which of two API surfaces (control plane vs `Discoverable` data plane) returns it. ARD is a separate, proposal-stage interoperability spec; the registry stays the enforcement point. (Facts as of 2026-09-14.)

## Frameworks Introduced
- **Two Planes over one record store**: Governance Plane = everything registered, any lifecycle state (admins; control plane, IAM-only, management events). Discovery Plane = "curated, not comprehensive", approved only (consumers; data plane, IAM or JWT, data events). When: reasoning about who sees what. How: check whether the API name contains `Discoverable`.
- **Four Personas** (guidelines, not IAM roles): administrator (registry config + everything), publisher (create/update/delete/submit), curator (approve/reject/deprecate via one action), consumer (search/list/get approved, invoke MCP).
- **Discovery triad**: search (top ≤20, semantic+keyword) → list (paged summaries, no descriptors) → batch get (full descriptors). When: walking the whole catalog use list + batch get, not search.
- **Minimum-registries rule**: start with the fewest registries that meet isolation needs; split only when auth type or approval setting must differ (both are per-registry).
- **ARD (Agentic Resource Discovery) v0.91**: Proposal, 2026-08-26, Apache 2.0; authored by people from Google, Microsoft, Hugging Face (AWS gave feedback). Defines entries, publication, search endpoints, federation modes.

## Key Concepts
- **Control plane**: `agent-registry-control.{region}.api.aws`, `aws agent-registry-control`, `AgentRegistryControlClient`; create/manage registries and records, approvals; always IAM.
- **Data plane**: `agent-registry.{region}.api.aws`, `aws agent-registry`, `AgentRegistryClient`; search/list/batch-get approved records, MCP.
- **Record states (9)**: `DRAFT | PENDING_APPROVAL | APPROVED | REJECTED | DEPRECATED | CREATING | UPDATING | CREATE_FAILED | UPDATE_FAILED` (blog diagram shows only 5). Registry states (7): CREATING, READY, UPDATING, CREATE_FAILED, UPDATE_FAILED, DELETING, DELETE_FAILED.
- **`recordType`**: `AGENT`, `MCP`, `SKILL`, `CUSTOM`; `descriptors` has 6 keys: `mcpServer`, `a2aAgentCard`, `agentSkillsDefinition`, `custom`, plus endpoint-based `agui`, `http`. `descriptorType` filter accepts only the first four.
- **Schema validation**: MCP and Agent records validated against MCP/A2A schemas — format only, not existence, behavior, or security. SKILL/CUSTOM unvalidated.
- **`name` vs `displayName`**: `name` = required dedup key (unique, or unique with `recordVersion`); `displayName` = human label. Migration renamed old `name` → `displayName`.
- **Synchronization**: pull metadata from an MCP/A2A URL; creates a new revision that may need re-approval. Outbound auth (OAuth/IAM credential provider ARN) is separate from inbound.
- **`autoApprovalRules`**: array (was boolean `autoApproval`), max 10, only value `APPROVE_ALL`; default none = manual review. Changes apply only to records entering `PENDING_APPROVAL` after the update.
- **Org auto-detection**: finds AgentCore Runtimes and Gateways in member accounts, creates `aws-autodetected-` DRAFT records; one org-scoped registry per Region; needs trusted access + delegated admin or management-account ownership.
- **Registry MCP endpoint**: `https://agent-registry.<region>.api.aws/registry/<registryId>/mcp`, MCP spec 2025-11-25, three read-only tools; needs `InvokeRegistryMcp` + the per-tool action.

## Mental Models
- Think of approval as a visibility switch between API surfaces, not a move between tables.
- Think of persona names, RAM permission names, and real IAM effects as three different things — only IAM actions exist.
- Use relevance ≠ trust: ARD says scores "MUST NOT be interpreted as a trust, compliance, or safety judgment"; the registry encodes trust separately via approval.
- Think of auto-detection as showing admins shadow agents exist, not stopping them.
- Treat batch get partial results as normal: HTTP 200 with an `errors` list (`RESOURCE_NOT_FOUND`, `ACCESS_DENIED`, `INTERNAL_ERROR`).

## Anti-patterns
- Relying on the default RAM share (`AWSRAMDefaultPermissionAgentRegistryReadOnly`): it grants control-plane `GetRegistryRecord`/`ListRegistryRecords`, exposing drafts and rejected records (but no MCP invoke).
- Assuming RAM `...ForAdmin` = administrator: `UpdateRegistry`/`DeleteRegistry` never delegate via RAM.
- Expecting condition keys to narrow search/list results — they apply only to individual record read/write.
- Blanket find-replace `bedrock-agentcore` → `agent-registry`: workload identity and OAuth credential providers stay in `bedrock-agentcore` (e.g., `bedrock-agentcore:CreateWorkloadIdentity` still needed for URL sync).
- Sharing one registry across dev and prod (auto-approval is registry-wide).
- Reverting auto-approval and assuming exposure is undone — approved-in-between records must be found and deprecated by hand.
- Coding to 5 states or 4 descriptor keys.
- Checking only the HTTP status of batch get.
- Designing around blog "forward looking" features (per-consumer discovery, dedup, security assessment, EC2/EKS/ECS detection, ARD integration).
- Picking JWT for search convenience without weighing PrivateLink policy limits and IdP migration.

## Code Examples
```
DRAFT | PENDING_APPROVAL | APPROVED | REJECTED | DEPRECATED | CREATING | UPDATING |
CREATE_FAILED | UPDATE_FAILED
```
What it demonstrates: the full `status` enum your state-handling code must cover.

Namespace identifiers after migration (launched 2026-08-06; old `bedrock-agentcore` preview namespace discontinued 2026-09-17): IAM prefix `agent-registry:`, principal `agent-registry.amazonaws.com`, ARN `arn:aws:agent-registry:`, CloudFormation `AWS::AgentRegistry::Registry`. EventBridge migration gotcha: a rule matching detail type "Registry State transitions from Creating to Ready" no longer fires — update to "Registry Ready"; record-side `PENDING_APPROVAL` detail type unchanged.

## Reference Tables
| Operation | Control plane (all states) | Data plane (approved only) |
|---|---|---|
| List | `ListRegistryRecords` | `ListDiscoverableRegistryRecords` |
| Get | `GetRegistryRecord` | none (`GetDiscoverableRegistryRecord` is an IAM action only) |
| Batch get | — | `BatchGetDiscoverableRegistryRecord` |
| Search | — | `SearchDiscoverableRegistryRecords` |

| Persona | IAM actions |
|---|---|
| administrator | `CreateRegistry`, `UpdateRegistry`, `DeleteRegistry` + all below |
| publisher | `CreateRegistryRecord`, `UpdateRegistryRecord`, `DeleteRegistryRecord`, `SubmitRegistryRecordForApproval` |
| curator | `UpdateRegistryRecordStatus` (approve, reject, deprecate — not separable) |
| consumer | `SearchDiscoverableRegistryRecords`, `ListDiscoverableRegistryRecords`, `GetDiscoverableRegistryRecord`, `InvokeRegistryMcp` |

| RAM managed permission | Grants |
|---|---|
| `AWSRAMDefaultPermissionAgentRegistryReadOnly` (default) | Control-plane + data-plane reads; no MCP invoke — sees drafts |
| `AWSRAMPermissionAgentRegistryForConsumer` (recommended) | 3 data-plane actions + MCP invoke; approved only |
| `AWSRAMPermissionAgentRegistryForPublisher` | + view config, record CRUD, submit |
| `AWSRAMPermissionAgentRegistryForAdmin` | + approve/reject/deprecate; no registry config changes |

| Limit | Value |
|---|---|
| Registries per account/Region | 5 (default, raisable) |
| Registry name / description | 64 chars / 1–4,096 chars; CFN tags max 50 |
| Search results | 1–20, default 10; query ≤256 chars |
| List page | 1–100 (MCP tool default 20); ≤10 filters |
| Batch get | 100 per call (MCP tool definition only) |
| Registries per discovery call | exactly 1 (`registryIds`, `entries` fixed at 1 item) |
| KMS key / auth type / JWT discovery URL | immutable after creation (`AuthorizerType` change = CFN Replacement) |

| Audit | Default |
|---|---|
| Management events (12 control-plane ops incl. approvals) | Logged; `name`, `description`, `statusReason`, descriptor `data` masked as `HIDDEN_DUE_TO_SECURITY_REASONS` |
| Data events (search, list, batch get, MCP invoke) | Not logged; enable for `AWS::AgentRegistry::Registry`; `searchQuery`, `filters` masked |

Condition keys (record-level only): `agent-registry:RecordCreatorAccount`, `agent-registry:RecordSourceAccount` — resolved from stored record, unspoofable.

ARD: entries need global ID, display name, IANA media type, body or reference; publish via `/.well-known/ard.json` or `rel="ard"`; `POST /search` (required), `POST /explore`, `GET /agents` (optional); federation `auto` / `referrals` / `none`.

## Worked Example
Sharing a department registry with a consumer account: default share would let the account enumerate drafts whose names may leak internal endpoints → name `AWSRAMPermissionAgentRegistryForConsumer` explicitly. To hide other accounts' records, condition keys won't help search/list → withhold search and list actions instead (no per-consumer result tailoring exists). If the org split registries per department, cross-department duplicate checks need one call per registry. With JWT, a PrivateLink endpoint policy can't single out bearer callers (they match only `Principal: *`) → restrict with a `Deny` scoped by action/resource.

## Key Takeaways
1. Grant consumers only `Discoverable` data-plane actions; control-plane reads reveal unapproved records.
2. Always name the RAM permission; prefer Consumer.
3. Decide auth type (IAM vs `CUSTOM_JWT`), JWT discovery URL, and KMS key before creation — they're permanent.
4. Wire EventBridge approval notifications to a reviewer + `UpdateRegistryRecordStatus`; nothing routes approvals for you, and auto-approval doesn't clear backlog.
5. Separate dev (auto-approve) and prod registries; keep count minimal otherwise.
6. Store approval rationale outside the registry (CloudTrail masks `statusReason`); enable data events if query auditing is required.
7. Semantic search embedding inference may run in any commercial Region and logs don't say which — check data-residency rules.

## Connects To
- ch05 (Identity, Gateway, Cedar), ch07/ch09 (multi-agent, A2A/MCP agents being cataloged), ch10 (CRIS/data residency, audit trail), ch11 (WAF on AgentCore Gateway, MCP security), ch13 (enterprise identity design).
