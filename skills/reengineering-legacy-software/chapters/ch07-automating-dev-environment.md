# Chapter 7: Automating the Development Environment

## Core Idea
Treat the development environment as code: a good README plus Vagrant (VM) and Ansible (provisioning) let any developer go from `git clone` to a running, identical environment with one `vagrant up` command — eliminating days of manual detective work and "works on my machine."

## Frameworks Introduced
- **README-as-onramp**: A concise, structured plain-text (Markdown) file in the repo root that gives a new developer exactly what they need to start, and nothing more.
  - When to use: every repository; it's the most discoverable, most-likely-to-stay-current form of docs because it lives next to the code and is a target for code review.
  - How: standard sections — what the software is, `## Dependencies`, required env vars, `## How to configure`, `## How to run locally`, `## How to run tests`, `## How to build`, `## How to release/deploy`. Keep it short; push architecture/troubleshooting docs to a `docs/` folder or wiki (linked from the README).
- **Vagrant**: Programmatically builds an isolated VM holding all of an app's dependencies, isolated from the host and other projects.
  - When to use: when projects have conflicting dependency versions, or you want to mirror a Linux production environment locally.
  - How: create a `Vagrantfile` (Ruby DSL) in repo root via `vagrant init`; set `config.vm.box`; `vagrant up` to boot, `vagrant ssh` to log in, `vagrant provision` to re-run provisioning, `vagrant destroy` to remove. Folder with the Vagrantfile is auto-shared two-way as `/vagrant` inside the VM. Needs a provider (VirtualBox/VMware/EC2).
- **Ansible**: Automates provisioning — installs and configures dependencies declared in YAML playbooks.
  - When to use: anything beyond trivial shell scripts; when you want composable, reusable provisioning across projects/environments.
  - How: write `provisioning/playbook.yml`; organize dependencies as **roles** (`provisioning/roles/<name>/tasks/main.yml`); wire it into Vagrant via `config.vm.provision "ansible"`. Agentless — runs over SSH, no agent on the VM.

## Key Concepts
- **Provisioning**: installing and configuring everything needed to run a piece of software.
- **Infrastructure as code**: the environment setup is captured in version-controlled files (Vagrantfile, playbooks) that double as executable documentation.
- **Idempotency**: a well-written playbook can be run any number of times with the same result — Ansible declares desired state (`state=present`) rather than imperative commands, and checks before acting.
- **Box**: a Vagrant base image used as the foundation of a VM (e.g. `ubuntu/trusty64`).
- **Role**: an Ansible unit grouping the tasks for one dependency, kept separate for reuse.
- **Module**: a built-in Ansible action (`apt`, `get_url`, `unarchive`, `file`, `copy`, `lineinfile`, `command`, `postgresql_user`, `postgresql_db`).
- **Agentless**: Ansible needs no software pre-installed on the target; it executes remotely via SSH.
- **Developer autonomy**: removing blocking steps (waiting on ops to create a DB user) by running everything locally under the developer's control.

## Mental Models
- Use a **README in repo root** when you want docs that are discoverable and stay current — proximity to code keeps it honest.
- Use **automation over a wiki page** when setup is a repeated "download / install / configure" loop — scripts become the documentation and guarantee version parity.
- Use a **VM per project** when dependency versions conflict between projects on one machine.
- Use **a local DB inside the VM** instead of a shared test DB when you want to remove human-blocking onboarding steps and prevent developers trampling each other's data.

