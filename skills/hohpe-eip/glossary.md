# Glossary — Enterprise Integration Patterns

Key terms and concepts (patterns themselves are in [patterns.md](patterns.md)).

- **ACT (Asynchronous Completion Token)** — caller-supplied data returned with an async reply so an event-driven endpoint resumes the right request without blocking (Ch 9, 10).
- **Aggregation algorithm** — how an Aggregator combines messages: select best, condense/average, or collect (Ch 7).
- **Application coupling** — degree of dependency on other apps' internals; minimize so each evolves independently (Ch 1, 2).
- **BAM (Business Activity Monitoring)** — tracks business payload data; distinct from system management, which tracks counts/latency/headers (Ch 11).
- **Body** — the opaque payload of a message, transmitted as-is (Ch 3).
- **Canonical Data Model** — application-independent message format; each app needs one translator (2N, not N²) and is isolated from others' format changes (Ch 1, 8).
- **Channel** — a logical address both sender and receiver agree on without knowing each other's identity (Ch 1, 3).
- **Completeness condition** — Aggregator rule for when to publish: Wait-for-All, Time-Out, First-Best, Time-Out-with-Override, External Event (Ch 7, 9).
- **Composed messaging** — solving one integration problem by composing routing/transformation patterns into a larger flow, independent of transport (Ch 9).
- **Control channel** — an extra input for configuration/control messages (Dynamic Router registration, Aggregator purge) (Ch 7, 11).
- **Correlation Identifier** — unique token in a request echoed in the reply header to link the pair; correlate by application field, not system message ID (Ch 5, 9).
- **Coupling** — how many assumptions parties make about each other when communicating; loose coupling reduces them at the cost of complexity (Ch 1).
- **De-duping** — detecting/removing duplicate messages via unique identifiers (Ch 10).
- **Distribution vs auction** — Recipient List to a computed known set vs Pub-Sub broadcast to an unknown self-subscribing set (Ch 9).
- **Endpoint** — the explicit connection of an application into the integration solution (Ch 1, 3, 10).
- **Event-driven vs polling consumer** — callback invoked on arrival (immediate, transaction-hostile) vs thread blocking on receive (throttleable, transaction-safe) (Ch 10).
- **Guaranteed Delivery "number of 9s"** — reliability is resilient, not 100%; cost rises exponentially toward 99.99%+ (Ch 4).
- **Header** — message metadata used by the messaging system (origin, destination, reply-to, correlation) (Ch 3).
- **Heartbeat** — periodic "I am alive" message, optionally carrying vital stats (Ch 11).
- **Idempotent** — f(x) = f(f(x)); same effect whether a message is received once or many times (Ch 10).
- **Initialized / self-starting Aggregator** — pre-seeded from the request with an expected count vs creating an aggregate on first unmatched message (Ch 7, 9).
- **JMS Destination** — abstract channel handle; a Queue = Point-to-Point, a Topic = Publish-Subscribe (Ch 6).
- **JMS Session** — single-threaded producing/consuming context from a Connection; one session per independent thread (Ch 6).
- **Marshalling** — converting data to/from a byte stream to copy it across separate memory spaces (Ch 3).
- **Message intent** — sender's expectation: invoke code (Command), hand over data (Document), or note a change (Event) (Ch 5).
- **Messaging RPC / Query / Notify** — Request-Reply variants: Command+Document return value; query results; Event+acknowledgement (Ch 5).
- **Middleware** — the layers between applications: channel, message, translation, routing, management, endpoint (Ch 1).
- **Performer** — worker object a Message Dispatcher delegates a message to, in its own thread (Ch 10).
- **Pipes and Filters** — architectural style dividing a task into independent filters connected by pipes (channels) (Ch 3).
- **Predictive routing vs reactive filtering** — router pushes to known destinations vs recipients pull via Pub-Sub + Message Filters (Ch 3, 7).
- **Promotion** — lifting a field from the message body into the header so infrastructure/routers can act on it (Ch 8).
- **Process instance vs definition** — an active execution with its own id/state vs the reusable template (Ch 7).
- **Push vs pull model** — push sends full state with the event; pull sends a minimal event and observers request details (Ch 5).
- **Return Address** — caller-specified reply channel (JMSReplyTo / MSMQ ResponseQueue); why Wire Taps can't track replies (Ch 5, 11).
- **Semantic dissonance** — common syntax (XML) does not imply common meaning; different apps name the same concept differently (Ch 1, 2, 8).
- **Sequence number** — consecutive comparable ordering field the Resequencer needs; distinct from message ID and correlation ID (Ch 5, 7).
- **Service directory** — request channels acting as a lookup of available services in a Message Bus / SOA (Ch 4).
- **Slow consumer** — a consumer that can't keep up, causing expiration and back-pressure (Ch 13).
- **Stateless vs stateful router** — processes each message independently (parallelizable) vs stores state across arrivals (Aggregator, Resequencer, Process Manager) (Ch 7).
- **Store and forward** — messaging persists a message at each hop until it can forward to the next (Ch 4).
- **Synchronous Block vs Asynchronous Callback** — one blocked thread (simple, single request) vs a separate reply thread with callbacks (many requests, crash-recoverable) (Ch 5).
- **Throttling** — the application controlling the rate at which it consumes messages (Ch 10).
- **Transactional Client / XA** — client controls messaging transaction boundaries; distributed (XA) transactions coordinate messaging with a DB (Ch 10).
- **Tunneling** — encapsulating one protocol/format inside another to cross infrastructure that only supports the outer one (Ch 8).

### Emerging standards (Ch 14, as of 2003)
- **BPEL4WS** — declarative XML Process Manager for web services (merged IBM WSFL + Microsoft XLANG).
- **ebXML / ebMS** — XML successor to EDI; reliable secure messaging over SOAP-with-Attachments.
- **WS-Addressing** — transport-neutral From/To endpoint identifiers; standardizes Return Address.
- **WS-Reliability / WS-ReliableMessaging** — SOAP reliable delivery (at-most/at-least/exactly-once, in-order); implement Guaranteed Delivery + Resequencer.
- **WS-Coordination / WS-Transaction** — propagate coordination context; Atomic Transaction (AT) + Business Activity (BA).
- **WS-Security** — associate security tokens with SOAP messages (PKI, Kerberos, XML Signature/Encryption).
- **WS-I Basic Profile** — named bundle of interoperable web-service standards (XML Schema, SOAP, WSDL, UDDI).
