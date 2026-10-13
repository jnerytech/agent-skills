# Chapter 9: Kiro: When the IDE Is the Spec Engine

## Core Idea
Kiro is the second shape of spec-driven tooling: an agentic IDE/CLI where the spec is the substrate, not a harness bolted on top. It makes the "plan, then execute" loop the path of least resistance for individuals, but it industrializes the *authoring* of intent, not its *enforcement*.

## Frameworks Introduced
- **The Spec Trinity (requirements / design / tasks)**: decompose each feature into three version-controlled Markdown artifacts instead of one prose blob.
  - When to use: every feature, as the default file layout for the Chapter 7 "plan, then execute" gate.
  - How: (1) A natural-language prompt is turned into `requirements.md` (what and why). (2) Requirements drive `design.md` (technical approach). (3) Design decomposes into `tasks.md` (ordered, implementable breakdown) the agent executes. (4) Review and commit each artifact before the next is generated.

- **EARS-Constrained Requirements**: pin requirements to the Easy Approach to Requirements Syntax: `WHEN [trigger], THE SYSTEM SHALL [response]`.
  - When to use: any requirement an AI will implement; it is the Section 7.4 schema mechanism moved upstream to the moment intent is first written.
  - How: rewrite each free-text wish as a trigger/response predicate that can be measured. A constrained grammar collapses the model's improvisation space to near zero: the grammar is the hallucination suppressant.

- **Spec-Native Project Setup Order**: steering → specs → hooks → MCP.
  - When to use: standing up a project in a spec-native environment.
  - How: (1) Steering files first (invariants, Chapter 3). (2) Specs (per-feature intent, Chapter 7). (3) Hooks (local automation). (4) MCP servers (external reach). Pin the tool version your team adopts for reproducibility (Section 8.2).

## Key Concepts
- **Harness vs spec-native environment**: a harness (Spec Kit) standardizes the loop across a team's existing agents; a spec-native IDE makes the loop the default for the individual.
- **Steering files**: project-resident Markdown loaded on every turn; the Chapter 3 Context Diet promoted to a first-class feature.
- **Hooks**: actions triggered on development events (save, test change, commit prep); cooperative local automation.
- **MCP servers**: Model Context Protocol connections giving the agent first-class access to databases, ticketing, internal APIs.
- **Powers**: on-demand bundles of domain-specific context and tooling loaded only when a task needs them.
- **Pull, not push**: keep standing context lean; let the agent acquire specialized context when the task is at hand.
- **IDE vs CLI**: the same loop at two latencies: the IDE is where a human authors/reviews intent, the CLI is how it runs unattended in pipelines.

## Mental Models
- Think of the tool as the example: products get acquired or shut down; the durable move is *versioned requirements/design/tasks with requirements pinned to a grammar*.
- Treat a local hook as fast feedback, not enforcement: anything local can be skipped, disabled, or never installed, and an autonomous agent feels no friction doing so. The mandatory version is the branch (Part IV).
- Use MCP and Powers instead of growing steering files: retrieval on demand beats stuffing standing instructions.
- A pristine EARS spec with no test, contract, or annotation behind it is a wish with good grammar.

## Anti-patterns
- **Vague requirements ("handle errors gracefully")**: the AI satisfies them in whatever way is cheapest.
- **Steering directory as wish list**: steering files sit under the same context-fatigue ceiling as any CLAUDE.md; keep them short, falsifiable, and pointing at executable enforcers rather than trying to be the enforcer.
- **Treating local hooks as enforcement**: they are the local mirror of the pipeline, not a substitute for it.
- **Equating a polished spec with a true one**: the environment produces and orders the spec; it does not make it true.

## Code Examples
```text
Vague:  Handle errors gracefully.
EARS:   WHEN the payment provider returns a timeout,
        THE SYSTEM SHALL retry twice and then mark the order payment_pending.
```
- **What it demonstrates**: turning a wish into a measurable trigger/response predicate the model can be held to.

## Reference Tables
| Shape | Tool | Spec form | Strength |
|---|---|---|---|
| Harness | Spec Kit (Ch 8) | Markdown a human reads | Standardizes loop across existing agents |
| Environment | Kiro (Ch 9) | EARS a grammar constrains | Loop is the default path for the individual |
| Executable graph | Zenflow (Ch 10) | Validated DAG a machine runs | Fails before a token is spent |
| Context framework | GSD (Ch 11) | Context engineering | Context as central concern |

## Why It Works / Failure Mode
- **EARS + trinity**: each artifact is reviewed and committed before the next is generated, and the grammar removes degrees of freedom the model would improvise into. Fails when nothing executable stands behind the spec: Kiro will satisfy its letter and still erode the structure underneath. Enforcement remains the tests, annotations, and diagrams of Chapters 4–6.
- **Steering**: moves intent from the volatile chat window into the repository. Fails by overuse: a built-in feature invites growth into a rotting wish list.

## Key Takeaways
1. Decompose features into requirements, design, and tasks; gate each before the next.
2. Write requirements in EARS: `WHEN [trigger], THE SYSTEM SHALL [response]`.
3. Keep steering files short, falsifiable, and pointing at enforcers.
4. Local hooks give fast feedback; only the pipeline gives enforcement.
5. Prefer pull (MCP, Powers) over push (bigger standing context).
6. Set up in order: steering, specs, hooks, MCP; pin the tool version.
7. The principle (spec-native environment) outlives the vendor.

## Connects To
- **Ch 7**: intent as durable source of truth; Section 7.4 schema as hallucination suppressant; "plan, then execute".
- **Ch 8**: Spec Kit, the harness shape; Section 8.2 version pinning.
- **Ch 3**: Context Diet; steering files are its first-class form.
- **Ch 4–6**: annotations, ArchUnit, living diagrams: the actual enforcement.
- **Ch 10 / Ch 11**: the next two tooling shapes; Ch 11 makes "local can be skipped" central.
- **Part IV**: branch/pipeline enforcement.
- **EARS (Mavin et al., Rolls-Royce)**; **Model Context Protocol**.
