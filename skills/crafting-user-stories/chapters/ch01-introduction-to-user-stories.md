# Chapter 1: Introduction to User Stories

## Core Idea
A user story is a short, informal description of a feature written from the end user's perspective — capturing the *who, what,* and *why* — and INVEST is the quality bar that makes one effective.

## Frameworks Introduced
- **User Story Template** — `As a [user role], I want [feature/goal], so that [benefit].`
  - When to use: every requirement you capture in Agile.
  - How: name the **persona** (who), the **action/goal** (what), the **benefit** (why). The "so that" is what keeps the story user-centered instead of feature-centered.
- **INVEST model** — quality criteria for a good story:
  - **I**ndependent — self-contained, no dependency on other stories (faster dev/test cycles).
  - **N**egotiable — a conversation placeholder, scope can change during development.
  - **V**aluable — delivers clear benefit to the user.
  - **E**stimable — effort can be sized, or it can't be planned.
  - **S**mall — completable in one iteration/sprint.
  - **T**estable — has criteria to confirm it meets user needs.
  - When to use: as a checklist before accepting a story into the backlog.
- **Three core components** — Persona, Action, Goal. Optional extras: acceptance criteria, epics.

## Key Concepts
- **User story**: concise, informal feature description from the user's view, written by the product owner.
- **Persona**: the user/stakeholder the story focuses on — role, goals, needs.
- **Epic**: a large story too big for one sprint; broken down into smaller stories.
- **Acceptance criteria**: conditions that must be met for a story to be "done."
- **Product backlog**: prioritized list of stories the product owner orders by user value.
- **Use case** (Cockburn, early 1990s): the more formal/rigid predecessor user stories reacted against.

## Mental Models
- Think of a story as a **placeholder for a conversation**, not a contract spec — "Negotiable" is the point.
- Use the **"so that" test**: if you can't state the benefit, the story isn't user-focused yet.
- Origin (late 1990s): Kent Beck & Ron Jeffries created stories as a lightweight, customer-centric alternative to heavyweight requirements docs.

## Anti-patterns
- **Writing epics instead of stories**: too big to plan/estimate → split into sprint-sized stories.
- **Not focusing on the user**: stories drift into technical detail → keep the persona at the front.
- **Failing to include acceptance criteria**: can't tell when "done" → add clear, specific criteria.
- **Not prioritizing**: low-value work ships first → order backlog by user/product value.
- **Failing to collaborate**: misalignment → involve dev team, product owner, end users.

## Worked Example
INVEST-conformant, user-focused story:

> *As a customer, I want to be able to save my payment information so that I don't have to enter it every time I make a purchase.*

- **Persona**: customer. **Action**: save payment info. **Benefit**: convenience on future purchases.
- Passes INVEST: independent of other features, negotiable in scope, valuable (saves time), estimable, small (one sprint), testable (info persists across purchases).

Prioritization examples — same template surfaces requirements to rank:
- *As a frequent traveler, I want to search flights by date and destination so that I can find the best options.*
- *As an online shopper, I want to filter products by price so that I can find items within my budget.*

## Key Takeaways
1. Stories capture the *who/what/why* — always include "so that."
2. INVEST is the acceptance filter for whether a story is ready.
3. Split epics down to sprint-sized stories before estimating.
4. A story is a conversation starter; detail (acceptance criteria) is added through collaboration.
5. Stories run through the whole SDLC: planning (build backlog), design (drive UX/workflows), testing (derive test cases).

## Connects To
- **Ch 2**: who the persona is — personas, empathy maps, user research.
- **Ch 3**: how to write the story well — guidelines, acceptance criteria.
- **Ch 4**: prioritizing and estimating the backlog.
- **External**: ATDD/BDD use stories as the seed for acceptance tests; INVEST coined by Bill Wake.
