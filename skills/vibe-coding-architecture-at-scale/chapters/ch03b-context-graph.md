# Chapter 3b: From Context Diet to Context Graph

## Core Idea
The three-tier diet controls the calories but not the architecture of what you feed: by around month six, knowledge (redesigns, incident lessons, boundary rationale) outgrows twenty lines and sprawls into a 600-line CLAUDE.md and an unlinked `docs/` graveyard. Replace the flat wall of text with a different container — a **lat.md** knowledge graph of small linked markdown nodes, bidirectionally anchored to code and validated by a CLI in CI.

## Frameworks Introduced
- **Wall vs. Graph (Container vs. Content)**: a flat context file is read sequentially and degrades in the middle no matter how well written; a knowledge graph lets the agent traverse from an entry point to only the connected nodes it needs.
  - When to use: when knowledge itself has structure (decisions → code, incidents → rules).
  - How: stop curating the wall; give the knowledge a structured container. "You cannot diet a flat file into a graph."
- **lat.md Knowledge Graph**: a `lat.md/` directory at project root replacing the monolithic instruction file with focused, interlinked markdown nodes.
  - When to use: medium-to-complex projects (see triggers below).
  - How: (1) one bounded file per concept (`architecture.md`, `auth.md`, `payments.md`, `inventory.md`, `tests.md`); (2) link with wiki references plus section anchors `[[payments#PaymentPort]]`; (3) link nodes to source `[[src/payments/PaymentPort.java#PaymentPort]]`; (4) mark critical sections `require-code-mention: true` so code must reference them; (5) anchor code back with `// @lat: [[section]]`; (6) run `lat check` in CI. Install `npm i -g lat.md`, `lat init`.
- **Bidirectional Links**: knowledge → code (source references inside nodes) and code → knowledge (`@lat:` comments).
  - When to use: to close the staleness loop from Ch 3.
  - How: when a referenced file moves or changes, `lat check` fails loudly in the same feedback loop the AI already watches — knowledge cannot drift in silence.
- **The Staleness Principle**: "Unverified documentation is a liability with a shelf life." Docs fail not because nobody wrote things down but because nothing failed when they stopped being true; making link integrity a build verdict surfaces decay the day it happens.
- **Four Operational Triggers for adopting lat.md**:
  - How: adopt when any applies — (1) **Context window bloat**: the central instruction file is a monolith; `lat search` retrieves only the needed subset; (2) **Distributed domain logic**: one change requires several disjoint files; nodes link to them (`[[src/auth.java#validateToken]]`) instead of brittle grepping; (3) **Groundhog Day syndrome**: you re-explain the same constraints every session; the graph makes knowledge cumulative, and the agent can write new decisions back into nodes; (4) **Referential integrity**: you need verifiable spec-to-source links; `@lat` anchors + `lat check` in CI prevent silent orphaning.

## Key Concepts
- **Graveyard problem**: 600-line CLAUDE.md, fourteen unstructured docs, incident context in an unlinked `notes.md`; the agent attends to maybe a third and hallucinates connections that aren't written down.
- **Knowledge node**: a bounded document about one concept, explicitly linked to related concepts and to code that implements/enforces it.
- **Wiki link with section anchor**: `[[file#Section]]` syntax for node-to-node and node-to-source references.
- **`require-code-mention: true`**: enforcement directive — the section must be referenced by actual code or `lat check` fails; wires incident context to the code changed because of it.
- **`@lat:` anchor**: in-line comment in any language tying an implementation to its governing node.
- **Architectural knowledge layer**: the graph sits *between Tier 1 and Tier 2* — too rich for 20 lines, too cross-cutting for a single directory.
- **Enforcement boundary**: the CLI only enforces what the graph knows; a rule never written down stays invisible.
- **Structural threshold**: adoption is triggered by structure (unmaintainable instruction file, fragmented knowledge), not lines of code.

## Mental Models
- Think of Tier 1 as the *what* ("no business logic in controllers") and the graph as the *why* — linking to the incident that made the rule and the test that enforces it.
- "A knowledge graph that can go stale without failing a check is a graveyard with a nicer directory structure."
- Use domain complexity, not code volume, to decide: a small concurrency library or prompt-injection firewall can be dense in rationale and still benefit.
- Think of the graph and annotations as complementary: the graph carries system-level reasoning; annotations (Ch 4) carry per-element enforcement.

