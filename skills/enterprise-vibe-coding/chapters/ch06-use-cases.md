# Chapter 6: Use Cases: Building Agentic Solutions with the HVE Primitives

## Core Idea
In an agentic product built from HVE primitives, governance is the architecture: the orchestration pattern, the MCP connectors, the agent scopes and a handful of hooks are the controls. Building from primitives pays off twice. It ships the first business outcome (a booking, a sale, a campaign), and it keeps the system cheap and safe to change as suppliers, catalogs and regulations evolve. Three worked products show this: a travel concierge, a shopping assistant and a campaign generator.

## Frameworks Introduced
- **MAF orchestration pattern selection (Microsoft Agent Framework, five built-in patterns)**: Sequential, Concurrent, Group chat, Magentic, Handoff.
  - When to use: at the start of any multi-agent project, before writing agents. Choose the pattern from the *shape of the problem*, not from habit.
  - How: match the problem shape to a pattern:
    - Sequential is a fixed assembly line where each output feeds the next (draft → review → compliance check). Use it only when later steps really depend on earlier ones being complete.
    - Concurrent runs agents in parallel on the same input, and a coordinator aggregates the results. Use it for fan-out from independent specialists (three reviewers grading one document, three retrievers over three corpora).
    - Group chat puts agents in a shared conversation, and an orchestrator picks who speaks next. Use it for iterative refinement in rounds.
    - Magentic has a manager agent that builds and revises a task list on the fly. Use it for open-ended problems whose steps you cannot declare in advance.
    - Handoff passes control from agent to agent based on live context, so exactly one agent talks to the user at a time. Use it for single-threaded conversations where the right specialist changes with the topic.
  - Why it works / failure mode: a wrong fit leaks into the user experience. For travel, sequential imposes a rigid order the customer does not follow. Concurrent produces two voices the customer must reconcile. Group chat and Magentic are overkill when branching is limited and the roles are known in advance. Handoff fits: one voice, a clean transfer when the topic changes, and a trace of which agent owned each decision.

- **Advice / Action / Transaction boundary**: split what an agent may do into three explicit tiers.
  - When to use: any customer-facing agent that touches revenue (commerce, booking).
  - How:
    - (1) Advice: recommend, compare, explain trade-offs, ask clarifying questions. This tier has the most freedom.
    - (2) Action: low-risk state changes on the customer's behalf, such as adding to a cart or placing a hold. Allow these only if they fall inside the business-approved scope, and validate price and stock against the system of record first.
    - (3) Transaction: checkout and payment stay *outside* the agentic boundary, in the existing secure flow, with the agents on the outside of it.
    - Customers must always be able to review, remove or undo agent actions before checkout.
    - Escalate to a human when there is uncertainty, high financial value, conflicting system data, repeated failures or suspected fraud.
  - Why it works / failure mode: customer authorization does not remove business accountability. The organization stays accountable for the boundary it sets, so the boundary must be designed deliberately and never left implicit. Customer control is a tunable design choice. It runs from "recommend only, confirm before every cart add" to "proactively add/update within agreed preferences".

- **RPI applied at runtime (product-level Research → Plan → Implement)**: the RPI cadence also structures the *product's* agentic flow, not just the dev loop.
  - When to use: to design what each agent does in each phase of a live interaction.
  - How:
    - Research grounds the agent in systems of record. Live fares, inventory, price, stock and compliance rules always come from tools, never from model memory.
    - Plan synthesizes the options into one coherent proposal with the trade-offs explained. A human gate goes here where stakes demand it; the marketing lead approves the plan before any copy is written.
    - Implement executes through the agent's own connectors, within scope. Irreversible or regulated steps, such as payment and publication, stay human-controlled.

- **Layered automated gate (deterministic → probabilistic → human)**: for content controls.
  - When to use: compliance and brand checks on generated content at volume.
  - How:
    - (1) Fixed rules automatically reject clear violations: prohibited phrases, missing required disclaimers, character limits, regulated claims without approved wording.
    - (2) AI reviewers flag ambiguous content: misleading claims, tone that is wrong for a region, legal risk. These checks are probabilistic and can produce false positives or misses.
    - (3) High-risk claims and regulated campaigns require a legal/compliance specialist's approval before publication.
  - Why it works: not every control should rely on AI judgment. With deterministic checks first, humans only see drafts already clean enough to be worth their time.

