# Chapter 5c: AI-Native Design Patterns

## Core Idea
Classical design patterns managed human working memory; AI-native patterns manage the agent's constraints — context window density, attention dilution, and navigation — while keeping human intent as the controlling surface. Each pattern must name its enforcement, because a pattern that cannot fail a build is a suggestion.

## Frameworks Introduced
Each pattern uses the classical form (context, problem, solution, impact) plus an explicit enforcement.

- **Spec-Implementation Separation Pattern (Context Decoupling)**: isolate public contracts into an `api/` or `spec/` module, detached from `impl/`.
  - When to use: large services or modular monoliths where domain models, interfaces, queries and helpers are co-located in the same files, so the agent loads thousands of irrelevant lines to learn a boundary.
  - How: (1) `spec` holds only interfaces and immutable models/DTOs — no business logic, no queries, no private helpers; (2) `impl` depends on `spec` and holds execution logic; (3) tooling rules restrict the agent to reading `spec` during routing, planning and mapping, and `impl` only during active coding. Enforcement: one ArchUnit rule asserting nothing in `spec` depends on `impl`.
- **Interface-First Development Pattern (Contract-to-Token Efficiency)**: during integration, the agent's context holds the interface, not the concrete class, and signatures document themselves.
  - When to use: internal service interfaces and API boundaries where agents write the call sites.
  - How: expose a ~20-line interface instead of the 500-line implementation; replace `Map<String, Object>` payloads and bare boolean flags (connascence of meaning) with strongly typed domain and parameter objects (connascence of name and type). Enforcement: the type system plus a review rule flagging `Map<String, Object>` returns on public boundaries.
- **Self-Documenting Exception Pattern (Error-to-Spec Routing)**: custom exceptions carry machine-resolvable links to diagnosis and recovery instructions.
  - When to use: automated test pipelines and self-correcting loops where agents receive stack traces and attempt fixes.
  - How: append a wiki anchor or lat.md node path (e.g. `[[lat.md/troubleshooting.md#db-pool-drift]]`) to the exception message; the agent's tool chain resolves the link and fetches explicit do/don't steps. Enforcement: `lat check` fails the build when a diagnostic link goes stale.
- **Feature-Locality Pattern (One Feature, One Directory)**: package by feature, package-private by default, a small public port as the only entry.
  - When to use: layer-first codebases (`controllers/`, `services/`, `repositories/`) where every task starts with a scavenger hunt across parallel trees.
  - How: one directory per feature containing controller, service, persistence and models; the sole public type is a port (e.g. `PaymentPort`). Enforcement doubled: compiler rejects cross-feature access to package-private types; Ch 5 ArchUnit/Modulith rules fail on new inter-feature dependencies.

## Key Concepts
- **Context window density**: how much task-relevant signal is in what the agent loads; the agent's equivalent of human working-memory limits.
- **Attention dilution**: attention spent on irrelevant code (helpers, logging, serialization) is unavailable for the contract, raising the odds of a wrong call.
- **Spec module**: interfaces and immutable models only; the planning-time view of the system.
- **Connascence of meaning**: coupling via undocumented value meanings (map keys, boolean flags) — the weakest form to leave across a module boundary.
- **Self-documenting signature**: types alone reveal parameter structure and return shape; "the contract is the documentation."
- **Diagnostic Spec link**: a resolvable reference in an exception message routing the agent from failure back to the specification.
- **Blast radius**: the scope a task should touch; feature-locality makes loaded context match it by construction.
- **Port**: the small public type through which other features reach an otherwise package-private feature.

## Mental Models
- Think of each AI-native pattern as a classical discipline (module decoupling, contract-first design, diagnosable failures, high cohesion) re-derived from a new constraint: the agent didn't change what good structure is, it changed the price of ignoring it.
- Use Feature-Locality first: it asks the least and pays the most often, turning the agent's most frequent operation (finding the code) from search into lookup.
- Think of errors as navigable entries into the knowledge graph rather than dead ends.
- Use the enforcement, not the pattern catalogue, as the part that matters.

## Anti-patterns
- **Interleaving contracts with implementation**: the agent loads the whole file to learn the API.
- **`Map<String, Object>` / boolean-flag signatures on public boundaries**: force the reader to open the implementation and invite plausible-but-wrong call sites.
- **Generic exceptions (`DatabaseConnectionException: Connection timeout`)**: the agent guesses, writes retry logic, edits DB config in a loop, compounding the error.
- **Layer-first packaging**: every loaded neighbor is an invitation to change code outside the intended blast radius.
- **Patterns without enforcement**: suggestions decay (Ch 1).

