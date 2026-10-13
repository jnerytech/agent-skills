# Chapter 18: Schema Drift & API Contracts

## Core Idea
The AI is as reckless with contracts outside the process (database schema, wire payloads) as it is with shared state inside it, but here the failure is immediate and total: the whole consumer base breaks at deploy. Freeze schema and wire contracts as human-owned, committed artifacts. Enforce them with tests the AI can't edit, and make every breaking change a deliberate, versioned expand/migrate/contract act, never a side effect of a "cleanup" prompt.

## Frameworks Introduced
- **Expand / Migrate / Contract (parallel change) for migrations**: the only safe shape for a live-schema change.
  - When to use: any prompt that touches a database used by running consumers or previously deployed app versions.
  - How: (1) **Expand**: additive changes only. Add a nullable or defaulted column, or a new table. Never rename, drop, retype or add NOT NULL to an existing column in this step. (2) **Migrate**: backfill, then move readers and writers to the new shape while the old one still works. (3) **Contract**: only after every consumer has moved and rollback is no longer needed, a separate, later migration removes the old shape. Put this standing rule in Tier 1 context (Ch 3) and enforce it in CI (Ch 21): *"Every migration is additive. A destructive change (DROP, NOT NULL on an existing column, type narrowing, rename) is only ever its own migration, explicitly justified, never bundled with a feature."*
- **Schema-first contract posture**: the committed OpenAPI document is the source of truth, and the AI can't write to it.
  - When to use: the default posture for AI-generated services.
  - How: mark `openapi.yaml` `@AILocked` or keep it outside the AI's writable scope. Add a contract test that validates live responses against the committed schema. The AI can rewrite the controller however it likes, but the moment the response shape diverges, the test goes red locally, before a PR exists.
- **Consumer-driven contracts (Pact / Spring Cloud Contract)**: each consumer publishes the shape it actually depends on, and the provider build verifies it still satisfies all of them.
  - When to use: you want the strongest signal, one that fails only when a real consumer would break, not on cosmetic shape changes. It's also the removal gate for deprecated versions.
  - How: consumers commit contracts. The provider's CI verifies them on every build. A shape is safe to delete only when no published consumer contract still references it.
- **Versioned API break (expand-contract lifted to the wire)**: "A break is a deliberate, versioned act, never a side effect of a cleanup prompt."
  - When to use: a field really must change type, a resource has to be restructured, or a default was wrong.
  - How: **Expand**: add a new field (never a renamed one), a `v2` endpoint beside `v1`, or a new enum value without reassigning an existing meaning. **Migrate**: consumers move on their own schedule. For clients you can't redeploy (mobile), that means waiting for the install base to turn over. Put `Deprecation` and `Sunset` headers (RFC 8594) on the old path. **Contract**: remove the old shape in a separate, justified change once no consumer contract references it. Commit the sunset decision (date, reason) next to the contract.
- **Schema-Touching Prompt Workflow** (5 steps):
  - When to use: every prompt that touches the DB or a serialized payload. The AI won't volunteer the safe path.
  - How: (1) Name the consumers in the prompt, e.g. "consumed by the mobile app (cannot be redeployed) and reporting; `api/openapi.yaml` is frozen." (2) Demand expand-only: "Additive migration only. If a column should be dropped, list it as a follow-up; do not include it." (3) ★ Require the contract test and forbid editing the contract: "Do not modify `openapi.yaml` or weaken an assertion." (4) Run it, and expect red on a real break. (5) Paste the failure back: "`customer_id` was renamed. Restore the wire field; keep internal renaming behind the serialization boundary."

## Key Concepts
- **Contract break vs concurrency bug**: sibling failure modes with opposite timing. Concurrency bugs show up once in a million runs. A contract break shows up at deploy, for every consumer.
- **The transition is the product**: for a live database, a schema that's correct in its final form but destructive in its rollout counts as a destructive change.
- **End-state optimization**: the AI aims for the clean final schema and treats the rollout as an implementation detail, which is why it bundles drops and renames into feature work.
- **Versioned migration tool**: Flyway or Liquibase, which make every change an immutable, ordered, reviewable file instead of an ad-hoc `ALTER TABLE`. The tool also gives you the enforcement surface.
- **Backwards-compatibility migration test**: boot against the new migration and prove that the previously deployed version's queries still succeed.
- **Wire signature**: the JSON property names and types a consumer deserializes. Where Ch 4's `@AIContract` froze the Java signature, this freezes the network one.
- **Serialization boundary**: where internal refactoring stops and the contract begins. Java fields can be renamed freely. JSON properties can't.
- **Removal gate**: consumer contracts decide when `v1` can be deleted, not anyone's belief that "everyone has moved."
- **Sunset headers (RFC 8594)**: make the deprecation timeline visible to consumers' own monitoring.

## Mental Models
- Think of a contract change as the inverse of the AI's instinct. The AI breaks things quietly, now, bundled with a feature. The safe path breaks them loudly, later, on their own.
- Use the contract file as an enforcer, not a spec the generator negotiates with: "An agent that is allowed to change the specification until its implementation passes does not have a specification."
- Treat a red contract test after an AI "cleanup" as the system working. It caught a consumer outage locally.
- Concurrency (Ch 17) and contract drift both live at seams that in-process tests don't watch. You tame both by forcing the failure into a local, automated signal you can paste back to the AI.

