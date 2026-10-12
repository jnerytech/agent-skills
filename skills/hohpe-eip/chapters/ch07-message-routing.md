# Chapter 7: Message Routing

## Core Idea
Message Router variants decouple a message's source from its ultimate destination by making routing a separate, composable concern. Simple routers refine the base Message Router (one inbound → one or more outbound); composed routers chain simple ones for parallel or sequential flows; the Message Broker generalizes them into a hub-and-spoke architecture.

## Frameworks Introduced
- **Content-Based Router**: Route each message to the correct single recipient based on inspecting its content (fields, values).
  - When to use: one logical function is spread across multiple physical systems (e.g. widget vs. gadget inventory); you need exactly-one delivery and central control.
  - How: a stateless router examines content and forwards to one output channel; unmatched → Invalid Message Channel ("dunno" queue). Predictive routing — knows all recipients' capabilities. Can be a configurable rules engine.
- **Message Filter**: A special Content-Based Router with a single output channel; passes the message only if content matches criteria, else discards it (routes to a "null channel").
  - When to use: recipients should reject uninteresting messages themselves; used with Publish-Subscribe Channel for reactive, distributed filtering when channel-topic granularity is too coarse.
  - How: evaluate criteria on each message; forward or drop. Usually stateless, but can be stateful (e.g. deduplication by stored message IDs). Differs from a Selective Consumer (which is inside the endpoint and leaves non-matching messages on the channel).
- **Dynamic Router**: A Router that self-configures from control messages sent by recipients.
  - When to use: you want predictive-routing efficiency without the maintenance dependency of hard-coded destinations; service discovery in SOA.
  - How: adds a **control channel**; recipients announce capabilities/rules at startup (or subscribe/unsubscribe at runtime); router stores rules in a persistent rule base and routes accordingly. Must resolve rule conflicts (ignore-conflicts / first-match / all-match).
- **Recipient List**: A Content-Based Router that forwards a single message to a computed list of multiple recipients.
  - When to use: send to a controlled subset (request-for-quote to select suppliers, credit check to multiple agencies) where you must not trust others to ignore.
  - How: two logical parts — compute recipient list (from rules or attached to the message), then send a copy to each. Must be atomic/restartable (single transaction, persistent sent-list, or idempotent receivers). A **Dynamic Recipient List** lets recipients register preferences via a control channel.
- **Splitter**: Break a composite message into a series of individual messages, one per element.
  - When to use: message contains a list (order → order items) whose elements need individual routing/processing.
  - How: consume one message, publish one per element (or subset). Copy common fields (order number, customer ID) into each child to make it self-contained and later re-aggregatable; add a Correlation Identifier / sequence number. **Iterating Splitter** walks tree children generically; **Static Splitter** breaks a fixed mega-message into fixed sub-messages.
- **Aggregator**: A stateful filter that collects related messages until a set is complete, then publishes one distilled message.
  - When to use: recombine Splitter output or reconcile multiple responses (pick best bid, sum values).
  - How: define **Correlation** (which belong together), **Completeness Condition** (when to publish), **Aggregation Algorithm** (how to combine). Maintains active aggregates keyed by correlation ID; closes and (optionally) tracks closed aggregates to reject/ignore latecomers.
- **Resequencer**: A stateful filter that buffers out-of-order messages and republishes them in the correct order.
  - When to use: parallel/competing processing reorders a stream, but downstream needs in-sequence delivery (ledgers, referential integrity).
  - How: each message carries a unique **Sequence Number** (distinct from Message ID / Correlation ID); buffer higher numbers until gaps fill, then emit the consecutive run. Output channel must be order-preserving. Consumes and publishes the *same* number of messages. Avoid buffer overrun via active-acknowledgement throttling (sliding window, like TCP).
- **Composed Message Processor**: Splitter + Content-Based Router + Aggregator inside one filter.
  - When to use: process a composite message whose parts need different processing, then reassemble (order items → per-item inventory check → single validated order).
  - How: split, route sub-messages to appropriate destinations concurrently, aggregate responses. Maintains control over the set of destinations; appears externally as a single filter (one in, one out).
