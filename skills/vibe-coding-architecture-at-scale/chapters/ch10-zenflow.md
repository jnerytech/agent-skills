# Chapter 10: Zenflow: The Spec as an Executable DAG

## Core Idea
Zenflow is the third shape of spec-driven tooling, the multi-agent spec orchestrator: the spec is a declarative, schema-validated workflow graph that an engine executes. Its key move is validation before a token is spent, so a malformed plan fails like a failed compile, not like a confused agent halfway through a paid session.

## Frameworks Introduced
- **Workflow File as Spec (declarative DAG)**: state the work as a typed YAML file of agents, steps, dependencies, conditions (CEL), and loops; the prompt shrinks to a step's `instructions` field, a trigger rather than the source of truth.
  - When to use: any multi-agent run you need to specify, version, and reproduce.
  - How: (1) Declare agents with roles (e.g. `implementer`, `inquisitor`). (2) Declare steps, each bound to one agent with scoped instructions. (3) Express ordering via `dependsOn`, conditions via CEL. (4) Commit the file; it is the spec.

- **Validate Before Generation**: check the workflow against `spec/v1/schema.json` plus conformance fixtures before any LLM call.
  - When to use: always, as the earliest point a guardrail can fire.
  - How: the validator catches cycles, unknown dependencies, and malformed CEL in milliseconds at zero tokens; an invalid spec never runs. This merges Section 7.4 (schema removes degrees of freedom) and Chapter 5 (spec as a test that fails loudly) and moves both before generation.

- **Mediated Hub-and-Spoke Coordination**: every agent talks only to a central coordinator via a per-agent mailbox; no peer-to-peer.
  - When to use: multi-agent systems where reproducibility matters.
  - How: explicit delivery and explicit drop reasons; independent steps parallelize through the DAG executor, dependent steps wait. No silent loss, no out-of-order surprises. Determinism is not a performance feature; it is what makes a run specifiable.

- **Draft with `goal`, Commit and Run with `flow`**: the three entry points form a spectrum from fully specified to spec-synthesized.
  - When to use: when you want speed without losing the artifact.
  - How: let `zenflow goal` synthesize a workflow from a prompt, then review and commit it and execute via `zenflow flow`. A synthesized DAG is a generated spec, only as trustworthy as any generated spec.

## Key Concepts
- **Zenflow**: a single Go binary coordinating LLM agents through a hub-and-spoke message bus; the runtime matters less than what it forces you to write.
- **DAG executor**: runs independent steps in parallel, dependent steps in order.
- **CEL expressions**: Common Expression Language conditions inside the workflow.
- **Conformance fixtures**: test cases the workflow must satisfy alongside the JSON schema.
- **Well-formed vs correct**: schema validation proves the workflow parses and resolves, not that the agents' architecture is sound.
- **AGENTS.md / CLAUDE.md vs SKILL.md**: the former instruct an agent *editing* Zenflow's code; SKILL.md is the contract for an agent *consuming* Zenflow (CLI verbs, NDJSON event schema, exit codes).
- **Agent-facing contract**: a scoped, machine-readable file so any agent on any platform drives the tool the same way.

## Mental Models
- Think of the spec hardening one notch per tool: Markdown a human reads (Spec Kit) → EARS a grammar constrains (Kiro) → a DAG a machine executes (Zenflow).
- Think of free-for-all agent-to-agent prompting as the multi-agent version of the volatile chat window; a mediated, validated DAG is the multi-agent version of the durable repository.
- Use the fast path (`goal`) to produce the artifact, never as a replacement for having one.
- The tool is the example: any engine that validates a declared workflow before spending a token gives you the benefit; the binary is incidental.

