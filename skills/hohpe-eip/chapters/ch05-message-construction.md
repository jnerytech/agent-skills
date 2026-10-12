# Chapter 5: Message Construction

## Core Idea
Deciding to send a message is only the start; you must also choose the message's *intent* (command, document, or event), arrange for responses, correlate related messages, chunk oversized data, expire stale data, and let formats evolve. These nine patterns are the vocabulary for constructing well-behaved messages.

## Frameworks Introduced
- **Command Message**: reliably invoke a procedure in another application by wrapping a request as an object (GoF Command) inside a message.
  - When to use: you want RPC-style invocation but with the asynchrony/reliability of messaging (caller need not block, target need not be up right now).
  - How: put method name + parameters in a regular message (JMS `ObjectMessage`/`TextMessage`, .NET `Message`, RPC-style SOAP body). Send on a **Point-to-Point Channel** so the command runs exactly once.
- **Document Message**: reliably transfer a data structure between applications without dictating what to do with it.
  - When to use: one process has data another needs, and messaging beats File Transfer/Shared Database for coordination and reliability.
  - How: place a single data unit (object or XML) in a message; send Point-to-Point to avoid duplication. Used as the reply in Request-Reply; document-style SOAP body.
- **Event Message**: reliable, asynchronous event notification between applications (the Observer pattern over messaging).
  - When to use: a change in one app must notify others without the sender knowing/blocking on each listener.
  - How: wrap the event and broadcast on a **Publish-Subscribe Channel**. Contents often minimal; timing critical. Subscribers can be non-durable and drop events when busy.
- **Request-Reply**: get a response back over one-way messaging by sending a *pair* of messages, each on its own channel.
  - When to use: communication must be two-way (return value, query result, acknowledgement).
  - How: requestor sends request, replier sends reply on a separate (almost always point-to-point) channel. Requestor receives via **Synchronous Block** or **Asynchronous Callback**.
- **Return Address**: tell the replier where to send the reply.
  - When to use: a replier serves many requestors, or replies must go to a callback processor rather than the requestor itself.
  - How: put the reply channel in the request *header* (JMS `JMSReplyTo`, .NET `ResponseQueue`). Analogous to email `reply-to`.
- **Correlation Identifier**: let a requestor match a received reply to the request that caused it.
  - When to use: multiple outstanding asynchronous requests where reply order/timing is unpredictable.
  - How: request carries a unique **request ID**; replier copies it into the reply's **correlation ID** (in the header). Can key off the message ID or a business object ID.
- **Message Sequence**: transmit an arbitrarily large amount of data by splitting it into ordered chunks.
  - When to use: data exceeds a single message's practical/absolute size limit (e.g., MSMQ 4 MB, 32 Kb mainframe chunks) or a reply is too large.
  - How: mark each message with three fields — sequence identifier, position identifier, size-or-end indicator (like "1 of 3"). Single consumer; optionally use a Transactional Client.
- **Message Expiration**: mark a message stale after a deadline so it is ignored.
  - When to use: time-sensitive contents (e.g., a stock quote) that are useless if delivered late.
  - How: set a relative time-to-live (JMS `JMSExpiration`/`setTimeToLive`, .NET `TimeToBeReceived`/`TimeToReachQueue`); expired messages are discarded or moved to a Dead Letter Channel.
- **Format Indicator**: allow a message's data format to evolve over time.
  - When to use: an enterprise/canonical data format must change while old and new formats coexist on shared channels.
  - How: include a version number, a foreign key to a schema, or an embedded format document, so receivers know how to interpret contents.

## Key Concepts
- **Message intent**: the sender's expectation of the receiver — invoke code (command), take data (document), or note a change (event).
- **Messaging RPC**: Request-Reply where request is a Command Message and reply is a Document Message carrying the return value or exception.
- **Messaging Query**: Request-Reply where the request is a query command and the reply is the result set (often a Message Sequence).
- **Notify/Acknowledge**: Request-Reply where request is an Event Message and reply is a Document Message acknowledging it.
- **Push vs. pull model**: push sends full state with the event (combined document/event); pull sends a minimal event, and interested observers request details (Event + Command + Document, three messages).
- **Request ID / Correlation ID**: unique token in the request; the same value echoed in the reply's header to link the two.
- **Synchronous Block vs. Asynchronous Callback**: single blocked thread (simple, one outstanding request) vs. separate reply thread invoking callbacks (many outstanding requests, crash-recoverable).
- **Sequence identification fields**: sequence identifier, position identifier, and size/end indicator that let a receiver reassemble chunks even if out of order.
- **Time-to-live (relative expiration)**: expiration = sent time + TTL, letting the messaging system compute the absolute deadline across timezones/clocks.

