# Chapter 20: This Class Is Too Big and I Don't Want It to Get Any Bigger

## Core Idea

Big classes are where legacy systems go to rot. Features arrive as "little tweaks" — a method here, an instance variable there — and the path of least resistance is to bolt them onto whatever class already holds the data. Do that for a year and you get a 50-method God class with 20 responsibilities. Feathers names three concrete costs:

1. **Confusion** — with 50–60 methods and a sea of instance variables, you can't tell what a change affects.
2. **Task scheduling** — 20 responsibilities means ~20 reasons to change, so multiple programmers collide in the same class in the same iteration (thrashing).
3. **Testing pain** — big classes hide too much. Over-encapsulation means there's no way to *sense* the effect of a change, so people fall back on **Edit and Pray**.

The chapter splits cleanly into two jobs. **Tactics**: stop the bleeding *now* without making things worse — use Sprout Class and Sprout Method so the new code lands somewhere small instead of inflating the monster. **Strategy/design skill**: learn to *see* the responsibilities already latent in the class (you're discovering, not inventing them), then extract classes incrementally — applying the **Single Responsibility Principle** at the implementation level first, the interface level later. The governing constraint throughout: this is *legacy code* (code without tests), so the extraction techniques must be safe even when you can't get a test harness around the class yet.

## Frameworks Introduced

### Single Responsibility Principle (SRP)
> Every class should have a single responsibility: a single purpose in the system, and only one reason to change.

"Responsibility" is nebulous, so anchor on **primary/main purpose**, not on counting methods. SRP can be violated two ways:
- **At the interface level** — the public interface *looks* like it does four classes' worth of things.
- **At the implementation level** — the class actually *does* all that work itself instead of delegating.

The violation you care most about is the **implementation level**. If a big class is really a *facade* delegating to small classes, the monolith is already gone — it's just a friendly front end. Fixing implementation-level SRP first is cheap and makes the later interface-level fix easier.

### Heuristics for Finding Responsibilities (the checklist)
A usable, in-order checklist for seeing responsibilities in existing code:

1. **Group Methods** — Write down every method with its access type (public/private/...). Find names that go together; each cluster hints at a responsibility. You don't have to classify all of them — find ones "off to the side" of the main purpose and wait until you must modify one before extracting.
2. **Look at Hidden Methods** — Lots of private/protected methods = "another class dying to get out." If you ever want to test a private method, it probably belongs on another class where it can be legitimately public.
3. **Look for Decisions That Can Change** — Find decisions already baked in: a hard-coded DB, a particular API, a specific set of objects. Do **Extract Method** first (name the method after the *information* you're getting), so a low-level decision gets encapsulated behind methods you can later pull into a class.
4. **Look for Internal Relationships** — Which instance variables are used by which methods? Draw a **feature sketch** (circles for variables and methods; lines from each method to the variables/methods it uses or modifies — skip constructors). Clusters reveal candidate classes; a **pinch point** is a thin set of lines connecting two big clusters — an ideal cut line / new-class interface.
5. **Look for the Primary Responsibility** — Describe the class's responsibility in *one sentence*. Keep adding "...and this, and this" clauses; whatever feels most important is the key responsibility, and the rest should be factored out.
6. **When All Else Fails, Do Some Scratch Refactoring** — Refactor freely (no tests, throwaway) just to see what's possible; then throw it away. What you see is not necessarily what you'll keep.
7. **Focus on the Current Work** — If the change you're making right now provides "a different way of doing" something, that variation point is itself a responsibility to extract and allow substitution for. Stops you from drowning in every possible responsibility.

### Extract Class — conservative, test-free variant
When you can get tests, use Fowler's **Extract Class** directly. When you *can't* (the usual legacy case), use this very conservative sequence (works with or without a refactoring tool):

1. Identify a responsibility to separate.
2. Move the instance variables it needs into a separate section of the class declaration, away from the others.
3. For whole methods to move, **extract their bodies into new methods** named the same but with a unique loud prefix like `MOVING`. Don't move the originals. **Preserve Signatures** if extracting by hand.
4. For parts of methods, extract those into `MOVING`-prefixed methods too, in the separate section.
5. Text-search the class **and all subclasses** to confirm no variable you're moving is used outside the methods you're moving. **Do NOT Lean on the Compiler here** — shadowed variables in subclasses won't be caught and you'll silently change behavior.
6. Move the separated variables and methods to the new class; create an instance in the old class; now you *can* **Lean on the Compiler** to find call sites that must route through the instance.
7. Strip the `MOVING` prefixes, leaning on the compiler to navigate.

The whole point of extracting *bodies* (not moving originals) is to dodge inheritance bugs: moving a method that overrides a base method silently redirects callers to the base version; moving a shadowing variable exposes the one it hid.

### Interface Sniffing / Interface Segregation Principle (ISP)
> When a class is large, rarely do all clients use all its methods.

Carve an interface for each *grouping of methods a particular client uses* and have the big class implement them. Clients see the big class only through their slice — less coupling, no recompiles when the big class changes. This is also how you eventually attack interface-level SRP: make a client-specific interface (e.g., `JobController` for clients that only run `ScheduledJob`s), then flip delegation so a small `StandardJobController` delegates *to* `ScheduledJob` and code migrates out of the monolith. Note: this is "nearly always tougher than it sounds" — clients must change, so you need tests around them first.

## Key Concepts

- **Sprout Class / Sprout Method** — tactical first line of defense: put new code in a *new* class/method so the big class doesn't grow. Sprout Method also *names a thing the class does*, which feeds Heuristic #1.
- **Feature sketch** — disposable 10-minute diagram of internal method→variable/method usage. Arrows point *toward what is used* (the inverse of an **effect sketch**, whose arrows point toward what is *impacted*). Feature sketches map internal structure; effect sketches reason forward from a change point.
- **Pinch point** — a narrow set of dependencies between two clusters in a feature sketch; the natural seam for extraction.
- **Tactics vs. Strategy** — Tactics = stop growth now (Sprout). Strategy = identify responsibilities, share the map with the team, break the class down *on an as-needed basis*. Avoid the "refactoring binge": large refactoring sprees destabilize the system even with care.
- **Implementation-level SRP before interface-level SRP** — the cheap, safe ordering.

## Mental Models

- **The class is a swamp; you drain it one bucket at a time, when you happen to be standing there.** Extraction is opportunistic — triggered by a change you already have to make — not a scheduled crusade.
- **You're an archaeologist, not an architect.** Responsibilities are *already in the code* doing identifiable things. The heuristics are excavation tools; you discover the lines, you don't draw new ones.
- **Castle in the sky.** A beautiful from-scratch multi-class design (the hypothetical `SymbolTable`, etc.) is worthless unless you're actually rewriting that part. Sketch it to learn what's possible — then "just forget about it" and move what exists in a *better direction*, not toward the ideal.
- **The compiler is a flashlight with a blind spot.** Lean on it to find call sites after a move — but it goes blind around inheritance (overrides and shadowed variables). There, manual search + a pair partner is the only safety.

## Anti-patterns

- **Edit and Pray** — changing an over-encapsulated big class with no way to sense the effects.
- **The convenient append** — adding each tweak to the existing class because the data is already there; the root cause of God classes.
- **Refactoring binge** — breaking everything down at once; destabilizes the system mid-release.
- **Overambition after a scratch refactor** — falling in love with the ideal design and rewriting working structure instead of nudging it.
- **Leaning on the Compiler to find variable uses during extraction** — misses shadowed variables in subclasses and silently changes behavior.
- **Making methods public just to test them** — the smell that they belong on a different class entirely.
- **Counting methods as responsibilities** — naïve reading of SRP; the unit is *primary purpose*, not method count.

## Code Examples

The `Reservation` class (a feature-sketch subject). Two strong clusters emerge:

```java
class Reservation {
    private int duration;
    private int dailyRate;
    private Date date;
    private Customer customer;
    private List fees = new ArrayList();

    public void extend(int additionalDays) { duration += additionalDays; }
    public void extendForWeek() { /* uses date, customer, dailyRate, duration */ }
    public void addFee(FeeRider rider) { fees.add(rider); }
    int getAdditionalFees() { /* iterates fees */ }
    int getPrincipalFee() { return dailyRate * RateCalculator.rateBase(customer) * duration; }
    public int getTotalFee() { return getPrincipalFee() + getAdditionalFees(); }
}
```

Cluster A: `duration, dailyRate, date, customer` ↔ `extend, extendForWeek, getPrincipalFee`.
Cluster B: `fees` ↔ `addFee, getAdditionalFees`. The only line crossing between them is `getTotalFee → getPrincipalFee` — the **pinch point**.

Extracting cluster B into `FeeCalculator` and passing the principal fee across the seam (so `FeeCalculator` never reaches back into `Reservation`):

```java
public class Reservation {
    private FeeCalculator calculator = new FeeCalculator();
    private int getPrincipalFee() { ... }            // stays — depends on Reservation's vars
    public void addFee(FeeRider fee) { calculator.addFee(fee); }   // delegate
    public int getTotalFee() {
        int baseFee = getPrincipalFee();
        return calculator.getTotalFee(baseFee);      // pass across the pinch point
    }
}
```

`getPrincipalFee` is *kept* in `Reservation` even though it'd "align names" better in `FeeCalculator`, because it depends on too many `Reservation` variables — design pragmatism over purity.

## Worked Example

**The `RuleParser` excavation** — applying the heuristics end to end.

A class that evaluates strings of rule expressions. Walking the heuristics:

- **#5 Primary responsibility / name:** the name says "parses," but it also clearly *evaluates* — already more than one sentence.
- **#1 Group Methods + #2 Hidden Methods:** only two public methods, `evaluate` and `addVariable`; everything else private. The `*Expression` methods (`branchingExpression`, `causalExpression`, `variableExpression`, `valueExpression`) all take `Node`s and return `int` — one group: **expression evaluation**. `nextTerm` / `hasMoreTerms` form another group — a special **term tokenization**.
- **#4 Internal relationships:** the `variables` field and `addVariable` method obviously belong together — **variable management**. The `current` string and `currentPosition` belong with the tokenizing methods.

Four responsibilities surface: **Parsing, Expression evaluation, Term tokenization, Variable management.**

**The key insight from Heuristic #2:** making `nextTerm`/`hasMoreTerms` public *on `RuleParser`* would be bizarre — clients would think they must call them to evaluate. But the same methods are *perfectly natural as public methods on a `TermTokenizer` class*, accessed privately from inside the parser. Extracting them makes the design *more* encapsulated, not less.

**Now the test-free extraction of `TermTokenizer`:** we must move `current`, `currentPosition`, `hasMoreTerms`, `nextTerm`. They're private, so we can't write tests directly against them. Two options: make them public (we're moving them anyway), or — easier — instantiate a `RuleParser` in a test harness and feed it a set of strings to evaluate; those **characterization tests** cover `hasMoreTerms`/`nextTerm` indirectly, letting us move them safely. (If `RuleParser` won't instantiate in a harness — common — Chapter 9's seam techniques apply; if the methods won't run, Chapter 10's.)

With tests covering the behavior, run the conservative Extract Class steps: group the four members into a separate declaration section, extract method bodies into `MOVING_hasMoreTerms` / `MOVING_nextTerm` (Preserve Signatures), text-search `RuleParser` and subclasses to confirm `current`/`currentPosition` aren't used elsewhere (no Lean on the Compiler here — watch for shadowing), move everything to `TermTokenizer`, instantiate it inside `RuleParser`, lean on the compiler to fix call sites, then strip the `MOVING_` prefixes. `RuleParser` stops growing; tokenization now lives — and can grow — on its own focused class.

## Key Takeaways

- Stop the growth *first* with **Sprout Class / Sprout Method**; design the breakup *second*. Tactics buy time for strategy.
- Responsibilities are **discovered, not invented** — run the 7-heuristic checklist over the class.
- Lead with **#5 Primary Responsibility** (one sentence) and **#1 Group Methods**; reach for **feature sketches** (#4) to find clusters and **pinch points** when method names aren't enough.
- A pile of **private/protected methods** signals a class trying to escape; "I want to test a private method" means it belongs elsewhere.
- Apply **SRP at the implementation level first** (delegate to extracted classes / facade), interface level later (needs client tests).
- You *can* extract a class **without tests** via the conservative `MOVING`-prefix procedure — but never Lean on the Compiler to track variables (shadowing), and pair up.
- **Lean on the Compiler** for moving methods and finding call sites; distrust it around inheritance (overrides + shadowed variables).
- Use **Interface Sniffing / ISP** to give each client its own slice of a big class and to eventually whittle the monolith's public interface down.
- Break classes down **as-needed**, not in a binge. The existing structure *works*; move it in a better direction, not toward a castle in the sky.

## Connects To

- **Ch 6 (Sprout/Wrap)** — Sprout Class & Sprout Method are the tactical openers cited here.
- **Ch 8 (How Do I Add a Feature?)** — SRP and responsibility-finding feed Open/Closed and clean feature placement.
- **Ch 9 (Can't Get This Class into a Test Harness)** & **Ch 10 (Can't Run This Method)** — prerequisites for getting the characterization tests that make Extract Class safe.
- **Ch 11 (Changes / effect reasoning)** — effect sketches are the mirror image of this chapter's feature sketches.
- **Ch 12 (Many Changes in One Area)** — where **pinch points** are explored in depth.
- **Ch 13 (Characterization Tests)** — the test style used to pin `RuleParser`'s behavior before extraction.
- **Ch 22 (Monster Method)** — the method-level counterpart; Extract Method here feeds class extraction there.
- **Ch 25 (Dependency-Breaking Techniques)** — Extract Class, Preserve Signatures, Lean on the Compiler, Scratch Refactoring are catalogued there.
- **Fowler, _Refactoring_** — the canonical (test-backed) Extract Class this chapter adapts for the test-free legacy case.
- **The Legacy Code Change Algorithm** (identify change points → find test points → break dependencies → write tests → make changes) — this chapter operates at the "break dependencies / make changes" steps, with the conservative Extract Class as a dependency-breaking move that survives the absence of a seam and enabling point.
