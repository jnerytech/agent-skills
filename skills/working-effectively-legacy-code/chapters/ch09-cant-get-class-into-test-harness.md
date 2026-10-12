# Chapter 9: I Can't Get This Class into a Test Harness

## Core Idea

This is the hard chapter. The whole reason legacy code resists change is that you often can't get a single instance of a class into a test harness. Feathers reduces the misery to four recurring obstacles to instantiation:

1. **Objects of the class can't be created easily.**
2. **The test harness won't easily build** with the class in it.
3. **The constructor we need has bad side effects** (talks to a server, a database, the file system, sends real mail).
4. **Significant work happens in the constructor** and we need to *sense* it.

The chapter is a catalog: each "Case" names an obstacle and pairs it with one or more dependency-breaking techniques. The unifying advice is brutally simple — **just try to instantiate it.** Write a *construction test* (a test with no assertion that only news up the object), compile it, and let the compiler enumerate exactly what stands in your way. From there you introduce a **seam** with an **enabling point**, drop in a **fake**, and you can finally **sense** behavior or **separate** the class from its environment. Remember the operating definition the whole book runs on: **legacy code = code without tests.** This chapter is how you make untestable code testable enough to write the first characterization test.

## Frameworks Introduced

Organized as **obstacle → technique**:

- **"I have an irritating parameter"** (a constructor arg that's expensive/dangerous to build, e.g. a live `RGHConnection`) → **Extract Interface** on the parameter's class, implement a fake; or **Pass Null** if the param is unused in the test; or **Subclass and Override Method** if the bad behavior (e.g. `connect()`) isn't hard-wired into the constructor.
- **"I have a hidden dependency"** (constructor news-up a resource internally, e.g. `mail_service` in the initializer list) → **Parameterize Constructor** — externalize the dependency by passing it in, then keep a no-arg constructor that delegates so existing clients don't change. Also available: **Extract and Override Getter**, **Extract and Override Factory Method**, **Supersede Instance Variable**.
- **"Construction is a blob"** (constructor builds objects that build objects; the thing you want to sense, e.g. `cursor`, is buried mid-blob) → **Supersede Instance Variable** — add a setter to swap the instance in *after* construction. Reserve it: in C++ it raises resource/destructor hazards; prefer **Extract and Override Factory Method** where the language allows (Java/C#, not C++ constructors).
- **"I have an onion parameter"** (to build the param you must build another object, and another...) → find the innermost class that needs no collaborators; **Pass Null** if you need nothing from the params, or **Extract Interface / Extract Implementer** on the most immediate dependency and feed a fake.
- **"I have an aliased parameter"** (the param sits in a class hierarchy assigned to a base-class field, so extracting interfaces would cascade interfaces all the way down) → don't sever the whole class; **Subclass and Override Method** to neutralize only the offending method (e.g. override `validate()` so it skips the database).
- **Irritating global / singleton dependency** (constructor calls `Singleton.getInstance()`) → **Introduce Static Setter** — add `setTestingInstance()` to relax the singleton property; or add `resetForTesting()`; subclass the singleton to override DB-touching methods. To actually *remove* the global later: **Parameterize Method** / **Parameterize Constructor**.
- **Horrible include dependencies (C++)** → put the test in the same directory, add `#include`s one at a time, and supply alternative (fake) definitions for hard methods in a `Fakes.h`, building a separate test program. A heavy, last-resort technique.

## Key Concepts

- **Construction test** — a throwaway test whose only job is to `new` the object. No assertion. Once it compiles and runs, rename or discard it. The compiler is your worklist generator.
- **Sensing vs. separation** — two reasons to break a dependency. *Sensing*: you can't see effects your code has on other objects, so you fake the collaborator to detect calls. *Separation*: you can't even get the code into the harness, so you fake to detach it from its environment. Most cases here are about separation that also unlocks sensing.
- **Fake object** — a stand-in with empty/`null`-returning methods and public fields, used only under test. It legitimately violates encapsulation rules because it is never production code.
- **Seam + enabling point** — the place where you can alter behavior without editing in place (the parameter, the overridable method, the swappable instance variable) plus the spot where you choose which behavior runs (the constructor arg, the subclass, the static setter).
- **Test code vs. production code** — test code may break encapsulation (public fields, `null` args) but must stay clean and DRY; pull duplicated setup into `setUp()`.
- **Characterization test** — the real test you write *after* instantiation is possible, pinning down current behavior so you can change safely.
- **Legacy Code Change Algorithm** — identify change points → find test points → break dependencies → write tests → make changes/refactor. This chapter is overwhelmingly the *break dependencies* step.

## Mental Models

- **"Just try it."** Don't analyze whether instantiation will be hard — attempt it. The build errors are a precise, free spec of your obstacles.
- **The onion has a center.** No matter how deep the constructor-needs-an-object recursion goes, at least one class takes no object args — otherwise the system would never have compiled. Find it and work outward.
- **Singletons are a testing-time conflict, not a law.** The single-instance guarantee exists for a reason (real-world uniqueness, catastrophic duplicates, resource cost) — or, more often, just to dodge passing a variable around. Each test should be a "mini-application," fully isolated, so *relax* the singleton for tests and protect uniqueness with team rules, build checks, or runtime alarms instead.
- **Severing a whole class is a blunt instrument.** Extract Interface cuts everything. If only one method misbehaves (touches the DB, sends mail), subclass and override just that method — cut the wire, not the cable.
- **Pass Null is a probe.** Passing `null` and watching for an exception tells you whether a parameter is even used in your test path.

## Anti-patterns

- **`null` in production code** — Pass Null belongs in tests only. In production, prefer the **Null Object Pattern** (`NullEmployee` that pays nothing) over scattering `null` checks. Beware: null objects are only safe when the client doesn't care whether the operation succeeded (the "count paid employees" loop breaks silently).
- **Construction blobs** — constructors that create objects to create objects, mixing wiring with logic. They force Supersede Instance Variable or worse.
- **Singletons-as-global-variables** — opacity: you can't tell what a class touches. Most singletons exist only to avoid passing an argument and don't deserve the single-instance lock.
- **Supersede Instance Variable in C++ without care** — `delete`-ing the old object can double-free things passed to its constructor; superseding objects that own resources leaks them. Never use the superseding setter in production.
- **Include-everything-until-it-builds (C++)** — transitive includes drag in tens of thousands of lines and untestable classes; add includes deliberately, one at a time.
- **One interface per class** — extracting interfaces "all the way down" an aliased hierarchy clutters the design into near 1:1 class/interface pairs. A last resort, not a default.

## Code Examples

**Parameterize Constructor with a safe delegating overload (C++):** externalize the hidden `mail_service`, keep the old signature.

```cpp
void mailing_list_dispatcher::initialize(mail_service *service) {
    status = MAIL_OKAY;
    const int client_type = 12;
    service->connect();
    if (service->get_status() == MS_AVAILABLE) {
        service->register(this, client_type, MARK_MESSAGES_OFF);
        service->set_param(client_type, ML_NOBOUNCE | ML_REPEATOFF);
    } else status = MAIL_OFFLINE;
}
mailing_list_dispatcher::mailing_list_dispatcher(mail_service *service)
    { initialize(service); }                 // tests call this
mailing_list_dispatcher::mailing_list_dispatcher()
    { initialize(new mail_service); }         // clients unchanged
```

In Java/C# this is even cleaner via constructor chaining: `public MailingListDispatcher() : this(new MailService()) {}`.

**Introduce Static Setter on a singleton:**

```java
public class PermitRepository {
    private static PermitRepository instance = null;
    protected PermitRepository() {}          // relaxed from private
    public static void setTestingInstance(PermitRepository newInstance) {
        instance = newInstance;
    }
    public static PermitRepository getInstance() {
        if (instance == null) instance = new PermitRepository();
        return instance;
    }
    public Permit findAssociatedPermit(PermitNotice notice) { ... }
}
```

Then in `setUp()`, build a `TestingPermitRepository` subclass that overrides `findAssociatedPermit` to read from an in-memory map and call `PermitRepository.setTestingInstance(repository)`.

## Worked Example

**The Case of the Irritating Parameter — `CreditValidator`.** Mission: add `getValidationPercent()` to a billing class whose simplest constructor is `CreditValidator(RGHConnection, CreditMaster, String)`.

1. **Construction test.** Write `new CreditValidator()` in a JUnit test. The compiler reports there's no default constructor and demands the three args.
2. **Triage the parameters.** `CreditMaster` loads a small read-only file quickly — harmless. `RGHConnection` opens a real socket to a server that's slow and often down — the *irritating parameter.*
3. **Introduce a seam.** Apply **Extract Interface** to `RGHConnection`, yielding `IRGHConnection`. The production class still connects for real; a `FakeConnection implements IRGHConnection` returns canned reports:

```java
public class FakeConnection implements IRGHConnection {
    public RFDIReport report;
    public void connect() {}
    public void disconnect() {}
    public RFDIReport RFDIReportFor(int id) { return report; }
    public ACTIOReport ACTIOReportFor(int customerID) { return null; }
}
```

4. **Sense through the fake.** Inject the report and assert behavior:

```java
void testAllPassed100Percent() throws Exception {
    CreditMaster master = new CreditMaster("crm2.mas", true);
    IRGHConnection connection = new FakeConnection();
    CreditValidator validator = new CreditValidator(connection, master, "a");
    connection.report = new RFDIReport(...);
    validator.validateCustomer(new Customer(...));
    assertEquals(100.0, validator.getValidationPercent(), THRESHOLD);
}
```

5. **Simplify further.** While writing `getValidationPercent`, you notice it never touches `CreditMaster`. So **Pass Null**: `new CreditValidator(connection, null, "a")`. If the test ever uses it, the runtime throws and the harness catches it — fast feedback. (Clean up the duplicated first three lines into `setUp()`.)

The pattern generalizes across every Case: try to construct → let the compiler list obstacles → pick the lightest dependency-breaking technique → fake → sense.

## Key Takeaways

- The fastest diagnosis is an attempt: write a **construction test** and read the build errors.
- Match the technique to the obstacle. **Extract Interface / Pass Null / Subclass and Override Method** for parameters; **Parameterize Constructor** for hidden dependencies; **Supersede Instance Variable** for construction blobs; **Introduce Static Setter** for singletons.
- Reach for the *lightest* tool first — **Parameterize Constructor** over Supersede Instance Variable; **Subclass and Override Method** over interfacing a whole hierarchy.
- Keep the old constructor signature (delegate to an `initialize`/chained constructor) so existing clients never know you changed anything.
- **Fakes** earn the right to break encapsulation; production code does not. Pass Null and superseding setters stay out of production.
- Singleton-ness is a design choice you may relax for testability; protect true uniqueness with rules and checks, not with an untestable private constructor.

## Connects To

- **Ch. 4 (The Seam Model)** — every technique here installs an object seam with an enabling point.
- **Ch. 3 (Sensing and Separation)** — this chapter is mostly separation that unlocks sensing via fakes.
- **Ch. 2 / Ch. 13 (Characterization Tests)** — instantiation is the precondition; characterization tests come right after.
- **Ch. 10 ("I can't run this method in a test harness")** — the sequel: once the object exists, exercise its methods.
- **Ch. 23 / Ch. 25 (technique reference)** — Extract Interface, Parameterize Constructor, Supersede Instance Variable, Pass Null, Introduce Static Setter, Subclass and Override Method, Extract and Override Factory Method/Getter, Extract Implementer, Parameterize Method, Lean on the Compiler all feed `patterns.md`.
- **Ch. 15 / Ch. 17 ("All API Calls" / "No Structure")** — where a genuinely global variable signals missing layering.
- **Legacy Code Change Algorithm** — this chapter is the "break dependencies" step in depth.
