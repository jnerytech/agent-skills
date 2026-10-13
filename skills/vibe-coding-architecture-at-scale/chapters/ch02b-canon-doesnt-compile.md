# Chapter 2b: The Canon Doesn't Compile

## Core Idea
The classical architecture canon (Richards & Ford's *Fundamentals of Software Architecture*, Page-Jones's connascence, Ford/Parsons/Kua's fitness functions) is correct but unenforceable in prose — and unenforceable guidance loses to a generator producing a thousand lines an hour. "If a principle cannot fail a build, the agent will eventually violate it." Convert each principle into a test, rule or gate, or accept that it is decoration.

## Frameworks Introduced
- **The Two Laws, re-read for AI**: (1) everything in software architecture is a trade-off; (2) why is more important than how.
  - When to use: deciding where human labor goes on an AI team.
  - How: Law 2 is now literal — *how* is free; *why* is the only artifact a human must produce because the generator has no access to it unless you put it there (version it: prompt lineage, Ch 23). Law 1 is the half that never became free — the AI doesn't weigh trade-offs; it optimizes the current ask against loaded context, with no memory of the team's prior trade-offs. You must name which characteristic wins.
- **Make the -ilities readable**: every architecture characteristic you care about must leave the slide deck and become something the generator reads at the moment it decides.
  - When to use: any characteristic, especially *implicit* ones (assumed, never written down).
  - How: convert each to one of three forms — (1) a clause in the specification/`.specs/` constitution (Ch 7); (2) a source-resident annotation, a VibeTag next to the code it governs (Ch 4); (3) a number — a performance budget the build enforces (Ch 17b) or a feedback-latency budget the test suite is designed around (Ch 5b). Prose the agent never opens "does not exist, as far as the generation is concerned."
- **The Fitness-Function Question**: a fitness function is any mechanism giving an objective, repeatable, automatic verdict on how well the architecture holds one characteristic (Ford, Parsons, Kua, *Building Evolutionary Architectures*, 2017).
  - When to use: before claiming to care about any characteristic.
  - How: ask "what is the fitness function for this, and where does it run?" No answer = an opinion, not an architecture decision. Map: modularity → ArchUnit rules (Ch 5); testability/test topology → coverage-on-the-diff (Ch 5b); architectural drift → living diagram as telemetry (Ch 6); scalability/performance → query-count budget in the inner loop (Ch 17b); all of them → pipeline on every branch (Ch 21).
- **Style Catalog as Constraint Surface, Not a Menu**: the architecture style you commit to determines which fitness functions make sense.
  - When to use: before letting an agent generate a new system or module.
  - How: (1) declare the style first, as a written constraint; (2) derive fitness functions from it — layered → "does anything skip a layer"; event-driven → "is any consumer coupled to a producer's internal schema instead of its published event"; (3) default stance: **domain partitioning with a package-private default** (feature packages hide a quantum's internals unless a rule says otherwise). Undeclared style = no boundary to violate = nothing to check.
- **Connascence as a build assertion** (Page-Jones, 1995): two components are connascent if changing one forces a coordinated change in the other.
  - When to use: judging AI-introduced coupling.
  - How: classify the form (static: name, type, meaning/convention, position, algorithm; dynamic: execution order, timing, value, identity), then rate on three dials — **strength** (how hard to break), **locality** (how far apart), **degree** (how many places change together). Worst case = high strength + weak locality. Bolt the measuring tape to the build: ArchUnit (Ch 5), jQAssistant graph queries (Ch 6).

## Key Concepts
- **Architecture characteristics ("-ilities")**: operational (availability, performance, scalability, recoverability, elasticity), structural (maintainability, extensibility, portability, configurability), cross-cutting (security, privacy, accessibility, legal compliance).
- **Explicit vs. implicit characteristics**: written into requirements vs. assumed by everyone — implicit ones are *invisible* (not disregarded) to an agent.
- **Generic architecture**: tries to satisfy every characteristic, optimal at nothing — the AI's default output when no priority is stated ("the agent architecting correctly, given the absence of any instruction").
- **Afferent / efferent coupling, instability, distance from the main sequence**: Robert Martin's package metrics telling whether a module has become a load-bearing wall.
- **AI as a connascence machine**: local pattern matching plants high-strength, weak-locality coupling (copied magic constants, mirrored argument orders) and never pays it down — the agent has no session next sprint.
- **Architecture quantum**: unit of independent deployability — high functional cohesion, low external coupling, static dependencies.
- **Technical vs. domain partitioning**: organize by what code *is* (controllers/repositories) vs. what it *does* (order, billing, loyalty packages).
- **Entity trap**: a Manager/Service class wrapping one DB entity, absorbing every operation into a God object — the generator's favorite shape, learned from tutorials and scaffolding.
- **Big Ball of Mud** (Foote & Yoder): no discernible boundaries — the week-20 checkout controller.
- **"Architecture is now the stuff the agent can't generate"**: Richards's "stuff you can't Google," updated — trade-offs, the why, budgets, uncrossable lines.

## Mental Models
- "If a principle can't fail a build, the agent will eventually violate it. Not might. Will."
- Think of the agent as having infinite shallow breadth: recall is free; judgment (weighing an unasked trade-off, protecting an unnamed characteristic, refusing a remembered-costly shortcut) is what's left.
- Use Hickey's line as a warning label: "programmers know the benefits of everything and the trade-offs of nothing" — the generator is that failure mode at 10,000x speed.
- Reciting a fallacy and generating code that respects it are unrelated skills: the AI can list all eight fallacies of distributed computing and still write a synchronous cross-service call with no timeout, retry or circuit breaker.

## Anti-patterns
- **-ilities that live only in prose/slide decks**: invisible to the agent.
- **No stated priority among characteristics**: produces the generic architecture, adequate at everything, optimal at nothing.
- **Treating the style catalog as a menu**: lets the agent pick; nothing to check against.
- **The entity trap**: God-object services around single entities.
- **Copying magic constants / mirroring argument order across packages**: connascence of meaning/position across boundaries neither side can see.
- **Trusting the AI's knowledge of the network fallacies**: knowledge doesn't produce timeouts, retries, circuit breakers.

## Reference Tables
**Connascence (Page-Jones)**

| Kind | Forms | Detectable |
|---|---|---|
| Static | name, type, meaning/convention, position, algorithm | by reading code |
| Dynamic | execution order, timing, value, identity | only at runtime |
| Dials | strength, locality, degree | judge any instance |

**Characteristic → fitness function → chapter**

| Characteristic | Fitness function | Where |
|---|---|---|
| Modularity (structural) | ArchUnit rule: order must not import billing | Ch 5 |
| Testability | Coverage-on-the-diff flags untested AI branches | Ch 5b |
| "Architecture is what we think" | Living diagram regenerated each build (telemetry, not gate) | Ch 6 |
| Scalability/performance | Query-count budget asserted in inner loop | Ch 17b |
| All of the above, always | Pipeline on every branch | Ch 21 |

**The eight fallacies of distributed computing** (Deutsch, +Gosling): network is reliable; latency is zero; bandwidth is infinite; network is secure; topology doesn't change; one administrator; transport cost is zero; network is homogeneous. Timing half caught by Ch 17, contract/schema half by Ch 18.

## Worked Example
**AWS S3 outage, Feb 28, 2017.** A routine capacity-reduction command in us-east-1 removed more servers than intended, disrupting S3 for hours. The AWS Service Health Dashboard couldn't update — it depended on S3. Recoverability had been treated as a characteristic of the storage service, never written down as a characteristic of the *status page*: an implicit dependency, invisible until it failed. Fix was architectural (decouple the reporter from the reported-on system). Lesson: an implicit characteristic "is not the one you forgot to build. It is the one you never named, so nothing, human or machine, was ever watching it." For an agent, the fix is to name it as a spec clause, VibeTag, or budget — and give it a fitness function.

## Why It Works / Failure Mode
- **Fitness functions work** because they are automatic, objective verdicts that run at generation speed and don't care how confident code looks — the canon's measuring tape bolted to the build. **They fail** when a characteristic has none: it then exists only in a document or memory and is invisible to the generator.
- **Declaring the style works** because it creates boundaries that fitness functions can check. **It fails** when left undeclared: unguided generation converges on the Big Ball of Mud or the entity trap.

## Key Takeaways
1. *How* is free; the *why* and the trade-off are the human's remaining labor.
2. Every characteristic you care about must become a spec clause, a VibeTag, or an enforced number.
3. For every -ility, answer "what is its fitness function and where does it run?" — or admit it's an opinion.
4. The AI is a connascence machine; turn coupling metrics into build assertions.
5. Declare the architecture style first; derive fitness functions from it. Default: domain partitioning, package-private.
6. Name the entity trap and Big Ball of Mud so you can test against them.

## Connects To
- **Ch 1**: the checkout controller is the unnamed Big Ball of Mud; connascence first mentioned.
- **Ch 3**: next step — deciding what the agent may read.
- **Ch 4**: VibeTags as source-resident characteristics.
- **Ch 5 / 5b / 6 / 17b / 21**: fitness functions for modularity, test topology, drift, performance, pipeline.
- **Ch 7**: `.specs/` constitution holds characteristics as clauses.
- **Ch 17 / 18**: timing and contract halves of the network fallacies.
- **Ch 23**: prompt lineage versions the *why*.
- **Fundamentals of Software Architecture (Richards & Ford)**, **Building Evolutionary Architectures (Ford/Parsons/Kua)**, **connascence (Page-Jones)**, **Robert Martin package metrics**, **Simple Made Easy (Hickey)**, **Big Ball of Mud (Foote & Yoder)**, **Fallacies of distributed computing (Deutsch)**.
