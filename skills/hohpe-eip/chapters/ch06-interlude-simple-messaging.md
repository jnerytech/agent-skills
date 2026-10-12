# Chapter 6: Interlude — Simple Messaging

## Core Idea
This interlude drops from abstract patterns into runnable code, showing how a
handful of Message Construction and Channel patterns compose into two working
programs — Request/Reply (JMS + .NET/MSMQ) and Publish/Subscribe (JMS Topic).
The point: real APIs already give you these patterns; you just wire them together.

## What This Interlude Demonstrates
- **JMS Request/Reply** (Requestor + Replier): Request-Reply over a pair of Point-to-Point Channels, with Return Address, Correlation Identifier, and rerouting bad messages to an Invalid Message Channel.
- **.NET Request/Reply** (MSMQ): the same example in C#/`System.Messaging` — same patterns, different API (`MessageQueue`, `ResponseQueue`, async `BeginReceive`).
- **JMS Publish/Subscribe**: implements the GoF Observer pattern distributedly via a JMS Topic, wrapped in Messaging Gateways, contrasting push vs pull models.

## Code Examples
### JMS Request/Reply
Requestor sets a **Return Address** and sends; blocks synchronously for the reply (Polling Consumer):
```java
public void send() throws JMSException {
  TextMessage requestMessage = session.createTextMessage();
  requestMessage.setText("Hello world.");
  requestMessage.setJMSReplyTo(replyQueue);   // Return Address
  requestProducer.send(requestMessage);
}
public void receiveSync() throws JMSException {
  Message msg = replyConsumer.receive();      // blocks = Polling Consumer
  if (msg instanceof TextMessage) { /* ... */ }
  else { msg.setJMSCorrelationID(msg.getJMSMessageID());
         invalidProducer.send(msg); }          // Invalid Message Channel
}
```
Replier is event-driven (`MessageListener.onMessage`), honoring the Return Address and setting the Correlation Identifier:
```java
Destination replyDestination = message.getJMSReplyTo();     // use sender's Return Address
MessageProducer replyProducer = session.createProducer(replyDestination);
TextMessage replyMessage = session.createTextMessage();
replyMessage.setText(contents);
replyMessage.setJMSCorrelationID(requestMessage.getJMSMessageID()); // Correlation Identifier
replyProducer.send(replyMessage);
```
- **Demonstrates**: Request-Reply, Return Address (`JMSReplyTo`), Correlation Identifier, Datatype Channel, Invalid Message Channel; Polling Consumer (requestor) vs Event-Driven Consumer (replier).

### .NET Request/Reply
Same shape in MSMQ — `ResponseQueue` is the Return Address, `Receive()` blocks:
```csharp
public void Send() {
  Message requestMessage = new Message();
  requestMessage.Body = "Hello world.";
  requestMessage.ResponseQueue = replyQueue;   // Return Address
  requestQueue.Send(requestMessage);
}
public void ReceiveSync() {
  Message replyMessage = replyQueue.Receive(); // synchronous = Polling Consumer
}
```
Replier subscribes asynchronously and correlates the reply:
```csharp
requestQueue.ReceiveCompleted += new ReceiveCompletedEventHandler(OnReceiveCompleted);
requestQueue.BeginReceive();                    // Event-Driven Consumer
// inside OnReceiveCompleted:
MessageQueue replyQueue = requestMessage.ResponseQueue;   // Return Address
Message replyMessage = new Message();
replyMessage.Body = contents;
replyMessage.CorrelationId = requestMessage.Id; // Correlation Identifier
replyQueue.Send(replyMessage);
requestQueue.BeginReceive();                     // listen for the next one
```
- **Demonstrates**: identical patterns to JMS. Note API differences — `MessageReadPropertyFilter.SetAll()` + `XmlMessageFormatter` configure how bytes become a typed body; `BeginReceive`/`EndReceive` is the async Event-Driven Consumer idiom; invalid messages caught via `try/catch` (a wrong body type throws) then resent to the invalid queue.

