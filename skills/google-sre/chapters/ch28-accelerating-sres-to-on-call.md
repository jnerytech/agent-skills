# Chapter 28: Accelerating SREs to On-Call and Beyond
*Subtitle: How Can I Strap a Jetpack to My Newbies While Keeping Senior SREs Up to Speed?*
*Author: Andrew Widdowson (edited by Shylaja Nukala)*

## Core Idea
Replace "trial by fire" with structured, sequential, varied learning (postmortems, reverse engineering, disaster role play, real breakages, shadowing) that builds the *trust* a team needs before a newbie goes on-call, and that keeps senior SREs current too. "You have to scale your humans faster than you scale your machines."

## Frameworks Introduced
- **SRE education practices (Table 28-1)**: recommended patterns paired with their anti-patterns (see Reference Tables).
  - When to use: designing or auditing any onboarding program. Pick a mix that suits different learning styles, because there's no single formula.
- **Blueprint for bootstrapping an SRE to on-call and beyond (Figure 28-1)**: two axes. X runs from abstract/passive to applied/active work. Y is time, read top-down: postmortems and reverse engineering first, then hands-on work, then shadow on-call and fixing docs, then on-call. Project work & ownership is triangular (starts small, grows, continues past on-call). Activities after on-call are dashed (self-directed). Pace them: some immediate, some just before on-call, some continual even for veterans.
- **Learning Paths That Are Cumulative and Orderly**: frontload recurring abstract concepts and get hands-on as soon as practical. Order the curriculum by purpose or by normal-case execution order. Example for a user-facing serving stack: (1) how a query enters the system; (2) frontend serving; (3) mid-tier services; (4) infrastructure; (5) tying it all together (debugging, escalation, emergencies).
  - Why it works: it answers the student's three questions: *What am I working on? How much progress have I made? When will I be ready for on-call?* Vague answers slow development and hurt retention.
- **On-call learning checklist** (Google Search SRE): per component, list who fronts it and its backends, SRE experts, developer contacts, docs to read, "Know before moving on", and comprehension questions. It's future-proof because it lists contacts, docs, required knowledge and probing questions rather than procedures. Mentors check homework answers before the student moves to the next phase.
  - Serves three audiences. *Student*: system boundaries and what matters most. *Mentors/managers*: observable progress ("which sections today? most confusing?"). *Team*: a **social contract**, since mastering it admits the student to on-call.
- **Tiered access / "powerups"**: completing checklist sections earns progressively deeper access, from read-only to mutating production state.
- **Targeted Project Work, Not Menial Work**: starter projects split time with learning. Patterns: (1) ship a trivial user-visible feature change all the way to production (builds developer empathy); (2) add monitoring where there are blind spots; (3) automate a not-yet-painful-enough pain point (teaches the value of removing toil).
- **Three SRE attributes to train for**: **Reverse engineers** (dig into debugging surfaces, RPC boundaries and logs of unfamiliar systems); **Statistical and comparative thinkers** (prune the incident decision tree with hypotheses: "which of these things is not like the other?" across kernel, CPU arch, binary versions, regional traffic mix); **Improv artists** (improvise when SOPs fail, avoid untested assumptions, "zoom out").
- **Five Practices for Aspiring On-Callers**:
  1. **A Hunger for Failure: Reading and Sharing Postmortems**: curate "teachable postmortems", run "postmortem reading clubs" and "tales of fail" sessions.
  2. **Disaster Role Playing** ("Wheel of Misfortune" / "Walk the Plank").
  3. **Break Real Things, Fix Real Things**.
  4. **Documentation as Apprenticeship**.
  5. **Shadow On-Call Early and Often** (then reverse shadow).
  - Why it works: "able to take on-call" is a useful proxy for "knows enough and can figure out the rest".

## Key Concepts
- **Trial by fire**: onboarding by dumping tickets and alerts on newbies. It alienates capable engineers, and "if the tickets queue adequately trains for the job, this is not an SRE position."
- **Proactive vs. reactive work**: automation, design consulting and launch coordination vs. debugging, troubleshooting and escalations. Onboarding should be proactive.
- **Teachable postmortem**: a postmortem lightly edited so an engineer "who hasn't yet been hired" can learn structural or novel failure lessons from it.
- **Wheel of Misfortune**: a weekly tabletop RPG. A Game Master (GM) picks primary and secondary on-call, announces a page, and reveals consequences of their actions over 30–60 min.
- **"Let's burn a search cluster to the ground!"**: a quarterly Search SRE exercise that progressively impairs a known-good stack and compares predictions with observed behavior.
- **Shadow on-call**: pages copied to the newbie (business hours first) with no responsibility and no time pressure. Afterwards the on-caller reviews their reasoning with them.
- **Reverse shadow**: the newbie is primary, and the veteran diagnoses independently without changing state, ready to help.
- **Rite of passage**: going on-call is gated by a final exam or a completed checklist and should be celebrated as a team.
- **Reverse Engineering a Production Service (without help from its owners)**: a Google class built on the scenario of the Google News team lost on a Bermuda Triangle cruise.

