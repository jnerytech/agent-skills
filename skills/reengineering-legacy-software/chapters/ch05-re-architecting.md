# Chapter 5: Re-architecting

## Core Idea
Re-architecting is "refactoring in the large" — changing software structure at the level of modules and services (not methods/classes) while keeping externally visible behavior the same. The two big moves are: splitting a monolithic *codebase* into modules, and distributing a monolithic *application* into separate services (SOA / microservices). Both buy modularity, but each network hop you introduce buys a new class of failures.

## Frameworks Introduced

- **Modularization of a monolithic codebase**: break one project/JAR into separate modules, each with an explicit interface and its own build artifact.
  - When to use: fine-grained method/class refactoring has plateaued but the code still lacks high-level clarity, structure, and testability.
  - How:
    1. Decide the target module structure *up front* — one module per major user-facing feature.
    2. Introduce explicit Java interfaces for each feature (also unlocks mock injection for tests).
    3. Build a skeleton: per-module folders, build scripts, dependency-management files, standard dir layout.
    4. Separate each module's interface artifact from its implementation artifact (e.g. `stats-iface.jar` vs `stats-impl.jar`); put only the interface on the compile-time classpath to *enforce* that nobody depends on another module's implementation.
    5. Spin modules out one at a time, starting with the easiest/most self-contained (the Stats engine).
    6. Use dependency-injection (Guice) so callers depend on interface + DI module at compile time, implementation only at runtime.
    7. Dump hard-to-untangle shared utilities into a single `Common` module rather than fighting every cyclic dependency.

- **"One-sentence purpose" granularity test**: a heuristic for deciding component boundaries.
  - When to use: deciding package or module structure — how big/small a component should be.
  - How: every component must have a single purpose explainable to a typical *user* in one sentence (e.g. "the component that stores log data reliably on disk"). If you can't, it does too much; if it does less than one useful thing, it's too fine-grained.

- **Architecture-comparison matrix**: evaluate candidate architectures across four axes — technical benefits, technical challenges, organizational benefits, organizational challenges (see Reference Tables).
  - When to use: deciding whether/how to distribute a monolith.
  - How: score Monolithic vs Front-end+Back-end vs SOA vs Microservices on all four axes; remember "no silver bullet" — pick the trade-off set you can live with operationally.

- **Incremental strangler-style migration**: keep the monolith and spin out a couple of noncritical functions as separate services first.
  - When to use: any large monolith you're tempted to split — don't do it in one big-bang.
  - How: experimentally extract 1-2 low-risk features into back-end services; build tooling/experience/process as you go; re-evaluate after a couple of services — you can stop, continue toward SOA, or retreat to a few medium services.

## Key Concepts
- **Re-architecting**: refactoring at a level higher than methods/classes — e.g. moving classes out of the main codebase into a separate library/module/service.
- **Monolithic codebase**: all source in one folder, built as one binary (one JAR / one IDE project).
- **Module (component)**: source in a separate folder, built as a separate binary, exposing an interface so other modules know nothing of its implementation.
- **Monolithic application**: runs entirely in one process on one machine — may be built from a monolithic codebase *or* from modules.
- **Service**: software isolated from the rest, communicating only via network messages (HTTP/Thrift, JSON/XML), in its own process, usually on its own machine.
- **SOA (service-oriented architecture)**: an application distributed across multiple services.
- **Microservice**: an SOA with an especially strong focus on decoupling, bounded contexts, and developer autonomy/ownership (paraphrasing Adrian Cockcroft).
- **Bounded context**: each service owns its domain model; service A's `User` model is *not* service B's `User` — a translation layer converts between them (from Domain-Driven Design, Eric Evans).
- **Hotspot service**: a service nearly everything depends on (e.g. authentication) — becomes a single point of failure and scaling bottleneck.
- **God class**: anti-pattern object that knows about everything and controls too many other objects; obstacle to modularization.

## Mental Models
- **Use modules-only (keep one process) when** you want code clarity/testability but the current Core/UI architecture works — separate the *codebase* concern from the *deployment* concern. (The case study deliberately left architecture unchanged.)
- **Use interface/impl artifact separation when** you want to make implementation coupling literally impossible — "for psychological reasons as much as technical ones."
- **Use a service split when** lack of isolation between features is your biggest pain — services can "fail as hard as they like" and the rest of the site stays up.
- **Use the monolith when** low latency and simple development matter more than fine-grained scaling, and you're not ready for SOA's operational burden — first ask "is it really necessary?"

