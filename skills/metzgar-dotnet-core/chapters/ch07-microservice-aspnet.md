# Chapter 7: Creating a microservice

## Core Idea
A **microservice** owns a single piece of functionality, is individually deployable, is singularly responsible for its own datastore, and is replaceable behind a stable interface. This chapter builds a Markdown-to-HTML blog-post microservice with **ASP.NET Core** (MVC/Web API + controllers), tests it with **Curl**, makes it non-blocking with **async/await**, and backs it with **Azure Blob Storage** — talking to Azure over raw HTTP (no Azure SDK) so you see the HTTP request/auth mechanics directly.

## Frameworks Introduced
- **ASP.NET Core Web API / controllers**: Convention-based routing. MVC finds controllers by reflection; `Http*` attributes (`[HttpGet]`, `[HttpPost]`, `[HttpPut]`, `[HttpDelete]`) map HTTP verbs to action methods; method params bind from query string / route / body automatically. Use for REST services (Web API and MVC are merged in ASP.NET Core; WebForms is gone). Enable with `services.AddMvc()` in `ConfigureServices` and `app.UseMvc()` in `Configure`.
- **HttpClient**: The preferred .NET Core type for making outbound HTTP requests (`PostAsync`, `GetAsync`, `PutAsync`, `SendAsync`). Prefer over legacy `WebClient` for new code. Reuse a single instance (`static readonly`) rather than constructing per-request.
- **async/await for I/O-bound service work**: Frees the thread while waiting on network/disk I/O so the service handles more concurrent requests with fewer threads. Use on any action that reads a request body or calls another service.
- **Azure Blob Storage client (over raw HTTP)**: Store/retrieve BLOBs by issuing signed HTTP requests. Use when the microservice needs an isolated, externally-durable datastore. Requires a **SharedKey** auth header built from an HMAC-SHA256 signature over a canonicalized string.

## Key Concepts
- **Convention-based routing**: no manual URI parsing; `[Route("/")]` on the controller + verb attributes + param names do the wiring.
- **Result helpers match the HTTP spec**: `Content()`, `Created()`, `NoContent()` (and `Accepted`) return the semantically correct status code.
- **Streaming the body**: `Request.Body` is a `System.IO.Stream`; read it async (`ReadToEndAsync`) so slow/malicious uploads only hold a socket, not a thread. `StreamContent` lets you send a stream without buffering the whole payload in memory.
- **Configuration-driven secrets**: account name/key/endpoint/version come from `config.json` via `Microsoft.Extensions.Configuration` (`ConfigurationBuilder.AddJsonFile("config.json", false)` — `false` = not optional), registered as a DI singleton `IConfigurationRoot`.
- **Idempotency**: `PUT` is idempotent (repeat PUT of same BLOB → same 201, no adverse effect); `POST` is not (on timeout, state unknown — GET to verify before retry). Service uses POST only for the non-persisting convert operation.
- **DELETE status**: Azure returns **202 (Accepted)** because the BLOB is unavailable immediately but GC'd later; the service normalizes to **204 (No Content)** since it returns no entity.

## Mental Models
- **The service is a translating proxy**: client speaks simple HTTP to your service; your service re-signs and forwards to Azure Blob Storage with the right headers. `CreateRequest` + `GetAuthHeader` are the reusable core reused by every verb.
- **The signature string (`signme`) is positional**: blank lines are header slots you intentionally leave empty; canonicalized `x-ms-*` headers and the `/{account}/{path}` resource line follow. The server recomputes the same hash and compares — a mismatch tells you exactly what it hashed.
- **async is a service concern, not a client concern**: a one-shot console client can block on `.Result`; a service serving many clients cannot.

## Anti-patterns
- **Blocking on async in a service** — calling `.Result` / `.Wait()` on `PostAsync`/`ReadAsStringAsync`/`SendAsync` inside an action ties up a thread for the duration of a slow client, exhausting the thread pool. Use `async Task<IActionResult>` + `await`. (In a trivial single-purpose console client, blocking on `.Result` is acceptable.)
- **Synchronously reading the request body** (`reader.ReadToEnd()`) — same thread-starvation problem; use `await reader.ReadToEndAsync()`.
- **Exposing a secure resource through an insecure one** — the PUT-proxy example is illustrative only; don't ship it as-is (see *ASP.NET Core in Action*, Lock).
- **Putting content headers on the wrong collection** — `Content-Length` goes on `request.Content.Headers`, not `request.Headers`.
- **Using `long` instead of `long?` for content length** — a value type writes a default `0` into the signature for GETs; nullable `long?` writes nothing when null, so GET and PUT share one code path.

