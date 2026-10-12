# Chapter 23: Configuration Management

## Core Idea
Configuration management (CM) automates OS/server configuration by **capturing desired state as code** — you declare how systems should be, and the CM system makes reality conform. This replaces the **snowflake model** (ad-hoc shell scripts where no two systems are alike) with version-controlled, reproducible, self-documenting infrastructure that doubles as inventory + command-and-control. The four major systems: **Ansible, Salt, Puppet, Chef** — all do the same basic job with different vocabularies.

## Frameworks Introduced
- **Declarative over procedural**: describe the *state you want*, not the steps to get there; the CM system figures out the diff and applies it.
- **The CM building blocks** (vendor-neutral terms): **operation** (a small idempotent action — create user, install package, render template), **parameter** (operation argument), **variable** (named value, scoped), **fact** (auto-discovered system info — IP, OS), **handler** (operation triggered by a *change* event, e.g. restart service on config change), **binding** (associates operations to hosts/groups), **bundle** (reusable operation collection), **environment** (dev/test/prod axis of variation).
- **Idempotence**: operations can be applied repeatedly without harm — they detect whether state needs changing and do nothing if already conformant; they report rich results (richer than exit codes) and strive to be cross-platform.
- **Environments as a pipeline**: dev → test → prod are versions of the same config base (like Git tags moving forward as releases are vetted); each can supply different variable values (credentials, network).

