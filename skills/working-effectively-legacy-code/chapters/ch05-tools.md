# Chapter 5: Tools

## Core Idea
Working with legacy code (code without tests) demands a toolkit: an editor/IDE, a build system, automated refactoring tools, mock object libraries, and — above all — a free, language-native testing framework. Tools accelerate the Legacy Code Change Algorithm, but no refactoring tool is a substitute for tests, because not every tool actually preserves behavior.

## Frameworks Introduced
- **xUnit (JUnit, CppUnitLite, NUnit, ...)**: A small, powerful unit-testing harness design — originally written in Smalltalk by Kent Beck, ported to Java by Beck and Erich Gamma — for writing and running tests in the language you develop in.
  - When to use: Almost always. It's the primary tool for sensing and separation in legacy work; use it for unit-sized characterization tests and equally for larger multi-class tests since "xUnit doesn't care how large or small a test is."
  - How: Write tests in your own language; each test runs in isolation; group tests into suites that run and rerun on demand.
- **JUnit**: The preferred Java xUnit harness; subclass `TestCase`, write `void testXXX()` methods containing assertions.
  - When to use: Default for Java examples in the book.
  - How: The runner uses reflection to find `testXXX` methods and creates one separate object per method so tests cannot affect each other; `setUp` runs before and `tearDown` after each test object.
- **CppUnitLite**: Feathers's leaner C++ rewrite of his own CppUnit, using C idioms and only a bare subset of C++ for portability.
  - When to use: C++ legacy work, especially with weak/old compilers lacking templates, STL, or exceptions; used for the book's C++ examples.
  - How: A `TEST(testName, ClassName)` macro builds a static test subclass that self-registers into a static list the runner walks — no reflection, no manual `suite()` boilerplate.
