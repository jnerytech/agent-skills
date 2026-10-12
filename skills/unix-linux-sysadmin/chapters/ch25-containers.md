# Chapter 25: Containers

## Core Idea
A container is an **isolated group of processes** with a private root filesystem and process namespace, **sharing the host kernel** (unlike a VM). Containers solve software *packaging*: a **container image** bundles an app + all its version-pinned dependencies + runtime into one portable file (~hundreds of MB or less). Any host with a compatible engine runs it identically — that portability is the main reason for containers' popularity. There's no magic: containers are a fusion of long-existing Linux kernel features.

## Frameworks Introduced
- **The kernel features that make containers work**: **namespaces** (isolate filesystem mounts, PIDs, networking — a private view of the system), **cgroups** (limit/prioritize CPU/memory — stop runaway containers), **capabilities** (grant specific privileged operations), **seccomp** (restrict syscalls, finer than capabilities).
- **Union filesystem + copy-on-write**: an image is read-only union-mounted layers; a running container adds a thin read/write layer on top. Many containers share immutable base layers → storage-efficient, fast startup. Each layer is content-hashed for integrity.
- **Docker architecture**: `docker` (CLI client) talks to `dockerd` (persistent daemon that creates containers, network plumbing, manages `/var/lib/docker`) over a UNIX socket or TLS TCP. Images come from a **registry** (default Docker Hub; pull/push).
- **Dockerfile**: a recipe — each instruction commits a new layer. `FROM` (base, first) → `RUN`/`COPY`/`ADD`/`ENV` → `EXPOSE` → `CMD` (default foreground process).

## Key Concepts
- **Image vs container**: image = read-only template; container = image + writable layer, running (or stopped). Same image can have multiple tags (`debian:jessie` and `debian:latest` may share an ID).
- **Shared kernel**: `uname -r` is identical inside and outside the container — containers must run the host's kernel (distro userland may differ).
- **PID namespacing**: container processes can't see host/other-container processes; the host *can* see container processes (with different PIDs). The container's first command is PID 1.
- **Foreground requirement**: a container exits when its PID-1 process exits — daemons must run in the foreground (`nginx -g 'daemon off;'`); use `supervisord` as a lightweight init for multi-process containers.
- **Volumes**: writable dirs maintained *outside* the union filesystem — persist when the container is removed, shareable. **Bind mounts** (`-v /host:/container`) map a host dir in (host contents supersede). For data-intensive apps (databases), use volumes, not the overlay layer.
- **Networking**: default **bridge** (`docker0`, private namespaced IPs, host proxies via iptables, `-p host:container` maps ports), **host** (shares host stack — faster but port conflicts + less isolation), **none** (no networking).
- **Storage drivers**: overlay (modern default), aufs (deprecated), devicemapper (RHEL, buggy history), btrfs/zfs (native CoW, good but distro-limited), vfs (no union — slow but robust). Stick with the distro default unless you're an expert.

## Mental Models
- **Containers are cattle: created and destroyed at a moment's notice.** The ideal is a fleet of identical `dockerd` hosts where any container deploys anywhere. **Persistent data breaks this** — volumes couple a container to a host (an "impedance mismatch"); accept it where apps genuinely need state, and back volumes with cloud block storage (EBS) for snapshots/portability.
- **Smaller base images are better.** The base should have what you need and nothing more (Alpine ~5MB but possible lib incompatibilities; Ubuntu ~188MB). Shared bases mean less to download and faster starts. *Vet the base's Dockerfile* — it may carry vulnerable or surprising dependencies.
- **Log to STDOUT, run in foreground.** The container convention: redirect app logs to `/dev/stdout` (so `docker logs` works) and run the main process in the foreground so PID 1 stays alive.
- **`docker` is just a client; only `dockerd` touches registries/containers.** Understanding the client/daemon split clarifies remote operation and security.

## Anti-patterns
- **Adding users to the `docker` group**: socket access = effective root — a significant security risk. Use `sudo` to control `docker` instead.
- **Plain HTTP to a remote `dockerd`**: "you may as well hand out root privileges freely to anyone on your network." Always use TLS (port 2376); enable `DOCKER_CONTENT_TRUST=1` to validate image integrity/publisher.
- **Daemonizing the app inside a container**: it forks, PID 1 exits, the container dies. Run the process in the foreground.
- **Heavy reliance on the overlay layer for database data**: poor for data-intensive apps — use volumes.
- **Leaving stopped containers around**: poor hygiene, name collisions on reuse — `docker rm` them (or `docker run --rm` for ephemeral).
- **Storing secrets in `ARG`**: build-time args aren't meant for secrets.

