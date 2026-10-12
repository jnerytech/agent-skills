# Glossary — Working Effectively with Legacy Code

**Adapt Parameter** — break a dependency by giving a method a new narrow interface instead of a fat/library parameter type you can't fake (Ch 25).
**Break Out Method Object** — move a long method into a new class so it can be tested without instantiating its original class (Ch 22, Ch 25).
**Bulleted Method** — a monster method made of sequential chunks with little indentation; relatively easy to extract (Ch 22).
**Characterization Test** — a test that documents the *actual current behavior* of code (not intended behavior), written to pin behavior before changing it (Ch 13).
**Change Point** — the place in code where you must make a modification (Ch 2, Ch 11).
**Cover and Modify** — change software under a safety net of tests; opposite of Edit and Pray (Ch 2).
**Decorator** — transparent Wrap Class form: same interface, holds an instance, delegates, augments selected methods; nestable (Ch 6).
**Definition Completion** — C/C++ technique: include a header, drop the real source, supply alternate definitions in the test file (Ch 25).
**Dependency** — reliance on other code that makes a class hard to instantiate, run, or sense in isolation; the central obstacle in legacy work (Ch 2).
**Dependency Inversion Principle** — depend on abstractions (interfaces), not concretions, to cut compile-time coupling (Ch 7).
**Edit and Pray** — plan carefully, change code, then poke around hoping nothing broke; the unsafe industry default (Ch 2).
**Effect Sketch (Effect Graph)** — a drawing of how a change propagates through return values, params, fields, and globals, used to decide where to test (Ch 11).
**Enabling Point** — the place where you decide which behavior a seam uses; every seam has one (Ch 4).
**Encapsulate Global References** — bundle scattered globals into a class so they can be replaced under test (Ch 25).
**Expose Static Method** — extract a no-instance-data method as a public static so it can be tested without instantiating the class (Ch 25).
**Extract and Override Call** — replace a single side-effecting call with a local overridable method (Ch 10, Ch 25).
**Extract and Override Factory Method** — move a constructor's `new` into a protected method a test subclass overrides (not C++) (Ch 9, Ch 25).
**Extract and Override Getter** — lazy getter for a constructor-created object; subclass overrides it (C++ workaround / many bad methods) (Ch 9, Ch 25).
**Extract Implementer** — make the original class an interface and move its body to a `Production…` class when the interface name is taken (Ch 25).
**Extract Interface** — create an interface a class implements so collaborators can be faked; one of the safest techniques (Ch 7, Ch 25).
**Fake Object** — an object that impersonates a collaborator and records what happened, for sensing (Ch 3).
**FIT / FitNesse** — Framework for Integrated Tests; table-driven acceptance testing tools (Ch 5).
**Gleaning Dependencies** — extract/identify the dependencies a monster method relies on before restructuring it (Ch 22).
**God Class** — an oversized class with too many responsibilities (Ch 20).
**Higher-Level Test** — a test covering several classes/scenarios at once, used as a cover before unit-testing them (Ch 11, Ch 12).
**Hyperaware Editing** — editing with enough awareness (pairing, TDD) to notice mistakes as you make them (Ch 23).
**Interception Point** — a place where you can sense an effect of a change to write a test (Ch 11, Ch 12).
**Introduce Instance Delegator** — add an instance method that delegates to a static, creating an object seam (Ch 25).
**Introduce Sensing Variable** — add a temporary variable to a monster method to observe internal state under test (Ch 22).
**Introduce Static Setter** — add a static setter so a global/Singleton instance can be replaced by a fake (Ch 9, Ch 25).
**Lean on the Compiler** — deliberately introduce a compile error (e.g. change a declaration) and use the error list to find every place to change (Ch 23, Ch 25).
**Legacy Code** — code without tests (the book's working definition); code you can't change confidently (Intro).
**Legacy Code Change Algorithm** — 1) identify change points, 2) find test points, 3) break dependencies, 4) write tests, 5) make changes and refactor (Ch 2).
**Legacy Code Dilemma** — to change code safely you need tests; to get tests you often must change code first (Ch 2).
**Link Seam** — substitute behavior at link/classpath time; enabling point is the build script (Ch 4, Ch 19).
**Link Substitution** — replace functions/libraries via a dummy library linked in place of production (Ch 19, Ch 25).
**Liskov Substitution Principle (LSP)** — subtypes must be usable wherever their base type is expected (Ch 8).
**Mock Object** — a fake that performs assertions internally via preset expectations and `verify()` (Ch 3).
**Monster Method** — a method so large/complex it resists testing; Bulleted or Snarled (Ch 22).
**Naked CRC** — Class-Responsibility-Collaboration modeling with bare index cards (Ch 17).
**Object Seam** — vary which method a call dispatches to without editing the call; the preferred OO seam (Ch 4).
**Open/Closed Principle** — code should allow adding behavior without modifying existing code (Ch 21).
**Parameterize Constructor** — pass an internally-created object into the constructor instead of `new`-ing it (Ch 9, Ch 25).
**Parameterize Method** — pass an internally-created object into a method instead of creating it (Ch 25).
**Pay Me Now or Pay Me Later** — testing/dep-breaking costs time today but saves more later, especially as changes cluster (Ch 6).
**Pinch Point** — a narrow interception point where one test exercises many classes; a natural place to start testing (Ch 11, Ch 12).
**Preprocessing Seam** — C/C++ seam via `#define`/`#include`; enabling point is a preprocessor symbol like `TESTING` (Ch 4, Ch 19).
**Preserve Signatures** — copy whole parameter lists/signatures verbatim when breaking dependencies to avoid mistakes (Ch 23, Ch 25).
**Primitivize Parameter** — do work in a free function over a simplified representation when a class is too costly to instantiate (Ch 2, Ch 25).
**Programming by Difference** — use inheritance to add a feature quickly, then refactor the inheritance away (Ch 8).
**Pull Up Feature** — move a cluster of wanted methods into an abstract superclass, away from bad deps, to test them (Ch 25).
**Push Down Dependency** — make the class abstract and push pervasive bad deps into a production subclass; test via a testing subclass (Ch 25).
**Replace Function with Function Pointer** — C technique: swap a function via a reassignable pointer for tests (Ch 25).
**Replace Global Reference with Getter** — wrap a global access in an overridable getter (Ch 25).
**Responsibility-Based Extraction** — extract the responsibilities your code performs around a large API into your own classes (Ch 14, Ch 15).
**Scratch Refactoring** — refactor freely *without* tests purely to understand code, then throw it away (Ch 16).
**Seam** — a place where you can alter behavior without editing in that place (Ch 4).
**Sensing** — breaking dependencies to observe effects/values your code computes that you otherwise can't access (Ch 3).
**Separation** — breaking dependencies to get a piece of code to run outside production at all (Ch 3).
**Single Responsibility Principle (SRP)** — a class should have one reason to change / one responsibility (Ch 20).
**Single-Goal Editing** — do one thing at a time when editing to avoid mistakes (Ch 23).
**Skin and Wrap the API** — wrap a third-party API behind a thin interface you own and can fake (Ch 14, Ch 15).
**Snarled Method** — a monster method that is one deeply-nested tangled mass; harder than a Bulleted Method (Ch 22).
**Software Vise** — tests that fix behavior in place so you change only what you intend (Ch 2).
**Sprout Class** — put new behavior in a new tested class called from untested code, when you can't instantiate the source class (Ch 6).
**Sprout Method** — put new behavior in a new tested method called from untested code (Ch 6).
**Subclass and Override Method** — the core OO dependency-breaking move: override methods in a testing subclass to null or sense behavior (Ch 10, Ch 25).
**Supersede Instance Variable** — C++ method to swap an instance variable created in the constructor with a sensing object (Ch 9, Ch 25).
**Telling the Story of the System** — explain a system's architecture simply to surface real vs ideal structure (Ch 17).
**Template Redefinition** — C++ technique using templates + typedef to substitute a dependency type under test (Ch 25).
**Temporal Coupling** — grouping operations only because they happen at the same time; Wrap Method avoids it (Ch 6).
**Test Harness** — code that exercises software plus the code needed to run it (e.g. xUnit, FIT) (Ch 2, Ch 5).
**Test Point** — a place where you can write a test for a change (Ch 2, Ch 11).
**Test-Driven Development (TDD)** — write a failing test, make it compile, make it pass, remove duplication; repeat (Ch 8).
**Text Redefinition** — Ruby/interpreted technique: reopen a class in the test to redefine methods (Ch 25).
**Unit Test** — an isolated test of an atomic unit (class/function) that runs fast and localizes errors; not a unit test if it hits DB, network, filesystem, or needs special env (Ch 2).
**Wrap Class** — add behavior around a class without modifying it, often as a decorator (Ch 6).
**Wrap Method** — add behavior before/after an existing method by renaming it and wrapping the call (Ch 6).
**xUnit** — the family of unit-testing frameworks (JUnit, CppUnit, NUnit, etc.) (Ch 5).
