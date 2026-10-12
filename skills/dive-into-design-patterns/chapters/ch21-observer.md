# Chapter 21: OBSERVER

## Core Idea
Observer is a behavioral pattern that defines a subscription mechanism so multiple objects (subscribers) are automatically notified about any events happening to the object they observe (the publisher). Also known as Event-Subscriber, Listener.

## Frameworks Introduced
- **Observer**: A publisher maintains a list of subscriber references and notifies each one (via a common interface) whenever a relevant event occurs.
  - When to use: when changes to one object's state require changing others, and the set of dependents is unknown or changes dynamically; when objects must observe others only for a limited time or in specific cases.
  - How: (1) split logic into core (publisher) and reactive (subscribers); (2) declare subscriber interface with an `update` method; (3) declare publisher interface with add/remove subscriber methods; (4) put subscription list in an abstract publisher class or a composed helper; (5) concrete publishers notify on events; (6) implement `update` in concrete subscribers; (7) client registers subscribers with publishers.

## Key Concepts
- **Publisher (Subject)**: object holding interesting state that issues events and manages the subscription list.
- **Subscriber**: interface declaring the notification method (usually a single `update`).
- **Concrete Subscriber**: performs actions in response to notifications; all implement the same interface so the publisher stays decoupled.
- **Subscription mechanism**: array of subscriber references plus public add/remove methods.
- **Context data**: info the publisher passes to `update` (as arguments, or by passing itself so the subscriber can fetch data).
- **EventManager**: helper object that holds the subscription list when composition is used instead of inheritance.

## Mental Models
- **Real-World Analogy**: Magazine/newspaper subscriptions. The publisher keeps a list of subscribers and delivers new issues to their mailbox; subscribers can leave the list anytime.
- Think of the publisher as a broadcaster and subscribers as radios tuned in — they can switch on/off at runtime.
- Think of `EventManager` as a centralized event dispatcher letting any object act as publisher.

## Anti-patterns
- **Coupling publisher to concrete subscriber classes**: defeats the pattern; always communicate via the subscriber interface.
- **Relying on notification order**: subscribers are notified in random order — don't depend on sequence.

## Code Examples
```
class EventManager is
    private field listeners: hash map of event types and listeners
    method subscribe(eventType, listener) is
        listeners.add(eventType, listener)
    method unsubscribe(eventType, listener) is
        listeners.remove(eventType, listener)
    method notify(eventType, data) is
        foreach (listener in listeners.of(eventType)) do
            listener.update(data)

class Editor is
    private field events: EventManager
    method openFile(path) is
        this.file = new File(path)
        events.notify("open", file.name)

interface EventListener is
    method update(filename)

class EmailAlertsListener implements EventListener is
    method update(filename) is
        system.email(email, replace('%s', filename, message))
```
- **What it demonstrates**: Composition-based Observer — the Editor delegates subscription management to an EventManager and notifies typed listeners without knowing their concrete classes.

## Reference Tables
| Pros | Cons |
|------|------|
| Open/Closed Principle: add subscribers without changing publisher | Subscribers are notified in random order |
| Establish relations between objects at runtime | |

## Worked Example
A Customer wants to buy a new iPhone soon to arrive at a Store. Polling the store daily wastes the customer's time; mass-emailing every customer spams the uninterested. Observer resolves the conflict: the Store becomes a publisher with a subscription mechanism; interested customers subscribe and are notified only when the product arrives. In the pseudocode this maps to a text Editor (publisher) notifying a LoggingListener (writes to log on "open") and an EmailAlertsListener (emails admin on "save").

## Key Takeaways
1. The publisher communicates with subscribers only through a shared interface, keeping it decoupled.
2. Subscription is dynamic: subscribers join/leave at runtime.
3. Use composition (a helper EventManager) when the publisher is already a subclass and can't extend an abstract base.
4. Pass context data via update arguments, or pass the publisher itself so subscribers fetch data.
5. Notification order is not guaranteed.

## Connects To
- **Chain of Responsibility / Command / Mediator / Observer**: four ways to connect senders and receivers. Observer lets receivers dynamically subscribe/unsubscribe.
- **Mediator**: often implemented using Observer (mediator = publisher, components = subscribers), making the two look similar; but Mediator can also be implemented by permanently linking components.