## Anti-patterns
- **Long-lived re-architecting branch diverging from main**: the author's main regret. They kept a modularization branch separate, manually merged from dev, and had to *freeze development for ~2 days* to cut over — "pretty painful and quite dangerous." Prefer refactoring on the main branch, or merge main into the work branch frequently.
- **Changing functionality during a re-architecture**: explicitly out of scope — adding features mid-reorganization is "asking for trouble."
- **Regression through reuse**: a utility written for feature A gets tweaked for feature B, silently breaking A (and its test gets "fixed" to match). The more code in one place, the likelier this is; isolation prevents it even at the cost of some duplication.
- **Sharing a database between microservices**: the most common way to accidentally couple "independent" services — every service owns its own datastore.
- **Total tech freedom in SOA**: every team picking a different language → no shared code, duplicated work, devs locked into teams. Lay down 2-3 recommended languages.
- **Breaking API changes in a FE/BE or service split**: instantly destroys the decoupling benefit — both sides must then deploy simultaneously. Avoid "at all costs."
- **Big-bang monolith→SOA rewrite**: don't refactor a large app into FE/BE in one go; go incremental.

## Code Examples

Enforcing the interface boundary with an interface-only artifact, then wiring with Guice DI:

```java
// stats-iface.jar — interface only, the compile-time dependency
interface StatsEngine {
    StatsResult calculateStats(StatsRequest request);
}

// stats-impl.jar — runtime only; callers must NOT see this
public class StatsEngineImpl implements StatsEngine {
    @Inject private SearchEngine searchEngine;        // injected, not new'd
    public StatsResult calculateStats(StatsRequest request) {
        SearchResult searchResult = searchEngine.search(...);
        return result;
    }
}

// Each module ships a Guice module binding its interface to its impl
public class StatsModule extends AbstractModule {
    @Override protected void configure() {
        bind(StatsEngine.class).to(StatsEngineImpl.class);
    }
}
```

Before Guice, callers had to know implementation details (bad — compile-time dep on `*-impl`, plus constructor boilerplate):
```java
StatsEngine statsEngine = new StatsEngineImpl(new SearchEngineImpl(), ...);
```

Awkward but tolerated transitional interface, where tight coupling forced the caller to supply a helper:
```java
interface ReportEngine {
    ReportResult createReport(ReportRequest request, ReportEngineHelper helper);
}
```

## Reference Tables

Architecture comparison (condensed from Table 5.1):

| Architecture | Technical benefits | Technical challenges | Org benefits | Org challenges |
|---|---|---|---|---|
| **Monolithic** | Low latency; simple dev; no duplicated models/validation | Scaling (whole-app replicas only); complexity of large codebase; unexpected interactions | Low intra-feature comms | Fear of failure; high inter-feature comms overhead |
| **Front end + Back end** | Scale FE/BE separately; presentation split from logic; reuse BE for many FEs | Complexity from network calls | Specialization; FE iterates faster; stepping stone to SOA | Comms overhead; siloing; FE/BE teams block each other |
| **SOA** | Fine-grained scaling; isolation; encapsulation | Ops overhead; latency; service discovery; tracing/debug/logging; hotspot services; API docs/clients; integration testing; data fragmentation | Autonomy | Dilemma over extent of autonomy; risk of duplicated work |
| **Microservices** | Same as SOA, only more so | Same as SOA + risk of *implicit* coupling | Even more autonomy via bounded contexts | Implies DevOps; requires a platform team; demands a major shift in thinking |

Tooling adopted in the case study: **Ant → Gradle** (purpose-built for multi-module, Groovy DSL, plugins), **Apache Ivy + Artifactory** (dependency management / artifact repo), **Guice** (DI), **Jenkins** (per-module build jobs), **Eclipse → IntelliJ** (better multi-module support). SOA-era tooling name-checked: **Eureka** (service discovery), **Fluentd/Logstash** (log aggregation), **Zipkin** (distributed tracing), **Swagger** (API docs generation).

## Worked Example

**Case study — log management application (a large Java enterprise app).**

*Starting state:* A semi-monolithic system — one monolithic codebase split into three packages (`core`, `ui`, `common`), but deployed as two services (a command-line Core service and a Struts/Tomcat UI service) communicating over Java RMI. The split existed only for scalability (multiple Core instances to ingest/search more logs; one UI). Built by a complicated Ant script; dependencies were "a folder full of JARs." Grown organically from an in-house tool, so it carried historical accidents: no single `ReportEngine` interface (report code smeared across coupled classes), low test coverage blocked by untestable code, and big God classes of utility methods. Refactoring had plateaued and velocity was falling.

