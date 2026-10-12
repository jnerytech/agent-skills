# Chapter 22: I Need to Change a Monster Method and I Can't Write Tests for It

## Core Idea

A **monster method** is so long and so complex (hundreds to thousands of lines, with scattered indentation) that you genuinely don't feel comfortable touching it. The trap is circular: legacy code is code without tests, you can't safely refactor without tests, but the method is too tangled to test as it stands. Feathers' escape is to lean on the safest possible mechanisms to carve out **seams** and get a foothold — primarily an **automated refactoring tool** (which proves extractions safe without tests), and when you don't have one, a kit of conservative manual techniques that never touch more than a few lines at a time.

The strategic goal of every early extraction is not beauty. It is two things: (1) **separate logic from awkward dependencies**, and (2) **introduce seams** that make it easier to get tests in place for *more* refactoring. You buy testability incrementally, paying with tiny, low-risk moves. Names can be hokey, methods can land on the "wrong" class — that is fine. Coarse safe work first, details after tests arrive.

## Frameworks Introduced

**Bulleted Method vs. Snarled Method (varieties of monsters).** A **Bulleted Method** has nearly no indentation — a flat sequence of code chunks that reads like a bulleted list. It is the *less* intimidating variety because the lack of wild indentation lets you keep your bearings. The catch: temporaries declared in one chunk are used in the next, so you can't just cut/paste chunks into methods. A **Snarled Method** is dominated by a single large, deeply-nested indented section (e.g., one giant conditional, or loops-inside-switches-inside-ifs). The test for a real snarl: try to line up the blocks — *if you feel vertigo, it's a snarl.* Deep nesting makes it hard to write tests that pin down inner behavior. Real methods are platypuses — mixtures of both, often with bulleted sequences buried inside a snarl.

**Introduce Sensing Variable.** Refactoring doesn't permit *features*, but you may add code that *senses*. Add a (often instance) variable purely to detect that a condition fired or a branch executed, write characterization tests against that variable, then extract the now-pinned logic. Keep the sensing variable and its tests across the whole refactoring session so you can undo and re-extract easily; delete the variable and rewrite/retire the tests when done. Sensing variables also progressively *de-snarl* methods — sense a deeply nested condition, extract it, then work on the extracted method.

**Extract What You Know.** Start small. Find 2–5 line chunks you understand and can name, extract them confidently *without* tests, then add tests to cover them. The key safety metric is **coupling count** — the number of values passing into and out of the extraction (instance-variable accesses don't count; they're just copied along). Favor low counts; a **count of 0** (no parameters, no return — a command) is the safest of all and a great way to map structure. The chief danger a low count avoids is a **type-conversion error**. If count > 0, often pair it with a sensing variable. Naming chunks cascades into design insight.

**Gleaning Dependencies.** When secondary code (e.g., display) is tangled with critical code (e.g., the actual add/computation), write tests for the *critical* behavior you must preserve, then extract the code the tests *don't* cover. It feels like a cop-out — you work on the display code unprotected — but not all behaviors are equal. You lock down what's costly to break and edit the rest freely.

**Break Out a Method Object.** When the ideal sensing variables already exist as *locals* (turning them into instance variables would be confusing), instead move the whole method into a new class whose sole responsibility is that work. Method parameters become constructor parameters; the body goes into a `run`/`execute` method. Now the temporaries become legitimate instance variables you can sense through — and unlike a sensing variable, they're needed in production, so the tests you build are keepers. Drastic, but powerful (originally described by Ward Cunningham; an "invented abstraction").

## Key Concepts

- **Legacy Code Change Algorithm**: identify change points → find test points → break dependencies → write tests → make changes and refactor. This chapter is about getting started when step 4 seems impossible.
- **Seam + enabling point**: extractions create seams (e.g., `displayCommodity`, `clearDisplay`) you can later Subclass and Override to sense or substitute behavior.
- **Sensing vs. separation**: two reasons to break dependencies — *sensing* (observe effects, e.g., via a sensing variable) and *separation* (pull logic away from awkward collaborators). Extractions here serve both.
- **Characterization test**: a test that documents current behavior, not desired behavior — what the sensing-variable tests are.
- **Coupling count**: values in + values out of an extraction; minimize it.
- **Automated refactoring support**: the single biggest lever. A tool that does Extract Method safely removes the need for tests on that step.

## Mental Models

- **Squint at the method.** Blur your eyes: flat = bulleted (lean toward *finding sequences*); one tall indented mass = snarled (lean toward *skeletonizing*).
- **Skeleton, not sculpture.** After extraction the control structure stays put but delegates to named methods — `update()` still looks structurally identical, yet the body is gone. A skeleton is the win.
- **Refactor with one hand behind your back.** With a tool, make a *series* of changes using the tool *exclusively* — no manual edits, no reordering statements, no breaking expressions. This cleanly separates known-safe changes from risky ones. Get tests in place afterward to cover any manual edits.
- **Progress sneaks up on you.** Tiny extractions feel like they make no difference; cumulatively they reveal hidden sequences and better organizations.

## Anti-patterns

