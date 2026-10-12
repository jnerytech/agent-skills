# Patterns — Enterprise Integration Patterns (all 65 + 4 styles)

Format: **Pattern** (chN) — *When* → *How* → *Trade-off*. Grouped by family. This is the lookup index; open the chapter file for full treatment.

## Integration Styles (ch02)
- **File Transfer** (ch02) — apps on divergent platforms, batch latency OK → each app reads/writes files in a negotiated format → very loose coupling but stale data + manual plumbing.
- **Shared Database** (ch02) — data must be consistent, format enforced, real-time → all apps share one SQL schema under transactions → strong consistency but tight schema coupling, locking bottlenecks, politics.
- **Remote Procedure Invocation** (ch02) — must share behavior/process, not just data → expose apps as components called via CORBA/RMI/.NET/Web Services → shares functionality but stays coupled; remote calls slow and fail.
- **Messaging** (ch02) — frequent, immediate, reliable, async exchange while decoupled → connect apps to a messaging system; small async packets with retry → timely+reliable+decoupled but async learning curve, harder test/debug.

## Messaging Systems — root patterns (ch03)
- **Message Channel** (ch03) — two apps must communicate; each data type needs a conduit → create a type-specific logical channel at deploy time; code only accesses it → channels cheap not free (plan/fix at deploy).
- **Message** (ch03) — move a discrete data unit between processes → header+body, marshal→send→unmarshal → data copied not shared; large/chatty payloads cost marshalling.
- **Pipes and Filters** (ch03) — one event triggers reusable/testable/distributable steps → chain single-responsibility filters via channels; async gives pipelining → more channels = buffering cost + repeated format conversion.
- **Message Router** (ch03) — messages take different paths without sender knowing topology → filter consumes then republishes *unchanged* to a chosen channel → router must know all destinations (maintenance bottleneck).
- **Message Translator** (ch03) — apps use different formats, must stay decoupled → Adapter-style filter converts across transport/representation/type/structure layers → chaining multiplies overhead; complex maps hard to debug.
- **Message Endpoint** (ch03) — app can't natively talk to messaging → client code bridges app domain ↔ messaging API → one instance sends OR receives, channel-specific; product switch = rewrite.

## Messaging Channels (ch04)
- **Point-to-Point Channel** (ch04) — message must be processed exactly once → one of many receivers consumes each message → no broadcast; extra consumers become Competing Consumers.
- **Publish-Subscribe Channel** (ch04) — broadcast an event to all interested → fan out one copy per subscriber → enables eavesdropping/debug but copies = privacy risk; WAN-inefficient.
- **Datatype Channel** (ch04) — receiver must know how to process each type → one channel per message type → type proliferation (mitigate: Selective Consumer / Dispatcher).
- **Invalid Message Channel** (ch04) — a delivered message can't be parsed/validated → *receiver* reroutes it to a dedicated channel a monitor inspects → validity is receiver-defined; must be monitored; not for app errors.
- **Dead Letter Channel** (ch04) — the *system* can't deliver (bad channel, expiry, timeout) → system auto-moves it, recording where/why → vendor-fixed behavior, no custom handling.
- **Guaranteed Delivery** (ch04) — message loss on crash unacceptable → persist to disk at each hop before send completes → costs perf+disk; never truly 100% ("number of 9s").
- **Channel Adapter** (ch04) — connect a non-messaging/legacy app unchanged → adapter is a messaging client invoking app via UI/API/DB layer → UI brittle, DB risky, often one-way, QoS lost.
- **Messaging Bridge** (ch04) — two messaging systems must share messages → set of Channel Adapters mapping/transforming channel pairs → common API (JMS) ≠ interoperability; often build-your-own.
- **Message Bus** (ch04) — many apps coordinate behind unified GUIs → common data model + command set + messaging infra (Pub-Sub/Router) → all apps must adopt canonical model; lightweight SOA.

