# Chapter 2: Integration Styles

## Core Idea
There is no single right way to integrate applications; four styles — File Transfer, Shared Database, Remote Procedure Invocation, and Messaging — each trade off coupling, timeliness, data format, and reliability differently. Pick the style that fits each integration opportunity, and expect to mix styles across an enterprise.

## Frameworks Introduced
- **File Transfer**: Have each application produce files of shared data for others to consume, and consume files that others produce.
  - When to use: applications on divergent languages/platforms need to share data with minimal specialized tooling, and update latency (nightly/weekly/quarterly cycles) is acceptable.
  - How: each app writes files in a negotiated standard format (COBOL feeds, Unix text, XML); integrators handle transformation between formats. Developers manually manage naming conventions, directories, unique filenames, deletion of stale files, and read/write locking or timing. Files become the app's interface.
- **Shared Database**: Integrate applications by having them store the data they wish to share in a single common database.
  - When to use: data must be shared rapidly and consistently, and an agreed-upon data format must be enforced to force out semantic dissonance up front.
  - How: all apps read/write one SQL relational schema; transaction management keeps concurrent updates consistent. The hard part is designing a unified schema all apps accept (technically and politically).
- **Remote Procedure Invocation**: Develop each application as a large-scale object/component with encapsulated data, exposing an interface so other applications can invoke its procedures remotely.
  - When to use: integration must share functionality/processes (not just data) responsively, letting the owning app maintain data integrity behind a function-call interface.
  - How: use an RPC mechanism (CORBA, COM, .NET Remoting, Java RMI, or Web Services via SOAP/XML/HTTP). Each app negotiates its interface with neighbors; encapsulation lets internal data change without breaking others.
- **Messaging**: Have each application connect to a common messaging system and exchange data and invoke behavior using messages.
  - When to use: you need frequent, immediate, reliable exchange of small data packets — collaborating behaviorally — while keeping systems loosely coupled and resilient to partner/network outages.
  - How: send small packets over the messaging system asynchronously with retry; storage details are hidden; messages can be transformed in transit and routed/broadcast to receivers without sender or receiver knowing. Built from Message, Message Channel, Message Router, Message Translator, Message Endpoint.

## Key Concepts
- **Application coupling**: degree to which apps depend on each other's internals; good integration minimizes it so each can evolve independently.
- **Integration simplicity**: minimizing changes to applications and the amount of integration code needed.
- **Integration technology**: the specialized software/hardware a style requires, with cost, vendor lock-in, and learning burden.
- **Data format (and evolution)**: apps must agree on exchanged data formats or use an intermediate translator; formats must be able to change over time.
- **Data timeliness / latency**: the lag between one app sharing data and others receiving it; longer lag means staler, more error-prone, more complex integration.
- **Data vs. functionality**: whether apps merely share data or also invoke each other's behavior.
- **Asynchronicity**: invoking a remote action without waiting for it — the caller proceeds while the receiver acts later, tolerating downtime.
- **Semantic dissonance**: subtle differences in what data *means* across apps (e.g., "oil well" = one hole vs. a rig covering many); harder to fix than format mismatches.
- **Staleness / inconsistency**: infrequent updates let systems drift out of sync, producing conflicting data (e.g., two addresses for one customer).
- **Encapsulation**: hiding data behind a function-call interface so the owner can react to changes and protect integrity — the principle RPC applies to integration.

## Mental Models
- **Increasing order of sophistication**: the four styles share the same problem and context; each builds on the last to fix its predecessor's shortcomings, so the ordering is a progression, not a ranking of "always best."
- **Messaging as fine-grained File Transfer**: Messaging is essentially File Transfer producing a tiny file on every change, with automatic notification, retry, and hidden storage — once files get that granular, treat them as messages.
- **High cohesion, low adhesion**: thinking asynchronously forces designers to do lots of work locally and only selective work remotely, because remote calls are slow and can fail.
- **The files/messages become the interface**: apps stay decoupled as long as they keep emitting the agreed data; internals can change freely behind that contract.

