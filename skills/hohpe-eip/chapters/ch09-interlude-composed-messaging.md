# Chapter 9: Interlude — Composed Messaging (Loan Broker)

## Core Idea
One integration problem — a loan broker that shops for the best rate across many banks — implemented three times (synchronous Web Services, asynchronous MSMQ, asynchronous TIBCO). The same *pattern language* describes all three; only the messaging model, coupling, and concurrency change.

## The Loan Broker Problem
A consumer wants the lowest interest rate for a loan. Instead of calling every bank, they use a broker. The broker gathers the customer data once, obtains the customer's credit score/history from a credit agency, decides which banks to ask, sends each a quote request, collects the replies, picks the best (lowest) rate, and returns it. This decomposes into 7 steps: receive request → enrich with credit score → select banks → send requests → collect responses → pick best → reply.

## Pattern Composition
The broker is a *composition* of routing and transformation patterns:

- **Content Enricher** — adds the credit score/history (and computes the recipient bank list) before routing.
- **Recipient List** (distribution) or **Publish-Subscribe Channel** (auction) — fans the request out to banks.
- **Scatter-Gather** — the overall "ask many, combine one" interaction.
- **Aggregator** — collects bank replies and selects the best quote; needs a *completeness condition*.
- **Message Translator / Normalizer** — each bank uses a different message format; translate outbound requests and normalize inbound replies to a common format.
- **Correlation Identifier** — matches asynchronous replies (arriving on a shared channel, out of order) back to the right request/aggregate.
- **Return Address** — lets each caller specify where replies go.
- **Process Manager** — drives the multi-step, event-driven flow and keeps per-request state.
- **Service Activator** — connects the messaging channel to the request-handling business logic.

Three orthogonal design axes produce the variants: **sequencing** (sync/async), **addressing** (fixed/distribution/auction), and **aggregation** (multiple reply channels vs. single channel + correlation).

## Implementations Compared

| Dimension | Sync Web Services (Java/Axis) | Async MSMQ (C#/.NET) | Async TIBCO (ActiveEnterprise) |
|-----------|-------------------------------|----------------------|-------------------------------|
| Sequencing | Synchronous / sequential | Asynchronous / parallel | Asynchronous / parallel |
| Addressing | Distribution (Recipient List) | Distribution (Recipient List) | **Auction** (Pub-Sub) |
| Aggregation | One reply channel per bank (no correlation) | Single channel + **Correlation ID** | Single channel + **Correlation ID** + timeout |
| Completeness | Blocks until each bank returns/times out | Wait for N expected replies (Initialized Aggregator) | **Time-out only** — count of banks unknown |
| Coupling | Tight; broker knows every bank endpoint | Loose; queues decouple, banks addressed by queue | Loosest; banks self-subscribe, broker unaware |
| Concurrency | One open connection per client; server complexity grows | Single event-driven instance + ACTs; pipeline throughput | Process Manager job per request; Selective Consumer filters |
| Complexity | Simplest to reason about, slowest (~n× serial) | Hand-built plumbing (gateways, delegates) | Visual workflow + ECMAScript; infra hidden |

Same composition, very different runtime characteristics. The async versions processed 50 quotes in ~12s vs. an estimated 8–10× longer synchronously; scaling out the credit-bureau bottleneck was as simple as starting more consumer instances on the shared queue.

## Code Examples
### Async MSMQ (.NET) — key snippet
The bank gateway issues one aggregate ID per request (not per message), stamps it on `AppSpecific`, and correlates replies back to the live aggregate:

```csharp
public void GetBestQuote(BankQuoteRequest req, OnBestQuoteEvent cb, Object ACT) {
    Message m = new Message(req);
    m.AppSpecific = aggregationCorrelationID;      // Correlation Identifier
    m.ResponseQueue = bankReplyQueue.GetQueue();   // Return Address
    IMessageSender[] banks = connectionManager
        .GetEligibleBankQueues(req.CreditScore, req.HistoryLength, req.LoanAmount); // Recipient List
    aggregateBuffer.Add(aggregationCorrelationID,
        new BankQuoteAggregate(aggregationCorrelationID, banks.Length, cb, ACT));   // Aggregator init
    aggregationCorrelationID++;
    MessageRouter.SendToRecipientList(m, banks);   // Scatter
}
```
The broker itself extends `AsyncRequestReplyService` and chains callbacks (`ProcessMessage` → `OnCreditReply` → `OnBestQuote` → `SendReply`), later refactored into a `LoanBrokerProcess` + `LoanBrokerPM` **Process Manager**.
- **Demonstrates**: Recipient List, Scatter-Gather, Aggregator, Correlation Identifier, Return Address, Process Manager, Service Activator.

## Key Concepts
- **Distribution vs. Auction**: distribution = Recipient List to a computed set of banks (broker controls who bids, needs a reply per recipient); auction = broadcast via Pub-Sub, any bank may bid, count unknown.
- **Completeness Condition**: how the Aggregator knows it's done — "all expected replies" (distribution) vs. "timeout window" (auction).
- **Initialized Aggregator**: the Recipient List tells the Aggregator how many replies to expect on a shared channel.
- **Correlate by AppSpecific, not Message ID**: a broker-chosen ID survives intermediaries and lets many messages share one aggregate; system message IDs break under a Recipient List (unique per message) and routers.
- **Asynchronous Completion Token (ACT)**: caller-supplied state handed back with the reply so an event-driven broker can resume the right request without blocking.
- **Pipeline (event-driven) processing**: an Event-Driven Consumer processes many requests concurrently in one thread instead of pseudo-synchronously blocking on each step.
- **Mock messaging layer**: narrow `IMessageSender`/`IMessageReceiver` interfaces let a `MockQueue` fire replies inline, so business logic is unit-tested synchronously.

## Key Takeaways
1. Patterns are a *composition language*: the same diagram (Enricher → Recipient List/Pub-Sub → Scatter-Gather → Aggregator) describes wildly different tech stacks.
2. Sync vs. async is the dominant trade-off for one composition: synchronous is simpler (no threads, no correlation, per-bank reply channels) but slow and connection-heavy; asynchronous is far faster and scalable but forces correlation, out-of-order handling, and event-driven state.
3. Addressing choice (distribution vs. auction) determines the Aggregator's completeness condition — count-based when you know the recipients, timeout-based when you don't.
4. Correlation Identifiers are essential once replies share a channel and arrive out of order; choose an application-level ID so intermediaries don't break matching.
5. Loose coupling pays off operationally: async queues let you scale bottleneck consumers (extra credit-bureau instances) with zero code change, and tune routing (drop the pawn-shop from non-catch-all requests) to cut latency 4×.
6. Encapsulate messaging behind gateways/interfaces so the app holds business logic only — this enables mocking, unit testing, and swapping transports (MSMQ ↔ SOAP) without touching the broker.

## Connects To
- **Ch 7**: Scatter-Gather, Aggregator, Recipient List, Process Manager, Content Enricher, Message Translator/Normalizer.
- **Ch 13**: another end-to-end case study (System Management), reusing the Correlation Identifier and Control Bus ideas.
