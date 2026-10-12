# Chapter 8: Extending Automation to Test, Staging, and Production Environments

## Core Idea
Take the Ansible playbook built for DEV (Ch7) and refactor it with variables and per-environment inventory files so the *same* scripts provision TEST and PROD, achieving perfect environment parity. Then hand the `ansible-playbook` command to Jenkins so provisioning is recorded, traceable, and consistently applied across every environment.

## Frameworks Introduced
- **Reuse one playbook across all environments**: One set of roles + playbook, differing only by inventory and variables.
  - When to use: any time you have DEV/TEST/PROD that have drifted apart, or whenever you want TEST to genuinely predict PROD behavior.
  - How: (1) replace hardcoded values (e.g. the `vagrant` user) with variables like `{{ app_user }}`; (2) split roles across host groups (`postgres`, `webserver`, `redis`, `activemq`) instead of cramming all onto one VM; (3) create one inventory file per environment (`hosts-DEV.txt`, `hosts-TEST.txt`, `hosts-PROD.txt`); (4) run `ansible-playbook -i <inventory> playbook.yml` per environment.
- **Incremental environment rollout**: Automate environments one at a time in increasing order of importance: DEV → TEST → PROD → (Cloud?).
  - When to use: migrating manually-provisioned legacy servers to automation, where missing a step could break the app.
  - How: prove the playbook on the least-critical environment first; verify it works before touching PROD.
- **Central library of reusable Ansible roles**: One org-wide `ansible-scripts` Git repo with `common_roles/` shared across all apps.
  - When to use: when multiple applications need the same building blocks (PostgreSQL, Java, etc.).
  - How: pull roles out of the app repo into `ansible-scripts/common_roles/`; each app gets its own folder with a `playbook.yml` referencing common roles; provide sensible default variable values so a role is one line to include, with optional overrides.
- **Put Jenkins (CI) in charge of running Ansible**: CI executes provisioning, not individuals' laptops.
  - When to use: as soon as more than one person could run provisioning, or you need an audit trail.
  - How: a Jenkins build clones the `ansible-scripts` repo and runs the playbooks against TEST and PROD periodically or on every push to the repo; restrict `sudo`/SSH on targets so only Jenkins (and a few ops members) can provision.

## Key Concepts
- **Environment parity**: TEST matches PROD (and machines within an env match each other) so behavior is consistent and bugs are reproducible.
- **Configuration drift**: Servers silently diverge over years of manual, undocumented changes — and you can't even tell *how* they differ.
- **Production-only bug**: Code that passes all tests on TEST but breaks on PROD because the environments aren't identical (e.g. NTP set on TEST but not PROD → clock skew).
- **Ansible variables**: Define a value once (e.g. `app_user: uad`) and reference it everywhere as `{{ app_user }}`; can carry defaults and be overridden per playbook.
- **Inventory / host groups**: A file listing target machines grouped by role (`[webserver]`, `[postgres]`, ...); a host can belong to multiple groups and groups can be generated dynamically from a cloud API.
- **Ansible role**: A reusable, customizable unit of provisioning (tasks + templates); the same role (`user`, `java`) can be applied to multiple host groups.
- **Idempotency**: Ansible modules can be re-run safely with the same result — hard to get right in homegrown shell scripts.
- **Immutable infrastructure**: Never provision a machine twice; to change config, throw the machine away and spin up a new one. Deployment becomes a controlled "failure."
- **DevOps**: The team that builds the software also runs it in production, eliminating the dev/ops handoff bottleneck.
- **Ansible Tower**: GUI dashboard for Ansible with access control and better visibility than Jenkins (equivalents exist for Chef/Puppet).

