# Chapter 7: Bringing Better OO Practices to the Project

> Ch 7 opens Part 2 ("The Code") — the book shifts from ecosystem/process to changing the application's actual code for maintainability.

## Core Idea
Most brownfield pain comes from procedural code wrapped in classes that ignores basic OO. This chapter re-grounds you in the four OO fundamentals, a set of design "-abilities," and battle-tested OO principles (SRP, OCP, DIP, Law of Demeter) so every later refactoring rests on a shared foundation.

## Frameworks Introduced

- **The 4 OO Fundamentals**: Encapsulation, Inheritance, Abstraction, Polymorphism.
  - When to use: Constantly — ask "is this procedural code in OO clothing?" while reviewing.
  - How: Hide implementation (encapsulation), specialize via subclasses (inheritance), simplify complex things into APIs/levels (abstraction), treat subclasses as their base type (polymorphism).
  - Why it works / failure mode: They underpin every later principle. Failure mode: wrapping large procedural methods in a class and calling it "object-oriented"; over-using inheritance into deep, fragile trees.

- **Code "-abilities" (5 attitudes)**: Maintainability, Readability, Testability, Extensibility, Reversibility (plus Adaptability).
  - When to use: As background goals on every change.
  - How: Name things clearly; design so classes can be tested with minimal infrastructure (depend on interfaces); allow extension without rewriting; keep design decisions cheap to reverse.
  - Why it works / failure mode: Maintainability is the granddaddy — code spends most of its life being read and maintained. Failure mode: "Framework Builder Anxiety" — agonizing over irreversible decisions.

- **Useful OO Principles**: Favour composition over inheritance; Single Responsibility (SRP) / Separation of Concerns; Open/Closed (OCP); Principle of Least Knowledge (Law of Demeter); Dependency Inversion (DIP); Interface-Based Design.
  - When to use: Guiding new features and refactors; isolating changes in coupled brownfield code.
  - How: Code to interfaces; one reason to change per class; extend via new implementations not edits; talk only to immediate friends; depend on abstractions; design contracts from the caller's view (via tests).
  - Why it works / failure mode: Isolates ripple effects. Failure mode: SRP yields many small classes (manage with navigation tools / ReSharper); Law of Demeter overdone creates wrapper-method bloat that itself breaks SRP.

- **Agile design acronyms**: KISS, YAGNI, DRY.
  - When to use: Whenever tempted to over-engineer, speculate, or copy-paste.
  - How: Pick the simplest solution; don't build until needed; eliminate duplication ruthlessly.
  - Why it works / failure mode: Keeps code spry/adaptive. Failure mode: premature optimization; YAGNI taken to extreme ("don't refactor, it works").

## Key Concepts
- **Encapsulation**: Shielding an object's implementation details from callers — the most overlooked of the four; screens shouldn't know connection strings or SQL.
- **Single Responsibility Principle (SRP)**: "A class should have only one reason to change" (Martin) — the best road to maintainability.
- **Separation of Concerns (SoC)**: Breaking functionality into distinct, non-overlapping modules; abstract, made concrete by SRP.
- **Open/Closed Principle (OCP)**: "Software entities should be open for extensibility but closed for modification" — achieved by coding to interfaces.
- **Principle of Least Knowledge (Law of Demeter)**: "Only talk to your immediate friends" — don't chain calls more than one level deep.
- **Dependency Inversion Principle (DIP)**: "Abstractions should not depend on details; details should depend on abstractions" — full chapter in Ch 9.
- **Interface-Based Design**: Client and supplier agree on a method contract; the core idea behind test-driven design.
- **Fluent interface**: Chained methods (From/Using/With) that read like prose; deliberately flouts Law of Demeter for readability.
- **Reversibility**: Designing so decisions can be undone cheaply — "We can change it later."
- **Legacy Code Dilemma (Feathers)**: "When we change code we should have tests; to put tests in place we often have to change code."

## Mental Models
- Use **composition over inheritance** when a "pure" inheritance tree would explode combinatorially (DecorativeHandCraftedMug...) — compose behaviours via interfaces (IUse, IManufactureMethod) instead.
- Use **OCP + Strategy/Decorator/Template Method** when new variants keep forcing edits to a stable class — pass an interface (IFinder) or a Predicate<T> instead of a concrete type.
- Use **Interface-Based Design (write the test first)** when designing a new class — the caller's perspective shapes a cleaner API than building bottom-up.
- Use **YAGNI** when you catch yourself parameterizing for hypothetical futures (Oracle/XML "just in case") — but balance against near-certain near-term changes.

## Anti-patterns
- **Procedural logic in code-behind**: Business logic / data access stuffed in an ASP.NET click event — breaks SRP, encapsulation, abstraction; nearly impossible to test.
- **Large multi-responsibility methods/classes**: e.g. a 6000-line method or a PrintFunctions class doing reset + print + email + config.
- **Deep inheritance trees**: Each level adds a bit until the base class's intent is lost; a top-level change ripples down everywhere.
- **Chained calls (`customer.Invoices.FindOverdue()`)**: Breaks encapsulation — caller knows internals of two objects; changing the collection ripples outward.
- **Naming classes after patterns** (`...Decorator`): Ties the name to an implementation; name by responsibility instead.

