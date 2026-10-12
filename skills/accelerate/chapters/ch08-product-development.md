# Chapter 8: Product Development
*Authors: Nicole Forsgren, Jez Humble, Gene Kim*

## Core Idea
Lean product management practices (small batches, visible flow, customer feedback, and team authority to change specifications) predict both software delivery performance and organizational performance (productivity, profitability, market share), and software delivery performance in turn predicts these practices, forming a **virtuous cycle**.

## Frameworks Introduced
- **Lean product development / Lean product management (four capabilities)**:
  1. **Work in small batches**: slice products and features into small batches that can be completed in **less than a week** and released frequently, including the use of **MVPs**.
  2. **Make the flow of work visible**: teams understand the flow of work from the business all the way through to customers, with visibility into it, including status of products and features.
  3. **Gather and implement customer feedback**: actively and regularly seek customer feedback and incorporate it into product design.
  4. **Team experimentation**: development teams have the authority to create and change specifications as part of the development process without requiring approval.
  - When to use: to replace "faux Agile" (months of budgeting, analysis and requirements before work starts, big infrequent releases, customer feedback as an afterthought).
  - How: decompose work into features allowing rapid development instead of complex features on long-lived branches; prototype and validate from the beginning; pivot products and business models early and often.
  - Why it works: small batches give short lead times and fast feedback loops; feedback is only valuable if teams have authority to act on it. Failure mode: teams bound to requirements written by other teams build products that do not delight customers or deliver expected business results.
  - Findings: statistically significant in predicting higher software delivery performance and organizational performance; improves culture; decreases burnout.

- **The virtuous cycle (reciprocal model)**: 2016 model: Lean product management -> software delivery performance (plus generative culture, less burnout). 2017 model flipped: software delivery performance -> Lean product management. Combined across years: a reciprocal relationship. Lean product management also predicts organizational performance.
  - When to use: to justify investing in delivery capability as a product strategy enabler, and vice versa.
  - Why it works: better delivery makes small batches and continuous user research feasible, which produces better products. Failure mode: treating delivery and product practices as separate investments.

- **Team experimentation, bounded**: not "set developers free to work on whatever they like"; experimentation must be combined with small batches, visible flow, and customer feedback so decisions are well-reasoned, informed, feedback-driven, and communicated across the organization.

## Key Concepts
- **Faux Agile**: following some common Agile practices while failing to address wider organizational culture and processes.
- **Lean Startup**: Eric Ries' (2011) synthesis of Lean, design thinking, and Steve Blank's customer development for exploring products under uncertainty.
- **MVP (minimum viable product)**: a prototype with just enough features to enable validated learning about the product and its business model.
- **Validated learning**: evidence about the product and business model gathered from real users.
- **Small batches**: work units completable in under a week and released frequently.
- **Pivoting**: evolving products and their business models early and often.
- **A/B testing**: experimental technique for gathering user feedback quickly, enabled by small-batch delivery.
- **Customer feedback practices**: regularly collecting satisfaction metrics, seeking insights on quality, and using them to inform design.
- **Organizational performance**: measured here as productivity, market share, and profitability.
- **Virtuous cycle**: a reciprocal relationship where each capability predicts the other.

## Mental Models
- Think of **delivery performance and product management as one flywheel**: improving either accelerates the other.
- Use **authority to change specs** as the litmus test of real agility: feedback the team cannot act on is waste.
- Think of an **MVP as an experiment**, not a smaller release: its output is learning about the product and business model.
- Use the **one-week batch** as a default sizing rule for features.

## Anti-patterns
- **Faux Agile**: months of budgeting, analysis, and requirements-gathering before work starts.
- **Big projects with infrequent releases**: long feedback loops, long lead times.
- **Customer feedback as an afterthought**.
- **Requirements handed down by other teams**, with no authority to change them: sharply inhibits innovation.
- **Complex features developed on branches and released infrequently**.
- **Unbounded experimentation**: freedom without small batches, visibility, and feedback.

## Reference Tables

**Lean product management model (Figures 8.1 and 8.2)**

| Capability | Predicts / impacts |
|---|---|
| Work in small batches (incl. MVPs) | Software delivery performance; organizational performance |
| Make flow of work visible | Generative culture |
| Gather & implement customer feedback | Less burnout |
| Team experimentation (authority over specs) | Organizational performance (profitability, productivity, market share) |
| Software delivery performance (reciprocal) | Lean product management practices |

**Study timeline**

| Year | Model direction | Finding |
|---|---|---|
| 2016 | Lean product mgmt -> delivery | Positive impact on delivery, generative culture, decreased burnout |
| 2017 | Delivery -> Lean product mgmt | Confirmed: delivery drives Lean product management |
| Combined | Reciprocal | Virtuous cycle; Lean product mgmt predicts organizational performance |

## Worked Example
**Testing the reciprocal relationship over two years.** In 2016 the researchers modeled Lean product management practices as predictors and found they positively impact software delivery performance, stimulate a generative culture, and decrease burnout. In 2017 they flipped the model and confirmed that software delivery performance drives Lean product management practices: the better a team can deliver, the more it can work in small batches and perform user research along the way. Combining the two years yields a reciprocal model. Because these are predictive (not causal-proof) findings across years, the practical reading is: invest on both sides, since each makes the other easier, and together they predict profitability, productivity, and market share.

## Key Takeaways
1. Slice features so each can be completed in under a week and released frequently; use MVPs to test new products.
2. Make the end-to-end flow of work, from business to customer, visible to the team.
3. Collect customer satisfaction metrics and insights regularly and feed them into design decisions.
4. Give teams authority to create and change specifications without outside approval.
5. Pair experimentation with small batches, visible flow, and feedback; it is not a free-for-all.
6. Invest in continuous delivery capability to unlock Lean product practices (the virtuous cycle).

## Connects To
- **Ch 2**: organizational performance (productivity, profitability, market share) as the outcome.
- **Ch 3**: Lean product management stimulates a generative culture.
- **Ch 4**: experimental product development is highly correlated with continuous delivery technical practices; trunk-based development vs. long-lived branches.
- **Ch 5**: team autonomy (no outside permission) mirrors the architectural capability.
- **Ch 7**: Lean management practices (visual displays, flow) complement Lean product management.
- **Ch 9**: Lean product management decreases burnout.
- **The Lean Startup (Ries), customer development (Blank), design thinking**: external sources of the practices.
