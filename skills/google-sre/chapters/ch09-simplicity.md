# Chapter 9: Simplicity
*Authors: Max Luebbe (ed. Tim Harvey)*

## Core Idea
"The price of reliability is the pursuit of the utmost simplicity" (C.A.R. Hoare). Software systems are inherently dynamic and unstable; SRE's job is "to keep agility and stability in balance in the system," and software simplicity is a prerequisite to reliability.

## Frameworks Introduced
- **Essential vs Accidental Complexity** (from Fred Brooks, "No Silver Bullet"): essential complexity is inherent in the problem definition and cannot be removed; accidental complexity is fluid and can be resolved with engineering effort.
  - When to use: reviewing designs and systems being onboarded.
  - How: SRE teams should (1) **push back** when accidental complexity is introduced into systems they're responsible for; (2) **constantly strive to eliminate complexity** in systems they onboard and assume operational responsibility for.
  - Example: a web server's essential complexity is serving pages quickly; writing it in Java may add accidental complexity in minimizing GC performance impact.
  - Why it works: accidental complexity is the removable part of operational risk. Failure mode: accepting it silently compounds over time into unsupportable systems.

- **The Virtue of Boring**: "boring" is a positive attribute in software; programs should stick to the script and predictably accomplish business goals. "Surprises in production are the nemeses of SRE." (Robert Muth: lack of excitement, suspense, and puzzles is a desirable property of source code.)

- **Exploratory coding (System Stability Versus Agility)**: sometimes sacrifice stability for agility by setting an **explicit shelf life** for code written to learn a domain ("try and fail once"); such code can be liberal with test coverage and release management because it never ships to production or users.
  - When to use: unfamiliar problem domains. Otherwise, aim for a balanced mix — and note reliable processes *increase* developer agility (rapid, reliable rollouts make bugs easier to see and quicker to fix).

- **The "Negative Lines of Code" Metric**: every line changed or added creates potential for new defects; smaller projects are easier to understand, test, and have fewer defects. Treat deleting useless code as valuable work; be reserved about adding features. "Every new line of code written is a liability" for a 24/7 service.
  - How: scrutinize code to ensure it drives business goals; routinely remove dead code; build bloat detection into all levels of testing.

- **Minimal APIs**: "perfection is finally attained not when there is no longer more to add, but when there is no longer anything to take away" (Saint-Exupéry). Fewer methods and arguments → easier to understand and more effort available to perfect each. A small, simple API is a hallmark of a well-understood problem.

- **Modularity**: OOP rules of thumb apply to distributed systems.
  - Loose coupling between binaries, and between binaries and configuration, promotes both agility and stability (fix and push one component independently).
  - **Version APIs** so consumers upgrade safely and release cadence can vary across the system.
  - Clear separation of responsibility: no "util" or "misc" binaries (like "grab bag" classes); each collaborator has a clear, well-scoped purpose.
  - Apply to data formats: protocol buffers designed for backward- and forward-compatible wire format.

- **Release Simplicity**: release in small batches; measuring the impact of one change is far easier than 100 unrelated changes at once. Analogy: **gradient descent** — small steps, evaluating whether each improves or degrades.

## Key Concepts
- **Agility vs stability balance**: the summary of SRE's systems job.
- **Exploratory coding**: code with an expiration date, used to learn.
- **Essential complexity**: irreducible complexity in the problem.
- **Accidental complexity**: removable complexity introduced by implementation choices.
- **Software bloat**: tendency of software to become slower and bigger over time from a constant stream of features.
- **Dead code / flag-gated never-executed code**: a "time bomb" (Knight Capital).
- **Minimal API**: fewest methods/arguments needed for the problem.
- **API versioning**: lets dependents upgrade on their own cadence.
- **Protocol buffers**: language/platform-neutral serialization with backward/forward-compatible wire format.

## Mental Models
- Think of **every new line of code as a liability**, not an asset, for a service expected to be available 24/7.
- Use **"boring" as a design goal** when choosing between clever and predictable implementations.
- Think of **releases as gradient descent**: small steps, measure, keep or revert.
- Think of **saying "no" to a feature** as protecting focus on innovation, not restricting it.

## Anti-patterns
- **Keeping code "in case we need it later"**: source control makes reversal easy; keep the tree clean.
- **Commenting code out instead of deleting**: hundreds of commented lines distract and confuse as files evolve.
- **Gating dead code behind an always-disabled flag**: a time bomb (Knight Capital).
- **"util" or "misc" binaries**: grab-bag components with unclear responsibility.
- **Unversioned API changes**: a single change can force rebuilding the entire system and introduce bugs.
- **Big-batch releases**: 100 unrelated changes make performance regressions hard to attribute.
- **Accepting accidental complexity silently**: SRE should push back.

## Worked Example
**Big batch vs small batch release.** A team ships 100 unrelated changes at once and performance degrades; identifying which change(s) caused it and how requires considerable effort or extra instrumentation. Shipping the same changes in smaller batches lets each change be understood in isolation, so the team moves faster with more confidence — like gradient descent, each small step is evaluated for improvement or degradation before taking the next.

## Key Takeaways
1. Push back on accidental complexity and actively remove it from systems you onboard.
2. Delete dead code; never comment it out or hide it behind a permanently disabled flag.
3. Celebrate negative lines of code; add bloat detection to testing.
4. Design minimal, versioned APIs and single-purpose binaries; keep config loosely coupled.
5. Release small batches so each change's impact is measurable.
6. Use explicitly time-boxed exploratory code to learn, and keep it out of production.
7. Prefer boring, predictable software; treat surprises in production as defects.

## Connects To
- **Ch 8**: release simplicity, small frequent releases, binary/config decoupling.
- **Ch 6**: "As simple as possible, no simpler" monitoring.
- **Ch 3**: agility vs stability balanced via error budgets.
- **Ch 7**: autonomous design via decoupled subsystems and APIs.
- **Ch 32**: SRE onboarding and pushing for simpler architectures.
- **Fred Brooks, "No Silver Bullet"**: essential vs accidental complexity.
- **Knight Capital incident**: dead code reactivated by a flag.
- **Protocol buffers**: compatible data-format modularity.
