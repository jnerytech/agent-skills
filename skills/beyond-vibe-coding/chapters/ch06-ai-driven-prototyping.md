# Chapter 6: AI-Driven Prototyping: Tools and Techniques

## Core Idea
AI compresses idea-to-working-model from days to hours: state the intent, let the AI write the first draft, then refine it in fast conversational loops. A prototype is a first draft, not the product. Turning it into production code takes a deliberate change of mindset toward disciplined engineering, with a human directing every step.

## Frameworks Introduced
- **Fidelity vs. Control**: the two dimensions on which every AI prototyping tool trades off. *Fidelity* is how closely the output matches your input or intention. *Control* is how far you can guide and modify the generation.
  - When to use: picking a prototyping tool or approach.
  - How:
    1. Name the prototyping goal: fast visual implementation, a functional demo, or a technical exploration.
    2. Choose by goal. A designer validating an interaction pattern should favor fidelity and speed and give up control over implementation. A developer testing technical feasibility should favor control and transparency, even if that means more manual work.
    3. Map goal to category. **Screenshot-to-code** tools (e.g., v0) give high visual fidelity, but the code may not match your architecture. **Conversational full-app builders** (e.g., Lovable, Bolt.new) scaffold whole apps from loose prompts and return generic code. **AI-augmented IDEs** (e.g., Cursor, Windsurf, Cline) give the most control, with either auto-applied changes for experimentation or explicit acceptance for careful iteration.
    4. Whatever the tool, check its code. Most tools let you inspect it.
  - Why it works / failure mode: tools change fast, but this trade-off and the need for human oversight stay the same. The usual failure is picking a high-fidelity black box when you need a specific architecture, specific performance work, or integration with an existing codebase.

- **The 80% Prototype**: no AI tool produces production-quality code without oversight. Expect output that is good enough to test concepts and show stakeholders. The missing 20% is usually security hardening, performance optimization, error handling and architectural refinement.
  - When to use: setting expectations for any AI-built prototype and planning the work after it.
  - How: treat the output as throwaway or scaffolding. Even during prototyping, do a quick review for exposed API keys and insecure data handling so those problems don't spread into later stages.

- **Iterative Refinement Loop** (Figure 6-1): Generate → Review & run → Refine prompts → Rinse and repeat.
  - When to use: going from a baseline prototype to the version you have in mind.
  - How:
    1. **Initial generation**: write one intent-level prompt for the core feature.
    2. **Review and run**: run the code yourself and note what is plain, missing or wrong.
    3. **Refine prompts**: ask for one specific change per prompt. The tool keeps context, so the AI edits the right places.
    4. **Rinse and repeat**: check each result and correct regressions with targeted prompts ("sorting is backward, sort ascending by default").
  - Why it works / failure mode: each cycle takes seconds, so a dozen iterations fit in an hour. Broad changes such as restyling or adding a feature gain the most. The conversation itself becomes the development log. Vague prompts ("make it look nicer") are the main failure. You stay the director: when the AI's approach is correct but not what you expected, either accept it if it doesn't hurt the prototype's goals or redirect it.

- **Prototype-to-Production Transition**: a fixed checklist for hardening, with the AI as a quality assistant instead of a feature generator.
  - When to use: once the prototype has done its job (design validated with users, or feasibility proven).
  - How:
    1. **Architecture/structure**: split single files into modules, components or MVC. Either start fresh and use the prototype as a reference, or refactor it step by step with AI-generated tests as a safety net.
    2. **Error handling & edge cases**: go through each feature's failure modes. Prompt: "What are potential error cases for this feature and how to handle them?"
    3. **Performance**: find naive algorithms that only work on small datasets. Profile first, then ask the AI to optimize the hot spot.
    4. **Security**: look for unparameterized SQL, leaked secrets and weak auth or data handling. Run static analysis or security tests, or prompt "scan this code for security issues."
    5. **Documentation**: once the code is clean, have the AI draft a README or API doc, then review it.
    6. **Testing**: write unit tests for core logic and integration tests for main flows. Generate them with AI, then run and adjust them.
    7. **Replace hacks**: swap in-memory or quick-and-dirty parts for real ones (e.g., "Integrate an SQLite database for storing the tasks instead of an in-memory array"), using the AI's output as a starting point.

