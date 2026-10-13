# Chapter 11c: Vibe Architecture at Org Scale

## Core Idea
At thirty repos, eight squads, and four different AI tools, the single-repo disciplines still apply; they just need a layer above them: an org-level tier of invariants, a cross-repo contract registry, a two-layer Inquisitor, owned shared artifacts, and governance by stewardship. Encode the decision once, enforce it automatically, reserve human judgment for policy.

## Frameworks Introduced
- **Org-Level Context Diet (Tier 0 above Tiers 1–3)**: org-wide invariants every agent follows regardless of tool or repo, held in a shared, version-controlled `vibe-arch-standards` repository and imported read-only by every team's CLAUDE.md.
  - When to use: multiple teams, multiple AI tools, and zero standardisation on governance.
  - How: (1) Put cross-cutting rules in `vibe-arch-standards`: shared-service/API naming, approved secrets pattern (vault only, no env-var credentials), regulated-data policy (`@AIPrivacy` fields handled the same everywhere), approved licence set (no AGPL into proprietary code), no auth/authz code without human sign-off. (2) Every CLAUDE.md imports it read-only. (3) The platform CI template, which every squad's pipeline extends, runs a version-pinned standards check. (4) A failure blocks the PR before domain CI runs.

- **Cross-Repo Contract Registry**: one repo (or well-known monorepo path) holding every published API contract with explicit ownership and registered consumers.
  - When to use: when a provider's API change must break consumers' CI before it merges.
  - How: (1) Store `contracts/<api>/vX.Y.openapi.yaml`, `consumers.txt`, `OWNERS`. (2) The provider's Inquisitor diffs any OpenAPI change against the published version. (3) Breaking changes block the PR. (4) Additive changes open a draft PR in each registered consumer repo showing the delta, requiring explicit acceptance before the provider merges. Built today from Ch 18 contract tests + Ch 21 pipeline architecture + cross-repo webhooks.

- **Two-Layer Inquisitor**: a platform Inquisitor plus a domain Inquisitor, plus a non-blocking consultation loop.
  - When to use: when per-team Inquisitor configs diverge (rules missing, ArchUnit export unwired, system prompt drifted).
  - How: the platform layer runs org rules, version-pinned from `vibe-arch-standards`, merge-blocking, unmodifiable by teams; opting out of the CI template means losing platform support. The domain layer is the team's Ch 22 Inquisitor; teams may make it stricter, never weaker than the baseline. The consultation loop is pre-push, dev-triggered, advisory only.

- **Governance by Stewardship**: a named owner changes the standard on a cadence, rather than a committee that must unanimously approve.
  - When to use: always, once there is an org standard.
  - How: a named platform/architecture-governance team owns it; changes ship on a regular cadence (quarterly is common) with a migration window; breaking changes get a deprecation period; new requirements get an adoption deadline. The steward also owns the compliance dashboard, automated PRs pushing standard updates to squads, and an escalation path for teams below baseline.

- **Owned Context Graph**: every `lat.md` diagnostic node has an owner; a cross-cutting node has exactly one.
  - When to use: when the Ch 3b context graph spans many repos.
  - How: repo-local failures keep local nodes owned by the squad (OWNERS marker on the node or directory); cross-squad failure modes (shared auth flow, payments timeout, regulated-data rule) get one authoritative node in `vibe-arch-standards`, imported read-only.

## Key Concepts
- **`vibe-arch-standards`**: the shared, change-managed standards repo; source of the org tier.
- **Pinned standards version**: CI references an exact version (e.g. `"2.1"`), never a floating one.
- **`consumers.txt` / `OWNERS`**: explicit consumer registration and ownership per contract.
- **Platform Inquisitor**: org-rule, merge-blocking reviewer no team can modify.
- **Domain Inquisitor**: team-configured reviewer that may only be stricter than the platform.
- **Drift rate**: how often a squad's Tier 1 file diverges from the org standard, and how fast it is caught.
- **Fragmented context graph**: duplicated/stale diagnostic nodes across repos; worse than no graph.
- **Governance by committee**: every squad approves every change, so nothing changes and the standard rots.

## Mental Models
- Think of org governance as the Context Diet at org scale: make compliance the path of least resistance so squads spend attention on features.
- Think "stricter allowed, weaker forbidden" for any team-level override of a platform baseline.
- A stale or duplicated diagnostic node resolves an exception to the wrong fix with total confidence: Ch 2's beautifully deceptive failure wearing a diagnostic badge.
- At org scale, the only decisions automation can't make are policy decisions; everything else should be machinery.

