# Chapter 21b: The Parallel-Agent Workshop: Isolation Hygiene for Concurrent Agents

## Core Idea
When several agents, or an agent plus a running test harness, share a working tree, port, dev server or terminal, you inherit Ch 17's concurrency hazards with whole processes as the "threads" and the filesystem and network stack as the "shared memory". Vigilance doesn't fix it. Isolation has to be structural: a worktree per writer, exclusive verification windows, explicit exit codes, and an environment audit before every run.

## Frameworks Introduced
- **Unit of Parallelism: Writers Isolate, Readers Share**: the unit of parallelism that never bites is the repository, or within one repo a `git worktree` checked out to its own directory.
  - When to use: deciding how to fan out more than one agent.
  - How: classify each agent. Any job that edits a file, runs a build or starts a server is a **writer** and gets its own worktree (or a lock, but avoiding sharing is the cheapest lock). Read-only research agents can share one checkout all day. A worktree takes seconds to create and `git worktree remove` to discard. It shares the object DB and nothing else: no file locks, no same-path writes, no port fights.
- **Verification-Window Exclusivity**: a running verification window freezes the whole repository (documentation included) for its duration, or the harness owns an isolated copy.
  - When to use: any e2e/integration run against a dev server with hot-module-reload or file watchers.
  - How: give the e2e suite its own worktree to build and serve from, so it no longer shares a watcher with the primary tree, and let other agents edit the primary tree freely. Never rely on a "don't edit near the test" convention.
- **Explicit Exit-Code Discipline**: never trust a pipeline's exit status as the verdict for anything but its last stage.
  - When to use: any harness or agent that runs verification and reads pass/fail.
  - How: echo each step's exit code explicitly, immediately after the step. Use `set -o pipefail` in shell. In general, never let a verdict pass through a layer that can substitute its own status.
- **Pre-Run Environment Audit**: before starting, ask who already owns the resources this run needs.
  - When to use: before every run that binds ports, starts servers or takes locks.
  - How: `lsof -i :3000` (or the platform equivalent) and a census of what is listening, running or holding a lock, including leftovers from prior sessions. Kill the stale ones.