## Mental Models
- **Command/Document/Event = verb/noun/announcement.** Command says "do this," Document says "here's data," Event says "this happened." Same bytes, different contracts.
- **Two-way conversation from one-way pipes.** You can't share or reclaim a message; instead you send two independent messages and glue them with Return Address (where) + Correlation Identifier (which).
- **Shipping in boxes.** A Message Sequence is a mail order split across "1 of 3, 2 of 3, 3 of 3" — labels let the receiver know when it has the whole thing.
- **Carton of milk.** Message Expiration is a sell-by date: past it, the system pulls the message rather than delivering spoiled data.

## Anti-patterns
- **Document Message as disguised RPC**: over-specifying what the receiver must do defeats the point of passing data; use a Command Message if you truly mean to invoke behavior.
- **Assuming reply order matches request order**: messaging guarantees neither ordering nor equal processing time — you need a Correlation Identifier, not positional luck.
- **Serializing requests to avoid confusion**: one-outstanding-request-at-a-time kills throughput; correlate instead.
- **Broadcasting Document Messages**: a Publish-Subscribe Channel creates divergent mutable copies of the document; keep documents point-to-point (or read-only).
- **Message Sequence with Competing Consumers/Message Dispatcher**: different consumers get different chunks and no one can reassemble.
- **Expiring reply messages**: if a reply expires, the requestor never learns whether the request was even received — design for missing replies if you must.
- **Separate channel per format version**: leads to channel explosion; use a Format Indicator on shared channels.

## Reference Tables

Message intent comparison:

| Pattern | Sender's intent | Typical payload | Timing vs. content | Usual channel |
|---|---|---|---|---|
| Command Message | Invoke a procedure | Method name + params | — | Point-to-Point (run once) |
| Document Message | Transfer data | A single data structure/object | Content matters; timing less so | Point-to-Point (no dup) |
| Event Message | Notify of a change | Often minimal/empty | Timing critical; content less | Publish-Subscribe (broadcast) |

Request-Reply supporting patterns:

| Concern | Pattern | Answers | Placed in |
|---|---|---|---|
| Where to send reply | Return Address | "What channel does the requestor listen on?" | Message header |
| Which request a reply is for | Correlation Identifier | "Which of my outstanding requests?" | Message header |
| Reply too big | Message Sequence | "How do I chunk and reassemble?" | Header (ideally) |

## Worked Example
Messaging RPC via JMS temporary queue (from the slice):

1. Requestor creates a **TemporaryQueue** (private to its connection) and sets it as the request's **Return Address** (`setJMSReplyTo(replyQueue)`) — a **Command Message** naming the function to invoke.
2. It sends the request on the request queue and, using `QueueRequestor.request(request)`, blocks (**Synchronous Block**) for the reply.
3. Replier receives the request, reads `getJMSReplyTo()` to learn where to answer, and captures the request's message ID: `requestID = requestMessage.getJMSMessageID()`.
4. Replier builds a **Document Message** (the return value or exception), sets the **Correlation Identifier** `replyMessage.setJMSCorrelationID(requestID)`, and sends it on the reply queue.
5. Requestor receives the reply, reads the correlation ID, and matches it to the original request — completing the two-way exchange over two one-way channels.

If the return value were too large, the reply would instead be a **Message Sequence**, where the sequence identifier is typically the same as the Correlation Identifier.

## Key Takeaways
1. Choose message intent deliberately: Command (invoke), Document (transfer), Event (notify) — they carry different contracts even with identical data.
2. Build two-way conversation from two one-way messages joined by Return Address (routing) and Correlation Identifier (matching).
3. Never rely on reply ordering; correlate replies explicitly and keep IDs in the header, not the body.
4. Chunk oversized data as a Message Sequence with sequence/position/size fields; keep it on a single-consumer channel.
5. Use Message Expiration (relative TTL) for time-sensitive data, but be wary of expiring replies.
6. Plan for format change up front with a Format Indicator (version number, foreign key, or embedded schema) on shared channels.

## Connects To
- **Ch 3**: refines the Message root pattern, splitting it into intent variants (Command/Document/Event) and adding construction concerns (correlation, sequence, expiration, format).
