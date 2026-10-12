# Chapter 20: The Release Plan (Extended Example)

## Core Idea
The fourth stage: build a **release plan** that fits the boss's four-week deadline by choosing iteration length, estimating velocity, prioritizing, and allocating stories to iterations.

## What This Demonstrates
- Applies **release planning** (Ch 9) and **MoSCoW prioritization**: iteration length → velocity → priority → allocation.
- Shows velocity **guessed** (no historical data) and a conservative buffer for the first iteration.

## Worked Example (the four steps)

1. **Iteration length:** two-week iterations → two iterations before the four-week deadline.
2. **Velocity:** only Maria and Rafe will code (Jay only helped estimate). One story point ≈ one ideal day; ~2–3 real days per ideal day; two-week (10-day) iteration × 2 programmers = 20 programmer-days. They expect 7–10 points/iteration and conservatively set **velocity = 8** (16 points over two iterations).
3. **Prioritize:** Lori sorts cards into **Must / Should / Could / Won't Have**. Must-Have sums to **9 points**; she then pulls Should-Have stories (4 more) to reach **15½ points**, close to the 16 available.
4. **Allocate:** stories assigned to Iteration 1 and Iteration 2.

## Reference Tables

**Must-Have stories (Table 20.1) — sum = 9:**

| Story | Est. |
|---|---|
| Basic simple search (author + title) | 1 |
| Put books in cart and buy them | 1 |
| Remove books from cart | ½ |
| Enter billing/shipping + credit card to buy | 2 |
| Establish account remembering shipping/billing | 2 |
| *(Constraint)* Orders land in telephone order DB | 0 |
| Admin add new books | 1 |
| Admin delete a book | ½ |
| Admin edit existing book | 1 |
| *(Constraint)* Support 50 concurrent users | 0 |

**Should-Have stories added (Table 20.2) — +4½ → 15½ total:**

| Story | Est. |
|---|---|
| Advanced search (any combo of author, title, ISBN) | 1 |
| Edit credit card in account | ½ |
| Edit shipping/billing addresses in account | 1 |
| See recommended books by topic | 4 |

**Finished release plan (Table 20.3):**

| Iteration 1 | Iteration 2 |
|---|---|
| Basic simple search | Admin edit existing book |
| Put books in cart and buy | Advanced search (any combo) |
| Remove books from cart | Edit credit card in account |
| Enter billing/shipping + credit card | Edit shipping/billing addresses |
| Orders land in telephone DB *(constraint)* | See recommended books by topic |
| Establish account | |
| Admin add new books | |
| Admin delete a book | |
| Support 50 concurrent users *(constraint)* | |

## Key Takeaways
1. With no history, guess velocity from ideal-day-to-real-day ratios and stay conservative for iteration one.
2. MoSCoW lets the customer fill the available velocity with the highest-value stories.
3. The plan is a communicated commitment but stays flexible — finish early and pull a story up; fall behind and push one down (renegotiate scope, not the date).

## Connects To
- **Ch 9 (Planning a Release)** and **Ch 10 (Planning an Iteration)**: velocity, prioritization, allocation.
- **Ch 19**: the estimates that make this plan computable.
- **Ch 21**: the release stories now get acceptance tests.
