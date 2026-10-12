# Chapter 14: Managing Incidents
*Authors: Andrew Stribblehill (edited by Kavita Guliani)*

## Core Idea
Effective incident management channels enthusiastic individuals through a pre-agreed structure — distinct roles, a command post, a live incident document, and explicit handoffs — based on the **Incident Command System**, so incidents don't spiral and mean time to recovery drops.

## Frameworks Introduced
- **Incident management process (based on the Incident Command System, ICS)**: four features of a well-designed process:
  1. **Recursive separation of responsibilities** — everyone knows their role and stays off others' turf; overloaded members ask the planning lead for staff, delegate, create **subincidents**, or delegate components whose owners report up.
  2. **A recognized command post** — a "War Room" or a known channel (Google uses **IRC**: reliable, loggable, bots log alerts and traffic, good for distributed teams).
  3. **Live incident state document** — kept by the incident commander; concurrently editable; template-based; most important info at the top; retained for postmortem and meta-analysis (Appendix C sample).
  4. **Clear, live handoff** — explicitly state "You're now the incident commander, okay?" and don't leave the call until firm acknowledgment; announce the handoff.
  - When to use: any event meeting the declaration criteria; also for routine cross-team/time-zone changes, for practice.
  - Why it works: clear separation of responsibilities counterintuitively gives individuals *more* autonomy — they don't second-guess colleagues; structure scales smoothly.
  - Failure mode: skills atrophy quickly when not in constant use; an ad hoc response under pressure defaults to the unmanaged pattern.
- **Incident roles**:
  - **Incident Command (IC)**: holds high-level state; structures the task force; assigns responsibilities by need/priority; *de facto holds every role not delegated*; removes roadblocks for Ops.
  - **Operational Work (Ops lead)**: applies operational tools with the IC; **the ops team is the only group modifying the system during an incident.**
  - **Communication**: public face of the task force; periodic updates to team and stakeholders (usually email); may keep the incident doc current.
  - **Planning**: supports Ops on longer-term issues — files bugs, orders dinner, arranges handoffs, tracks how the system diverged from normal so it can be reverted.
- **When to Declare an Incident** — declare if **any** is true:
  1. Do you need to involve a **second team** in fixing the problem?
  2. Is the outage **visible to customers**?
  3. Is the issue **unsolved even after an hour's concentrated analysis**?
  - Principle: better to declare early and close quickly with a simple fix than to spin up the framework hours into a growing problem.
- **Best Practices for Incident Management**:
  - **Prioritize**: stop the bleeding, restore service, preserve evidence for root-causing.
  - **Prepare**: develop and document procedures in advance, with incident participants.
  - **Trust**: give full autonomy within the assigned role.
  - **Introspect**: watch your emotional state; if panicky or overwhelmed, get support.
  - **Consider alternatives**: periodically re-evaluate whether to continue or change tack.
  - **Practice**: use the process routinely so it becomes second nature.
  - **Change it around**: rotate roles so everyone knows each one.

## Key Concepts
- **Unmanaged incident**: everyone "doing their job" with no structure, leading to escalation of damage.
- **Sharp focus on the technical problem**: the technically strongest responder gets absorbed in fixing and loses the big picture of mitigation.
- **Poor communication**: no one knows coworkers' actions; leaders angry; helpers unused.
- **Freelancing**: uncoordinated changes by well-meaning individuals that worsen the situation.
- **Incident Command System (ICS)**: FEMA-origin emergency management framework known for clarity and scalability.
- **Subincident**: a delegated child incident when a role's load becomes excessive.
- **War Room**: central designated location for the task force.
- **Living incident document**: messy but functional shared state; don't host it on the system you're fixing (Google Docs SRE use Google Sites).
- **Prearranged mailing list**: channel for high-level status updates to stakeholders/VPs without minutiae.