## Message Construction (ch05)
- **Command Message** (ch05) — invoke a procedure in another app async/reliably → wrap method+params, send Point-to-Point → runs once but couples sender to receiver's API.
- **Document Message** (ch05) — transfer data without dictating handling → single data unit/XML, Point-to-Point → decoupled but broadcasting creates divergent copies.
- **Event Message** (ch05) — async event notification (Observer over messaging) → wrap event, broadcast Pub-Sub → timely+decoupled but delivery not guaranteed; push vs pull.
- **Request-Reply** (ch05) — get a response over one-way messaging → two messages on separate channels; Synchronous Block or Async Callback → adds channels + blocking/callback complexity.
- **Return Address** (ch05) — tell replier where to reply → put reply channel in request header (JMSReplyTo/ResponseQueue) → flexible but needs header convention.
- **Correlation Identifier** (ch05) — match a reply to its request → request carries unique ID, replier echoes it as correlation ID → enables many outstanding requests; needs ID agreement.
- **Message Sequence** (ch05) — transmit data past size limits → split into chunks marked sequence id + position + size/end → reassembles out-of-order; incompatible with Competing Consumers.
- **Message Expiration** (ch05) — ignore stale time-sensitive messages → set relative TTL; expired discarded or → Dead Letter → avoids stale action but expiring replies leaves requestor uncertain.
- **Format Indicator** (ch05) — let message format evolve → include version number / schema key / embedded schema → old+new coexist but needs shared meaning of the indicator.

## Message Routing (ch07)
- **Content-Based Router** (ch07) — one function spread across systems, exactly-once + central control → stateless router inspects content, forwards to one channel (unmatched→Invalid) → must know all recipients.
- **Message Filter** (ch07) — recipient rejects uninteresting messages itself → evaluate criteria, forward or drop → distributes routing logic, honor-system, often less efficient than a router.
- **Dynamic Router** (ch07) — predictive efficiency without hard-coded destinations (SOA discovery) → recipients announce rules on a control channel; router stores + routes → complexity, rule conflicts.
- **Recipient List** (ch07) — send one message to a controlled subset → compute list, send a copy to each; make atomic/restartable → predictive coupling; prevent bypass.
- **Splitter** (ch07) — composite message with items needing individual processing → publish one child per element, copy common fields + correlation/sequence → children lose context; plan re-aggregation.
- **Aggregator** (ch07) — recombine Splitter output / reconcile responses → stateful: correlate, buffer, apply completeness condition + aggregation algorithm → handle latecomers/missing; purge closed aggregates.
- **Resequencer** (ch07) — parallel processing reordered a stream, downstream needs order → buffer out-of-order by sequence number, emit consecutive runs → buffer-overrun risk; throttle/sliding-window.
- **Composed Message Processor** (ch07) — process a composite whose parts differ, then reassemble → Splitter + Router + Aggregator, concurrent → synchronization waits on slowest part.
- **Scatter-Gather** (ch07) — solicit competing replies, pick best → broadcast via Recipient List or Pub-Sub (+Return Address) then Aggregator → may not know responder count; slowest blocks.
- **Routing Slip** (ch07) — linear, per-message, steps known up-front → attach ordered step list; generic router on each component advances it → path fixed at start; can't branch on results.
- **Process Manager** (ch07) — steps non-linear / not known at design-time (branch/fork/join) → central hub, per-trigger instance holds state, correlates, dispatches next → central bottleneck; overkill for simple routing.
- **Message Broker** (ch07) — many apps, per-pair channels explode (N²) → hub-and-spoke built from routing patterns + Canonical Data Model → single-point bottleneck; risk of über-broker.

