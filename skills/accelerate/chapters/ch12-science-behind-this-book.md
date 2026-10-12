# Chapter 12: The Science Behind This Book
*Authors: Nicole Forsgren, Jez Humble, Gene Kim*

## Core Idea
The book's claims rest on **primary, quantitative** research (Likert-type surveys) analyzed at the descriptive, exploratory, and **inferential predictive** levels, plus classification (clustering). Wherever the book says practices "impact" or "drive" outcomes, it means theory-driven inferential prediction, **not causation**.

## Frameworks Introduced
- **Leek's six types of data analysis (Leek 2013)**, in order of increasing complexity (knowledge, cost, and time):
  1. **Descriptive**: summarize and report data (e.g., a census).
  2. **Exploratory**: look for relationships and patterns, visualize, detect outliers. This includes correlation but not causation.
  3. **Inferential predictive**: test theory-driven hypotheses in field settings where experiments aren't possible.
  4. **Predictive**: forecast future events from historical data.
  5. **Causal**: the "gold standard". It generally requires randomized studies (e.g., A/B tests).
  6. **Mechanistic**: calculate the exact variable changes that cause exact behaviors. Seen in the physical sciences and engineering, and not suitable for complex systems.
  - When to use: use it to judge how strong a claim any report (vendor, analyst, internal) can support.
  - How: identify the highest level the study design and data actually support. Accelerate covers **levels 1–3 only** (plus classification), because it lacked the data for 4–6.
  - Why it works / failure mode: it stops you from over-reading a result. The failure mode is "fishing in the data", where exploratory correlations get read as drivers.
- **Theory-driven hypothesis testing (inferential design)**: state a hypothesis grounded in a well-developed, well-supported theory, design research to test it, collect data, and test it. More supporting evidence means more confidence.
  - When to use: use it whenever you want to claim X *impacts* or *drives* Y without a randomized experiment, such as in complex organizations that won't give up profits to fit control groups.
  - How: start from theory, then hypothesis, then instrument, then data, then a statistical test (multiple linear regression or partial least squares regression; see Appendix C).
  - Why it works: requiring a theory up front guards against spurious correlations found by chance. The authors' answer to the charge of confirmation bias is that science tests stated hypotheses rather than merely confirming them.
- **Classification (clustering) analysis**: depending on context and design, it can count as exploratory, predictive, or even causal. Enter the classification variables into a clustering algorithm and identify significant groups.
  - How (in this book): put the four measures (deployment frequency, lead time for changes, mean time to repair, change fail rate) into **hierarchical clustering**. High, medium, and low performer groups emerge.

