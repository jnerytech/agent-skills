# Chapter 1: Understanding Your Audience

## Core Idea
Good docs start with empathy: break the **curse of knowledge** by researching who your users are, what they need (not just what they want), and where they hit friction — before writing a word.

## Frameworks Introduced
- **The Curse of Knowledge**: the cognitive bias that you assume others know what you know. Demonstrated by the "tappers vs. listeners" experiment (tappers predicted 51% would guess the song; only 2.5% did).
  - When to use: the lens for everything in the book — recognize that you (the expert) cannot judge what a beginner needs.
  - How: deliberately surface jargon, missing endpoints, terse errors you'd skip; validate against real users.
- **Needs vs. Wants**: document what users *need*, not what they *want*. "They want the sports car; they need the bus ticket."
  - How: in interviews, dig past stated desires to the underlying task.
- **User Persona**: a semi-fictional character (real or amalgam) with goals, skills, knowledge, situation.
  - How: list essential characteristics from research; pick the persona to focus on (usually the larger, less-expert group — "Charles" the junior dev over "Mei" the advanced lead).
- **User Story**: `As a [type of user], I want [activity] so that I can [goal].` Keeps higher-level motivation front of mind.
- **User Journey Map**: timeline diagram of the path a user takes across channels, with what they do/feel at each step.
  - How: (1) define task, (2) list channels, (3) piece together steps, (4) note experience per step, (5) connect into a flow.
- **Friction Log**: a journal where you use your own software as a user would, logging expected vs. actual behavior step by step. The bigger the gap, the bigger the opportunity.
  - How: tight scope, one user + one scenario with clear start/end; numbered steps; color-code positive/negative; convert product bugs into issues, doc gaps into writing.

## Key Concepts
- **User research**: interviews, surveys, and reviewing existing data to confirm/reject assumptions about users.
- **Open vs. closed question**: open = exploratory ("What's your experience with translation software?"); closed = yes/no. Use open for interviews, closed for surveys.
- **Existing data sources**: dev relations, support, UX, marketing teams; **support tickets** are a "gold mine."
- **User goal vs. business goal**: your goal (onboard users) differs from theirs (translate barks); a good doc set aligns both.

## Mental Models
- Think of every doc decision as "what does someone *without* my context need here?"
- Prefer **quality over quantity** in research: 3–5 well-fit participants beat 50 ill-fit ones.
- A persona is a focusing lens, not a deliverable — pick who you must help *most*.

## Anti-patterns
- **"The code is self-explanatory, skip the docs"**: the rationalizations that delay docs until launch pain hits.
- **Researching wants instead of needs**: builds docs nobody can act on.
- **Sprawling friction logs**: no clear scope → unactionable.

## Reference Tables
Grouping support issues by theme (Table 1-1):

| Issue | Example |
|---|---|
| topic | Users confused by an endpoint's name |
| process | 80% of users had issues authenticating |
| type of user | Recently-started devs more likely to request help |
| action | Rewriting an error message helped 4/5 users |

## Worked Example
**Corg.ly friction log (sign up for a paid account):**
1. Opened website. 2. Navigated to sign-up form — had to scroll to bottom, hard to find (move to top?). 3. Completed form, entered card. 4. Clicked submit — *no confirmation, no error*. 5. Noticed blank fields — did they block submit? 6. Filled blanks. 7. Resubmitted — got confirmation.

The gaps (no submit feedback, hidden form) are concrete doc/product fixes the log surfaces that the expert never noticed.

## Key Takeaways
1. Empathy is the prerequisite for good docs — the curse of knowledge is always working against you.
2. Define the user *goal* and write it down; you'll measure docs against it later (Ch 9).
3. Validate assumptions by talking to 3–5 real users; mine support tickets first.
4. Condense findings into durable artifacts: personas, stories, journey maps.
5. Run a tightly-scoped friction log to feel your users' pain firsthand.
6. Separate product bugs (file issues) from doc gaps (write docs).

## Connects To
- **Ch 2**: research → a documentation plan with content types.
- **Ch 9**: the goal you write down becomes the yardstick for measuring quality.
- **Agile/XP user stories**: same `As a… I want… so that…` format ([[cohn-user-stories]]).
