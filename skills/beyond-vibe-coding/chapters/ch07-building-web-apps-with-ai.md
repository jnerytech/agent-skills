# Chapter 7: Building Web Applications with AI

## Core Idea
Every layer of a full-stack web app can be built faster with an AI pair programmer: scaffolding, frontend, backend, database, integration and tests. The human still owns architecture, the frontend/backend contract, data-integrity rules, novel logic and final validation. AI speeds up execution. It does not replace understanding the requirements or ensuring quality.

## Frameworks Introduced
- **End-to-end AI-assisted web workflow**: Scaffold → Frontend → Backend → Database → Full-stack integration → Testing and validation, with the AI acting as an always-available pair programmer at each stage.
  - When to use: building a complete web app, not an isolated snippet or throwaway prototype.
  - How:
    1. **Scaffold by intent.** Describe the whole setup in one prompt (stack, folders, starter endpoint, dev proxy or CORS). Accept that you may need to finish some steps by hand, such as pasting a proxy setting.
    2. **Assert architecture first.** Decide these yourself: monorepo or separate repos, REST or GraphQL, which database, which ORM. Then tell the AI ("Also set up a basic Prisma schema for SQLite"). The AI follows your lead.
    3. **Frontend.** Generate components from descriptions of what they do and how they look. Describe styling in visual terms. Add data fetching and state handling one behavior at a time, and test after each addition.
    4. **Backend.** Build one endpoint at a time. Then add validation and business rules in plain language. Refactor into routers or modules as the code grows.
    5. **Database.** Brainstorm the schema with the AI, then confirm it using your domain knowledge. Generate ORM models or SQL DDL. Put the schema details and integrity rules into every database prompt.
    6. **Integrate.** Align the API contract and run a real end-to-end call. Have the AI change one side to match the other. Add loading and error states.
    7. **Validate.** Run unit, integration, end-to-end and manual exploratory tests, then a code review and a security scan.
  - Why it works / failure mode: AI is strongest at repetitive glue code, and web development is mostly glue. It fails at the seams. If each side is generated separately, contracts drift: different response shapes, key names or encodings. If the schema isn't stated, queries use guessed field names. Developers who skip validation ship flaws they don't understand.

- **Optimizing AI-human collaboration in full-stack development** (five strategies):
  - When to use: to set a steady working rhythm over a multi-day full-stack build.
  - How:
    1. **Use the AI for boilerplate; write any custom logic yourself.** Delegate CRUD APIs and standard components. Hand-write proprietary algorithms and tricky business rules, then ask the AI to review or test them.
    2. **Use AI to tackle your to-do list one item at a time.** Keep a list of features and bugs. Give the AI each item as its own targeted prompt ("Add password hashing using bcrypt in the POST /api/register route before saving the user").
    3. **Prompt AI to improve code quality as you go.** Once the code works, ask for "Refactor for readability" or "Optimize this function", then re-run your tests.
    4. **Use AI for cross-checking.** Bounce design choices off it like a colleague ("in-memory array or database? pros and cons?"). It may raise a point you missed, for example that an in-memory store won't sync across multiple server instances.
    5. **Use AI to coordinate with your team.** Have the AI document what was built. Tell the team which code is AI-generated, and keep normal code review for all AI-written code.
  - Why it works / failure mode: it splits work by comparative advantage, with the AI on repetition and you on novelty and judgment. The failure mode is the reverse: letting the AI improvise core business logic while you hand-type boilerplate.

- **Practical evaluation of model proficiency per stack**: how well a model handles a stack depends on how much of that stack was in its training data. JavaScript, Python and Java get strong support. Newer frameworks and less common languages give more variable results.
  - When to use: before relying on AI for a less common language or framework (Rails, Angular, niche or new libraries).
  - How: start with basic tasks, then raise the complexity. Check three things: (a) the code is idiomatic and follows the language's conventions, (b) the model recognizes frameworks and libraries without long explanation, (c) it suggests design patterns that fit the ecosystem. Weak support shows up as generic or outdated patterns. Vendor documentation rarely has language-level benchmarks, so run small experiments on your real stack (for example, does it know ActiveRecord patterns and RSpec?). Where support is weak, add more context to your prompts.

