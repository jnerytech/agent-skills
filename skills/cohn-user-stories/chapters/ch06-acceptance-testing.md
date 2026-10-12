# Chapter 6: Acceptance Testing User Stories

## Core Idea
Acceptance tests capture the details and assumptions that surface in customer-developer conversations; they are written by the customer, before coding, and define when a story is "done."

## Frameworks Introduced
- **Two-step testing process**: tests grow alongside the story, not after it.
  - When to use: from the first conversation about a story through the end of every iteration.
  - How: (1) jot test *reminders* on the back of the story card whenever anyone thinks of one; (2) later turn those notes into full executable tests that demonstrate the story is correctly and fully coded.
  - Why it works: separates cheap idea-capture from expensive test construction, so no detail is lost and tests exist before coding starts.
- **Customer test-generation questions** (asked at iteration start, per story):
  - What else do the programmers need to know about this story?
  - What am I assuming about how this story will be implemented?
  - Are there circumstances when this story may behave differently?
  - What can go wrong during the story?
- **FIT / FitNesse (Framework for Integrated Test)**: Ward Cunningham's tool (FitNesse extends it).
  - When to use: to automate acceptance tests so they can re-run every iteration cheaply.
  - How: customer writes tests as spreadsheet/tabular rows of inputs + expected results; a programmer writes "fixture" code that invokes the application; results render green (pass) / red (fail).

## Key Concepts
- **Acceptance test**: criterion specified by the customer proving a story meets her vision/expectations.
- **Confirmation**: the test side of the story; lives on the *back* of the card.
- **Test reminder**: a short note (not yet a real test) jotted on the card back.
- **Functional testing**: verifying the application behaves as expected (the bulk of story testing).
- **Regression burden**: acceptance tests from all prior iterations must keep passing, so the suite grows each iteration — motivating automation.
- **Testing for bugs, not coverage**: agile testing aims to find/eliminate bugs, not chase 100% coverage or all boundaries.

## Mental Models
- Think of an acceptance test as the cake-doneness toothpick: an explicit, agreed signal that tells you exactly when to stop investing effort — neither too little nor too much.
- Use the back of the card as the home for expectations: if behavior isn't recorded on the card before coding, programmers may guess wrong (e.g., insert scanned pages into the open document vs. a new one).
- Customer specifies tests; whoever is *best equipped* executes/automates them. The tester brings a suspicious mindset; the product manager brings org goals.
- Stop writing tests when another test adds no clarification (don't re-test expired Visa after expired MasterCard); unit tests already cover low-level minutiae (Feb 30, June 31).

## Reference Tables
FIT/FitNesse credit-card validity table (Table 6.1) — each row is one input set; `valid()` is the expected result column:

| CardType | Expiration | Number | valid() |
|---|---|---|---|
| Visa | 05/05 | 4123456789011 | true |
| Visa | 05/23 | 4123456789012349 | false |
| MasterCard | 12/04 | 5123456789012343 | true |
| MasterCard | 12/98 | 5123456789012345 | false |
| MasterCard | 12/05 | 42 | false |
| American Express | 4/05 | 341234567890127 | true |

## Worked Example
Story: *"A company can pay for a job posting with a credit card."* On the back of the card the customer writes reminders:
- Test with Visa, MasterCard, American Express (pass)
- Test with Diner's Club (fail)
- Test with good, bad, and missing card ID numbers
- Test with expired cards
- Test with different purchase amounts, including one over the card's limit

The "over the limit" reminder, seen *before* coding, prompts the programmer to handle a declined-for-insufficient-credit case she'd otherwise forget. Note the customer learns from developers that all card types are processed identically, so testing one expired card type (MasterCard) suffices — bug-focused, not coverage-driven.

## Key Takeaways
1. Tests express the details and customer assumptions that arise in conversation — a substitute for "the system shall…" requirement lists.
2. Write tests *before* coding so they inform implementation; capture reminders on the card back the moment they're thought of.
3. The customer specifies and executes the tests (with help from testers/developers); testing is part of development, not an after-coding phase.
4. Acceptance tests are the "done" criterion — they prevent over- and under-investing in a story.
5. Stop when more tests stop clarifying; rely on unit tests for low-level cases.
6. Run all prior iterations' acceptance tests each iteration; automate with FIT/FitNesse to keep this affordable.

## Connects To
- **Ch 5 (The Customer)**: it is the customer/product manager who owns and specifies these tests.
- **Ch 10 (Planning an Iteration)**: initial tests are written as a dedicated effort at iteration start, before programming.
- **Specification by Example / ATDD (external)**: same pattern of executable, customer-authored examples as living documentation.
