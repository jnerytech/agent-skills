# Chapter 19: Estimating the Stories (Extended Example)

## Core Idea
The third stage: assign **story-point estimates** to the 27 stories using collaborative estimation, splitting and clarifying stories as estimation exposes ambiguity.

## What This Demonstrates
- Applies **estimating in story points** and **Planning-Poker-style** group estimation (Ch 8): three programmers (Rafe, Jay, Maria) each reveal a card, discuss the spread, re-estimate until convergence.
- Shows the customer (Lori) **present but not estimating** (and not allowed to gasp at estimates).
- Shows estimation driving **story splitting** and clarification.

## Worked Example (the estimation dynamics)

**First story split before estimating:** "search by author, title or ISBN" became two stories once Lori clarified she wanted both a basic and an advanced mode:
- 19.1 — Basic search across author + title fields.
- 19.2 — Advanced search: any combination of author, title, ISBN.

**Planning-poker round (Story 19.1):** Rafe 1, Jay ½, Maria 2 → discuss (search-engine selection vs. familiarity) → re-vote → all **1**.

**Splits driven by estimation:**
- "rate and review" split into 19.3 **rate** (2 pts) and 19.4 **write review** (4 pts) — reviews far more involved.
- "edit account info" split into 19.5 **edit credit card** (½) and 19.6 **edit addresses** (1) — finer prioritization flexibility.
- "check status / change order" split into 19.8 **check status** (½) and 19.9 **change unshipped order** (1).
- vague wish-list-find rewritten as 19.7 — search wish list by owner's name and state (1).

**Constraints estimated at 0 points** (they influence other stories, no standalone code): the 90-second order constraint, the shared-order-database constraint, the 50-concurrent-users constraint.

## Reference Table — Complete Estimates (Table 19.4)

| Story | Est. |
|---|---|
| Basic simple search (author + title) | 1 |
| Search by any combination of author, title, ISBN | 1 |
| View detailed information on a book | 1 |
| Put books in cart and buy them | 1 |
| Remove books from cart before order | ½ |
| Enter billing/shipping address + credit card to buy | 2 |
| Rate books 1–5 (any book) | 2 |
| Write a review with preview (any book) | 4 |
| Admin approve/reject reviews | 2 |
| Establish account remembering shipping/billing | 2 |
| Edit credit card stored in account | ½ |
| Edit shipping/billing addresses in account | 1 |
| Put books in a wish list visible to others | 2 |
| Search wish list by owner name + state | 1 |
| Check status of recent orders | ½ |
| Change unshipped order (add/remove, shipping, address, card) | 1 |
| Place wish-list item (even another's) into cart | ½ |
| *(Constraint)* Find + order in <90 seconds | 0 |
| View history of past orders | 1 |
| Re-purchase items from past orders | ½ |
| Show last 3 (?) items viewed, links (between sessions) | 1 |
| See recommended books by topic | 4 |
| Gift wrap items | ½ |
| Enclose a gift card with message | ½ |
| Report Viewer reports (purchases, traffic, best/worst) | 8 |
| Authenticate before viewing reports | 1 |
| *(Constraint)* Orders land in telephone order DB | 0 |
| Admin add new books | 1 |
| Admin delete a book | ½ |
| Admin edit existing book | 1 |
| *(Constraint)* Support 50 concurrent users | 0 |

## Key Takeaways
1. Estimation conversations surface ambiguity — let them trigger splits and rewrites (search, rate/review, edit account, order-status all split here).
2. Use independent reveal + discuss + re-vote until convergence; one or two rounds usually suffice.
3. The customer attends to answer questions but does not estimate and must not react to numbers.
4. Constraints can be 0 points — they shape other work rather than producing their own deliverable.

## Connects To
- **Ch 8 (Estimating User Stories)**: story points, ideal time, Planning Poker.
- **Ch 11 (Splitting User Stories)**: the splits performed here.
- **Ch 20**: these estimates feed velocity-based release planning.