## Anti-patterns
- **"Add a status column and clean up the schema"**: the AI also drops the column it thinks is redundant and renames another. Each edit is locally reasonable, and together they're an outage.
- **Destructive changes bundled with a feature migration**: there's no rollback path, and old app versions fail on deploy.
- **Ad-hoc `ALTER TABLE` run by the AI against a connection**: there's no ordered, reviewable artifact and no test surface.
- **"Tidy up the order response"**: renaming `customer_id` to `customerId`, promoting a string to an object, dropping "unused" fields. Each one breaks a consumer you don't control.
- **AI-editable OpenAPI doc or contract tests**: the generator edits the contract until it passes. Ch 5's "do not modify the test" clause applies in full.
- **Deprecation recorded in Slack**: when a consumer breaks six months later, there's no committed record of the warning.

## Code Examples
```java
@Test void migrationIsBackwardsCompatible() {
    flyway.migrate(); // apply through the new migration
    // The previously-deployed app version's queries must still succeed
    assertThatCode(() -> legacyDao.readUsingOldSchema())
        .doesNotThrowAnyException();
}

@Test void responseStillMatchesPublishedContract() {
    var response = mockMvc.perform(get("/orders/42"))
        .andReturn().getResponse().getContentAsString();
    // Validates against the committed, human-owned OpenAPI schema
    openApiValidator.assertValid("/orders/{id}", "GET", 200, response);
}
```
- **What it demonstrates**: two local guardrails. A sneaked-in `DROP COLUMN` fails the first test, and any wire-shape drift fails the second, inside the generator's own loop.

## Reference Tables
| Beat | Database | API |
|---|---|---|
| Expand | Add nullable/defaulted column or new table; no rename/drop/retype/NOT NULL | New field (not renamed), `v2` beside `v1`, new enum value |
| Migrate | Backfill; move readers/writers while old shape works | Consumers move on their schedule; `Deprecation` + `Sunset` headers |
| Contract | Separate later migration drops the old column | Remove `v1` only when no consumer contract references it |
| Proof | Old-version-against-new-schema test | Consumer-driven contract verification |

| Posture | Source of truth | Fails when | Use |
|---|---|---|---|
| Schema-first | Committed, AI-locked OpenAPI | Response diverges from doc | Default under vibe coding |
| Consumer-driven | Consumers' published contracts | A real consumer would break | Strongest signal; removal gate |

## Worked Example
Prompt: "Tidy up the order response." The AI renames `customer_id` to `customerId` for consistency. The mobile app, which can't be redeployed, depends on `customer_id`. Because `openapi.yaml` is frozen and `responseStillMatchesPublishedContract` exists, the test goes red locally. Paste back: "The contract test fails: `customer_id` was renamed. Restore the wire field; keep any internal renaming behind the serialization boundary." The AI keeps the Java field `customerId` and maps it to the JSON property `customer_id` (e.g. via a serialization annotation). The test goes green, and no consumer ever sees the change.

## Why It Works / Failure Mode
- **Expand/contract** works because it splits one dangerous change into a safe additive step and a destructive step that's isolated, justified and delayed, and the version-compatibility test checks the split mechanically. It fails if the destructive step is still bundled in, or if migrations run outside the versioned tool.
- **Frozen contract + contract test** works because the box (the wire shape) is a committed artifact the generator can't write to, enforced by a test it can't weaken. It breaks the moment the AI may edit `openapi.yaml` or the assertions. Then the spec just follows the implementation.

## Key Takeaways
1. A contract break is total and immediate: the blast radius is every consumer at deploy.
2. Every migration is additive. Destructive changes are their own justified, later migration.
3. Use Flyway or Liquibase plus a test that the previous app version still works against the new schema.
4. Freeze the wire contract (OpenAPI schema-first, ideally plus consumer-driven contracts), keep it out of the AI's writable scope, and never let it weaken the contract test.
5. Breaking API changes are versioned expand/migrate/contract, with Sunset headers and consumer contracts as the removal gate.
6. Name consumers and frozen files in every schema-touching prompt. The AI can't respect a contract it doesn't know exists.
7. Rename internals freely, but the JSON property is the contract.

## Connects To
- **Ch 4**: `@AIContract` (Java signature) and `@AILocked` (freezing the contract file).
- **Ch 5**: architecture as tests, the "do not modify the test" clause, and leaky-entity discipline at the serialization boundary.
- **Ch 17 / 17b**: the sibling failure modes inside the process (concurrency, cost).
- **Ch 18b**: the other external contract, dependencies you import.
- **Ch 18c**: expand-contract applied to data encodings.
- **Ch 20**: the Attacker Agent fuzzes this contract.
- **Ch 21**: CI enforcement of the additive-migration rule.
- **Ch 23**: prompt lineage, with deprecation intent kept in version control.
- **Parallel change / Refactoring Databases (Ambler & Sadalage)**; **Consumer-driven contracts (Pact)**; **RFC 8594 Sunset header**.
