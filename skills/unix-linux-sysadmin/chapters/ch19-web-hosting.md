# Chapter 19: Web Hosting

## Core Idea
The web runs on **HTTP** — a stateless client/server request/response protocol — and at scale on a **distributed stack** of cooperating components (web servers, load balancers, caches, CDNs, app servers). Each layer must be redundant across regions to survive failures, load spikes, and attacks. Understanding HTTP transactions, virtual hosts, TLS, and the proxy/cache/load-balancer roles is core sysadmin competency; the cloud increasingly provides these as managed services (build-vs-buy: prefer buy).

## Frameworks Introduced
- **HTTP transaction structure**: request (verb + path + version, then headers, blank line, body) ↔ response (status line `HTTP/1.1 200 OK`, headers, blank line, payload). Same shape both directions.
- **The web application stack** (each layer redundant): user → load balancer → cache/reverse proxy → web server → app server → database. Requests resolve as high in the stack as possible; only DB-needing requests traverse all layers.
- **Proxy taxonomy**: load balancer, web application firewall, and cache are all specialized **proxies** (intermediaries that receive, maybe process, and relay requests). A web server proxies to app servers.
- **Load-balancing algorithms**: round robin (fixed rotation), load equalization (fewest active connections), partitioning (hash client IP → same server, for session stickiness).

## Key Concepts
- **URL structure**: `scheme://[user:pass@]host[:port][/path][?query][#anchor]`. http→80, https→443. Never embed passwords/sensitive data in URLs (logged, bookmarked, in `ps`).
- **HTTP methods**: GET (safe, retrieve — most common), HEAD (metadata only), POST (apply data), PUT (replace, idempotent), DELETE, OPTIONS. "Safe" verbs shouldn't change server state.
- **Status classes**: 1xx info, 2xx success (200 OK, 201 Created), 3xx redirect (301/302), 4xx client error (403, 404), 5xx server error (503).
- **Virtual hosts**: the **Host header** (required in HTTP/1.1) lets one server/IP host many sites. With TLS, **SNI** (Server Name Indication) sends the hostname in the TLS handshake so the server picks the right certificate *before* reading the Host header.
- **Connection reuse**: TCP handshakes are expensive (a full round-trip of latency); **keep-alive/persistent** connections (default in HTTP/1.1) reuse one connection for many requests. **HTTP/2** adds multiplexing (interleaved transactions on one connection) and binary framing — but is TLS-only in major browsers.
- **TLS**: a layer between TCP and HTTP; verifies server identity and encrypts URL/headers/payload (attackers see only host:port). (SSL is its deprecated predecessor — "SSL" colloquially means TLS.)
- **Cache types**: browser cache, proxy cache (edge of org network — active via browser config or passive "intercepting proxy"), reverse proxy cache (in front of origin servers). **CDN** = globally distributed edge servers, routed via DNS to the nearest node.

