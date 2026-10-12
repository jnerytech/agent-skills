# Chapter 18: The Stories (Extended Example)

## Core Idea
The second stage: run a **story-writing workshop** for South Coast Nautical Supplies and generate the initial backlog by walking through each user role/persona.

## What This Demonstrates
- Applies **story writing** (Ch 2) and the practice of **deferring detail** — questions ("search by one field or several at once?") are noted and left unanswered, keeping momentum.
- Shows writing stories **per role/persona** (Teresa, Captain Ron, Novice Sailor, Non-Sailing Gift Buyer, Report Viewer, Administrator), plus capturing **constraints** on cards.

## Worked Example (representative story cards)

**For Teresa (Experienced Sailor — power user, speed):**
- 18.1 — A user can search for books by author, title or ISBN number.
- 18.2 — A user can view detailed information on a book (pages, publication date, brief description).
- 18.3 — A user can put books into a 'shopping cart' and buy them when done.
- 18.4 — A user can remove books from her cart before completing an order.
- 18.5 — To buy a book the user enters billing address, shipping address and credit card info.
- 18.6 — A user can rate and review books.
- 18.7 — A user can establish an account that remembers shipping and billing info.
- 18.8 — A user can edit her account information.
- 18.9 — A user can put books into a 'wish list' visible to other visitors.
- 18.10 — A user can place an item from a wish list (even someone else's) into the cart.
- 18.11 — *(Constraint)* A repeat customer must find one book and complete an order in <90 seconds.

**For Captain Ron (Instructor — tentative, knows what he wants):**
- 18.12 — A user can view a history of all past orders.
- 18.13 — A user can easily re-purchase items when viewing past orders.
- 18.14 — The site tells a shopper the last 3 (?) items viewed, with links back (works between sessions).

**For Novice Sailor:**
- 18.15 — A user can see what books we recommend on a variety of topics.

**For Non-Sailing Gift Buyer:**
- 18.16 — A user (esp. Non-Sailing Gift Buyer) can easily find other users' wish lists.
- 18.17 — A user can choose to have items gift wrapped.
- 18.18 — A user can enclose a gift card with her own message.

**For Report Viewer:**
- 18.19 — A Report Viewer can see reports of daily purchases by category, traffic, best/worst sellers, etc.
- 18.20 — A user must be properly authenticated before viewing reports.
- 18.21 — *(Constraint)* Website orders must land in the same order database as telephone orders.

**For Administrator:**
- 18.22 — An administrator can add new books to the site.
- 18.23 — An administrator can approve or reject reviews before they appear.
- 18.24 — An administrator can delete a book.
- 18.25 — An administrator can edit information about an existing book.

**Wrap-up:**
- 18.26 — A user can check order status; if unshipped, add/remove books, change shipping method, delivery address, credit card.
- 18.27 — *(Constraint)* The system must support peak usage of up to 50 concurrent users.

Result: **27 stories** total to carry into estimation.

## Techniques visible in the example
- **Parenthetical notes on cards** (e.g., 18.10 "even someone else's") capture intent without designing.
- **Good performance constraint** (18.11) targets the whole user experience (find + order in 90s) rather than a narrow "search in 2 seconds."
- Detail is intentionally postponed; not every story must be found up front because development is iterative — new stories can be swapped in later for equal work removed.

## Key Takeaways
1. Workshop by role/persona to systematically surface stories; starting from the critical persona (Teresa) keeps focus on what matters.
2. Write the story, note the open question, move on — don't stall on detail.
3. Capture constraints as cards too, even though they aren't directly coded.
4. End-to-end, experience-level performance constraints beat component-level ones.

## Connects To
- **Ch 2 (Writing Stories)** and **Ch 7 (Guidelines for Good Stories)**: live application.
- **Ch 17**: roles/personas drive who each story serves.
- **Ch 19**: these 27 stories are next estimated (and several get split).
