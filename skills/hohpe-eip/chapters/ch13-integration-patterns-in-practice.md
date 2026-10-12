# Chapter 13: Integration Patterns in Practice — Bond Trading System

## Core Idea
A real Wall Street bond pricing system, built and run in production for two years, assembled almost entirely from the book's pattern language — showing not just *which* pattern to pick, but how to combine, adapt, and even use one pattern to implement another under real business, technical, and legacy constraints.

## The System
A major investment bank builds a bond pricing system to streamline its trading desk, replacing the drudgery of pricing many bonds across several trading venues (each with its own UI) with one encapsulated application plus bond-specific analytics. Market data (prices reflecting what people will buy/sell a bond for) flows in, is modified per-trader by an analytics engine, then is pushed out to trading venues. The client is a Java thick client (Windows NT + Solaris) chosen for responsiveness and platform independence; the server side inherits legacy C++ components on the TIBCO Information Bus (TIB). Scale: ~20 traders, a couple hundred bonds each, market data feed uses nearly 100,000 channels, updates arrive several times per second (some under 1 ms apart).

## Architecture With Patterns
- **Messaging (integration style)**: Chosen over File Transfer (too much latency), Shared Database (unwanted DB code in client), and RPC (too complex to push constantly-changing data to an unknown number of clients without polling or per-client threads).
- **Publish-Subscribe Channel**: Gateways publish new pricing data to a per-data-type channel; any number of interested clients subscribe without the gateway tracking them. Also used server-to-client so all of a trader's logged-in machines get updates.
- **Message Bus**: All-Java components communicating over JMS (IBM MQSeries, since the bank is an "IBM shop") form a generic bus so future bank systems can integrate with little change.
- **Message Translator**: Needed to bridge TIB (C++) and MQSeries (Java) messages — but implementing it directly would sacrifice JMS-server independence, so it was realized *via other patterns* instead.
- **Channel Adapter + Messaging Bridge**: A pair of lightweight Channel Adapters (one C++/TIB, one Java/JMS) talking over CORBA form a cross-language Messaging Bridge that effectively simulates the Message Translator between two incompatible messaging systems and languages.
- **Content-Based Router**: The Pricing Gateway registers as a consumer of every trader's per-bond channels and forwards each client only its trader's messages, collapsing ~10,000 TIB channels down to ~one JMS channel per trader — keeping routing logic in Java, not split into C++.
- **Message Filter / Selective Consumer**: Considered for letting subscribers screen the data flow; largely sidestepped because TIBCO's per-subject virtual channels let subscribers "filter" by subscribing only to bonds of interest.
- **Point-to-Point Channel**: Used for client-to-server (a client invoking gateway behavior needs exactly one server to handle it).
- **Recipient List**: Considered to solve the "trader logged in on two machines" problem under point-to-point, but rejected as too much recipient-management logic — publish-subscribe on trader-specific channels solved it more cheaply.
- **Aggregator + Polling Consumer**: Fixed a GUI freeze from too-frequent flashing updates by reconciling many partial per-bond field updates into one message; the client became a Polling Consumer (background thread pulling via a Command Message, gateway replying with a Document Message) so the *client*, not the aggregator, controls flow.
- **Message Dispatcher**: Fixed a production crash by pooling Performer consumers behind one Dispatcher listener that returns immediately — parallel processing that (unlike Competing Consumers) works on a Publish-Subscribe Channel.

## Reference Tables

| Problem faced | Pattern applied | Why |
|---|---|---|
| Push constantly-changing prices to unknown # of clients | Messaging + Publish-Subscribe Channel | Gateways broadcast without tracking listeners; avoids polling/per-client RPC threads |
| Let future bank systems reuse pricing | Message Bus (JMS/MQSeries) | Generic backbone; new systems integrate with little change |
| Bridge C++/TIB to Java/JMS without TIBCO Java API | Channel Adapter pair + CORBA = Messaging Bridge | Simulates a Message Translator while keeping JMS-server independence |
| Trader-specific analytics vs per-bond channels | One channel per trader per bond + Content-Based Router in Pricing Gateway | Preserves data integrity and TIB channel separation; collapses to ~1 JMS channel/trader |
| Trader logged in on multiple machines | Publish-Subscribe Channel on trader channels (not Recipient List) | All the trader's clients get the message; avoids recipient-management logic |
| One consumer per client-to-server call | Point-to-Point Channel | Exactly one eligible consumer handles each message |
| GUI freeze from flood of flashing updates | Aggregator + Polling Consumer | Merges partial field updates; client controls consumption rate |
| MQSeries crash: dead-letter queue full of expired msgs | Message Dispatcher (not Aggregator, not Competing Consumers) | Parallel processing on a pub-sub channel; Aggregator can't buffer prices that must forward immediately |

## Key Concepts
- **Market data**: Price and other bond attributes reflecting free-market buy/sell interest; fed in real time and modified per trader by analytics.
- **Analytics engine**: Generic C++/TIB server applying trader-configurable math functions to market data, then rebroadcasting it.
- **Gateway (Pricing / Contribution)**: Java servers encapsulating business logic between the thick client and the legacy C++ servers (market data in, trading-venue contribution out).
- **TIB subjects / virtual channels**: Hierarchical topic names; TIBCO filters one message flow by subject into lightweight per-subject channels, making ~100,000 channels cheap.
- **Dead Letter Channel**: MQSeries' dead-letter queue where expired ("slow consumer") messages land; its unbounded growth crashed the server.
- **Message Expiration**: Time-to-live on market data messages; expired prices are worthless, so they route to the Dead Letter Channel.
- **Slow consumer**: A consumer that can't keep up with message rate, causing expiration and back-pressure.

## Key Takeaways
1. Choosing a pattern is a *discovery process* driven by real forces — business requirements, client decisions, legacy systems, and platform specifics — not a menu pick.
2. Patterns compose: two Channel Adapters over CORBA implemented a Messaging Bridge that in turn simulated a Message Translator — one pattern built from others, with contexts adapted.
3. The right pattern is often decided by *where logic should live* and by business rules (per-bond channels won because keeping the analytics engine generic mattered more than fewer channels).
4. Business requirements break ties between technically valid options — Aggregator beat Message Filter because filtering would have sacrificed data integrity.
5. Patterns help throughout the lifecycle, including firefighting production crashes — but they can't compensate for a fundamental design flaw (the client bottleneck ultimately needed an architectural re-route, not another pattern).
6. Combine channel types by direction: publish-subscribe server-to-client, point-to-point client-to-server, getting each pattern's benefit without its drawback.

## Connects To
- **Ch 4–11**: this is where the whole language comes together — channels, translators, routers, endpoints, and system-management patterns all appear in one running system.
- **Ch 9**: another full case study (Loan Broker).