- **NUnit**: xUnit for .NET (C#, VB.NET, any CLR language); close to JUnit but uses attributes (`<TestFixture()>`, `<Test()>`) instead of naming conventions to mark classes and methods.
- **FIT (Framework for Integrated Tests)**: Ward Cunningham's acceptance-test framework; embeds input/output tables in HTML documents, runs them as tests, and emits the same HTML with cells colored green (pass) or red (fail).
  - When to use: Integrated/acceptance testing across several classes, and to let non-programmers specify behavior executably — the domain beyond unit-sized xUnit tests.
  - How: Customize table-handling fixture code to invoke your code and retrieve results; the framework supplies code for common table types.
- **FitNesse**: FIT hosted in a wiki (mostly by Robert and Micah Martin); hierarchical pages of FIT tables runnable individually or in suites, geared toward team collaboration. Free.

## Key Concepts
- **Legacy code**: Code without tests — the condition every tool in this chapter exists to remedy.
- **Refactoring**: A change to internal structure that makes code easier to understand and cheaper to modify *without changing existing behavior* (Fowler's definition).
- **Behavior preservation**: The cardinal rule — a change is a refactoring *only* if it doesn't change behavior; trustworthy tools verify this, fringe tools may not.
- **Mock object**: An object substituted for a real dependency that supplies the right values during a test, enabling sensing and separation when you break dependencies.
- **Sensing vs separation**: We break dependencies either to *sense* values our code computes or to *separate* code so it can run at all in a harness — mocks and xUnit serve both.
- **Test in isolation**: xUnit's guarantee that each test runs against its own fresh objects so tests cannot contaminate one another.
- **`setUp` / `tearDown`**: Methods run before/after each test object, allocating shared fixtures lazily (saving resources and allowing setup failures to be detected and reported).
- **Reflection**: Java capability that lets JUnit discover and invoke test methods automatically; C++'s lack of it forced CppUnit's manual registration and CppUnitLite's macro trick.
- **Characterization test**: A test written to pin down what legacy code actually does (chapter 13) — xUnit is the harness you write these in.

## Mental Models
- Think of an automated refactoring tool as a fast hand that doesn't always check its work — trust it only after you've put its Extract Method through sanity checks (e.g., does it flag colliding or base-class method names?).
- Use tests *before* automated refactoring when you can't prove what the tool checks; use tool-only refactoring chains only when you go straight from one safe automated refactoring to another with no manual edits between.
- Think of the UI as the worst place to write tests: volatile, far from the functionality, and hard to diagnose when red — push tests down to xUnit instead.
- Use FIT/FitNesse when the *specifiers* and *developers* need one shared, executable, always-current view of system behavior; use xUnit when programmers test in code.

## Anti-patterns
- **Trusting a refactoring tool that doesn't verify behavior**: You introduce subtle bugs silently; if your tool's refactorings don't preserve behavior, don't use them — work as if you had no tool, which is safer.
- **Skipping tests because "the tool is automated"**: Tools only guard the transformation, not surrounding edits — the `getValue()`/`alpha` example proves a "safe" refactoring can change behavior.
- **Buying expensive per-seat GUI/web testing tools**: Seductive ("test through the GUI with no app changes") but usually more work than admitted, and brittle; the most effective harnesses are free (xUnit, FIT, FitNesse).
- **CppUnit-style manual registration**: Declaring a method in a header, defining it in source, *and* registering it in a `suite()` kills test-writing momentum.

## Code Examples *(include if present in chapter)*
```java
public void doSomething() {
    int v = getValue();           // getValue() increments alpha and returns 12
    int total = 0;
    for (int n = 0; n < 10; n++) { total += v; }
}
// After "remove temp v" refactoring:
for (int n = 0; n < 10; n++) { total += getValue(); }  // alpha now incremented 10x
```
- **What it demonstrates**: An automated refactoring that does *not* preserve behavior — why you want tests around code before refactoring it.

```cpp
TEST(testNormalPay, Employee) {
    auto_ptr<Employee> employee(new Employee("Fred", 0, 10));
    LONGS_EQUAL(400, employee->getPay());
}
```
- **What it demonstrates**: CppUnitLite's `TEST` macro and `LONGS_EQUAL` assertion — a whole self-registering C++ test in one source file, no header/suite boilerplate.

## Reference Tables

| Harness | Platform/Language | Distinguishing trait |
|---|---|---|
| JUnit | Java | `TestCase` subclass, `testXXX()` via reflection |
| CppUnit | C++ | Manual `suite()` registration; needs templates/STL |
| CppUnitLite | C++ | `TEST` macro, static self-registration, bare-subset C++ |
| NUnit | .NET (C#, VB.NET) | `<TestFixture()>` / `<Test()>` attributes |
| (other) xUnit ports | most major + niche languages | spec, group, run unit tests |

(The de facto repository of xUnit ports is Ron Jeffries's www.xprogramming.com Downloads section.)

## Worked Example
The book walks through JUnit's "sneaky" runner with `EmployeeTest`. `setUp` builds an `Employee("Fred", 0, 10)` and adds one 40-hour `TimeCard`. JUnit reflects over the class, finds `testOvertime` and `testNormalPay`, and creates *two separate `FormulaTest`/`EmployeeTest` objects* — one per method. Before each runs, that object's own `setUp` rebuilds a fresh employee. `testNormalPay` asserts `getPay() == 400` against the single timecard; `testOvertime` adds a second 50-hour card and asserts `hasOvertimeFor(...)` is true. Because each test owns its objects, neither can corrupt the other — and lazy `setUp` (vs. a constructor) conserves resources across the large set of test objects and lets setup failures be detected and reported.

## Key Takeaways
1. Legacy code is code without tests; the testing harness — not the IDE — is the indispensable legacy tool.
2. A change is a refactoring only if behavior is unchanged; verify your tool actually checks this, and fall back to manual, tested refactoring when it doesn't.
3. Automated refactoring without tests is only safe across chains of trusted refactorings with no manual edits between.
4. Mock objects let you break dependencies and still feed correct values, enabling sensing and separation.
5. xUnit's power is simplicity and isolation: tests in your own language, each in its own object, grouped into rerunnable suites.
6. Choose the harness that fits the language's features (reflection in Java/JUnit; macros/static registration in C++/CppUnitLite; attributes in .NET/NUnit).
7. FIT and FitNesse extend testing to multi-class, document-driven acceptance tests that bridge specifiers and developers.

## Connects To
- **Ch 1 (Changing Software)**: Tools execute the four reasons to change while preserving behavior — refactoring relies on the behavior-preservation rule stated here.
- **Ch 2 (Sensing and Separation)**: Mocks and xUnit are the concrete tools for sensing values and separating code under test.
- **Ch 4 (The Seam Model)**: You exploit seams at their enabling points by substituting mocks and running the result in an xUnit harness.
- **Ch 13 (characterization tests) & Ch 6 (the Legacy Code Change Algorithm)**: xUnit is where you write the tests in steps 4-5 (write tests, then make changes and refactor).
