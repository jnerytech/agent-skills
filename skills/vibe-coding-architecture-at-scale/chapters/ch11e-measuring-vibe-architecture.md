# Chapter 11e: Measuring Vibe Architecture

## Core Idea
Generation is now free, so every activity metric (lines, commits, PRs, story points) stops measuring progress and starts rewarding entropy. Stop measuring how much code is produced; measure whether the structure holds while it is produced, using a small set of leading, health, and efficiency metrics, led by the plan-versus-debug ratio.

## Frameworks Introduced
- **The Three-Way Financial Argument**: a God Prompt spends real money three times; the discipline moves cost rather than adding it.
  - When to use: making the case to leaders who fund numbers, not elegance.
  - How: show (1) **tokens**: sprawling prompts against bloated context, plus retries and re-reading, cost a multiple per feature, every time; (2) **senior hours**: untangling a 2,000-line AI diff burns staff-engineer afternoons that 20 minutes of planning would save; (3) **incidents**: shipped entropy becomes regressions, outages, 2 a.m. pages. Spec-Driven Development, the Context Diet, and guardrails convert unbounded, recurring, back-loaded spend into small, bounded, front-loaded spend: minutes stating intent plus a one-time guardrail build that runs free thereafter. Prove it with tokens-per-accepted-change, plan-vs-debug ratio, escaped-defect rate.

- **Three-Group Metric Set (leading / health / efficiency)**: track a small set; none is line count.
  - When to use: rolling the discipline out to a team or organization.
  - How: see Reference Tables. Read leading metrics to confirm the discipline exists, health metrics to confirm it works, efficiency metrics for ROI.

- **Plan-versus-Debug Ratio**: time spent on planning/spec vs debugging.
  - When to use: as the single headline number for a skeptical leader.
  - How: track both buckets per change. Pre-AI teams plan a little and debug a lot; under Vibe Architecture the ratio should invert. If it hasn't moved after adoption, the discipline isn't in place, whatever other dashboards say.

- **Anti-Metrics**: explicitly stop rewarding activity, because an AI optimizes for whatever you measure faster than any human.
  - When to use: whenever building dashboards or team goals.
  - How: remove lines/PRs/commits, "tests added," velocity/story points, and "AI adoption %" as goals. Measure outcomes (did defects escape, how fast did we recover, did architecture stay intact), never activity.

## Key Concepts
- **Activity metric**: a proxy for human effort, which used to be scarce; meaningless once generation is free.
- **Escaped-defect rate**: defects reaching production (not defects found); the only quality number that matters.
- **Tokens per accepted change**: context efficiency; flat with the diet, ballooning without it.
- **Mean-time-to-reload**: seconds to recover from a bad generation; the resilience number.
- **Machine-to-machine remediation rate**: share of Inquisitor gripes fixed without human attention.
- **Rework rate**: generations discarded/reloaded vs shipped; healthy when low because failures are caught and reset cheaply, not because they don't happen.
- **God Prompt**: a sprawling, unscoped prompt (Ch 24b anti-pattern).

## Mental Models
- A team shipping 40,000 AI-authored lines a week without guardrails is not a high performer; it is a future incident with good dashboards.
- Think of adoption as an input, not an outcome; the outcome is the structure holding.
- Speed was never the question; whether structure holds at speed is the only thing worth measuring.
- If volume rises along with escaped defects and review hours, you bought speed and sold structure.

## Anti-patterns
- **Rewarding lines/PRs/commits**: free to generate, free to game, and gaming produces the entropy you are fighting.
- **"Tests added" as a metric**: an AI told to raise test count writes tests that assert nothing; use escaped defects plus mutation/behavioral coverage on core domains.
- **Velocity/story points**: now measure generation speed, which is not the constraint.
- **"AI adoption %" as a goal**: pushes AI where it doesn't belong (see Ch 11b).

## Reference Tables
| Group | Metric | What it tells you |
|---|---|---|
| Discipline in place (leading) | % of features with a spec committed before code | Whether intent is the source of truth or the spec is theatre written afterward |
| | Tier-1 context-file size (lines) over time | Whether the Context Diet holds or the file rots into a wish list |
| | % of high-cost elements under a guardrail (`@AILocked` / `@AIContract` / contract tests) | Coverage of the boundaries that matter |
| | Guardrails present and merge-blocking in CI | Whether rules are law or advice |
| Is it working (health) | Escaped-defect rate | Should fall as guardrails mature |
| | Architectural violations caught in CI vs in production | Catches move left, then the rate itself falls |
| | Inquisitor gripe rate + % remediated machine-to-machine | Whether review scales without human attention |
| | Mean-time-to-reload | Resilience to bad generations |
| ROI (efficiency) | Tokens (or cost) per accepted change | Context efficiency |
| | Plan/spec time vs debugging time | Headline ROI; should invert |
| | Human review-hours per merged change | Should fall sharply as the Inquisitor absorbs the line-by-line pass |
| | Rework rate | Cheap catch-and-reset, not absence of failure |

## Worked Example
What "working" looks like over the first few quarters: escaped defects trend down even as change volume rises; architectural violations appear in CI rather than production, then taper as prevention beats detection; human review-hours per change fall while throughput holds or grows; tokens per accepted change stay flat instead of compounding; the plan-to-debug ratio visibly inverts. The failure signature: volume up, with escaped defects and review hours up alongside it.

## Why It Works / Failure Mode
Outcome metrics can't be satisfied by generating more, so they can't be gamed by an AI the way activity metrics can, and they directly price the three costs AI made expensive (tokens, senior debugging time, escaped defects). The set fails when leading metrics are tracked alone (specs written after the code satisfy "% with spec" in form only) or when an anti-metric creeps back in as a team goal.

## Key Takeaways
1. Drop activity metrics; generation is free and volume rewards entropy.
2. Pitch the discipline as moving cost: tokens, senior hours, incidents.
3. Track leading, health, and efficiency metrics; none of them is line count.
4. Lead with the plan-vs-debug ratio; it should invert.
5. Measure escaped defects, not tests added or defects found.
6. Success is falsifiable: defects down while volume up, catches move left, review hours fall, tokens per change flat.

## Connects To
- **Ch 3**: Context Diet; Tier-1 file size.
- **Ch 4**: `@AILocked`, `@AIContract`.
- **Ch 5**: tests that assert nothing.
- **Ch 7–11**: spec committed before code.
- **Ch 18**: contract tests.
- **Ch 21 / Ch 22**: merge-blocking CI; Inquisitor and machine-to-machine remediation.
- **Ch 24 / Ch 24b**: reload; God Prompt.
- **Ch 11b / 11c / 11d**: per-risk-tier AI metrics, org-level metrics, PCE and lead time.
- **Goodhart's Law**; **DORA metrics (change failure rate, time to restore)**; **mutation testing**.
