# Chapter 16: Additional Topics

## Core Idea
Practical answers to recurring story questions: handle nonfunctional requirements as constraints, choose paper cards vs. software by project context, watch how iteration affects the user interface, decide whether to retain or rip up cards, and treat bugs as stories.

## Frameworks Introduced
- **Nonfunctional requirements as constraint cards**: capture qualities (performance, accuracy, portability, etc.) by writing the constraint on a card annotated "Constraint."
  - When to use: requirements that can't be expressed as a normal story.
  - How: write the constraint; where possible add an automated test run at least daily; supplement with other formats (e.g., a data dictionary) when a card isn't enough.
  - Why it works: keeps NFRs visible and verifiable; failure mode — a few constraints (e.g., "written in Java") aren't worth testing.
- **Story-based Agile Usage-Centered Design** (adapted from Constantine & Lockwood): drive UI design from stories instead of essential use cases.
  - Steps: (1) user role modeling → (2) trawl high-level stories → (3) prioritize (high/medium/low) → (4) refine high/medium into smaller stories → (5) group stories likely performed together → (6) paper prototype each group → (7) refine prototype with users → (8) start programming.
  - Keep it lightweight (a few days to a few weeks); some prototyped stories may be dropped before development.
- **"Write two" user interfaces** (Ward Cunningham): build two UIs to keep the middle tier honest and avoid betting on the wrong UI technology.

## Key Concepts
- **Constraint**: a nonfunctional requirement written on an annotated card, ideally backed by an automated test.
- **Nonfunctional requirement areas**: performance, accuracy, portability, reusability, maintainability, interoperability, availability, usability, security, capacity.
- **Paper note cards**: simple, low-tech, sortable/stackable; their limited size is a constant reminder that stories are imprecise.
- **Story-tracking software**: VersionOne, XPlanner, Select Scope Manager (or spreadsheets, defect trackers, wikis); favored for distributed teams or ISO traceability.
- **Retaining/archiving stories**: keeping completed cards (rubber-banded on a shelf, photocopied) or software records rather than discarding.
- **Bugs as stories**: treat each bug report as its own story; batch quick bugs under a cover card.

## Mental Models
- Match the tool to the team: start with cards; switch to software only when there's a compelling reason (remote stakeholders, lost cards, ISO traceability).
- Cards' low-tech feel guards against stories mutating into IEEE 830-style "shall" requirements with needless detail.
- For UI-critical products, iterative refinement can hurt users who've already learned the interface — treat "change the UI as little as possible once started" as an unwritten constraint and do more upfront UI design.

## Anti-patterns
- **Forcing everything into stories**: some requirements (NFRs) don't fit; express them as constraints or whatever format is traditional.
- **Iterating the user interface freely**: even small placement/form changes disrupt users who've mastered the interface (Constantine) — UI architecture should fit the full task set up front.
- **Refusing to retain cards**: the pleasure of ripping a card up can cost you later — Cohn lists acquisitions, rewrites, and a deal-closing "provide the requirements" moment where retained stories saved the day.
- **Colored cards for story types**: appealing in theory, not worth the hassle in practice (carrying/refilling colors, rewrites); stick to a pile of white cards.

## Reference Tables
| NFR Area | Sample Constraint |
|---|---|
| Performance | 80% of database searches return to screen in < 2 seconds |
| Accuracy | Correctly predict the winner of a football game ≥ 55% of the time |
| Portability | Use no technology that makes porting to Linux difficult |
| Reusability | Database and access code reusable in future applications |
| Maintainability | Automated unit tests for all components, run fully every 24 hours |
| Interoperability | Written in Java; config in XML; data in MySQL |
| Capacity | Store 20 million members on specified hardware while meeting performance objectives |

## Worked Example
**Bugs as stories.** A bug expected to take about as long as a typical story is simply treated as its own story and planned like any other. Bugs the team can fix quickly are combined: with note cards, staple the bug cards together behind a cover story card, and for planning purposes treat the stapled bundle as a single story. (Supporting case: ClickTactics moved from cards to VersionOne because remote sales/management couldn't "go look at the board" and cards kept getting lost; J. B. Rainsberger's Diaspar used a FitNesse wiki with "todo" tags so a remote customer could answer questions a few times a week.)

## Key Takeaways
1. Express nonfunctional requirements as constraint cards, ideally with daily automated tests; supplement with other formats only when needed.
2. Neither cards nor software is universally best — start with cards, switch when distribution or traceability demands it.
3. An iterative process can churn the UI; for UI-critical apps add upfront, story-driven usage-centered design and treat UI stability as a constraint.
4. Err on the side of retaining stories — they've proven useful in acquisitions, rewrites, and contract moments.
5. Treat each bug as a story; staple quick bugs under a cover card.

## Connects To
- **Ch 7 (Good Stories)**: constraints handling originates there.
- **Ch 3 & 4 (User Roles / Gathering Stories)**: feed steps 1–2 of story-based usage-centered design.
- **Ch 12 / Ch 14**: cards' low-tech nature counters IEEE-830 creep and the "too many details" smell.
- **Constantine & Lockwood, Agile Usage-Centered Design**: external source for the UI design process.
