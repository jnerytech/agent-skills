# Chapter 17: My Application Has No Structure

## Core Idea

Long-lived systems sprawl. A clean architecture erodes under schedule pressure until nobody holds the whole picture, and developers add features only at the "hack points" they happen to know. The root problem is not the code — it is *awareness*. When teams aren't conscious of their architecture, it degrades, because you can't protect something you never think about.

Feathers' central claim: **architecture is too important to be left exclusively to a few people.** You can have an architect, but the only durable way to keep an architecture intact is for *everyone who touches the code* to share the same picture and have a stake in it. On a team of 20 where 3 people know the architecture, the other 17 make structure-eroding mistakes out of unfamiliarity. The fix is cheap, social techniques that keep architectural concerns alive in daily conversation — so that changes fall *in line* with the structure instead of grinding against it.

## Frameworks Introduced

### Telling the Story of the System

A two-person exercise. One asks, "What is the architecture of the system?" The other explains it using only a handful of concepts — as few as two or three. You pretend the listener knows nothing, and in a few sentences name the core pieces and how they interact. Then you add the *next* most important thing, and keep layering until the core design is covered.

The diagnostic signal is the discomfort. To compress the architecture that far you must simplify, and as you say the simple thing ("The gateway gets rule sets from the active database") part of you screams the caveat ("...but also from the current working set!"). That feeling of *lying by omission* is the point. Each lie marks a place where the real system diverges from the ideal — an expediency, an accidental responsibility, a missing abstraction.

The story becomes a design compass. When two implementations are on the table, prefer the one that makes the brief story feel like *less* of a lie. In the JUnit worked example below, adding a report feature to `TestCase` introduces a bold new lie (Tests now also generate reports — never mentioned in the story), while routing the data through `TestResult` only *generalizes* an existing true statement. The second change falls in line with the architecture; the first corrodes it.

Tell the story often, in different ways, trading off which concept is most important. Forcing brevity is forcing abstraction — "when we simplify and rip away detail to describe a system, we are really abstracting," and that is exactly when new abstractions reveal themselves.

### Naked CRC

Classic CRC (Class, Responsibility, Collaborations — Ward Cunningham and Kent Beck, 1980s) marks index cards with a class name, its responsibilities, and its collaborators; if a responsibility doesn't fit, cross it out and move it to another card. **Naked CRC** is CRC with one subtraction: *you don't write on the cards.* The describer lays blank cards on a table, moves them, points at them, overlaps them, and gestures the interactions between them.

The power is physical. Cards make objects tangible, and motion + position make involved scenarios graspable and — oddly — memorable in a way diagrams aren't. Two guidelines only:

1. **Cards represent instances, not classes.**
2. **Overlap cards to show a collection of them.**

In the online-voting example, a "client session" card gets two cards (incoming/outgoing connections) laid on it; a server-session card appears on the right with its own connections; a vote-manager card sits above; and a vote is *acted out* by motioning from a client connection to a server connection. UML documents a system, but it is not the only way to think with design ideas — Naked CRC is for *working out* and *communicating* design live.

## Key Concepts

- **Conversation Scrutiny.** Listen to how the team talks about the design. Are the concepts in conversation present in the code? When the team discusses "a locking policy" but writes inline count-bumping in an array, the missing abstraction is hiding in plain sight — make a `LockingPolicy` class. A strong gap between conversation and code means either the code wasn't allowed to adapt to the team's understanding, or the team needs to understand it differently. "Put some of that understanding in the code."
- **Lie of omission.** The deliberate simplification in a system story; each one is a pointer to architectural debt or a candidate abstraction.
- **The mesmerizing effect of procedural code.** Large procedural blocks "seem to beg for more" — even experienced teams add to them rather than introducing a class. Naming this pull is half of resisting it.
- **Design is never "over."** If the team believes design ends at a milestone while changes keep coming, new code lands in poor places and classes bloat because nobody feels safe introducing abstractions. "There is no surer way to make a legacy system worse."

## Mental Models

- **Architecture as a shared idea, not a document.** When everyone works off the same set of ideas, the team's overall system intelligence is amplified. The artifact lives in heads and conversations; diagrams are downstream.
- **The story as a roadmap.** A simple story of how the system works gives you bearings when hunting for where to add a feature — and makes a scary system less scary.
- **Simplifying = abstracting.** Forced brevity surfaces abstractions you couldn't see while drowning in detail.
- **Changes "falling in line."** Good changes keep the brief story substantially true; bad ones add un-narratable responsibilities.

## Anti-patterns

- **Architect in an ivory tower.** An architect with other duties who can't get into the code or talk to the team daily develops a view that diverges from reality; communication breaks down across the org.
- **Hack-point development.** Adding features only where you already understand the code, regardless of where they belong.
- **Reactive amnesia.** Firefighting emergency after emergency until the big picture is lost — or never existed.
- **UML-as-method.** Believing the notation *is* the design process: draw diagrams, then code, treating documentation as thinking.
- **Abstraction avoidance in legacy code.** Staring at five 1,000-line classes and only asking "what must change?" — never "what class is missing?"

## Key Takeaways

- Architecture degrades when teams stop *thinking* about it; the cure is making it a frequent, shared conversation.
- Use **Telling the Story of the System** to find a 2–3 concept core narrative; treat each uncomfortable simplification as a map marker for debt or a needed abstraction.
- Choose between implementations by which one keeps the story truer — prefer generalizing an existing truth over adding an unspoken responsibility.
- Use **Naked CRC** (blank cards, instances not classes, overlap for collections) to make design tangible, mobile, and memorable.
- Practice **Conversation Scrutiny**: when a concept lives in talk but not in code, that's a missing class.
- Design is never finished while the code is changing.

## Connects To

- **Legacy Code Change Algorithm** (identify change points, find test points, break dependencies, write tests, make changes): the techniques here operate at the *whole-system* scale that the algorithm assumes — you need a shared picture to find good change points instead of hacking the nearest familiar spot.
- **Seam / enabling point** and **sensing vs. separation**: Conversation Scrutiny and the story often reveal *where* responsibilities should split, which is exactly where seams want to be introduced for sensing or separation.
- **Characterization tests** and **"legacy code = code without tests"**: a story gives you the architectural map; characterization tests give you the safety net. Naked CRC and storytelling tell you *what* the structure should become; tests let you refactor toward it without fear.
- Foreshadows the cluster-mapping and feature-sketching techniques used elsewhere in the book for orienting in unfamiliar code.
