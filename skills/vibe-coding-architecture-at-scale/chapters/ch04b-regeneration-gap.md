# Chapter 4b: The Regeneration Gap: When Generated Guardrails Rot

## Core Idea
Generation is the easy half. A generated guardrail file is only as trustworthy as the verification that keeps it regenerated, and a stale generated file is worse than a stale hand-written one because it still looks machine-verified. If the guardrail itself can't fail a build, it will eventually go stale; close the gap by making drift checks, version locks, and locked-file enforcement default merge gates rather than opt-ins.

## Frameworks Introduced
- **The Regeneration Gap**: generation runs on every build, verification is wired to nothing; the guardrail generator becomes the one risk category not gated.
  - When to use: auditing any repo that commits generated AI config (VibeTags output, codegen'd rule files, generated docs).
  - How: ask four questions: (1) Is the generator's check/drift mode in required status checks? (2) Does a committed generated file ever disagree with a fresh regeneration? (3) Are processor and annotation library pinned to the same release? (4) Are "locked" elements enforced by a CI action or hook, or only by advisory Markdown?
- **Closing the Loop (four fixes, no new tooling)**:
  - When to use: as soon as the audit finds any "no."
  - How:
    1. **Make check mode a merge gate, not an opt-in**: same required-status list as linter and tests. If it can't block a merge, it is documentation about a feature, not a guardrail.
    2. **Treat generated-file drift as a build failure, unconditionally**: fail when the committed file and a fresh regeneration disagree, every commit; no window for "temporary" hand edits to become permanent.
    3. **Version-lock the generator to the annotations it reads**: one BOM or version property for annotations and processor; fail the build if they diverge.
    4. **Enforce locked annotations with a CI action, not prose**: wire the locked-files GitHub Action or a Ch 3d PreToolUse hook so @AILocked becomes a wall the agent cannot walk through.
- **Default-on beats opt-in**: the only enforcement that ran in the survey was the one nobody had to enable.
  - When to use: designing any guardrail tooling or CI policy.
  - How: put checks in the default build path; remove the step where a human must remember to inspect (Deming).

## Key Concepts
- **Check mode (drift check)**: run the processor against current annotations, diff against committed generated files, fail on mismatch.
- **Locked-files GitHub Action**: CI-layer block on AI modification of specific files; the enforcing companion to @AILocked.
- **Advise vs enforce**: instruction/rule/skill primitives advise; only a hook (no model judgment in the path) enforces (Ch 3d).
- **Silent annotation drop**: an older processor doesn't fail on an unknown annotation; it omits it from output and the build stays green.
- **Partially wrong file**: worse than a uniformly stale one because there's no visual signal where the gap is.
- **CI maximalism, guardrail minimalism**: a pipeline gating on everything (PMD, SpotBugs, Checkstyle, Error Prone, CodeQL, dependency review, fuzzing, SBOM, Scorecard) except its own guardrail generator.
- **Externalized theory**: tacit design judgment (which boundaries matter) made durable and machine-readable; what annotations really encode (Ch 3e).
- **Agloe effect**: an unverified artifact consumed as truth until decisions built on it make removal costly (Hyrum's Law on fiction).

## Mental Models
- Think of a stale generated guardrail as **"a rumor with excellent production values"**: it borrows the authority of a machine-verified fact it no longer is.
- Use the second-derivative law: **if a principle can't fail a build, the agent violates it; if the guardrail can't fail a build, the guardrail goes stale.**
- Think of an opt-in check mode as **inspection you have to choose to perform**; it gets skipped under deadline pressure exactly when an AI-authored change is most likely to touch a locked element.
- Think of absence of enforcement as **symptomless locally**: `mvn compile` regenerates correctly, so nothing looks wrong until source and committed file quietly diverge.

## Anti-patterns
- **"hand-maintained until regenerated once" comments**: a promise with no mechanism behind it; the same defect annotations eliminated for code, recurring in the tooling.
- **Unchecked sidecar files**: companion artifacts whose payload no longer matches the primary file, with nothing comparing them.
- **Processor pinned behind the annotation vocabulary**: silently drops newer annotations (potentially every @AILocked) with a clean build.
- **@AILocked enforced only by generated Markdown**: binding on nothing if the agent, a human, or a merge from a branch that never generated the file decides otherwise.
- **Trusting a feature because it is documented and tested**: existing check mode, never invoked in CI, protects nothing.

## Code Examples
```bash
# The fix shape: in CI, regenerate and fail on any diff against committed guardrail files
mvn -q compile                     # processor regenerates managed blocks
git diff --exit-code -- CLAUDE.md AGENTS.md .cursorrules .claude/rules/ \
  || { echo "Generated guardrails drifted from annotations"; exit 1; }
```
- **What it demonstrates**: the drift check as a required merge gate (illustrative; VibeTags ships its own check mode for this). Pair with a single BOM version for annotations + processor and a locked-files action / PreToolUse hook for @AILocked.

## Reference Tables
**Survey of the author's 5 VibeTags projects (~300 annotation sites)**

| Finding | Result |
|---|---|
| Annotation choice tracks domain | Yes: crypto lib → @AIPrivacy; arch tooling → layering/boundary; published library → @AIContract |
| Projects wiring drift check mode in CI | 0 of 5 |
| Projects adopting locked-files Action | 0 of 5 |
| @AILocked sites | 8, all enforced only by advisory Markdown |
| Drift artifacts found | "hand-maintained until regenerated once" comment; mismatched sidecar; processor 2 minor versions behind annotations |
| Enforcement that actually fired | 1: default-on @AIIgnore-without-ignore-file warning, fixed within a minute |

**The four fixes**

| Gap | Fix |
|---|---|
| Opt-in check mode | Required status check |
| Hand edits to generated blocks | Drift = unconditional build failure |
| Processor/annotation version skew | Single BOM/version property; fail on divergence |
| @AILocked as prose | Locked-files CI action or PreToolUse hook |

## Worked Example
The one case enforcement ran: VibeTags emits a default build-time warning when @AIIgnore is used but no ignore file exists. In one project it fired; the developer read the build output and created the missing file within a minute. A machine surfaced a gap at the moment it mattered, specifically enough to act on, and behavior changed on the spot, not at the next retro. Every other mechanism in the survey (check mode, locked-files action, version pin) failed for the same reason: it required someone to turn it on.

Contrast case: the most CI-disciplined project of the five gates on nine categories of risk but not on the generator in its own build file, because the annotations look like they work on every local compile.

## Why It Works / Failure Mode
- **Why the fix works**: moving verification into the default merge path turns "did the generated file drift?" into a five-second question answered on every commit (Humble/Farley: bring the pain forward). It keeps generated files *living documentation* (Martraire) rather than documentation-as-prose with better production values.
- **Failure mode**: any step requiring a human to remember to enable it will be skipped. Once committed, a generated file has consumers (agents every session, humans in onboarding, other tools), so silent drift becomes a live contract violation under Hyrum's Law, like Agloe, the fake map town that got a real general store.

## Key Takeaways
1. Generation without verification produces the worst artifact in the repo: a file that is partly true.
2. Annotations do encode real, domain-specific boundary knowledge; the gap is adoption of enforcement, not invention.
3. Make the drift check a required merge gate and treat any mismatch as a build failure.
4. Pin processor and annotations to one release; old processors drop unknown annotations silently.
5. @AILocked only means what it says when a CI action or hook enforces it.
6. Prefer default-on checks: the guardrail that worked was the one nobody had to remember to enable.

## Connects To
- **Ch 2b**: "if a principle can't fail a build..." applied one derivative up.
- **Ch 3d**: advise vs enforce; PreToolUse hook as @AILocked's wall.
- **Ch 3e**: annotations as externalized theory.
- **Ch 3f**: the same "enforces nothing" audit one layer up, for the instruction layer.
- **Ch 4**: the annotation pattern this chapter audits; BOM version alignment.
- **Ch 5 / 21 / 22**: rules as tests, branch-level law, Inquisitor only as good as verified guardrails.
- **Fitness functions (Ford/Parsons/Kua)**, **Continuous Delivery (Humble/Farley)**, **Living Documentation (Martraire)**, **Brooks on self-documenting programs**, **Hyrum's Law (Software Engineering at Google)**, **Deming: cease dependence on inspection**.
