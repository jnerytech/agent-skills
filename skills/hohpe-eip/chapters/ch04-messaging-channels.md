# Chapter 4: Messaging Channels

## Core Idea
Channels are the fixed, design-time paths that carry messages between applications; the real work is deciding *which* channels an enterprise needs and *what each is for*, based on cardinality (one vs. many), data type, error handling, reliability, and how non-messaging or foreign systems plug in.

## Frameworks Introduced
- **Point-to-Point Channel**: A channel that ensures exactly one receiver consumes any given message, even when multiple receivers listen.
  - When to use: RPC-style calls or document transfers where a message must be processed once and only once (e.g., a trade request).
  - How: Put the message on the channel; the messaging system guarantees only one consumer succeeds. Multiple consumers become Competing Consumers for load balancing, but each message goes to just one.
- **Publish-Subscribe Channel**: A channel that delivers a copy of each message to every subscriber.
  - When to use: Broadcasting events to all interested parties (e.g., announcing trade completions); also for eavesdropping/debugging.
  - How: One input channel fans out to per-subscriber output channels; each subscriber consumes its own copy once. The message is "consumed" only after all subscribers are notified. Implements Observer/Publisher-Subscriber over messaging.
- **Datatype Channel**: A separate channel per data type so all messages on a channel share one type/format.
  - When to use: When a sender transmits multiple data types and the receiver must know how to process each.
  - How: One channel per type; sender picks the channel by type, receiver infers type from the channel it read on. If too many types, share a channel via Selective Consumer or Message Dispatcher.
- **Invalid Message Channel**: A special channel where a *receiver* moves messages it cannot process.
  - When to use: A delivered message fails parsing/validation, is missing required headers, or lands on the wrong channel.
  - How: On failed interpretation, the receiver reroutes the message here (a messaging "error log"); a monitor/error handler inspects it. Validity is defined by the receiver's context, not the message itself.
- **Dead Letter Channel**: A channel where the *messaging system* puts messages it cannot deliver.
  - When to use: Undeliverable messages — bad/deleted channel, expired (Message Expiration), timed-out, or malformed header.
  - How: System-managed and typically local to each machine (records where/why it died). Automatic from the developer's view; behavior is fixed by the vendor.
- **Guaranteed Delivery**: Persist messages to disk so they survive a messaging-system crash.
  - When to use: Loss is unacceptable (trade requests/confirmations, address changes); skip it when speed matters and loss is tolerable (price ticks).
  - How: Built-in local data store; send doesn't complete until the message is persisted, and it isn't deleted from one store until stored in the next. Costs performance and disk; configurable per-channel or per-message.
- **Channel Adapter**: A component connecting an application to the messaging system without modifying the application.
  - When to use: Legacy/packaged apps not built for messaging, or apps reachable only via UI, API, DB, HTTP/TCP.
  - How: Adapter acts as a messaging client and invokes the app via UI, Business Logic, or Database layer; usually paired with a Message Translator to reach the Canonical Data Model. Variants: Metadata/Design-Time Adapter (extracts formats, not functions).
- **Messaging Bridge**: A connection that replicates messages between two different messaging systems.
  - When to use: Multiple messaging products in one enterprise (mergers, mainframe vs. J2EE/.NET, B2B, or multiple system instances).
  - How: A set of Channel Adapters where the "non-messaging client" is another messaging system; maps and transforms each corresponding channel pair. A standardized API (JMS) does NOT solve this — systems must be interoperable.
- **Message Bus**: A shared backbone (common data model + common command set + messaging infrastructure) letting applications work together while being added/removed freely.
  - When to use: Many independent enterprise apps must coordinate in a decoupled way behind unified GUIs (e.g., insurance product systems).
  - How: Combine a common communications infrastructure (often Pub-Sub + Message Router), Channel Adapters/Service Activators, and a Canonical Data Model with a common command structure (Command Message). Forms a lightweight SOA where request channels act as a service directory.

## Key Concepts
- **Fixed set of channels**: Channels are agreed at design/deployment time, not discovered at runtime (exceptions: reply channels in Request-Reply, hierarchical channels).
- **Unidirectional channel**: A channel effectively flows one way (a bucket with direction); two-way conversation needs two channels.
- **Competing Consumers**: Multiple consumers on a Point-to-Point Channel that split the load, one message each.
- **Durable Subscriber**: A Pub-Sub subscriber that still receives messages sent while it was inactive.
- **Store and forward**: Messaging persists a message at one hop until it can be forwarded to the next.
- **Message type**: The structure and format of a message's contents that a receiver must know to process it.
- **Selective Consumer**: A consumer filtering a shared channel by criteria, letting one channel act as several Datatype Channels.
- **Canonical Data Model**: A unified enterprise-wide data model all channels/applications conform to.
- **"Number of 9s" reliability**: Guaranteed Delivery is resilient, not 100% — cost rises exponentially toward 99.99%+.

