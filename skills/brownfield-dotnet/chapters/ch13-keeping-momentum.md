# Chapter 13: Keeping the Momentum

## Core Idea
The technical fixes in this book only stick if the team sustains them; without a deliberate, long-term effort to change culture and expectations, a brownfield project quickly reverts to its old, contaminated self. Keep momentum through small, continuous nudges rather than dramatic one-shot cleanups.

## Frameworks Introduced
- **Nudge the Beast (incremental course correction)**: A brownfield project is a three-ton beast barrelling downhill with built-up momentum. You can't stop it with a roadblock (a rewrite or a big-bang change) — it crashes through and reverts. Instead, apply many small pushes toward a clear end goal so it arrives where you want.
  - When to use: any time you want to redirect an established codebase or process away from its current trajectory.
  - How: define the desired end state explicitly (not a vague "make it better"); pick the next single incremental change; apply it; re-aim; repeat. Each "nudge" is one of the incremental change techniques used throughout the book.

- **Set Expectations for the Long Haul**: Sustaining a brownfield effort requires a dedicated, directed, long-term commitment from everyone — developers, project manager, and client — not a New Year's-resolution promise.
  - When to use: at project start and continually, before promising maintainability improvements.
  - How: communicate that improvements have a great improvement/effort ratio but take time to implement and to show benefit; manage hopes so a perceived "failure" doesn't poison morale and all future brownfield work; deliver consistent, timely results to build a track record that earns leeway.

- **Set the Pace (velocity-aware adoption)**: Evaluate the team's real velocity and underlying capabilities, then take on only what it can absorb. Each book topic is a stand-alone concept layered on the previous one.
  - When to use: when sequencing which improvements to introduce and when.
  - How: assess current velocity honestly (steady pace? bugs breeding bugs? research time available?); adopt one concept at a time in a foundational order — version control → continuous integration → ecosystem → layering → UI/data-access refactoring — confirming the team is comfortable before adding the next.

- **Periodic Progress Review**: Informal, timeboxed round-table to keep the team comfortable and on track.
  - When to use: at regular intervals throughout the project.
  - How: discuss architecture shifts since last meeting and what's planned next; surface successes, failures, concerns, and mentoring needs; review tracked code metrics (from Ch 5) to target problem areas or validate that practices are paying off; rely on gut feeling, say what's bothering you, timebox it, and follow up on parked issues.

