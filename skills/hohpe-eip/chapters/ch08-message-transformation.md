# Chapter 8: Message Transformation

## Core Idea
Integrated applications rarely agree on a common data format, so the integration solution must reconcile the differences without modifying the applications. These six patterns are specialized variants of the Message Translator, each handling a distinct transformation task: wrapping, adding, removing, stashing, unifying formats, and standardizing the whole model.

## Frameworks Introduced
- **Envelope Wrapper**: Wrap application data inside an envelope compliant with the messaging infrastructure; unwrap it at the destination.
  - When to use: Existing systems must join a messaging exchange that imposes header fields, security credentials, or encryption they know nothing about; or a message crosses multiple messaging infrastructures via a Messaging Bridge.
  - How: Source publishes raw message → Wrapper adds header/credentials/encryption to make it compliant → Messaging System processes it → Unwrapper reverses the changes → Recipient gets "clear text." Wrappers can chain hierarchically (payload contains another envelope, like SOAP/TCP-IP/postal mail — "tunneling"). Elevate ("promote") key fields from body into the new header so routers can still see them.
- **Content Enricher**: A specialized transformer that accesses an external data source to augment a message with missing information.
  - When to use: The target system requires data fields the originating system cannot supply (e.g., message carries only a customer ID or ZIP, receiver needs full name, SSN, insurance carrier, or state code).
  - How: Use key fields in the incoming message to fetch data, then append it. Sources: **Computation** (derive it, no external source), **Environment** (e.g., timestamp from OS), **Another System** (DB, file, LDAP, user — the most common). Interaction with the source is inherently synchronous and tightly coupled, so use a synchronous protocol (HTTP, ODBC) for performance rather than asynchronous messaging.
- **Content Filter**: Remove unimportant data items from a message, leaving only the important ones.
  - When to use: You need only a few items from a large message; to strip data a requestor is not authorized to see (security); or to simplify/flatten deeply nested structures (e.g., from a database adapter or large B2B standard like RosettaNet/ebXML).
  - How: Delete unwanted elements and optionally flatten hierarchy into a simple list. Multiple filters can act as a Filtering Splitter. Pairs naturally with Content Enricher when talking to external parties (enrich outbound, filter inbound).
- **Claim Check**: Store message data in a persistent store and pass a claim check (a key) to subsequent components, which use it to retrieve the data later.
  - When to use: Reduce data volume across a system without losing information — large payloads, hard message-size limits, XML bloat, or data needed only at the final destination (not intermediate steps). Also to hide sensitive data from outside parties.
  - How: "Check Luggage" component generates a unique key → stores the extracted data keyed by it → removes data from message and inserts the claim check → later a Content Enricher retrieves data by the key. Key choice: business key, message ID (discouraged — dual semantics, changes per message), or a generated unique ID. Data cleanup via delete-on-read, expiration + garbage collection, or keep forever. A Process Manager can serve as the store.
- **Normalizer**: Route each message type through a custom Message Translator so all resulting messages match a common format.
  - When to use: You receive semantically equivalent messages in many different formats (classic B2B aggregator — e.g., 1700 affiliates sending EDI, CSV, XML, Excel), with a high rate of format change.
  - How: A Message Router detects the incoming type and dispatches to the matching translator. Type detection: header type-specifier field, XML root element name, XPath on sub-nodes, CSV field count/types, or file name/folder as a surrogate Datatype Channel. One router lets one translator serve multiple partners sharing a format.
- **Canonical Data Model**: Design a data model independent of any application; require every application to produce and consume messages in this common format.
  - When to use: Many applications with different data formats must integrate, and you want to minimize the maintenance nightmare of pairwise translators — or an app is likely to be replaced later.
  - How: Add a level of indirection so each app translates only to/from the canonical model, not to every peer. Conform via: changing the app's format (unlikely), an internal Messaging Mapper (custom apps), or an external Message Translator (packaged apps). Costs "double translation" (two hops, added latency) vs. "direct translation." Model only the portion that participates in messaging, and specify a Format Indicator since the canonical format will evolve.

## Key Concepts
- **Data vs. metadata**: An integration solution is two parallel systems — one moving message data, one managing metadata (data describing the data, e.g., XSD schemas in a repository).
- **Promotion**: Lifting a field from a message body into the header so infrastructure components (routers) can act on it.
- **Tunneling**: Encapsulating one protocol/format inside another to traverse infrastructure that only supports the outer one.
- **Double translation vs. direct translation**: Two translation hops through a canonical model, vs. one hop directly between two app formats.
- **Semantic dissonance**: Different applications naming the same concept differently ("account," "payer," "contact" all meaning customer).
- **Filtering Splitter**: Multiple Content Filters used to split one complex message into aspect-specific messages.
- **Datatype Channel**: A dedicated channel per message type; the Normalizer avoids needing one physical channel per format.
- **Message-only modeling**: A Canonical Data Model need only cover the fields that flow through messages, not each app's full data model.

