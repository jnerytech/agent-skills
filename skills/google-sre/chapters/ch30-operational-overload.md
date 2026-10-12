# Chapter 30: Embedding an SRE to Recover from Operational Overload
*Authors: Randall Bosetti (edited by Diane Bates)*

## Core Idea
When a team's ticket volume pushes it past the standard 50/50 project/ops split and it slides into "ops mode", temporarily embed **one** SRE. That SRE fixes the team's *practices and mental model*, not its ticket queue, so the team can self-regulate after the SRE leaves.

## Frameworks Introduced
- **Three-phase embedding engagement**: *Phase 1: Learn the Service and Get Context* → *Phase 2: Sharing Context* → *Phase 3: Driving Change*, closed by an after-action report (a "postvitam").
  - When to use: a team has spent months overloaded by tickets/ops and project work is stalled. It also helps when starting your first SRE team, to avoid becoming a ticket-rotation ops team.
  - How:
    1. *Learn*: shadow on-call; decide whether scale matters; rank outages by their **stress impact** on the team; identify **kindling**.
    2. *Share*: own and write the next **blameless postmortem** with the on-call engineer. Sort fires into **toil vs. not-toil** and present the list with the reason for each.
    3. *Drive change*: start with the basics (write an **SLO**); get the team to clear kindling (don't do it yourself); **explain your reasoning** for every decision; **ask leading questions**.
    4. Write the after-action report, then stay available for design/code reviews and watch the team for a few months.
  - Why it works: humans are good at homeostasis. Restore the right initial conditions and teach a small set of principles, and the team keeps making healthy choices. Team health is a *process*, not something heroic effort can solve.
  - Failure mode: the embedded SRE fixes things personally, which reinforces "making changes is for other people", or sends two SREs, which makes the team defensive.
- **Ops mode vs. nonlinear scaling**: in ops mode, work items grow with service size and are met by adding administrators. SRE instead writes software or eliminates scalability concerns so headcount does not grow as a function of load. "More tickets should not require more SREs". Add humans only as complexity grows.
- **Kindling checklist** (emergencies waiting to happen):
  - Knowledge gaps from overspecialization
  - SRE-developed services quietly increasing in importance
  - Strong dependence on "the next big thing" (temporary fixes ignored for months)
  - Common alerts that neither dev nor SRE diagnoses (triaged as "transient"). Investigate them fully or fix the rule.
  - A service that clients complain about and that lacks a formal SLI/SLO/SLA
  - A capacity plan that is effectively "Add more servers: our servers were running out of memory last night"
  - Postmortems whose only action items roll back the specific change
  - Serving-critical components where SREs say "We don't know anything about that; the devs own it"
- **Get Help Clearing Kindling (4 steps)**: (1) find useful work one team member can do; (2) explain how it fixes a postmortem issue *permanently*; (3) act as reviewer for the code/doc changes; (4) repeat for two or three issues. Log further issues in bugs or docs.
- **Explain Your Reasoning**: explain every decision, whether or not anyone asks, by tying it back to the basics (SLO, error budget, MTTR). Success test: after you leave, the team can predict your comment on a design or changelist.
- **Ask Leading Questions (not loaded questions)**: frame questions to make people reason from first principles.

## Key Concepts
- **Ops mode**: running a service by scaling people linearly with load.
- **Embedded SRE**: one SRE temporarily transferred into an overloaded team to improve its practices.
- **Kindling**: latent conditions that will become emergencies.
- **Largest sources of stress**: outages ranked by their effect on team stress, which may be out of proportion to their technical size.
- **Bad Apple Theory**: the false belief that the system is fine and only bad individuals cause failures. Evidence from airline safety and other fields refutes it.
- **Blameless postmortem**: records what the on-call engineer thought at each point, to find where the system misled them.
- **Toil vs. not-toil fires**: fires that shouldn't exist (automate them) vs. acceptable overhead of running the service.
- **SLO as primary lever**: "probably the single most important lever" for moving from reactive ops to SRE. Without it, nothing else in the chapter helps.
- **Postvitam**: an after-action report that explains the critical decisions that led to success (the opposite of a postmortem).

## Mental Models
- Think of your job as **making the service work, not shielding developers from alerts**.
- Use **one** embedded SRE, never two. Two don't produce better results and may trigger defensiveness.
- Think of the team as a **homeostatic system**: fix the initial conditions and principles, and it maintains itself.
- Use **"what's the effect on the SLO?"** as the universal argument. Every pushback should trace back to SLO, error budget or MTTR.

## Anti-patterns
- **Helping empty the ticket queue**: treats the symptom. The embedded SRE should change the practices.
- **"My service is tiny" so scale doesn't matter**: verify by shadowing on-call. A 100 req/s service can become 10k req/s in a year.
- **Leaving improvement comments on archived postmortems**: puts the team on the defensive. Own the *next* postmortem instead.
- **Rollback-only action items**: e.g., "Change the streaming timeout back to 60 seconds" instead of "Figure out why it sometimes takes 60 seconds to fetch the first megabyte".
- **Short-term loadtest passes as capacity planning**: if the model predicts 2 GB, a 1.99 GB run doesn't mean capacity is adequate.
- **Fixing kindling yourself**: bolsters the idea that "making changes is for other people".
- **Unexplained decisions**: the team will emulate the poor reasoning it observed.

## Reference Tables
| Explanation quality | Example |
|---|---|
| Good | "I'm not pushing back on the latest release because the tests are bad. I'm pushing back because the error budget we set for releases is exhausted." |
| Good | "Releases need to be rollback-safe because our SLO is tight. Meeting that SLO requires that the mean time to recovery is small, so in-depth diagnosis before a rollback is not realistic." |
| Insufficient → fixed | "Every server generating its routing config isn't safe because we can't see it" → "...isn't safe because a bug in that code can cause a correlated failure across the service and the additional code is a source of bugs that might slow down a rollback." |
| Insufficient → fixed | "Automation should give up on a conflicting deployment" → "...because we assume all changes pass through the automation, and something violated that rule. If frequent, identify and remove sources of unorganized change." |

| Leading question (good) | Counterexample (bad) |
|---|---|
| "The TaskFailures alert fires frequently but on-call usually doesn't act. How does this impact the SLO?" | "What's up with all of these old, stalled releases?" |
| "This turnup procedure looks complicated. Do you know why so many config files must be updated for a new instance?" | "Why does the Frobnitzer do so many things?" |

## Worked Example
**Reframing a defensive postmortem.** An outage happens during the embedding, and the on-call engineer asks "Why me?" because the team sees postmortems as retaliatory (Bad Apple Theory). The embedded SRE pairs with them and uses this framing: "Mistakes are inevitable in any system with multiple subtle interactions. You were on-call, and I trust you to make the right decisions with the right information. I'd like you to write down what you were thinking at each point in time, so that we can find out where the system misled you, and where the cognitive demands were too high." The postmortem then produces *permanent* fixes instead of rollbacks. That shows how the SRE model reduces outage impact on team time, and it seeds the Phase 3 kindling work.

## Key Takeaways
1. Send a single SRE to fix practices, not tickets. More tickets should not mean more SREs.
2. First write an SLO. Without it, no other improvement advice works.
3. Rank problems by their stress impact, then hunt kindling with the checklist.
4. Model blameless postmortems by owning the next one, not by critiquing old ones.
5. Sort fires into toil vs. acceptable overhead, and explain the reasoning for each.
6. Make the team fix things while you review. Explain every decision, and ask leading questions.
7. Close with a postvitam and action items, then stay on as a reviewer for months.

## Connects To
- **Ch 1 (Introduction)**: 50% cap on ops work, and headcount that should scale sublinearly with service size.
- **Ch 4 (SLOs)**: the SLO is the primary lever. The kindling checklist flags services without SLI/SLO/SLA.
- **Ch 5 (Eliminating Toil)**: the toil vs. not-toil fire sort.
- **Ch 6 (Monitoring)**: recommended reading before embedding. Fix undiagnosed "transient" alerts.
- **Ch 15 (Postmortem Culture)**: blameless postmortems and permanent action items.
- **Ch 29 (Dealing with Interrupts)**: team-level interrupt structure that prevents overload.
- **External, Dekker's "Field Guide to Understanding Human Error"**: the refutation of the Bad Apple Theory.