## Code Examples
```csharp
// Startup.cs — register MVC, the Markdown engine, and config as DI singletons
public void ConfigureServices(IServiceCollection services)
{
    services.AddMvc();
    var builder = new GfmEngineBuilder(new Options());
    var engine = builder.CreateEngine(new HtmlRenderer());
    services.AddSingleton<IMarkdownEngine>(engine);

    var configBuilder = new ConfigurationBuilder();
    configBuilder.AddJsonFile("config.json", false);   // false = not optional
    services.AddSingleton<IConfigurationRoot>(configBuilder.Build());
}
public void Configure(IApplicationBuilder app) => app.UseMvc();

// Controller action: return HTML from posted Markdown — ASYNC, non-blocking
[HttpPost]
public async Task<IActionResult> Convert()
{
    using (var reader = new StreamReader(Request.Body))
    {
        var markdown = await reader.ReadToEndAsync();
        var result = engine.Markup(markdown);
        return Content(result);      // text/html by default
    }
}

// Async HttpClient call INTO Azure Blob Storage from within GetBlob
[HttpGet]
public async Task<IActionResult> GetBlob(string container, string blob)
{
    var request = CreateRequest(HttpMethod.Get, container, blob);
    var response = await client.SendAsync(request);
    var markdown = await response.Content.ReadAsStringAsync();
    return Content(engine.Markup(markdown));
}

// Building the SharedKey auth header (config-driven)
private string GetAuthHeader(string verb, string path, string rfcDate, long? contentLen)
{
    var devStorage = BlobEndpoint.StartsWith("http://127.0.0.1:10000") ? $"/{AccountName}" : "";
    var signme = $"{verb}\n\n\n{contentLen}\n\n\n\n\n\n\n\n\n"
               + "x-ms-blob-type:BlockBlob\n"
               + $"x-ms-date:{rfcDate}\n"
               + $"x-ms-version:{ServiceVersion}\n"
               + $"/{AccountName}{devStorage}/{path}";
    string signature;
    using (var sha = new HMACSHA256(Convert.FromBase64String(AccountKey)))
        signature = Convert.ToBase64String(sha.ComputeHash(Encoding.UTF8.GetBytes(signme)));
    return $"SharedKey {AccountName}:{signature}";
}
```
- **What it demonstrates**: DI wiring of engine + config; an async controller action that never blocks; a reused `HttpClient` sending a signed request to Azure; the positional HMAC-SHA256 signature built from configuration values.

## Reference Tables

**BLOB operations → HTTP verb, attribute, URI, success handling**

| Operation | Verb / attribute | URI (query or route) | Azure success → returns |
|-----------|------------------|----------------------|-------------------------|
| Convert Markdown (no store) | POST `[HttpPost]` | `/` (body = markdown) | `Content(html)` |
| Download BLOB | GET `[HttpGet]` | `?container=c&blob=b` | `Content(markup(html))` |
| List BLOBs in container | GET `[HttpGet]` | `?container=c` (blob null) | XML, `Content(xml,"text/xml")` |
| List all containers | GET `[HttpGet]` | `/` (container & blob null) | XML |
| Upload / update BLOB | PUT `[HttpPut("{container}/{blob}")]` | route params | `Created(...)` on 201 |
| Delete BLOB | DELETE `[HttpDelete]` | `?container=c&blob=b` | `NoContent()` (204) on Azure 202 |

**Azure request headers**

| Concern | Where it goes | Value |
|---------|---------------|-------|
| BLOB type | `request.Headers` `x-ms-blob-type` | `BlockBlob` (omitted for list requests) |
| Date | `request.Headers` `x-ms-date` | `DateTime.UtcNow.ToString("R")` (RFC1123) |
| Version | `request.Headers` `x-ms-version` | `ServiceVersion` from config |
| Auth | `request.Headers` `Authorization` | `SharedKey {AccountName}:{signature}` |
| Content-Length (PUT) | `request.Content.Headers` | number only, 3 lines after verb in `signme` |
| List query params | encoded in URI + `signme` | `?restype=container&comp=list` (blobs) / `?comp=list` (containers) |

**config.json** (`IConfigurationRoot` singleton) supplies: `AccountName`, `AccountKey`, `BlobEndpoint`, `ServiceVersion`. Emulator/dev-storage uses `devstoreaccount1` + the well-known key and endpoint `http://127.0.0.1:10000/devstoreaccount1/`.