## Message Transformation (ch08)
- **Envelope Wrapper** (ch08) — systems need header/security/encryption they don't understand, or cross infrastructures → wrap payload in a compliant envelope, unwrap at destination; promote key fields → overhead; hides fields from routers unless promoted.
- **Content Enricher** (ch08) — target needs fields the source lacks (only an ID present) → use key fields to fetch from computation/env/another system, append → tightly coupled to its data source; lookup per message.
- **Content Filter** (ch08) — need only a few items, or must strip sensitive data, or flatten → delete unwanted elements, optionally flatten → removed data is gone (use Claim Check to restore).
- **Claim Check** (ch08) — reduce data volume / hide sensitive data → store data by key, pass the key, retrieve later via Content Enricher → needs shared persistent store + cleanup strategy.
- **Normalizer** (ch08) — receive semantically-equal messages in many formats → Router detects type → per-format Translator → type detection fragile without a specifier.
- **Canonical Data Model** (ch08) — many apps, pairwise translators unmaintainable → app-independent common model; each app translates to/from it (2N not N²) → double-translation latency; hard to design one model for all.

## Messaging Endpoints (ch10)
- **Messaging Gateway** (ch10) — hide messaging behind domain methods → class exposing e.g. GetCreditScore; blocking or event-driven (ACT); rethrow app exceptions → extra layer, but decouples app from messaging tech.
- **Messaging Mapper** (ch10) — move data between domain objects and messages, both independent → separate mapper class, reflection/codegen → extra class, but domain objects stay messaging-ignorant.
- **Transactional Client** (ch10) — client controls transaction boundaries → transacted session with explicit commit; XA for DB coordination → atomic, but works well only with a single Polling Consumer.
- **Polling Consumer** (ch10) — consume when the app is ready → thread calls blocking receive()/receiveNoWait() → best throttling, but wastes cycles polling empty channels.
- **Event-Driven Consumer** (ch10) — consume automatically on arrival → register listener (JMS onMessage / .NET handler) → immediate+efficient, but processes at arrival rate; transaction-hostile.
- **Competing Consumers** (ch10) — process multiple messages concurrently → many consumers on one Point-to-Point Channel, broker gives each message to one → scales throughput; transactional rollbacks waste work.
- **Message Dispatcher** (ch10) — coordinate multiple consumers on one channel → single dispatcher consumes and delegates to performers in own threads → you control matching/specialization; transactions hard.
- **Selective Consumer** (ch10) — choose which messages to receive → sender sets selection value; consumer supplies selector expression → dynamic, channel-conserving; not a security boundary.
- **Durable Subscriber** (ch10) — don't miss pub-sub messages while disconnected → durable subscription (topic+clientID+subName) saves messages while inactive → risk of unbounded accumulation if never unsubscribed.
- **Idempotent Receiver** (ch10) — safely handle duplicate messages → de-dup via unique message-ID buffer, or idempotent semantics ("set" not "add") → enables fearless resend; de-dup adds state.
- **Service Activator** (ch10) — expose one service to sync AND async callers → component receives message, invokes service like any client, optional reply → single service reused; each transport needs a new activator.

## System Management (ch11)
- **Control Bus** (ch11) — administer a distributed solution at runtime → separate management channels link every component to a central console (config/heartbeat/stats) → adds a second messaging subsystem per component.
- **Detour** (ch11) — toggle validation/logging/debug on for test → context-based router with two outputs, flipped via Control Bus → extra hop latency; can modify messages.
- **Wire Tap** (ch11) — inspect all messages without consuming → fixed Recipient List republishes each message to main + tap channel → added latency, new IDs; cannot alter (use Detour).
- **Message History** (ch11) — debug paths/dependencies, break pub-sub loops → each component appends its ID to a header list → transient (gone once consumed); not cross-message.
- **Message Store** (ch11) — report throughput/runtime persistently → fire-and-forget a duplicate (via component or Wire Tap) to a central DB → extra traffic/storage; per-type schema burden; needs purging.
- **Smart Proxy** (ch11) — track request-reply services with variable Return Addresses → store original Return Address + Correlation ID keyed by request ID; swap in proxy's own; restore on reply → per-request state; may abuse Correlation Identifier.
- **Test Message** (ch11) — detect components alive but garbling output → Generator→Injector(tag)→component→Separator→Verifier → active load cost; unsafe for stateful components.
- **Channel Purger** (ch11) — clear leftover test replies / evict poison messages → drain via receiveNoWait until empty, or filter by ID → destructive; careful not to delete pending messages.
