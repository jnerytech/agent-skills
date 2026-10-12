# Chapter 10: Messaging Endpoints

## Core Idea
A Message Endpoint is the thin layer of code where an application attaches to the messaging system to send and receive messages. Sending is easy; receiving is where the design choices live, and the overriding theme is *throttling* — letting the application control the rate at which it consumes messages while staying decoupled from any specific messaging technology.

## Frameworks Introduced
- **Messaging Gateway**: A class that wraps messaging-specific calls and exposes domain-specific methods (e.g. `GetCreditScore(SSN)`), so the rest of the app never knows messaging is involved.
  - When to use: Whenever an application integrates via messaging — every endpoint should also be a gateway.
  - How: Separate interface from implementation; catch messaging exceptions and rethrow app-specific ones. Implement blocking (synchronous, waits for reply) or event-driven (async callback/delegate, often carrying an ACT — Asynchronous Completion Token — to correlate reply with request). A fake implementation acts as a Service Stub for testing.
- **Messaging Mapper**: A separate class holding the mapping logic between domain objects and messages; neither the objects nor the infrastructure know it exists.
  - When to use: When message format differs from domain objects, or you must keep domain objects reusable outside messaging.
  - How: Access domain object(s), convert to/from the message format; invoke via events or the Observer pattern. Use reflection or code generation to cut repetitive field-copy code. Combine with a Message Translator for canonical-model conversion.
- **Transactional Client**: Make the client's session with the messaging system transactional so it can set transaction boundaries.
  - When to use: To batch several messages atomically or coordinate messaging with other resources (send-receive pairs, message groups, message/DB or message/workflow coordination).
  - How: Create a transacted session (JMS `createSession(true,...)`) or transactional queue (.NET `MessageQueueTransaction`); explicitly commit sends/receives. Cross-system coordination needs a distributed (XA/JTA) transaction. A request-sender cannot send-then-wait in one transaction (send never commits).
- **Polling Consumer**: A synchronous receiver that explicitly calls `receive()` when it is ready for a message.
  - When to use: When the application must control consumption rate (best throttling); safest partner for Transactional Client.
  - How: A thread calls a blocking `receive()`, or `receiveNoWait()`/`receive(timeout)` to poll multiple channels or do other work. Limit polling threads to limit concurrency.
- **Event-Driven Consumer**: An asynchronous receiver the messaging system invokes via callback when a message arrives.
  - When to use: When you want messages consumed as soon as available and don't want to waste resources polling an empty channel.
  - How: Register a listener/handler (JMS `MessageListener.onMessage`, .NET `ReceiveCompletedEventHandler`). Sits dormant with no thread until invoked; typically processes one message at a time. Transactions work poorly here.
- **Competing Consumers**: Multiple consumers on a single Point-to-Point Channel, each in its own thread, competing to receive messages concurrently.
  - When to use: When one consumer can't keep up and you want to scale throughput across threads/apps/machines.
  - How: The messaging system's transactional controls ensure exactly one consumer gets each message; consumers don't coordinate with each other. Each needs its own session. Only works point-to-point (pub-sub just duplicates).
- **Message Dispatcher**: A single consumer (the dispatcher) that receives messages and hands each to a performer for processing.
  - When to use: When you want to control message-to-consumer matching yourself, specialize performers by type, or avoid inconsistent multi-consumer behavior across messaging systems.
  - How: Dispatcher consumes and delegates; performers (often Event-Driven-style, e.g. Runnable/MessageListener) run in their own threads for concurrency. A messaging-specific Reactor. Should be a Polling Consumer if transactional. Performers usually all live in the dispatcher's app.
- **Selective Consumer**: A consumer that filters by a message's *selection value* so it receives only messages matching its criteria.
  - When to use: When one channel carries several message kinds and a consumer wants only some (e.g. loans ≤ $100K vs > $100K); more dynamic than separate channels.
  - How: Sender sets a selection value (ideally in the header); consumer supplies a selector expression (JMS selector string; .NET `Peek`+`ReceiveById`). Design criteria so every valid value is handled; not a security boundary.
- **Durable Subscriber**: A subscriber whose subscription survives disconnection, so the messaging system saves pub-sub messages published while it is inactive.
  - When to use: When a pub-sub subscriber must not miss messages during downtime/maintenance (e.g. a price-range database vs a throwaway GUI).
  - How: Create a durable subscription (JMS: topic + client ID + subscription name); disconnecting makes it *inactive* (still subscribed). Must explicitly `unsubscribe` to stop message accumulation; guard against unbounded buildup with Message Expiration.
- **Idempotent Receiver**: A receiver designed so receiving the same message multiple times has the same effect as receiving it once.
  - When to use: When duplicates are possible — "at least once" delivery, lost acknowledgments over HTTP/B2B, or failed distributed transactions.
  - How: (1) Explicit de-duping via a unique message identifier + a buffer/history of seen IDs; or (2) idempotent message semantics ("set balance to $110" not "add $10"). Avoid overloading a business key with dedup semantics.
