# Chapter 7: It Takes Forever to Make a Change

## Core Idea

Slow change has two distinct causes, and you have to diagnose which one is biting you. The first is **understanding**: as a codebase grows it surpasses anyone's mental model, so figuring out *what* to change takes forever. The second — the focus of this chapter — is **lag time**: the gap between making a change and getting real feedback about it. Feathers' image is the Mars rover *Spirit*: a 7-minute signal delay each way means you act, then wait 14 minutes to see what happened. Most of us develop software exactly this way — bundle a pile of changes, kick off a build, wait, and react. That waiting is almost entirely unnecessary. In nearly every mainstream language you can break dependencies so that any class or module compiles and runs in its own test harness in under 10 seconds. The chapter's central technique: **break compile-time dependencies** by depending on interfaces instead of concrete classes, so that editing one class no longer triggers an avalanche of recompilation across the system.

## Frameworks Introduced

- **The Dependency Inversion Principle (DIP)** — Depend on abstractions, not on concretions. When your code depends on an interface, that dependency is minor and unobtrusive: your code changes only when the *interface* changes, and interfaces change far less often than the code behind them. Depending on less volatile things minimizes the chance that a given edit triggers massive recompilation.
- **Extract Interface** — Pull a named interface out of a concrete class, then redirect external references to the interface. IDE-supported in many languages (pick methods, name the interface, auto-replace references). Preferred in languages like Java/C#.
- **Extract Implementer** — The inverse maneuver, easier in C++. Instead of creating a new name for the interface, you keep the original name *as* the interface and rename the concrete class (e.g. `ConsultantSchedulerDB` becomes the interface, `ConsultantSchedulerDBImpl` the implementation). You avoid renaming references everywhere; you only fix the spots that instantiate the old concrete class.
- **Moving clusters into packages/libraries** — Once a cluster runs under test, relocate it into its own package or library so it compiles and is tested independently of the rest of the system.

## Key Concepts

- **Lag time** — Time between a change and feedback on it. The thing you are actually optimizing.
- **Build avalanche / forced recompilation** — In statically compiled systems (acutely in C++ via header coupling), a change to a concrete class forces every direct dependent to recompile. Concrete-to-concrete dependency chains turn a one-line edit into a full-system rebuild.
- **Compilation firewall** — Once `AddOpportunityFormHandler` depends only on the `ConsultantSchedulerDB` and `OpportunityItem` *interfaces*, you can change `...DBImpl` and `...ItemImpl` freely without recompiling the handler or its users. The interface boundary is the firewall.
- **Whole build vs. average build (the make)** — Adding interfaces and packages slightly *increases* the time for a full from-scratch rebuild (more files), but dramatically *decreases* the average incremental build, because most edits now recompile far fewer files.
- **One-time cost** — Getting a cluster compiling separately and under test is painful once; afterward you reap fast feedback forever.

## Mental Models

- **Mars rover driving** — High lag time forces you to batch and guess; your mind plans, then wanders while it waits. Compress feedback to seconds and the work becomes "like driving rather than waiting at a bus stop" — tighter concentration, mistakes caught and corrected almost immediately.
- **Interfaces as shock absorbers** — Volatile concrete code sits behind a stable interface. Volatility stays local; the rebuild blast radius shrinks to the interface's true change frequency.
- **Two-sided shielding** — Break dependencies on *both* sides of a class: stop it recompiling when its collaborators change (extract interfaces on what it uses), and stop its clients recompiling when it changes (extract an interface on it).

## Anti-patterns

- **Batching changes to avoid building** — Bundling many edits into one big build to amortize lag time. It compounds risk: when you hit an obstacle (a test failure) you go even slower, and you've lost the link between a specific change and its effect.
- **Concrete-on-concrete dependencies** — Constructors that directly `new` up database, hardware, or XML classes. Each forces real resources into the test harness and chains recompilation through implementation code.
- **Treating slow builds as a fact of life** — Accepting minutes-long edit-compile-test cycles in a compiled language when sub-10-second cycles are achievable.
- **Over-rotating on the full-build number** — Refusing to add interfaces because the total rebuild got slightly slower, ignoring that the *average* build (what you pay all day) dropped sharply.

## Code Examples

Extract Implementer, C++-style, on a database-bound dependency:

