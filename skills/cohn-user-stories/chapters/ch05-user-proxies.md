# Chapter 5: Working with User Proxies

## Core Idea
A real user on the customer team beats any substitute, but when you can't get enough real users you must work through **user proxies** — and each proxy type carries a predictable bias you must recognize and compensate for. A real user beats a proxy any time.

## Frameworks Introduced
- **The user-proxy taxonomy (with each one's pitfall)**: a catalog for choosing and correcting proxies.
  - When to use: whenever real users are missing or access is limited.
  - How: identify which type(s) you have, anticipate the bias, and counterbalance — ideally combine *different* proxy types rather than two of the same.
- **Constituting the customer team (four steps)**:
  1. Add **real users** — one of each type if users differ (e.g., regular, oncology, diabetic nurses).
  2. Identify a single **project champion** ("first among equals," often a product manager) — one customer *voice* even if not one customer.
  3. Determine the project's **critical success factors**.
  4. Supplement with proxies whose skills address those factors (e.g., add a trainer when migrating existing users).
- **Techniques when access is limited / no user exists**: start a **user task force** (real users as a sounding board while the proxy stays final decision-maker); use **multiple, differing** proxies; do **competitive analysis** of rival products; **release early** to open a channel to real users.

## Key Concepts
- **User proxy**: someone on the project to represent users who may not be a user themselves.
- **Users' manager**: available when real users aren't — but has different usage patterns; may ego-intercede; can be a misinformation amplifier ("five minutes" was really one).
- **Development manager**: one of the worst proxies — conflicting goals (pet technology, bonus tied to a date) and rarely a real user, unless also a domain expert.
- **Salesperson**: biased toward the feature that lost the last sale; lacks comprehensive vision — but an excellent *conduit* to users.
- **Domain / subject-matter expert**: great for domain models and business rules, but workflow/usage is better from actual users; risks software only an expert can use.
- **Marketing group**: understands *markets*, not users (Constantine & Lockwood); tends to favor feature *quantity* over quality.
- **Former user**: useful only if experience is very recent and incentives still align.
- **Customer**: the one who makes the buying decision, not necessarily a user (e.g., IT staff choosing a word processor) — great proxy only if in close contact with users; ideal if also a user.
- **Trainers / technical support**: yield a system that's easy to *train* or *support*, not what users would prioritize (support may de-prioritize advanced features).
- **Business / systems analyst**: often good (one foot in tech, one in domain) — if they actually talk to users and don't over-invest in up-front activities.
- **User task force**: a handful to a couple dozen real users used as a sounding board while a proxy retains final decisions.

## Mental Models
- Treat every proxy as **"a real user beats a proxy any time"** — proxies are a fallback, never a preference.
- **"Talk to your users"**: gut feel fails (the health site with 200 hits; the "automated book"; XML chosen over the CSV the IT users actually wanted) — proxies' assumptions must be checked against real users.
- **Balance strengths against weaknesses**: combine a domain expert with someone from marketing, not two domain experts, so biases cancel.
- Don't fall into **"can I do it myself?"** — developers usually have *more* shortcomings than any proxy (no marketing sense, no customer contact, not domain experts).

## Worked Example
Internal call-center / VP scenario chain of distortion: real users ran a **one-minute** query (acceptable for the data size). Users reported it to their manager, who inflated it to **two minutes** to get the VP's attention; the VP inflated it to **"up to five minutes"** to get developers' attention. The team's own query-execution logs (parameters, time, user, monitored daily) showed no real problem. Lesson: the users' manager (and layers above) amplify misinformation — corroborate with real users and real data.

Successful pattern: an internal project ran month-long iterations, spent the first days prototyping and holding **user task force** meetings, took top-level direction from the proxy (the users' manager) but moved implementation decisions to the task force.

## Key Takeaways
1. Always put real users on the customer team first; use proxies only to fill gaps.
2. Know each proxy's built-in bias and actively counterbalance it.
3. When forced to use proxies, use *multiple different types* so weaknesses offset.
4. Use salespeople and the users' manager as *conduits* to real users, not as the sole voice.
5. Establish a user task force when access is blocked; let the proxy keep final say but route day-to-day decisions to real users.
6. Use competitive analysis and early/beta releases to open communication paths to actual users.
7. Build the customer team in four steps and ensure one consistent customer voice via a project champion.
8. Resist "I know my users" — developers are usually worse proxies than the proxies.

## Connects To
- **Ch 3 (User Role Modeling)**: proxies stand in for specific roles; modeling clarifies which roles go unrepresented.
- **Ch 4 (Gathering Stories)**: salespeople/task forces are conduits for interviews and observation; release-early enables observation.
- **Ch 1**: defines and now staffs the customer team with the right voices.
- **Usage-centered design (Constantine & Lockwood)**: source of the markets-vs-users insight.
