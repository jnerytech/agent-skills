# Chapter 31: Communication and Collaboration in SRE
*Authors: Niall Murphy with Alex Rodriguez, Carl Crous, Dario Freni, Dylan Curley, Lorenzo Blanco, and Todd Underwood (edited by Betsy Beyer)*

## Core Idea
SRE is not a command-and-control organization. It serves "at least two masters" (its product dev partners and SRE as a whole) and is geographically distributed. So treat the team's communication like an **API**: design it carefully, because a wrong interface is painful to fix later. Use the weekly **production meeting** as the core feedback loop from operations to design.

## Frameworks Introduced
- **Communication as data flow / API-as-contract**: data about projects, service state, production and individuals must flow reliably between interested parties. The team's interface to other teams is like an API, so get its design right early. The same contract metaphor applies to collaboration among SRE teams and with product dev.
  - Corollary: putting someone in charge of reliability *without the full skill set* is not enough. SRE's promise relies on having the same skills as product dev.
- **Production meeting**: a weekly, *service-oriented* (not person-status) meeting, lasting 30–60 minutes, in which the SRE team articulates the state of its services so that everyone leaves with **the same idea** of what's going on. It also connects operational performance to design, configuration and implementation decisions.
  - When to use: every SRE team, every week.
  - How: rotate the chair. Make attendance compulsory for the SRE team and invite major stakeholders and product dev partners. Use a shared, well-known collaborative doc for a pre-populated, bottom-up agenda.
  - Why it works: regularly connecting service performance to design decisions is "an immensely powerful feedback loop". A rotating chair builds group ownership and trains chairing skills for incident coordination.
  - Failure mode: not inviting product dev partners. Then the operations feedback loop is broken and "a large part of the value of having an SRE team is lost". Fix the relationship, starting with one representative or a trusted intermediary.
- **Default production meeting agenda** (see Appendix F):
  1. *Upcoming production changes*: default to enabling change. Track start time, duration and expected effect (near-term horizon visibility).
  2. *Metrics*: core metrics (latency, CPU, resource use/efficiency) over time, to learn the system's performance envelope.
  3. *Outages*: postmortem-sized problems (Ch 15).
  4. *Paging events*: tactical list of pages. Ask: should it have paged the way it did? Should it have paged at all? If not, remove it.
  5. *Nonpaging events*: (a) should have paged but didn't, so fix monitoring; (b) not pageable but needs attention, so track it; (c) not pageable and no attention needed, so remove it.
  6. *Prior action items*: assign, track, deliver. Consistent delivery builds credibility.
- **Cross-site project recommendations** (from Viceroy):
  - Go cross-site only when you must. You trade higher latency and more communication for higher throughput.
  - Accept committed contributors with a specific goal, not those seeking a "notch on their belt".
  - Have strong project leaders for long-term vision and an agreed decision process. Allow local decisions where trust is high.
  - **Divide and conquer**: split the project into reasonably sized components, each owned by a small group, preferably at one site, with clear deliverables and deadlines. Don't let Conway's law distort the software too much.
  - Goals should be functionality- or problem-oriented. Work is done only when integrated and used.
  - Use design docs and reviews. Writing things down offsets distance.
  - **Standards**: argue debates fully but with a strict time limit, then pick, document and move on, using a respected arbitrator if needed.
  - In-person contact is irreplaceable. Hold team summits, at a neutral location when neutrality matters.
  - Scale project management to the project's current size.

## Key Concepts
- **Two masters**: SRE teams are accountable for their partner services but report through SRE.
- **Production meeting chair placement**: in video calls with imbalanced team sizes, put the chair on the smaller side, so the larger side quiets down.
- **Prefilled agenda**: a shared Google Doc agenda that is populated in parallel ahead of time.
- **Team charter**: a crisp definition of what a team will, and more importantly *won't*, support. It counters siloization.
- **Specialization trade-off**: specialization raises technical mastery but causes silos and ignorance of the bigger picture.
- **TL / SRM / TPM**: tech lead (technical direction), SRE manager (performance management plus catchall), project manager. Fluid roles adapt better but require more communication.
- **Email-address decay**: without in-person contact, even a great writer "decay[s] into just being an email address".
- **Singleton projects fail** unless the person is gifted or the problem is simple.
- **OKRs**: the process used to track early-design collaboration with product dev.

