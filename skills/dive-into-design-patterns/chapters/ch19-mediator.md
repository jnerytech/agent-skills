# Chapter 19: MEDIATOR

*Also known as: Intermediary, Controller. Category: Behavioral.*

## Core Idea
Reduce chaotic dependencies between objects by forbidding direct communication and forcing them to collaborate only through a mediator object.

## Frameworks Introduced
- **Mediator**: Centralizes the web of inter-component relations into a single mediator class; components depend only on it.
  - When to use:
    - Some classes are hard to change because they're tightly coupled to many others.
    - You can't reuse a component because it's too dependent on other components.
    - You're creating tons of component subclasses just to reuse basic behavior across contexts.
  - How: Declare a mediator interface (usually one `notify(sender, event)` method); concrete mediator holds references to all components and encodes their relations; each component holds only a mediator reference and notifies it instead of calling peers.

## Key Concepts
- **Component**: A class with business logic; holds a reference typed as the mediator interface; unaware of other components.
- **Mediator interface**: Declares the communication/notification method components use.
- **Concrete Mediator**: Encapsulates relations between components; keeps references to them and may manage their lifecycle.
- **notify(sender, event)**: The single channel — a component reports an event; the mediator identifies the sender and triggers the right responses.
- **Black box**: Sender doesn't know who handles its request; receiver doesn't know who sent it.

## Mental Models
- **Real-World Analogy**: Air-traffic control tower — pilots never talk to each other directly; all coordination goes through the controller, who enforces constraints in the busy terminal area.
- Think of the dialog/form class as the mediator that already knows all its sub-elements.

## Anti-patterns
- **God Object**: Over time a mediator can absorb too much and become a bloated God Object.
- **Logic inside form elements**: Putting cross-element rules directly in elements (e.g. checkbox coupled to a text field) makes them unreusable in other forms.

## Code Examples
```
interface Mediator is
    method notify(sender: Component, event: string)

class AuthenticationDialog implements Mediator is
    private field loginOrRegisterChkBx, loginUsername, ..., okBtn, cancelBtn
    method notify(sender, event) is
        if (sender == loginOrRegisterChkBx and event == "check")
            if (loginOrRegisterChkBx.checked) title = "Log in"  // show login, hide registration
            else title = "Register"                              // show registration, hide login
        if (sender == okBtn && event == "click")
            // validate fields / find user / create account

class Component is
    field dialog: Mediator
    method click() is dialog.notify(this, "click")

class Checkbox extends Component is
    method check() is dialog.notify(this, "check")
```
- **What it demonstrates**: UI elements report events to the dialog (mediator); only the mediator knows how elements should collaborate.

## Reference Tables
| Pros | Cons |
|------|------|
| Single Responsibility (communications in one place) | A mediator can evolve into a God Object |
| Open/Closed (new mediators without changing components) | |
| Reduces coupling between components | |
| Components become more reusable | |

## Worked Example
A customer-profile dialog has interdependent controls: checking "I have a dog" reveals a dog-name field; the submit button must validate every field. Embedding these rules in the elements makes them non-reusable. With Mediator, the dialog acts as mediator: each element just calls `dialog.notify(this, event)`; the dialog decides what to show, hide, or validate. Extract a mediator interface and the same button works with any dialog implementing it.

## Key Takeaways
1. Components communicate only through the mediator, never directly.
2. The complex web of relations lives in one concrete mediator class.
3. Components reference the mediator via its interface, enabling reuse with different mediators.
4. A single `notify` method usually suffices as the protocol.
5. Watch for the mediator growing into a God Object.

## Connects To
- **Chain of Responsibility, Command, Observer**: alternative sender/receiver schemes; Mediator removes direct connections, routing via itself.
- **Facade**: also organizes coupled classes, but only simplifies an existing subsystem (which still talks directly); Mediator centralizes and replaces direct communication.
- **Observer**: often elusive distinction — a popular Mediator implementation uses Observer (mediator = publisher, components = subscribers); Mediator's goal is eliminating mutual dependencies, Observer's is dynamic one-way connections.