## Anti-patterns
- **Prompt-driven orchestration**: tangles (self-waits, missing steps) surface only as a deadlock deep in a paid session, leaving you to reverse-engineer a transcript.
- **Treating the `goal` prompt as the artifact**: an uncommitted synthesized workflow is unreviewed, unversioned intent.
- **Peer-to-peer agent chatter**: nondeterministic and unrepeatable; you can only observe it, not specify it.
- **Confusing validation with enforcement**: a valid DAG still only orchestrates what you thought to declare.

## Code Examples
```yaml
name: review-feature
agents:
  implementer: { description: "Writes the feature against the spec" }
  inquisitor:  { description: "Adversarial reviewer; cites the rules" }
steps:
  - id: build
    agent: implementer
    instructions: "Implement the spec in feature-spec.md. Do not weaken any test."
  - id: review
    agent: inquisitor
    instructions: "Diff against the architecture rules. Block on any violation."
    dependsOn: [build]
```
- **What it demonstrates**: the spec as a versioned DAG with an implementer and an Inquisitor reviewer; the prompt is reduced to per-step instructions.

```text
$ zenflow flow workflow.yaml
✗ spec invalid (0 agents invoked, 0 tokens spent)
  - step "review": dependency cycle (review → review)
  - step "ship": dependsOn references unknown step "merge"
```
- **What it demonstrates**: structural defects caught at the cheapest point, with a line-pointing diagnostic instead of a transcript.

## Reference Tables
| Command | Spec status | Use |
|---|---|---|
| `zenflow flow workflow.yaml` | Fully declared, validated | Disciplined case: execute DAG to completion |
| `zenflow goal "<prompt>"` | Synthesized by coordinator | Fast path to *draft* a workflow; then commit and `flow` it |
| `zenflow agent "<prompt>"` | None | Single agent with optional tool loop |

## Worked Example
A fat-fingered workflow: `review` has `dependsOn: [review]` (waits on itself) and a new `ship` step has `dependsOn: [merge]`, a step never declared. A prompt-driven orchestrator would start building, spend tokens, then deadlock at review or fail at ship deep into the session. Zenflow validates against `spec/v1/schema.json` and refuses to start: two structural errors reported, 0 agents invoked, 0 tokens spent. The failure reads "the spec was malformed and never ran," not "the AI built the wrong thing."

## Why It Works / Failure Mode
- **Validate-before-generation**: the schema both constrains what can be expressed and acts as a test, with no model in the loop to be confidently wrong. Fails at the semantic layer: well-formed is not correct. Zenflow guarantees parsing, dependency resolution, and ordered delivery, not sound architecture; enforcement still lives in the tests, annotations, and diagrams of Chapters 4–6.
- **Mediated coordination**: one coordinator with explicit delivery/drop semantics makes runs reproducible. Fails if teams bypass it with ad hoc agent-to-agent prompting.

## Key Takeaways
1. Express multi-agent work as a declarative, version-controlled DAG; that file is the spec.
2. Validate the workflow against a schema and fixtures before spending any tokens.
3. Route all agent communication through a coordinator; determinism is what makes a run specifiable.
4. Use `goal` to draft, `flow` to run committed workflows.
5. Ship a SKILL.md-style agent-facing contract (verbs, event schema, exit codes) for tool consumers.
6. Schema validity is not correctness; keep the Ch 4–6 guardrails.

## Connects To
- **Ch 7 (Section 7.4, 7.6)**: schema as strongest hallucination suppressant; the multi-agent spec orchestrator shape.
- **Ch 5**: spec as a test that fails loudly.
- **Ch 8 / Ch 9 / Ch 11**: the other three tooling shapes (harness, environment, context framework).
- **Ch 3 / Ch 4**: AGENTS.md/CLAUDE.md vs SKILL.md mirrors the context-file vs annotation distinction and cross-platform consistency.
- **Ch 22**: the Inquisitor as adversarial reviewer step.
- **Ch 1**: a volatile source of truth is no source of truth.
- **Compile-time vs runtime failure**; **CEL (Common Expression Language)**; **hub-and-spoke messaging**.
