# Chapter 3: The 70% Problem: AI-Assisted Workflows That Actually Work

## Core Idea
AI coding tools reliably deliver the first ~70% of a solution (boilerplate, routine, well-trodden patterns), but the final 30% (edge cases, architecture, maintainability, production readiness) still demands human expertise. Pick a workflow pattern deliberately (first drafter, pair programmer, or validator) and wrap it in team guardrails (the Golden Rules) so you get the speed without building "house of cards" code.

## Frameworks Introduced
- **The 70% Problem**: AI gets you ~70% of the way quickly; the last 30% becomes an exercise in diminishing returns, with fixes that take "one step forward and two steps backward."
  - When to use: To set expectations before adopting AI on a project, and to decide where human effort must go.
  - How: (1) Let AI own the *accidental complexity* (repetitive, mechanical, patterned code). (2) Reserve the *essential complexity* (Brooks's intrinsic difficulty) for humans: edge cases, unusual inputs, race conditions, performance limits, future requirements, architecture. (3) Assume edge cases are absent unless you asked for them explicitly. (4) Treat any polished-looking output as unverified, because AI's confidence far exceeds its reliability.
  - Why it works / failure mode: AI stitches together patterns that usually make sense; it doesn't understand the problem, invent new abstractions or take responsibility. The failure mode is accepting the 70% as "done". Non-engineers hit a wall because they can't reason about the remaining 30%.

- **Bootstrappers vs. Iterators** (two usage patterns):
  - **Bootstrappers** take a project from zero to MVP: start from a design or concept → AI generates a complete initial codebase → working prototype in hours or days → focus on rapid validation. Typical tools: Bolt, v0, screenshot-to-code.
  - **Iterators** use AI in daily development: completion and suggestions, complex refactoring, tests and documentation, AI as a "pair programmer." Typical tools: Cursor, Cline, Copilot, Windsurf. Less flashy, potentially more transformative.
  - When to use: Name which mode you are in. Bootstrapping is fine for early user feedback, not production. Iterating needs strong review habits.

- **What seniors do with AI output** (the hidden discipline): constantly (1) refactor generated code into smaller, focused modules; (2) add comprehensive error handling and the edge cases the AI missed; (3) strengthen type definitions and interfaces; (4) question its architectural decisions. AI speeds up their implementation; their expertise keeps the code maintainable.

- **Three workflow patterns that work**:
  - **AI as first drafter**: AI generates the initial code; developers refine, refactor and test it.
    - How: coordinate in stand-up about which tasks will use AI; agree on coding standards and prompting practices, and feed them to the tool (e.g., an "AI Usage Tips" section in the README); share prompts that worked; commit often and isolate AI changes; then manually review for modularity, error handling, tests, and documented decisions.
  - **AI as pair programmer**: developer and AI are in constant conversation, with tight feedback loops, frequent code review and minimal context provided.
    - How: (1) start a new AI session for each distinct task (keeps the context clean); (2) keep prompts focused and concise; (3) review and commit changes frequently; (4) keep feedback loops tight, correcting and refining as you go. Cross-check AI-drafted integration code against official docs. This also helps you learn the library.
  - **AI as validator**: developers write the initial code; AI analyzes it for bugs, security issues and best-practice violations, generates tests, and suggests improvements; developers review and apply them.
    - How: (1) use AI for the first scans to catch obvious issues; (2) put human review first for critical areas (complex functionality, UX, known AI limitations); (3) keep AI tools and human testers collaborating, with feedback loops in both directions.

- **The Golden Rules of Vibe Coding** (12 rules across three dimensions: human–AI interaction, integrating AI code into systems, team practice):
  1. Be specific and clear about what you want.
  2. Always validate AI output against your intent.
  3. Treat AI as a junior developer (with supervision).
  4. Use AI to expand your capabilities, not replace your thinking.
  5. Coordinate up front among the team before generating code.
  6. Treat AI usage as a normal part of the development conversation.
  7. Isolate AI changes in Git by doing separate commits.
  8. Ensure that all code, whether human or AI-written, undergoes code review.
  9. Don't merge code you don't understand.
  10. Prioritize documentation, comments, and ADRs.
  11. Share and reuse effective prompts.
  12. Regularly reflect and iterate.
  - When to use: As the team's working agreement for any AI-assisted work. Rule 9 is the one the author calls nonnegotiable.

## Key Concepts
- **Accidental vs. essential complexity**: Fred Brooks's split. AI handles the incidental, mechanical difficulty, but the intrinsic difficulty of the problem stays with humans.
- **Last-mile gap**: The final 30% (edge cases, architecture, maintainability) where AI output stops being sufficient.
- **"Wildly productive junior developer"**: Steve Yegge's framing of LLMs. Fast and enthusiastic, but prone to unworkable approaches that look polished.
- **House of cards code**: Code that looks complete but collapses under real-world pressure. The usual result when juniors accept AI output without refinement.
- **Knowledge paradox**: Seniors use AI to speed up what they already know how to do, while juniors use it to learn what to do, so the people who benefit least are the ones who need verification skills most.
- **Skill atrophy / dependency**: When code just "appears," you don't build debugging skill or pattern knowledge, so you keep going back to the AI to fix things. Autonomous agents make this risk much worse (Ch 10).
- **Cascading decisions**: With agents, each choice can look reasonable on its own while the combined effect steers the project somewhere unintended.
- **The lost art of polish**: The attention that makes software truly self-serve: clear error messages, slow-connection testing, real nontechnical users, discoverability, graceful edge cases.
- **[AI]-tagged commit**: A commit message marker for heavy AI involvement. It exists for traceability, not blame, and tells the reviewer to look harder at edge cases.

## Mental Models
- Think of AI as a **force multiplier, not a silver bullet**: a turbo boost on the repetitive 70%, with zero ownership of the hard 30%.
- Think of every AI output as a **draft from a supervised junior**. It's plausible, fast, and unverified until you've checked it against your intent.
- Use **frequent, isolated commits as the safety net** whenever AI writes code quickly. Granular history makes bisecting and reverting cheap.
- The more powerful the tool, the more fundamentals matter: stay the **architect of the system, not its operator**.

## Anti-patterns
- **"Two steps back" loop**: fix a small bug → AI suggests a plausible change → it breaks something else → ask AI to fix that → two new problems → repeat. It fails because nobody holds a mental model of the cause. It's whack-a-mole on code you don't understand. Even experienced iterators fall into it when they over-rely on AI suggestions.
- **Demo-quality trap**: the happy path impresses investors and social media, then real users hit confusing errors, crashing edge cases, stale UI states, missing accessibility, and slowness on weaker devices. These aren't minor bugs. They're the difference between software people tolerate and software people love.
- **"Looks good to me!" acceptance**: running with polished-looking AI code without checking it. The landmines show up weeks later.
- **Uncoordinated generation**: two developers each prompting for the same helper (e.g., `formatDate`) produces duplicate or conflicting implementations.
- **Monolithic AI commits**: mixing unrelated AI changes in one commit makes it hard to untangle them when something breaks.
- **Merging code you don't understand**: it kills maintainability and security, and it builds dependency.

## Code Examples
```text
# Isolate unrelated AI-produced changes into separate, tagged commits
git add src/components/WorkoutList.tsx
git commit -m "Optimize list rendering performance [AI-assisted]"

git add src/copy/workout.ts
git commit -m "Update UI copy for workout completion message [AI-assisted]"
```
- **What it demonstrates**: Golden Rule 7. One concern per commit, with a descriptive message and an AI tag, so each change can be reviewed, bisected or reverted on its own. (File paths are illustrative; the commit messages are the chapter's.)

## Reference Tables
| Pattern | Who writes first | Human role | Best for |
|---|---|---|---|
| AI as first drafter | AI | Refine, refactor, test, document | Team feature work with shared standards |
| AI as pair programmer | Both, in conversation | Steer continuously, review frequently | Solo devs, limited team capacity, learning a new library |
| AI as validator | Human | Write code, then triage AI findings | Code review, security scans, test generation, QA |

| | Human–AI pairing | Human–human pairing |
|---|---|---|
| Strength | Rapid generation, handles mundane tasks | Complex problem solving, nuanced brainstorming |
| Builds | Speed; solo productivity | Shared ownership, collective code understanding |
| Choose by | Project complexity, resource availability, goals | Same criteria |

| Usage pattern | Goal | Output quality | Hidden cost |
|---|---|---|---|
| Bootstrapper | Zero → MVP in hours/days | Good enough for early feedback, not production | Demo-quality trap |
| Iterator | Daily acceleration | Depends on review discipline | Two-steps-back loop if over-reliant |

## Worked Example
**Scenario: a team adopts "AI as first drafter" on a fitness app.**
1. **Coordinate up front (Rule 5).** In stand-up, two developers find that both of their features need a date-formatting utility. Instead of each one prompting for a `formatDate` helper and ending up with two similar functions, one says "I'll generate a date utility we can both use."
2. **Steer the tool with team standards.** The README has an "AI Usage Tips" section, for example "We use functional components only" and "Prefer using Fetch API over Axios". Developers include these in their prompts so the generated code stays consistent.
3. **Share what works (Rule 11).** Developer A gets a great result for a complex component and posts the prompt in the issue tracker or team chat so Developer B can reuse it.
4. **Generate, then commit granularly (Rule 7).** An agent asked to optimize performance also changes some UI text. The developer splits this into two commits: `Optimize list rendering performance [AI-assisted]` and `Update UI copy for workout completion message [AI-assisted]`.
5. **Review like a senior (Rules 8–10).** Before merging, refactor into focused modules, add error and edge-case handling, tighten types, question the architecture, write tests, and record key decisions (ADRs). The `[AI-assisted]` tag tells the reviewer to check edge cases extra carefully.
6. **Close the loop (Rules 6, 12).** Share warnings in team discussion (e.g., "Copilot suggests an outdated library for X, so be careful") and revisit the workflow regularly.

## Key Takeaways
1. Expect AI to deliver ~70%. Plan human time for edge cases, architecture and maintainability, and ask for edge cases explicitly.
2. Choose one workflow pattern (first drafter, pair programmer, validator) and experiment with it systematically.
3. Break the "two steps back" loop by understanding the root cause before you prompt again. Never merge code you don't understand.
4. Commit frequently, one concern per commit, and tag heavy-AI commits for extra review.
5. Put all code, human or AI, through the same review, and document the rationale (comments, ADRs).
6. Build team infrastructure: shared standards fed to the AI, a repository of proven prompts, and AI usage discussed in stand-ups.
7. Polish (errors, accessibility, slow devices, real users) is what separates a demo from a product, so budget for it.

## Connects To
- **Ch 1 What Is Vibe Coding**: the bootstrapper mode is vibe coding's natural habitat, and this chapter marks where it stops being enough.
- **Ch 2 Art of the Prompt**: Golden Rule 1 (be specific) and prompt sharing build on prompting technique.
- **Ch 4 Beyond the 70%**: the durable human skills (system design, debugging, architecture) that cover the last 30%.
- **Ch 5 Understanding Generated Code**: the prerequisite for "don't merge code you don't understand."
- **Ch 8 Security, Maintainability, Reliability**: the AI-as-validator scans and the review discipline.
- **Ch 10 Autonomous Background Coding Agents**: where skill atrophy and cascading decisions become acute.
- **Fred Brooks, "No Silver Bullet"**: the accidental vs. essential complexity distinction.
- **Pair programming (XP)** and **Architecture Decision Records**: the established practices the chapter adapts for AI.
