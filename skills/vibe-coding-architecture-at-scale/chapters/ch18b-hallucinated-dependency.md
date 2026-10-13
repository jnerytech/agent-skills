# Chapter 18b: The Hallucinated Dependency: The Supply Chain at Generation Speed

## Core Idea
Every import is a contract you sign with strangers, transitively and forever, and vibe coding removes the twenty minutes of human deliberation that used to come before it. The fix is the book's usual pattern: a human writes the dependency law once (deny by default, frozen resolution, cooldown, diff gate), and machines enforce it on every generation, so no stranger gets in at generation speed on a model's say-so.

## Frameworks Introduced
- **Four Ways the Generator Gets It Wrong**: a family of dependency failures, each with a different blast radius.
  - When to use: as a checklist when reviewing any generated build-file change.
  - How: check for each. (1) **Invented packages**: about 1 in 5 package references across 16 models pointed at nothing (Spracklen et al., USENIX Security 2025). Commercial models were around 1 in 20. Many hallucinations recur on every re-run of the same prompt. (2) **Stale popularity**: it picks the library that was popular at training time (old major lines, abandoned clients, CVE'd minor versions). (3) **Duplication**: a codebase that already uses Jackson gains Gson, and you end up with three JSON libraries and two HTTP clients. (4) **License-blindness**: it'll pull a GPL library into proprietary code, and nothing flags it.
- **Five Dependency Guardrails ("Deny by Default, Resolve Deterministically")**, in ascending ceremony:
  - When to use: any repo where agents can touch build files or run installs.
  - How: (1) **Freeze resolution**: commit lockfiles and install with `npm ci` or `pnpm install --frozen-lockfile`. On the JVM, pin versions and let Maven Enforcer fail on drift. (2) **Deny by default**: route installs through a curated proxy (Nexus, Artifactory) so unknown packages don't resolve, and/or use a Maven Enforcer `bannedDependencies` allowlist. (3) **Cooldown**: `minimumReleaseAge` (e.g. 3 days). Renovate has the same brake for update PRs. (4) **Gate the diff** in CI: any build-file change gets merge-blocking checks for registry existence, age, maintainer history, edit distance to famous names, OSV / OWASP Dependency-Check, and SPDX license allowlist. (5) **Tell the generator the rule**: put this in Tier 1 context: *"Never add a dependency. If a task needs a new library, name it in the plan with a one-line justification and stop."* Keep the approved and forbidden lists in `tech-stack.md` (Ch 7).
- **Lockfile Sentinel** (counter to **dependency tyranny**): a deterministic script that parses the lockfile diff and fails on any added package that isn't on a human-curated, source-resident allowlist.
  - When to use: you want a blunt "who invited you?" gate in the pipeline.
  - How: diff `package-lock.json`, `pnpm-lock.yaml` or `go.sum` against `allowed-dependencies.json`. Write the failure message for the agent as its reader: name the package, say it isn't allowed, point to the curation queue, and tell it to write the logic inline using standard utilities.

## Key Concepts
- **Slopsquatting**: registering package names that models repeatedly hallucinate, then waiting for the models to deliver victims (term coined by Seth Larson, PSF). Hallucinations are frequent and repeatable, unlike human typos, so they can be farmed.
- **`huggingface-cli` case (Bar Lanyado, 2024)**: a hallucinated name registered as an empty placeholder got thousands of downloads and ended up in a major company's install instructions.
- **Install-time execution**: npm `postinstall` and Python `setup.py` run code at install, so the compromise happens before any test runs.
- **Dependency tyranny**: the generator prefers installing a library over writing about 30 lines of first-party code, because typing costs it nothing and it never feels the permanent tax (license audit, scanning, patching, lockfile bloat).
- **Inverted pyramid**: first-party code is a thin layer over an enormous tree of strangers' packages.
- **Supply-chain case history**: left-pad (2016, single unexamined blocks), event-stream (2018, trust follows whoever holds the package this year), xz Utils CVE-2024-3094 (2024, patient adversaries beat patient review), chalk/debug phish and the Shai-Hulud worm (Sep 2025, human-speed response breaks).
- **Two accelerants**: dependencies now arrive at generation speed while judgment still runs at human speed, and the thing running `npm install` is increasingly an agent holding your credentials.
- **Double cut**: a compromised package attacks at install time, and its README and error text also feed the agent's context as an injection surface (Ch 19).

## Mental Models
- Think of every import as signing a contract with a stranger and all of that stranger's strangers.
- Treat the model as an unpinned dependency (Ch 23.6). Its "right library" is frozen at the corpus cutoff and weighted by popularity, so "a model recommends the dependency that was popular when it was trained, not the one that is correct today."
- Use a cooldown when you want immunity from the whole class of attack whose lifetime is shorter than the cooldown. You give up three days of freshness for it, which is about as lopsided a trade as you'll find.
- Prefer proposal over installation: the artifact you want from the AI is a written argument for taking on a new stranger, which a human approves or rejects at a glance.

## Anti-patterns
- **Reviewing a three-line pom.xml change buried in a forty-file diff**: the eye slides over it, as Ch 2 predicts.
- **Letting agents `pip install` / `npm install` freely in a credentialed environment**: install-time payloads run with your secrets in reach.
- **Version-range widening without frozen installs**: what ships changes silently from one morning to the next.
- **Relying on the Tier 1 instruction alone**: instructions are advisory. The enforcer plugin and the CI gate make them true.
- **Installing a library for Levenshtein, a CSV dialect or backoff retry**: that's dependency tyranny, a permanent obligation for 30 lines of code.

## Code Examples
```xml
<plugin>
  <groupId>org.apache.maven.plugins</groupId>
  <artifactId>maven-enforcer-plugin</artifactId>
  <executions><execution>
    <goals><goal>enforce</goal></goals>
    <configuration><rules><bannedDependencies>
      <!-- deny everything... -->
      <excludes><exclude>*</exclude></excludes>
      <!-- ...except the reviewed allowlist -->
      <includes>
        <include>org.springframework.*:*</include>
        <include>com.fasterxml.jackson.*:*</include>
        <include>io.github.resilience4j:*</include>
      </includes>
    </bannedDependencies></rules></configuration>
  </execution></executions>
</plugin>
```
```yaml
# .npmrc / pnpm-workspace.yaml
minimumReleaseAge: 4320   # no version younger than 3 days can resolve
```
- **What it demonstrates**: deny-by-default enforced locally. When the AI adds Gson, `mvn verify` fails with a named rule you can paste back ("com.google.code.gson is not on the approved list; use the existing Jackson stack"), and the young-release window is closed.

## Reference Tables
| Instrument | Mechanism | Stops |
|---|---|---|
| Freeze resolution | Lockfile + `npm ci` / `--frozen-lockfile` / Enforcer pins | Silent version drift |
| Deny by default | Curated proxy (Nexus/Artifactory), `bannedDependencies` | Unknown/duplicate/hallucinated packages |
| Cooldown | `minimumReleaseAge`, Renovate | Slopsquats and worm releases in their first days |
| Diff gate (CI) | Existence, age, maintainer, typo-distance, OSV/Dependency-Check, SPDX | Everything the 20 minutes of deliberation used to catch |
| Tier 1 rule | "Never add a dependency; propose with justification and stop" | Saves a round trip; produces the proposal artifact |

## Worked Example
An agent is asked for a camel-casing helper and adds `lodash.camelcase`. The lockfile sentinel in CI fails:
```
[dependency-gate] FAIL: The package 'lodash.camelcase' was added by this change.
This package is not listed in 'allowed-dependencies.json'.
If the dependency is absolutely required, request human review in the curation queue.
If the logic can be implemented using standard utilities, please write it inline.
```
The message goes back into the agent's context. The agent can't argue with a deterministic gate, so it drops the import and writes the utility using the standard library, with no human in the loop. The import only comes back through a human decision in the curation queue.

## Why It Works / Failure Mode
- **Deny by default plus the diff gate** work because the questions involved (does it exist, how old is it, which license, any CVEs) need no intelligence, and a machine asks them on every PR, including the ones no human reads closely. Failures come back fast enough to correct inside the generator's loop.
- **Limit**: nothing here audits the code *inside* an approved dependency. A curated allowlist would have admitted xz Utils. Cooldowns and provenance checks raise attacker cost by orders of magnitude and eliminate machine-manufactured attacks outright, but trust in distant maintainers remains. What you are guaranteed is narrower: no stranger enters at generation speed without a human decision on record and a deterministic gate behind it.

## Key Takeaways
1. Roughly 1 in 5 package references from code models can be hallucinated, and the same names repeat, which is what makes slopsquatting cheap.
2. Resolve every new dependency against the registry, the license list and its maintenance signal before it reaches the build.
3. Deny by default: use a curated proxy and/or an Enforcer allowlist so unknown packages don't resolve.
4. Freeze resolution with lockfiles and frozen installs. Add a roughly 3-day minimum release age.
5. Treat build-file changes as special in CI, with merge-blocking existence, age, CVE and license checks.
6. Tell the generator to propose, not install, and back that with a lockfile sentinel whose message is written for the agent.
7. Prefer 30 lines of first-party code over a new dependency for self-contained algorithms.

## Connects To
- **Ch 1**: the AI optimizes the current prompt, not the whole system, which leads to duplicate libraries.
- **Ch 2**: deceptive, fluent diffs the reviewer's eye slides over.
- **Ch 3 / Ch 7**: Tier 1 context rule; `tech-stack.md` in the repo-as-constitution.
- **Ch 5**: deny-by-default package rules, lifted to the package universe.
- **Ch 11b**: quiet, fluent failures (license defects).
- **Ch 18**: lockfiles as expand-contract for the package graph.
- **Ch 19 / 19b**: README and tool-output injection; sandboxing agents that run installs.
- **Ch 20**: slopsquatting is the Attacker Agent's move run by someone else.
- **Ch 21**: proposal-not-merge, and the CI gate that enforces this.
- **Ch 22**: generation speed vs human review speed.
- **Ch 23.6**: the model as an unpinned dependency.
- **SLSA / OSV / OWASP Dependency-Check / SPDX**; **Software Engineering at Google (Winters)**: costs of programming over time; **SRE toil (Beyer)**.