## Mental Models
- **Build vs buy: outsource to the vendor unless it's a core competence.** A managed load balancer (AWS ELB) is created in seconds and needs no patching/tuning; running your own means OS management, config, security patches, and failure-handling glue. "Avoid building unless the function is a core competence for your business."
- **No single server can be highly available.** One box exposes users to every hiccup and blocks zero-downtime updates; past a load threshold performance *craters* abruptly. Use a load balancer (run them in pairs so they aren't themselves a SPOF).
- **Caches trade freshness for speed — and cause subtle bugs.** Debug stale content by `curl`-ing each hop (origin → reverse proxy → proxy → browser) directly; don't assume a no-cache request was honored unless you can prove it server-side.
- **A web API is just HTTP by convention.** REST = explicit HTTP verbs + directory-like paths + (usually) JSON; far simpler than the heavy XML-based SOAP it replaced.

## Anti-patterns
- **Passwords/sensitive data in URLs or query strings**: logged in plaintext everywhere — put credentials in headers or request bodies; HTTP basic auth only over HTTPS (it's not self-securing).
- **Single web server for production**: no HA, no zero-downtime updates, catastrophic under load — front with a load balancer.
- **Single load balancer**: becomes the SPOF — run in pairs (active/passive or both-active).
- **Assuming a cache honored your refresh**: verify on the server; stale caches at any layer serve out-of-date content.
- **Caching HTTPS without TLS termination at the cache**: encrypted payloads can't be cached unless the cache decrypts them.
- **Elastic Beanstalk for complex production multi-service workloads**: fine for prototyping, but customization is tedious/proprietary.

## Code Examples
```sh
# curl: the command-line HTTP client
curl -s -v -o /dev/null http://admin.com        # -v shows request(>)/response(<) headers
curl -H "Host: www.admin.com" 54.84.253.153     # set Host header to test by IP, bypass DNS
curl -O http://example.com/file.tar.gz          # download to current dir
curl -H "Cache-Control: no-cache" http://...    # request a cache refresh (=Shift-Reload)
curl https://api.spotify.com/v1/artists/ID | jq '.'   # REST API → JSON, pretty-print with jq

# Raw HTTP request (HTTP/1.x is plain text)
# GET /index.html HTTP/1.1
# Host: www.admin.com        <- only required request header
# (blank line)

# Apache httpd control
apachectl start|stop|graceful|status   # vendor-customized wrapper around httpd
```

## Reference Tables
**HTTP methods**: GET (safe), HEAD (safe, metadata), POST (apply data), PUT (replace, idempotent), DELETE, OPTIONS (safe).

**Stack components & examples**: app server (Unicorn, Tomcat), cache (Varnish, Squid, NGINX), load balancer (HAProxy, NGINX, AWS ELB, F5), web app firewall (ModSecurity), web server (Apache httpd, NGINX, H2O).

**Web servers**: Apache httpd (~46%, reference impl, modular, MPMs — use `event`) vs NGINX (~20%, faster, simpler config — recommended for production) vs H2O (HTTP/2-native, newer). Node.js/Go embed their own servers.

**Cloud hosting tiers**: IaaS (raw VMs + your own NGINX/HAProxy) · PaaS (App Engine, Elastic Beanstalk, Heroku — upload code, vendor runs it, less flexibility) · static hosting (S3 + CDN) · serverless (Lambda + API Gateway + S3).

## Worked Example
**Debug "the site shows old content."** A cache somewhere in the path is serving stale data. The fix is to query each hop directly with `curl` and compare. (1) `curl` the **origin** server directly (by its real IP, with `-H "Host: site.com"` to bypass DNS/load balancer) — if it's fresh, the origin is fine. (2) `curl` the **reverse proxy cache** — if stale, it hasn't revalidated. (3) `curl` the org's **proxy cache**, then check the **browser cache**. At each layer, `curl -H "Cache-Control: no-cache"` politely requests a refresh — *but conformant caches obey and non-conformant ones don't*, so don't trust it: prove the refresh happened on the server. The lesson: caches make the web fast but introduce a multi-layer freshness problem best isolated hop-by-hop.

## Key Takeaways
1. HTTP is stateless request/response; know verbs (GET/POST/PUT/DELETE), status classes (2/3/4/5xx), and the required Host header.
2. Production web hosting is a redundant, multi-region stack of proxies: load balancer → cache → web server → app server → DB.
3. Virtual hosts (Host header + SNI for TLS) consolidate many sites on one server/IP; always use TLS, never put secrets in URLs.
4. Load balancers (in pairs) give HA, rolling updates, and health checks; caches/CDNs cut latency and origin load but risk stale content — debug hop by hop.
5. HTTP/1.1 keep-alive and HTTP/2 multiplexing amortize expensive TCP handshakes.
6. In the cloud, prefer managed services (ELB, S3 static hosting, Lambda+API Gateway serverless) over building — unless it's a core competence.

## Connects To
- **Ch 16**: DNS (virtual host names, CDN routing, CNAME to cloud endpoints).
- **Ch 9**: cloud (managed load balancers, PaaS, serverless, regions/zones for HA).
- **Ch 27**: security (TLS, WAF, DDoS via CDN, basic-auth caveats).
- **Ch 7**: web languages (Ruby/Python/Go scripting) and JSON/`jq` tooling.
- **Ch 18**: shared TLS/cert concerns and HAProxy.
