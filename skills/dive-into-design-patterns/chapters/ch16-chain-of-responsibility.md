# Chapter 16: CHAIN OF RESPONSIBILITY

*Also known as: CoR, Chain of Command. Category: Behavioral.*

## Core Idea
Pass a request along a chain of handler objects. Each handler decides either to process the request or to forward it to the next handler in the chain.

## Frameworks Introduced
- **Chain of Responsibility**: Turns each processing step into a stand-alone handler object, linked one-to-the-next into a chain.
  - When to use:
    - Your program processes different kinds of requests in various ways, but request types/sequences are unknown beforehand.
    - It's essential to execute several handlers in a particular order.
    - The set of handlers and their order should change at runtime (provide setters to insert/remove/reorder).
  - How: Define a common handler interface with an `execute`/`handle` method; give each handler a reference to the next; each handler chooses to process and/or forward; client composes the chain and triggers any handler in it.

## Key Concepts
- **Handler**: Interface common to all handlers; declares the request-handling method (and optionally `setNext`).
- **Base Handler**: Optional class holding the boilerplate `next` reference + default forwarding behavior.
- **Concrete Handler**: Contains real processing code; decides (1) whether to process, (2) whether to pass along.
- **Request**: The data traveling the chain, best passed as a single object argument.
- **Client**: Composes the chain (statically or dynamically) and dispatches a request to any link.
- **Two styles**: (a) every handler processes then forwards; (b) canonical — first capable handler consumes and stops.

## Mental Models
- **Real-World Analogy**: Tech-support phone tree — autoresponder → live operator → engineer. Each level either solves your problem or escalates to the next.
- Think of a GUI event bubbling up: button → panel → window, processed by the first element capable of handling it.
- A chain can always be extracted from a branch of an object tree.

## Anti-patterns
- **Relying on a request being handled**: Some requests reach the end of the chain unhandled — don't assume guaranteed processing.
- **Confusing with Decorator**: Decorators must keep the request flowing and preserve the base interface's behavior; CoR handlers may stop the flow and act arbitrarily.

## Code Examples
```
interface ComponentWithContextualHelp is
    method showHelp()

abstract class Component implements ComponentWithContextualHelp is
    field tooltipText: string
    protected field container: Container
    method showHelp() is
        if (tooltipText != null) // Show tooltip.
        else container.showHelp()   // forward to next link

class Panel extends Container is
    field modalHelpText: string
    method showHelp() is
        if (modalHelpText != null) // show modal
        else super.showHelp()
```
- **What it demonstrates**: GUI containers form the chain; a help request bubbles up until a component can display it.

## Reference Tables
| Pros | Cons |
|------|------|
| Control the order of request handling | Some requests may end up unhandled |
| Single Responsibility Principle (decouple invokers from performers) | |
| Open/Closed Principle (add handlers without breaking client) | |

## Worked Example
An online ordering system accumulates sequential checks: authentication, data sanitization, brute-force IP filtering, cache lookup. Cramming them into one bloated block makes changes risky and reuse impossible. CoR extracts each check into its own handler class linked in a chain; a request flows through until a check fails (stopping it) or all pass and the order is handled. Chains can be rebuilt per component needing only a subset of checks.

## Key Takeaways
1. Each handler implements the same interface and holds a reference to the next.
2. A handler may process, forward, or stop the request entirely.
3. Compose chains at runtime without coupling client to concrete handlers.
4. Client can trigger any link, not just the first.
5. Be ready for single-link chains and unhandled requests.

## Connects To
- **Command, Mediator, Observer**: all connect senders/receivers differently; CoR passes along a dynamic chain until one handles it.
- **Composite**: a leaf can pass a request up through parents to the root.
- **Command**: handlers can be implemented as Commands; or the request itself can be a Command run across a chain of contexts.
- **Decorator**: similar recursive-composition structure, but Decorators can't break request flow.
