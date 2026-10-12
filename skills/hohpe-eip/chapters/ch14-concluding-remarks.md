# Chapter 14: Concluding Remarks

## Core Idea
Patterns endure while their implementation strategies evolve rapidly; emerging standards do not replace integration patterns but *extend their reach* by making separate implementations of the same pattern interoperable across products, languages, and enterprise boundaries. (Guest chapter by Sean Neville.)

## Emerging Standards Discussed (as of 2003)
- **SOAP / WSDL / UDDI / XML Schema**: The W3C building blocks. Bundled by the WS-I **Basic Profile** (XML Schema 1.0, SOAP 1.1, WSDL 1.1, UDDI 1.0) plus rules for using them together interoperably.
- **ebXML / ebMS**: OASIS + UN/CEFACT successor to EDI. ebMS layers reliability and security onto SOAP-with-Attachments; payloads can be any format (XML, binary, EDI). Uses SOAP Headers to implement Message Routing and Endpoint patterns; its Message Status Service acts as a Control Bus over Message History. The authors treat it as the most mature ("not quite as emerging") of the set.
- **BPEL4WS ("bee-pel")**: Merger of IBM's WSFL and Microsoft's XLANG; submitted to OASIS. A declarative XML **Process Manager** that composes web services ("partners") via "containers" (a Datatype Channel) and "activities," generating Routing Slip / Durable Subscriber / Datatype Channel behaviors. Presented as the most promising process-composition standard.
- **WSCI ("whiskey")**: W3C-submitted rival to BPEL (Sun, Intalio, SAP, BEA), influenced by BPML. Choreography syntax embedded directly inside WSDL. Authors note support was already draining toward BPEL.
- **JSR-207 (Process Definition for Java) & JSR-208 (JBI)**: Java bindings — 207 (BEA) a micro view using Javadoc-style metadata to author components; 208 (Sun) a macro view defining SPIs, bindings/machines/environment, and packaging for integration.
- **WS-\* stack**: Narrower SOAP/WSDL extensions — WS-Coordination/WS-Transaction (Atomic Transaction vs. long-running Business Activity with compensation), WS-Reliability vs. WS-ReliableMessaging (Guaranteed Delivery, Resequencer via SOAP headers), WS-Conversation (stateful Correlation Identifier), WS-Security (broadest consensus; bridges SOAP to PKI/Kerberos/XML Signature), WS-Addressing (Return Address / Recipient List), WS-Policy. The authors warn this landscape was "muddled with competing versions" and a "shake-out seems looming."

## Enduring Lessons
- **The pattern outlasts the standard.** Standardizing a pattern's tactic never retires the pattern — it strengthens it "like rings within a tree trunk," letting it recur at ever-broader scales because implementations become interoperable.
- **Standards raise the level of abstraction.** They free developers from linking protocols (hand-coding a Message Router over raw XML) so they can link business processes and services instead.
- **Don't be enslaved by standards.** Cull useful idioms, but stay focused on the use case; immature standards that become "hindrances or distractions" should "boldly be ignored until mature."
- **The pattern, not the implementation idiom, is what matters** to crafting a message-based application.

## Key Concepts
- **Business process component**: An object/process hybrid uniting a set of web services behind a single endpoint, defined by its *interactions* (and the rules governing them), not its internal composition. The car+driver analogy — viewed as one component by their interaction.
- **Choreography vs. orchestration**: Declaring cross-service message flow (WSCI/BPEL) rather than hand-coding a Process Manager per client.
- **Atomic Transaction (AT) vs. Business Activity (BA)**: Short-lived XA-style rollback vs. long-lived flow using compensation instead of global rollback (the travel-booking example).
- **Standards body**: W3C (open, IP-unencumbered), OASIS (e-business), WS-I (interoperability/profiles), JCP (Java bindings, Sun-controlled), and ad-hoc vendor consortiums (many WS-\* specs) that publish before submitting to a body.
- **Delivery assurances**: WS-ReliableMessaging's four guarantees — at most once, at least once, exactly once, in order.

## Historical Note
*(Commentary.)* Aged well: SOAP/WSDL/XML as the SOA foundation, and BPEL — which did win out over WSCI and became a mature OASIS standard (WS-BPEL 2.0). WS-Security and WS-ReliableMessaging survived. The predicted "shake-out" happened, but harder than forecast: the sprawling WS-\* stack (WS-Coordination, WS-Conversation, WS-Policy, the JBI JSRs) was largely superseded after ~2010 by REST/JSON, and later by lighter messaging (Kafka, AMQP) and event-driven microservices — vindicating the chapter's own warning to favor the pattern over the standard.

## Key Takeaways
1. Standards exist to make different implementations of the same pattern interoperable — that is their value to a pattern language.
2. The patterns in this book (Message Router, Correlation Identifier, Guaranteed Delivery, Process Manager, Control Bus…) reappear inside these standards at a higher level of abstraction.
3. Business process components are the unit the 2003 industry bet on: services composed and choreographed behind one endpoint.
4. Choose standards pragmatically per use case; ignore immature ones until they settle.
5. Written in 2003, the specifics are dated — but the meta-lesson (implementations churn, patterns persist) is exactly why the pattern language still applies.

## Connects To
- **Ch 1**: closes the loop on the vision for a pattern language of integration — showing the same patterns re-emerging inside emerging standards, at broader scale.