```cpp
// BEFORE: handler depends on a concrete class that hits the DB
class AddOpportunityFormHandler {
public:
  AddOpportunityFormHandler(ConsultantSchedulerDB *db, ...);
  // any edit to ConsultantSchedulerDB's .cpp forces this to recompile
};

// AFTER: ConsultantSchedulerDB becomes a pure interface
class ConsultantSchedulerDB {        // now an interface
public:
  virtual ~ConsultantSchedulerDB() {}
  virtual int getNextAvailableSlot(...) = 0;
  virtual void bookSlot(...) = 0;
};

class ConsultantSchedulerDBImpl : public ConsultantSchedulerDB {
  // the real, database-touching implementation lives here
};
```

In a test, you now construct the handler with a **fake** that implements the interface — no database connection, fast link, fast run:

```cpp
class FakeConsultantSchedulerDB : public ConsultantSchedulerDB {
public:
  int getNextAvailableSlot(...) override { return 1; }  // canned answer
  void bookSlot(...) override { booked = true; }        // sensing
  bool booked = false;
};

// AddOpportunityFormHandler handler(new FakeConsultantSchedulerDB(), ...);
```

## Worked Example

Feathers' running example is the opportunity-handling cluster (Figures 7.1–7.5). The goal: change `AddOpportunityFormHandler` *and* make builds faster.

1. **Try to instantiate it.** `AddOpportunityFormHandler` needs a `ConsultantSchedulerDB` and an `AddOpportunityXMLGenerator`, all concrete, possibly dragging in unseen classes. You can't tell how many objects you'd really construct — the dependency that blocks the test harness is the first one to break.
2. **Extract Implementer on `ConsultantSchedulerDB`.** It becomes an interface; the real class is `ConsultantSchedulerDBImpl`. Now the handler can be created in a test with a fake DB — no real database. Bonus: editing `...DBImpl` no longer recompiles the handler, because the handler depends only on the interface.
3. **Extract Implementer on `OpportunityItem`.** Yielding `OpportunityItemImpl`. Now the handler depends on *neither* concrete implementation — a "compilation firewall." Changes to both `...DBImpl` and `...ItemImpl` recompile neither the handler nor its users.
4. **Refactor packages.** Move the interface-facing classes into an `OpportunityProcessing` package that has *no* dependency on the database implementation. Tests placed there compile and run fast and don't rebuild when DB code changes.
5. **Shield the clients too.** `AddOpportunityFormHandler` is the lone public production class in the package. Apply Extract Interface (or Extract Implementer) to *it* as well; classes in other packages then depend on its interface, so most changes to the handler no longer force them to recompile.

Net result: the full-system rebuild grew a little (more files), but the average incremental make dropped dramatically — and this corner of the code is now fast to work in, permanently.

## Key Takeaways

- Diagnose slowness as **understanding** vs. **lag time**; this chapter attacks lag time.
- Aim for a sub-10-second edit-compile-link-test loop; every class should compile separately in its own test harness.
- **Break dependencies by depending on interfaces** (Extract Interface / Extract Implementer) — apply the **Dependency Inversion Principle**.
- Shield **both sides**: protect a class from its collaborators' changes and protect its clients from the class's changes.
- The interface boundary doubles as the **seam's enabling point**: it's where you swap in a **fake/mock** to test without real resources.
- Full-build time rises slightly; **average build time** falls sharply. That trade is worth it.
- The cost is paid once per cluster; the fast feedback is yours forever.

## Connects To

- **Ch. 4 (The Seam Model)** — Each extracted interface is an object seam; the constructor/parameter where you pass the fake is its **enabling point**. Faking the DB is **separation** (getting the class to run at all); asserting on the fake's recorded calls is **sensing**.
- **Ch. 2 / Ch. 13 (Sensing & Separation, the Legacy Code Change Algorithm)** — Breaking these dependencies is the "break dependencies → write tests" core of the algorithm; with **legacy code = code without tests**, this is how you earn the **characterization tests** that make change safe.
- **Ch. 9 & 10 (Get a class / method into a test harness)** — Hands-on techniques when instantiation is the wall.
- **Ch. 12 (Many changes in one area / pinch points)** — Where to put larger chunks under test efficiently.
- **Ch. 16 & 17 (Understanding, structure)** — The other half of "forever": comprehension and missing architecture.
- **External: Robert C. Martin, _Agile Software Development: Principles, Patterns, and Practices_** — fuller treatment of DIP and interface/package dependency management.
