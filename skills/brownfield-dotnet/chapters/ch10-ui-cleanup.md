# Chapter 10: Cleaning Up the User Interface

## Core Idea
The UI is where most .NET apps slide into brownfield: RAD/drag-n-drop habits push business logic, data access, validation, and authentication into untestable code-behind. Apply Separation of Concerns to split the UI into Model, View, and an interaction class (Presenter or Controller), so the "real" logic lives outside the screen where it can be tested in isolation.

## Frameworks Introduced

- **Separation of Concerns in the UI**: Decompose screen code into three roles — (1) the object(s) being manipulated = **Model**, (2) the code that displays it = **View**, (3) the code that manages the interaction = **Presenter/Controller**.
  - When to use: any screen with non-trivial code-behind; mandatory before you can unit-test screen logic.
  - How: identify Model, then View, then the Presenter is "everything else."
  - Why it works: each component is testable in isolation; SRP restored. Failure mode: logic creeps back into the View ("just one validation check").

- **Passive View (an MVP flavor)**: The View has **no knowledge of the Model whatsoever**. The Presenter sets every UI value explicitly via fine-grained properties/methods (`view.Title = ...`, `view.AddGenre(...)`).
  - When to use: maximum testability; simple screens (login); screens with a history of bugs; complex view-element interaction; teams learning to test (no place to sneak in logic).
  - How: View implements an interface (`ISongDetailView`) exposing string/primitive properties per control; Presenter pushes data field-by-field; inject dependencies via constructor.
  - Why it works: View is "stupid as a sack of doorknobs," so leaving it untested is acceptable. Failure mode: **chatty** interface, explosion of tiny methods (`GetProvince`, `SetShippingCostLabel`).

- **Supervising Controller (an MVP flavor)**: Same as Passive View, except the **View knows about the Model** and can use .NET data binding directly (`view.Song = song`).
  - When to use: screen already relies on built-in data binding (grids/repeaters bound to objects/DataSets); you want concise, readable code and can tolerate some untestable view logic.
  - How: View exposes Model-typed properties and binds controls; Presenter just hands over the model — code is much shorter than Passive View.
  - Why it works: less ceremony. Failure mode: complex sync logic (history, cross-user updates, on-the-fly list edits) hides in the untestable View.

- **Presentation Model**: A screen-specific class that holds **both state and behavior** of the screen using internal variables (no `System.Windows.Forms`/`WebControls` reference). The View monitors it and re-syncs itself; the Presentation Model wraps the domain model. Acts as both Model and Presenter.
  - When to use: screens with lots of complex state-based behavior; the pattern of choice for WPF (there called Model-View-ViewModel / MVVM).
  - Failure mode: double synchronization (View↔PM and PM↔domain) is tedious — authors usually fall back to Passive View / Supervising Controller.

- **Model-View-Controller (MVC)**: Pre-dates MVP; MVP flavors are derivatives. The **Controller is the entry point** — it runs first, picks a view, sends the model down, then goes away. View and Controller are clearly separated with little ongoing communication; new actions instantiate a new controller (often routed via a **Front Controller**).
  - When to use: greenfield **web** apps (stateless nature fits); the authors' pattern of choice for new web UIs.
  - How: needs a framework on ASP.NET (Castle MonoRail or ASP.NET MVC) using HTTP Handlers to intercept requests before the .aspx page; navigation is by route, not page.
  - Why it works: cleanest separation/testability. Failure mode for brownfield: you don't refactor to MVC, you **rewrite** — broken URLs, subverted ViewState, server-side controls stop working.

