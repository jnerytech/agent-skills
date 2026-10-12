# Chapter 17: COMMAND

*Also known as: Action, Transaction. Category: Behavioral.*

## Core Idea
Turn a request into a stand-alone object holding all info about the request. This lets you parameterize methods with requests, queue/delay/log execution, and support undoable operations.

## Frameworks Introduced
- **Command**: Extracts request details (target object, method, arguments) into a separate command class with one trigger method.
  - When to use:
    - You want to parametrize objects with operations.
    - You want to queue, schedule, or execute operations remotely (commands serialize).
    - You want reversible operations (undo/redo via a command history).
  - How: Declare a command interface with a single parameterless `execute()`; concrete commands hold receiver + params as fields set in constructor; senders trigger commands via the interface; client wires receivers → commands → senders.

## Key Concepts
- **Sender (Invoker)**: Initiates requests; holds a command reference and triggers it instead of calling the receiver directly. Doesn't create the command.
- **Command interface**: Usually one `execute()` method, no parameters.
- **Concrete Command**: Implements a specific request; delegates work to a receiver; stores parameters as immutable fields.
- **Receiver**: Object containing the actual business logic; does the real work.
- **Client**: Creates and configures concrete commands, passing receiver + params into their constructors.
- **Command History**: A stack of executed commands (with state backups) enabling undo.

## Mental Models
- **Real-World Analogy**: Ordering in a restaurant — the written paper order is a command. It contains all info, queues on the kitchen wall, and lets the chef cook without re-clarifying with the customer.
- Think of commands as a middle layer that decouples the GUI layer from the business-logic layer.

## Anti-patterns
- **GUI calling business logic directly**: Couples volatile business code to GUI; leads to an explosion of button subclasses and duplicated copy/paste logic across toolbar, menu, shortcut.
- **State-backup undo memory cost**: Full-state backups can eat RAM; alternative is inverse operations (but those may be hard/impossible to implement).

## Code Examples
```
abstract class Command is
    protected field app; protected field editor; protected field backup
    method saveBackup() is backup = editor.text
    method undo() is editor.text = backup
    abstract method execute()   // returns true if state changed

class CutCommand extends Command is
    method execute() is
        saveBackup()
        app.clipboard = editor.getSelection()
        editor.deleteSelection()
        return true

method executeCommand(command) is
    if (command.execute) history.push(command)
```
- **What it demonstrates**: Commands back up editor state before mutating; only state-changing commands push to history, enabling undo.

## Reference Tables
| Pros | Cons |
|------|------|
| Single Responsibility (decouple invokers from performers) | Adds a whole new layer → more complexity |
| Open/Closed (add commands without breaking clients) | |
| Undo/redo possible | |
| Deferred / queued execution possible | |
| Assemble simple commands into a composite (macro) | |

## Worked Example
A text editor toolbar needs buttons that each do different things; copy/paste must also fire from menus and Ctrl+C shortcuts. Instead of button subclasses, the base `Button` stores a command reference and runs it on click. `CopyCommand`, `CutCommand`, `PasteCommand`, `UndoCommand` each delegate to the `Editor` (receiver). The same command instance binds to button, menu, and shortcut — no duplication. A `CommandHistory` stack with state backups powers undo.

## Key Takeaways
1. A command packages receiver + parameters + the action into one object.
2. The sender knows only the command interface, never the receiver.
3. Commands enable undo/redo, queuing, logging, and remote execution.
4. Client wires the object graph: receivers → commands → senders.
5. Same command can serve multiple senders, eliminating duplication.

## Connects To
- **Chain of Responsibility, Mediator, Observer**: alternative sender/receiver connection schemes; Command makes unidirectional connections.
- **CoR**: handlers can be Commands; or the request can be a Command.
- **Memento**: use together for undo — commands run operations, mementos save pre-execution state.
- **Strategy**: similar shape, different intent — Command converts an operation into an object; Strategy swaps interchangeable algorithms.
- **Prototype**: helps store copies of commands in history.
- **Visitor**: a more powerful Command operating across objects of different classes.
