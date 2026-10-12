# Chapter 5: Working with Stakeholders

## Core Idea
A product succeeds only when the right stakeholders are identified, categorized by influence, and kept actively engaged through transparent, two-way communication — from requirements elicitation and backlog building through prioritization, conflict resolution, and delivery feedback.

## Frameworks Introduced

- **Power/Interest Matrix**: categorize stakeholders by their level of *power* (influence over the product) and *interest* (stake in the outcome).
  - When to use: after listing all stakeholders, to decide how much engagement each one warrants.
  - How: plot each stakeholder on two axes (power, interest); high-power/high-interest get the most engagement and joint decision-making; low/low get periodic updates only.

- **Salience Model**: categorize stakeholders by *power*, *urgency*, and *legitimacy*.
  - When to use: when influence alone is insufficient and timing/legitimacy of claims matters.
  - How: assess each stakeholder against the three attributes; those holding all three are the most salient and demand priority attention.

- **MoSCoW prioritization**: sort backlog items into Must-have, Should-have, Could-have, Won't-have.
  - When to use: prioritizing the backlog against stakeholder needs and scope constraints.
  - How: classify each item with stakeholders; commit to Musts first, treat Won'ts as explicitly out of scope.

- **Value-based prioritization**: rank backlog items by the value they deliver to the customer and product objectives.
  - When to use: alongside or instead of MoSCoW when value, not just necessity, drives sequencing.
  - How: score items by customer/business value; develop the highest-value items first.

- **Conflict resolution ladder**: Understand → Collaborate/Compromise → Active Listening → Negotiate → Escalate.
  - When to use: when stakeholder conflict arises from differing opinions, competing priorities, or communication breakdowns.
  - How: first diagnose source and parties; seek a mutually beneficial (collaborative) or middle-ground (compromise) solution; listen actively; negotiate creative options; escalate to a higher authority or mediator only as a last resort.

- **Crucial Conversations technique** (Grenny, Patterson, Switzler, McMillan): handle discussions where opinions differ, stakes are high, and emotions run strong.
  - When to use: aligning stakeholders with conflicting expectations before conflict damages the product.
  - How: create a safe environment (ground rules, no blame); use active listening (clarify, summarize, validate emotions); state your view with "I" statements, avoiding absolutes; prepare by knowing your own triggers and the other party's motivations.

## Key Concepts
- **Stakeholder**: any individual or group with a vested interest in the product — internal (employees, managers, execs, shareholders) or external (customers, suppliers, partners, regulators).
- **Product backlog**: living, owner-maintained list of features, enhancements, and fixes, continuously refined from feedback.
- **Stakeholder mapping**: visualizing the stakeholder landscape and relationships to surface key players.
- **Stakeholder management plan**: document outlining how each stakeholder group will be engaged and have expectations managed.
- **Communication plan**: defines what information is shared, how often, by what method — two-way, with active listening and feedback.
- **Transparency**: giving stakeholders access to plans, timelines, budgets, and risks to build trust.
- **Stakeholder resistance**: pushback on changes affecting a stakeholder's interests, requiring acknowledgment, alternatives, and a contingency plan.
- **Tailored communication**: matching mode and detail to the audience (visual aids for designers, technical specs for developers).
- **Best-practice-in-context**: "no such thing as best practices, only best practices in context" — adapt rather than blindly adopt.

## Mental Models
- Use the **Power/Interest Matrix** when you have a long stakeholder list and limited engagement bandwidth — it tells you where to spend effort.
- Use **active listening + "I" statements** when emotions are high and a conversation is crucial, rather than asserting position or assigning blame.
- Use **escalation** only when collaboration, compromise, listening, and negotiation have all been exhausted — never as a first move.
- Use **early and continuous involvement** when requirements are uncertain, so stakeholder needs shape the backlog before code is written, not after.

## Anti-patterns
- **Identifying stakeholders late**: needs and expectations get baked in without their input, forcing costly rework.
- **One-size-fits-all communication**: ignoring that designers, developers, and executives consume information differently kills shared understanding.
- **Blindly copying "best practices"**: ignores industry, culture, team dynamics, and constraints unique to your context.
- **Treating the backlog as static**: a backlog not refined against feedback drifts away from real stakeholder needs.
- **Avoiding crucial conversations**: poor handling causes delays, low morale, and a suboptimal product.
- **Escalating prematurely**: jumping to a higher authority before genuine attempts at resolution erodes trust.

## Worked Example
**Collaborative workshop — new e-commerce platform.** A product manager facilitates a cross-functional session to define the platform before development:
- *Invitees (by function):* marketing, sales, design, development — chosen to cover the range of expertise needed.
- *Goal:* collectively define key features, target audience, and business goals.
- *Method:* brainstorm ideas together, then converge on shared priorities; output feeds directly into the product backlog.
- *Outcome:* cross-functional alignment and a shared vision, reducing later ambiguity and rework.

This pairs with **user interviews** (e.g., a mobile-banking PM probing interface and feature preferences) and **usability testing** (observing stakeholders complete tasks on a prototype) as the three elicitation channels feeding prioritized backlog decisions.

## Key Takeaways
1. List every stakeholder early, then categorize with a Power/Interest matrix or salience model to allocate engagement proportionally.
2. Build the backlog from real elicitation — interviews, surveys, user/usability testing, workshops — and keep refining it.
3. Prioritize explicitly with MoSCoW and value-based methods, deciding *with* stakeholders, not for them.
4. Write a communication plan: define content, frequency, and mode; make it two-way and tailor it per audience.
5. Set realistic expectations on scope, timeline, and budget, and communicate changes promptly to pre-empt resistance.
6. Walk the conflict-resolution ladder (understand → collaborate/compromise → listen → negotiate → escalate) and reserve escalation for last.
7. Prepare for crucial conversations: create safety, listen actively, and state your view with "I" statements.

## Connects To
- **Ch 4**: acceptance criteria depend on stakeholder needs surfaced and prioritized here.
- **Ch 6**: backlog and stories built with stakeholders feed directly into user story refinement and continuous improvement.
- **Communication/EI chapters**: stakeholder engagement relies on the emotional intelligence, empathy, and self-regulation those chapters develop.
