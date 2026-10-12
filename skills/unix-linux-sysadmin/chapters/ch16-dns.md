# Chapter 16: DNS — The Domain Name System

## Core Idea
DNS is a **distributed, hierarchical, cached database** mapping names ↔ IP addresses (and more). Each site stores data for its own hosts and cooperates to resolve others'. A query = (name, record type); the answer = a set of resource records (RRs). The system scales to billions of hosts via delegation (each domain delegates subdomains) and caching (answers cached for a TTL). Every host is a DNS *client*; running a server is increasingly optional (managed providers like Route 53/CloudFlare), but BIND still runs >75% of servers.

## Frameworks Introduced
- **The resolution chain**: resolver (client lib) → recursive name server → follows referrals from root → TLD (com/edu) → domain → authoritative server → answer, caching everything along the way.
- **Name-server taxonomy** (a server can play multiple roles per zone): **authoritative** (officially represents a zone) = **master/primary** (data from disk file) + **slave/secondary** (data via zone transfer); **caching-only** (no own data, just caches); **recursive** (follows referrals for you) vs **nonrecursive** (returns referrals); **forwarder** (queries on behalf of many clients).
- **Zone vs domain**: a zone = a domain minus its delegated subdomains. Each zone has exactly one SOA record and ≥1 (ideally ≥2, geographically separate) slaves.
- **Forward vs reverse mapping**: forward = name→IP (A/AAAA records); reverse = IP→name (PTR records under `in-addr.arpa`, with octets reversed).