## Worked Example
Reconstruct the Markdown microservice end-to-end.

1. **Prove the library**: `dotnet new console` in `MarkdownLiteTest`, add `Microsoft.DocAsCode.MarkdownLite`. `new GfmEngineBuilder(new Options()).CreateEngine(new HtmlRenderer()).Markup(source)` renders Markdown → HTML string (no `<html>`/`<body>` wrappers — ideal for templating).
2. **Create the service**: `dotnet new web` in `MarkdownService`; project SDK `Microsoft.NET.Sdk.Web`, reference `Microsoft.AspNetCore.All` + Markdown Lite. `Program.cs` = `WebHost.CreateDefaultBuilder(args).UseStartup<Startup>().Build().Run()` (Kestrel). `Startup` registers MVC + engine (DI singleton). `MdlController` (`[Route("/")]`) receives `IMarkdownEngine` by constructor injection and exposes `[HttpPost] Convert()`.
3. **Test with Curl** (no client code yet):
   ```bash
   curl -X POST --data-binary @test.md http://localhost:5000
   ```
   Use `--data-binary` (not `-d`) to preserve newlines. A browser GET returns 404 because only POST exists.
4. **Client with HttpClient** (console, blocking OK here):
   ```csharp
   var client = new HttpClient();
   var response = client.PostAsync("http://localhost:5000",
       new StreamContent(new FileStream("test.md", FileMode.Open))).Result;
   Console.WriteLine(response.Content.ReadAsStringAsync().Result);
   ```
5. **Make the service async**: rewrite `Convert` to `async Task<IActionResult>` with `await reader.ReadToEndAsync()` so slow uploads hold only a socket.
6. **Back it with Azure Blob Storage (config-driven)**: add `config.json` (copied to output) with the four keys; register `IConfigurationRoot` in DI; read values in the controller ctor. Add `[HttpGet] GetBlob(container, blob)` that builds a signed request via reusable `CreateRequest` → `GetAuthHeader` (HMAC-SHA256 over `signme`), `await client.SendAsync`, then `engine.Markup` the result. Test: `curl "http://localhost:5000?container=somecontainer&blob=test.md"` (quote the URL on Windows — `&` is special).
7. **Upload (isolate the datastore)**: `[HttpPut("{container}/{blob}")] PutBlob` reads `Request.ContentLength`, sets `request.Content = new StreamContent(Request.Body)`, adds `Content-Length` to `Content.Headers`, returns `Created(...)` on 201.
   ```bash
   curl -X PUT --data-binary @test.md http://localhost:5000/somecontainer/foo.md
   ```
8. **List**: let `blob`/`container` be null in `GetBlob`; null blob → list blobs (`?restype=container&comp=list`, `text/xml`), null container → list containers (`?comp=list`). `GetAuthHeader` gains `listBlob`/`listContainer` flags that append `comp:list` / `comp:list\nrestype:container` and drop the `x-ms-blob-type` line.
9. **Delete**: `[HttpDelete] DeleteBlob` sends a DELETE; Azure returns 202 → service returns `NoContent()` (204).

Service now covers GET, PUT, POST, DELETE (not PATCH — Azure Blob Storage doesn't support it).

## Key Takeaways
- Use `HttpClient` for outbound calls; `Http*` attributes for inbound routing; let ASP.NET Core bind params from query/route/body and access the raw `Request.Body` stream when needed.
- Make service actions `async`/`await` for all I/O — never block on `.Result`/`.Wait()` in a service.
- A microservice controls its own datastore; here that means signing raw HTTP requests to Azure Blob Storage with a config-driven SharedKey HMAC-SHA256 header.
- Result helpers (`Content`, `Created`, `NoContent`, `Accepted`) map cleanly to HTTP semantics; Curl is the fastest way to exercise a service before writing a client.

## Connects To
- **Ch 2**: `dotnet new web`, **Kestrel**, and the `Program.cs` / **Startup** host-builder pattern — this chapter adapts that website template into a web-service-only project.
- **Ch 6**: **dependency injection** via `Microsoft.Extensions.DependencyInjection` (`AddSingleton` for the engine and `IConfigurationRoot`) and `Microsoft.Extensions.Configuration` (`config.json`) reused verbatim.
- **Ch 8**: debugging this service across platforms (Visual Studio debuggers, WinDBG/CDB, LLDB, SOS) when the HTTP/auth wiring misbehaves.
