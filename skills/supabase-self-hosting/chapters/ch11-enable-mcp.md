# Chapter 11: Enabling MCP Server Access

## Core Idea
The self-hosted MCP server runs behind the API gateway with **all connections denied by default** (no OAuth 2.1 yet, not Internet-safe). To use it you allow-list the Docker bridge gateway IP at the gateway and reach it through a VPN or SSH tunnel — never expose it publicly.

## Frameworks Introduced
- **Network-restricted access model**: MCP must never be Internet-reachable; access only via VPN to the Studio host or SSH tunnel from your machine.
- **Allow-list the bridge gateway IP** (Kong or Envoy):
  - When to use: enabling local MCP access through an SSH tunnel.
  - How: find the bridge gateway IP (`docker inspect supabase-kong`/`supabase-envoy` `.Gateway`), add it to the `/mcp` allow rule, restart the gateway.
- **Per-gateway edit**:
  - Kong: in `kong.yml` comment out `request-termination`, enable `cors` + `ip-restriction` with your IP in `allow` (keep `deny: []`).
  - Envoy: in `lds.template.yaml` comment the DENY `rbac` block on `/mcp`, uncomment the ALLOW policy, add your IP under `principals` (keep `127.0.0.1`/`::1`).

## Key Concepts
- **Docker bridge gateway IP**: the source IP when tunneling into the Studio container (e.g. `172.18.0.1`) — this is what you allow-list.
- **SSH tunnel**: `ssh -L localhost:8080:localhost:8000 you@host` forwards local `:8080` → host `:8000`.
- **YAML whitespace sensitivity**: indentation must be preserved or the config fails to load.
- **MCP client config**: point at the tunnel URL `http://localhost:8080/mcp`.

## Mental Models
- Treat MCP as a privileged internal tool behind a locked door: the allow-list is the lock, the SSH tunnel/VPN is the only key. No public exposure, ever.

## Anti-patterns
- **Exposing MCP to the Internet**: no auth — never do it.
- **Breaking YAML indentation when editing**: gateway won't load the config.
- **Removing `deny: []` (Kong)**: keep it — the instructions are explicit.
- **Forgetting to restart the gateway**: edits don't apply until restart.

## Code Examples
```sh
# Find the bridge gateway IP
docker inspect supabase-kong \
  --format '{{range .NetworkSettings.Networks}}{{println .Gateway}}{{end}}'   # e.g. 172.18.0.1
# (Envoy: docker inspect supabase-envoy ...)

# Tunnel local 8080 -> host 8000
ssh -L localhost:8080:localhost:8000 you@your-supabase-host
```
```json
{ "mcpServers": { "supabase-self-hosted": { "url": "http://localhost:8080/mcp" } } }
```
- **What it demonstrates**: discovering the IP, tunneling, and client wiring.

## Reference Tables
| Gateway | File | Edit |
|---|---|---|
| Kong | `volumes/api/kong.yml` | comment `request-termination`; enable `cors` + `ip-restriction` `allow:` (keep `deny: []`); restart `kong` |
| Envoy | `volumes/api/envoy/lds.template.yaml` | comment DENY `rbac`, uncomment ALLOW policy, add IP to `principals`; restart `api-gw` |

Steps: 1) find bridge IP → 2) allow-list it → 3) restart gateway → 4) SSH tunnel → 5) client config → 6) test.

## Worked Example — Kong allow-list block
```yaml name=volumes/api/kong.yml
- name: mcp
  url: http://studio:3000/api/mcp
  routes:
    - name: mcp
      strip_path: true
      paths: [/mcp]
  plugins:
    #- name: request-termination          # <- commented out
    - name: cors
    - name: ip-restriction
      config:
        allow:
          - 127.0.0.1
          - ::1
          - 172.18.0.1                     # <- your Docker bridge gateway IP
        deny: []                           # <- do NOT remove
```
Then `docker compose restart kong`, open the SSH tunnel, and smoke-test:
```sh
curl http://localhost:8080/mcp -X POST \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "MCP-Protocol-Version: 2025-06-18" \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-06-18","capabilities":{"elicitation":{}},"clientInfo":{"name":"test-client","title":"Test Client","version":"1.0.0"}}}'
```

## Key Takeaways
1. MCP is denied by default and has no auth — never expose it to the Internet.
2. Access only via VPN or SSH tunnel.
3. Allow-list the Docker bridge gateway IP (Kong `ip-restriction` / Envoy RBAC ALLOW).
4. Preserve YAML indentation; keep loopback entries (and Kong's `deny: []`).
5. Restart the gateway after editing.
6. Point the MCP client at the tunnel URL `http://localhost:8080/mcp`.

## Connects To
- **Ch 3**: Envoy `/mcp` route is DENY by default via RBAC.
- **Ch 8**: VPN/SSH as the secure access path (not public HTTPS).
- **Ch 1**: Studio container hosts the MCP endpoint at `/api/mcp`.