## Key Concepts
- **`/etc/resolv.conf`**: client config — `search` domains (for unqualified names) + up to 3 `nameserver` lines. Listed servers must be **recursive** (resolvers don't follow referrals). Often auto-filled by DHCP.
- **`/etc/nsswitch.conf`**: decides DNS-vs-`/etc/hosts` order, e.g. `hosts: files dns` (hosts file first, fall back to DNS).
- **FQDN + trailing dot**: in zone files, a name ending in `.` is absolute; without it, the origin is appended. A missing dot turns `anchor.cs.colorado.edu` into `anchor.cs.colorado.edu.cs.colorado.edu` — a classic mistake.
- **TTL & caching**: each record's TTL controls cache lifetime (typical 1h–1d). **Negative caching** remembers failures (NXDOMAIN, no such record). Lower TTLs *a week before* a renumbering so old cached records expire first.
- **SOA timers**: serial (slaves refresh when master's is higher — must increase monotonically; forgetting to bump it = changes don't propagate), refresh, retry, expire (how long slaves serve without the master), minimum (negative-cache TTL).
- **Authoritative vs nonauthoritative answer** (`aa` flag in dig): authoritative comes from a zone's master/slave; cached answers are nonauthoritative (usually still correct).

## Mental Models
- **Externally-facing servers must be nonrecursive; resolv.conf servers must be recursive.** Public recursive servers are vulnerable to cache-poisoning; clients can't act on referrals so their configured servers must do the recursion.
- **Always bump the serial number** when editing a zone — it's the slaves' only signal to pull fresh data. Encode the date: `2017110200` = first change on 2017-11-02. (A too-large serial is painful to fix — sequence-space arithmetic or kill+reload slaves.)
- **Debug the delegation chain link by link.** `dig +trace` (or query each server with `@server`) from root → TLD → domain reveals exactly where resolution breaks. "If you can reach a host by IP but not by name, DNS is the culprit."
- **Use trailing dots deliberately** in zone files — their presence/absence changes meaning fundamentally.

## Anti-patterns
- **Editing zone data without incrementing the serial**: "your name server punishes you by failing to propagate changes."
- **A world-visible recursive server**: cache-poisoning risk — external authoritative servers should be nonrecursive.
- **Forgetting the trailing dot** on absolute names in zone files → doubled-origin names.
- **Active Directory DNS as an external server**: fine internally, never Internet-facing (security).
- **Single slave / co-located slaves**: when name service stops, all network access stops — put slaves on different networks, power circuits, and ideally sites.
- **Lame delegation**: parent NS records point to servers that aren't actually serving the zone — check delegations with `dig`.

## Code Examples
```sh
# Client config
# /etc/resolv.conf
search atrust.com booklab.atrust.com
nameserver 63.173.189.1
nameserver 174.129.219.225
# /etc/nsswitch.conf
hosts: files dns

# Debugging (dig from BIND; drill from NLnet for DNSSEC)
dig www.example.com A            # query default resolver
dig @8.8.8.8 example.com SOA     # query a specific server
dig +trace www.example.com       # follow delegation root->TLD->domain
dig -x 63.173.189.1              # reverse lookup
dig example.com NS               # authoritative name servers
# aa flag in output = authoritative answer; status NXDOMAIN = no such name;
# SERVFAIL = server config error
```
```
; Zone file resource records  [name] [ttl] [class] type data
$TTL 1d
$ORIGIN atrust.com.
atrust.com. IN SOA ns1.atrust.com. hostmaster.atrust.com. (
        2017110200 ; serial (bump on every edit! date-encoded)
        10800      ; refresh (slaves check master)
        1200       ; retry
        3600000    ; expire (serve without master)
        3600 )     ; minimum (negative-cache TTL)
        IN NS  ns1.atrust.com.
        IN NS  ns2.atrust.com.
ns1     IN A    63.173.189.1
        IN AAAA 2001:500:2f::f
nubark  IN A    63.173.189.1
        IN MX 10 mailserver.atrust.com.
www     IN A    192.168.0.1      ; multiple A records = round-robin DNS LB
        IN A    192.168.0.2
; reverse zone 189.173.63.in-addr.arpa:
1       IN PTR  nubark.atrust.com.
```

## Reference Tables
**Record types**: SOA (zone start, timers), NS (authoritative servers / delegate subdomain), A (name→IPv4), AAAA (name→IPv6), PTR (IP→name, reverse), MX (mail routing, with priority), CNAME (alias→canonical name), SRV (service location), TXT (text, e.g. SPF/DKIM), DS/DNSKEY/RRSIG/NSEC (DNSSEC). IN = Internet class (always).

**Parser directives** (zone files, column 1): `$TTL` (default TTL, must be first line), `$ORIGIN` (default domain appended to unqualified names — *doesn't revert* after `$INCLUDE`), `$INCLUDE`, `$GENERATE` (BIND only). `@` = current zone name.

**Query tools**: `dig`/`host`/`nslookup` (general), `drill`/`delv` (DNSSEC chains). Flags: `@server`, `-x` reverse, `+trace`/`-T` full chain, `any` = all *cached* records.

## Worked Example
**Trace `www.viawest.com` from the root.** (1) Query a root server: `dig @a.root-servers.net viawest.com soa` → status `NOERROR`, ANSWER 0, but an AUTHORITY section referring you to the gTLD `.com` servers (`a/b/c.gtld-servers.net`). The "recursion not available" warning confirms the root is nonrecursive. (2) `dig @c.gtld-servers.net viawest.com soa` → referral to `ns1/ns2.viawest.net` (the domain's authoritative servers). (3) `dig @ns1.viawest.net viawest.com soa` → now ANSWER 1 with the `aa` flag set — authoritative. (4) `dig @ns1.viawest.net www.viawest.com any` → reveals `www` is a `CNAME` to a DDoS-provider host. Each step followed a referral and observed cached TTLs (42d roots, 2d edu, etc.). A recursive server would do all this for you in one query — but link-by-link is how you *debug* a broken delegation.

## Key Takeaways
1. DNS is a distributed, delegated, cached hierarchy; queries follow referrals from root → TLD → domain unless answered from cache.
2. Configure every host as a client (`resolv.conf` recursive servers + `nsswitch.conf` order); running a server is optional.
3. A zone = domain minus subdomains, with one SOA, a master, and ≥2 well-separated slaves (data flows via zone transfer).
4. **Always bump the SOA serial** on edits, or slaves never update; mind trailing dots and `$ORIGIN`.
5. Tune TTLs deliberately — lower them before renumbering; negative caching remembers failures.
6. Debug with `dig`/`dig +trace` link by link; external servers nonrecursive, resolver-facing servers recursive.

## Connects To
- **Ch 13**: `/etc/resolv.conf`, hostnames as shorthand for IPs, ports (DNS on 53).
- **Ch 17**: single sign-on (Active Directory integrates DNS; `nsswitch.conf` and LDAP).
- **Ch 18**: email (MX records route mail).
- **Ch 19**: web hosting (A/AAAA/CNAME for sites, round-robin/load-balancer integration).
- **Ch 27**: security (DNSSEC, cache poisoning, recursive-server exposure).