- **Stay Focused (North Star)**: write down the single goal of the prototype and resist gold-plating.
  - When to use: whenever adding "one more thing" feels tempting.
  - How: state the goal in one sentence ("Demonstrate that users can upload a CSV and get a chart to test viability"). Stub anything outside it, such as login or payments, and let the AI generate a fake flow.

## Key Concepts
- **Programming by intent**: you describe what the prototype should do or look like, and the AI works out the implementation.
- **Throwaway code**: prototype code written for speed and experimentation, not maintainability. That is acceptable as long as you plan to refactor or rewrite it.
- **Screenshot-to-code**: turning screenshots, sketches or Figma designs into working HTML/CSS/React.
- **Fidelity**: how closely generated output matches your input or intention.
- **Control**: how much you can guide and modify the generation process, from a black box to iterative dialogue and direct editing.
- **80% prototype**: functional enough to demo, but missing security, performance, error handling and architecture.
- **Context persistence**: the tool remembers the app's purpose and earlier instructions, so the conversation becomes the development log.
- **Scope creep**: easy AI feature-adding grows the prototype until it is trying to be the final product.
- **"Things to address if we move forward" list**: a running record of shortcuts (mock data, emails logged to the console), backed by `// TODO` comments.
- **Sunny-day scenario**: the happy path that prototypes cover while ignoring failures.

## Mental Models
- Think of AI prototyping as **brainstorming with an assistant**, not grinding out boilerplate. It is conversational, high-level and fast.
- Use **prototype mode** to explore, then switch to a **disciplined engineering mindset** to productionize. In the second mode, judge every AI suggestion critically, because stability and quality now come first. This is the senior mindset from Ch 4: knowing what to accept and what to fix.
- Think of a prototype as a **tool for learning**. When it has answered its key question, either harden it or put it aside and keep the lessons.
- Use the **AI for the tedious parts** (basic UI, form handling, sample data) so your attention goes to the unique feature being tested.

## Anti-patterns
- **Vague refinement prompts** ("Make it look nicer"): the AI has no concrete direction. Say exactly what you want: "Apply a light theme with a blue header and increase the font sizes for readability."
- **Shipping the prototype as-is**: AI prototypes cover the sunny day and often contain unparameterized SQL, missing auth and missing input validation. A 2021 study found about 40% of AI-generated code had potential vulnerabilities.
- **Gold-plating / scope creep**: building login, payments and similar systems at the prototype stage. It wastes time and makes the prototype harder to throw away or rework.
- **Forgetting temporary shortcuts**: mock data, fake email and local files get missed at integration time unless you track them.
- **Skipping review "because it's just a prototype"**: exposed API keys and insecure data handling carry over into later stages.
- **Accepting AI architecture without question when productionizing**: state management and component hierarchy need your own best-practice judgment.

## Code Examples
```text
Create a simple HTML page for a sign-up form with fields for Name, Email,
and Password, and a Submit button. Make it look presentable with basic styling.
```
The result was one HTML file with inline CSS: a centered column form (max-width 400px), `required` inputs of type `text`, `email` and `password`, and a green "Create Account" button.
- **What it demonstrates**: programming by intent. One outcome-level prompt produces a usable first draft that you can open in a browser and refine.

```text
// Refinement prompts, each one specific and single-purpose:
Make the expense list sortable by amount or date.
Add some color styling, maybe use a modern CSS framework.
Validate the form so you can't add an expense without a name and amount.
The sorting is backward—please sort ascending by default.
The new color scheme is good, but make the header dark blue instead of black.
```
- **What it demonstrates**: the refinement loop. Each prompt names one concrete change, and corrections fix regressions without starting over.

