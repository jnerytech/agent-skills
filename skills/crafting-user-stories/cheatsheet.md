# Cheatsheet — The Art of Crafting User Stories

## Story skeleton
`As a [persona], I want [goal], so that [benefit].`
- No "so that" you can state → **not user-focused yet**, rewrite.
- Story is technical/UI-detailed → **you lost the user**, restart from the persona.

## INVEST — accept/reject filter
| Letter | Pass if… | Fail tell → action |
|---|---|---|
| **I**ndependent | deliverable alone | depends on another story → merge or re-split |
| **N**egotiable | scope can flex | reads like a fixed spec → strip detail, leave intent |
| **V**aluable | clear user benefit | only benefits the team/tech → reframe to user |
| **E**stimable | team can size it | can't estimate → too vague or too big, split/spike |
| **S**mall | fits one sprint | spans sprints → it's an epic, split |
| **T**estable | has acceptance criteria | no "done" condition → add criteria |

## When to use which prioritization
| Situation | Use | Rule |
|---|---|---|
| Fast stakeholder alignment | **MoSCoW** | Must / Should / Could / Won't |
| Maximize ROI, cut waste | **WSJF** | `(BV + OppEnable + TimeCrit + RiskRed) / JobSize`, highest first |
| Score by impact | **RICE** | `Reach × Impact × Confidence / Effort` |
| Satisfaction + differentiation | **Kano** | cover Basic, invest in Delight |

## Kano decision
- **Basic** need missing → product feels broken. Always cover first.
- **Performance** need → linear payoff; invest where competitive.
- **Delight** need → highest priority for differentiation; but delighters decay to expected over time.

## Estimation
- Use **story points** (relative effort), not hours.
- **Planning poker**: private pick → simultaneous reveal → discuss outliers → re-vote.
- Forecast with **velocity** (avg points/sprint); trust it only after ~3 sprints.
- Big spread in poker votes = hidden disagreement on scope → discuss before re-voting.

## How to split a too-big story
Split by, in rough preference order:
1. **Workflow steps** (stages of the user's process)
2. **Business rules / conditions**
3. **Data variations** (types, ranges, locales)
4. **Operations** (CRUD: create / read / update / delete)
5. **UI components** or **user roles / modules**
- Each slice must still be **independently valuable** — never split by tech layer (UI vs DB).

## Ready vs Done gates
- **DoR** (enter sprint): clear · estimated · acceptance criteria written · dependencies known.
- **DoD** (leave sprint): coded · tested · reviewed · acceptance criteria met.

## Acceptance criteria smell test
- Can't tell when the story is finished → criteria missing or vague.
- Criteria describe *implementation* not *observable behavior* → rewrite as user-visible outcomes.

## Top anti-patterns (recognize fast)
| Smell | Problem | Fix |
|---|---|---|
| Story spans multiple sprints | it's an epic | split |
| No "so that" | not user-driven | add the benefit |
| No acceptance criteria | undefined "done" | add criteria |
| Backlog unordered | low-value ships first | prioritize by value |
| Written solo by PO/dev | misalignment | collaborate (PO + dev + users) |
| Persona built on stereotype | exclusionary | research with diverse users |

## Discovery toolkit (pick by question)
- Need *why/how* (depth) → interviews, empathy map (Says/Thinks/Feels/Does).
- Need *how many/how often* (scale) → surveys, analytics, A/B test.
- Need cross-touchpoint friction → user journey map.
- Need a fast solution to a complex problem → design sprint (Understand→Define→Sketch→Decide→Prototype).