## Key Concepts
- **Operations are just scripts** (in the CM system's language) that often shell out under the hood; you can write custom ones.
- **Facts are cached** — invalidate the cache if a flow uses stale data. Clients can add their own facts (static file or code) — useful for cloud (EC2 tags) but a security risk (a compromised client controls its facts).
- **Architecture split**: Ansible = **agentless** (no daemons, drives clients over SSH, needs only sshd + Python 2 on clients, leaves no trace). Salt/Puppet = optional daemons (facilitators/accelerators, enable advanced features like event reporting). Chef = **server is authoritative** (changes uploaded via `knife`; the outlier in complexity).
- **Config languages**: Ansible/Salt = YAML + Jinja2 templating (Python under the hood, rarely seen). Puppet = custom declarative DSL (Ruby underneath). Chef = Ruby DSL (most code-like).
- **Dependency models**: Ansible/Chef run operations in **presentation order**; Salt/Puppet allow **explicit dependencies** (`require`) so order in the file doesn't matter (Puppet even infers some). Both have moved to hybrid (order matters within a file; cross-file needs explicit declaration).

## Mental Models
- **Once a host is under CM, never touch it manually** — a manual change instantly reverts it to a snowflake, and worse, making changes immutable to block the CM system causes baffling outages (real war story).
- **The fault line runs between Chef and everyone else.** Ansible/Salt/Puppet have similar modest complexity; Chef requires significantly more investment and a developer mindset. Adopt Chef only at scale (hundreds/thousands of hosts, tiered staff, compliance needs) — not "because it's the most powerful."
- **Agentless ≠ simpler-but-weaker.** Ansible is legitimate for complex sites (just slower at scale); Salt/Puppet are *also* approachable, not "advanced options." Daemons buy speed and central-coordination features (event reporting, inter-client data sharing).
- **YAML is shorthand for JSON, and it strains under CM complexity.** Edge cases (`name=value` shorthand, quoting Jinja, the `args` wrapper, where `with_items` nests) cause constant ambiguity — config is data, not code, so "which level does this argument go?" is rarely obvious.

## Anti-patterns
- **Manually editing a CM-managed host**: reverts it to snowflake status; setting changes immutable to override CM is a recipe for confusing outages.
- **Adopting more CM complexity than you need**: Chef's enterprise features (permissions, attribute precedence, cookbook dependency hell) impose cognitive overhead even on a single machine.
- **Trusting client-reported facts for privilege decisions**: a compromised client controls its facts and could escalate.
- **Not pinning dependency versions** (Chef cookbooks): an upstream break propagates to all systems.
- **Diving into production without practice**: steep learning curves — rehearse on a VM lab first.
- **Putting heavy logic in Jinja/YAML**: even Salt warns against it — config should be mostly data.

## Code Examples
```yaml
# Ansible (YAML) — ordered tasks; user depends on group existing first
- name: Ensure that www group exists
  group: name=www state=present
- name: Ensure that www user exists
  user: name=www group=www state=present createhome=no

# Ansible playbook with a loop (Jinja {{ item }})
- name: Install OCAML packages
  hosts: cloud
  become: yes
  tasks:
    - name: install packages
      package: name={{ item }} state=present
      with_items: [gmake, ocaml, ocaml-opam]
```
```yaml
# Salt (YAML) — explicit dependency via require; order in file irrelevant
www-user:
  user.present:
    - name: www
    - gid: www
    - require:
      - www-group
www-group:
  group.present:
    - name: www
```
```ruby
# Chef (Ruby DSL)
service 'sshd' do
  supports :restart => true, :status => true
  action [:enable, :start]
end
```
```puppet
# Puppet (custom DSL)
service { "ssh": ensure => "running", enable => "true" }
```
```sh
# Ansible: no daemons — just run from the control host over SSH
ansible-playbook site.yml          # apply config
# ~/.ansible.cfg : [defaults] inventory=./hosts  roles_path=./roles
# /etc/ansible/ansible.cfg : [ssh_connection] pipelining = true  (perf boost)

salt test-system state.apply order-test   # Salt: apply a state
```

## Reference Tables
**CM Rosetta Stone** (our term → Ansible / Salt / Puppet / Chef): operation → task / state / resource / resource · op list → tasks / states / manifest / recipe · binding → play(book) / top file / declaration / run list · master → control / master / master / server · client → host / minion / agent / node · variable → variable / variable / parameter / attribute · fact → fact / grain / fact / automatic attribute · handler → handler / requisite / subscribe / subscribes · bundle → role / formula / module / cookbook · bundle repo → galaxy / GitHub / forge / supermarket.

**System profiles**: Ansible (Python, YAML/Jinja, **no daemons**, agentless/SSH — recommended for most, slower at scale) · Salt (Python, YAML/Jinja, optional daemons, fast, event-driven) · Puppet (Ruby, custom DSL, oldest/largest base but losing share, server-side bottlenecks) · Chef (Ruby DSL, authoritative server, most powerful/complex — enterprise scale only).

**Distribution models**: client daemon pulls from CM server · CM server pushes to clients · each node self-applies from a local clone (no server).

## Worked Example
**Ordering an operation that has a prerequisite.** A `www` user needs a dedicated `www` group, and creating a user with a nonexistent group errors out. Two ways to guarantee order: **(1) Presentation order (Ansible/Chef)** — just list the group task before the user task; Ansible runs operations top-to-bottom, so the group exists first. Simple, but order is implicit and fragile across files. **(2) Explicit dependency (Salt/Puppet)** — declare `require: - www-group` on the user state; now the operations run correctly *regardless* of their order in the file (the Salt example deliberately puts the user first to prove it). The payoff of explicit dependencies: the CM system knows the dependency graph, so on failure it can abort just the affected chain while letting independent chains continue — more resilient, but more typing. Puppet sweetens this by *inferring* the dependency automatically when a user names a group. Both systems ultimately went hybrid (order matters within a file; cross-file needs `require`).

## Key Takeaways
1. CM captures desired state as version-controlled code, killing the snowflake model and giving inventory + audit trail + documentation for free.
2. Think declarative and idempotent: describe the end state; operations detect and apply only needed changes, repeatably.
3. Learn the universal concepts (operation, variable, fact, handler, binding, bundle, environment) — they map across all systems via the Rosetta Stone.
4. Never modify a managed host by hand; rehearse on a VM lab before production.
5. Choose by complexity: Ansible/Salt for most sites (Ansible agentless/simple, Salt fast/daemon-capable); Puppet if inherited; Chef only at enterprise scale.
6. Dependencies come from presentation order (Ansible/Chef) or explicit `require` (Salt/Puppet) — explicit is more resilient but more work; YAML is data-not-code with real ergonomic warts.

## Connects To
- **Ch 7**: scripting (the ad-hoc predecessor CM replaces; operations shell out).
- **Ch 6**: software installation (package operations).
- **Ch 26**: CI/CD (environments pipeline, staged rollout).
- **Ch 25**: containers (an alternative/complement to CM for immutable infrastructure).
- **Ch 31**: DevOps philosophy (CM enables but isn't identical to DevOps).
