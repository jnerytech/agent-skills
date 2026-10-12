# Glossary — Brownfield Application Development in .NET

**Afferent coupling (Ca)** — number of types outside a package that depend on types inside it; incoming dependencies (Ch 5, Ch 8).

**Anti-Corruption Layer (ACL)** — an isolating layer (Adapter pattern) that translates between your domain and an external/legacy system so their model can't leak into yours (Ch 8, Ch 12).

**Aspect-Oriented Programming (AOP)** — factoring cross-cutting concerns (logging, security) into reusable aspects/vertical layers instead of scattering them (Ch 8).

**Brownfield application** — an existing, actively-developed codebase contaminated by poor practices but with real potential for improvement (Ch 1).

**Characterization / pinning test** — a test written to capture existing behavior before refactoring untested code (Ch 4, Ch 8).

**Check-In Dance** — the disciplined sequence a developer follows before committing: get latest, merge, build, run tests, then commit (Ch 2; updated for CI in Ch 3).

**Class coupling** — degree to which a class depends on others; high coupling = fragile, hard to test (Ch 5).

**Collective code ownership** — the whole team owns all the code; bugs are the team's fault, features the team's win (Ch 1, Ch 6).

**Continuous Integration (CI)** — automatically building and testing on every check-in to surface integration problems immediately (Ch 3).

**Cyclomatic complexity (CycCom)** — count of independent paths through a method; high values signal hard-to-test, defect-prone code (Ch 5).

**Code coverage** — percentage of code exercised by tests; a diagnostic, never a target (Ch 5).

**Deferred Defect** — a known defect consciously postponed rather than fixed now; tracked, not forgotten (Ch 6).

**Dependency Injection (DI)** — supplying a class's dependencies from outside (constructor/setter/method) rather than constructing them internally (Ch 9).

**Dependency Inversion Principle (DIP)** — depend on abstractions, not concretions; high-level modules shouldn't depend on low-level ones (Ch 7, Ch 9).

**Depth of Inheritance (DIT)** — how many levels a class sits below the root; deep trees raise complexity (Ch 5).

**DTO (Data Transfer Object)** — a simple object carrying data across a boundary, decoupling your domain from an external contract (Ch 12).

**Efferent coupling (Ce)** — number of types inside a package that depend on types outside it; outgoing dependencies (Ch 5, Ch 8).

**Feedback loop** — the cycle from making a change to learning whether it worked; CI/tests shorten it (Ch 3, Ch 4).

**Friction** — anything that gets in the way of a developer's normal process; a burden even when not painful (Ch 1).

**Greenfield application** — a project with no prior code or technical history (Ch 1).

**Hand-rolled data access** — manually written ADO.NET/SQL data layer (Ch 11).

**Hero Programmer Syndrome (HPS)** — reliance on individuals working heroic hours; erodes team ownership, should be discouraged (Ch 1).

**Instability (I)** — Ce / (Ca + Ce); 0 = maximally stable, 1 = maximally unstable (Ch 5).

**Interface-Based Design** — programming to interfaces to isolate and insulate components and enable substitution/testing (Ch 7, Ch 8).

**Inversion of Control (IoC)** — the general principle of handing control of flow/construction to a framework or container rather than calling it yourself (Ch 9).

**IoC container** — a framework (Castle Windsor, StructureMap, Autofac) that resolves and injects dependencies automatically (Ch 9, Ch 13).

**Iron Triangle** — time/budget/scope trade-off model; the authors prefer a *Scale* metaphor instead (Ch 1).

**Layer** — a logical grouping of responsibilities (presentation, domain, data); distinct from a physical *tier* (Ch 8).

**Law of Demeter (LoD)** — "talk only to your immediate friends"; don't chain through object graphs (Ch 7).

**Legacy application** — old code in maintenance mode, "dealt with" not improved; Feathers: code without tests (Ch 1).

**Living in fear of change** — the state where untested, fragile code makes any edit risky (Ch 4).

**Model-View-Controller (MVC)** — UI pattern; controller handles input, selects view, controller is the entry point (Ch 10).

**Model-View-Presenter (MVP)** — UI pattern; view is entry point, presenter holds presentation logic; variants Passive View & Supervising Controller (Ch 10).

**Object/Relational Mapper (ORM)** — tool (e.g. NHibernate) that maps objects to relational tables, abstracting hand-written data access (Ch 11).

**Pain point** — a process causing grief that pushes you to find a better way; defines where to improve (Ch 1).

**Passive View** — MVP variant where the view is fully dumb and the presenter drives everything (most testable) (Ch 10).

**Poor man's DI** — dependency injection without a container, via a default constructor chaining to an injectable one (Ch 9).

**Presentation Model** — UI pattern where a model object represents view state independent of the widget toolkit (Ch 10).

**Repository** — pattern providing a collection-like interface over data access, hiding persistence details (Ch 11, Ch 12).

**Seam** — a place where you can alter behavior without editing in place (e.g. an interface), enabling testing (Ch 8, per Feathers).

**Separation of Concerns (SoC)** — keep distinct responsibilities (UI, logic, data) in distinct components (Ch 7, Ch 10).

**Service locator** — an object you ask for dependencies; an alternative (often discouraged) to DI (Ch 9).

**Single Responsibility Principle (SRP)** — a class should have one reason to change (Ch 7).

**Supervising Controller** — MVP variant where the view handles simple binding and the presenter handles complex logic (Ch 10).

**Technical debt** — known-bad code/design deferred for lack of time, experience, or manpower (Ch 1).

**The Scale** — authors' balance metaphor: time & resources (keep low) vs. quality & features (keep high), always balanced (Ch 1).

**Tier** — a physical deployment boundary (process/machine); distinct from a logical *layer* (Ch 8).

**Zero Defect Count** — cultural policy of keeping the open-defect count at (near) zero by fixing defects immediately (Ch 6).