- **Reordering statements to group them for extraction.** No tool analyzes whether a reorder is safe — it's a classic bug source. Don't.
- **Extracting big chunks first.** Large chunks miss details (and details are what make code work); they're not as safe or as easy as they look.
- **Extracting straight to another class.** Tempting when the chunk "belongs" elsewhere, but error-prone. *Extract to the current class first* with an awkward name (`recalculateOrder`), then move it once the direction is clear.
- **Promoting locals to instance variables ad hoc** to enable sensing — confusing lifetime/semantics. Prefer Break Out Method Object.
- **Treating the first slicing as final.** Be prepared to undo and re-extract; the first cut buys insight, not waste.
- **Common extraction errors**: forgetting to pass a variable in (and mistakenly declaring it local); naming the extracted method so it hides/overrides a base-class method; wrong parameter/return types or returning the wrong value.

## Code Examples

Skeletonize — extract condition and body *separately* so the control structure is left clean for later reorganization:

```java
// before
if (marginalRate() > 2 && order.hasLimit()) {
    order.readjust(rateCalculator.rateForToday());
    order.recalculate();
}
// after — a skeleton
if (orderNeedsRecalculation(order)) {
    recalculateOrder(order, rateCalculator);
}
```

Find Sequences — extract condition and body *together* so an overarching sequence of operations becomes visible:

```java
recalculateOrder(order, rateCalculator);

void recalculateOrder(Order order, RateCalculator rateCalculator) {
    if (marginalRate() > 2 && order.hasLimit()) {
        order.readjust(rateCalculator.rateForToday());
        order.recalculate();
    }
}
```

Extract What You Know — coupling count = 3 (two in, one out):

```java
void process(int a, int b, int c) {
    int maximum = max(a, b);   // extracted; low count = low risk
    ...
}
```

## Worked Example

`DOMBuilder.processNode(root, childNodes)` is a snarl: much of its real work happens *tangentially* and can only be sensed indirectly — in particular, whether a node gets added to `paraList` when its type matches a gnarly condition (`TF_G || TF_H || (TF_GLOT && isChild())`). No refactoring tool is available, so manual safety is required.

Step 1 — **Introduce Sensing Variable.** Add `public boolean nodeAdded = false;` to the class and set `nodeAdded = true;` right where `paraList.add(node)` happens inside the matched condition.

Step 2 — **Engineer inputs and write characterization tests** against that variable:

```java
void testAddNodeOnBasicChild() {
    DOMBuilder builder = new DOMBuilder();
    List children = new ArrayList();
    children.add(new XDOMNNode(XDOMNNode.TF_G));
    builder.processNode(new XDOMNSnippet(), children);
    assertTrue(builder.nodeAdded);
}
void testNoAddNodeOnNonBasicChild() {
    DOMBuilder builder = new DOMBuilder();
    List children = new ArrayList();
    children.add(new XDOMNNode(XDOMNNode.TF_A));
    builder.processNode(new XDOMNSnippet(), children);
    assertTrue(!builder.nodeAdded);
}
```

Step 3 — **Extract the pinned condition** wholesale into `isBasicChild(node)`:

```java
if (isBasicChild(node)) {
    paraList.add(node);
    nodeAdded = true;
}
...
private boolean isBasicChild(XDOMNNode node) {
    return node.type() == TF_G || node.type() == TF_H
        || (node.type() == TF_GLOT && node.isChild());
}
```

The tests still pass, confirming the condition stayed on the code path. Note the deliberately *cheap* test: a boolean only verifies the branch still fires — Feathers didn't characterize every logical combination because he was confident extracting the whole condition body was safe (see Targeted Testing). Step 4 — later, **remove the flag and its tests**, or refactor the tests to target `isBasicChild` directly.

Parallel tool-assisted example: `CommoditySelectionPanel.update()` is reduced via a series of tool extractions to `commoditiesAreReadyForUpdate()`, `clearDisplay()`, `updateCommodities()`, `singleBrokerCommodity()`, `displayCommodity()` — the body now a skeleton that delegates. Those seams let you Subclass and Override to sense, then split a logic class off the panel.

## Key Takeaways

- Prefer **Sprout Method/Sprout Class** to avoid editing a monster at all; when you must change it, carve seams with the safest mechanism available.
- A **refactoring tool that does Extract Method is your strongest ally** — use it *exclusively* for a run of changes, no manual edits, to keep safe and unsafe work separated.
- Without a tool: **Extract What You Know** (small chunks, low/zero **coupling count**), **Introduce Sensing Variable** to pin tangential behavior, **Gleaning Dependencies** to protect critical behavior while editing the rest, and **Break Out a Method Object** when locals would make ideal sensing instance variables.
- **Skeletonize** when the control structure will need reworking; **Find Sequences** when an overarching sequence will clarify things. Bulleted methods lean toward sequences; snarled toward skeletonizing.
- **Extract to the current class first** with an awkward name; move later. **Extract small pieces first** and **be prepared to redo extractions** — early cuts pay you back in design insight.

## Connects To

- **Ch. 6 (Sprout/Wrap)**: techniques to avoid touching the monster directly.
- **Ch. 13 (I Don't Know What Tests to Write)**: Targeted Testing — how much to test during extraction.
- **Ch. 20 (This Class Is Too Big)**: extracted methods that don't fit signal a class to pull out next.
- **Ch. 25 toolbox**: Extract Method, Introduce Sensing Variable, Break Out Method Object, Subclass and Override Method — the dependency-breaking primitives used here.
- **Legacy Code Change Algorithm**: this chapter unblocks the "find test points / break dependencies / write tests" steps when the method seems untestable.