## Mental Models
- **Data lives at multiple levels of decoupling**: transport (Message Channel), location (Message Router), data representation (common XML), and data format/semantics (Canonical Data Model) — each pattern removes one layer of dependency.
- **The envelope metaphor**: the header is writing on the outside (infrastructure reads it to route/track), the body is the sealed contents (infrastructure ignores it until arrival).
- **The luggage-check metaphor**: check heavy data at the counter, carry only the claim ticket, reclaim it at the destination.
- **Enrich / filter / stash are three directions on the same axis**: add data, drop data, or temporarily set data aside and restore it.

## Anti-patterns
- **Point-to-point translator explosion**: one Message Translator per communicating pair grows roughly with the square of the app count (6 apps → 30 translators; every format change ripples to all peers) → **Canonical Data Model** (6 apps → 12).
- **Reusing the message ID as a Claim Check key**: attaches dual semantics to one element; a new message needs a new ID and then cannot retrieve the stored data → assign a dedicated key element.
- **Injecting required data by modifying the source app** (Enricher Option A/B): couples the sender to downstream consumers and turns an Event Message into a command → use a Content Enricher instead.
- **Making the sender fetch missing data itself** (Option B): ties it to both the target and the data source → decouple with an Enricher between them.
- **One Datatype Channel per format**: a large number of formats means an equally large number of channels → add a Message Router (the Normalizer).

## Reference Tables

| Pattern | Effect on data | Needs external source? | Key mechanism |
|---|---|---|---|
| Content Enricher | Adds / augments fields | Yes (or computes/environment) | Look up by key, append |
| Content Filter | Removes / flattens fields | No | Delete unwanted elements |
| Claim Check | Stores now, retrieves later | Yes (persistent store) | Extract → store by key → pass key |

| Level of decoupling | Pattern that removes it |
|---|---|
| Transport protocol | Message Channel |
| Location of receiver | Message Router |
| Application-specific data types | Common representation (XML) |
| Data format & semantics | Canonical Data Model |

## Worked Example
A hospital **scheduling system** publishes a "Doctor Visit" event containing only the patient's first name, patient ID, and visit date. The **accounting system** needs the full name, insurance carrier, and SSN to bill the insurer — but that data lives in a **customer care system**. Options A–D all fail by coupling systems together or requiring changes to packaged apps: modifying the scheduling system (A) ties it to consumers' needs; having it request the data first (B) turns an event into a command and couples it to both other systems; routing through customer care first (C) buries billing logic there; modifying accounting (D) couples it to customer care. The solution: insert a **Content Enricher** between the scheduling and accounting systems that uses the patient ID to fetch SSN and carrier from customer care, then appends them. The scheduling system just publishes a plain event; accounting stays independent of customer care. This pairs cleanly with a **Content Filter** for outbound external messages and a **Claim Check** to stash data the message shouldn't carry along the way.

## Key Takeaways
1. Each pattern is a specialized Message Translator: wrap (Envelope), add (Enricher), remove (Filter), stash-and-restore (Claim Check), unify-formats (Normalizer), standardize-the-model (Canonical Data Model).
2. Enricher and Filter are opposites; the Claim Check is a Filter that guarantees restoration by persisting the removed data under a retrievable key.
3. Prefer decoupling via transformation over modifying applications — modifying an app to suit another app's needs creates brittle, spreading coupling.
4. The Enricher is inherently synchronous and tightly coupled to its source, so a synchronous protocol (HTTP/ODBC) usually beats asynchronous messaging for it.
5. A Canonical Data Model trades performance (double translation, added latency) for maintainability; choose it unless throughput requirements forbid it, and model only the messaging-relevant fields.
6. The Normalizer = Message Router + a translator per format; detect type via header specifiers, XML roots/XPath, CSV shape, or file naming.
7. Dependencies exist at multiple levels (transport, location, representation, semantics) — reach for the pattern that removes the specific layer that hurts.

## Connects To
- **Ch 3**: refines the Message Translator root pattern into six concrete variants.
- **Ch 4 (Messaging Channels)**: Datatype Channel and Messaging Bridge underpin the Normalizer and Envelope Wrapper.
- **Ch 7 (Message Routing)**: the Normalizer embeds a Message Router; the Filtering Splitter builds on the Splitter; Content-Based Router relies on promoted header fields.
- **Ch 9 (Messaging Endpoints)**: Messaging Mapper and Channel Adapter implement Canonical Data Model conformance and metadata extraction.
- **Ch 12 (System Management)**: Format Indicator versions the evolving canonical format.