## Key Concepts
- **Model**: Whatever object the screen displays/edits; screen-specific, contains only what that screen needs. Need not map to a domain object.
- **DTO (Data Transfer Object)**: Lightweight screen-specific class that shuttles data from domain to screen; divorces UI from domain change; built via a translation layer (e.g. AutoMapper).
- **View**: Display-only widgets (textboxes, lists, grids). The only layer allowed a `System.Windows.Forms` / `System.Web.UI` reference.
- **Presenter**: The interaction/"goo" class; holds the View (via interface) and injected data dependencies. No interface needed — nothing depends on it.
- **Seam**: The boundary between Model, View, and Presenter where you cut code out into testable classes (concept from Ch 8).
- **Direct reference vs. publish/subscribe**: Two ways the View talks back to the Presenter on events — a private reference + method calls, or raising events the Presenter subscribes to.
- **Event Aggregator**: Centralized class tracking publishers/subscribers so View and Presenter need no knowledge of each other.
- **Front Controller**: Central MVC dispatcher that maps a raised action/route to a controller method.
- **ISongRetriever vs ISongRepository**: Inject an intermediary "retriever" (not the repository directly) when the UI must not touch domain/repositories — depends on screen complexity and preference.

## Mental Models
- **Use the entry-point test to tell MVC from MVP**: if the **View** is the first class instantiated (e.g. .aspx code-behind creates the presenter), it's MVP; if the **Controller** runs first and picks the view, it's MVC.
- **Use Passive View when testability trumps everything**; use Supervising Controller when readability/data-binding matters and you'll accept some untested view code.
- **Use a screen-specific Model (DTO) when** the screen aggregates data from many sources, or when you want to attach `PropertyChanged` events without polluting a real domain object.
- **Treat the View as "stupid as possible"**: it shows what it's told and reports that a widget was clicked — nothing more. If you feel the urge to calculate tax/shipping in it, that's the flag.

