# Patterns & Techniques — Working Effectively with Legacy Code

Concrete, named techniques. Dependency-breaking techniques are catalogued in full in [ch25](chapters/ch25-dependency-breaking-techniques.md); this file is the quick index plus the non-catalog techniques.

## Core Algorithm

## The Legacy Code Change Algorithm (Ch 2)
**When**: any change to code without tests.
**How**: 1) Identify change points → 2) Find test points → 3) Break dependencies → 4) Write tests → 5) Make changes and refactor.
**Trade-off**: slower than Edit-and-Pray up front; pays back as tested "islands" grow.

## Feature-Addition Techniques (Ch 6, 8)

## Sprout Method / Sprout Class
**When**: must add behavior to code you can't get under test now.
**How**: write the new logic as a new, TDD-tested method (Sprout Method) or new class (Sprout Class when you can't instantiate the source class); call it from the untested code.
**Trade-off**: the call site stays untested; leaves the source class in limbo until you return.

## Wrap Method / Wrap Class
**When**: add behavior *around* (before/after) existing work without growing or modifying it.
**How**: Wrap Method — rename the old method, create a same-signature method that calls new behavior + the renamed old one. Wrap Class — new class (often a Decorator) takes the wrapped object and augments selected methods.
**Trade-off**: can force awkward names (Wrap Method); stacked decorators get onion-like (Wrap Class).

## Test-Driven Development (Ch 8)
**When**: adding a feature to legacy code once a test point exists.
**How**: write a failing test → make it compile → make it pass (quickly, even ugly) → remove duplication → repeat.
**Trade-off**: needs the class testable first; pairs with dependency-breaking.

## Programming by Difference (Ch 8)
**When**: you need a feature fast and a subclass can express the difference.
**How**: subclass and add/override to get the behavior under test; then refactor the inheritance away (toward composition) to avoid LSP violations and subclass explosion.
**Trade-off**: temporary inheritance is a means, not the end.

## Comprehension Techniques (Ch 16, 17)

## Scratch Refactoring
**When**: you don't understand the code well enough to change it.
**How**: refactor freely **without tests** just to learn the structure — then **throw it away** (revert). The output is understanding, not committed code.
**Trade-off**: none if you discard it; dangerous only if you keep it.

## Notes/Sketching, Listing Markup
**When**: tracing responsibilities/structure in unfamiliar code.
**How**: draw what you read; print the listing and mark up responsibilities, blocks, and method boundaries.

## Telling the Story of the System / Naked CRC (Ch 17)
**When**: the application has no discernible structure.
**How**: explain the architecture simply (real vs ideal) to a colleague; model designs with bare CRC index cards before coding.

## Reasoning Techniques (Ch 11, 12)

## Effect Sketch + Pinch Point
**When**: deciding what to test for a change.
**How**: sketch how the change's effects propagate (returns, params, fields, globals); find interception points where effects are observable; locate a pinch point (narrow waist) where one higher-level test covers many classes. Start there, then drive tests down to unit level.
**Trade-off**: pinch-point tests can grow into mini-integration tests — break them down once units are testable.

## Monster-Method Techniques (Ch 22)

## Introduce Sensing Variable · Extract What You Know · Break Out Method Object
**When**: a method is too big to test, can't write tests first.
**How**: classify it (Bulleted vs Snarled). Add a sensing variable to observe internal state; extract the smallest well-understood pieces first; lean heavily on **automated refactoring tools**; if the class blocks you, Break Out a Method Object. Preserve indentation as a structural guide.
**Trade-off**: extracted pieces may expose internals until tests exist.

## Safety Techniques (Ch 23)

## Lean on the Compiler
**When**: breaking dependencies and you need to find every affected site.
**How**: change a declaration to deliberately break compilation; the error list becomes your worklist; fix each; remove the deliberate break.
**Trade-off**: only works for statically-typed languages and type-visible changes.

## Preserve Signatures · Single-Goal Editing · Hyperaware Editing
**When**: editing without (or with thin) tests.
**How**: cut-and-paste whole signatures verbatim to avoid typos; change one thing at a time; pair-program / use TDD to stay aware of mistakes as they happen.

## Library / API Techniques (Ch 14, 15)

## Skin and Wrap the API vs Responsibility-Based Extraction
**When**: code is dominated by third-party API calls.
**How**: **Skin and Wrap** — thin interface you own wrapping the API (good when the API is small/stable). **Responsibility-Based Extraction** — pull the responsibilities around the API into your own classes (better when the API is large).
**Trade-off**: wrapping is more code to maintain but maximally fakeable; extraction is more design work but better long-term structure.

## Dependency-Breaking Catalog (Ch 25) — index

Pick by obstacle (full entries + decision table in ch25):

| Obstacle | Technique(s) |
|---|---|
| Un-fakeable constructor param | Extract Interface, Adapt Parameter |
| Object `new`-ed in constructor | Parameterize Constructor, Extract and Override Factory Method, Extract and Override Getter (C++), Supersede Instance Variable (C++) |
| Object created in a method | Parameterize Method |
| Single side-effecting call | Extract and Override Call, Subclass and Override Method |
| Many bad methods on one object | Extract and Override Getter |
| Global / Singleton dependency | Introduce Static Setter, Encapsulate Global References, Replace Global Reference with Getter |
| Static utility to swap | Introduce Instance Delegator, Expose Static Method |
| Long method, class not instantiable | Break Out Method Object, Expose Static Method |
| Good methods trapped with bad deps | Pull Up Feature |
| Pervasive bad deps | Push Down Dependency |
| Class absurdly costly to instantiate | Primitivize Parameter (last resort) |
| Interface name already taken | Extract Implementer |
| C function dependency | Link Substitution, Definition Completion, Replace Function with Function Pointer |
| C++ template dependency | Template Redefinition |
| Ruby / interpreted | Text Redefinition |