## Code Examples
```java
// Anti-pattern: the agent must read the implementation to guess the map keys
Map<String, Object> updateUser(String id, boolean flagA, boolean flagB);

// Pattern: the schema and the options are legible from the types alone
UserUpdateResult updateUser(UserId id, UserStatusUpdateOptions options);
```
- **What it demonstrates**: converting connascence of meaning into compiler-checked connascence of name and type.

```java
public class DatabasePoolDriftException extends RuntimeException {
  public DatabasePoolDriftException(String message) {
    super(message + " | Diagnostic Spec: [[lat.md/troubleshooting.md#db-pool-drift]]");
  }
}
```
- **What it demonstrates**: an exception that routes the agent to its recovery spec.

```
[api/spec module]  <--- read by agent for planning (minimal context)
 ├── UserInterface.java
 └── UserDTO.java
        ▲ implements / depends on
[impl module]      <--- read by agent only during active coding
 ├── UserServiceImpl.java
 └── UserRepository.java
```

## Reference Tables
| Pattern | Agent constraint addressed | Solution | Enforcement |
|---|---|---|---|
| Spec-Implementation Separation | Context density in planning | `spec/` (interfaces, DTOs) vs `impl/` | ArchUnit: `spec` must not depend on `impl` |
| Interface-First Development | Token cost and guessing at call sites | 20-line interface + typed signatures | Type system + review rule on `Map<String,Object>` |
| Self-Documenting Exception | Guessing root cause from stack traces | Diagnostic Spec links in messages | `lat check` fails on stale links |
| Feature-Locality | Navigation by search | One feature, one directory, package-private, one port | Compiler + ArchUnit/Modulith module rules |

## Worked Example
**Error-to-Spec routing for connection pool drift.** A test fails with:
```
com.example.db.DatabasePoolDriftException: Connection pool size drifted to 50 | Diagnostic Spec: [[lat.md/troubleshooting.md#db-pool-drift]]
  at com.example.db.ConnectionPool.verify(ConnectionPool.java:42)
```
Without the link, the agent would raise the pool size or add retries. With it, the tool chain resolves the node, which instructs: (1) do not increase the pool size in `application.yml`; (2) verify the caller releases the connection it acquired — the release obligation is declared in the `@AIContract` on `ConnectionPool.acquire()` (Ch 4); (3) check `tests/txn-audit.log`. The agent fixes the leaking caller instead of masking the symptom, inside the inner feedback ring Ch 5b budgets for.

**Feature-locality layout**:
```
src/main/java/com/shop/
  checkout/   ← everything checkout: port, service, repository, models
  inventory/  ← everything inventory
  payments/   ← everything payments; PaymentPort is the sole public type
```

## Why It Works / Failure Mode
- **Spec-Implementation Separation**: shrinks the planning-time contract from codebase size to interface size, the same decoupling spec-driven development does at document level. Fails if the boundary is a convention only — without the ArchUnit rule, logic creeps into `spec` and the agent loads noise again.
- **Feature-Locality**: loaded context equals blast radius by construction, and visibility physically blocks cross-feature reach-in. Fails if classes default to public or the port grows into a broad public surface.

## Key Takeaways
1. Design for the agent's limits: context density, attention dilution, navigation.
2. Give the agent a spec-only view for planning; load implementation only while coding.
3. Make signatures self-documenting; ban `Map<String, Object>` and bare booleans on public boundaries.
4. Put resolvable diagnostic links in exceptions so failures route back to the spec.
5. Package by feature with package-private default and a single public port — the cheapest, most frequently paid-off pattern.
6. Every pattern names its enforcement; without one it is only a suggestion.

## Connects To
- **Ch 1**: suggestions without enforcement decay.
- **Ch 2b**: "The Canon Doesn't Compile"; connascence vocabulary; only enforceable canon survives.
- **Ch 3b**: lat.md knowledge graph and `lat check`.
- **Ch 4**: `@AIContract` declares obligations referenced by diagnostic nodes.
- **Ch 5**: ArchUnit/Modulith rules and package-by-feature enforce these patterns.
- **Ch 5b**: diagnostic routing keeps correction inside the inner loop budget.
- **Ch 6**: living diagrams of the structure the agent works inside.
- **Ch 7**: Spec-Driven Development at document level.
- **GoF Design Patterns (1994)**, **fitness functions (Ford et al.)**, **connascence (Page-Jones)**, **Software Engineering at Google (Winters et al.)**, **Living Documentation (Martraire)**.