## Anti-patterns
- **Treating remote calls like local calls**: RPC feels familiar to developers, but remote calls are slower and can fail; assuming local semantics yields slow, unreliable systems.
- **One universal shared schema**: forcing every app onto a single database schema creates unworkable designs, political fights, breaks with external packages, and locking/deadlock/performance bottlenecks when distributed.
- **Designing integration like a single application**: rules that don't matter within one app (sequencing, tight call chains, failure propagation) become knots across apps.
- **Infrequent file cycles when data must be fresh**: nightly extracts cause disasters when a consumer acts on stale data (billing to an old address).

## Reference Tables

| Dimension | File Transfer | Shared Database | Remote Procedure Invocation | Messaging |
|---|---|---|---|---|
| Coupling | Very loose (file is the interface) | Tight (all coupled to the schema) | Fairly tight (interfaces + sequencing) | Loose (transform/route in transit) |
| Timeliness | Poor (batch cycles) | Good (immediate, consistent) | Good (immediate) | Good (frequent, immediate) |
| Shares data or functionality? | Data only | Data only | Functionality (and data) | Data + behavior |
| Data format | Negotiated file formats + transforms | One enforced unified SQL schema | Per-interface, negotiated | Customizable per message type, transformable |
| Reliability / failure isolation | High (offline-friendly) | DB is single dependency; locks/deadlocks | Low (remote call can fail, propagates) | High (async, retry, no simultaneous uptime needed) |
| Asynchronicity | Yes (inherently decoupled in time) | No | No (typically synchronous) | Yes (fundamental) |
| Technology needed | Minimal (files, built-in) | SQL relational DB (ubiquitous) | RPC middleware / Web Services | Messaging system / EAI middleware |
| Consistency handling | Weak; drift and inconsistency | Strong; transactions | Owner maintains integrity | High frequency reduces (not eliminates) lag |
| Main downside | Staleness, manual plumbing | Schema design + politics + bottlenecks | Tight coupling, false locality | Async learning curve, harder testing, glue code |

## Worked Example
A customer changes address. With **File Transfer**, the customer-management system writes a nightly extract; the billing system may still mail today's bill to the old address — and if two systems record the change with a typo, you get two inconsistent addresses to reconcile later. **Shared Database** fixes timeliness and consistency (one row, transaction-managed) but demands every app agree on one schema and confronts semantic dissonance (is an "oil well" one hole or a rig?). **RPC** lets the address change *invoke behavior* — triggering jurisdiction-specific registration/legal processes in another app via a call — but ties the systems together and behaves badly if the remote call is slow or fails. **Messaging** sends the change as a small packet the moment it happens, asynchronously with retry: billing is notified immediately, the sender doesn't block, transforms handle differing models, and one app's outage won't bring down the others.

## Key Takeaways
1. Choose the best style per integration point, not one style always; two apps may use several styles, and EAI products hide hybrids internally.
2. The core trade-off axis is coupling vs. timeliness: File Transfer is decoupled but stale; Shared Database is timely but coupled to the schema.
3. Sharing data isn't enough when changes must trigger processes — that's when you need functionality sharing (RPC) or behavioral collaboration (Messaging).
4. RPC's biggest trap is that remote calls look local but are slower and can fail; don't let that familiarity produce fragile designs.
5. Messaging is the authors' generally-preferred style — timely, reliable, asynchronous, decoupled, transformable — but it adds an async learning curve, harder testing, and glue code.
6. Enforcing one format early (Shared Database) surfaces semantic dissonance before bad data accumulates; Messaging instead tolerates different conceptual models via translation.

## Connects To
- **Ch 3**: Messaging leads into the messaging pattern language — Message, Message Channel, Message Router, Message Translator, and Message Endpoint.