## Mental Models
- Think of **incident response as pruning a massive decision tree**: experience plus well-built hypotheses cut the space.
- Use **newbie enthusiasm to fix stale docs**: seniors keep state in their heads, while newbies need current docs. Assign the most outdated sections to the incoming hire.
- Think of **"follow the RPC"** as the universal way into an unknown stack, interactive or batch. For batch, start with the triggering operation.
- Use **realism** in hands-on training: a production instance diverted from live traffic, or a full-featured staging/QA instance, under synthetic load.

## Anti-patterns
- **Trial by fire / deluging with menial ticket triage**.
- **Training strictly through procedures, checklists and playbooks**: produces operators, not reasoners.
- **Burying outages as secrets to avoid blame**.
- **First chance to fix something only after already on-call**.
- **Compartmentalized experts**: knowledge silos.
- **Pushing students to primary on-call before holistic understanding**.
- **Static on-call training docs editable only by SMEs**.
- **Giving all new projects to seniors**: juniors "pick up the scraps".
- **Dumping postmortem writing solely on the newbie**: teaches that postmortems are grunt work. Make them coauthor instead.
- **Being too procedural during an outage**: forgets analytical skills and gets stuck on untested assumptions.

## Reference Tables
**Table 28-1. SRE education practices**
| Recommended patterns | Anti-patterns |
|---|---|
| Concrete, sequential learning experiences | Deluging with menial work (alert/ticket triage); "trial by fire" |
| Reverse engineering, statistical thinking, fundamental principles | Training strictly via operator procedures, checklists, playbooks |
| Celebrating failure analysis via suggested postmortems | Treating outages as secrets to bury to avoid blame |
| Contained but realistic breakages fixed with real monitoring/tooling | First fix opportunity only once on-call |
| Group role-play of theoretical disasters | Experts with compartmentalized techniques/knowledge |
| Early shadowing of on-call, comparing notes | Primary on-call before holistic understanding |
| Pairing students with experts to revise on-call training plan sections | Static training plans editable only by SMEs |
| Nontrivial project work with partial ownership | All new project work to seniors, scraps to juniors |

**Example on-call learning checklist section: Results Mixing Server ("Mixer")**
```
Frontended by: Frontend server
Backends called: Results Retrieval Server, Geolocation Server, Personalization Database
SRE experts: Sally W, Dave K, Jen P
Developer contacts: Jim T, results-team@
Read and understand the following docs:
  - Results Mixing Overview: "Query execution" section
  - Results Mixing Overview: "Production" section
  - Playbook: How to Roll Out a New Results Mixing Server
  - A Performance Analysis of Mixer
Know before moving on:
  - Which clusters have Mixer deployed
  - How to roll back a Mixer release
  - Which backends of Mixer are considered "critical path" and why
Comprehension questions:
  - Q: How does the release schedule change if a company holiday occurs on the normal release build day?
  - Q: How can you fix a bad push of the geolocation dataset?
```
What it demonstrates: a checklist that lists contacts, docs, required knowledge and probing questions rather than procedures, so it stays durable as the system changes.

## Worked Example
**Wheel of Misfortune session**: the GM prepares a scenario, which could be a past outage newer members missed, a hypothetical breakage of a soon-to-launch feature (everyone equally unprepared), or a novel breakage a coworker just found. The GM picks primary and secondary on-callers to join them at the front and announces a page. The on-callers say what they would query or do, and the GM describes the results (e.g., what dashboards show), plays other teams on escalation, and steers away from red herrings with stimuli ("You're getting paged by another team…") or urgency ("We're losing money quickly! How could you stop the bleeding?"). After 30–60 minutes everyone has learned a tool, a perspective, or (for newbies) that they could have solved it. "SRE Zork."

**Let's burn a search cluster to the ground** (quarterly): (1) discuss which observable performance characteristics might change as the stack is crippled; (2) poll participants for predictions and reasoning before inflicting damage; (3) validate assumptions and justify the observed behavior. It regularly shakes out bugs because systems don't degrade as gracefully as expected.

## Key Takeaways
1. Replace ticket-queue onboarding with an ordered curriculum (query entry → frontend → mid-tier → infra → tie together) captured in an on-call learning checklist with comprehension questions.
2. Gate production access in tiers ("powerups") tied to checklist progress.
3. Give each newbie a real starter project: a feature to prod, monitoring for blind spots, or automating toil.
4. Run weekly Wheel of Misfortune and periodic real-breakage exercises on diverted or staging stacks under synthetic load.
5. Curate teachable postmortems and run reading clubs. Make newbies coauthors, not sole authors.
6. Shadow on-call (business hours first) across multiple teammates, then reverse shadow, then celebrate the on-call rite of passage.
7. Keep learning after on-call: recorded talks on upcoming stack changes, co-presented with developers, and SRE talks to developers.

## Connects To
- **Ch 11**: being on-call, the target state of this training.
- **Ch 12**: effective troubleshooting. Hypothesis-driven, comparative reasoning.
- **Ch 15**: postmortem culture. Teachable postmortems.
- **Ch 5**: toil. Starter projects that automate pain points.
- **Ch 29 / Ch 30**: interrupts and operational overload, the context that tempts teams into trial by fire.
- **Ch 31**: communication and collaboration.
- **Ch 26 / Ch 33**: DiRT and disaster testing, the organizational cousin of Wheel of Misfortune.
- **External**: tabletop RPGs, apprenticeship models, game-day exercises.