### JMS Publish/Subscribe
A Topic implements distributed Observer. The subject's gateway just sends one message:
```java
protected void initialize() throws JMSException, NamingException {
  ConnectionFactory cf = JndiUtil.getQueueConnectionFactory();
  connection = cf.createConnection();
  session = connection.createSession(false, Session.AUTO_ACKNOWLEDGE);
  Destination updateTopic = JndiUtil.getDestination(UPDATE_TOPIC_NAME); // a Topic
  updateProducer = session.createProducer(updateTopic);
  connection.start();
}
public void notify(String state) throws JMSException {
  TextMessage message = session.createTextMessage(state);
  updateProducer.send(message);   // one send fans out to all subscribers (push model)
}
```
Each observer's gateway subscribes to the same Topic and reacts:
```java
updateConsumer = session.createConsumer(updateTopic);
updateConsumer.setMessageListener(this);   // Event-Driven Consumer
public void onMessage(Message message) {
  TextMessage textMsg = (TextMessage) message;
  update(textMsg.getText());                // push: state travels in the message
}
public void attach() { connection.start(); }   // = Observer.Attach / subscribe
```
- **Demonstrates**: Publish-Subscribe Channel (JMS Topic), Event Message, Messaging Gateway (subject/observer are messaging-agnostic), Event-Driven Consumer, Durable Subscriber (to survive disconnects). The **push model** carries state in the notification; the **pull model** sends a stateless notify, then each observer does a Request-Reply (Command Message → Document Message) using a `TemporaryQueue` as its private Return Address.

## Key Concepts
- **JMS Session**: single-threaded context created from a `Connection` for producing/consuming; one connection per app, one session per independent thread.
- **Destination / Queue / Topic**: a `Destination` is the channel; a Queue is Point-to-Point, a Topic is Publish-Subscribe.
- **MessageProducer / MessageConsumer**: send / receive endpoints on a Destination (`TopicPublisher`/`TopicSubscriber` are the Topic-typed variants).
- **JMSReplyTo / ResponseQueue**: the Return Address property carried by the request.
- **JMSCorrelationID / CorrelationId**: links a reply (or resent invalid message) back to the original message's ID.
- **MSMQ `MessageQueue`**: .NET queue handle; `Receive()` = blocking, `BeginReceive`/`EndReceive` + `ReceiveCompleted` = async.
- **XmlMessageFormatter / MessageReadPropertyFilter**: MSMQ config for deserializing the body type and reading all properties.
- **TemporaryQueue**: a JMS-created private, non-persistent queue an observer uses as its own reply channel in the pull model.

## Key Takeaways
1. The abstract patterns are already primitives in the APIs — Return Address is `JMSReplyTo`/`ResponseQueue`, Correlation Identifier is `JMSCorrelationID`/`CorrelationId`.
2. Requestor and Replier differ mainly in consumption style: the requestor polls (`receive()`/`Receive()`), the replier is event-driven (`MessageListener`/`ReceiveCompleted`).
3. Invalid messages are never silently dropped — they are resent to an Invalid Message Channel, and because resending mints a new ID, the original ID is preserved in the correlation ID.
4. Publish-Subscribe makes distributed Observer trivial: one send fans out to all subscribers, so the Subject needs no threading, no remote methods, and no ORB.
5. Messaging Gateways keep the domain Subject/Observer completely unaware of JMS.
6. Choose push (state in the message, one one-way hop) vs pull (stateless notify + a Request-Reply per observer, needing per-observer reply channels) by weighing simplicity against wasted data transfer.

## Connects To
- **Ch 5**: implements Request-Reply, Correlation Identifier, Return Address, and Message Construction types (Document/Command/Event Message).
- **Ch 4**: Point-to-Point (Queue) vs Publish-Subscribe (Topic) channels, Datatype Channel, and Invalid Message Channel shown in code.