## Key Concepts
- **Primary research**: the research team collects new data (e.g., the US Census, Accelerate, the State of DevOps Reports). It gives more control but costs more.
- **Secondary research**: uses data collected by someone else (e.g., book reports, case studies, some market reports). It is faster and cheaper but limited to existing data.
- **Qualitative research**: non-numerical data (interviews, blog posts, long-form logs, ethnography). It is rich for new areas but costly to analyze.
- **Quantitative research**: numerical data (system data, stock data, survey data on a scale). Survey research is not inherently qualitative.
- **Likert-type scale**: assigns numbers to responses, e.g., Strongly disagree = 1, neutral = 4, Strongly agree = 7.
- **Population vs. sample**: the population is the entire group of interest. The sample is a carefully defined and selected portion of it. Sampling must be sound for conclusions to generalize.
- **Correlation**: how closely two variables move together (or in opposition). It doesn't say why, and it can be due to a third variable or chance.
- **Pearson's r**: the strength of a linear relationship, from −1 to 1 (1 = move exactly together, −1 = exactly opposite, 0 = no correlation). It is the type used throughout the book.
- **Spurious correlation**: a high correlation by chance (Tyler Vigen's site).
- **Hierarchical clustering**: the clustering method used to derive the performer groups.

## Mental Models
- Think of "correlates" < "predicts" < "causes" as escalating claims. Map every finding in this book to "correlates" (exploratory) or "predicts/impacts/drives" (inferential), never to "causes".
- Use inferential predictive design when randomized experiments are impossible, as in real organizations.
- Think of exploratory analysis as idea generation, not the endpoint. It is the place for new hypotheses, not for conclusions about prediction or causation.
- Use descriptive reports as gauges of where an industry is and where it's trending. They are only as good as their sampling and data collection.

## Anti-patterns
- **Fishing in the data**: mining for correlations without theory. Your mind fills in a plausible story for spurious links.
- **Treating correlation as causation**: two variables moving together can be due to a third variable or chance.
- **Mislabeling outliers**: outliers must be confirmed as true outliers, not legitimate members of the group.
- **Trusting descriptive reports without scrutinizing their sampling**: a report that aims to represent a population must sample it carefully and discuss its limitations.
- **Claiming causation from survey or field data**: causal analysis generally needs randomized studies.

## Code Examples
```
Pearson's r ∈ [−1, 1]
  r =  1   → perfect positive linear correlation (move together exactly)
  r = −1   → perfect negative (move in exactly opposite directions)
  r =  0   → not correlated
Example (spurious): per capita cheese consumption vs. deaths by bedsheet tangling, r = 0.9471
```
What it demonstrates: how to read correlation values, and that a very high r can still be meaningless.

```
Likert-type scale: 1 = Strongly disagree ... 4 = Neutral ... 7 = Strongly agree
```
What it demonstrates: how the book's survey turns perceptions into quantitative data.

## Reference Tables
| Analysis type | Used in Accelerate? | Example in book / typical use | Statistical method |
|---|---|---|---|
| Descriptive | Yes | Demographics (country, org size, industry, job title, gender; Ch 10) | Summary statistics |
| Exploratory | Yes | Reported correlations | Pearson correlation |
| Inferential predictive | Yes | CD and architecture drive software delivery performance; software delivery performance affects organizational performance; culture affects both | Multiple linear regression, PLS regression |
| Predictive | No | Cost or utilities forecasting; needs historical data | n/a |
| Causal | No | A/B testing; needs randomized studies | n/a |
| Mechanistic | No | Physical sciences, engineering | n/a |
| Classification | Yes | High/medium/low performers | Hierarchical clustering |

**Why hierarchical clustering rather than k-means:**
1. There was no prior theory about how many groups to expect.
2. It shows parent-child relationships among clusters, which aids interpretation.
3. The dataset wasn't huge, so compute and speed weren't a concern.

Research scope: four years, primary, quantitative survey data, conducted by the authors. Research question: what capabilities drive software delivery performance and organizational performance?

## Worked Example
**Deriving the performer groups by classification.**
1. Take the four software delivery performance variables (tempo: deployment frequency and lead time for changes; stability: mean time to repair and change fail rate).
2. Feed them into hierarchical clustering with no preset number of groups.
3. Groups emerge with statistically significant differences. **High performers** are significantly better on all four measures. **Low performers** are significantly worse on all four. **Medium performers** are significantly better than low and significantly worse than high.
4. These clusters are the high/medium/low categories used throughout Part I (Ch 2). They then serve as groupings for comparisons like "2.2 times more likely to recommend" (Ch 10).

## Key Takeaways
1. Read every "drives/impacts" claim in Accelerate as *theory-based inferential prediction*, not proof of causation.
2. Before acting on any report, classify it on Leek's scale and discount claims that go beyond its level.
3. Start your own measurement with a theory and hypotheses, not by fishing through dashboards.
4. Treat correlations as prompts for hypotheses. Check for third variables and chance.
5. Use clustering to find natural performance groups when you have no prior on how many there are.

## Connects To
- **Ch 2**: the clustering of the four measures into high/medium/low performers.
- **Ch 3 / Ch 4 / Ch 5**: the inferential hypotheses tested (culture, CD, architecture leading to performance).
- **Ch 10**: an example of descriptive analysis (demographics).
- **Ch 13**: Likert-type data is turned into valid constructs through psychometrics.
- **Ch 14 / Ch 15**: why surveys are used, and how the data was collected.
- **Appendix C**: details of the statistical methods (regression, PLS).
- **External: Leek (2013), "The Elements of Data Analytic Style"**: the six-type framework.
- **External: Spurious Correlations (Tyler Vigen)**: the cautionary examples of chance correlation.
