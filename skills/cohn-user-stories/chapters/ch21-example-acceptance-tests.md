# Chapter 21: The Acceptance Tests (Extended Example)

## Core Idea
The final stage: the customer (with programmer help) writes **acceptance tests** on the backs of the release stories to define "done" — and the conversation refines stories and the design.

## What This Demonstrates
- Applies **acceptance testing** (Ch 6): customer-specified tests, written before/while coding, focused on confirming behavior including edge and failure cases.
- Shows tests **driving design simplification** (merging delete-from-cart into quantity adjustment) and surfacing clarifications (Visa/MasterCard only; price-change handling).

## Worked Example (sample tests on story-card backs)

**Basic search (21.1):** search a word in titles but not authors ("navigation"); a likely author not a title ("John"); a word in neither ("wookie").

**Advanced search (21.2):** author+title matching ≥1 book; author+title matching none; an ISBN search.

**Shopping cart** — discussion led to **ripping up the remove-from-cart story and replacing it** with 21.5 (adjust quantity; setting quantity to 0 removes the item), simplifying the system and avoiding a separate delete story.
- *Add to cart (21.3):* add out-of-stock book (told it ships when available); add not-yet-published book (same); add in-stock book; add a second copy (count goes up).
- *Adjust quantity (21.5):* change 1→10; change 10→1; set to 0 to remove.

**Buy books (21.6)** — clarified: separate or same shipping/billing address; **Visa and MasterCard only**:
- billing with shipping marked same; separate billing/shipping; state vs. postal-code mismatch caught; ship to shipping (not billing) address; valid Visa; valid MasterCard; **American Express (fail)**; expired Visa; over-limit MasterCard; Visa missing digits; Visa transposed digits; completely invalid Visa.

**Accounts (21.7):** order without an account; create an account, recall it, verify saved info.

**Edit credit card (21.8):** invalid number warned; past expiration not saved; valid new number saved; future expiration saved.

**Edit addresses (21.9):** change parts of shipping address (saved); change parts of billing address (saved).

**Admin add book (21.10):** admin can add; non-admin cannot; add only if required data present.

**Admin delete book (21.11):** admin can delete; non-admin cannot; after delete, outstanding orders still ship.

**Admin edit book (21.12)** — discussion surfaced a price-change rule:
- name/author/pages etc. can be changed; price can change but price changes do **not** affect previously placed (unbilled, unshipped) orders.

**Constraints:**
- *Same order DB (21.13):* place a web order, open the telephone order-entry database, verify it's stored there.
- *50 concurrent users (21.14):* simulate 50 users searching and ordering; no screen takes >4 seconds; no orders lost.

**Recommendations (21.15):** decided to be a simple static page — select a topic (navigation, cruising), verify recommendations make sense; click an item, verify it links to that book's info page.

## Key Takeaways
1. Writing acceptance tests is itself a requirements conversation — it clarifies scope (card types, price changes) and can simplify the design (quantity-0 replaces a separate delete story).
2. Good tests cover happy path, edge cases, and explicit failure cases (expired/over-limit/invalid cards, non-admins, wrong card brand).
3. Constraints get concrete, measurable tests too (verify shared DB; 50 users, <4s, no lost orders).
4. The customer owns the tests; programmers/testers help, which deepens shared understanding.

## Connects To
- **Ch 6 (Acceptance Testing User Stories)**: customer-specified tests on card backs.
- **Ch 11 (Splitting/refining)**: the cart story rewrite mid-testing.
- **Ch 20**: tests are written for exactly the stories prioritized into the release.
