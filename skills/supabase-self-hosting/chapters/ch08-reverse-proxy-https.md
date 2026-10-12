# Chapter 8: Configure Reverse Proxy and HTTPS

## Core Idea
Production self-hosting needs HTTPS, and the recommended way is a reverse proxy (Caddy or Nginx) in front of the API gateway that terminates TLS — internal traffic stays HTTP. Pick Caddy for zero-config auto-TLS, Nginx for more control; self-signed certs are dev-only.

## Frameworks Introduced
- **Three TLS options**:
  - When to use Caddy: simplest — auto Let's Encrypt, HTTP→HTTPS redirect, WebSocket, HTTP/2+3. Override `docker-compose.caddy.yml`.
  - When to use Nginx+Certbot: more proxy control. Override `docker-compose.nginx.yml` (`jonasal/nginx-certbot` image); set `PROXY_DOMAIN`+`CERTBOT_EMAIL`.
  - When to use self-signed: dev/internal only — configure Kong directly for SSL on port 8443.
- **Proxy contract** (any proxy — HAProxy/Traefik/NPM work too):
  - Proxy to gateway on `:8000`; enable WebSocket (Realtime); add `X-Forwarded` headers; comment out gateway host-port bindings if proxy shares the Docker network; update the 3 URLs to HTTPS.
- **URL trio update**: `SUPABASE_PUBLIC_URL`, `API_EXTERNAL_URL`, `SITE_URL` all → `https://<your-domain>`.

## Key Concepts
- **TLS termination**: proxy holds the cert; backend stays HTTP. Internal `kong:8000` unchanged.
- **Envoy vs Kong in the proxy override**: if running Envoy, edit `docker-compose.caddy.yml`/`nginx.yml` to comment the `kong:` block and uncomment `api-gw:` (+ matching `depends_on`).
- **WebSocket upgrade**: Caddy auto; Nginx needs explicit `Upgrade`/`Connection` headers on `/realtime/v1/`.
- **Self-signed port**: Kong serves HTTPS on `8443`; URLs become `https://<your-domain>:8443`.

## Mental Models
- Think "proxy = TLS boundary": everything public is HTTPS:443, everything internal is HTTP:8000.
- A successful `curl -I https://<your-domain>/auth/v1/` returning `401` is the *success* signal (connected to Auth, just no key).

## Anti-patterns
- **Self-signed in production**: browser warnings + OAuth providers reject them.
- **Forgetting WebSocket on Nginx**: Realtime subscriptions silently fail.
- **Not restarting after URL change**: `API_EXTERNAL_URL` change needs `down && up -d` or OAuth callbacks break.
- **Mismatched OAuth callback**: provider callback must equal `API_EXTERNAL_URL` + `/auth/v1/callback`.

## Code Examples
```sh name=.env
SUPABASE_PUBLIC_URL=https://<your-domain>
API_EXTERNAL_URL=https://<your-domain>
SITE_URL=https://<your-domain>
PROXY_DOMAIN=your-domain.example.com    # Nginx
CERTBOT_EMAIL=admin@your-domain.example.com
```
```sh
docker compose -f docker-compose.yml -f docker-compose.caddy.yml up -d   # Caddy
docker compose -f docker-compose.yml -f docker-compose.nginx.yml up -d   # Nginx
curl -I https://<your-domain>/auth/v1/          # expect 401 = connected
docker logs supabase-caddy                       # or supabase-nginx
```
- **What it demonstrates**: the URL updates, both proxy launches, and the verify check.

## Reference Tables
Prereqs: domain DNS A-record → server public IP; ports 80 + 443 open.
| Option | Auto-TLS | WebSocket | Config file |
|---|---|---|---|
| Caddy | Yes (zero-config) | Auto | `volumes/proxy/caddy/Caddyfile` |
| Nginx+Certbot | Yes | Manual headers | `volumes/proxy/nginx/supabase-nginx.conf.tpl` |
| Self-signed | No (manual) | n/a | Kong env in `docker-compose.yml` |

## Worked Example — self-signed cert for dev (Kong SSL on 8443)
```sh
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout volumes/api/server.key -out volumes/api/server.crt \
  -subj "/CN=<your-domain>" && \
  chmod 640 volumes/api/server.key && chgrp 65533 volumes/api/server.key
```
Then in `docker-compose.yml`: comment Kong's HTTP port `${KONG_HTTP_PORT}:8000`, uncomment the cert volume mounts + `KONG_SSL_CERT`/`KONG_SSL_CERT_KEY`. Set the URL trio to `https://<your-domain>:8443`. Restart and verify with `curl -I -k https://<your-domain>:8443/auth/v1/` (`-k` accepts the self-signed cert). `ERR_CERT_AUTHORITY_INVALID` is expected for self-signed.

## Key Takeaways
1. Production = reverse proxy terminating TLS; backend stays HTTP.
2. Caddy = zero-config auto-TLS; Nginx = more control; self-signed = dev only.
3. Update all three URLs to HTTPS and restart after changing `API_EXTERNAL_URL`.
4. Any proxy works if it proxies `:8000`, supports WebSocket, and adds `X-Forwarded` headers.
5. For Envoy, swap the `kong:`/`api-gw:` blocks in the proxy override.
6. `401` from `curl -I https://.../auth/v1/` confirms a working connection.

## Connects To
- **Ch 4**: OAuth requires HTTPS; callback must match `API_EXTERNAL_URL`.
- **Ch 3**: Envoy as the gateway behind the proxy.
- **Ch 6**: `STORAGE_PUBLIC_URL`/`X-Forwarded-Prefix` for signed S3 URLs through the proxy.
