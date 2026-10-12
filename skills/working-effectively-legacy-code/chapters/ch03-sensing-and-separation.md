# Chapter 3: Sensing and Separation

## Core Idea
There are exactly two reasons to break dependencies to get code under test: **sensing** (to see effects you otherwise can't access) and **separation** (to get the code to run at all outside production). Fake objects are the dominant tool for sensing.

## Frameworks Introduced
- **Sensing vs. Separation** — the two motives for breaking a dependency.
  - **Sensing**: break dependencies to *sense* values/effects your code computes that you can't otherwise reach.
  - **Separation**: break dependencies to *separate* a piece of code so it can even run in a harness.
  - When to use: before breaking any dependency, name which problem you're solving — it points to the right technique.
- **Fake Object**: an object that impersonates a collaborator of the class under test, capturing what would have happened.
  - How: extract an interface the real collaborator implements; write a fake implementation that records calls; inject it into the class under test.
- **Mock Object**: a fake that performs assertions internally — you set expectations up front, then call `verify()`.
  - When to use: when you'd otherwise write many hand-rolled fakes; only if your language has a mock framework. Simple fakes suffice most of the time.

## Key Concepts
- **The Two Sides of a Fake**: the *production side* implements the collaborator interface (e.g. `showLine`); the *test side* exposes extra query methods (e.g. `getLastLine`). Hold the object as the fake type in the test, pass it as the interface type to production code.
- **Fakes support real tests**: "that's not really testing" misses the point — a focused test that tells you how `Sale` affects displays *localizes* errors. Divide and conquer.

## Code Examples
Extract a `Display` interface so `Sale` can take a real or fake display:
```java
public interface Display { void showLine(String line); }

public class FakeDisplay implements Display {
    private String lastLine = "";
    public void showLine(String line) { lastLine = line; }   // production side
    public String getLastLine() { return lastLine; }          // test side
}

public void testDisplayAnItem() {
    FakeDisplay display = new FakeDisplay();   // held as FakeDisplay, not Display
    Sale sale = new Sale(display);
    sale.scan("1");
    assertEquals("Milk $3.99", display.getLastLine());
}
```
- **What it demonstrates**: injection + extracted interface turns an untestable hardware call into a sensible assertion.

A **mock** moves the assertion inside the object:
```java
MockDisplay display = new MockDisplay();
display.setExpectation("showLine", "Milk $3.99");
Sale sale = new Sale(display);
sale.scan("1");
display.verify();   // fails if the expected call didn't happen
```

## Mental Models
- Before any dependency break, ask: "Am I sensing or separating?" The answer narrows the catalog.
- A fake has two faces: one the production code sees, one the test interrogates.

## Key Takeaways
1. Sensing and separation are the *only* two reasons to break a dependency for testing.
2. There are many separation techniques but one dominant sensing technique: fakes.
3. Extract an interface, inject a fake, query the fake — the canonical sensing move.
4. In non-OO languages, fake by defining an alternative function that records into a global structure (see Ch 19).
5. Reach for mocks only when hand-fakes multiply.

## Connects To
- **Ch 4**: the seam that lets you substitute the fake.
- **Ch 19**: faking in non-OO code.
- **Ch 25**: Extract Interface, Parameterize Constructor — the moves that enable injection.
