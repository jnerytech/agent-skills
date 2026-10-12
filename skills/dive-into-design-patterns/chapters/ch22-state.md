# Chapter 22: STATE

## Core Idea
State is a behavioral pattern that lets an object alter its behavior when its internal state changes — as if the object changed its class. It is closely related to the Finite-State Machine concept.

## Frameworks Introduced
- **State**: Extract each possible state of an object into its own class implementing a common interface; the original object (context) delegates state-specific work to the current state object and swaps it to transition.
  - When to use: when an object behaves differently by current state, the number of states is large, and state code changes frequently; when a class is polluted by massive conditionals keyed on field values; when there's duplicate code across similar states/transitions.
  - How: (1) pick the context class; (2) declare the state interface with state-specific methods; (3) create a class per state, moving relevant code in; (4) add a state reference field + setter in context; (5) replace conditionals with delegation to the state object; (6) switch state by instantiating a state class and passing it to the context.

## Key Concepts
- **Finite-State Machine**: a finite set of states; the program behaves differently per state and switches via predetermined transitions.
- **Transition**: a rule allowing a switch from one state to another (finite and predefined).
- **Context**: stores a reference to a concrete state and delegates all state-specific work; exposes a setter for a new state.
- **State interface**: declares the state-specific methods all concrete states must implement.
- **Concrete State**: provides its own implementation of those methods; may hold a backreference to the context.
- **Backreference**: state's pointer to the context, used to read data and initiate transitions.

## Mental Models
- **Real-World Analogy**: A smartphone's buttons behave differently by device state — unlocked (run functions), locked (show unlock screen), low charge (show charging screen).
- Think of the context as a TV remote whose buttons do different things depending on the active "mode" object plugged in.

## Anti-patterns
- **Massive switch/if conditionals on a `state` field**: any change to transition logic forces edits in every method — the very smell State eliminates.
- **Overusing State**: overkill if there are only a few states or they rarely change.

## Code Examples
```
class AudioPlayer is        // Context
    field state: State
    constructor AudioPlayer() is
        this.state = new ReadyState(this)
    method changeState(state: State) is
        this.state = state
    method clickPlay() is
        state.clickPlay()   // delegate to active state

abstract class State is
    protected field player: AudioPlayer
    abstract method clickPlay()

class ReadyState extends State is
    method clickPlay() is
        player.startPlayback()
        player.changeState(new PlayingState(player))

class PlayingState extends State is
    method clickPlay() is
        player.stopPlayback()
        player.changeState(new ReadyState(player))
```
- **What it demonstrates**: The same UI control (`clickPlay`) produces different behavior and triggers transitions, with states themselves replacing the context's active state.

## Reference Tables
| Pros | Cons |
|------|------|
| Single Responsibility: state code organized into classes | Overkill for few states / rare changes |
| Open/Closed: add new states without changing existing ones or context | |
| Eliminates bulky state-machine conditionals | |

### State vs. Strategy
| State | Strategy |
|-------|----------|
| States may know about each other and initiate transitions | Strategies are independent and unaware of each other |
| Seen as an extension of Strategy | The base pattern; objects fully independent |
| Behavior tied to a lifecycle/transition graph | Behavior is interchangeable algorithms |

## Worked Example
A `Document` has three states: Draft, Moderation, Published. Its `publish()` behaves differently in each: Draft → Moderation; Moderation → Published (only if user is admin); Published → does nothing. Naively this is a switch statement that grows monstrous as states multiply. State extracts each into a class, so `publish()` is delegated to the current state object. The chapter's running pseudocode reuses this idea for a media player (Locked/Ready/Playing states).

## Key Takeaways
1. Each state becomes a class; the context delegates and swaps states to transition.
2. States can hold a backreference and trigger transitions in the context.
3. State replaces sprawling conditionals with polymorphism (SRP + OCP).
4. The distinguishing trait vs. Strategy: states may depend on and transition into one another.
5. Don't apply it to trivial state machines.

## Connects To
- **Bridge, State, Strategy, Adapter**: similar composition-based structures solving different problems.
- **Strategy**: State is considered an extension of Strategy; both delegate to helper objects, but State allows inter-state dependencies and transitions.