- **Six-step method for applying HVE to your own use case**:
  1. Define the business problem and expected outcome.
  2. Select how the agents will work together (orchestration).
  3. Map the six HVE primitives to the solution.
  4. Identify what agents, tools and people are each allowed to decide.
  5. Define the checks, approval points and success measures.
  6. Use the RPI cadence to plan, build and review.

## Key Concepts
- **Concierge agent**: the single agent that owns the customer conversation and hands off to domain specialists (Flight, Hotel, Loyalty, Booking). The customer never sees the internal coordination.
- **Handoff log as audit trail**: the record of which agent held control at each moment. It is the audit of who made which decision.
- **System of record grounding**: every specialist reads from its own authoritative system through MCP/connectors, never from model memory. The agent making a claim is the one connected to the system that backs it.
- **Failure path**: the designed recovery behavior for partial failures, as opposed to the happy path. It covers idempotency against duplicate requests, retries of transient failures within defined limits, preserving or reversing completed steps, and escalation to a human with full handoff/tool-call history.
- **Handoff edge**: a declared, allowed transfer between two agents. You extend the system by adding an agent, exposing its connector and declaring new edges.
- **Build-time vs run-time primitives**: some primitives serve developers building the product (orchestration skill, scaffold prompts, design-system MCP, contract-check hooks). Others serve the running product (booking tools, compliance hooks, audit hooks).
- **Conversational evaluator agent**: a persona that tests the assistant with simulated customer journeys. Conversational quality emerges from whole conversations, which unit tests on single API responses cannot validate.
- **"The control and the construction are the same artifact"**: building from primitives means the governance controls are the connectors, scopes and hooks themselves, not separate policies added later.
- **Maintainability as long-term value**: immediate outcomes secure funding. Value three years later depends on safe, affordable, repeatable updates when suppliers, catalogs and regulations change.

## Mental Models
- Think of **the user-facing agent as one attentive advisor fronting a team of specialists**. Use handoff when the conversation is single-threaded but expertise shifts by topic. One generalist agent tends to become "reasonably good at many things but exceptional at none."
- Use **"generation is cheap; governance is the bottleneck"** when scoping content agents. Drafts take minutes, so the expensive work moves to keeping content accurate, consistent, compliant, localized and on-strategy. Design the pipeline around review, not writing.
- Think of **change as an engineering activity, not reinvention**. If a new supplier, category or regulation forces a rewrite, the system was not built from versioned primitives. If you only update one skill, instruction or connector and everything inherits it, it was.
- Use **"evaluate empirically, don't assume faster"** when adopting multi-agent designs. Handoffs add latency and cost, so measure them against a simpler alternative.

## Anti-patterns
- **One mega-agent expert in every domain**: results are uneven, good at many things and exceptional at none.
- **Designing only the happy path**: a held flight plus a failed hotel confirmation leaves duplicates and orphaned state unless you have idempotency, bounded retries, compensation and human escalation.
- **Quoting prices or inventory from model memory**: you confidently sell a seat or item that no longer exists, at a price you cannot honor. This is the signature failure of travel and retail chat.
- **Letting agents inside the payment/checkout path**: transactions belong in the existing secure flow.
- **Implicit autonomy boundaries**: assuming customer consent covers the business's accountability for what the agent may do.
- **Oversized result lists for ambiguous requests**: ask a targeted follow-up with 2–3 concrete options instead.
- **Governance "bolted on at the end" by a review committee**: controls should be woven into the pipeline as hooks, connectors and scopes.
- **Rules duplicated across a dozen separately maintained prompts**: when a regulation changes, the prompt you miss is the one that ends up in front of the regulator.
- **Relying solely on AI judgment for compliance**: deterministic rules should catch clear violations first.

## Reference Tables

**MAF orchestration patterns**

| Pattern | Mechanics | Good for |
|---|---|---|
| Sequential | Fixed order; each output feeds the next | Pipelines with real dependencies (draft → review → compliance) |
| Concurrent | Parallel on same input; coordinator aggregates | Fan-out to independent specialists |
| Group chat | Shared conversation; orchestrator picks next speaker | Iterative refinement in rounds |
| Magentic | Manager builds/revises a task list dynamically | Open-ended problems with undeclarable steps |
| Handoff | Control transfers by live context; one agent speaks at a time | Single-threaded conversations with shifting expertise |

**Primitives per use case**

