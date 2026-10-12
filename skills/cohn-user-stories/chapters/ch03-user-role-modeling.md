# Chapter 3: User Role Modeling

## Core Idea
Writing all stories from the perspective of a single generic "user" is a fallacy that ignores whole classes of users; identifying **user roles** (and, for a few, **personas**) before writing stories produces more complete stories and better software.

## Frameworks Introduced
- **User Role Modeling (Constantine & Lockwood)** — four steps:
  - When to use: at project start, before story-writing; even when you have on-site users.
  - How:
    1. **Brainstorm** an initial set — customer + as many developers as possible, each writes role-name cards and places them on a wall, calling out the name only, no discussion/evaluation (~15 min).
    2. **Organize** — physically position cards so overlap of cards mirrors overlap of roles; stack generic roles above their specializations.
    3. **Consolidate** — for heavily overlapping cards, authors explain intent; merge equivalents or rip up duplicates; also rip up roles unimportant to project success.
    4. **Refine** — add **role attributes** (notes) that distinguish roles.
  - Why it works: an hour of this puts more thought into users than 99% of teams; failure mode is over-investing — it's a tool, don't let it become the goal.
- **Personas (Alan Cooper / interaction design)**: an imaginary, named representation of a user role.
  - When to use: only for one or two *vital* user roles where satisfying them is essential.
  - How: give a name, a rich backstory, and a *photograph* so the whole team "knows" them; hang on a wall (too long for a card). Requires real market/demographic research to be valid.
- **Extreme Characters (Djajadiningrat et al.)**: design for exaggerated personalities (e.g., a drug dealer, the Pope, someone juggling boyfriends) to surface stories you'd otherwise miss.

## Key Concepts
- **User role**: a collection of defining attributes characterizing a population of users and their intended interactions with the system.
- **Role attribute**: a useful fact about the users in a role (frequency of use, domain expertise, computer proficiency, proficiency with this software, general goal) that distinguishes one role from another.
- **Role card**: a note card holding a role name plus its attribute notes.
- **User role map**: the spatial layout of role cards showing relationships/overlap.
- **Persona**: an imaginary, fleshed-out, named-and-pictured representation of an important role.
- **A role is one user**: model roles as individuals, not organizations ("a company can post a job" → a Recruiter posts a job).
- **System roles**: prefer human roles; add a non-human/system role only if it clearly helps and could make or break success.

## Mental Models
- Think of roles as **aggregating real individuals** — Scott, Laura, Kindra, Allan all collapse into Job Seeker / First Timer / Layoff Victim / Geographic Searcher with subtly different goals.
- Use **card overlap as a similarity dial**: overlap cards a lot when roles overlap a lot, slightly when slightly.
- Rip up a role when its stories would be **identical to another's** (College Grad ≈ First Timer) or when the role can't make-or-break the system (the Monitor).
- Write stories **in role terms** ("A Geographic Searcher can restrict searches to a region") to keep a concrete user in mind — without excluding other roles.

## Worked Example
BigMoneyJobs brainstorm → consolidate:

Initial roles: Job Seeker (Scott), First Timer (Laura), College Grad, Layoff Victim (Kindra), Geographic Searcher (Allan), Monitor (Ashish), Job Poster (Mario), Resume Reader (Delaney), Recruiter (Savannah).

Consolidation decisions:
- College Grad ≈ First Timer → rip up College Grad.
- Job Poster + Resume Reader → covered by **Recruiter**; rip up the two, then specialize Recruiter into **Internal Recruiter** and **External Recruiter**.
- Monitor unimportant to success → rip up; focus on Job Seeker and Recruiter roles.

Sample refined role card:
> **User Role: Internal Recruiter** — Not particularly computer-savvy but adept on the Web. Uses the software infrequently but intensely. Reads other companies' ads to word her own. Ease of use matters, but what she learns must be easily recalled months later.

## Key Takeaways
1. Never write all stories from one generic user; brainstorm a full set of roles first.
2. Run the four steps — brainstorm, organize, consolidate, refine — in roughly an hour; most teams should stop after refining.
3. Consolidate aggressively: merge equivalents, delete duplicates, and drop roles that can't affect project success.
4. Add role attributes (frequency, expertise, goals) to make differences between roles actionable.
5. Promote only one or two critical roles to full personas (name + backstory + photo); back personas with real research.
6. Use extreme characters sparingly as a creativity probe, knowing the stories they yield may or may not belong in the product.
7. Do role modeling even with on-site users — having users doesn't guarantee the right mix.

## Connects To
- **Ch 1–2**: roles give stories a concrete subject; "a company can..." becomes a one-user role.
- **Ch 4 (Gathering Stories)**: low-fidelity prototyping walks the system from each role's main screen.
- **Ch 5 (User Proxies)**: roles clarify which users a proxy is (or isn't) representing.
- **Usage-centered design / Interaction design**: Constantine & Lockwood, Cooper — the source disciplines.