- **Culture of Quality / Continuous-Improvement Pact**: From this day forward the team commits to three things — add maintainable new code, make any old code you touch maintainable, and eliminate pain and friction in your processes.
  - When to use: instead of a "spring cleaning" iteration; as the ongoing default working mode.
  - How: keep delivering features and bug fixes, but treat every pain point as a signal to stop, find the cause, and remove it. Refuse to tolerate defective code (extends Ch 6's culture of quality).

## Key Concepts
- **Reversion / re-contamination**: Without conscientious effort, a brownfield app slides back to its old self — deadlines, cut corners, last-minute requirement changes, and lapsed habits undo the gains.
- **Refactoring binge**: One "small" refactoring cascades into re-architecting the app just to populate a listbox, leaving the project unreleasable.
- **Inconsistent mess**: Doing too much too fast yields half-done CI, ignored tests, DI in some places not others — worse than the original uniform mess.
- **Velocity**: How much solid work the team can do under normal conditions; must be measured before committing to change.
- **Spring cleaning iteration**: A dedicated all-refactoring iteration with no features or bug fixes — the authors argue against it.
- **Hallway conversation / talking it out**: Solutions surface by explaining a problem aloud to a teammate; informal daily face-to-face communication keeps momentum flowing.
- **The pact**: A team agreement not to stand for code or process that causes pain or friction.
- **Challenge Your Assumptions**: Look past your own community (.NET, Java, COBOL) and paradigm (OO, procedural, functional) for better ideas — many in this book trace to Smalltalk and Java.

## Mental Models
- Use **nudges, not roadblocks**, when redirecting a project with momentum — big-bang stops get crashed through; steady small corrections compound.
- Use **slow and steady** (Aesop) when introducing change, especially early — make the whole team comfortable before adding the next change.
- Use **pair programming / collaboration to "make time"** when you feel too busy to improve — two people on two problems sequentially often beat two people working separately, and the code comes out cleaner.
- Use **"there's rarely nothing you can do now"** when full refactoring isn't feasible — extract a responsibility from a monster method even if you can't yet add an IoC container.

## Anti-patterns
- **Spring-cleaning iteration**: Naïve (you can't fix brownfield in one iteration), insulting to the client (admits no work can proceed until cleanup), and it removes the day-to-day contact that reveals what actually hurts.
- **Too much, too fast**: Crippling the project by piling on changes faster than the team can absorb, producing an inconsistent mess.
- **Complacency / "I've got a little OO knowledge now" license**: "I know where to fix this, I don't need a test" or "I'll just add a comment and move on" — sliding back into old habits.
- **Latching onto the newest framework** without the team's cycles or core knowledge to maintain it — leaves sections of the app looking wildly different.
- **Unrealistic promises to the client**: Over-promising maintainability and under-delivering dooms not just this project but all future brownfield projects.
- **Tolerating an uncommitted teammate**: Someone working with the code daily who won't commit to improving it is itself a pain point to remove.

## Reference Tables

### Recommended Tools (from the closing appendix "Our .NET Toolbox")
| Category | Tools |
| --- | --- |
| Automated Testing | nUnit, MbUnit, RhinoMocks, Moq, SqlLite |
| CI / Automated Builds | CruiseControl.Net, Team City, nAnt, nAnt Contrib |
| Metric Generation | nCover, nDepend, Simian |
| Data Access | nHibernate, Fluent nHibernate, IglooCoder Commons WcfNhibernate, NH Prof, AutoMapper |
| IoC / DI | Castle Windsor, Structure Map, Autofac |
| User Interface | Castle MonoRail MVC, ASP.NET MVC |

*Additional appendix categories:* Productivity (ReSharper, CodeRush, TestDriven.Net); Aspect-Oriented Programming (Castle Windsor, PostSharp); Logging (log4net); Source Control (VisualSVN Server, TortoiseSVN, AhnkSVN, VisualSVN, KDiff3); Code Profiling and Diagnosis (dotTrace, ANTS Profiler, Fiddler2). The authors note duplicate solutions (e.g. CruiseControl.Net vs Team City) aren't differentiated: "we will work with either, but never neither."

## Worked Example
A momentum-keeping checklist the team can adopt without a special iteration:
1. Pick a clear end goal for the codebase — not "add unit tests," but a concrete target state.
2. Measure current velocity honestly before committing to any change.
3. Introduce improvements one layer at a time (VCS → CI → ecosystem → layering → UI/data), confirming comfort before advancing.
4. On every task, follow the pact: new code maintainable, touched old code made better, pain points hunted down and removed.
5. When a refactor is too big for now, do the small version (extract a method/class) and leave the codebase better than you found it — never forge ahead by rote.
6. Hold short daily stand-ups and harness hallway conversations; pair when stuck.
7. Run timeboxed periodic progress reviews; review code metrics; follow up on parked issues.
8. Resist the "spring cleaning" urge and the refactoring binge alike.

## Key Takeaways
1. The hardest pain point is reversion — a brownfield app reverts fast unless the team actively, continuously fights it.
2. Redirect with steady incremental nudges toward an explicit goal, never a big-bang roadblock.
3. Manage expectations up the whole chain; a "failed" brownfield project devastates morale and poisons future efforts.
4. Match the pace of change to the team's real velocity and capability — too much too fast leaves an inconsistent mess.
5. Reject the dedicated "spring cleaning" iteration; instead bake quality into continuous, day-to-day work via the three-part pact.
6. Make time by collaborating, pairing, and talking problems out — and remember there's almost always a small improvement you can make right now.
7. Address dissenters honestly: remove an uncommitted developer; be diplomatic with a skeptical client/PM and win them with a track record — or "change your environment, or change your environment."

## Connects To
- **Ch 1**: closes the loop on being an agent for change — returns to the "softer side" (morale, pain, stakeholders) that opened the book and ties the whole journey together.
- **Ch 5**: progress reviews are the venue for revisiting code metrics to target problem areas and confirm payoff.
- **Ch 6**: extends the "culture of quality" used to fight the defect backlog into the team's permanent operating mode.
- **External**: Fowler's *Refactoring* and Feathers' *Working Effectively with Legacy Code* for quick, high-value refactorings that set the stage for later work.
