# Chapter 9: The Ethical Implications of Vibe Coding

## Core Idea
Vibe coding is no excuse for low-quality work or for ethical shortcuts: any code you accept from an AI is *your* responsibility. Doing it responsibly means respecting four stakeholders: original creators (IP and attribution), colleagues (transparency and fairness), users (privacy, security, fair outcomes) and society (no harm from misuse).

## Frameworks Introduced

- **Golden Rules for Responsible AI Use** (eight practices):
  1. *Always keep a human in the loop.* Never let the AI work unsupervised. Review every line; never deploy raw AI output without human validation.
  2. *Take responsibility for your code.* It is never "the AI's fault." Be ready to justify every line. "I don't know; Copilot did that" is not an answer (this ties to Ch 3's rule "Never commit code you don't fully understand").
  3. *Protect users' privacy and ask for their consent.* Keep real user data out of prompts and use sanitized or synthetic data. Opt out of training on your inputs, or use on-prem tools for sensitive code. Get consent, and offer an opt-out, when user data reaches a model.
  4. *Comply with laws and regulations.* Track GDPR, the EU AI Act and similar rules, and work with legal and compliance. Never generate malware, phishing or exploits without ethical justification (pentesters under responsible disclosure are the exception).
  5. *Foster a responsible AI culture in your organization.* Hold ethics discussions and training, use a review checklist, name an ethics champion or committee, and read model cards.
  6. *Create guardrails and safety nets.* Fail safely rather than silently. Let users correct or override AI-driven recommendations. Degrade gracefully when an AI component misbehaves.
  7. *Document AI usage decisions within your team.* Keep a log of where you used AI suggestions and where you didn't, and why.
  8. *Proactively work to avoid bias, discrimination, and unfairness.* Is the AI feature multilingual or English-favoring? Do all team members have equal access to AI tools and training?
  - When to use: as the team charter whenever vibe coding is adopted.
  - Why it works / failure mode: rules 1 and 2 close the accountability gap that AI creates ("the tool wrote it"). Without them, every other rule becomes optional. The usual failure is complacency: shipping output nobody can explain.

- **Responsible AI Checklist** (Figure 9-1, three tiers by role):
  - When to use: before integrating AI-generated code into production, at prompt time, in review, and at org level.
  - How:
    1. *Prompting and code generation (developers):* no confidential data, PII or secrets in prompts. Check licensing of the output (no proprietary or GPL code unless allowed; use scanners such as FOSSA). Test for bias. Prompt for safe defaults and avoid insecure patterns (eval, unsanitized input). State constraints (style, framework, performance, compatibility).
    2. *Code review (developers and reviewers):* no unlicensed copyrighted material. Attribution given where due. Audit logic, language and naming for bias, especially in UI-facing layers. The code must not enable harm, misuse, manipulation or discrimination. Validate sanitization, data handling and logging, and check for leaked secrets. Prove correctness with unit tests, edge cases, error handling and coverage. Look for inefficient or power-hungry patterns. Check dependencies for unvetted libraries or license risks. Code must be readable, follow the style guide and drop unused code. Comments must explain the intent of AI-generated logic. Review feedback must be respectful, specific and empathetic.
    3. *Governance and process (organization):* license scanners, audit logs and provenance tracking. Ongoing ethics and AI-coding training. A vetted list of AI tools, with unapproved or high-risk tools banned. An incident process with escalation and whistleblower channels. Responsible-AI metrics (bias incidents, security findings, license violations). Community feedback and diverse perspectives through retros or external audits.
  - **How to use the checklist:** customize it to your domain, stack, risk tolerance and values. Start small ("Did we avoid sensitive data?", "Did we scan for licenses?"). Wire it into PR templates, CI pipelines and review tools. Revisit it **quarterly or after major incidents**. Treat it as a conversation starter, as pilots and surgeons do, not as a rigid rulebook.
  - Why it works / failure mode: it turns abstract ethics into checks attached to specific roles and moments. It fails when it is imposed whole and unadapted, or never revised.

- **"When in doubt, leave it out"** (suspicious-output protocol):
  - When to use: when output looks verbatim or near-verbatim (distinctive comments, author names, a recognizable algorithm).
  - How: (1) run a similarity or plagiarism check, or web-search unique strings. (2) If the source is identified, check that its license is compatible and attribute it. (3) Otherwise rewrite it in your own way, using the AI's answer as a guide only, or import the original library under its license. (4) If you still can't clear it, drop it.

- **Bias mitigation levers**: test with diverse examples, prompt for inclusivity, and hire diverse teams to review outputs.
  - When to use: for any user-facing component or any logic that handles human-related data.

## Key Concepts
- **De minimis / non-copyrightable snippet**: a few lines that lack enough originality to be protected. There is no agreed line-count threshold, so don't rely on it.
- **Fair use (US) / fair dealing**: weighed on four factors: purpose and character (commercial vs. nonprofit, transformative vs. duplicative), nature of the work, amount and substantiality used, and market effect. It is unsettled for code. *Google v. Oracle* covered API declaring code only.
- **"Open source ≠ public domain"**: code is under exclusive copyright by default. Licenses grant the permissions explicitly.
- **Derivative work risk**: feeding someone else's copyrighted code to an AI to fix or transform may make the output a derivative work that falls under the original license.
- **Ambiguous-license posture**: treat AI-generated code as if it were under an unclear license. Use it only if you're comfortable that it doesn't infringe and that you can meet any license obligations.
- **Human authorship requirement**: the US Copyright Office does not protect purely AI-generated works. Only the human's creative modifications or arrangement can be protected.
- **Transparency vs. attribution**: transparency means being open that AI was used. Attribution means crediting identifiable sources that AI-derived code came from.
- **Proxy variable**: a seemingly neutral input that correlates with a protected trait, for example a zip code standing in for race in credit scoring because of redlining.
- **Model card**: a "nutrition label" for a model. It covers what and which version, intended uses, out-of-scope uses, benchmark and fairness results across demographic groups, training-data limits and biases, and risks with mitigations.
- **Ethics champion / committee**: a person or group that tracks AI ethics and regulation, facilitates project discussions, curates training and answers questions. Responsibility for ethics stays shared.

## Mental Models
- Think of the AI as a tool like a compiler or word processor. The developer (or their employer) is the author, so the developer also owns every defect and every license violation.
- Think of AI disclosure as listing your frameworks and libraries. It gives context without diminishing your work. Using AI is no more "cheating" than using Stack Overflow or an IDE.
- The AI outputs whatever seems "normal" to it, and we shape that normal. If you don't ask for inclusivity, internationalization or fairness constraints, you'll get the majority pattern from the training data: Western, English-centric and male-defaulted.
- When AI touches users, design for its failure: safe failure, human override, graceful degradation.

## Anti-patterns
- **"The AI wrote it, not me"**: it shifts blame to a tool that has no accountability, and it disrespects the developers whose shared code trained it.
- **Stripping attribution via AI**: laundering Stack Overflow or OSS code through an AI to dodge credit rules erodes trust in the open knowledge ecosystem.
- **Deleting author comments** (such as "John Doe 2018") from generated snippets: this removes the original author's credit. Keep the comment or move it to a proper attribution section.
- **Pasting GPL/AGPL-matching output into proprietary code**: copyleft can "infect" the whole codebase.
- **Feeding real user records or others' copyrighted code into cloud prompts**: the first is a privacy breach, the second creates derivative-work exposure.
- **Disclaimer overload**: a bare "We used AI to code this" can frighten clients. Always pair disclosure with the quality measures you applied.
- **Breaking the model's content filters** to obtain malware or discriminatory algorithms.
- **Unexamined cultural defaults**: requiring First and Last Name fields, sample users who are all "JohnDoe," ignoring Unicode and multibyte scripts, or omitting needs as the original Apple Health app did with period tracking.

## Code Examples
```text
# Steering away from verbatim copying
Please provide an original implementation rather than one copied from a library.

# Steering toward inclusive output
Generate examples using a variety of names from different cultures.
Avoid gendered language in this code comment; use neutral phrasing or they/them pronouns.

# Disclosure in code/README (general -> specific)
This project was built with assistance from AI tools like ChatGPT.
Added a function to parse CSV (generated with ChatGPT's help, then modified).

# User-facing consent notice
This feature uses an AI service; your input will be sent to it for processing.
```
- **What it demonstrates**: ethics carried out through ordinary prompts and one-line disclosures. Asking for originality doesn't guarantee it, but it reduces outright copying.

## Reference Tables

| Situation | Action |
|---|---|
| Output matches a permissive-licensed (e.g., MIT) source | Include it with the attribution the license requires |
| Output matches GPL/AGPL code, project is closed | Don't include it. Rewrite from the idea or drop it |
| Output matches a known library | Depend on the library itself under its license |
| Output matches a known algorithm or paper | Cite the paper or project in a comment |
| AI produced something arguably creative (an approach, doc text) | Acknowledge the AI's contribution, for transparency |
| Debugging with production data | Use sanitized or synthetic data, an opt-out from training, or on-prem tools |
| An OSS project you contribute to | Check its contributor guidelines (some ban AI patches) and disclose AI generation to maintainers |
| A system that makes automated decisions about individuals (e.g., credit) | Inform users that results are automated (EU AI Act) and apply fairness constraints |

| Disclosure phrasing | Effect |
|---|---|
| "We used AI to code this product." | May trigger misplaced distrust |
| "We utilized advanced coding assistants to speed up development, and all AI-generated code was rigorously reviewed and tested to meet our quality standards." | Honest disclosure paired with the quality measures that justify trust |

## Worked Example
**Scenario: a suspicious Copilot suggestion in a proprietary codebase.**
1. *Trigger:* the suggestion is a well-known algorithm and carries a comment reading `John Doe 2018`. That is a near-verbatim signal.
2. *Investigate:* web-search a unique string from the snippet, or run a similarity checker. You find a match in an open source project.
3. *Read the license:*
   - **MIT:** keep the code, keep the author line or move it into a proper attribution section with a full citation, and satisfy MIT's notice requirement.
   - **GPL:** including it would require sharing derivative code in a closed product. Use the snippet only to understand the idea, then rewrite it your own way (copyright protects the expression, not the idea). Alternatively, prompt for "an original implementation rather than one copied from a library."
   - **It's a published library:** add the library as a dependency under its license instead of copying it.
4. *Can't clear it?* When in doubt, leave it out.
5. *Record it:* note in the team's AI-usage log what happened and why (Golden Rule 7). Make sure the PR's checklist items for licensing and attribution are ticked.

**Bias variant:** an AI-generated signup form requires both "First Name" and "Last Name." Testing with diverse inputs shows it rejects single names, which are common in some cultures. Relax the validation, then prompt the AI for culturally varied example data so the test fixtures stop defaulting to "JohnDoe."

## Key Takeaways
1. Own every accepted line. Review, test and understand AI code as if you had written it, because ethically and legally you did.
2. Treat AI output as ambiguously licensed. Check for verbatim matches, respect copyleft, attribute recognized sources, and when in doubt leave it out.
3. Never put secrets, PII, real user records or others' copyrighted code in prompts. Get consent when AI features process user data.
4. Disclose AI use honestly, and always pair the disclosure with the review and testing you performed.
5. Actively counter default bias: diverse test inputs, inclusive prompts, i18n and Unicode, no proxy variables, diverse reviewers.
6. Put responsibility into the workflow: a three-tier checklist in PR templates and CI, an ethics champion, model cards, an AI-usage log, and quarterly checklist reviews.

## Connects To
- **Ch 3 (The 70% Problem)**: the golden rule "Never commit code you don't fully understand" underpins Golden Rule 2.
- **Ch 4 (Beyond the 70%)**: the ethics of how AI changes workplaces, especially for junior developers.
- **Ch 8 (Security, Maintainability, Reliability)**: the security hygiene items in the checklist (eval, unsanitized input, secret leaks).
- **Ch 10 (Autonomous Background Coding Agents)**: human-in-the-loop and accountability matter more once agents act unsupervised.
- **Model Cards (Mitchell et al.)**: the standardized model-transparency document recommended here.
- **EU AI Act / GDPR**: transparency obligations for automated decisions and consent for personal data.
- **SPDX / license compliance scanning (FOSSA, OSI, FSF)**: tooling and bodies behind license-aware use of generated code.
