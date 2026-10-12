# Chapter 30: Data Center Basics

## Core Idea
A service is only as reliable as the data center that houses it — even cloud resources live in mundane physical reality. A data center is a safe/secure space + racks + sufficient (and standby) power + cooling + network connectivity + on-site staff. The fast pace of IT and low tolerance for downtime have forced a "shotgun marriage" of IT and facilities staff. Know where your data actually lives, and evaluate vendors (or build your own) quantitatively.

## Frameworks Introduced
- **The six data-center components**: physically safe/secure space, racks, electric power (+ standby), cooling, network connectivity, on-site operational staff.
- **Three power-resilience strategies**: **UPS** (battery — minutes to a couple hours, bridges gaps), **on-site generators** (diesel/gas — long-term, store ≥72h fuel from multiple providers), **redundant power feeds** (multiple grid sources). Servers + network gear should at minimum be on UPSs that signal a clean shutdown before batteries die.
- **Per-rack power tiers** (not floor-space-based): allocate the same wattage to all racks in a tier (normal 6kW → 1U high-density 16kW → blade 20kW → custom 40kW); zone same-tier racks together to plan cooling.
- **Hot aisle / cold aisle**: alternate aisles — cold aisles have perforated cooling tiles, racks draw cool air from the cold aisle and exhaust into the hot aisle (exhaust sides back-to-back). Optimizes airflow so inlets never breathe another server's exhaust.
- **Cooling-load estimation**: sum heat from roof/walls/windows (HVAC team) + electronic gear + lights + operators (you calculate), convert watts → BTUH (×3.413), BTUH → tons (÷12,000), add ≥50% slop.

## Key Concepts
- **Racks over tables/floor**: the only maintainable choice; overhead cable tracks (Chatsworth) keep cables visible and traceable. Modern practice: raised floor for *power feeds and cooled air only* — route network cabling overhead.
- **kVA vs kW**: UPSs are rated in kVA; computer gear in W/kW. `watts = volts × amps × power-factor`. For modern computer gear, use a constant fudge factor; measure *actual* consumption (label values are misleading maximums).
- **PUE (Power Usage Effectiveness)** = total facility power ÷ IT-equipment power. Perfect = 1.0 (unreachable); good modern centers ≤1.4; a decade ago 2.0–3.0; Google ~1.12. *Replacing servers with more efficient ones raises PUE* (less IT power for the same overhead).
- **ASHRAE temperature**: 64.4–80.6°F (18–27°C) at server inlets (2012 lenient range). Humidity 8–60% (too low = static, too high = condensation/shorts).
- **Reliability tiers (Uptime Institute)**: Tier 1 (N, single feed, 99.671% = ~29h/yr downtime) → Tier 4 (2N generators/UPS/HVAC, dual simultaneous feeds, compartmentalized, 99.995% = ~26 min/yr). N = just enough, N+1 = one spare, 2N = full duplicate.
- **Remote power control**: APC web-controllable PDUs let you power-cycle wedged servers remotely.

## Mental Models
- **Plan power per-rack, not per-square-foot.** Floor area tells you nothing about what equipment a rack will house; magic-number-times-square-footage models fail. Use power tiers and look a decade ahead (you build/remodel a data center rarely).
- **All consumed electric power becomes heat.** Estimate cooling load from measured power consumption (watts × 3.413 = BTUH); double-check HVAC estimates, which can be off by an order of magnitude for modern high-density gear.
- **The data center is necessary but not sufficient for availability.** No amount of redundant power/cooling saves a poorly-architected or poorly-administered application — it's a foundational building block, not a guarantee.
- **Layered physical security, like layered network security.** Fence ≥25ft out, video covering 100% of perimeter, unmarked building, multifactor + guard at facility access, multifactor + video per rack in shared centers.

## Anti-patterns
- **Raised floor as a hidden cable rat's nest**: traditional all-under-floor routing looks nice but is unmaintainable — power/cooled-air under floor, network cabling overhead.
- **Sizing power/cooling from manufacturer label values**: those are misleading maximums — measure actual draw (Kill A Watt for small loads, clamp ammeter for large).
- **Putting only a few 1U servers per rack to dodge power density**: prodigious waste of space — provision realistic per-rack power instead.
- **Random rack/tile placement**: comfortable for humans, not optimized for computers — use hot/cold aisles.
- **Letting unverified "vendors" into the data center**: a security guard must turn away anyone whose visit can't be confirmed as authorized/requested (classic social-engineering vector).
- **Skipping standby-power test/maintenance**: test all UPS/generator components every ≤6 months, preventive maintenance ≥annually — untested backup power is no backup.
- **Building near hazard zones**: avoid fire/tornado/quake/flood areas and man-made hazards (airports, refineries, tank farms); research USGS risk data.

## Reference Tables
**Power tiers (watts/rack)**: normal 6kW · network switching 8kW · storage 12kW · 1U high-density 16kW · blade 20kW · ultra 25kW · custom 40kW.

**Reliability tiers**: T1 = N/single/99.671% (~29h/yr) · T2 = N gen, N+1 UPS/HVAC/single/99.741% · T3 = N+1, dual switchable/99.982% · T4 = 2N, dual simultaneous, compartmentalized/99.995% (~26min/yr).

**Cooling math**: watts → BTUH (×3.413); BTUH → tons (÷12,000); operators 300 BTUH each; add ≥50% slop. ASHRAE: 18–27°C, 8–60% humidity.

## Worked Example
**Size cooling for a 25-server room.** Sum the heat sources, each derived from power. (1) *Electronic gear*: 25 servers × 450W = 11,250W × 3.413 BTUH/W = 38,385 BTUH (all consumed power becomes heat — measure actual draw, not label max). (2) *Lights*: 6 fixtures × 4 tubes × 40W = 960W × 3.413 = 3,276 BTUH. (3) *Operators*: 4 people × 300 BTUH = 1,200 BTUH. (4) *Roof/walls/windows* (from your HVAC engineer, incl. solar load): 20,000 BTUH. **Total = 62,861 BTUH** → ÷12,000 = ~5.2 tons → add 50% slop ≈ **~8 tons** of cooling. Then compare against the HVAC team's estimate and reconcile any discrepancy *before* construction — textbook models can be off by an order of magnitude for high-density gear. Lay out hot/cold aisles so inlets breathe only cold air, and verify with an infrared thermometer (Fluke 62) that aisles are noticeably hot and cold.

## Key Takeaways
1. Reliability starts with the physical data center: secure space, racks, power+standby, cooling, network, staff — cloud doesn't escape physical reality.
2. Power: UPS (short gap) + generators (long-term, ≥72h fuel) + redundant feeds; plan per-rack power tiers, measure actual draw, test backup power every ≤6 months.
3. Cooling = sum of all heat sources (all power → heat); use hot/cold aisles; ASHRAE 18–27°C, 8–60% humidity; double-check HVAC estimates.
4. Track efficiency with PUE (good ≤1.4); route power under raised floor, network cabling overhead; use racks with overhead cable tracks.
5. Classify reliability by Uptime tiers (N / N+1 / 2N) — but the data center is necessary, not sufficient, for availability.
6. Physical and access security must be layered (fenced perimeter, video, multifactor + guard per facility and per rack); turn away unverified vendors.

## Connects To
- **Ch 9**: cloud computing (cloud resources still live in data centers; evaluating providers).
- **Ch 14**: physical networking (cabling, racks, structured wiring).
- **Ch 20**: storage hardware (rack-mounted disk arrays, power/cooling load).
- **Ch 27**: security (physical security as defense in depth).
- **Ch 28**: monitoring (environmental monitoring — temperature, power, humidity).
