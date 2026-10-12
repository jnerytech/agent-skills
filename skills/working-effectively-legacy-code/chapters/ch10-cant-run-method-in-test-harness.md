# Chapter 10: I Can't Run This Method in a Test Harness

## Core Idea

Getting a class into a test harness (Chapter 9) is only the first battle. The
second is writing a test for the *specific method* you need to change. You may
have a live object but still be unable to exercise the one method that matters,
because it is hidden, takes parameters you can't construct, fires destructive
side effects, or buries its results inside collaborators you can't see. This
chapter is a catalog of those obstacles and the smallest move that gets past
each one — always in service of the **Legacy Code Change Algorithm** (identify
change points, find test points, break dependencies, write tests, change and
refactor). Remember the working definition: **legacy code is simply code
without tests**. The goal here is not beautiful design; it is to buy yourself a
**characterization test** that pins current behavior before you touch it.

## Frameworks Introduced

| Obstacle (the method...) | Technique to reach for |
|---|---|
| ...is **private**, but a public caller exists | Test through the public method first |
| ...is private and you *must* test it directly | Make it **protected**, then **Subclass and Override Method** to expose it |
| ...is private and exposing it feels wrong (class does too much) | **Move the private method to a new class** (public there, instance held internally) |
| ...uses almost no instance data | **Expose Static Method** |
| ...is long and tangled | **Break Out Method Object** |
| ...takes a **hard-to-fake parameter** (sealed/final library type) | **Adapt Parameter**, then **Skin and Wrap the API** behind an extracted interface + fake |
| ...has a **bad/undetectable side effect** | **Extract Method** to isolate the call, then **Subclass and Override Method** / **Extract and Override Call** to neutralize it and sense |
| ...builds an object internally (`new`) you can't intercept | **Extract and Override Factory Method** |

## Key Concepts

- **Seam + enabling point.** A *seam* is a place where you can alter behavior
  without editing in that place; its *enabling point* is where you decide which
  behavior runs. Making `setSnapRegion` protected creates an object seam — the
  subclass is the enabling point. Extracting a call into an overridable method
  manufactures a seam where none existed.