## Code Examples
```csharp
// Listing 7.1 — Sample ASP.NET click event (the anti-pattern)
public void listBoxSearch_Click(object sender, EventArgs e)
{
    string searchTerm = textBoxSearchTerm.Text;          // #1 gather inputs
    searchTerm = parseSearchString(searchTerm);          // #1
    int countryId = listBoxCountry.SelectedValue;        // #1
    DataTable searchResults = SearchApplicationDb         // #2 retrieve (static
        .GetSearchResults(searchTerm, countryId);        //    data-access call)
    gridSearchResults.DataSource = searchResults;        // #3 bind to page
    gridSearchResults.DataBind();                        // #3
    string searchCriteriaText = getSearchCriteriaText(); // #4 display criteria
    labelCurrentSearch.Text = searchCriteriaText;        // #4
}
```
- **What it demonstrates**: Four responsibilities in one code-behind method — short but untestable (static data access + ASP.NET infrastructure), violating SRP, encapsulation, and abstraction.

```csharp
// Listing 7.9 — OrderRepository closed for modification (OCP via Strategy)
public class OrderRepository
{
    IEnumerable<Order> FindBy(IFinder finder)   // #1 takes interface, not concrete
    {
        foreach (Order order in _orders)
            if (finder.Matches(order)) yield return order;
    }
}
public interface IFinder { bool Matches(Order order); }   // #2
```
- **What it demonstrates**: Coding to an interface makes `FindBy` infinitely extensible (OrderedDateFinder, FilledDateFinder, CustomerFinder...) without ever modifying the repository.

## Reference Tables
| Principle | One-line statement | Brownfield payoff |
|---|---|---|
| SRP | One reason to change per class | Smaller classes; change location obvious |
| OCP | Open for extension, closed for modification | Add features without recompiling/risking existing code |
| Least Knowledge (Demeter) | Talk only to immediate friends | Isolates ripple effects of internal changes |
| DIP | Depend on abstractions, not details | Decouples high/low-level modules (Ch 9) |
| Composition > inheritance | Compose behaviours via interfaces | Avoids fragile, deep inheritance trees |
| Interface-Based Design | Agree the contract (write test first) | Wrap legacy class in an interface, then swap implementation |

Agile acronyms: **KISS** (simplest solution; beware premature optimization / Occam's Razor) · **YAGNI** (build only when needed) · **DRY** (no duplication — core idea of *The Pragmatic Programmer*).

## Worked Example
Refactoring `PrintFunctions` to SRP (Listings 7.6 → 7.7). The original class resets printers, prints to file, prints to printer, emails the sender, and has three `SetPrinterConfiguration` overloads — many reasons to change. The refactor produces a lean `PrintManager` whose sole job is the print action:

```csharp
public class PrintManager
{
    private IPrintNotifier _printNotifier = new EmailNotifier();          // #1
    private IPrintConfiguration _configuration = new DefaultPrintConfiguration(); // #2
    private IPrintDestination _destination = new PrintFileDestination(DEFAULT_PRINT_FILE);
    private IDocumentPrinter _printer = new Default();                    // #3
    public IPrintNotifier PrintNotifier { get; set; }   // overridable
    public IDocumentPrinter Printer { get; set; }
    public void Print(PrintJob printJob)
    {
        _printer.Print(printJob.Document);
        _printNotifier.Notify(printJob.Sender);
    }
}
```
Notification and configuration are delegated to other classes; this class changes only if the print process itself changes. The book is candid that it's still highly coupled (hard-coded defaults like `EmailNotifier`) — decoupling those dependencies is deferred to Ch 9.

## Key Takeaways
1. Wrapping procedural code in a class is not OO — re-examine encapsulation, inheritance, abstraction, polymorphism while you code.
2. Maintainability is the master goal; readability, testability, extensibility, and reversibility all feed it.
3. SRP ("one reason to change") is the single highest-leverage move toward a maintainable brownfield app — accept "more, smaller files."
4. Achieve OCP by coding to interfaces (Strategy, Decorator, Template Method, or Predicate<T>); favour composition over inheritance.
5. Law of Demeter and Interface-Based Design exist mainly to isolate change — wrap legacy classes in interfaces before bigger refactors.
6. Honor the Legacy Code Dilemma: if a unit test is truly impossible, lean on an integration test as a safety net, then split responsibilities.
7. Introduce principles to the team via prototype/spike, lunch 'n learn, mentoring, and quiet refactoring-as-you-go — code improvements without team buy-in only slow the decay.

## Connects To
- **Ch 4**: Mocking/testing and "no new code without tests" — testability depends on these OO principles; Interface-Based Design ≈ test-driven design.
- **Ch 5**: Depth of Inheritance metric — motivates favouring composition.
- **Ch 8**: Re-layering uses encapsulation and Separation of Concerns to split UI from logic/data.
- **Ch 9**: Inversion of Control — full treatment of Dependency Inversion and breaking the residual coupling left in Listing 7.7.
- **Ch 10**: MVC/MVP — fixes the code-behind SRP violation of Listing 7.1.
- **Ch 11/12**: Data access and integration refactors apply OCP and interface-based isolation.
