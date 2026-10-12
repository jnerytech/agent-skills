# Chapter 15: Postmortem Culture: Learning from Failure
*Authors: John Lunney and Sue Lueder (edited by Gary O'Connor)*

> "The cost of failure is education." (Devin Carraway)

## Core Idea
Incidents are inevitable at scale. Without a formal, **blameless** process for learning from them, they recur and can cascade. A postmortem is a written record of an incident: its impact, the mitigation and resolution actions, the root cause(s), and follow-up actions to prevent recurrence. It works only when the culture makes writing one a reward, not a punishment.

## Frameworks Introduced
- **Postmortem triggers (defined in advance)**: objective criteria, agreed before any incident, for when a postmortem is required.
  - When to use: set them when you onboard a service, so nobody argues about whether one is needed after an outage.
  - How: the common triggers are:
    1. User-visible downtime or degradation beyond a threshold
    2. Data loss of any kind
    3. On-call engineer intervention (rollback, traffic rerouting, etc.)
    4. Resolution time above a threshold
    5. A monitoring failure (which usually means a human discovered the incident)
    - Any stakeholder may also request a postmortem for any event.
  - Why it works: postmortems cost time, so fixed criteria spend that effort deliberately and stop people from skipping them when it suits them.
- **Blameless postmortem**: focus on the contributing causes without indicting any individual or team. Assume everyone "had good intentions and did the right thing with the information they had."
  - When to use: every postmortem, with no exceptions.
  - How: ask why the person had incomplete or incorrect information, not who erred. Fix systems and processes, because "you can't 'fix' people." Still call out clearly where services can improve. Constructive is not the same as vague.
  - Why it works / failure mode: if blame prevails, people hide issues for fear of punishment, and incidents get "swept under the rug," which raises organizational risk. The idea comes from healthcare and avionics, where every mistake is a chance to strengthen the system. Don't stigmatize a person or team for producing many postmortems.
- **Collaborative postmortem tooling**: the key features to look for in a tool (Google uses Google Docs with the Appendix D template):
  - Real-time collaboration, for fast collection of data and ideas early on
  - An open commenting/annotation system, to crowdsource solutions
  - Email notifications, to loop in collaborators
- **Postmortem review criteria**: senior engineers review the first draft for completeness:
  1. Was key incident data collected for posterity?
  2. Are the impact assessments complete?
  3. Was the root cause sufficiently deep?
  4. Is the action plan appropriate, and are the resulting bug fixes at an appropriate priority?
  5. Did we share the outcome with relevant stakeholders?
- **No Postmortem Left Unreviewed**: "An unreviewed postmortem might as well never have existed."
  - How: hold regular review sessions, close open discussions and comments, finalize the document, then add it to a team or org repository of past incidents. Etsy's *Morgue* is one such tool.
- **Cultural reinforcement activities**: Postmortem of the month (a newsletter), a postmortem discussion group, **postmortem reading clubs** (often on incidents months or years old, with refreshments), and the **Wheel of Misfortune** (new SREs reenact a past postmortem, with the original incident commander present).
- **Strategies for overcoming "postmortems cost too much"**:
  1. Ease postmortems into the workflow with a trial period of several complete, successful postmortems. This also tunes the triggers.
  2. Reward and celebrate effective postmortems, both socially and in performance management.
  3. Get senior leadership to acknowledge and participate.

## Key Concepts
- **Postmortem**: a written record of an incident's impact, mitigation and resolution, root cause(s), and preventive follow-up actions.
- **Blameless culture**: assumes good intent, targets systemic causes, and makes people confident they can escalate without fear.
- **Root-cause analysis**: teams choose whichever RCA technique suits their service. Any technique is acceptable, but the cause must go "sufficiently deep."
- **Action items**: preventive fixes, filed at an appropriate priority. They are the main payoff of a postmortem.
- **Incident repository**: a searchable store of past postmortems that makes trend analysis and learning across teams possible.
- **Peer bonus**: Google's token cash recognition from peers, used to reward good incident handling.
- **"Postmortems at Google" working group**: coordinates templates across the company, automates postmortem creation from incident tooling, and extracts data for trend analysis.
- **PII exclusion**: postmortems, even internal ones, never contain information that could identify a user.

## Mental Models
- Think of a postmortem as an **investment in resilience**, not a formality. It is the company paying its "education" bill once instead of repeatedly.
- Use "**fix the system, not the person**" whenever a draft names a human as the cause. Rewrite it to ask why the system let that action happen, or why it didn't give that person the right information.
- Think of sharing as **widening the blast radius of the lesson**: share with the widest audience that would benefit.
- Use **objective triggers plus stakeholder request** as the rule. Triggers ensure coverage, and the request option catches anything the triggers miss.

## Anti-patterns
- **Finger-pointing**: for example, "if I get paged one more time I'll rewrite it myself." It vents frustration but drives problems underground.
- **Writing a postmortem as a formality**: the document gets filed and forgotten, and the action items never land.
- **Unreviewed postmortems**: without closure, the lessons and action items evaporate.
- **Stigmatizing frequent authors**: it punishes the teams that are most transparent.
- **Deciding the criteria after the incident**: it invites rationalized skipping.
- **Excessive postmortem toil**: survey teams on whether the process is too heavy (see Ch 5).

## Worked Example
**Blame versus blameless rewrite of the same complaint:**
- Pointing fingers: "We need to rewrite the entire complicated backend system! It's been breaking weekly for three quarters… if I get paged one more time I'll rewrite it myself."
- Blameless: "An action item to rewrite the backend might prevent these pages, and the maintenance manual for this version is long and hard to train up on. Future on-callers will thank us!"
Both versions want the same fix. The blameless one frames it as a systemic action item with a stated rationale, which is the cost of the training burden.

**TGIF "The Art of the Postmortem" (2014):** an SRE's release took down a critical service despite thorough testing, because of an unexpected interaction. He rolled back immediately, so the outage lasted only **four minutes**. He received **two peer bonuses** and applause in front of the founders and thousands of Googlers. The lesson is to visibly reward people for doing the right thing during and after an incident (see Ch 13).

## Key Takeaways
1. Define the postmortem triggers (downtime, data loss, on-call intervention, resolution time, monitoring failure) before incidents happen, and let any stakeholder request one.
2. Write every postmortem blamelessly. Target the information and system gaps that led good people astray.
3. Use collaborative tooling and a standard template (Appendix D), and have senior engineers review drafts against the five review criteria.
4. Never leave a postmortem unreviewed. Finalize it, then store it in a shared repository.
5. Cultivate the culture actively: reading clubs, postmortem of the month, Wheel of Misfortune, and public rewards for good incident handling.
6. Survey teams on how effective the process is and how much toil it creates, and invest in aggregation and metadata for cross-product trend analysis.

## Connects To
- **Ch 5 (Eliminating Toil)**: the postmortem process itself must not become toil.
- **Ch 13 (Emergency Response)**: has the full account of the four-minute outage praised at TGIF.
- **Ch 14 (Managing Incidents)**: incident management produces the raw record a postmortem formalizes.
- **Ch 16 (Tracking Outages)**: Outalator covers the frequent small-impact incidents that postmortems miss.
- **Ch 28 (Accelerating SREs to On-Call)**: Wheel of Misfortune / Disaster Role Playing, and postmortems as training material.
- **Appendix D**: the example postmortem template.
- **Just Culture (healthcare/aviation safety)**: the origin of blameless postmortems.