## Mental Models
- Think of **the team's interface as an API**: design it deliberately, because changes later are painful.
- Use the **production meeting** when you need to close the loop from operational pain to design change.
- Think of **diversity as a performance multiplier**: diverse teams are better teams, but they need explicit attention to communication and cognitive biases.
- Use **SRE for infrastructure, product dev for business logic** when splitting joint project work. Define the interface between them early so each side works independently.

## Anti-patterns
- **Person-status production meetings**: they should be service-oriented.
- **Meetings under 30 or over 60 minutes**: too short means something is cut short or the portfolio should grow. Too long means you're mired in detail, or you should shard the team or service set.
- **Change-stopping meetings**: Google defaults to enabling change while tracking it.
- **Keeping unactionable pages and noise alerts**: remove them.
- **Per-team reinvention when shared infra is a toolkit, not a product**: incentives that reward each team's own solution produce "smoldering, abandoned hulks" of duplicate frameworks.
- **Casual contributors with no maintenance commitment**: dilution of ownership, so features become unsupported and get dropped.
- **Local decisions excluding remote owners**: the path of least resistance creates conflict.

## Reference Tables
| Production meeting parameter | Value |
|---|---|
| Frequency | Weekly |
| Duration | 30–60 min |
| Chair | Rotating; on the smaller side in imbalanced video calls |
| Attendance | Compulsory for SRE team; stakeholders and product dev invited |

| DFP→F1 migration system | Value |
|---|---|
| CPUs | ~1,000 |
| RAM | 8 TB |
| Data indexed per day | 100 TB |

## Worked Example
**Viceroy: cross-SRE collaboration.** Monarch replaced Borgmon (Ch 10), but its consoles didn't scale to complex dashboards or support the legacy system. Teams (Spanner, Ads Frontend, and others) spun up duplicate projects for 12–18 months, e.g., *Consoles++*. In mid-2012 engineers discovered each other's work and formed **Viceroy**. Shared requirements were: complex curated dashboards, plus support for both Monarch and legacy. Other requirements diverged (no JS vs. full JS/AJAX, config vs. HTML layout, static/cacheable content). In early 2013 Consoles++ found the gap too wide, mainly over JavaScript, so the merge was parked. By late 2013 Viceroy used JS for graphs and integration reduced to "serve Consoles++ data from the Viceroy server". Prototypes came in early 2014, and the combined system was complete by end of 2014 under the Viceroy brand. Gains: new data sources and JS clients, modular JS compilation, and caching plus a background pipeline for Consoles++. Combined velocity was greater than the sum of the duplicates. Viceroy was declared SRE's general monitoring solution, but *recommended*, not mandated. Costs: remote coordination, contributor churn (1–3 month stints), dilution of ownership, and scope creep. One benefit was unplanned: returning contributors became local experts and drove adoption.

**DFP→F1 migration (outside SRE).** The aim was to migrate DoubleClick for Publishers from MySQL to F1 with byte-identical index output and zero user disruption. SREs drove the infrastructure design (incremental extraction of changed data, filtering/joins, machine-loss tolerance, linear resource growth, capacity planning). Two SREs wrote the design doc, both teams reviewed it, and the infrastructure/BL interface was defined early so product dev could work independently. SREs then built a prod-like test environment, product dev iteratively fixed index discrepancies, SREs prepared production (resources, monitoring, on-call training, a release process with validation), and the teams launched jointly with no visible user impact.

## Key Takeaways
1. Run a weekly, service-oriented production meeting with a rotating chair and a fixed agenda: changes, metrics, outages, paging, nonpaging, action items.
2. For every page, ask whether it should have paged that way and whether it should have paged at all. Delete noise.
3. Always include product dev partners. If you can't, repair the relationship first.
4. Write a crisp team charter that says what you won't support.
5. Go cross-site only when necessary. When you do, divide into single-site components, write everything down, and meet in person.
6. Engage with product dev at design time, before code exists. SRE owns infrastructure, dev owns business logic, and the interface is fixed early.
7. Prefer joining forces over duplication. Shared vision is what makes merges work.

## Connects To
- **Ch 4 (SLOs)**: metrics section of the production meeting.
- **Ch 10 (Practical Alerting)**: Borgmon, the legacy system Viceroy had to support.
- **Ch 15 (Postmortem Culture)**: the Outages agenda item.
- **Ch 32 (Evolving Engagement Model)**: early collaboration with product dev.
- **Ch 33 (Lessons from Other Industries)**: diverse backgrounds of SREs.
- **Appendix F**: example production meeting minutes.
- **External, Conway's law; OKRs; Spanner/F1**.
