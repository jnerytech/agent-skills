# Chapter 8: Re-Layering Your Application

## Core Idea
Layering is the first significant architectural rework on a brownfield project: use Interface-Based Design to carve a tangled codebase into logical layers separated by seams, so changes stay local and code becomes testable and reversible. You do this incrementally, one screen at a time, never all at once.

## Frameworks Introduced

- **Tiers vs. Logical Layers**: A *tier* is a physical/deployment boundary (UI machine, app server, DB server — typically one-to-one with hardware). A *logical layer* is a task-based software concern with no knowledge of hardware; many logical layers can live inside one physical tier, and an infrastructure layer can span tiers.
  - When to use: Reason in layers, not tiers, when deciding where granular code (validation, conversion, data access) belongs. Tiers are too coarse to express these separations.
  - How: Within a tier, split focused concerns into their own layers (e.g. a layer that converts web-service objects into your own format, a validation layer, a DAL).
  - Why it works / failure mode: Layers give "a place for everything"; failure mode is treating tier boundaries as sufficient and dumping all "business logic" into one undifferentiated middle tier.

- **Interface-Based Design (isolation & insulation)**: Define the contract between two layers as an interface; consumer and producer then implement independently against the agreed inputs/outputs.
  - When to use: Wherever two layers meet (a seam). Treat each logical layer as if it were a third-party library you're consuming.
  - How: Extract the interaction into an interface; client code references only the interface, not the concrete class. Concrete implementation is supplied later (injected — see Ch 9).
  - Why it works / failure mode: *Isolation* = your code is shielded like a vendor library (your changes don't force the layer to recompile). *Insulation* = a well-understood contract shields the layer from external change. Bonus: reversibility — a well-isolated layer can be replaced wholesale.

- **Anti-Corruption Layer (ACL)**: A custom wrapper exposing only the functionality *your* application needs, delegating internally to a volatile dependency, so changes within that dependency don't ripple into client code.
  - When to use: Most valuable around external dependencies (third-party grid/textbox controls, web services); also internally around areas in constant flux.
  - How: Apply the **Adapter pattern** — create an interface/wrapper designed for your needs, expose the *bare minimum* (e.g. one bind-data method), delegate to the wrapped control. On upgrade, change only the wrapper.
  - Why it works / failure mode: Contains the ripple of an upgrade inside the wrapper instead of across dozens of forms (avoids a DRY violation). Failure mode: exposing the whole chatty third-party surface makes the wrapper brittle and defeats the purpose; and a fundamental change in the wrapped control can't be hidden by a "fuzzy" interface.

- **Domain-Centric Approach**: Refactor toward the actual domain the app models (Consultant, Timesheet, Song, Playlist) rather than around DataSets, services, and servers.
  - When to use: When deciding *where* functionality belongs as you layer; brownfield apps usually have business logic scattered with no real domain.
  - How: Put the Domain at the center; arrows flow *into* it (no strict hierarchy). Domain holds both domain objects and repository *interfaces* (e.g. `IConsultantRepository`); concrete repository implementations live in the data access layer and are wired up via Factory, Service Locator, or (preferred) an IoC container.
  - Why it works / failure mode: Code reads in terms of the business, and the domain is decoupled from database technology. (Drawn from Evans' *Domain-Driven Design* and Nilsson's *Applying DDD and Patterns*.)

## Key Concepts
- **Tier**: A physical deployment boundary, usually mapped to distinct hardware.
- **Logical layer**: A task-focused software concern, hardware-agnostic; multiple can sit in one tier.
- **Seam**: A point of clearly defined decoupling — the interface a layer uses to talk to its neighbour (Feathers' *object seam*: a place to alter behaviour without editing in that place).
- **Contract**: Often synonymous with an interface — the agreed inputs/outputs between consumer and producer.
- **Isolation**: Your app's changes don't affect a layer's internals (encapsulation, restated).
- **Insulation**: A well-understood contract shields a layer from external changes; a side effect of isolation.
- **Reversibility**: Ability to replace a well-isolated layer's implementation entirely.
- **Vertical layer / cross-cutting concern**: Functionality spanning many/all horizontal layers — logging, security, error handling, performance monitoring, transactions.
- **Horizontal layer**: A concern specific to one tier (e.g. serialization prep within the presentation tier).
- **Whittling**: Incrementally shaving thin layers off a big block of screen code until each layer is manageable.

## Mental Models
- **Treat a logical layer like a third-party component.** Use it when designing a layer's contract — you wouldn't unit-test the vendor's code, so build the seam so the layer is equally isolated.
- **Use an Anti-Corruption Layer when an external dependency is out of your control and likely to change** (a grid control upgrade), so the ripple is contained in a wrapper.
- **Use AOP / vertical layers when a concern (logging, transactions, auth) is inextricable from method bodies** — intercept calls instead of sprinkling code.
- **Use a domain-centric layout when the code talks about DataSets and services more than the business** — flip the arrows to point at the domain.

## Anti-patterns
- **UI with intimate knowledge of non-UI work**: ASPX repeater bound directly to DB column names; the DAL data structure ripples all the way to the UI.
- **Lip-service layering**: A WhosOnTour → TourService → TwilightDB chain that *looks* layered but couples a DataSet's table/relation structure straight to the page.
- **Sprinkling cross-cutting calls**: `Log.For(this).Debug(...)` at every method entry/exit — noise, clutter, broken SoC, and easy to forget or get wrong.
- **Over-exposing a wrapper**: Mirroring every property/method/event of a wrapped third-party control — makes the ACL brittle.
- **Refactoring without a test**: Sweeping re-layering with no safety net — the code already works in a known way; prove it still does.
- **Cleaning up while extracting**: Trying to perfect the extracted layer in the same step instead of a plain cut-and-paste behind the seam.
- **Big-bang relayering**: "Friday afternoon, done by the weekend" — a variable rename quietly becomes a data-access overhaul.

## Code Examples
```csharp
[Logging]
public class MyClass : ContextBoundObject
{
    public void DoSomething()
    {
        Debug.WriteLine("I'm doing some work");
    }
}
```
- **What it demonstrates**: A hand-rolled AOP aspect — the `[Logging]` attribute (backed by `ContextAttribute`/`IMessageSink` interceptors) logs every call with *no* logging code inside the method. Caveats: requires deriving from `ContextBoundObject` (a confusing coupling) and remembering the attribute — which is why real projects use Aspect#, PostSharp, or the Policy Injection Block instead.

```csharp
// Domain layer
public interface IConsultantRepository { /* well-defined contract */ }
// Data access layer holds the concrete implementation; UI references only the interface.
```
- **What it demonstrates**: A repository interface living in the domain while its DB-specific implementation lives in the DAL — domain concept without database coupling.

## Reference Tables

| Element | Direction of references | Coupling (Ch 5 terms) |
|---|---|---|
| Domain | Center; everything refers to it | high afferent |
| Utilities / Vertical (logging, perf) | Referenced *by* every layer | high afferent |
| Automated Tests | Refers *to* every layer | high efferent |
| Data Access | Referenced only by tests; reached via interfaces in the domain + IoC/factory | low afferent |

## Worked Example
Refactoring one screen into layers (the whittling process):

1. **Pick a starting point** — examine your physical tiers to spot natural seams; start with a *test* (use Feathers' techniques if the code "can't" be tested), and pick a simple read-only screen (e.g. an admin "list users" page).
2. **Define one seam first** — identify a single interface (contract) between the screen and the layer just below it. Work *down* from the UI, not up, so you thin out responsibilities as you go.
3. **Extract without cleaning** — cut-and-paste the relevant block into a new class implementing that interface; the screen now news-up the implementation behind the seam. The extracted layer will be ugly. That's fine — goal is layering, not beauty. Leave the big "blue blob" of remaining screen code alone for now.
4. **Check in** — run the build script; confirm it compiles and the pre-existing test(s) pass. Small, reversible, "check-in early/check-in often" steps.
5. **Whittle further** — repeatedly move bits of the leftover blob down into the appropriate layer; total code volume doesn't change, it just relocates into new classes, until the screen holds only UI code.
6. **Next screen** — far less work: the layers are already defined and you know what to expect.
7. **Recognize advances** — take coupling metrics before and at intervals; run informal reviews focused *only* on layering (not implementation details).
8. **Know when to stop** — pause for a critical release or higher-priority work, or once a section is adequately layered; resist "just one last thing."

Scale note: large codebases *can* be relayered but demand a *dedicated, focused* effort (sometimes one person) working in an isolated VCS branch so radical experiments can be backed out.

## Key Takeaways
1. Distinguish tiers (physical) from logical layers (task-based) — many layers live in one tier; tiers alone are too coarse for real separation of concerns.
2. Interfaces are the contracts between layers; they buy you isolation, insulation, reversibility, and testability (mockable dependencies at the seams).
3. An Anti-Corruption Layer (Adapter pattern, minimal surface) wraps volatile dependencies so upgrades ripple into the wrapper, not your whole app.
4. Handle cross-cutting/vertical concerns (logging, transactions, security) as aspects via AOP — never by sprinkling calls through every method.
5. Refactor toward the domain: domain holds objects and repository interfaces; implementations live in the DAL, wired via an IoC container.
6. Re-layer incrementally — one seam, one screen at a time, behind a test, checking in often. Do NOT underestimate the effort or attempt it big-bang.
7. Layer first, clean up later: extract code behind a seam as-is, then refactor the now-isolated implementation in a separate step.

## Connects To
- **Ch 7 (OO Fundamentals)**: Layering is the first application of encapsulation, separation of concerns, DRY, SRP, reversibility, the Adapter and Decorator patterns, and Interface-Based Design introduced there.
- **Ch 9 (Taming Dependencies / IoC)**: Builds directly on these interface contracts — how to inject concrete implementations into a class, via the Dependency Inversion Principle and IoC containers, so a single central spot controls how seams are "newed up."
- **Ch 4 (Automated Testing)**: Seams enable interaction testing — dependencies conform to interfaces, so they can be mocked.
- **Ch 5 (Metrics)**: Track dropping afferent/efferent coupling to measure relayering progress.
- **Ch 2 (Source Control / CI)**: "Check-in early/check-in often," build scripts, and isolated branches are the safety net that makes incremental relayering feasible.
- **Ch 12**: Expands on object-conversion layers around web services.