## Reference Tables
| Tool category | Example tools | Fidelity | Control | Best for |
|---|---|---|---|---|
| Screenshot/design-to-code | Vercel v0 | High (visual) | Lower; code may not match your architecture | Designers turning sketches/Figma into UI fast |
| Conversational full-app builders | Lovable, Bolt.new | Looser; functional but generic | Medium (dialogue) | Non-coders scaffolding a whole app quickly |
| AI-augmented IDEs | Cursor, Windsurf, Cline | Depends on prompts | High; auto-apply vs. explicit accept | Developers testing technical feasibility, existing codebases |

| Prototype shortcut | Production fix |
|---|---|
| Everything in one file / script tags + CDN | Modules, components, MVC; build system + npm |
| Happy path only | Systematic failure-mode review, validation |
| In-memory arrays, mock data | Real DB (e.g., SQLite) and services |
| No auth | Auth (e.g., JWT), hashed passwords, secure tokens |
| Load everything into memory | Streaming / optimized algorithms |
| Emails logged to console | Real email service (`// TODO` tracked) |
| No docs/tests | AI-drafted, human-reviewed README; unit + integration tests |

## Worked Example
**Jane's CSV-to-charts app, end to end.** In one weekend, Jane builds a prototype with an AI assistant: a Node.js API plus a single-HTML frontend that uploads CSVs and renders charts. A few potential users like it, so she productionizes it.
1. **Hardening the backend**: the API had no auth, so anyone could upload. She has the AI scaffold JWT-based auth, then reviews it herself to confirm passwords are hashed and tokens are secure. She adds input validation to the upload endpoint, which the AI had left out, combining AI-suggested code with her own changes.
2. **Refactoring the frontend**: the single HTML file loaded dependencies from a CDN via script tags. She asks the AI to move it to a build system and npm, then to restructure it as React components (the chart code becomes `<Chart>`). She keeps control of state management and component hierarchy herself.
3. **Testing and checking performance**: she writes unit tests for CSV parsing and data transformation. She asks the AI, "What edge cases should I test for CSV parsing?", gets cases such as empty fields and irregular columns, and adds them to her tests. She notices the prototype loaded whole files into memory, which could crash on large inputs. She rewrites that part to stream and uses the AI only to double-check the stream logic.
4. **Polishing the UI**: she asks the AI for a responsive layout. It adds Bootstrap and standard pieces (navbar, loading spinner), and she fine-tunes the CSS by hand.

**Result**: the app is production-ready in about two weeks, much faster than building from scratch. The AI sped up both the prototype and the transition, but her review, restructuring and tests are what made it production quality.

## Key Takeaways
1. Prototype by intent: describe the outcome, let the AI draft it, run it right away, and refine in seconds-long loops.
2. Choose tools on **fidelity vs. control** according to your goal (visual, functional demo, or technical exploration), not on the brand.
3. Expect an **80% prototype**. Do a quick security scan even on throwaway code, at minimum for exposed keys and insecure data handling.
4. Make refinement prompts specific and single-purpose, and stay the director: accept or redirect the AI's implementation choices.
5. Write down a one-sentence North Star goal, stub everything outside it, and avoid gold-plating.
6. Keep a "things to address if we move forward" list plus `// TODO`s for every shortcut.
7. When productionizing, switch to disciplined mode: restructure, error handling, performance, security, docs and tests, with the AI as a reviewed assistant.

## Connects To
- **Ch 1 (What Is Vibe Coding)**: programming with intent, and using the AI to explain code and draft docs.
- **Ch 2 (Art of the Prompt)**: specific refinement prompts depend on prompt-engineering skill.
- **Ch 3/4 (The 70% Problem / Beyond the 70%)**: the AI handles about 70% of a prototype, and the senior mindset decides what to accept and what to fix.
- **Ch 5 (Understanding Generated Code)**: test thoroughly before and during the move to production.
- **Ch 7 (Building Web Apps with AI)**: moves from exploratory prototyping to systematic full-scale development.
- **Ch 8 (Security, Maintainability, Reliability)**: common flaws in AI-generated code (SQL injection, naive algorithms) that must be fixed when productionizing.
- **Throwaway prototyping / "plan to throw one away" (Brooks)**: a prototype is for learning and is not the base of the product.
- **YAGNI / MVP scoping**: the North Star goal and stubbing mirror lean scope control.
