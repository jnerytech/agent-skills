# Chapter 12: Risk and corruption: Managing external system dependencies

## Core Idea
External systems (third-party libraries, web services, COM components) are risk you don't control; insulate yourself by isolating each dependency behind an anti-corruption layer of your own design, so a change to the external interface forces a change in exactly one place instead of everywhere.

## Frameworks Introduced
- **Anti-Corruption Layer for external systems**: a layer of code you control inserted between your application and a third-party dependency, so your code never talks to the dependency directly. "A long-winded way of saying 'abstraction'."
  - When to use: any external dependency that is volatile, called from many places, has a cumbersome interface, or could force you to change when it changes.
  - How: define an interface/class you own (proxy/adapter/façade); route all calls to the dependency through it; inject it (Ch 9 IoC / poor-man's DI); translate the dependency's types into types you prefer at the boundary.
  - Why it works / failure mode: centralizes "nasty code" so changes are focused and retesting is contained. Failure mode: if you must change your layer's public interface every time the wrapped object changes, you aren't hiding the dependency, "merely sugar-coating it."
- **Risk-based abstraction decision**: don't wrap everything — decide by assessing the dependency's risk.
  - When to use: deciding whether a given external system warrants a layer.
  - How: ask three questions — How stable/reliable is it? What's the effort if it changes (dozens of classes vs. isolated)? Is it run-time or compile-time? Add the layer when you're already touching the code (upgrade, bug fix, new feature), not preemptively.
  - Why it works: refactor on an as-needed basis; "only do this if you are feeling pain."

## Key Concepts
- **Compile-time dependency**: resolved at build (third-party libs/controls); lower risk because you must consciously swap the version to break.
- **Run-time dependency**: resolved while running and usually outside your control (web services); volatile — if it changes, you may be forced to change with it.
- **Dynamically loaded libraries**: counted as compile-time dependencies because you still control them in your build process and can test them.
- **Anti-corruption layer**: a layer between two layers that protects the top from changes to the bottom (introduced Ch 8).
- **Intent-revealing naming**: name wrapper methods after the caller's goal (e.g., `OpenDocument(path)`), hiding the dozen optional parameters of the real call.
- **Hard boundary**: a transport edge such as a web service; keep code in the boundary minimal and delegate work to testable classes.
- **Limits of isolation**: you minimize, not eliminate, risk — a vendor going bankrupt or a fundamentally changed interface can still break you.

## Mental Models
- Use an anti-corruption layer when you call a third-party component from many screens/classes — change one place, not all of them.
- Treat any code you don't control as if you purchased it (even an internal team's API): no control over its release planning means it's a point of change and therefore risk.
- Use the risk questions (stability, change-effort, run-time vs compile-time) when deciding whether to abstract; don't wrap stable things like `TextBox` or a well-isolated O/RM.
- Wrap COM/Office interop the moment a parameter-heavy API or version differences threaten your sanity — "made for wrapping."

## Anti-patterns
- **Hard-wiring third-party calls everywhere**: the same grid/web-service called directly across the UI means a breaking change forces error-prone edits in every location.
- **Naming classes after the pattern** (e.g., `TwilightStarsProxy` once it also adapts): a proxy that converts types is now also an adapter; don't hard-wire class names to patterns.
- **"Lipstick on a pig"**: wrapping ugly code instead of fixing it as a permanent cop-out — at least add tests before hiding it behind an interface.
- **Hybrid migration trap**: introducing an object-returning method beside the old DataSet one, then never finishing — leaves developers unsure which to call (mitigate with `[Obsolete]`).
- **Fat web services**: putting all logic in the ASMX/WCF method rather than delegating to a testable translator class.