*Choosing the seams:* Module boundaries "fell into place quite naturally" — one module per major feature: Log collection, Storage, Search, Alerts, Database, Config, Report, Stats, plus Common, plus Core-service and UI-service modules that wire their members together and own the entry point. Each boundary validated by the one-sentence-purpose test. Database was deliberately separated from Storage/Search to allow a future swap to emerging open-source log stores. Untangle-resistant shared utilities were dumped into `Common`. Two things explicitly out of scope: **architecture changes** (Core/UI RMI split worked, left alone but kept flexible) and **functionality changes**.

*Incremental steps:* (1) Build the skeleton — module folders, build scripts, dependency files. (2) Keep Ant short-term (a shared `build.xml` + thin per-module ones — admittedly *worse* than before, but enough to start) and add Ivy + Artifactory. (3) Split each module's interface artifact from its impl artifact to enforce the boundary. (4) Spin out modules easiest-first, starting with the self-contained Stats engine; harder modules needed dependency-analysis tools and patient refactoring to break cyclic deps, sometimes yielding awkward interfaces (the `ReportEngineHelper`) tidied up later. (5) Introduce Guice for DI so callers depend on interface + Guice module, not impl — it "spread like wildfire" and pushed devs toward testable code. (6) Once mature, swap Ant for Gradle, consolidating everything into one multi-module build.

*End state:* A clean set of isolated modules with interface/impl separation, modern build (Gradle) and DI (Guice). Verbal feedback: code easier to work with, devs motivated by new tech. Crucially it made the codebase amenable to *future* re-architecture — e.g. later running each module as its own service (SOA) — which would have been very hard without modularizing first.

*The scar:* coordinating with devs still committing to the live branch. Because the structural change was so fundamental, normal "refactor on main / merge often" advice was impractical; they hand-merged a long-lived branch and froze dev ~2 days to cut over. In hindsight: should have been more incremental.

**Companion example — Orinoco.com** (100M page views/month e-commerce monolith, periodic Black Friday spikes, ~2-dozen full-stack devs, slow 2-3 week release cycle, fear-driven manual testing, no spare resources for a REST API). The chapter walks its four options through Table 5.1 and recommends *not* a big-bang split: keep the monolith, experimentally spin out a couple of noncritical functions (e.g. recommendations) as back-end services, build tooling/experience, then decide whether to continue toward SOA, stop, or settle on a few medium services.

## Key Takeaways
1. Separate two decisions: *how the codebase is organized* (modules) vs *how the app is deployed* (one process vs services). Modularize first; you can recombine modules any way later — monolith, microservices, or sell some and not others.
2. Forcing explicit module interfaces is the real payoff — it surfaces dependencies and makes mocking/testing possible.
3. Enforce boundaries mechanically (interface-only compile-time artifacts + DI), not by discipline alone.
4. Decide the target structure before moving code; spin modules out easiest-first; quarantine un-untanglable utilities in a `Common` module instead of stalling.
5. Every network call you add is a new class of failures (timeouts, hangs, partial data) plus clients, retries, circuit breakers, and service discovery to build and maintain.
6. The hardest costs of distribution are organizational: siloing, inter-team blocking, duplicated work — budget a Platform team and shared guidelines.
7. Migrate incrementally on the main branch; long-lived structural branches force dangerous manual merges and dev freezes. There is no silver-bullet architecture — pick trade-offs you can operate.

## Connects To
- **Ch4 — Refactoring**: same goal (improve structure without changing behavior) at the smaller method/class scale; re-architecting is "refactoring in the large" and often starts only after fine-grained refactoring plateaus.
- **Ch6 — The Big Rewrite**: the larger, riskier alternative when even re-architecting isn't enough; this chapter's incremental-extraction advice is the counter-argument to big-bang rewrites.
- **Ch9 — Development workflow**: Gradle and multi-module build tooling are revisited.
- **Strangler Fig pattern (Fowler)**: the "keep the monolith, spin out noncritical services, gradually grow them" recommendation is strangler-style incremental migration.
- **Domain-Driven Design (Eric Evans)**: bounded contexts — the conceptual basis for microservice model ownership and translation layers.
- **Working Effectively with Legacy Code (Feathers)**: breaking dependencies / God classes / getting code under test is the prerequisite groundwork that makes module extraction feasible.
