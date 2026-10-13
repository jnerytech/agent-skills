# Chapter 8: Security, Maintainability, and Reliability

## Core Idea
AI speed does not lower the bar. More code in less time means more attack surface to audit, so pair "AI-accelerated development" with deliberate human verification at every stage: security audits, tests, performance checks, maintainability work, code review, and careful deployment. **Trust but verify.**

## Frameworks Introduced
- **Common Security Vulnerabilities in AI-Generated Code**: the recurring insecure patterns AI copies from public training code unless the prompt steers it away.
  - When to use: as a scan list for any AI output that touches input, auth, config, errors or dependencies.
  - How: check for (1) hard-coded secrets (`api_key = "ABC123SECRET"`), (2) SQL built by string concatenation, (3) unescaped output and XSS (`innerHTML`, raw `{{comment.text}}`), (4) broken authN/authZ (weak JWT secret, plain password compare, no owner check before delete), (5) insecure defaults (HTTP instead of HTTPS, `verify=false`, CORS open to everything, MD5/SHA1 for passwords), (6) error handlers that leak stack traces (`res.send(err.toString())`), (7) stale, unmaintained or **hallucinated** dependencies.
  - Why it works / failure mode: AI reproduces what is common, not what is safe. A 2023 study of Copilot found 25–33% of generated code (depending on the language) had potential CWEs. A 2022 study found that AI users felt *more* confident about security while writing *less* secure code. Counter that false confidence with checks and tests.
- **Security Audit Toolkit**: layered detection, both automated and human.
  - When to use: on every AI-generated change, run more often than in traditional development because code arrives faster.
  - How: (1) run SAST in CI (ESLint security plug-ins, Bandit, CodeQL, Semgrep); (2) use **a separate AI as reviewer**, either the same model switching to auditor mode or a *different* model for cross-review, and treat its findings as input, never as clearance; (3) do a human review with a security checklist; (4) run pen-testing and fuzzing (OWASP ZAP, OSS-Fuzz, malformed API payloads); (5) write security-focused unit tests; (6) **compensate for training cutoffs** by naming current standards in the prompt; (7) log errors instead of swallowing them, and sanitize the logs; (8) use security-focused tools such as taint analysis (Snyk); (9) don't ignore IDE warnings; (10) **slow down** for the audit.
- **"AI-accelerated development, human-accelerated security"**: once generation is fast, deliberately change gear for auditing. Scan in the IDE and in CI so security never falls behind the speed of generation.
- **AI output = a junior developer's code**: the author's repeated mental model. Give it the same careful review you would give a junior's PR.
- **Testing frameworks for AI-generated systems**: reliability requirements (fail-safe? mission-critical? financial loss?) don't change because AI wrote the code.
  - How: write tests immediately after each AI feature (or have AI draft them, treating them as suggestions rather than ground truth). Run the suite plus security scans in CI on every commit. Add property-based tests and fuzzing, load and performance tests, deliberate error injection, log and monitoring assertions (an uncaught exception during the test run counts as a failure), maintainability linting, and **integration tests across separately generated components**.
- **Maintainability lifecycle (While Prompting → Working with Code Output → Follow-Up)**:
  - While prompting: consistent coding standards (formatter plus naming conventions), and architectural patterns named explicitly in the prompt ("follow the repository/service pattern", "hexagonal architecture") so the codebase does not sprawl.
  - Working with output: refactor continuously (DRY out duplicates), test, avoid excessive complexity and AI-specific cleverness, and build in resilience and fallbacks (circuit breakers, retries with backoff, timeouts).
  - Follow-up: docs and comments (review them for accuracy), code reviews and team norms, TODO comments that track tech debt, learning from patterns the AI introduces, and alternating generation sprints with **"hardening sprints"**.
- **Reliable deployment practices**: Before and during deployment, automate CI/CD; use IaC (sandbox-test any AI-written Terraform); use staged/canary rollouts with a rollback plan; set up observability (error tracking, APM, availability pings); manage secrets and scan images; use blue-green or shadow testing. Ongoing: keep operational runbooks, test in production behind feature flags, audit regularly (including drift between migrations and code), keep humans in the loop (on-call), and run postmortems.