## Code Examples
```csharp
// Listing 12.15 - the façade interface the form sees
public interface ISongRepository
{
    List<Song> GetAllFrom( string folder );
}

// Listing 12.16 - implementation hides two different libraries + recursion
public List<Song> GetAllFrom( string folder )
{
    var songs = GetWmasFromFolder( folder );
    songs.AddRange( GetWmasFromSubfolders( folder ) );
    songs.AddRange( GetMp3s( folder ) );
    return songs;
}
```
- **What it demonstrates**: a façade collapses two incompatible metadata libraries (UltraID3 for MP3, MediaDataManager for WMA) and subfolder handling into one clean call the form makes — components can now be upgraded or swapped behind it.

```csharp
// Listing 12.3 - quick-and-dirty proxy wrapping a web service
public class TwilightStarsProxy
{
    public DataSet GetTours( )
    {
        var client = new TwilightStarsSoapClient( );
        return client.GetTours( );
    }
}
```
- **What it demonstrates**: the minimal anti-corruption layer — if the service later returns objects instead of DataSets, only the proxy changes, and it can translate back to the DataSet the controls expect.

## Reference Tables
Decision: should I add an anti-corruption layer?

| Question | Lean toward wrapping | Lean toward leaving it |
|---|---|---|
| Stability | Changes often / unreliable | Very stable (mature O/RM, built-in controls) |
| Change effort | Spread across many classes | Isolated to a small area |
| Type | Run-time (forced to update) | Compile-time (can ignore new version) |
| Pain now? | Hitting bugs/upgrade | Working fine — wait until you touch it |

## Worked Example
A Windows Forms ticket app reads the Twilight Stars web service from three tab controls, each instantiating `TwilightStarsSoapClient` directly in `OnLoad` and consuming a `DataSet`. When the vendor announces it will switch the service to return serializable objects, every control would have to change in lockstep with the vendor's deployment. The fix: insert `TwilightStarsProxy` (Listing 12.3) exposing the same methods; controls instantiate the proxy instead of the SOAP client (Listing 12.4). Now the vendor's breaking change is absorbed in one class — the proxy converts the new objects back into the `DataSet` the controls expect. Going further, the team extracts an `ITwilightStarsProxy`, refactors each control into Model-View-Presenter (Supervising Controller, since DataSets), and injects the proxy via poor-man's DI (Listing 12.5), making the presenter testable without a live service. The same shape recurs in the Office example: wrap `Excel.Workbooks.Open` (15 `Missing.Value`-laden parameters, Listing 12.17/12.18) in an `ExcelFacade.OpenDocument(path)` so version differences and the unreadable signature live in one place.

## Key Takeaways
1. No application is an island — external integration is a given, and done wrong it turns an app "brown in a hurry."
2. Distinguish compile-time (lower risk, ignorable) from run-time (volatile, may force you to change) dependencies; the mitigation is the same, the urgency differs.
3. The single technique is "another layer of indirection" you control — proxy, adapter, or façade are just intent variations on it.
4. An anti-corruption layer lets you test against it, simplify/alter the interface, swap implementations, and absorb breaking changes in one location.
5. Minimize, don't eliminate — and don't abstract everything; use the risk questions and add layers as you touch code, not preemptively.
6. The boundary rule: keep web-service/transport code lean and delegate work to a testable class (e.g., `WebServiceTranslator` shared by ASMX and WCF).
7. The same techniques apply to internal dependencies you don't control — treat any awkward class as a third-party component.

## Connects To
- **Ch 8**: anti-corruption layer is introduced there; Ch 12 applies it concretely to external systems.
- **Ch 9**: inject the anti-corruption layer via IoC; the Common Service Locator is itself an anti-corruption layer over IoC containers.
- **Ch 11**: `SongRepository` mirrors the repository/abstraction pattern from data access.
- **Ch 7**: it's all "abstraction"; avoid hard-wiring class names to patterns (Adapter vs Proxy).
- **Ch 10**: MVP / Supervising Controller refactor used to make the web-service controls testable.
- **Ch 4**: write tests for any code you add or modify — the trigger for adding a layer incrementally.