## Code Examples
```sh
# Lifecycle
docker pull debian                          # download image (latest tag default)
docker images ; docker ps ; docker ps -a    # images / running / all containers
docker run debian /bin/echo "Hello"         # run a command, container exits when it ends
docker run --hostname debian -it debian /bin/bash   # interactive shell
docker run -p 80:80 --name nginx -d nginx   # daemonized, map host:container port
docker logs -f nginx                        # stream container STDOUT (like tail -f)
docker exec -ti nginx bash                  # new process in a running container
docker stop nginx && docker rm nginx        # stop + remove
docker inspect -f '{{json .NetworkSettings.Networks.bridge}}' nginx

# Volumes
docker run -v /data --rm -d nginx                  # named volume (persists in /var/lib/docker/volumes)
docker run -v /mnt/data:/data --rm -d nginx        # bind mount (host dir wins)

# Remote daemon — always TLS
export DOCKER_HOST=tcp://10.0.0.10:2376
export DOCKER_CONTENT_TRUST=1
```
```dockerfile
# Dockerfile — each instruction = a layer
FROM debian:jessie
ENV NGINX_VERSION 1.10.3-1~jessie
RUN apt-get update && apt-get install -y nginx=${NGINX_VERSION} \
    && rm -rf /var/lib/apt/lists/*
RUN ln -sf /dev/stdout /var/log/nginx/access.log   # log to STDOUT (container convention)
EXPOSE 80 443
CMD ["nginx", "-g", "daemon off;"]                 # foreground process
```
```sh
docker build -t nginx:ulsah .               # build from Dockerfile in cwd
docker push registry.admin.com/debian:jessie   # tag with registry URL, docker login first
```

## Reference Tables
**Key Dockerfile instructions**: `FROM` (base, first), `RUN` (run + commit), `COPY`/`ADD` (files in), `ENV` (env vars for build + runtime), `ARG` (build-only, not secrets), `EXPOSE` (declare ports), `CMD` (default process), `VOLUME`, `WORKDIR`, `USER`, `STOPSIGNAL`.

**Common `docker` subcommands**: `run`, `ps`, `images`, `pull`/`push`, `start`/`stop`, `rm`/`rmi`, `exec`, `logs`, `inspect`, `info`, `build`, `top`.

**Networks**: bridge (default, private IPs + iptables port mapping), host (shares host stack), none (manual). Storage drivers: overlay (modern default), aufs (deprecated), devicemapper (RHEL), btrfs/zfs (CoW), vfs (no union).

## Worked Example
**Run a customized NGINX container and reach it.** (1) `docker run -p 80:80 --hostname nginx --name nginx -d nginx` — Docker pulls the official image (only the layers it lacks), starts it detached, and maps host port 80 → container 80. The default `CMD` is `nginx -g 'daemon off;'` — foreground, so PID 1 stays alive (if NGINX daemonized, PID 1 would exit and the container would die). (2) `curl localhost` hits the container through the bridge + iptables rule. (3) `docker logs nginx` shows the access log (NGINX logs to STDOUT via the symlink trick). (4) `docker exec -ti nginx bash` opens a shell *inside* the running container to debug — but slim images lack tools, so `apt-get update && apt-get install procps` to get `ps`. To customize: write a 3-line Dockerfile `FROM nginx` + `ADD index.html /usr/share/nginx/html/`, `docker build -t nginx:ulsah .`, then run it. The new image shares all the base layers — only the changed layer is new.

## Key Takeaways
1. Containers = isolated processes sharing the host kernel (namespaces + cgroups + capabilities + seccomp) — not VMs, no magic.
2. Images are read-only union-filesystem layers; containers add a copy-on-write layer; many containers share immutable bases (efficient, fast).
3. `docker` (client) → `dockerd` (daemon) → registry; treat containers as ephemeral cattle, run the main process in the foreground, log to STDOUT.
4. Use volumes/bind-mounts for persistent or data-intensive state (back with cloud block storage); the overlay layer is for app code.
5. Build images from small, vetted base images via a Dockerfile (layer per instruction, content-hashed).
6. Security: never add users to the `docker` group (= root), always TLS to remote daemons, enable content trust.

## Connects To
- **Ch 24**: virtualization (containers vs VMs; containers-on-VMs for density).
- **Ch 3**: namespaces, cgroups, capabilities (the kernel access-control primitives).
- **Ch 26**: CI/CD (images as deployment artifacts; orchestration like Kubernetes/Swarm).
- **Ch 6/23**: packaging and configuration management (containers as an alternative packaging model).
- **Ch 13**: networking (bridge, iptables, port mapping, overlays/VXLAN).