## Anti-patterns
- **No README / docs on an unstructured wiki**: undiscoverable, hard to update, degrades into a mishmash of stale hints and "grain of salt" corrections (John & Ahmed's notes).
- **Manual setup steps**: each new developer repeats the same download/install/configure detective work, wasting time and producing divergent machine states.
- **Reliance on external/shared resources**: e.g. emailing the ops team for a PostgreSQL user — a step that waits on a human blocks onboarding; shared test DBs invite "oops, I wiped the DB" accidents.
- **Bloated README**: dumping architecture and troubleshooting into it makes it less likely to be read or maintained — keep it to getting-started only.

## Code Examples
```ruby
# Vagrantfile (repo root) — wires Vagrant to Ansible provisioning
VAGRANTFILE_API_VERSION = "2"

Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|
  config.vm.box = "ubuntu/trusty64"

  config.vm.provision "ansible" do |ansible|
    ansible.playbook = "provisioning/playbook.yml"
  end
end
```
```yaml
# provisioning/playbook.yml — runs the java role with sudo on all hosts
---
- hosts: all
  sudo: yes
  roles:
    - java
```
```yaml
# provisioning/roles/java/tasks/main.yml — declarative, idempotent install
---
- name: install OpenJDK 7 JDK
  apt: name=openjdk-7-jdk state=present
```
- **What it demonstrates**: the full chain — Vagrantfile delegates to a playbook, which composes roles whose tasks declare desired state (`state=present`) so reruns are safe.

## Reference Tables
| Command | Effect |
|---|---|
| `vagrant init` | create a new Vagrantfile |
| `vagrant up` | boot and provision the VM |
| `vagrant ssh` | log into the VM |
| `vagrant provision` | re-run the Ansible provisioning |
| `vagrant destroy` | delete the VM |

| Ansible module | Used for |
|---|---|
| `apt` | install OS packages (`name=... state=present`) |
| `get_url` | download a file (e.g. Resin tarball) |
| `unarchive` | extract a tarball into a destination |
| `file` | set ownership / create symlinks |
| `copy` | push a host file (e.g. custom config) into the VM |
| `lineinfile` | ensure a line exists (e.g. set an env var) |
| `command` | run an arbitrary command, with `register` to capture output |
| `postgresql_user` / `postgresql_db` | manage a Postgres user / database |

## Worked Example
Provisioning the UAD (User Activity Dashboard) dev environment. Dependencies discovered the hard way: Resin 3.x web container, Apache ActiveMQ (JMS), PostgreSQL, Redis, and a proprietary XML-parser license file.

1. **Vagrantfile** in repo root sets `config.vm.box = "ubuntu/trusty64"` and a `config.vm.provision "ansible"` block pointing at `provisioning/playbook.yml`.
2. **One role per dependency** under `provisioning/roles/`. Java/Redis/Ant are trivial `apt ... state=present` installs.
3. **Resin role** (`roles/resin/tasks/main.yml`) does the download/install/configure pattern as ordered tasks:
```yaml
---
- name: download Resin tarball
  get_url: >
    url=http://www.caucho.com/download/resin-3.1.14.tar.gz
    dest=/tmp/resin-3.1.14.tar.gz
- name: extract Resin tarball
  unarchive: >
    src=/tmp/resin-3.1.14.tar.gz
    dest=/usr/local
    copy=no
- name: change owner of Resin files
  file: >
    state=directory path=/usr/local/resin-3.1.14
    owner=vagrant group=vagrant recurse=yes
- name: create /usr/local/resin symlink
  file: >
    state=link src=/usr/local/resin-3.1.14 path=/usr/local/resin
- name: set RESIN_3_HOME env var
  lineinfile: >
    state=present dest=/etc/profile.d/resin_3_home.sh
    line='export RESIN_3_HOME=/usr/local/resin' create=yes
```
4. **ActiveMQ** mirrors Resin, then overwrites config with a repo-stored file via `copy` (big files downloaded onto the VM; small config files kept in the repo and copied over).
5. **Remove the external DB dependency**: dump the test schema once with `pg_dump --username chris --host=testdb --dbname=uad --schema-only > schema.sql`, then Ansible installs PostgreSQL (`postgresql`, `libpq-dev`, `python-psycopg2`), creates the `vagrant` user and `uad` DB, and conditionally loads the schema — using a `command` task with `register: table_count` and `when: table_count.stdout | int == 0` to stay idempotent.
6. **Result ("take two")**: the new hire clones the repo, reads the README, runs `vagrant up`, goes for coffee, and returns to a fully provisioned environment — implementing a feature and opening a PR by end of day one.

## Key Takeaways
1. The README is the most important file in the repository — discoverable, concise, and kept honest by living beside the code and being code-reviewed.
2. Repetitive download/install/configure steps are crying out for automation; automating them yields less wasted time, shorter docs, and version parity across machines.
3. Vagrant isolates each project's full dependency stack in a VM; Ansible declaratively provisions it from version-controlled YAML.
4. Write provisioning declaratively (`state=present`) so playbooks are idempotent and safe to rerun; use `register` + `when` for the tricky cases.
5. Pull external/shared resources (like a shared test DB) into the VM so the developer has full local control and onboarding never blocks on a human.
6. The provisioning scripts ARE documentation — they record the software's exact dependencies executably.

## Connects To
- **Ch1**: solves the legacy-onboarding pain — the days of detective work and undocumented dependencies that make legacy software intimidating to approach.
- **Ch8**: the same Ansible roles are reused to provision test, staging, and production — one definition across every environment.
- **Infrastructure as Code / DevOps**: this is IaC at the developer-workstation scale; the same philosophy (Chef, Puppet, Docker, Salt as alternatives) scales to whole fleets.
