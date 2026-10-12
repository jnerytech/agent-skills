# Chapter 33: Lessons Learned from Other Industries
*Authors: Jennifer Petoff (edited by Betsy Beyer)*

## Core Idea
SRE's core principles (preparedness, blameless postmortems, automation, data-driven decisions) already exist in high-reliability industries such as nuclear, aviation, medical, telecom, finance and manufacturing. What differs is how each industry implements them, and that depends on what failure costs. Google can accept more velocity because lives are rarely at stake, and it uses error budgets to "fund" that risk.

## Frameworks Introduced
- **The four key themes of reliability**: (1) Preparedness and Disaster Testing; (2) Postmortem Culture; (3) Automation and Reduced Operational Overhead; (4) Structured and Rational Decision Making.
  - When to use: as a lens for comparing any reliability practice across domains, or for auditing your own org's reliability culture.
  - How: for each theme ask how it shows up, why (regulation, safety, cost, speed), and whether the industry's risk appetite justifies its form.
  - Why it works / failure mode: it separates the *principle* from the *implementation*, so you can borrow ideas without importing another industry's risk tolerance. The failure mode is copying a practice (e.g., "the binder", zero automation) without the context that justified it.
- **"Hope is not a strategy" / DiRT (Disaster and Recovery Testing)**: annual drills that push production to its limits and cause real outages in order to (a) confirm systems react as expected, (b) find unexpected weaknesses, (c) make systems more robust against uncontrolled outages.
  - When to use: whenever you trust a failover or recovery path you have never exercised.
- **Seven preparedness strategies seen in other industries**:
  1. Relentless organizational focus on safety: every management meeting opens with safety, workers are empowered to speak up, and formal standards define levels such as Safety Integrity Level (SIL) 1–4 (UK Def Stan 00-56, IEC 61508, DO-178B/C, DO-254).
  2. Attention to detail: small lapses (submarine lube-oil maintenance) snowball in interconnected systems.
  3. Swing capacity: telecom "SOW" (switch on wheels), a mobile telco office rolled out for disasters or known peaks such as the Olympics.
  4. Simulations and live drills: the choice depends on the consequences of failure. Aviation uses high-fidelity simulators with live feeds, the nuclear Navy runs live drills "breaking real stuff but with control parameters" 2–3 days per week, and lifeguards stage "mystery shopper" mock drownings.
  5. Training and certification: rigorous initial certification plus periodic recertification and site-specific training.
  6. Detailed requirements gathering and design: gather requirements from real users and maintainers (surgeons, technicians). Defense work spent about 1 year on design and 3 weeks on code.
  7. Defense in depth (and breadth): redundancy on all systems, mandatory fallback behind every primary, and multiple layers down to a final physical barrier (nuclear).
- **CAPA (Corrective and Preventive Action)**: systematically investigate the root causes of issues or risks to prevent recurrence. SRE's version is the blameless postmortem. It evaluates what happened, how effective the response was, what to do differently, and which actions prevent recurrence.
- **Structured and rational decision making (Google SRE criteria)**: (1) agree on the basis for the decision in advance, not ex post facto; (2) make the inputs clear; (3) state assumptions explicitly; (4) data beats feelings, hunches and the HiPPO ("Highest-Paid Person's Opinion"). Baseline assumption: everyone has users' best interests at heart and can proceed from the available data.
- **UK nuclear 30-minute automation rule**: if a plant must respond to a situation in under 30 minutes, the response must be automated.

## Key Concepts
- **DiRT**: Google's annual Disaster and Recovery Testing drills, which inflict real outages.
- **Swing capacity / SOW**: excess mobile capacity deployed for emergencies or predictable surges.
- **Safety Integrity Level (SIL 1–4)**: formal reliability tiers for safety-critical software.
- **Defense in depth**: layered redundancy with fallbacks behind every primary system.
- **CAPA**: corrective and preventive action, the regulated-industry ancestor of postmortems.
- **Near miss**: an event that could have caused serious harm but did not. Treat it as a "preemptive postmortem". "Latent error, plus an enabling condition, equals things not working quite the way you planned" (VM Brasseur).
- **CHIRP**: the UK's Confidential Reporting Programme for Aviation and Maritime, where staff report near misses confidentially. Analyses are published in newsletters.
- **Trusted human decision chain**: the nuclear Navy's use of a series of people (operator, supervisor, a crew member on the phone with the engineering watch officer) instead of automation.
- **HiPPO**: Highest-Paid Person's Opinion. Decisions must not defer to it.
- **Enforcement team**: in proprietary trading, a group separate from the traders that halts the system on abnormalities. Only this team can restart it.
- **"The binder"**: a prescriptive playbook covering every conceivable scenario.