## Anti-patterns
- **Growing CLAUDE.md to hold all accumulated knowledge**: attention collapses; agent hallucinates links.
- **Unstructured `docs/` folders and orphan `notes.md`**: knowledge exists but isn't reachable or verified.
- **A graph without the CLI in CI**: decays into the same graveyard it replaced.
- **Adopting lat.md on small projects** (utility library, three-month project, two-person team): link maintenance, `@lat` wiring and checks cost more than they save; flat three-tier model suffices.
- **Assuming the tool captures unwritten rules**: it makes written knowledge reliable; it can't substitute for writing it down.

## Code Examples
```text
lat.md/
  architecture.md   <- system boundaries, key tradeoffs, non-negotiable decisions
  auth.md           <- OAuth flow, session model, token lifecycle
  payments.md       <- module boundaries, external provider contracts
  inventory.md      <- synchronous-call prohibition, cascade-risk documentation
  tests.md          <- integration test scope, coverage requirements
```

```markdown
<!-- inventory.md -->
## The Synchronous Call Prohibition
Calling InventoryService synchronously from within a request thread caused the
March cascade failure. All inventory queries now go through the async queue.
See [[tests#Integration Specs]] for the contract test enforcing this boundary.
require-code-mention: true
```

```java
// @lat: [[inventory#The Synchronous Call Prohibition]]
CompletableFuture<InventoryStatus> checkStock(OrderId id) {
    return asyncInventoryQueue.submit(id);
}
```
- **What it demonstrates**: an incident lesson wired bidirectionally — node requires a code mention, code anchors back; `lat check` fails if either side breaks.

## Reference Tables
**lat CLI commands**

| Command | Purpose |
|---|---|
| `lat check` | validate every link: broken wiki refs, dead source anchors, unreferenced `require-code-mention` sections — run in CI |
| `lat search` | semantic vector search; agent's entry point to an unfamiliar task without reading everything |
| `lat section` / `lat expand` | navigate section ref → content; source ref → current code snippet (no grepping) |
| `lat refs` | all source references to a node — answers "what code is governed by this decision?" |

**Where lat.md sits in the tier model**

| Layer | Holds | Example |
|---|---|---|
| Tier 1 (CLAUDE.md) | ~10 non-negotiable invariants | "no business logic in controllers" |
| lat.md graph | system decisions, post-mortems, trade-offs, non-obvious deps | why the rule exists, link to incident and test |
| Tier 2 | directory-scoped module rules | `payments/` rules |
| Tier 3 (Ch 4) | per-element annotations | lock-free class |

**When to adopt**: small project → overkill; medium-to-complex or high domain-complexity → sweet spot.

## Worked Example
**The inventory cascade, before and after.** Before: a March cascade failure (three engineers, two days to diagnose) taught "never call InventoryService synchronously from a request thread." The lesson lands in `notes.md`; nobody links it; months later the agent, reading a 600-line CLAUDE.md, writes a synchronous call. After: `inventory.md` holds the prohibition with `require-code-mention: true` and a link to the contract test in `tests.md`; `checkStock` carries `// @lat: [[inventory#The Synchronous Call Prohibition]]`; when an agent works on inventory it runs `lat search "inventory call"`, lands on the node, follows links to the test and code. If someone moves `checkStock` and drops the anchor, `lat check` fails in CI.

## Why It Works / Failure Mode
- **Works** because traversal replaces sequential reading (no lost-in-the-middle over a wall), and bidirectional links + `lat check` turn documentation drift into a build failure — closing the staleness loop from Ch 3.
- **Fails** without CI enforcement (graph decays into a graveyard), on small projects (overhead > value), and for anything never written into the graph (invisible to the CLI).

## Key Takeaways
1. The diet fixes size; it doesn't fix structure — around month six, flat files fail.
2. Change the container: small linked nodes, traversed on demand.
3. Link both ways — knowledge to code and code (`@lat:`) to knowledge.
4. `lat check` in CI is what makes it a graph and not a graveyard.
5. Adopt on structural triggers (bloat, distributed logic, Groundhog Day, referential integrity), not LOC.
6. The graph holds the *why* between Tier 1 and Tier 2; annotations hold per-element enforcement.

## Connects To
- **Ch 3**: three-tier model and the staleness problem this solves.
- **Ch 3c / 3d / 3e**: token-economy runtime, harness configuration, agent memory discipline.
- **Ch 4**: per-element annotations — complementary to the graph.
- **Ch 5**: architectural tests the graph links to as enforcers.
- **Ch 21**: CI as the place `lat check` runs alongside architectural tests.
- **Ch 23**: prompt lineage — another way to version the *why*.
- **Architecture Decision Records (ADRs)**, **Zettelkasten / wiki-linked notes**, **docs-as-code**.