## Mental Models
- Use **variables + inventory files** when the *only* differences between environments are configuration values and host lists — don't fork the playbook.
- Use **separate inventory files per environment** (over one big file with host groups) when an accidental run-against-everything would be disastrous — isolation prevents catastrophe.
- Use **immutable infrastructure** when machines are cheap and disposable (cloud) and deploys are frequent; treat a deploy exactly like recovering from a machine failure.
- Use **Packer-prebaked images or Docker** when immutable-infra provisioning at deploy time makes deployments too slow — bake the provisioning in advance.

## Anti-patterns
- **Divergent / drifting environments**: Manual logins and ad-hoc edits leave TEST ≠ PROD, the prime source of production-only bugs.
- **Manual provisioning of PROD**: Slow disaster recovery, no parity, error-prone (the forgotten-NTP class of mistake).
- **Running Ansible from individual laptops**: No record it ran, logs stuck on one machine, and people forget to apply changes (or apply to TEST but not PROD, destroying parity).
- **One big inventory with no group specified**: Forgetting the host group can run untested scripts against *all* environments at once.
- **Homegrown shell-script provisioning at scale**: Reinvents idempotency and templating, and shell scripts don't reuse cleanly like roles.
- **Leaving SSH/sudo open to everyone**: Manual tampering defeats the traceability and parity that automation provides — lock it to the provisioning tool.

## Code Examples

Variable definition and the user-creating role:
```yaml
# roles/user/tasks/main.yml
- name: create application user
  user: name={{ app_user }} state=present
```

Per-environment inventory with host groups (`provisioning/hosts-TEST.txt`, EC2):
```ini
[webserver]
ec2-54-77-241-248.eu-west-1.compute.amazonaws.com

[postgres]
ec2-54-77-232-91.eu-west-1.compute.amazonaws.com

[redis]
ec2-54-154-1-68.eu-west-1.compute.amazonaws.com

[activemq]
ec2-54-77-235-158.eu-west-1.compute.amazonaws.com
```

Playbook distributing roles across host groups, reusing `user`/`java` (Listing 8.1):
```yaml
---
- hosts: postgres
  sudo: yes
  roles:
    - postgresql

- hosts: activemq
  sudo: yes
  vars:
    - app_user: activemq
  roles:
    - user
    - java
    - activemq

- hosts: redis
  sudo: yes
  roles:
    - redis

- hosts: webserver
  sudo: yes
  vars:
    - app_user: uad
  roles:
    - user
    - java
    - ant
    - resin
```

Run a chosen environment by passing its inventory:
```bash
ansible-playbook -i provisioning/hosts-TEST.txt provisioning/playbook.yml
```

DEV inventory that puts every group on the single Vagrant VM (`hosts-DEV.txt`) + Vagrantfile wiring:
```ini
default ansible_ssh_host=127.0.0.1 ansible_ssh_port=2222
[webserver]
default
[postgres]
default
[redis]
default
[activemq]
default
```
```ruby
config.vm.provision "ansible" do |ansible|
  ansible.playbook = "provisioning/playbook.yml"
  ansible.inventory_path = "provisioning/hosts-DEV.txt"
end
```

Referencing a shared common role, with default vs. overridden variables:
```yaml
# accept role defaults
- hosts: postgres
  sudo: yes
  vars:
    db_user: uad
    db_password: abc
    database: uad
  roles:
    - ../common_roles/postgresql

# override a variable
  roles:
    - { role: ../common_roles/postgresql, max_connections: 10 }
```

- **What it demonstrates**: One playbook + roles serves every environment; only the inventory file and a handful of variables change. DEV collapses all groups onto one VM; TEST/PROD spread them across real hosts.

## Reference Tables

| Environment | Hosts | How provisioned | Who runs it |
|---|---|---|---|
| DEV | 1 Vagrant VM, all groups = `default` | `vagrant provision` → Ansible w/ `hosts-DEV.txt` | Developer (local) |
| TEST | Separate machines per role (e.g. EC2) | `ansible-playbook -i hosts-TEST.txt` | Jenkins |
| PROD | Separate machines per role | `ansible-playbook -i hosts-PROD.txt` | Jenkins (locked-down sudo) |