- **Observer-Effect Discipline**: watching or editing near a run in progress must not perturb the run. Where a tool cannot guarantee that (whole-tree watcher, shared server, shared port), the fix is isolation, not vigilance.
- **The Five House Rules** (workshop-scoped counterpart of Ch 21's pipeline law): (1) Isolate by default for anything that writes. (2) A verification window owns its resource exclusively or owns an isolated copy. (3) Never trust a pipeline exit code beyond its last stage, and echo every step's status. (4) Audit the environment before the run, not after the failure. (5) Trunk stays green and stays shared: no long-lived divergent agent branches.

## Key Concepts
- **Git worktree**: a private, disposable working-tree directory sharing the repo's object database. It gives full isolation at nearly the cost of a branch.
- **Writer agent**: any agent whose job includes a file edit, a build or a server start.
- **Verification window**: the span during which a test run is executing against a live resource.
- **Hot-module-reload (HMR) hazard**: the watcher covers the whole tree and reloads on any write, including markdown, tearing down the page under test.
- **"Execution context destroyed"**: the browser-automation error raised when the page the test was driving vanishes mid-run.
- **Masked exit code**: in `a | b`, `$?` is `b`'s status, so `run_suite | tail -n 50` reports success when the suite fails.
- **Stale server / silent port fallback**: an old server squats on :3000, the new one silently binds :3009, and tests exercise days-old code.
- **Heisenbug**: a fault that vanishes or changes under observation (term popularized via Jim Gray's 1985 Tandem report).
- **False green**: worse than a failure because it is trusted and nobody goes looking for it. Fan-out multiplies it.

## Mental Models
- Think of shared-resource conventions as the Abermule handoff: a structural token degraded into a casual promise exactly when traffic is heaviest.
- Use Brooks' Law for agents: every added participant sharing a resource adds coordination cost. Choose the unit of parallelism so you pay the coordination tax once at the boundary, not continuously inside it.
- Use Amdahl's Law: speedup is bounded by the serial fraction (merges, reviews, the CI gate). Ten agents multiply proposals by ten, not throughput. The serial fraction is where correctness lives, so don't skip it.
- Think of Conway's Law at the tooling layer: agent topology mirrors repo topology. In a monorepo, draw each agent's boundary as deliberately as a module boundary, with a worktree standing in for the missing repo split.

## Anti-patterns
- **Fixing the specific file instead of the hazard**: "stop editing that markdown file" let the same failure recur with another agent and another file. The hazard is shared watched scope, not the file.
- **Convention-based mutual exclusion among agents**: independent agents cannot hold a shared, unwritten lock in their heads.
- **Piping verification through `tail`/`head` for readability**: masks the failure status.
- **Starting servers without a port census**: a graceful fallback port is a mercy for humans and a landmine for suites with hardcoded ports.
- **Long-lived divergent agent branches**: recreate merge hell at machine speed, between agents that cannot talk in the hallway.
- **"Just run more agents"**: ignores Brooks and Amdahl. The bottleneck stays at the gate on purpose.

## Code Examples
```bash
# Isolated verification window: e2e suite gets its own tree and watcher
git worktree add ../app-e2e HEAD
lsof -i :3000 || true            # audit: who already owns the port?
( cd ../app-e2e && npm ci && npm run dev & )
set -o pipefail
run_suite | tail -n 50
status=$?                        # explicit verdict for the suite, not tail
echo "suite exit: $status"
git worktree remove ../app-e2e --force
exit $status
```
- **What it demonstrates**: an illustrative composite of the chapter's rules (worktree isolation, pre-run audit, pipefail plus an explicitly echoed status), not a verbatim listing.

## Reference Tables
| Trap | Symptom | Root cause | Structural fix |
|---|---|---|---|
| HMR watcher (bit twice) | e2e fails with "execution context destroyed"; passes on frozen tree | Watcher covers whole repo; any write (even docs) reloads page | Verification run in its own worktree |
| Masked exit code | Suite failed, pipeline reported success | `$?` of `a \| b` is `b`'s status | Echo each step's status; `set -o pipefail` |
| Nine stale servers | "Regression": behavior absent | Old server on :3000; new one silently on :3009 | Pre-run environment audit (`lsof -i :3000`) |
| Three-repo fan-out (success) | Clean diffs, three simple PRs | Zero shared state | Repo/worktree as the unit of parallelism |

## Worked Example
**One working day, three traps and one success.**
- *Success*: the same fix category was needed in three repos. One agent per repo ran in parallel, each with its own checkout, suite and history. All finished cleanly, and merging meant reviewing three separate PRs.
- *HMR trap*: an e2e suite ran against a local HMR dev server while another agent edited a markdown file elsewhere in the repo. Tests failed with "execution context destroyed", and the same suite passed on a frozen tree. The watcher reloaded on any write, killing the page the browser session held. The first fix (stop editing that file) was local, so the failure recurred when a different agent touched a different file. The real rule: freeze the whole tree or give the harness its own worktree.
- *Masked exit*: `run_suite | tail -n 50` failed but was reported green, because `tail` exited 0.
- *Stale servers*: an audit found nine days-old dev servers. The oldest held :3000 and the session's server had fallen back to :3009, so every test hit days-old code and blamed the new code.

## Why It Works / Failure Mode
- **Why it works**: structural isolation reduces the communication surface between agents to zero (Brooks), so collisions are impossible rather than merely discouraged, the same way a physical single-line token made head-on collisions vanishingly rare. Agents have no memory of last week's servers and feel no discomfort editing mid-run, so the harness must supply what human instinct used to.
- **Failure mode**: any isolation enforced by convention degrades into an Abermule handoff (1921: a token handed back casually, two trains head-on, 17 dead). The guardrail fails at its one manual handoff, under peak load.

## Key Takeaways
1. Writers isolate, readers share: one worktree per writing agent is cheap enough that collisions are never excusable.
2. A verification window owns its whole watched scope or an isolated copy of it. Docs edits count.
3. Never accept a pipeline's exit code as a verdict for earlier stages. Echo every step's status.
4. Audit ports, processes and leftovers before the run. It costs one command, versus an afternoon chasing a ghost.
5. Keep trunk green and shared, because divergent agent branches are merge hell at machine speed.
6. Parallelism is bounded by the serial gate (Amdahl). More agents raise proposal rate, not throughput.

## Connects To
- **Ch 17**: thread-level concurrency hazards and barrier synchronization, here scaled up to processes.
- **Ch 21**: pipeline law. This chapter is the shop-floor counterpart, and the serial gate is the Amdahl bottleneck.
- **Ch 20d**: the one-agent-per-repo parallel hunt that is this chapter's success case.
- **Ch 11d**: Conway's Law as organizational bottleneck, reappearing at the tooling layer.
- **Ch 3**: context hygiene. Agents won't tidy their window, or their workshop, unless the harness makes them.
- **Brooks' Law (The Mythical Man-Month)**, **Amdahl's Law (1967)**, **Heisenbug (Jim Gray, 1985)**, **Continuous Integration (Fowler)**, **trunk-based development (Paul Hammant)**, **railway token working / Abermule 1921**.
