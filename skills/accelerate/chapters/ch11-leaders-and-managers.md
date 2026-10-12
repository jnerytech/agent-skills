# Chapter 11: Leaders and Managers
*Authors: Nicole Forsgren, Jez Humble, Gene Kim*

## Core Idea
Transformational leadership is highly correlated with software delivery performance and eNPS. Its effect is **indirect**: it enables the technical, architectural, and Lean practices that drive performance. Leaders amplify teams but cannot get high outcomes alone. Managers add value by investing in people, building trust across teams, building a climate for learning, and enabling good tools.

## Frameworks Introduced
- **Transformational leadership: five dimensions (Rafferty and Griffin 2004)**:
  1. **Vision**: has a clear understanding of where the organization is going and where it should be in five years.
  2. **Inspirational communication**: communicates in a way that inspires and motivates, even in an uncertain or changing environment.
  3. **Intellectual stimulation**: challenges followers to think about problems in new ways.
  4. **Supportive leadership**: shows care and consideration for followers' personal needs and feelings.
  5. **Personal recognition**: praises and acknowledges goal achievement and improvements in work quality, and personally compliments outstanding work.
  - When to use: use it to assess and develop leaders (with or without direct reports) during a technology transformation.
  - How: survey team members with the 15 items (3 per dimension) on a Likert-type scale and average them per dimension. Develop the weakest dimensions.
  - Why it works / failure mode: transformational leaders get followers to *identify with the organization* and engage in its objectives, which amplifies existing practices. The failure mode is expecting leadership alone to deliver. Teams in the **top 10%** of transformational leadership were *equally or even less likely* to be high performers than the overall population. Leaders need teams executing on a suitable architecture with good technical and Lean practices.
- **Transformational vs. servant leadership**: the two are similar but differ in focus. Servant leaders focus on followers' development and performance. Transformational leaders focus on getting followers to identify with the organization and support its objectives. Transformational leadership was chosen because it is more predictive of performance outcomes in other contexts.
- **Three levers for team culture**: cross-functional collaboration, a climate for learning, and tools. All three are highly correlated with software delivery performance.
  - When to use: use them as a manager's, team lead's, or engaged practitioner's playbook for culture.
  - How: see the tactics under each lever in Reference Tables.
- **Ways to invest in DevOps and teams**: a manager's investment menu (see Reference Tables). Investment in DevOps is highly correlated with software delivery performance.

## Key Concepts
- **Leadership vs. management**: leadership means inspiring and motivating, and doesn't require reports on an org chart. Managers hold responsibility for people, budgets, and resources, and in the best case are also transformational leaders.
- **Indirect effect of leadership**: leadership affects organizational and noncommercial goals *through* the technical and Lean practices it supports.
- **Air cover**: leaders' authority and budget protect a transformation and let them change the incentives of whole groups (dev, QA, ops, infosec).
- **Bottom-third leadership effect**: teams with leadership in the bottom one-third of strength are **only half as likely** to be high performers.
- **Manager's linking role**: connecting the strategic objectives of the business to the team's work.
- **Delegating authority**: "Knowledge is power, and you should give power to those who have the knowledge."
- **Yak days**: internal events where teams work on technical debt, which is rarely prioritized otherwise.
- **Game days / DiRT**: disaster recovery testing exercises with simulated or real outages. They force cross-group collaboration and build relationships before a real disaster.
- **Blameless postmortems**: treat failure as a learning opportunity so people take (reasonable) risks.

## Mental Models
- Think of leadership as an amplifier, not a source. It multiplies the effect of CD, architecture, and Lean practices. With no practices underneath, there is nothing to amplify.
- Use leadership support to make grassroots success easier. Grassroots DevOps stories exist, but success is far easier with leaders.
- Think of trust between teams as built from kept promises, open communication, and predictable behavior under stress, accumulated over time.
- Use tool choice as both a satisfaction lever and a delivery lever. Let teams choose unless there's a good reason not to.

## Anti-patterns
- **Maligning leadership**: the DevOps community sometimes paints middle managers as obstacles, while leader buy-in is exactly what transformations need.
- **Hero leader, weak practices**: top-10% leaders without technical and Lean capabilities don't yield high performers.
- **Punishing failure**: people stop trying new things, and innovation dies.
- **Procurement-driven tool standardization**: if you must standardize, procurement and finance should act in teams' interests, "not the other way around".
- **Invisible metrics**: managers should make performance metrics visible and aligned with organizational goals.
- **Hidden training budget**: a budget nobody knows about doesn't create a learning climate.