- **Sensing vs. separation.** You break dependencies for two reasons:
  *separation* (to get the code into the harness at all) and *sensing* (to
  detect effects you otherwise can't observe). The undetectable-side-effect case
  is pure sensing — the method returns nothing, so you override the collaborator
  call and record what was passed.
- **Fake / mock.** A *fake* is a hand-written stand-in implementing an extracted
  interface (`FakeHttpPostedFile : IHttpPostedFile`). A testing subclass that
  captures `displayText`/`accountSymbol` is acting as a fake-by-override.
- **Characterization test.** The performCommand test asserts
  `"SYM: basic account"` — it documents what the code *does today*, giving you a
  safety net before refactoring further.
- **Command/Query Separation (Meyer).** A method is a *command* (changes state,
  returns nothing) or a *query* (returns a value, no side effect) — never both.
  Splitting the GUI handler along this line is what makes the logic senseable.

## Mental Models

- **"Should I make a private method public?"** The most common testing question
  has a blunt answer: *if you need to test a private method, make it public.* If
  that bothers you, the discomfort is diagnostic — your class is doing too much.
  Two reasons it bothers us, with remedies:
  1. *It's just a utility clients don't care about* — forgivable; an extra
     public method is minor, though consider relocating it to another class.
  2. *Clients could corrupt other methods' results* — serious; **move the
     private methods to a new class** where they are legitimately public and the
     original class holds an internal instance. That makes them testable *and*
     improves the design.
- **Good design is testable; untestable design is bad.** Feathers states this
  flatly. The friction you feel is information, not an obstacle to suppress.
- **Pain is an impetus, not an enemy.** Don't paper over a too-big class with
  reflection hacks — that "delays the bill" and hides how bad the code has
  gotten until repair is unaffordable.
- **Safety first; ugly is fine.** Coarse, automated **Extract Method**
  refactorings with poor names are an acceptable *first* step. A `setDescription`
  that secretly news-up and shows a frame is "downright nasty" — but tolerable
  until tests exist. Clean up *after* the net is in place.

## Anti-patterns

- **Subverting access protection** via reflection to poke private state. Handy
  for a moment, but keeping such tests around masks design rot — "the sneaky way
  out."
- **Depending directly on sealed/final library classes** (`HttpPostedFile`).
  The fault isn't `sealed`/`final`; it's binding straight to types you don't
  control with no wrapper for wiggle room.
- **Testing through the GUI** for logic that merely happens to live in a Frame —
  it prompts for input and shows windows; "there is no decent place to sense."
- **Methods that are both command and query**, forcing you to read the body to
  learn whether calling twice is safe.
- **Making a private method public reflexively** when the real problem is an
  overloaded class — fix the responsibility, don't widen the interface.

## Code Examples

**Subclass and Override Method to reach a hidden method** (C++):

```cpp
class CCAImage {
protected:                                   // was private
    void setSnapRegion(int x, int y, int dx, int dy);
public:
    void snap();
};

class TestingCCAImage : public CCAImage {
public:
    using CCAImage::setSnapRegion;            // expose via using-declaration
};
```

**Adapt Parameter + Skin and Wrap the API** for an unfakeable parameter (C#):

```csharp
public interface IHttpPostedFile {           // extracted interface
    int ContentLength { get; }
    string FileName { get; }
}
public class HttpPostedFileWrapper : IHttpPostedFile {     // production
    HttpPostedFile file;
    public int ContentLength { get { return file.ContentLength; } }
}
public class FakeHttpPostedFile : IHttpPostedFile {        // test
    public FakeHttpPostedFile(int length, Stream s) { ... }
}
```
(The sealed `HttpFileCollection` is sidestepped by subclassing its *unsealed*
superclass `NameObjectCollectionBase` — Adapt Parameter, with **Lean on the
Compiler** to make the swap safe.)

## Worked Example

`AccountDetailFrame.performCommand` does everything: it reads an `ActionEvent`,
computes text, **creates and shows a `DetailFrame`**, scrapes a value back out
of it, and sets a `TextField`. Running it in a harness is pointless — it would
pop windows and demand input, and its real result (the display text) is a side
effect with nowhere to sense.

The moves, conservatively, with a refactoring tool:

1. **Extract Method** the whole body into `performCommand(String source)`,
   severing the `ActionEvent` dependency at the `actionPerformed` boundary.
2. Promote `detailDisplay` to an **instance variable**, then **Extract Method**
   on every chunk that touches a collaborator — guided by *Command/Query
   Separation*: `setDescription(...)` (command, hides the frame creation),
   `getAccountSymbol()` (query), `setDisplayText(...)` (command). Names
   deliberately *hide* the GUI so the extracted methods read as domain
   operations.
3. **Subclass and Override Method** in a testing subclass that overrides those
   seams to stub the frame and capture output:

```java
public class TestingAccountDetailFrame extends AccountDetailFrame {
    String displayText = "", accountSymbol = "";
    void setDescription(String d) { }              // neutralize side effect
    String getAccountSymbol() { return accountSymbol; }   // feed sensed input
    void setDisplayText(String t) { displayText = t; }    // sense output
}

public void testPerformCommand() {
    TestingAccountDetailFrame frame = new TestingAccountDetailFrame();
    frame.accountSymbol = "SYM";
    frame.performCommand("project activity");
    assertEquals("SYM: basic account", frame.displayText);   // characterization
}
```

The overridden `setDescription` is the **Extract and Override Call** in spirit —
the offending `new DetailFrame(); ...show()` call is isolated behind a method
and overridden away. The business logic now runs, headless, under test. The
ugliness (a "setter" that creates a window) is noted and deferred; later this
splits cleanly into a `SymbolSource` collaborator (Figure 10.2).

## Key Takeaways

- Instantiating the class ≠ being able to run the method; diagnose the *method's*
  obstacle: accessibility, parameters, side effects, or sensing.
- Test private methods through public callers when you can — it tests them as
  actually used and resists over-generalizing.
- When you can't: protected + **Subclass and Override Method**, or relocate the
  method to a new class. Wanting it public is a signal the class is too big.
- For sealed/final parameters: **Adapt Parameter** + **Skin and Wrap the API**
  behind an extracted interface, then inject a fake.
- For undetectable side effects: **Extract Method**, then **Extract and Override
  Call** / **Subclass and Override Method** to convert an invisible effect into
  something you can sense.
- Coarse, safe, ugly-but-tested beats clean-but-untested. Get the
  characterization test first.

## Connects To

- **Chapter 9 (I Can't Get This Class into a Test Harness):** prerequisite —
  instantiation first, then method-level access.
- **Chapter 11 (I Need to Make a Change... What Methods Should I Test?):** once
  the method is runnable, characterization tests and effect sketches guide what
  to pin.
- **Chapter 20 (This Class Is Too Big):** the proper home for "move the private
  method to a new class"; here it's deferred under release pressure.
- **Chapters 14 & 15 (Dependencies on Libraries / All API Calls):** deeper
  treatment of wrapping sealed/final third-party types.
- **Chapter 25:** Extract and Override Call, Extract and Override Factory
  Method, Subclass and Override Method, Adapt Parameter, Expose Static Method,
  Break Out Method Object, Skin and Wrap the API, Lean on the Compiler — the
  technique reference.
