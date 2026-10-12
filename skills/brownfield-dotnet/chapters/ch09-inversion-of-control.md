# Chapter 9: Inversion of Control

## Core Idea
Decouple high-level classes from their concrete dependencies by depending on abstractions and having those dependencies supplied from outside, so each class can be tested and changed in isolation. In a brownfield codebase, get there incrementally — interfaces first, then inverted constructors, then (optionally) a container.

## Frameworks Introduced

- **Inversion of Control (IoC)**: A high-level, abstract principle about inverting *control flow* in general — code no longer decides which concrete collaborators it gets; that decision is made elsewhere and handed in.
  - When to use: as the umbrella mindset whenever a class reaches out and grabs/creates what it needs.
  - How: move the "who decides" responsibility out of the consuming class.
  - Why it works / failure mode: it is broader than dependencies (covers control flow generally); dependency inversion is just one way to achieve it.

- **Dependency Inversion Principle (DIP)**: A *specific means* of achieving IoC — both the high-level module and the low-level modules depend on an abstraction (interface/base class) instead of the high-level module depending on concretes.
  - When to use: a class (e.g. `SpellChecker`) `new`s up or references concrete collaborators (`EnglishDictionary`, `SpanishDictionary`).
  - How: extract an interface (`ISpellCheckDictionary`); make both consumer and implementations depend on it.
  - Why it works / failure mode: efferent coupling drops (4 dependencies → 1 interface); the dependency doesn't vanish — it moves to whoever must now create the concrete.

- **Dependency Injection (DI)**: A *concrete implementation* of DIP — objects do not create their dependencies; an external service injects them.
  - **Constructor injection** (preferred): all dependencies passed as constructor params; forces a valid, fully-wired object.
  - **Setter/property injection**: dependencies set via setter-only properties after construction; use for "optional" deps (authors call optional dependencies an oxymoron).
  - When to use: once a class depends on an interface, hand the implementation in rather than letting the class find it.
  - Why it works / failure mode: constructor injection documents requirements explicitly; setter injection makes it easy to create half-initialized objects.

- **IoC Container**: A centralized object that resolves requested types, creating and injecting their entire dependency graph.
  - When to use: to remove the last residue of coupling that constructor chaining leaves behind.
  - How: configure a mapping from requested type → resolved type (XML, code, or a fluent DSL); e.g. `ISpellCheckDictionary` → `EnglishDictionary`. At runtime, ask the container for the top object.
  - Why it works / failure mode: classes stop knowing concretes; cost is container configuration code (an "unfair trade-off, but in your favour"). Mass-configuring everything at once causes hard-to-trace missing mappings — so test the container's configuration (fail fast).

- **Service Locator (container abstraction)**: A wrapper (e.g. `ResolveType.Of<T>()`, or the **Common Service Locator** project) that hides the specific container behind a shared interface.
  - When to use: at the top-of-hierarchy point where you must request an object from the container explicitly.
  - How: route all container access through one class so swapping containers touches only that class.
  - Why it works / failure mode: limits the one remaining dependency (the container itself); a generic locator may forfeit a container's advanced features.

