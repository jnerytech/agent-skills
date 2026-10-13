# Chapter 20: The Attacker Agent: Adversarial Runtime Testing

## Core Idea
The pattern-completion talent that makes an LLM generate plausible code also makes it good at generating plausible-but-vicious input. Point an adversarial agent at your own contracts, give it an opposing objective, no view of the implementation and a disposable sandbox, and have it *execute* attacks against a running instance. Every break becomes a committed red test. It's the Inquisitor moved from review time to runtime.

## Frameworks Introduced
- **The Attacker Agent** (adversarial runtime testing): an agent paid to make a running contract fail.
  - When to use: on any service with a committed contract (OpenAPI/Pact, Ch 18), architectural boundaries (Ch 5), auth edges, or a serialization layer.
  - How, with three mandatory properties: (1) **Opposing objective**: the system prompt isn't "help ship this" but "the API in `openapi.yaml` claims these guarantees; produce inputs that violate them and prove it." (2) **Separate context**: it never sees the implementation or the conversation that produced it, only the contract and the running endpoint, so clean-looking code can't lull it. (3) **Separate, disposable runtime**: it executes the attacks it invents.
- **Two Fuzzing Modes**:
  - When to use: combine both on each contract surface.
  - How: **Property-based**: derive invariants from the contract ("every 200 matches this schema," "this endpoint is idempotent") and hunt for any input that breaks them. **LLM-guided**: reason about what *this* endpoint probably assumes and target that assumption: off-by-one, missing length cap, the "always present" field, the auth check guarding the handler but not the batch sibling beside it.
- **The Attacker Lives in the Sandbox**: the precondition for letting it be vicious.
  - When to use: always. An agent whose job is executing malicious input is the most dangerous process in your toolchain.
  - How: run it only inside the `docker sbx` microVM (Ch 19), against an ephemeral service instance, with throwaway data, no production credentials and no network path off the box. It may corrupt, crash or fill the disk of the instance, and cleanup costs a `docker rm`.
- **Every Break Becomes a Red Test** (attack → red test → fix → keep the test):
  - When to use: on every finding.
  - How: freeze the exact hostile input into the suite as a failing test *before* fixing. The fix is whatever turns it green, and the test stays forever so a later generation can't reintroduce the hole. Keep the loop local and pre-push. The attacker is "a factory that manufactures the regression tests you would never have thought to write."

## Key Concepts
- **Generator's twin talent**: the same completion machinery that produces plausible code enumerates sad paths cheaply and without getting bored.
- **Inquisitor vs Attacker**: the Inquisitor (Ch 22) is paid to be unhappy about a *diff*, and the Attacker is paid to make a *running contract* fail.
- **"Runs" is the critical word**: the output is a pass or a failure against the live service, not advice or a list of things to test.
- **Contract-vs-assumption gap**: defects live between what the contract says and what the code assumes. That gap is invisible to the person who wrote both, and the attacker, having seen only the promise, has no such blind spot.
- **Input collision**: the input-space counterpart of Ch 17's forced concurrency collision.
- **Vicious vs timid attacker**: an attacker confined by politeness finds nothing, while a vicious one confined by a microVM finds everything.

## Mental Models
- Think of the Attacker Agent as becoming the hostile input yourself, on purpose, before anyone else does.
- Use contracts as the attack surface. An endpoint outside the spec is one it never attacks, and an invariant you didn't encode is one it can't try to break.
- Treat an attacker log as a war story until it's a committed test. Only the test is a guardrail.
- It raises the cost of a hostile input dramatically, but it doesn't prove security. Selling it that way is like trusting a weak green test.

## Anti-patterns
- **Letting the attacker read the code**: it gets lulled by clean code and inherits the author's assumptions.
- **An attacker that emits suggestions instead of executing**: that's advice, not a guardrail-grade pass or fail.
- **Running it anywhere but a disposable sandbox**: it's executing hostile code paths by design.
- **Fixing before freezing the red test**: the regression protection is lost.
- **Running it only when someone remembers**: a guardrail that runs sometimes. It becomes real only as branch-level law in CI (Ch 21).

## Code Examples
```text
SYSTEM (Attacker Agent):
You are given ONLY the contract below and a running endpoint at http://svc:8080.
The API in openapi.yaml claims these guarantees. Produce inputs that violate them
and prove it by executing the requests. Report each break as: input, expected
(per contract), actual. You will never see the implementation.

CONTRACT: POST /orders accepts a JSON body, returns 201 with an order id,
and is idempotent on the Idempotency-Key header.
```
- **What it demonstrates**: an illustrative prompt showing all three properties: an opposing objective, contract-only context, and execution against a running instance.

## Worked Example
Contract: `POST /orders` accepts JSON, returns 201 with an order id, and is idempotent on `Idempotency-Key`. The attacker gets these three sentences plus the endpoint.
1. **Idempotency**: same body and same key twice gives matching responses. Same key with a *different* body should give the documented 409, but it returns a fresh 201 with a new id. The implementation keyed only on the header and never compared payloads. That's found in four requests, while a human reviewer read past it because "idempotent" was in the code comment.
2. **Integer boundary on `quantity`**: tries `0`, `-1`, `2147483648`, `"1"`, a float, `null`. A negative quantity is accepted and produces a negative line total, which downstream billing will turn into a credit.
3. **Length**: a 2 GB `notes` field crashes the JSON parser before validation runs, because the length cap lives in the validator and the parser sees the body first.
4. **Auth**: `POST /orders` is guarded, but the sibling `POST /orders/bulk`, added the same sprint and missing from the spec, inherited none of it.

A dozen requests found four defects, including an authorization hole that the Ch 21 SAST gate would only flag after merge. Each one is then frozen as a red test before it's fixed.

## Why It Works / Failure Mode
- **It works** because it combines a model's cheap, tireless enumeration of edge cases with independence from the implementation (no shared blind spot), and its findings come out in the same currency as every other guardrail: a deterministic test result. The sandbox makes it safe to be vicious.
- **It fails** when it's bounded by a narrow objective or an incomplete contract (unspecced endpoints go unattacked), when findings aren't converted into committed tests, and when it runs only as an optional local loop instead of pipeline law.

## Key Takeaways
1. Turn the generator's edge-case talent against your own contracts before an adversary does.
2. Give the attacker an opposing objective, contract-only context and a disposable runtime. All three are mandatory.
3. Combine property-based invariants from the contract with LLM-guided assumption hunting.
4. It must *execute* attacks against a running instance, and only inside a microVM sandbox with throwaway data.
5. Attack → red test → fix → keep the test, local and pre-push.
6. It finds only what it's pointed at. Spec everything (including batch siblings) and encode invariants.
7. Promote it to CI (Ch 21) so it runs on every change.

## Connects To
- **Ch 5**: architectural boundaries as attack surface; converting failures into committed tests.
- **Ch 17**: the forced concurrency collision. This is the input collision.
- **Ch 18**: the OpenAPI/Pact contract is the attacker's only view.
- **Ch 18b**: slopsquatting is this same move executed by someone else.
- **Ch 19 / 19b**: the containment the attacker requires (`docker sbx`, VibeKit Docker tier).
- **Ch 20b**: green has to mean something. Audit the tests the attacker manufactures.
- **Ch 21**: branch-level law; the SAST gate.
- **Ch 22**: the Inquisitor, the review-time sibling.
- **Property-based testing (QuickCheck)**; **fuzzing**; **red teaming / chaos engineering**.
