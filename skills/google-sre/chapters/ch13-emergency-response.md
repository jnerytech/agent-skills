# Chapter 13: Emergency Response
*Authors: Corey Adam Baye (edited by Diane Bates)*

## Core Idea
"Things break; that's life." What distinguishes an organization is how its people respond: don't panic, pull in help, follow the incident process, and then learn — document outages, ask "what if…?", and proactively test failures before reality does.

## Frameworks Introduced
- **What to Do When Systems Break**:
  1. **Don't panic** — you aren't alone, you're trained; usually "only those poor electrons are in peril."
  2. **Pull in more people** if overwhelmed; it may even be necessary to page the entire company.
  3. **Follow your incident response process** (Ch 14) and know it beforehand.
  - Why it works: a proper response comes from preparation and periodic, pertinent, hands-on training — not natural talent ("Few of us naturally respond well during an emergency").
  - Failure mode: an unfamiliar or undisseminated process is effectively no process (Test-Induced case).
- **Three emergency archetypes** (each with Details / Response / What went well / What we learned):
  - **Test-induced**: proactive disaster testing exposes hidden dependencies.
  - **Change-induced**: a configuration push triggers unexpected interactions.
  - **Process-induced**: efficient automation amplifies a subtle bug at scale.
- **All Problems Have Solutions**: a solution exists even if not obvious to the person being paged.
  - How: cast your net farther, involve teammates, seek help — quickly; highest priority is resolving the issue. **The person with the most state is often the one whose actions triggered the event — utilize that person.** After mitigation, set aside time to clean up and write up the incident.
- **Learn from the Past. Don't Repeat It.**:
  - **Keep a history of outages**: thorough, honest, ask hard questions; look for tactical *and* strategic preventive actions; publish and organize postmortems company-wide; hold people accountable to follow up on action items.
  - **Ask the big, even improbable, questions: "What if…?"** — building power fails, racks in two feet of water, primary datacenter goes dark, web server compromised. Who do you call? Who writes the check? Could the person next to you do it?
  - **Encourage proactive testing**: until a system has actually failed you don't know how it, its dependents, or users will react; prefer failing during a reviewed test with your best people at hand over 2 a.m. Saturday during an offsite.

## Key Concepts
- **Proactive disaster testing (DiRT, [Kri12])**: SREs deliberately break systems, watch them fail, and fix weaknesses/hidden dependencies.
- **Hidden dependency**: an undocumented reliance revealed only by failure (e.g. on one test database among a hundred).
- **Out-of-band communications**: highly reliable, low-overhead backup channels used regularly so they work when primary stacks fail.
- **Panic rooms**: dedicated secure rooms with backup access to production.
- **Alternative access methods / CLI tools**: let engineers push and roll back when normal interfaces are down — must be practiced.
- **Canarying regardless of perceived risk**: "low-risk" changes skipping thorough canary caused the change-induced outage.
- **Sanity checks on automation commands**: an empty filter must not mean "everything" — "sometimes zero does mean all."
- **Diskerase**: queue where decommissioned machines' disks are wiped.
- **Rate-limited updates to new clients**: a protective throttle that kept crash-looping jobs partially serving.
- **Tested rollback procedures**: untested rollbacks lengthen outages.

## Mental Models
- Think of every emergency as raw material for the next improvement cycle: outage/test → documented failure mode → system and process fix → retest.
- Use "What touched it last / who touched it last" as a resource: the triggering engineer holds the most state.
- Think of your own tooling as a dependency: if troubleshooting and comms run on the crashing stack, you need independent fallbacks.
- Use controlled tests to choose *when* failure happens — business hours, experts present, rollback tested.

