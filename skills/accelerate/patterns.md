# Patterns & Techniques — Accelerate

## Four Key Metrics (Software Delivery Performance)
**When to use**: Measuring and benchmarking a delivery organization.
**How**: Track lead time for changes, deployment frequency, time to restore service, change fail rate. Benchmark against the high/medium/low performer table (Ch 2). Measure the delivery part of lead time, not the fuzzy front end. Use them as global, outcome-based measures shared by dev and ops.
**Trade-offs**: In a fearful culture the numbers get gamed ("whenever there is fear, you get the wrong numbers"); use for learning, never for control.

## Capabilities over Maturity
**When to use**: Planning a transformation.
**How**: Pick the capabilities from the 24 that constrain you now; improve them, re-measure outcomes, repeat. Never declare "done". (Ch 1, 17)
**Trade-offs**: Requires measurement discipline and tolerance for a J-curve dip (Ch 17).

## Measure Culture with Westrum's Seven Items
**When to use**: Diagnosing or tracking organizational culture.
**How**: Survey the 7 Likert items (information sought, messengers not punished, shared responsibilities, cross-functional collaboration, failure → inquiry, new ideas welcomed, failures as system-improvement opportunities); score as the mean; track over time. (Ch 3, 13)
**Trade-offs**: Survey data is perceptual; requires anonymity and validated constructs.

## Act Your Way to a Better Culture
**When to use**: Wanting to change culture.
**How**: Change practices (CD, Lean management) rather than running culture campaigns — culture follows behavior. (Ch 3, 4, 7)
**Trade-offs**: Slow; needs leadership support.

## Continuous Delivery Foundations
**When to use**: Improving tempo and stability together.
**How**: Version control for all production artifacts → deployment automation → CI with trunk-based development (< 3 branches, < 1 day) → reliable test automation owned by developers → test data management → shift-left security → deployable at all times. (Ch 4)
**Trade-offs**: Upfront investment; flaky tests must be quarantined, not tolerated.

## Loosely Coupled Architecture + Inverse Conway
**When to use**: Teams blocked by coordination, integrated test environments or release orchestration.
**How**: Design for testability and deployability; teams can change, test and deploy on demand without permission or coordination; restructure teams around desired architecture; let teams choose tools. (Ch 5)
**Trade-offs**: Service type (mainframe vs microservices) matters less than coupling; tool freedom vs standardization balanced by making the paved road attractive.

## Shift Left on Security
**When to use**: Security reviews slow or block releases.
**How**: Infosec in design and demos; preapproved libraries and toolchains; security tests in the automated suite; compliance via a platform (18F cloud.gov). (Ch 6)
**Trade-offs**: Requires infosec staffing to change role from gatekeeper to enabler.

## Lightweight Change Approval
**When to use**: Replacing CABs and heavy change management.
**How**: Peer review (pairing or intrateam review) + deployment pipeline as audit trail; satisfies segregation of duties when non-author review is recorded and deploys go only through the pipeline. (Ch 7)
**Trade-offs**: Auditors need education; avoid "risk management theater".

## Lean Management Triad
**When to use**: Improving flow and decision making.
**How**: WIP limits that drive improvement + visual displays of quality/productivity + production monitoring feedback used for business decisions. (Ch 7)
**Trade-offs**: WIP limits alone don't help — they must surface and remove obstacles.

## Lean Product Management
**When to use**: Product discovery and prioritization.
**How**: Small batches (< 1 week, MVPs), visible flow through the value stream, gather customer feedback, and give teams authority to experiment and change specs. (Ch 8)
**Trade-offs**: Requires fast delivery to be useful — it's a virtuous cycle with CD.

## Reduce Deployment Pain and Burnout
**When to use**: Teams dread releases or show burnout.
**How**: Make deployments automated, low-risk and routine; address Maslach's six risk factors (workload, control, rewards, community, fairness, values); invest in learning; foster a respectful, supportive environment. (Ch 9)
**Trade-offs**: Burnout fixes are organizational, not individual — don't send people to yoga instead of fixing the system.

## Transformational Leadership + Team Investment
**When to use**: Leaders enabling a transformation.
**How**: Practice the five dimensions (vision, inspirational communication, intellectual stimulation, supportive leadership, personal recognition); fund learning (training budgets, conferences, yak days, game days/DiRT); enable cross-functional collaboration; give teams good tools. (Ch 11)
**Trade-offs**: Leadership alone doesn't produce high performance — it enables the technical and Lean practices.

## High-Performance Management Rhythm (ING)
**When to use**: Spreading Lean/DevOps management at scale.
**How**: Team and leadership Obeyas; daily stand-ups; catchball up/down; strategy deployment (Hoshin Kanri) with PDCA; leaders coach (do the work, improve the work, develop people). Don't copy practices ("implementation thinking") — learn your own way. (Ch 16)
**Trade-offs**: Demands sustained leader time on the floor.

## Survey-Based Measurement
**When to use**: Measuring capabilities and culture across a full stack and many teams.
**How**: Use validated latent constructs (several items each); test validity/reliability (AVE > 0.50, composite reliability/Cronbach's alpha ≥ 0.70); keep surveys anonymous; avoid leading, loaded, double-barreled items; triangulate with system data. (Ch 12–15, 17)
**Trade-offs**: Perceptual; system data is objective but partial and gameable by single bad actors.