## Key Concepts
- **IoC vs DIP vs DI**: IoC = abstract principle; DIP = a means of achieving IoC (move dependency to an abstraction); DI = a concrete implementation of DIP (inject via constructor/setter). They are nested, not synonyms.
- **Efferent coupling**: count of classes a given class depends on; keep it low. Inversion rolls many concretes into one interface.
- **Constructor chaining (poor man's DI)**: an overloaded default constructor calls the real one with a default concrete (`: this(new EnglishDictionary())`) — DI with no infrastructure, but reintroduces a hard dependency.
- **Assembler object**: the thing that actually creates an object with its dependencies wired (a container is one form).
- **Stub/mock**: framework-generated test double (Rhino Mocks, Moq, TypeMock) replacing a hand-written fake; auto-adapts when an interface gains a method.
- **Factory class**: a class whose sole responsibility is creating objects; lets a container decide *at runtime* which `ISpellCheckDictionary` to build.
- **Class explosion**: SRP + inversion yields many small classes/interfaces; navigation pain is a tooling problem, not a design problem.

## Mental Models
- Use **DIP** when a class references concretes — but accept that the dependency only *moves* to a creator class; that's correct, because creation is a separate responsibility.
- Use **constructor injection** when you want the compiler/reviewer to see every requirement; use setter injection only when a dependency is genuinely optional.
- Use **poor man's DI** when refactoring brownfield code incrementally; it leaves coupling residue but positions the code for a later, low-cost container swap.
- Use an **IoC container** when you want concrete coupling fully gone — but introduce it incrementally, never configuring all mappings at once.

## Anti-patterns
- **`new`-ing dependencies inline**: `new DocumentRepository()` inside a method ties the class to a concrete and to its construction details — untestable in isolation.
- **Forcing creation knowledge onto callers**: making `SpellCheckReviewService` know an `EnglishDictionary` is needed to build a `SpellChecker` spreads brittleness; a constructor change ripples across every call site.
- **Setter injection for required deps**: leaves objects in an unstable state if the caller forgets a setter.
- **Big-bang container adoption**: configuring the whole container in one shot causes silent missing mappings; instead configure in tiny pieces and test the config.
- **Compromising design for the IDE**: do not collapse classes to ease Visual Studio navigation — fix the tool (ReSharper/CodeRush), not the code.

## Code Examples
```csharp
// before (Listing 9.15) — dependencies created inline
public class DocumentFinder {
    public IEnumerable<DocumentDto> FindByTitle( string titleFragment ) {
        DocumentRepository repository = new DocumentRepository();          // #1
        IEnumerable<Document> documents =
            repository.Find( x => x.Title.Contains( titleFragment ) );
        DocumentToDtoTranslator translator = new DocumentToDtoTranslator(); // #1
        return translator.Translate( documents );
    }
}
// after (Listing 9.16) — dependencies inverted + injected
public class DocumentFinder {
    IDocumentRepository _documentRepository;
    IDocumentToDtoTranslator _translator;

    public DocumentFinder()                                                // poor man's DI
        : this( new DocumentRepository(), new DocumentToDtoTranslator() ) { }

    public DocumentFinder( IDocumentRepository documentRepository,         // #1 constructor injection
                           IDocumentToDtoTranslator translator ) {
        _documentRepository = documentRepository;
        _translator = translator;
    }

    public IEnumerable<DocumentDto> FindByTitle( string titleFragment ) {
        IEnumerable<Document> documents =
            _documentRepository.Find( x => x.Title.Contains( titleFragment ) );
        return _translator.Translate( documents );
    }
}
```
- **What it demonstrates**: replacing inline `new` of concretes with interface fields supplied through constructor injection (with a chained default constructor for incremental, low-impact adoption).

## Reference Tables

| DI flavor | How deps arrive | Best for | Trade-off |
|---|---|---|---|
| Constructor injection | All via constructor params | Required deps; explicit contract | Slightly more verbose constructors |
| Setter/property injection | Via setter-only properties | "Optional" deps (discouraged) | Easy to leave object unwired/unstable |
| Constructor chaining (poor man's) | Default ctor supplies a concrete | Incremental brownfield refactor | Reintroduces concrete coupling |
| IoC container | Container resolves whole graph | Eliminating concrete coupling | Config code + learning curve |

## Worked Example
`DocumentFinder.FindByTitle` (Listing 9.15) `new`s both a `DocumentRepository` and a `DocumentToDtoTranslator` inside the method — so a unit test can't run without a real repository (a real database) behind it. Applying DIP: extract `IDocumentRepository` and `IDocumentToDtoTranslator`, change the fields to those interface types, and add a constructor that accepts both (Listing 9.16). A test can now pass in a stub/mock repository and translator and verify `FindByTitle` purely as a coordination step. To keep existing call sites compiling during a brownfield migration, a chained default constructor (`: this(new DocumentRepository(), new DocumentToDtoTranslator())`) supplies the real concretes — poor man's DI. Later, a container can own that mapping and the default constructor disappears, removing the last concrete reference.

## Key Takeaways
1. IoC, DIP, and DI are nested layers — principle, means, implementation — not interchangeable terms; keep them distinct.
2. Inverting dependencies doesn't delete a dependency, it relocates creation to a class whose single responsibility is creation.
3. The payoff is testability and isolation from change — set-up shrinks from "configure a web service + app.config" to "inject a fake/mock."
4. Prefer constructor injection: it makes requirements explicit and prevents half-built objects.
5. In brownfield code, go incremental: interfaces → invert constructors → poor man's DI → IoC container, running tests after each baby step; never big-bang.
6. A container's only downside is config; abstract it behind a service locator and write a test that verifies the configuration (fail fast).
7. Expect class explosion from SRP + inversion; treat navigation friction as a tooling issue, not a reason to recouple.

## Connects To
- **Ch 8**: introducing interfaces/contracts is the first, lowest-impact decoupling step that DIP builds on; the same incremental layering applies.
- **Ch 7 (SOLID)**: DIP is the "D"; inversion repeatedly drives toward Single Responsibility and enables Open/Closed substitution.
- **Ch 5**: class-coupling metric (efferent coupling) is the measure that inversion improves.
- **Ch 4**: automated unit/integration tests are the safety net that makes brownfield decoupling safe; mocks (Rhino Mocks, Moq) replace hand-written fakes.
- **Ch 10**: next narrows focus to decoupling the user interface using the same principles.