## Code Examples
```
Transformational leadership survey items (adapted from Rafferty and Griffin 2004)
"My leader or manager..."
(Vision)
  - Has a clear understanding of where we are going.
  - Has a clear sense of where he/she wants our team to be in five years.
  - Has a clear idea of where the organization is going.
(Inspirational communication)
  - Says things that make employees proud to be a part of this organization.
  - Says positive things about the work unit.
  - Encourages people to see changing environments as situations full of opportunities.
(Intellectual stimulation)
  - Challenges me to think about old problems in new ways.
  - Has ideas that have forced me to rethink some things that I have never questioned before.
  - Has challenged me to rethink some of my basic assumptions about my work.
(Supportive leadership)
  - Considers my personal feelings before acting.
  - Behaves in a manner which is thoughtful of my personal needs.
  - Sees that the interests of employees are given due consideration.
(Personal recognition)
  - Commends me when I do a better than average job.
  - Acknowledges improvement in my quality of work.
  - Personally compliments me when I do outstanding work.
```
What it demonstrates: a validated 5-dimension × 3-item latent construct (see Ch 13 and Appendix C) that you can reuse to measure leadership in your own teams.

## Reference Tables
**Research findings**
| Finding | Result |
|---|---|
| Leadership dimensions across high/medium/low performers | High performers had the strongest behaviors on all five dimensions and low performers the lowest, all statistically significant. |
| Bottom one-third of leadership strength | **Only half as likely** to be high performers |
| Top 10% of transformational leadership | **Equally or even less likely** to be high performers than the whole population |
| Transformational leadership and eNPS | Highly correlated |
| Investment in DevOps and software delivery performance | Highly correlated |
| Gartner prediction | By 2020, half of CIOs who haven't transformed their teams' capabilities will be displaced from digital leadership teams |

**Transformational leadership is essential for:**
- Establishing and supporting generative, high-trust cultural norms.
- Creating technologies that enable developer productivity, reduce code deployment lead times, and support more reliable infrastructure.
- Supporting team experimentation and innovation, and building better products faster.
- Working across organizational silos to achieve strategic alignment.

**Ways to invest in DevOps and your teams**
- Make existing resources available and accessible to everyone, and create space for learning.
- Set a dedicated training budget, publicize it, and let staff choose their training (it can include dedicated time during the day).
- Have staff attend a technical conference at least once a year and summarize it for the team.
- Run internal hack days with cross-functional teams.
- Run internal "yak days" for technical debt.
- Hold regular internal DevOps mini-conferences (DevOpsDays format: prepared talks plus open spaces).
- Give dedicated experimentation time (e.g., 20% time, or several days after a release), plus budget and infrastructure for special projects.

**Culture levers: tactics**
| Cross-functional collaboration | Climate for learning | Tools |
|---|---|---|
| Build trust with counterparts on other teams; this is the most important thing you can do | Create a training budget and advocate for it internally | Let teams choose their own tools (a predictor of CD and of job satisfaction) |
| Encourage practitioners to move between departments (lateral moves) | Give resources and space for informal learning (3M 15%, Google 20%) | Make monitoring a priority (proactive monitoring relates to performance and job satisfaction) |
| Actively seek, encourage, and reward collaboration work, and make success reproducible | Make it safe to fail with blameless postmortems | |
| Use disaster recovery testing (game days) to build relationships | Create spaces to share information (lightning talks, lunch-and-learns) | |
| | Hold demo days and forums | |

## Worked Example
**Google DiRT as a relationship builder.** Kripa Krishnan, Director of Cloud Operations at Google, runs DiRT (disaster recovery testing) exercises. Outages are simulated or actually created according to a pre-prepared plan, and teams must work together to keep or restore service levels.
1. Precondition: the organization must first accept system and process failures as a means of learning.
2. The tests are deliberately designed so that engineers from several groups who don't normally work together must interact.
3. Result: if a real large-scale disaster strikes, those people already have strong working relationships. The exercise tests systems and also builds cross-functional trust, the first culture lever.

## Key Takeaways
1. Assess leaders on the five dimensions with the 15-item survey and target the weakest dimension.
2. Never fund leadership in place of practices. Pair leadership development with CD, architecture, and Lean capabilities, because leadership works only through them.
3. As a manager, make deployments less painful, make performance metrics visible and aligned with goals, and delegate authority to those with the knowledge.
4. Fund learning visibly: a training budget, conference attendance, hack days and yak days, and 20% time.
5. Build cross-team trust deliberately: kept promises, lateral moves, and game days.
6. Let teams choose their tools and prioritize proactive monitoring.

## Connects To
- **Ch 3**: transformational leaders build and support generative (Westrum) cultures.
- **Ch 4 / Ch 5 / Ch 7 / Ch 8**: the technical, architectural, Lean management, and product practices that leadership enables (Figure 11.1). Ch 5 covers teams choosing their own tools.
- **Ch 10**: leadership correlates with eNPS, and tools and resources drive job satisfaction.
- **Ch 13 / Appendix C**: validation of the leadership items as a latent construct.
- **Ch 16**: a high-performance leadership and management case (ING).
- **External: Servant leadership**: contrasted with transformational leadership by its focus on follower development.