## Anti-patterns
- **Panicking / going it alone**: delays resolution; escalate early.
- **Ignoring or not knowing the incident process**: in the test case, stakeholders weren't informed because a weeks-old process wasn't disseminated.
- **Untested rollback before large-scale tests**: rollback failed and extended the outage.
- **Lighter canary for "low-risk" changes**: rare config keyword + new feature combo untested before global push (on a Friday).
- **Alert storms**: alerts firing repeatedly overwhelmed on-calls and spammed emergency channels.
- **Depending on your own production stack for incident tools.**
- **Automation without sanity checks**: an empty response passed as a filter wiped every machine.
- **Relying on luck**: the quick rollback happened only because the push engineer was watching real-time channels — not part of the release process.

## Reference Tables
| Case | Trigger | Detection / response | Time to recover | Key lessons |
|---|---|---|---|---|
| Test-induced | Block access to 1 of 100 MySQL DBs to find hidden deps | Dependent services escalated within minutes; test aborted; rollback failed; restored permissions to replicas/failovers + library fix in parallel | ~1 hour | Insufficient understanding of interactions; follow and disseminate incident process; test rollback procedures first; periodic retesting |
| Change-induced | Global Friday config push to anti-abuse infrastructure → crash-loop across externally facing fleet, plus internal apps | Alerts within seconds; on-calls moved to panic rooms; push engineer rolled back within 5 min; incident declared within 10 min | Most fast; some services up to 1 hour | Canary thoroughly regardless of perceived risk; tune alerting to avoid storms; practice alternative tools; don't depend on own stack |
| Process-induced | Two consecutive turndown requests; second hit an automation bug sending all small server installations globally to Diskerase | Drained traffic to large installations; disabled all team automation; froze maintenance | Traffic diverted within 1 hour; first site rebuilt in 3 h; most capacity in 3 days; stragglers over 1–2 months | Sanity-check automation commands (empty ≠ all); reinstall infra couldn't handle thousands of machines (TFTP at lowest QoS, BIOS halts/reboot loops, regression limiting 2 setup tasks/worker, forced kernel reinstall) |

## Worked Example
**Process-induced emergency.** During routine automation testing, two turndown requests for the same soon-to-be-decommissioned server installation were submitted. On the second run, the turndown server received an *empty* response for the machine rack and, lacking sanity checks, passed the empty filter to the machine database — which interpreted it as *all* machines, sending every small server installation worldwide to Diskerase. On-call got paged as the first site went offline, saw machines in the Diskerase queue, and drained traffic per procedure; as pages fired globally, they **disabled all team automation** and froze production maintenance. Large installations (managed differently, built to handle full load) absorbed the traffic within an hour; users saw elevated latency but requests succeeded. Network engineers mitigated congested links as the top priority, and on-call reverted the automation's teardown of monitoring to assess damage. Recovery: one site rebuilt in 3 hours; US handed off to Europe; SRE ran a streamlined manual reinstall split into three teams, one per step; most capacity was back in 3 days. Reinstall bottlenecks were fixed by raising install traffic QoS, auto-restarting stuck machines, and escalating to the reinstall infrastructure owners to retune it. Incident communication was "superb," crediting the incident management program matured since the first case.

## Key Takeaways
1. Don't panic; escalate and pull in people early, up to paging the whole company.
2. Know and follow your incident process, and make sure updates to it are disseminated.
3. Test rollback procedures before large-scale disaster tests, and canary every change regardless of perceived risk.
4. Put sanity checks on automation — treat empty input as an error, never as "all."
5. Keep reliable out-of-band comms and alternative access tools, and use them regularly.
6. Use the person who triggered the event — they have the most state.
7. Keep a published history of outages, ask "What if…?", and proactively test failures under controlled conditions.

## Connects To
- **Ch 7**: "Automation: Enabling Failure at Scale" — the Diskerase incident in detail.
- **Ch 8**: canarying and release engineering.
- **Ch 11**: DiRT, escalation paths.
- **Ch 12**: triage/stop the bleeding.
- **Ch 14**: the incident response process to follow.
- **Ch 15/16**: postmortems and outage history tracking.
- **Ch 17**: disaster and reliability testing.
- **Ch 33**: preparedness and disaster testing in other industries.