## Key Concepts
- **Scaffolding**: the initial setup of build tools, file structure, dependencies and dev plumbing (proxy or CORS), which the AI can generate from one natural-language description.
- **Programming by intent**: you state the result you want and the AI works out the steps. Project setup is a good fit for this.
- **Frontend/backend contract**: the agreed request and response shapes, key names and encodings between client and server. It is the most common place for AI-induced mismatches.
- **Data-integrity requirements**: domain rules such as cascade delete versus blocking deletion. You must state them explicitly, because the AI can't infer them for your domain.
- **Atomic transaction**: an all-or-nothing group of database operations with rollback on any error. Review AI-generated transaction code with care.
- **AI-assisted TDD / post hoc tests**: generating tests right after generating each feature, so rapid development doesn't lower quality.
- **Manual exploratory testing**: a human clicking through the app to find real-world breakage (Back button, odd action sequences) and to judge subjective UX, which the AI can't assess.
- **Unbundling of the programmer**: nonspecialists such as PMs building useful team-specific apps with AI (covered more fully in Ch 10).

## Mental Models
- Think of setup as a **conversation rather than a hunt through documentation**. Ask step by step ("What commands should I run?", "How do I connect React to this API in dev?") when you have no AI IDE.
- Use **one prompt that covers both sides** (or a project-wide-context IDE with frontend and backend files open) when generating code that must agree on a contract. Generating each side separately invites drift.
- Think of time saved on code as **budget to reinvest in tests**: the AI saved you time writing code, so spend part of it writing and running tests.
- Treat AI-written code **like code from any human colleague**: assume it can have bugs, and review and test it to the same standard.

## Anti-patterns
- **Letting the AI pick the architecture**: it follows whatever lead it is given. Without decisions from you on stack, repo layout, API style and database, you get unexamined defaults.
- **Generating components or endpoints in isolation without reconciling them**: prop shapes and JSON envelopes won't match (`{ success, data: [...] }` versus a bare array; `taskList` versus `tasks`; form-encoded versus JSON).
- **Database prompts without schema details**: the AI writes `user_id` when your schema uses `userId` or `customer_ref`. Conversation memory isn't enough, so repeat the schema in every complex database prompt.
- **Assuming the AI handles performance and integrity**: it may skip indexes on frequently queried fields, ignore query plans, and leave cascade behavior unspecified.
- **Accepting trivial AI tests**: AI-generated tests often assume the implementation or only cover the happy path. Name the edge cases you want tested.
- **Skipping validation because "the AI wrote it"**: one study found developers using AI were overconfident about their code's security even when it was worse than manual code. Older models produced SQL-injectable queries unless told not to.
- **Trusting framework idioms blindly**: check React `useEffect` dependency arrays. Specify Vue Composition API or Options API. For Angular, use the CLI for structure and AI to fill in parts.

## Code Examples
```javascript
// AI-generated response to: "Implement a transaction: when transferring money
// (POST /api/transfer), deduct from account A and add to account B, ensure it's atomic."
async function transferMoney(fromAccountId, toAccountId, amount) {
  const session = await db.startSession();
  try {
    await session.startTransaction();
    // Deduct from source account
    const sourceAccount = await Account.findByIdAndUpdate(
      fromAccountId,
      { $inc: { balance: -amount } },
      { session, new: true }
    );
    if (sourceAccount.balance < 0) {
      throw new Error('Insufficient funds');
    }
    // Add to destination account
    await Account.findByIdAndUpdate(
      toAccountId,
      { $inc: { balance: amount } },
      { session }
    );
    await session.commitTransaction();
    return { success: true };
  } catch (error) {
    await session.abortTransaction();
    throw error;
  } finally {
    session.endSession();
  }
}
```
- **What it demonstrates**: a well-specified prompt can produce correct transaction structure: both writes in one session, an insufficient-funds check, rollback on any error, and session cleanup. You still need to review edge cases and add logging.

```text
Integrity rules must be stated, never assumed. Pick one:
  "When a project is deleted, configure the database to cascade delete all related tasks."
     -> AI emits FK constraint with ON DELETE CASCADE
  "When deleting a project, first check for existing tasks and prevent deletion if any exist."
     -> AI emits app-level query-before-delete guard
```
- **What it demonstrates**: the AI can implement either policy correctly, but only after you choose one.

## Reference Tables

**What the AI can generate in each layer, and what you must check**

| Layer | Example prompt | What you verify |
|---|---|---|
| Scaffolding | "React (Vite) frontend + Express backend, REST to-do API with in-memory array, dev proxy" | Architecture choices are yours; finish any manual steps (proxy config) |
| Components | "React TodoList: takes items, shows title + completion checkbox" | Prop shapes agree across components |
| Styling | "Flex column, spacing, completed items gray and crossed out" | Tailwind knowledge varies by model |
| Data/state | "Fetch /api/to-dos on mount, store in state" | Endpoints and payloads match the backend |
| Endpoints | "Add POST /api/to-dos, accept JSON, return new to-do with ID" | `express.json()` middleware is present; refactor into routers as it grows |
| Validation | "Reject empty title or >100 chars with 400" | Behavior matches the rule (test it) |
| Multistep | "Create user and send welcome email via SendGrid" | Supply real keys; review transaction logic carefully |
| DB/ORM | "Sequelize models User/Project/Task with associations" | Field names, indexes, cascade rules, connection string |
| Integration | "Ensure frontend fetch matches Express route; fix discrepancies" | Run a real end-to-end call; compare browser console with server logs |
| Polish | "Loading indicator; show error on non-200" | Behavior when the API fails |