## Mental Models
- Use **live drills** when the cost of a controlled real failure is acceptable. Use **simulations** when a production test would endanger people (aviation).
- Think of **risk appetite as the dial** that sets every implementation choice: speed of change, degree of automation, and prescriptiveness of procedures all follow from the cost of failure.
- Think of **automation speed as double-edged**: it removes human error (LASIK iris matching), but it also lets misconfiguration do irreparable damage fast (Knight Capital lost $440M in a few hours, and the 2010 Flash Crash caused losses on the order of trillions of dollars in 30 minutes).
- Use **prescriptive playbooks** when systems change slowly and worker skill varies. Use **open-ended data-driven problem solving** when systems change constantly (Google).

## Anti-patterns
- **Ignoring near misses**: almost every disaster is preceded by several near misses. They are disasters waiting to happen.
- **Blaming individuals**: incidents are chaotic and have many causes. Blame is counterproductive in Google SRE and in lifeguarding alike.
- **Automation without verification for high-speed, high-impact actions**: incorrectly configured automation in trading caused huge losses within minutes.
- **"If it ain't broke, don't fix it… ever"**: this works for bulletproof 1980s telecom switches and nuclear plants. It fails where scenarios keep changing because of continuous updates.
- **Thought exercises alone**: the nuclear Navy considers them insufficient. Responses must be practiced or they are forgotten.

## Worked Example
**LASIK automation, layered over time (Erik Gross).** Originally, the doctor typed refractive measurements and pressed a button. This risked data-entry errors, mixed-up patients and swapped left/right eyes.
1. First fix: a computerized sanity check prominently flags any manually entered value outside the expected range.
2. Next fix: the iris is photographed during the preliminary refractive test. At surgery, the patient's iris is automatically matched to the photo.
3. Result: an entire class of medical errors (patient mix-ups) disappeared.
Lesson: target automation at the error class that humans commit, starting with input validation. Compare Appendix B "Fail Sanely".

**Trading enforcement team (John Li).** On a system abnormality, the first response is to shut down: "If we aren't trading, we aren't losing money." Only the separate enforcement team can bring trading back up, however painful the missed opportunity is for traders. This is a separation-of-duties pattern for risk.

## Key Takeaways
1. Borrow principles, not implementations. Calibrate to your own cost of failure, as Google does with error budgets.
2. Exercise disaster responses regularly with live drills or realistic simulations. Practiced responses are the ones that work.
3. Treat near misses as free postmortems and give people a low-friction, confidential way to report them.
4. Automate any response that must happen faster than humans can reliably act (the 30-minute rule). Put verification and kill switches around fast, high-impact automation.
5. Decide on the basis of criteria agreed in advance, explicit assumptions and data, not the HiPPO.
6. Separate the people who take risk from the people who can halt the system when risk is very high.
7. Layer defenses: redundancy, fallbacks and a final barrier.

## Connects To
- **Ch 3 Embracing Risk**: error budgets are how Google pays for a higher velocity appetite than other industries.
- **Ch 7 Evolution of Automation**: the pros and cons of automation mirror the nuclear, trading and LASIK cases.
- **Ch 15 Postmortem Culture**: the blameless postmortem is SRE's CAPA.
- **Ch 28 Accelerating SREs to On-Call / Ch 11**: training, certification and Wheel of Misfortune parallel lifeguard recertification.
- **Ch 26 Data Integrity / Ch 22 Cascading Failures**: defense in depth and DiRT testing.
- **External: Safety Integrity Levels (IEC 61508), CAPA, Six Sigma**: formal reliability disciplines from regulated industries.