## Key Concepts
- **User enumeration**: specific login errors ("Incorrect password") confirm which usernames are valid, which turns guessing into a targeted attack. Always return "Invalid credentials".
- **Package hallucination**: the AI invents or misremembers a library name. An attacker can publish malware under names models commonly hallucinate, so verify every package on npm or PyPI before installing.
- **Timing attack**: inferring password correctness from response time. Prevent it with constant-time comparison functions.
- **Training cutoff gap**: the model doesn't know about vulnerabilities, patches or practices that appeared after training (e.g., OWASP Top 10 updates, Helmet for Express).
- **Property-based testing**: define invariants (sorted output, same elements, idempotence) and let the tool (Hypothesis, fast-check) generate inputs and counterexamples.
- **Assumption mismatch**: components generated separately each pass their unit tests but disagree on a convention (date formats, units). Only integration tests catch it.
- **Big ball of mud**: code with no structure or boundaries. AI removes the friction of adding features, which can speed this decay up.
- **Shadow testing**: send real production inputs to both the live version and a new one, show users only the live output, and compare the new version's results.
- **Developers as editors**: the reviewer acts as the editor who polishes AI "vibes" into code fit for production.
- **Hardening sprint**: a cleanup sprint after a burst of generation, used to refactor and document.

## Mental Models
- Think of runtime AI and AI-generated code as different problems. A chatbot is nondeterministic and needs tests with tolerance ranges. **Committed AI code is as deterministic as human code**, so traditional testing applies fully.
- Use the Frank Herbert warning ("Things we do without thinking — there's the real danger") as a trigger. Routine code the AI writes for you is exactly where you stop thinking, so apply the security-review mindset there on purpose.
- Make it work, then make it fast. AI gives you a correct solution first, so tune later, guided by profiling data rather than guesses. Leave non-critical code simple.
- AI implements patterns well but cannot choose them. Architectural judgment stays human.

## Anti-patterns
- **"The AI wrote it and the tests pass," so merge**: tests may not cover the case. Reason through the logic and try tricky inputs.
- **"We wrote it fast, let's merge fast"**: the review gets skimped. Use smaller, more frequent PRs instead.
- **An author who can't explain the code**: "the AI did it and I assume it's right" is a red flag. The team must understand everything in the codebase.
- **Bare "write secure code" prompts**: the AI falls back on dated knowledge. Name the current standard (e.g., the 2025 OWASP Top 10) and current tools (e.g., Helmet).
- **Treating an AI security review as clearance**: it produces false positives and misses subtle issues.
- **Catch blocks that swallow errors**: nothing is visible in production.
- **Premature optimization of AI code**: wasted effort. Optimize real bottlenecks only.
- **Overengineering and clever tricks**: unneeded abstraction layers and terse regex or comprehensions. Simplify them, or comment them.
- **Blaming the developer for an AI artifact in review**: it undermines knowledge sharing. Say something like "likely an oversight from the AI suggestion; let's fix it."

## Code Examples
```javascript
// Insecure AI output: plain-text compare + user enumeration, no rate limiting
app.post('/login', async (req, res) => {
  const { username, password } = req.body;
  const user = await Users.findOne({ username: username });
  if (!user) return res.status(401).send("No such user");
  if (user.password === password) {          // plain-text password comparison
    res.send("Login successful!");
  } else {
    res.status(401).send("Incorrect password");
  }
});

// After: "Improve the login route to use bcrypt to hash and compare passwords,
//         and ensure the password in the database is hashed."
const bcrypt = require('bcrypt');
app.post('/login', async (req, res) => {
  const { username, password } = req.body;
  const user = await Users.findOne({ username });
  if (!user) {
    return res.status(401).send("Invalid credentials");
  }
  const match = await bcrypt.compare(password, user.passwordHash);
  if (!match) {
    return res.status(401).send("Invalid credentials");
  }
  res.send("Login successful!");
});
```
- **What it demonstrates**: the "review and refine" loop. The naive output is insecure, and one targeted prompt fixes hashing and enumeration. Hash with `bcrypt.hash` when creating users, and add rate limiting and failed-attempt logging yourself.