| Cleanup option | Mechanism |
|---|---|
| Leave old packages | "Hard disk is cheap" — ignore unused leftovers |
| Explicit removal | Add task with `state=absent` (e.g. remove `openjdk-7-jre`) |
| Immutable infra | Throw the machine away; provision a fresh one |

Central repo layout:
```
ansible-scripts/
  common_roles/
    java/tasks/main.yml
    postgresql/
      tasks/main.yml
      templates/postgresql.conf.template
  uad/
    roles/uad/tasks/main.yml
    playbook.yml
    hosts-DEV.txt
    hosts-TEST.txt
    hosts-PROD.txt
  website/
  adserver/
  ...
```

## Worked Example
Starting from Ch7's single-VM DEV playbook for the UAD app (Java servlet on Resin + ActiveMQ, PostgreSQL, Redis), the author refactors for multi-environment use:

1. **Kill the Vagrant assumption.** The scripts assumed an OS user `vagrant`. He adds a `user` role that creates an `app_user`, defines `app_user: uad` once as a variable, and find-and-replaces every hardcoded `vagrant` with `{{ app_user }}`.
2. **Split the hosts.** DEV ran everything on one VM; TEST/PROD must spread services across machines. He builds a TEST inventory (`hosts-TEST.txt`) with four EC2 host groups (`webserver`, `postgres`, `redis`, `activemq`) and rewrites the playbook (Listing 8.1) so each role targets the right group — reusing `user` and `java` on both `webserver` and `activemq`.
3. **Fix DEV.** Splitting groups breaks Vagrant, so he adds `hosts-DEV.txt` mapping every group to the single `default` VM and points the Vagrantfile's `inventory_path` at it.
4. **Adjust roles for distribution.** DB creation/user tasks move into the `postgresql` role; schema init now connects to the Postgres *server* (not localhost), and PostgreSQL config is opened for remote access from the web server.
5. **Provision TEST**: `ansible-playbook -i provisioning/hosts-TEST.txt provisioning/playbook.yml` — Ansible SSHes into each server and runs tasks, fully provisioning TEST in minutes.
6. **Add PROD**: just create `hosts-PROD.txt`; pick the environment by passing its inventory file.
7. **Share roles**: extract `common_roles/` into an org-wide `ansible-scripts` repo; the UAD playbook references `../common_roles/postgresql` with default vars (overridable like `max_connections: 10`).
8. **Hand to Jenkins**: a Jenkins build clones `ansible-scripts` and runs the playbooks against TEST and PROD (periodically or on push), with sudo locked to Jenkins — giving logs, an audit trail, and guaranteed cross-environment parity.

## Key Takeaways
1. Disparity between TEST/PROD (or between machines within an environment) is a dangerous, hard-to-diagnose source of bugs — automation eliminates it by giving perfect parity.
2. Use the *same* Ansible scripts everywhere; encode all per-environment differences in variables and inventory files, never in forked playbooks.
3. Build a central library of reusable, default-bearing roles so one line includes a fully-configured service, with overrides when needed.
4. A CI server like Jenkins is the right place to run provisioning — it records that it ran, stores logs, and ensures changes hit every environment.
5. Roll out automation least-critical-first (DEV → TEST → PROD) and keep environments isolated (separate inventory files) to avoid catastrophic accidental runs.
6. Automated provisioning is the prerequisite for cloud migration, immutable infrastructure (provision-once, throw-away), and DevOps.
7. Treat deployment as a controlled failure: spinning up + provisioning a fresh machine is identical to recovering from one that died.

## Connects To
- **Ch7**: extends the Vagrant + Ansible DEV foundation (roles, playbook) to all environments.
- **Ch1**: the production-only bugs caused by divergent environments are solved here via parity.
- **Ch9**: automated *deployment* on top of this provisioning — the missing piece for fast, immutable-infrastructure deploys.