| Use case | Primitive | Artifact | Role |
|---|---|---|---|
| SkyBridge | Skill | `maf-orchestration-patterns/SKILL.md` | Templates, selection heuristics and a scaffold for all 5 patterns; reused for every multi-agent project |
| SkyBridge | Prompt | `specialist-agent.prompt.md` | Declares a specialist's scope, allowed handoff peers and callable tools; adding an agent = filling the template |
| Luxe | MCP | `sql-catalog.mcp` | Dev-time controlled access to the catalog DB; the contract between conversational layer and commerce platform |
| Luxe | Prompt | `clarifying-question.prompt.md` | Always 2–3 concrete options, each trade-off explained in the same shape |
| Luxe | Agent | `conversational-evaluator.agent.md` | Simulated shopping journeys; scores recommendations, memory consistency, tool calls and cart flows; structured report |
| Luxe | Hook | `catalog-contract-check` | After an agent edits catalog-touching code, verifies SQL/ORM/API contracts against the approved schema; blocks the commit on breakage |
| SkillForge | Skill | `campaign-workflow-scaffold/SKILL.md` | Patterns for content agents, approval chains, localization, channel adapters, audit logging, human gates |
| SkillForge | Prompt | `campaign-brief-to-workflow.prompt.md` | Developer-facing: turns a campaign spec into agent defs, workflow config, approval states, integrations, data models, events |
| SkillForge | MCP | `figma-design-system.mcp` | Dev-time access to approved Figma assets/templates so generated front-end matches the design system |

**Governance controls mapped to primitives**

| Use case | Control | Enforced by |
|---|---|---|
| SkyBridge | No invented flights/hotels | MCP |
| SkyBridge | No price the pricing tool has not returned | Skill + pre-confirmation hook |
| SkyBridge | No booking without explicit customer confirmation | Agent scope |
| SkyBridge | Audit of every handoff | Hook |
| Luxe | No hallucinated inventory; tool-confirmed pricing; safe marketing claims; advice separated from transaction | Connector config, two hooks, agent scope |
| SkillForge | Claim substantiation and regulated wording | Compliance hook |
| SkillForge | Accessibility checks | Skill |
| SkillForge | Full audit of sources and approvals | Audit hook |

**Table 6.1 — Comparison of the three use cases (with "Your use case" as a design template)**

| Dimension | SkyBridge Travel | Luxe Shopping Assistant | SkillForge Campaigns | Your use case |
|---|---|---|---|---|
| JTBD/Problem | Plan and book a whole trip in one conversation | Discover, compare, select products conversationally | Create and govern multi-channel campaign assets at scale | What job must the system accomplish? |
| Orchestration | Handoff among Concierge, Flight, Hotel, Loyalty, Booking | Single-agent decision support with tool-backed actions and checkout handoff | Workflow/sequential: research → generate → validate → approve | How should agents collaborate? |
| Primitives | Instructions, Skills, Prompts, Agents, Hooks, MCP | All six | All six | Which primitives are required? |
| Lifecycle | Build: orchestration skill, specialist templates. Run: handoffs, booking tools, audit | Build: catalog integrations, evaluator agent, contract checks. Run: recommendations, cart, checkout handoff | Build: scaffold, channel integrations, compliance controls. Run: generation, localization, validation, approvals | What is used at build vs. after launch? |
| Grounding | Live fares, hotel inventory, booking policies, loyalty data | Catalog, live price/stock, reviews, delivery and return policies | Brief, brand guide, past campaigns, compliance rules, design assets | Which systems provide trusted context? |
| Human approval | Customer confirms before booking/payment; escalation when unrecoverable | Customer approves purchase; payment in existing commerce flow | Lead approves plan; legal reviews high-risk claims; publication human-controlled | Where must a human intervene? |
| Metrics | Booking conversion, end-to-end response time, abandonment, human-escalation rate | Conversion, basket size, abandonment, recommendation quality | Campaign lead time, review cycles, compliance failures, cost per approved asset | How will success be measured? |
| Main failure modes | Stale availability, failed booking, duplicate action, incorrect handoff | Stale price/stock, poor recommendation, catalog/schema mismatch | Unsupported claims, brand inconsistency, localization errors, missed compliance rules | What is most likely to fail? |

## Worked Example
**SkyBridge Travel**, a regional Middle East online travel agency. Goal: more direct bookings through conversation instead of search forms.

