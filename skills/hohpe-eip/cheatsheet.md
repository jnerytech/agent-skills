# Cheatsheet — Enterprise Integration Patterns

Decision rules and tells. For a pattern's full context, open its chapter. For definitions, see [glossary.md](glossary.md).

## Pick an integration style (ch02)
| Need | Style | Because |
|---|---|---|
| Bulk data, batch latency OK, divergent platforms | **File Transfer** | no tooling, apps stay decoupled |
| Real-time consistency, enforced format | **Shared Database** | transactions + one schema kill inconsistency early |
| Trigger *behavior* in another app, tight OK | **RPC** | sharing raw data can't invoke a process |
| Frequent, reliable, async, decoupled | **Messaging** | timely + failure-isolated + loosely coupled |

## Message intent → type → channel (ch05)
- Invoke behavior → **Command Message**; hand over data → **Document Message**; announce a change → **Event Message**.
- Commands/Documents go **Point-to-Point** (once, no dup); Events go **Publish-Subscribe** (broadcast).
- Two-way = two one-way messages: **Return Address** says *where*, **Correlation Identifier** says *which*. Keep both in the header. Correlate by an application field, not the system message ID.

## Channel choices (ch03, ch04)
- One receiver → **Point-to-Point**; all receivers → **Publish-Subscribe**.
- **Invalid** = receiver got it but can't process it (*receiver* moves it). **Dead Letter** = system can't deliver it (*system* moves it). Never route application errors to Invalid.
- One data type per channel (**Datatype Channel**). Apply **Guaranteed Delivery** selectively — durability vs performance/disk; disable for testing.
- Router changes **destination** (content untouched); Translator changes **format** (routing untouched). Never let one pattern do both.
- Admin tools *create* channels; app code only *accesses* them.

## Routing (ch07)
- **Stateless** (Content-Based Router, Filter, Recipient List, Splitter) → parallelize freely. **Stateful** (Aggregator, Resequencer, Process Manager) → need correlation + state cleanup.
- Compositions: **Composed Message Processor** = Splitter + Aggregator. **Scatter-Gather** = (Recipient List *or* Pub-Sub) + Aggregator.
- Sequential flow: **Routing Slip** if linear + steps known up front; **Process Manager** if branching/forks/joins or re-routing on intermediate results.
- **Aggregator completeness**: Wait-for-All · Time-Out · First-Best · Time-Out-with-Override · External Event. Pick by addressing: count-based when recipients known (distribution), timeout-based when unknown (auction/Pub-Sub).
- N apps interconnecting → per-pair channels explode (N²) → **Message Broker** hub-and-spoke + **Canonical Data Model**.

## Transformation (ch08)
- Receiver needs MORE data → **Content Enricher**. Want LESS, permanently → **Content Filter**. Want less now, restore later → **Claim Check**.
- Reach for **Canonical Data Model** once several apps integrate (6 apps: 30 direct translators vs 12 canonical). Skip only when throughput forbids double-translation latency.
- **Normalizer** = Message Router + one Translator per format. Never modify a source app to satisfy a downstream consumer — insert a transformer.

## Endpoints (ch10)
- Every endpoint should be a **Messaging Gateway**; real endpoints combine several patterns, don't pick just one.
- **Polling** = best throttling + transaction-safe. **Event-Driven** = immediate + efficient but transaction-hostile.
- **Competing Consumers** (broker dispatches) vs **Message Dispatcher** (you dispatch, can specialize). Throttle by limiting consumer/performer count.
- Assume duplicates → **Idempotent Receiver** (unique-ID de-dup or idempotent semantics). **Transactional Client** pairs cleanly only with a single Polling Consumer.

## Debugging & managing a live flow (ch11)
- Read **Message History** in the header for the path; check the **Message Store** for cross-message throughput; drain stale channels with a **Channel Purger** before re-testing.
- **Observability** = copy/tag without disturbing flow (Wire Tap, Message Store, Message History). **Control** = command/reroute/remove (Control Bus, Detour, Channel Purger).
- Liveness ≠ correctness: heartbeats say *alive*, **Test Messages** say *correct*. For request-reply, insert a **Smart Proxy** and never correlate copies by message ID.
- Route all system-management traffic on a separate **Control Bus**, never mixed with application data.

## Async vs sync composition (ch09)
- **Sync** for simplicity (no threads/correlation, per-recipient reply channels) when latency + connection count are acceptable.
- **Async** for speed/scale — but then you MUST add Correlation Identifiers, out-of-order handling, and event-driven state.

## Tells & smells
- "Alive but wrong output" → you lack a **Test Message** loop.
- Silent message disappearance → a **Message Filter** or unmonitored **Invalid Message Channel**.
- Common XML ≠ common meaning → **semantic dissonance**; a Canonical Data Model models meaning, not just syntax.
- Über-broker / broker spaghetti → scale the Message Broker via stateless replicas or a hierarchy.
- **The pattern outlasts the standard** — cull idioms from standards; ignore immature ones until they mature.