**Testing layers for AI-generated web apps**

| Test type | Tooling (from chapter) | AI's role | Human's role |
|---|---|---|---|
| Unit | Jest, Mocha, PyTest | Generate tests | Specify edge cases; reject trivial or implementation-coupled tests |
| Integration | Jest + Supertest | Scaffold endpoint tests | Check assertions match the contract |
| Frontend/E2E | Jest, Cypress, Playwright | Script user flows | Run them and keep them maintained |
| Manual exploratory | Human / QA | None | Real-world breakage, UX judgment |
| Code review | Teammates | Can document changes | Find subtle bugs and security issues |
| Security audit | Linters, SAST, AI review prompt | Lists vulnerabilities to use as a checklist | Harden the app (see Ch 8) |

## Worked Example
**Full-stack flow: contact manager app**
1. **Scaffold** a React frontend and Node/Express backend with one intent prompt.
2. **Frontend:** prompt for `ContactList` and `ContactForm` components, then wire up the API: "In ContactList, fetch contacts from /api/contacts on mount. In ContactForm, on submit, send a POST to /api/contacts with the form data, then update the list of contacts on success."
3. **Backend:** start with an in-memory array (or a database), then prompt for `GET /api/contacts` (list) and `POST /api/contacts` (add).
4. **End-to-end check:** add a contact through the UI. It doesn't appear. Find the gap: the POST route didn't return the new contact, and/or the form didn't refresh the list.
5. **Targeted fix prompt that covers both sides:** "After adding a contact, the backend should return the new contact object in the response, and the frontend should append it to the list without requiring a full reload." The AI changes the backend response and the frontend state update together.
6. **Repeat** for edit and delete. The AI handles the routine parts; your input describes what each feature should do.
7. **Result:** the author estimates about a week or two of junior-dev work done manually, versus a day or two with an AI codeveloper.

The chapter's composite case studies follow the same pattern:
- **Solo e-commerce site**: about 2 weeks of evenings, with AI writing about 70% of the code (repetitive UI, forms). The human handled Stripe configuration and branding.
- **PM-built internal dashboard**: Flask with read-only database credentials, Vue charts, and SQL written from chart descriptions. Not enterprise grade, which was acceptable for an internal tool.
- **Startup MVP**: one developer with Next.js, OAuth, cloud uploads and an NLP API delivered in a few months what would normally take a small team 4–6 months. It was hacky but demoable, and later hires refactored significant portions for scalability.

## Key Takeaways
1. Make the architectural decisions (stack, repo layout, REST or GraphQL, database) yourself before prompting. The AI will follow your lead.
2. Build iteratively: one component, endpoint or to-do item per prompt, and test after each one.
3. Treat the frontend/backend contract as something to manage explicitly. Specify response shapes on both sides, or reconcile them with a cross-file prompt after a real end-to-end call.
4. Put schema details and integrity rules (cascade or block, indexes) in every database prompt. The AI will not infer them.
5. Delegate boilerplate and write novel or proprietary logic yourself, then have the AI review and test it.
6. Reinvest the time AI saves into tests, and specify the edge cases yourself. Add manual exploratory testing, code review and a security scan.
7. AI gets you to the first stage quickly. Plan to invest in quality and refactoring as the app scales.

## Connects To
- **Ch 2 (Art of the Prompt)**: the specific, incremental prompts used at every layer here.
- **Ch 3 / Ch 4 (The 70% Problem / Beyond the 70%)**: AI writes about 70% (the e-commerce case). Integration, edge cases and quality are the human's 30%.
- **Ch 5 (Understanding Generated Code)**: reviewing transaction logic, hook dependencies and generated queries.
- **Ch 6 (AI-Driven Prototyping)**: this chapter takes the prototype to a complete application.
- **Ch 8 (Security, Maintainability, Reliability)**: moves from building to hardening, expanding the security audit and SAST.
- **Ch 10 (Autonomous Background Coding Agents)**: "unbundling of the programmer" and nonspecialists building team software.
- **Contract-first / consumer-driven contract testing**: formalizes the frontend/backend alignment problem (OpenAPI specs, Pact).
- **Test pyramid**: the chapter's unit, integration and E2E layering with manual testing on top.
- **ACID transactions**: the atomicity guarantee shown in the money-transfer example.
