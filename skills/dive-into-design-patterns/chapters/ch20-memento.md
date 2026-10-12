# Chapter 20: MEMENTO

*Also known as: Snapshot. Category: Behavioral.*

## Core Idea
Save and restore an object's previous state without revealing the details of its implementation (preserving encapsulation).

## Frameworks Introduced
- **Memento**: Delegates snapshot creation to the state's owner (the originator); the snapshot lives in an opaque memento object that only the originator can read.
  - When to use:
    - You want snapshots of an object's state to restore a previous state (undo, or transaction rollback on error).
    - Direct access to an object's fields/getters/setters would violate its encapsulation.
  - How: Originator produces and restores mementos; memento is an immutable value object; caretaker stores mementos (often a stack) and decides when to capture/restore — but can't read their contents.

## Key Concepts
- **Originator**: Owns the state; creates snapshots of itself and restores from them.
- **Memento (Snapshot)**: Immutable value object holding the originator's state; data passed once via constructor.
- **Caretaker**: Knows when/why to capture and restore; stores mementos (e.g. a history stack) via a limited interface; can't tamper with their state.
- **Limited/intermediary interface**: What the caretaker sees — only metadata (creation time, operation name), never the state.
- **Three implementations**: nested classes (classic, C++/C#/Java); intermediate interface (for languages lacking nested classes, e.g. PHP); stricter encapsulation where the restore method lives in the memento linked to its originator.

## Mental Models
- **Real-World Analogy**: Think of an undo history as a stack of sealed envelopes — only the originator can open and read its own envelope; the caretaker just holds and orders them.
- Think of the originator as the only one allowed to peek inside its own snapshots.

## Anti-patterns
- **Broken encapsulation**: Letting outside objects copy state by exposing public fields makes classes fragile to refactoring — the very problem Memento solves.
- **Memory growth**: Creating mementos too often consumes lots of RAM; caretakers must track lifecycle to destroy obsolete mementos.
- **Dynamic-language leakage**: PHP/Python/JavaScript can't guarantee a memento's state stays untouched.

## Code Examples
```
class Editor is                               // Originator
    private field text, curX, curY, selectionWidth
    method createSnapshot(): Snapshot is
        return new Snapshot(this, text, curX, curY, selectionWidth)

class Snapshot is                             // Memento (immutable)
    private field editor, text, curX, curY, selectionWidth
    constructor Snapshot(editor, text, curX, curY, selectionWidth) is ...
    method restore() is
        editor.setText(text); editor.setCursor(curX, curY)
        editor.setSelectionWidth(selectionWidth)

class Command is                              // Caretaker
    private field backup: Snapshot
    method makeBackup() is backup = editor.createSnapshot()
    method undo() is if (backup != null) backup.restore()
```
- **What it demonstrates**: The editor (originator) makes a self-snapshot; the command (caretaker) holds it and restores on undo — the memento exposes no public state.

## Reference Tables
| Pros | Cons |
|------|------|
| Snapshot state without violating encapsulation | App may consume lots of RAM if mementos are created too often |
| Simplify originator by letting caretaker maintain history | Caretakers must track lifecycle to destroy obsolete mementos |
| | Dynamic languages (PHP/Python/JS) can't guarantee memento immutability |

## Worked Example
A text editor needs undo across text, cursor coordinates, scroll, etc. The naive approach exposes object internals to copy them — breaking encapsulation and making refactors painful. Memento has the `Editor` (originator) create immutable `Snapshot` mementos of its own state. A `History` (or `Command`) caretaker keeps a stack and, on undo, hands the latest memento back to the editor to restore. Mementos are linked to their editor, so the app can support multiple editor windows with one centralized undo stack.

## Key Takeaways
1. The originator — not outsiders — creates and restores its own snapshots.
2. Mementos are immutable value objects, data set once via constructor.
3. Caretakers store/order mementos through a limited interface, never reading state.
4. Nested classes give the cleanest encapsulation; an interface substitutes where they're unavailable.
5. Beyond undo, Memento supports transaction rollback on error.

## Connects To
- **Command**: use together for undo — commands perform operations, mementos save state just before each command runs.
- **Iterator**: capture iteration state with a memento and roll it back if needed.
- **Prototype**: a simpler alternative when the object's state is straightforward and lacks (or can easily re-establish) external links.