## Mental Models
- Think of the IC as the default owner of every unassigned responsibility — delegate deliberately to shed load.
- Use the declaration criteria as a cheap trigger: the cost of a false-positive declaration is small; the cost of a late one is large.
- Think of separation of roles as enabling autonomy, not bureaucracy.
- Use non-emergency operational changes spanning teams/time zones and DR tests as practice rounds; role-play already-solved on-call issues.

## Anti-patterns
- **Lone hero debugging while everyone else waits**: no one mitigates or communicates.
- **Freelancing changes to production** (Malcolm's CPU-affinity push killed the remaining servers).
- **"Just looking" bystanders without roles**: no coordination.
- **Executives demanding ETAs from the responder**: consumes cognitive effort; route through the communication role.
- **Implicit handoffs / leaving before acknowledgment.**
- **Hosting incident tooling on the failing system.**
- **Declaring the incident hours late.**

## Reference Tables
| Role | Owns | Key rule |
|---|---|---|
| Incident Commander | High-level state, staffing, priorities, roadblocks | Holds all undelegated roles; keeps live doc |
| Ops lead | Operational changes | Only Ops modifies the system |
| Communication | Stakeholder/team updates, incident doc | Periodic updates (usually email) |
| Planning | Bugs, food, handoffs, divergence tracking | Enables later revert to normal |

| Unmanaged hazard | Managed countermeasure |
|---|---|
| Sharp focus on technical problem | Separate IC from Ops |
| Poor communication | Communication role + mailing list + live doc |
| Freelancing | Only Ops changes the system; helpers report actions to Ops lead |

## Worked Example
**Mary at The Firm, managed vs unmanaged.** Unmanaged: 2 p.m. Friday, datacenters 1, 2, then 3 of 5 stop serving; survivors overload and the service fails. Mary stares at logs, reverts the release (no help), wakes developer Josephine (3:30 a.m. her time); Sabrina and Robin poke around "just looking"; VPs demand ETAs and suggest "Increase the page size!"; Josephine calls Malcolm, who pushes an uncoordinated CPU-affinity change — servers restart and die.

Managed: after the second DC fails, Mary recognizes a rapidly growing issue and asks Sabrina, "Can you take command?" Sabrina (IC) gets a rundown, emails a prearranged list, records Mary's impact assessment ("Users have yet to be impacted") in the live incident doc. When the third alert fires she updates the email thread (keeping VPs informed), asks external comms to draft user messaging, and — with Mary's approval — loops in developer on-call Josephine. Robin volunteers; Sabrina tells Robin and Josephine to prioritize tasks delegated by Mary (Ops) and report any actions to her; both onboard via the incident doc. Mary's old-binary rollback fails; Robin posts it on IRC; Sabrina pastes it into the doc. At 5 p.m. Sabrina arranges replacements, a 5:45 call syncs everyone, and at 6 p.m. they hand off to the sister office. Next morning the incident is mitigated, closed, and the postmortem started; Mary plans structural improvements.

## Key Takeaways
1. Declare an incident early if a second team is needed, customers see it, or an hour of focused analysis hasn't solved it.
2. Separate IC, Ops, Communication and Planning roles; the IC holds anything not delegated.
3. Allow only the Ops team to change the system; everyone else coordinates through the Ops lead.
4. Maintain a live, concurrently editable incident document with key info at the top, hosted off the failing stack.
5. Hand off command explicitly and wait for acknowledgment; announce it.
6. Practice the framework on routine cross-team changes, DR tests and role-plays, and rotate roles.
7. Prioritize: stop the bleeding, restore service, preserve evidence.

## Connects To
- **Ch 11**: on-call relies on this protocol and its supporting web tool.
- **Ch 12**: triage and stopping the bleeding.
- **Ch 13**: real emergencies where (not) following the process mattered.
- **Ch 15**: postmortems drawing on the incident document and IRC logs.
- **Ch 16**: tracking outages / meta-analysis.
- **Ch 28**: Wheel of Misfortune role-play.
- **Appendix C (Ch 35)**: example incident state document.
- **Incident Command System (FEMA NIMS)**: the source model.