## Reference Tables

**Human security review checklist for AI code**

| Area | Question |
|---|---|
| Authentication flows | Are they solid? |
| Data entering the system | Are inputs validated? |
| Data leaving the system | Are outputs sanitized and sensitive data protected? |
| External APIs | Are failures handled? Are keys exposed? |
| Database access | Is the ORM used safely, with parameterized queries? |
| Low-level code (C/C++/Rust) | Any overflows or memory misuse? |

**Performance smells in AI code → fix**

| Smell | Fix |
|---|---|
| Nested loops, O(n²) | Use a set or map for lookups (O(n)) |
| Concatenate + sort two sorted arrays, O(n log n) | Linear merge, O(n) |
| `loadAllRecords()` reads everything into memory | Stream, or process in batches/chunks |
| Unclosed file/DB handles, listeners never removed | Close in `finally`, remove listeners |
| Blocking I/O, CPU work on the main thread | async/await, worker thread, or background job |
| Expensive recomputation | Memoization or Redis cache |
| `SELECT *`, `findOne` in a loop (N+1), missing indexes | Select only needed columns, `WHERE id IN (...)`, add indexes in the migration |

**Deployment risk controls**

| Technique | What it buys |
|---|---|
| Canary (e.g., 5% of users) | Catch errors before everyone is affected |
| Blue-green | Full production test with instant switch back |
| Shadow testing | Validate a risky algorithm on real data with no user impact |
| Feature flags (TiP) | More granular than a canary, toggled per feature |
| Frequent small deploys | Easier to pinpoint a fault and quicker to roll back than big releases |

## Worked Example
**Catching a cross-component assumption mismatch (e-commerce):**
1. Prompt A: "Generate an order-processing module that handles international orders." It formats dates the US way: `12/25/2024`.
2. Prompt B, in a separate session: "Create a shipping-calculation service." Drawing on European examples, it expects `25/12/2024`.
3. Each module passes its own unit tests, so nothing looks wrong.
4. An integration test sends a real order through both modules. The order processor emits `12/01/2024` (Dec 1), and the shipping service reads it as Jan 12, so the delivery estimate is off by about 11 months.
5. Fix: agree on one contract (a single date format) for both modules, write it into the prompts for both, and keep an integration test that exercises the actual data flow.
Lesson: separately generated pieces carry different hidden assumptions, so integration testing matters more for AI-built systems than for hand-built ones.

## Key Takeaways
1. Treat every AI output as needing inspection. Review it as you would a junior's code: SAST in CI, a second AI reviewer, a human checklist, fuzzing and pen tests.
2. Put the security requirement in the prompt: parameterized queries, owner checks, generic auth errors, current OWASP guidance and current tools.
3. Write tests right after each AI feature, and treat AI-written tests as suggestions. Add property-based, load, error-injection and integration tests.
4. Name architectural patterns in prompts, run formatters and linters, refactor duplicates, track tech debt in TODOs, and schedule hardening sprints.
5. Profile before optimizing. Watch for AI's usual perf smells: O(n²) loops, N+1 queries, no streaming, no caching.
6. Deploy in small, frequent, staged releases with rollback, observability and secret management. Keep a human on call and run postmortems.

## Connects To
- **Ch 3 The 70% Problem**: security, edge cases and hardening are the hard last 30% that AI leaves behind.
- **Ch 4 Beyond the 70%**: covers code review and AI-generated tests first. This chapter makes them security- and reliability-specific.
- **Ch 5 Understanding Generated Code**: the "author must be able to explain it" rule applied in review.
- **Ch 7 Building Web Apps with AI**: XSS, auth and CORS pitfalls in real web stacks.
- **Ch 9 Ethical Implications**: licensing and duplicate-code detection (IP provenance).
- **OWASP Top 10 / CWE**: the vulnerability taxonomies to cite in prompts and audits.
- **The DevOps Handbook**: CI/CD, monitoring and small-batch deployment fundamentals.
- **GoF Design Patterns, Fundamentals of Software Architecture, Domain-Driven Design**: the architectural grounding for steering AI away from a big ball of mud.