## Mental Models
- **Channel as a homogeneous collection, receiver as an iterator**: Just as a typed collection lets an iterator know each element's type, a Datatype Channel lets a receiver know each message's type.
- **Communications bus analogy**: A Message Bus is like a PC's hardware bus (PCI) — common wiring, common command set, universal adapter — but carries finer-grained business messages.
- **Two error lanes**: Invalid = *received but not processable* (receiver's fault-domain); Dead = *never deliverable* (system's fault-domain). Different owners, different channels.
- **Reliability is a dial, not a switch**: Persistence trades throughput and disk for durability; choose per-channel/per-message.

## Anti-patterns
- **Bidirectional channel**: An app both sending to and receiving from one channel re-consumes its own messages — nonsensical.
- **Mixed data types on one channel**: Forces receiver case statements and breaks the "receiver knows type by channel" contract.
- **Treating application errors as invalid messages**: A well-formed Command Message to delete a nonexistent record is an app error, not an invalid message — routing it to the Invalid Message Channel is misleading.
- **Ignored Invalid/Dead channels**: As useless as an ignored error log; they signal integration problems and must be monitored/alerted.
- **Assuming a common API bridges vendors**: JMS makes systems *look* alike to clients but does not make two vendors' systems interoperate.
- **Guaranteed Delivery left on during test/debug**: Stale queued messages get processed before new ones — a classic debugging pitfall; purge or disable.
- **Central intermediary app instead of a bus**: Becomes a bottleneck and single point of failure.

## Reference Tables

| Aspect | Point-to-Point Channel | Publish-Subscribe Channel |
|---|---|---|
| Consumers per message | Exactly one | Every subscriber gets a copy |
| Delivery semantics | One-of-N receives; competing consumers load-balance | Fan-out; consumed only after all notified |
| Typical use | Commands / RPC / document transfer (trade request) | Events / broadcasts (trade completion) |
| JMS type | Queue (QueueSender/QueueReceiver) | Topic (TopicPublisher/TopicSubscriber) |
| Eavesdropping risk | Low (eavesdropper consumes, detected fast) | High (copies; needs security policy) |

| Aspect | Invalid Message Channel | Dead Letter Channel |
|---|---|---|
| Who moves the message | The receiver (application code) | The messaging system |
| Failure kind | Delivered but not *processable* (body/header content) | Cannot be *delivered* (bad channel, expiry, timeout) |
| Determined by | Message body / receiver-relevant header fields | System evaluation of message header |
| Developer control | Fully customizable | Whatever the vendor provides |

## Worked Example
Stock trading channel design (reconstructed from the slice): A **trade request** must execute once → **Point-to-Point Channel**. Once a trade completes, many systems care → publish it on a **Publish-Subscribe Channel**. Quote requests and trade requests have different formats → each gets its own **Datatype Channel** (likewise change-of-address vs. change-of-manager announcements). A trade request missing the security or share count is delivered but unprocessable → the trade app reroutes it to the **Invalid Message Channel**, which senders monitor to see if requests are being discarded. To bound latency, the requestor sets Message Expiration to five minutes; if undeliverable/unread in time, the system moves it to the **Dead Letter Channel**. Trade requests/confirmations use **Guaranteed Delivery**, but high-frequency price ticks do not (overhead prohibitive) — so price changes may need *two* channels, one persistent (for durable subscribers) and one not.

## Key Takeaways
1. Choose cardinality first: one receiver → Point-to-Point; all receivers → Publish-Subscribe.
2. One data type per channel (Datatype Channel) is why enterprises need many channels; the channel tells the receiver the type.
3. Separate the two error lanes: Invalid = receiver can't process; Dead = system can't deliver. Never conflate with application errors.
4. Guaranteed Delivery buys durability with performance and disk — apply selectively, and turn it off for testing.
5. Channel Adapter connects a non-messaging app (via UI, business logic, or DB) without touching it; add a Message Translator for canonical format.
6. Messaging Bridge = Channel Adapters between two messaging systems; interoperability, not a shared API, is what's required.
7. Message Bus = common data model + common commands + messaging infrastructure, forming a decoupled enterprise SOA where apps plug in and out freely.

## Connects To
- **Ch 3**: refines the Message Channel root pattern into concrete channel types and design decisions.
- **Ch 5 (Message Construction)**: Command/Document/Event Message, Request-Reply, Return Address, Message Expiration ride on these channels.
- **Ch 7 (Message Routing)**: Message Router and Selective Consumer extend Datatype Channel and power the Message Bus.
- **Ch 8 (Message Transformation)**: Canonical Data Model and Message Translator complete Channel Adapter and Message Bus.
