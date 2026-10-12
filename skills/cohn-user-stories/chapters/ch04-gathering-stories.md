# Chapter 4: Gathering Stories

## Core Idea
Requirements are not "out there" to be elicited or captured; they are **trawled** — actively and repeatedly fished for over the life of the project — using a combination of lightweight techniques and, above all, the right kinds of questions.

## Frameworks Introduced
- **Trawling for requirements (Robertson & Robertson)**: the governing metaphor replacing "elicitation"/"capture."
  - When to use: as the mindset for all requirements work on an agile project.
  - How: make passes with different "mesh" sizes — a coarse net for big requirements first, finer nets later for medium and small ones; revisit continuously because stories mature, change importance, and die.
  - Why it works: it correctly models that requirements differ in size, change over time, are never all caught, and that *skill* determines where you look. Failure mode: the prescriptive opposite — trying to write every requirement perfectly up front.
- **Four trawling techniques**: User interviews, Questionnaires, Observation, Story-writing workshops.
  - When to use each: interviews = default, pick interviewees across roles; questionnaires = prioritize/gather info on *existing* stories from a large population (not for finding new stories); observation = rich insight, but rare outside in-house software; workshops = the most effective way to rapidly generate many stories.
  - How (workshop): combine brainstorming with **low-fidelity prototyping**; hold at least one before each release.
- **Open-ended + context-free questions**: ask questions with no implied answer and room for in-depth response.
  - How: replace closed/leading questions ("Would you like it in a browser?", "How fast do searches need to be?") with open, context-free ones ("What would you give up to have it in a browser?", "What kind of performance is required?").

## Key Concepts
- **Trawling**: ongoing, skill-dependent gathering of requirements that change over time.
- **Low-fidelity prototype**: a paper/whiteboard map of high-level conceptual workflows (boxes = components, arrows = links) — *not* screens and fields like JAD/traditional prototyping; throw it away within days.
- **Closed-ended question**: yields only yes/no, often with an assumed answer; weak for discovery.
- **Open-ended question**: invites in-depth opinion; where the user goes (and doesn't) is itself the signal.
- **Context-free question**: contains no implied answer or preference.
- **Parking lot**: a visible list of issues raised mid-workshop to revisit later.
- **Depth-first prototyping**: detail one component, follow its link to the next, and so on — easier to track than breadth-first.

## Mental Models
- Think requirements like **fish, not caged objects**: you won't catch them all, sizes vary, and some mature or die between iterations.
- "**You built exactly what I asked for but it's not what I want**" — users have the problem but aren't necessarily qualified to design the solution (e.g., the text mini-language replaced by a drag-and-drop survey tool).
- Use observation to find the **real need behind the stated need** — nurses asked for a big text field; observation revealed they needed the *system to track decisions* (searches/recommendations logged).
- In workshops, optimize for **quantity over quality**: write it down, don't debate, rip up redundant cards later.

## Worked Example
BigMoneyJobs low-fidelity prototype: start with an empty box = the main screen, pick a role/persona, ask "what can this role do from here?" For each action draw a line to a new labeled box and write a story. Resulting stories:
- A Job Seeker can post her resume.
- An Employer can post jobs.
- An Employer can review submitted resumes.
- A Job Seeker can search for jobs.
- A Job Seeker can view results of jobs that match a search.
- A Job Seeker can view details about specific jobs.

Prompting questions while walking the prototype: What will the user most likely do next? What mistakes could they make here? What could confuse them? What more info do they need? — answers shift by role.

Browser question, fixed: closed/leading "Would you like our new app in a browser?" → open, context-free "What would you be willing to give up to have our next-generation product run in a browser?"

## Key Takeaways
1. Drop "elicit/capture"; adopt trawling — gather continuously, accepting stories emerge and change.
2. Don't write all stories up front, but do look ahead ~one release and write the stories you can, in decreasing detail with the time horizon.
3. Use a *combination* of techniques; don't over-rely on any one.
4. Favor story-writing workshops with low-fidelity prototyping for fast, high-volume story generation.
5. Ask open-ended, context-free questions; move to specific questions only after.
6. Observe real users whenever you can — it exposes needs hidden by users' own descriptions.
7. Use questionnaires only to prioritize/learn about existing stories at scale, never as the primary discovery tool.
8. Throw the prototype away within days; keep a parking lot for tangents.

## Connects To
- **Ch 3 (User Role Modeling)**: prototyping and interviewing are driven per role/persona.
- **Ch 5 (User Proxies)**: who to interview when real users are unavailable.
- **Ch 1–2**: workshops feed the initial story set that is then estimated, sized, and split.
- **JAD / traditional prototyping**: explicitly contrasted — lo-fi maps workflows, not screens.
