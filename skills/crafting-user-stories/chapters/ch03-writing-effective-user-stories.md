# Chapter 3: Writing Effective User Stories

## Core Idea
An effective user story is a short, user-perspective description built from three parts (persona, action, goal), paired with testable acceptance criteria, kept simple, unambiguous, and independent — and treated as a conversation starter, not a frozen specification.

## Frameworks Introduced
- **The user story anatomy (Persona / Action / Goal)**: every story decomposes into three elements.
  - When to use: drafting any user story.
  - How: name a specific **Persona** (target user with role/context), state the **Action** they want to perform (active voice, *what* not *how*), and state the **Goal** — the SMART (specific, measurable, achievable, relevant, time-specific) outcome/value they get.
- **Standard story format**: `As a [user], I want [goal], so that [reason]`.
  - When to use: enforce consistency across all stories.
  - How: fill persona, action, and the "so that" value clause; keep one need per story.
- **Acceptance criteria**: the specific, measurable conditions that must be met for a story to be "done."
  - When to use: every story, before development starts.
  - How: write in clear, concise, jargon-free language; make each criterion specific/measurable; focus on the end user; include negative scenarios and edge cases; develop collaboratively with stakeholders.
- **Job stories (Jobs-to-be-Done)**: `When [situation], I want to [motivation], and so I can [expected outcome]`.
  - When to use: complement user stories when you need underlying motivation/context rather than features; product discovery and design phases.
  - How: capture the triggering situation, the user's motivation, and the expected outcome; stay solution-agnostic. Coined by Clayton Christensen; popularized by Alan Klement and Bob Moesta.
- **Story mapping**: arrange stories on two axes to visualize the end-to-end user journey.
  - When to use: to see product scope holistically, sequence work, and identify the MVP.
  - How: horizontal axis = user's workflow/journey (backbone of high-level activities/epics); vertical axis = priority/level of detail (stories broken down beneath each activity). Evolve the map iteratively.

## Key Concepts
- **Persona**: a specific, named representation of the user archetype who benefits from the feature, including role and relevant context.
- **Action**: what the user wants to do, written in active voice — describing intent, not implementation.
- **Goal**: the measurable value/outcome the persona seeks, expressed in the "so that" clause.
- **Acceptance criteria**: testable, measurable conditions defining story completion; also the basis for QA and prioritization.
- **Negative case**: an acceptance scenario for invalid input or error conditions (e.g., invalid/unverified email on password reset).
- **Edge case**: an acceptance scenario for uncommon-but-valid boundary conditions (e.g., weak password, rapid repeated resets).
- **Independent story**: a story that stands alone with no dependency on other stories, so it can be prioritized and built in any order.
- **Conversation starter**: the role of a story as the seed of a dialogue with users, not a detailed spec.
- **Non-functional requirement**: a system characteristic (performance, security, scalability) not tied to a single user need but essential to success.
- **Assumption mapping/validation**: explicitly documenting the assumptions behind stories, then testing them via research, feedback loops, and iterative testing.

## Mental Models
- Think of a user story as a **conversation starter**, not a contract — its value is the discussion and feedback it triggers, refined over time.
- Use **"what, not how"** as the test for every story: if it dictates implementation, you've over-specified and stolen the dev team's design decisions.
- Treat a too-broad story as a **splitting signal**: "I want a search function" should break into search-by-name, filter results, suggested terms, save results — each independent.
- Use **job stories when motivation and context matter more than the feature** — they surface the emotional/contextual "why" that traditional requirement-gathering misses.

## Anti-patterns
- **Focusing on implementation details**: prescribes *how* and removes the dev team's design latitude; stories should state *what* the user wants.
- **Too broad or too narrow**: broad stories lack context and hide dependencies; narrow ones are over-prescriptive. Scope to one specific need.
- **Failing to capture acceptance criteria**: leaves "done" undefined, causing misunderstandings between team and stakeholders.
- **Not involving the right stakeholders / writing in isolation**: produces incomplete or misaligned stories detached from product goals; include users, customers, SMEs.
- **Forgetting non-functional requirements**: ignoring performance/security/scalability can sink an otherwise-correct feature.
- **Vague or ambiguous language**: causes misinterpretation, rework, delays — define terminology, use concrete examples.
- **Failing to prioritize**: wastes time/resources; rank each story by user importance and value.
- **Failing to revisit stories**: needs change; stale stories drift from reality — refine them during backlog refinement.

## Worked Example
**Password-reset story with negative and edge acceptance criteria.**

Story: *"As a user, I want to reset my password so that I can regain access to my account."*

Negative-case acceptance criteria:
- Invalid email format entered → show "email address is invalid" error.
- Email not tied to any account → show "no account found with the provided email."
- Email tied to an unverified account → instruct user to verify email before resetting.
- Account locked from failed logins → tell user to contact support.

Edge-case acceptance criteria:
- New password fails minimum complexity (length, special chars) → show the specific requirements.
- Multiple reset attempts in a short window → apply a temporary lockout to prevent abuse.
- Successful reset → redirect to login page with a success confirmation message.

This shows how criteria force coverage of error and boundary paths a happy-path story would silently omit.

## Key Takeaways
1. Build every story from persona + action + goal, and write it as `As a [user], I want [goal], so that [reason]`.
2. State *what* the user wants, never *how* to build it — leave implementation to the dev team.
3. Attach specific, measurable, testable acceptance criteria, and always include negative and edge cases.
4. Keep stories independent and single-purpose; split anything too broad into smaller standalone stories.
5. Don't include non-functional requirements by accident of omission — name performance, security, and scalability where they apply.
6. Use job stories (`When… I want to… so I can…`) to capture motivation/context that feature-focused stories miss.
7. Use story mapping (journey × priority) to see the whole product, sequence delivery, and find the MVP.

## Connects To
- **Ch 1/2**: builds on what user stories are and their role in Agile, turning the concept into concrete writing technique.
- **Ch 4**: ends pointing forward to prioritizing and estimating user stories (only briefly touched here via "prioritize by value").
- **Acceptance criteria → testing**: the testable criteria here become the basis for QA and acceptance testing downstream.