- **Scatter-Gather**: Broadcast a request to multiple recipients and re-aggregate their replies into one message.
  - When to use: solicit competing responses (request quotes from many suppliers/banks) and pick the best.
  - How: distribute via **Recipient List** (controlled recipients) or via **Publish-Subscribe Channel** (auction-style, open participation, add a Return Address); an Aggregator combines replies. May not know how many responders to expect, complicating completeness.
- **Routing Slip**: Attach a list of processing steps to the message; each component's wrapper router reads the slip and forwards to the next step.
  - When to use: route through a *sequence* of steps that varies per message and is known up-front and linear (per-partner transformation chains, sequential validations, composed SOA service).
  - How: an initial component computes the ordered step list and attaches it; a generic (unchanging) router on each component advances the slip. Central control + hard-wired efficiency, but path is fixed at start and process state travels in the message.
- **Process Manager**: A central component that maintains process state and decides the next step based on intermediate results.
  - When to use: steps aren't known at design-time, aren't linear, need branching, forks/joins, or re-routing on intermediate results.
  - How: hub-and-spoke — a **trigger message** creates a **process instance** (with process identifier, current step, stored data); each unit returns to the hub, which correlates replies (via Correlation Identifier) and dispatches the next step(s). Process **definition** (template) vs. **instance**. Acts as Claim Check for intermediate data. Fork ≈ Pub-Sub, join ≈ Aggregator, branch ≈ Content-Based Router. Defined via BPEL4WS/XLANG/WSFL.
- **Message Broker**: An architectural hub-and-spoke pattern that receives from many sources, determines destinations, and routes — avoiding point-to-point "integration spaghetti."
  - When to use: many applications interconnect and per-pair channels would explode (N-square); you want central control of message flow.
  - How: not monolithic — implemented internally from the routing patterns of this chapter. Often uses a Canonical Data Model to avoid N-square translation. Scale via stateless replicas or a broker hierarchy to avoid the "über-broker."

## Key Concepts
- **Stateless router**: processes each message independently; returns to prior state after each message; can be parallelized (Content-Based Router, Filter, Recipient List, Splitter).
- **Stateful router**: stores messages/state across arrivals (Aggregator, Resequencer, Process Manager).
- **Predictive routing**: router knows all recipients and sends directly — efficient, central control, but coupled to the recipient list.
- **Reactive filtering**: broadcast + let recipients filter — distributed control, easy to add/remove participants, but honor-system and often less efficient.
- **Correlation**: determining which incoming messages belong together, via message type or an explicit Correlation Identifier.
- **Completeness Condition**: an Aggregator's rule for when to publish (Wait-for-All, Time-Out, First-Best, Time-Out-with-Override, External Event).
- **Aggregation Algorithm**: how messages combine — select best, condense/average, or collect for later evaluation.
- **Self-starting vs. Initialized Aggregator**: self-starting creates an aggregate on first unmatched message; initialized is pre-seeded with the original request (e.g. expected count) for a better completeness strategy.
- **Sequence Number**: a consecutive, comparable ordering field the Resequencer needs — distinct from Message Identifier and Correlation Identifier.
- **Control channel**: extra input on which recipients (Dynamic Router / Dynamic Recipient List) or operators (Aggregator purge) send configuration/control messages.

## Mental Models
- Content-Based Router (predictive, central) and a Pub-Sub + Message Filter array (reactive, distributed) solve the same problem from opposite ends — choose by who owns/maintains the routing decision and by network efficiency.
- Composition: Composed Message Processor = Splitter + Aggregator; Scatter-Gather = Recipient-List/Pub-Sub + Aggregator. Complex flows are built by chaining simple filters, and the composite still looks like a single filter.
- Sequential-routing spectrum: distributed Pipes-and-Filters ↔ Routing Slip (central compute, linear, message-carried state) ↔ Process Manager (central hub, stateful, branching/parallel). Move right for flexibility/reporting, left for run-time efficiency.
- Message-based middleware recapitulates IP networking: Dynamic Router ≈ RIP routing tables; Resequencer ≈ TCP sliding-window in-order delivery; idempotent receivers ≈ TCP safe retransmission.

