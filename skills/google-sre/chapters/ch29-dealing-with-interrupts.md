# Chapter 29: Dealing with Interrupts
*Authors: Dave O'Connor (edited by Diane Bates)*

## Core Idea
Operational load (pages, tickets, ongoing ops) is inevitable. Structure it at the team level so each engineer's day is *polarized*: either fully on interrupts or fully on project work. Context switches are expensive, and humans are "imperfect machines" whose flow state is worth protecting.

## Frameworks Introduced
- **Three categories of operational load**: *pages* (production alerts, SLO measured in minutes), *tickets* (customer requests, SLO in hours/days/weeks), and *ongoing operational responsibilities* (also called "kicking the can down the road" or toil: rollouts, flag flips, ad hoc time-sensitive questions, often with no SLO).
  - When to use: as a starting inventory of what interrupts your team before you decide who handles each class.
  - How: list each interrupt source, classify it, then assign an owner model per class: a single primary on-call for pages (a single engineer avoids the bystander effect), a secondary as backup, and a dedicated ticket person or rotation.
- **Interrupt-handling metrics**: interrupt SLO/expected response time; number of interrupts usually backlogged; severity; frequency; number of people available to handle that kind of interrupt.
  - When to use: deciding how to staff and route each interrupt class.
  - Caveat: all of these optimize for the lowest response time and ignore human and productivity cost. Weigh that cost explicitly.
- **Polarizing time**: when someone arrives in the morning, they should know whether they are doing *just project work* or *just interrupts*. Make each period as long as possible: ideally a week, practically a day or half-day. It complements Graham's "make time".
  - When to use: always, as the default team structure.
  - How: assign a cost to context switches (a 20-minute interruption = 2 context switches ≈ a couple of hours of lost productive work); write off on-call weeks for project work; route all interrupt classes to the people on interrupts.
  - Why it works: when you concentrate full-time on interrupts, *interrupts stop being interrupts*. They become clear goals with clear feedback (close X bugs, stop getting paged), and projects become the distraction. Mixing the two leaves people in constant "interruptability", which is very stressful.
  - Failure mode: someone who is "free" for projects is still pulled in by randomly assigned tickets, colleagues' pages, escalated old tickets, and long rollouts they still shepherd (the Fred scenario).
- **Cognitive flow state**: "the zone", with clear goals, immediate feedback, a sense of control and time distortion. You can reach it through low-skill tasks (the *Angry Birds* mode: whacking tickets, chasing problems) or high-skill tasks (the *creative and engaged* mode). Maximize time in either; avoid the interrupted in-between.
- **"Seriously, Tell Me What to Do" components**, which can be adopted piecemeal:
  1. *General*: if one class of interrupt is too much for one person, **add another person**. On-call can bump work to the secondary or downgrade pages to tickets.
  2. *On-call*: primary does only on-call work. On a quiet pager, do quickly-abandonable interrupt work. If a project can't slip a week, that person shouldn't be on-call.
  3. *Secondary*: if it's purely a fallthrough backup, it can do project work. If it actively helps with high pager volume, it is on interrupts too. Consider merging the secondary role with the ticket role.
  4. *Tickets*: **stop assigning tickets randomly**. Make tickets a full-time role. If the load exceeds primary plus secondary, put two people on tickets rather than spreading them across the team.
  5. *Ongoing responsibilities*: define roles anyone can take up (e.g., a **push manager**) and formalize the handover, so no one shepherds a change across its whole lifetime.
  6. **Be on interrupts, or don't be**: people off rotation shouldn't grab tickets to look busy. It hides how unmanageable the queue really is.