## Anti-patterns
- **Per-team Inquisitor configs with no baseline**: silent divergence across teams.
- **Floating standards versions**: unreviewed rule changes land everywhere at once.
- **Unowned shared artifacts**: graphs and standards rot one stale node at a time.
- **Governance by committee**: paralysis, then rot.
- **Contract changes discovered after merge**: consumers learn about breakage in production.

## Code Examples
```yaml
# org-ci-template.yml: extended by every squad
jobs:
  standards-check:
    steps:
      - uses: org/vibe-arch-standards-action@v2
        with:
          standards-version: "2.1"   # pinned, not floating
```
- **What it demonstrates**: a mandatory, version-pinned org gate that checks CLAUDE.md imports the current standards, regulated classes weren't changed without sign-off, and the Inquisitor references the org ruleset.

```text
contracts/
  payments-api/
    v2.3.openapi.yaml   ← current published contract
    consumers.txt       ← ["checkout-service", "mobile-bff", "analytics"]
    OWNERS              ← payments team
  inventory-api/
    v1.8.openapi.yaml
    consumers.txt
```
- **What it demonstrates**: the cross-repo contract registry layout.

## Reference Tables
| Layer | Scope | Blocks merge? | Who configures |
|---|---|---|---|
| Platform Inquisitor | Org-level rules | Yes | Platform team only (pinned) |
| Domain Inquisitor | Team architectural rules | Yes | Team (stricter only) |
| Consultation Loop | Pre-push advice | No | Developer-triggered |

| Leadership metric | Question | Warning sign |
|---|---|---|
| Coverage | % of repos with all four context tiers | Teams use AI, but not safely |
| Drift rate | How often Tier 1 diverges from standard; time to detect | Fast drift + slow detection = governance failure |
| Inquisitor hit rate by team | Blocks per team per week | Persistently high = Generator not consuming feedback (workflow/tooling problem) |
| Protected-class change frequency | Changes to `@AILocked` / `@AIRegulation` classes and sign-off pattern | Unreviewed changes; answerable from git history with Ch 21 provenance |

## Worked Example
Payments changes its API. The payments Inquisitor diffs the new OpenAPI against `v2.3.openapi.yaml`. A removed field is breaking, so the PR is blocked. An added optional field is additive: webhooks open draft PRs in `checkout-service`, `mobile-bff`, and `analytics` showing the delta; each consumer must accept before payments can merge.

## Why It Works / Failure Mode
- **Org tier + pinned CI template**: one change-managed source, imported read-only and enforced by a template every pipeline must extend, removes per-team drift. Fails without a named steward and cadence: either nothing changes (committee) or teams opt out.
- **Two-layer Inquisitor**: a non-negotiable floor plus team freedom upward keeps local rules while preventing weakening. Fails if teams can edit the platform layer's prompt or config.

## Key Takeaways
1. Add an org tier above Tiers 1–3, held in a versioned standards repo and imported read-only.
2. Enforce it through a pinned CI template that blocks before domain CI runs.
3. Run a cross-repo contract registry: breaking changes block, additive changes require consumer acceptance.
4. Split the Inquisitor into an unmodifiable platform layer and a stricter-only domain layer.
5. Give every shared artifact (standards, contracts, diagnostic nodes) exactly one owner.
6. Govern by stewardship on a quarterly-ish cadence with migration windows and deprecation periods.
7. Measure coverage, drift rate, hit rate by team, and protected-class changes.

## Connects To
- **Ch 3**: three-tier context model, extended with an org tier.
- **Ch 3b**: `lat.md` context graph.
- **Ch 2**: beautifully deceptive failure.
- **Ch 4**: `@AIPrivacy`, `@AILocked`, `@AIRegulation`.
- **Ch 18**: contract tests and diffs.
- **Ch 21**: pipeline architecture and provenance.
- **Ch 22**: the Inquisitor.
- **Ch 11d / 11e**: org bottleneck and metrics.
- **Epilogue (26)**: multi-repo contract discipline as future direction, available today.
- **Consumer-driven contracts (Pact)**; **platform engineering / paved road**; **CODEOWNERS**.
