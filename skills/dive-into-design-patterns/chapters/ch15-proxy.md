# Chapter 15: PROXY

## Core Idea
Proxy is a structural pattern that provides a substitute or placeholder for another object, controlling access to it so you can run logic before or after a request reaches the real object — without the client or the real object knowing.

## Frameworks Introduced
- **Proxy**: A class sharing the same interface as a service object, holding a reference to it and delegating work after doing its own.
  - When to use (the popular variants): lazy initialization, access control, remote execution, logging, caching, and smart reference (dismiss/cleanup of an unused heavyweight).
  - How: reuse (or extract) the service interface; create a proxy with a field referencing the service; implement proxy methods to do extra work then delegate; optionally add a creation method/factory deciding proxy vs real service; optionally add lazy init.

## Key Concepts
- **Service Interface**: The contract both Service and Proxy implement, making them interchangeable.
- **Service**: The real class with the useful business logic.
- **Proxy**: Holds a reference to the service, manages its lifecycle, and inserts behavior around requests.
- **Virtual proxy (lazy initialization)**: Defers creating a heavyweight object until it's actually needed.
- **Protection proxy (access control)**: Passes the request through only if client credentials meet criteria.
- **Remote proxy**: Represents a service on a remote server, handling the network details locally.
- **Logging proxy**: Records each request before passing it to the service.
- **Caching proxy**: Stores results of recurring requests (using request params as cache keys) and manages the cache lifecycle.
- **Smart reference**: Tracks clients; dismisses the heavyweight service and frees resources when no clients remain.

## Mental Models
- **Real-World Analogy**: A credit card is a proxy for a bank account, which is a proxy for cash. All share the "make a payment" interface; the consumer avoids carrying cash, the merchant avoids robbery risk.
- Think of a proxy as a **stand-in with the same face** as the real object — callers can't tell the difference.

## Anti-patterns
- **Duplicating deferred-init/caching code across every client**: that's the smell Proxy removes by centralizing it in one class.
- **Over-applying Proxy**: it introduces many new classes (more complexity) and can delay the service response.

## Code Examples
```
class CachedYoutubeClass implements ThirdPartyYouTubeLib is
    private field service: ThirdPartyYouTubeClass
    private field listCache, videoCache
    field needReset
    constructor(service) is this.service = service

    method listVideos() is
        if (listCache == null || needReset)
            listCache = service.listVideos()
        return listCache

    method downloadVideo(id) is
        if (!downloadExists(id) || needReset)
            service.downloadVideo(id)

// Swap in the proxy transparently — same interface
class Application is
    method init() is
        aYouTubeService = new ThirdPartyYouTubeClass()
        aYouTubeProxy   = new CachedYouTubeClass(aYouTubeService)
        manager = new YouTubeManager(aYouTubeProxy)
        manager.reactOnUserInput()
```
- **What it demonstrates**: a caching proxy implements the same interface as the real downloader, returns cached results, and delegates only when a real request must fire — the GUI manager stays unchanged.

## Reference Tables
| Pros | Cons |
|------|------|
| Control the service object without clients knowing | Code may get more complicated (many new classes) |
| Manage service lifecycle when clients don't care | The service response might get delayed |
| Works even if the service isn't ready/available |  |
| Open/Closed: add new proxies without changing service or clients |  |

| Proxy type | Use it to... |
|------------|--------------|
| Virtual (lazy init) | Delay creating a heavyweight, rarely-used object until needed |
| Protection (access control) | Allow only clients with matching credentials through |
| Remote | Run a remote service locally, hiding network details |
| Logging | Keep a history of requests before delegating |
| Caching | Cache recurring request results (params as keys), manage cache lifecycle |
| Smart reference | Dismiss an unused heavyweight and free resources; reuse unmodified objects |

## Worked Example
A 3rd-party YouTube library (`ThirdPartyYoutubeClass`) downloads videos but re-downloads the same video every time — wasteful and slow. You can't edit it (closed/`final`). So you add `CachedYoutubeClass`, which implements the same `ThirdPartyYouTubeLib` interface, caches `listVideos`/`getVideoInfo`/`downloadVideo` results, and delegates to the real service only on cache miss. The `YoutubeManager` GUI is untouched because it works through the interface; `Application.init()` simply wires the proxy in place of the real service. This adds lazy loading + caching with zero changes to the library or the GUI.

## Key Takeaways
1. A proxy shares the service's interface, so it can substitute for the real object anywhere.
2. It inserts behavior before/after delegation without modifying the service class.
3. One proxy class removes duplicated access/init/cache logic scattered across clients.
4. Proxies usually own the service's full lifecycle (creation through disposal).
5. Pick the variant by intent: virtual, protection, remote, logging, caching, or smart reference.

## Connects To
- **Adapter** gives a different interface, **Proxy** the same interface, **Decorator** an enhanced interface.
- **Facade**: both buffer and self-initialize a complex entity, but Proxy shares the service's interface (interchangeable) while Facade does not.
- **Decorator**: similar composition-based structure, different intent — a Proxy usually manages its service's lifecycle itself, whereas a chain of Decorators is controlled by the client.