## Key Concepts
- **Operational load**: work required to keep a complex system functional (like servicing a car).
- **Primary on-call**: the single engineer who handles pages and resulting incidents. One person avoids the bystander effect.
- **Secondary on-call**: backup for the primary. Its duties range from "contact primary on fallthrough" to active interrupt help.
- **Interruptability**: the state of constant possible interruption. It is the main source of on-call stress.
- **Context-switch cost**: the hidden loss when an interruption breaks flow. It is far greater than the interruption's duration.
- **Make time**: long uninterrupted blocks for creative work (Graham's maker schedule).
- **Push manager**: a rotating role that juggles all pushes/rollouts during its on-call/interrupt period.
- **Ticket/page scrub**: a regular review of interrupt classes to find root causes.
- **Gauntlet rotation**: a rotation where each person "runs the gauntlet", sighs in relief, and hands off without fixing root causes.
- **Undistractible**: the goal state where people can arrive in the morning and not be pulled into interrupts.

## Mental Models
- Think of an engineer as **not** an interruptible unit of work with free context switches. Price every switch at hours, not minutes.
- Use **polarization** when the team mixes project and ops work: separate them in time rather than splitting each person's attention.
- Think of **policy as being as powerful a tool as code**: your team sets the level of service, and it's OK to push effort back onto customers.
- Use **silencing until fixed** when a root cause is fixable in reasonable time. It relieves the interrupt handler and sets a deadline for the fixer.

## Anti-patterns
- **Randomly autodistributing tickets across the team**: disrespects the team's time and maximizes context switches.
- **Being on-call while expected to make project progress**: guarantees both suffer.
- **Spreading ticket load across the whole team**: people are not machines, so every extra handler multiplies context switches.
- **Shepherding a multiweek rollout after your shift ends**: drags you back into interrupts during make time.
- **Working tickets when not assigned, to look busy**: skews load numbers and hides an unmanageable queue.
- **Gauntlet-style rotations without ticket handoff**: root causes are never investigated. Many teams do page handoffs and reviews, very few do the same for tickets.
- **Endlessly supporting a flaky, under-resourced tool for a few needy customers**: if you can't get root-cause attention, consider giving the pager back, deprecating it, or replacing it.

## Worked Example
**Fred's "free" Monday.** Fred isn't on-call, puts on "do not disturb" headphones and expects zone time. Then:
1. The auto-ticketing system assigns him a ticket due today.
2. The on-call colleague pings him about a component he's expert in.
3. A user escalates the priority of a ticket from his on-call week last week.
4. A 3–4-week flag rollout assigned to him goes wrong, so he drops everything to roll back.
5. A user asks him a question directly because he's helpful.

Some of this he can fix personally (closing email/IM). Most is caused by **team policy**: random ticket assignment, lifetime ownership of rollouts, tickets that stick to whoever was on-call. The fix is structural. Use a dedicated ticket role, a push-manager role with formal handover, ticket handoff at rotation end, and sparse use of uniquely qualified people. Then Fred can be genuinely undistractible on project days.

## Key Takeaways
1. Classify interrupts into pages, tickets and ongoing ops, then give each class an explicit owner model.
2. Polarize time: each person, each day (ideally each week), is either on interrupts or on projects, never both.
3. Write off on-call weeks for project work. Swap someone else in if a project can't slip.
4. Stop random ticket assignment. Make tickets a dedicated role and add a second person before spreading the load.
5. Do handoffs and regular scrubs for tickets as well as pages. Silence fixable interrupt classes until the root cause is fixed.
6. Use policy: push privilege-free legwork back to requestors, and require requests to be meaningful, rational and complete. In return, respond helpfully and promptly.
7. When the pager is quiet, do cleanup (docs, configs). You never run out of cleanup work.

## Connects To
- **Ch 5 (Eliminating Toil)**: ongoing operational responsibilities are toil. Reducing interrupts is toil reduction.
- **Ch 11 (Being On-Call)**: primary/secondary structure, on-call load limits.
- **Ch 30 (Operational Overload)**: what to do when interrupt load swamps the 50% project time.
- **Ch 28 (Accelerating SREs to On-Call)**: some teams require ticket work before going on-call.
- **Ch 6 (Monitoring)**: downgrading pages to tickets and removing unactionable alerts.
- **External, flow (Csikszentmihalyi)** and **Paul Graham's maker's schedule/"make time"**.