## Anti-patterns
- **Broadcast-and-let-each-system-decide for transactions**: risks zero or duplicate processing and turns non-matching orders into false errors — use a Content-Based Router for exactly-one delivery.
- **Channel-per-item / channel-per-parameter-combo**: explodes channel count and management overhead — filter on content instead.
- **Chain-of-Responsibility across systems**: passing a message system-to-system needs mutual knowledge and adds hop overhead, infeasible across partners.
- **Blending business logic with routing logic in each filter** (Routing Slip Option A/B): hurts reuse and forces edits everywhere on change; keep routing generic and central.
- **Process Manager for everything**: versatile but overkill for simple routing — adds a central bottleneck and obscures the core design.
- **Über-broker / broker spaghetti**: one giant broker becomes unmaintainable; a fragmented mess loses central control — prefer a broker hierarchy.
- **Overloading Sequence Number onto Message/Correlation IDs**: they're random/non-consecutive; use a dedicated header field.

## Reference Tables

| Pattern | Consumed | Published | Stateful? |
|---|---|---|---|
| Content-Based Router | 1 | 1 | No (mostly) |
| Message Filter | 1 | 0 or 1 | No (mostly) |
| Recipient List | 1 | multiple (incl. 0) | No |
| Splitter | 1 | multiple | No |
| Aggregator | multiple | 1 | Yes |
| Resequencer | multiple | multiple (same count) | Yes |

| Composition | Equals |
|---|---|
| Composed Message Processor | Splitter + (Router) + Aggregator, controlled recipients |
| Scatter-Gather | Recipient List **or** Pub-Sub Channel + Aggregator |

| Sequential routing | Flow | Change flow | Central point | Runtime |
|---|---|---|---|---|
| Distributed Pipes & Filters | complex | hard | none | efficient/distributed |
| Routing Slip | linear only | easy | admin (not reporting) | mostly distributed |
| Process Manager | complex | easy | admin + reporting | hub-and-spoke (bottleneck risk) |

## Worked Example
Widget/gadget order processing, combining Scatter-Gather with a Composed Message Processor:
1. A **Splitter** takes an incoming order and emits one message per line item, copying order number and customer ID into each (self-contained, correlatable).
2. For each item, a **Scatter-Gather** broadcasts a request-for-quote to multiple suppliers (via Recipient List or Pub-Sub with a Return Address).
3. The Scatter-Gather's **Aggregator** collects supplier bids and picks the best — with real logic (e.g. lowest-price supplier has 60 of 100 widgets, so fill remaining 40 elsewhere).
4. A second **Aggregator** (the Composed Message Processor's) concatenates all per-item bid responses into one complete quote, ensuring every item response is present and handling missing-item errors.
Externally this whole assembly looks like one filter: order in, quote out. The JMS Aggregator example correlates bids by an `AuctionID` property, uses completeness "at least 3 bids," and selects the lowest price — with aggregation strategy isolated in a JMS-independent `Auction` class.

## Key Takeaways
1. Most routing patterns are refinements of the base Message Router; the power comes from composing simple stateless filters into larger flows.
2. The recurring design axis is predictive/central (Content-Based Router, Recipient List) vs. reactive/distributed (Pub-Sub + Message Filter) — decided by control ownership and network topology.
3. Splitter and Aggregator are duals; pair them (Composed Message Processor) or pair Aggregator with broadcast (Scatter-Gather) to fan out and reconcile.
4. Stateful routers (Aggregator, Resequencer, Process Manager) need explicit correlation, completeness/ordering logic, and state cleanup to avoid unbounded growth.
5. For sequential multi-step routing, choose Routing Slip when the path is linear and known up-front; upgrade to a Process Manager only when you need branching, forks/joins, or re-routing on intermediate results.
6. The Message Broker is an *architecture* (hub-and-spoke) assembled from these patterns; keep it scalable (stateless replicas, hierarchy) and use a Canonical Data Model to dodge N-square translation.

## Connects To
- **Ch 3**: refines the Message Router root pattern; uses Point-to-Point vs. Publish-Subscribe Channel and Invalid Message Channel.
- **Ch 8**: Message Broker relies on transformation (Canonical Data Model, Message Translator) to decouple formats.
- **Ch 10**: Correlation Identifier, Message Sequence, Return Address underpin Aggregator, Resequencer, Scatter-Gather.