- **Service Activator**: A component that connects a channel to an existing synchronous service, invoking it when a message arrives.
  - When to use: When a service must be reachable both synchronously (direct call) and asynchronously (via messaging), possibly over multiple technologies/formats.
  - How: Receive the request (Polling or Event-Driven), extract service + parameters, invoke the service like any client, optionally build a Request-Reply response. Bad messages go to the Invalid Message Channel. Serves as a Messaging Gateway to the service (e.g. J2EE session bean + message-driven beans).

## Key Concepts
- **Throttling**: The server can't control send rate but *can* control its processing rate, letting extras queue up.
- **Synchronous vs asynchronous receiver**: Polling = synchronous (thread blocks on receive); Event-Driven = asynchronous (callback thread).
- **Asynchronous Completion Token (ACT)**: Arbitrary data passed to a request and handed back on the async callback so the app can correlate reply to request.
- **Performer**: The worker object a Message Dispatcher delegates a message to; runs in its own thread for concurrency.
- **Selection value / selector**: A message value (sender-set) tested against a consumer's criteria to decide delivery.
- **Inactive subscriber**: Disconnected but still subscribed — the third state (besides subscribed/unsubscribed) enabling Durable Subscriber.
- **Idempotent**: f(x) = f(f(x)); a message with the same effect however many times it is received.
- **De-duping**: Detecting/removing duplicates by tracking already-seen unique message identifiers.

## Mental Models
- **Endpoints combine patterns; don't pick just one.** A single endpoint may be a Polling Consumer that is also a Selective Consumer, a Competing Consumer, and a Service Activator — and it should always be a Messaging Gateway.
- **Throttle by limiting consumers/threads.** Consumption capacity is a dial (number of polling threads or competing consumers), not something fixed by the channel.
- **Let the messaging system dispatch, or do it yourself.** Competing Consumers delegate matching to the broker; Message Dispatcher and Selective Consumer take that control back into your code.
- **Idempotency lets you resend fearlessly.** If receivers ignore duplicates, senders can simply resend to recover from lost acks or partial failures.

## Anti-patterns
- **Transactional Client with Event-Driven Consumer**: Consumer commits the receive before handing the message over, so the app can't roll back — and in JMS `onMessage` can't throw, so the failing message is lost.
- **Competing transactional consumers on a naive broker**: If multiple consumers grab the same message, only the first commit wins; the rest do work then roll back, hurting the very throughput you wanted.
- **Serializing a domain object into one opaque "data" field**: Router can't route on it, it's hard to test/debug/validate, and cross-language serialization breaks.
- **Overloading a business key (e.g. order number) as the dedup identifier**: Ties infrastructure semantics to a business field; breaks when legit resends (order amendments) share the key.
- **Selective Consumer as a security control**: Brokers don't authorize selector criteria — a malicious authorized consumer can widen its criteria to read others' messages. Use separate Datatype Channels.

## Reference Tables

| Concern | Option A | Option B | Trade-off |
|---|---|---|---|
| Concurrency model | **Polling Consumer** (synchronous, calls receive) | **Event-Driven Consumer** (async callback) | Polling throttles best but can waste cycles/block threads on empty channels; event-driven is efficient but processes at arrival rate and works poorly with transactions |
| Distribute load | **Competing Consumers** (broker picks) | **Message Dispatcher** (you pick) | Both process concurrently; competing = broker-decided, spreadable across apps/machines; dispatcher = you control matching + specialization, but performers usually share one app |
| Route by criteria | **Selective Consumer** (consumer filters) | **Message Dispatcher** (dispatcher routes) | Selective needs broker support and can't easily do defaults/unmatched; dispatcher builds selection into code, can send unmatched to Invalid Message Channel and implement a default case |

## Worked Example
Reconstructed consumer-scaling scenario: an app consumes order messages from a Point-to-Point Channel but falls behind — messages pile up and the broker becomes the bottleneck. Using multiple channels fails (one fills while another sits empty; senders don't know which to use). Instead, create **Competing Consumers**: several consumer objects on the *same* channel, each `Runnable` in its own JMS `Session` (a session is single-threaded, so each thread needs one). The broker's transactional controls ensure only one consumer wins each message; the rest keep pulling the next. Throughput now scales with the number of consumer threads (and can spread across machines) until the only limit is how fast the channel can feed messages. If you needed to *specialize* consumers by loan size or reroute unmatched messages, you'd instead front the channel with a **Message Dispatcher** (a Polling Consumer, for transaction safety) that hands each message to a type-specific performer thread.

## Key Takeaways
1. Wrap all messaging behind a **Messaging Gateway** so application code stays technology-agnostic — every endpoint should be one.
2. Choose **Polling** (control the rate, transaction-friendly) vs **Event-Driven** (immediate, efficient, but transaction-hostile) as your consumer model.
3. Scale throughput with **Competing Consumers** (broker-dispatched) or a **Message Dispatcher** (self-dispatched, specializable) — throttle by limiting consumer/performer count.
4. **Transactional Client** works cleanly only with a single Polling Consumer; it fights event-driven consumers, dispatchers, and competing consumers.
5. Assume duplicates: make receivers **Idempotent** via unique-ID de-duping or idempotent message semantics.
6. Use a **Durable Subscriber** so pub-sub subscribers survive disconnection, and remember to unsubscribe to stop unbounded accumulation.

## Connects To
- **Ch 3**: refines the Message Endpoint root pattern into 11 concrete send/receive and consumer strategies.