## Anti-patterns
- **Logic in code-behind**: service config, authentication, localization, profile retrieval, validation all crammed into `Page_Load` — the original SRP violation (Listing 10.1).
- **Exposing UI controls outside the View**: returning a `TextBox` instead of a `string Title`. Combines Passive View chattiness with monolithic untestability — worst of both worlds. **Never** let the Presenter reference `System.Windows.Forms` / `System.Web.UI.Controls`.
- **Business logic in the View**: e.g. phone-length validation in the UI — escapes the test net (breaks when Greenland's 6-digit numbers arrive).
- **DataSets as the Model**: untyped, string-keyed (`ds.Tables[1].Rows[3]["ArtistName"]`), married to DB columns, poor discoverability. Prefer plain objects (bind equally well).
- **Over-specified tests**: tests tailored too tightly to existing implementation force test rewrites on every refactor (see Osherove, *The Art of Unit Testing*).

## Code Examples

```csharp
// Passive View — View exposes primitives; no Model knowledge
public class SongDetailView : Form, ISongDetailView
{
    public string Title  { get { return textBoxTitle.Text;  } set { textBoxTitle.Text  = value; } }
    public string Artist { get { return textBoxArtist.Text; } set { textBoxArtist.Text = value; } }
    public string AddGenre(string genre) { listBoxGenre.Items.Add(genre); }
}

// Passive View Presenter — DI'd deps; sets each field explicitly
public class SongDetailViewPresenter
{
    private readonly ISongDetailView _view;
    private readonly ISongRetriever _songRetriever;
    public SongDetailViewPresenter(ISongDetailView view, ISongRetriever songRetriever, IGenreRetriever genreRetriever)
    { _view = view; _songRetriever = songRetriever; /* ... */ loadGenres(); }

    public void ShowSong(int songId)
    {
        var song = _songRetriever.GetById(songId);
        _view.Title  = song.Title;   // chatty: one assignment per field
        _view.Artist = song.Artist;
        _view.Genre  = song.Genre;
    }
}
```
- **What it demonstrates**: Passive View's defining trait — Presenter pushes every value individually because the View knows nothing about the Song.

```csharp
// Supervising Controller — same Presenter, but View takes the Model
public void ShowSong(int songId) { _view.Song = _songRetriever.GetById(songId); }  // one line; View data-binds
```
- **What it demonstrates**: giving the View Model-knowledge collapses the Presenter to near-trivial code (the trade-off: sync logic now lives in the untested View).

## Reference Tables

| Aspect | Passive View | Supervising Controller | Presentation Model | MVC |
|---|---|---|---|---|
| View knows Model? | No | Yes | Via the PM | Yes |
| Interaction class | Presenter | Presenter | Presentation Model (is Model+Presenter) | Controller |
| Entry point | View | View | View | Controller |
| Data binding used | No (manual, field-by-field) | Yes | Yes (esp. WPF/MVVM) | Yes |
| Testability | Highest | High (view logic untested) | High | High |
| Downside | Very chatty, many tiny methods | Sync logic hides in View | Double sync (View↔PM↔domain) | Rewrite, not refactor |
| Best fit | Stateful (WinForms/WebForms), simple/buggy screens | Stateful + existing data binding | Complex state; WPF | Stateless greenfield web |

*MVC vs MVP rule of thumb: View-first = MVP; Controller-first = MVC. MVP suits brownfield (stateful WinForms/WebForms); MVC suits greenfield web.*

## Worked Example
**Refactoring an ASP.NET GridView page (BandList) to Supervising Controller.** Starting code-behind has `Page_Load` calling `bindPage()`, which uses a static `TwilightDB.GetData("twi_getArtists", ...)` and binds a DataSet straight to the grid — data access + display fused, untestable.

Steps (the "Don't shy away from objects" / move-don't-rewrite approach):
1. **Identify components**: Model = list of artists (a DataSet, for now); View = GridView + TextBox + Button; Presenter = everything else. Because the grid binds directly, choose **Supervising Controller**.
2. **Write the smallest test first**: assert you can construct `new BandListPresenter(view)` with a stubbed `IBandListView` and it isn't null — this fixes the decision that the Presenter takes an `IBandListView`.
3. **Make the View implement the interface**: `public partial class BandList : Page, IBandListView`; in the constructor `_presenter = new BandListPresenter(this);` (View creates Presenter and passes itself — they hold mutual references so MVP communication works; events/Event Aggregator can decouple this further).
4. **Move logic into the Presenter, leaving a seam**: `Page_Load` now calls `_presenter.ShowArtistList()`; the Presenter fetches data and calls back `_bandListView.BindTo(artistList)`; the View's `BindTo(DataSet)` just does `gridViewBands.DataSource = ...; DataBind();`.

Result: the Presenter has **no control references**, so it's unit-testable with a fake `IBandListView`. The ugly static `TwilightDB` call still sits in the Presenter — but now it's reachable by an integration test and can be teased apart later (Ch 11). The View has been reduced to "tell the presenter to do the work, then render what I'm handed."

## Key Takeaways
1. Most brownfield apps go bad in the UI — "all it takes is one demo application released to production." Separation of Concerns + SRP is the cure.
2. Split every non-trivial screen into Model, View, and Presenter/Controller; the View should be display-only and the only layer touching `System.Windows.Forms`/`System.Web.UI`.
3. Passive View = max testability but chatty; Supervising Controller = concise via data binding but some untested view logic; choose by how testable the screen needs to be.
4. Use screen-specific DTOs (not DataSets, not raw domain objects) as the Model to divorce UI from domain change; build them with a translation layer.
5. Refactor safely: define seams, **move code rather than rewrite it**, get a test in place before optimizing; write the presenter test first when you can.
6. Never expose UI controls outside the View and never let a Presenter reference a UI control library — that's the worst-of-both-worlds anti-pattern.
7. MVC is excellent but for **greenfield web** — for brownfield you rewrite, not refactor (broken URLs, subverted ViewState). Prefer the three MVP flavors.

## Connects To
- **Ch 7 (SRP / OO design)**: the UI is the most common place SRP is violated; these patterns reassert it screen-by-screen.
- **Ch 8 (Layering / seams)**: identifying Model/View/Presenter is drawing seams in the UI; DTOs sit in the translation layer introduced there.
- **Ch 9 (IoC / Dependency Injection)**: presenters receive their view and data dependencies via constructor injection — the wiring mechanism for these patterns.
- **Ch 11 (Data Access)**: the leftover static `TwilightDB.GetData` call and the `ISongRetriever`/`ISongRepository` question are resolved when the DAL is refactored next.
- **The Art of Unit Testing (Osherove)**: cited for avoiding over-specified tests when characterizing existing UI code.