A customer types: *"I'd like a long weekend in Lisbon next month. Flying from Dubai. Somewhere walkable near Alfama."* This is one request to the customer, but it spans fares, baggage, loyalty, refund rules, hotel availability, location and cancellation terms.

1. **Pattern choice.** The dev agent reads `maf-orchestration-patterns/SKILL.md` and lands on **Handoff**. The conversation is single-threaded, the specialist roles are known, and only one voice may speak.
2. **Specialists declared** with `specialist-agent.prompt.md`: the Concierge, Flight, Hotel, Loyalty and Booking agents, each with a scope, allowed handoff peers and tools.
3. **Research.** The Concierge extracts the constraints: dates, origin, destination, budget tone, neighborhood and loyalty status. It hands off to Flight, which pulls live availability and fare rules, then to Hotel, which pulls inventory, room types and cancellation terms. Each specialist reads its own system of record.
4. **Plan.** Control returns to the Concierge. It merges both legs into one itinerary in its own voice, for example: "this flight is a stretch on price but lands at a useful hour; this hotel is in Alfama but the deposit is non-refundable." If the customer pushes back on one leg, only that specialist is re-engaged and the other leg stays untouched.
5. **Implement.** On commit, Flight holds the seat and Hotel confirms the room, each via its own connector. Payment runs through the existing secure path, outside the agents. The Concierge stays on the line for follow-ups (change dates, add a transfer, switch to a refundable rate) and routes each one by handoff.
6. **Failure path.** Suppose the seat is held but the hotel confirmation fails. The system uses idempotency to prevent duplicates, retries transient failures within limits, and preserves or reverses the completed steps. If it still cannot recover, or the specialists conflict, it escalates to a human with the full handoff and tool-call history.
7. **Controls in place:** MCP (no invented inventory), skill + pre-confirmation hook (no unreturned price), agent scope (no booking without confirmation) and an audit hook on every handoff.
8. **Measure** against a simpler design. Track booking completion, end-to-end response time, failed/retried requests, handoffs per conversation, escalation rate, abandonment and cost per completed booking.
9. **Extend.** To add car hire, add an agent, expose its connector and declare the handoff edges. The Concierge only learns that a new specialist exists. It does not need domain knowledge of rental cars.

## Key Takeaways
1. Choose the orchestration pattern from the problem's shape. Use handoff for single-threaded conversations with shifting expertise, sequential for real dependencies, and concurrent for independent fan-out.
2. Ground every factual claim (price, stock, availability) in a live tool call to the system of record. Make the agent that states a fact the one connected to its source.
3. Draw explicit advice / action / transaction boundaries. Keep payment and publication outside the agentic boundary, and make every agent action reviewable and undoable.
4. Design the failure path: idempotency, bounded retries, compensation, and human escalation with the full trace.
5. Layer content controls: deterministic rules first, AI reviewers for ambiguity, humans for high-risk/regulated claims. Put a human gate on the *plan* before generation starts.
6. Encode rules once, in a skill or instruction, so a regulatory change propagates to every channel at once.
7. Judge success by long-term change cost as well as launch outcomes, and measure multi-agent overhead empirically against simpler alternatives.

## Connects To
- **ch03**: all six primitives (instructions, prompts, agents, skills, hooks, MCP) are applied here, at both build time and run time.
- **ch04**: the RPI cadence is reused as the runtime flow of each product, and the marketing plan approval is the RPI plan gate.
- **ch05**: the governance controls here (hooks, scoped agents, MCP boundaries, human approval) instantiate the five-layer model that moves agentic work from stochastic to deterministic.
- **ch07**: the evaluator agent and the contract-check hooks are inputs to continuous delivery/validation loops.
- **Microsoft Agent Framework (MAF)**: the source of the five orchestration patterns (Sequential, Concurrent, Group chat, Magentic, Handoff).
- **GitHub Copilot hooks**: the lifecycle hooks (before/after tool execution) behind `catalog-contract-check`.
- **Saga/compensation and idempotency (distributed systems)**: the failure-path design for multi-step bookings.
- **Evidence cited**: NBER WP 31161 (Brynjolfsson et al.) found +14% issues resolved per hour across 5,179 support agents using a gen-AI assistant. Michaels/Persado saw +41% SMS and +25% email click-through after AI personalization. McKinsey puts gen-AI marketing gains at 5–15% of marketing spend. Treat these as signs of potential value, not expected outcomes.
