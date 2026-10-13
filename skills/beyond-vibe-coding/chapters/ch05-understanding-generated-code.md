# Chapter 5: Understanding Generated Code: Review, Refine, Own

## Core Idea
AI output is a fast first draft, not shippable code: compare it to your intent, review it like an intern's work, debug and refactor it until it looks like good code, then lock its behavior with tests. Only then is it truly *your* code, and you are responsible for it either way.

## Frameworks Introduced
- **Intent-to-Implementation Check**: before you run anything, read the AI's code against the prompt you gave and confirm it does what you meant.
  - When to use: right after every generation, even if you plan to test. Tests won't cover everything, and reading is faster for obvious issues.
  - How: (1) trace a typical input through the code, on paper or in your head; (2) for multi-part prompts ("do X and Y"), confirm every part is implemented; (3) flag functionality you didn't ask for (logging, extra params, progress prints) and keep it only if you can find a good reason for it; (4) check edge cases you care about: empty input, `None`, negatives; (5) find where an ambiguous prompt forced the AI to choose (e.g., print vs. return) and decide whether to accept that choice; (6) list its assumptions (see Majority Solution Effect).
- **The Majority Solution Effect** (the "Majority" Problem): models tend to produce the solution most represented in their training data, or the simplest one that fits. It works for the general case but may be wrong for yours. *Most common doesn't mean most appropriate.*
  - When to use: any time the prompt left out context such as performance constraints, project conventions, or input guarantees.
  - How: (1) identify assumptions (sorted list? valid input?) and decide whether a check is needed; (2) enumerate the alternatives you know (linear vs. binary search) and confirm the AI picked the one you want; if it didn't, re-prompt or change it; (3) look for context-specific edge conditions that generic examples ignore (integer overflow, globals your project bans). The tailoring is your job.
  - Why it works / failure mode: you have context the model lacks. The failure is accepting a "very educated guess" as a tailor-made answer, for example code that is correct on the usual case and breaks on the edge that matters to you.
- **Treat AI Code as an Intern's Work**: review it as if an intern wrote it and left for the day. Assume it's plausible but unreviewed, and integrate it properly.
  - How: do a readability pass (style, names, comments, structure), then scan the issue checklist in the Reference Table.
- **Six-Step Debugging Approach** (the AI code debugging cycle): (1) Reproduce the issue; (2) Locate the source (prints/debugger, trace where logic diverges); (3) Check the prompt against the code (was a requirement or edge case left out?); (4) Leverage the AI to debug: feed it the code plus the failing behavior, but don't fully trust its analysis; (5) Fix the code: fix it by hand if the fix is obvious, otherwise prompt with "fails on X (expected Y, got Z)"; (6) Test again for the fix and for regressions.
  - When to use: whenever generated code misbehaves at runtime or in tests.
  - Why it works / failure mode: it treats the AI as a colleague who can read code, not as an oracle. The cycle is to execute, capture the error, give the error context back to the AI, apply the fix, and iterate. The risk is looping on AI fixes without understanding them, so always ask *why* the bug happened.
- **Six-Step Refactoring Process** (Making AI Code Your Code): (1) Align with style guidelines (formatter/linter); (2) Improve naming and structure (rename `_helper1`, inline single-use functions unless they add clarity); (3) Remove unnecessary parts (unrequested `main` blocks or test code), or split one big function if that helps; (4) Add documentation in your project's docstring format; (5) Optimize if needed (check complexity for hot paths and large data); (6) Simplify if needed (collapse verbose if/else returns).
  - When to use: once the code is functionally correct.
  - Goal: a later reader shouldn't be able to tell that an AI wrote it. It should just look like good code.
- **Test-Driven Debugging**: write a few tests for critical functions so failing tests show directly what's wrong. This is faster than checking by hand for anything but the simplest functions.

## Key Concepts
- **Majority solution effect**: the AI's bias toward the most common or simplest solution in its training data, which is correct in general but not tailored to your context.
- **Intent vs. interpretation**: the gap between what you meant and what the AI chose when the prompt was ambiguous or incomplete.
- **Unrequested functionality**: extras the AI adds on its own (logging, parameters, progress prints), often artifacts of tutorial-style training code.
- **Telltale AI patterns**: heavy or oddly phrased comments, generic `i/j/k` names, and verbose general-case layout, all signs that a readability pass is needed.
- **Ask why, not just what**: when debugging, find the cause of the AI's mistake (usually an unclear prompt) so you can fix your future prompts and review habits.
- **Testing locks down behavior**: tests do more than find bugs. They guard against regressions when you or an AI change the code later.
- **Ownership**: the code is yours once you understand it, trust it, and have tests guarding it. After that, who wrote line 10 doesn't matter.
- **Provenance check**: verifying that large, obscure, or "too clean" output wasn't copied verbatim from a licensed source.

## Mental Models
- Think of AI output as **a very educated guess, not a tailor-made solution**. You supply the tailoring.
- Think of the AI as **an intern who left for the day**. The code is plausible, unreviewed, and your responsibility.
- Use the **AI as a debugging colleague** when the bug isn't obvious. Its second opinion can quickly spot things like a `len(arr)-1` boundary, but verify what it says.
- Think of tests as **a ratchet**. Every test you add is behavior that future AI edits can't silently break.

## Anti-patterns
- **Shipping AI output blithely**: unverified code becomes your liability, because AI won't take the blame when it fails.
- **Skipping the reading step because "tests will catch it"**: tests rarely cover everything, and many issues are faster to spot by reading.
- **Accepting the majority solution by default**: a linear search, a global variable, or numpy for a simple sum can be correct and still wrong for your project.
- **Trusting AI-generated tests or fixes blindly**: suggested asserts and tests are a starting point, not complete coverage. Creative edge cases still need human intuition.
- **"That's the AI's code; I'll ask the AI to change it"**: once integrated, edit it by hand whenever that's more efficient and maintainable.
- **Ignoring stale docs and comments**: the AI may revise the logic but leave a docstring that describes the old behavior.

## Code Examples
```text
# Debug prompt (step 5 of the debugging approach): state input, expected, actual
The above function fails on input X (expected Y, got Z). Please correct it.

# Refactoring prompt (step 5, optimize): name the pattern you want
Optimize this code to run faster by using a set instead of a list for lookups.

# Test-generation prompt
Write PyTest unit tests for the above function, covering edge cases.
```
- **What it demonstrates**: follow-up prompts work best when they are concrete and carry evidence (the failing input, expected vs. actual output) or the exact technique you want.

## Reference Tables

**Review checklist: potential issues in AI-generated code**

| Issue | What to look for | Fix |
|---|---|---|
| Off-by-one errors | Loop boundaries | Mentally run a simple case through the loop |
| Unhandled exceptions | Assumes the file opens or the input is well-formed | Add error handling |
| Performance pitfalls | Inner-loop membership checks on large data | Use a better structure (e.g., a set) |
| Library usage | Unwanted or unavailable dependency (numpy for a sum) | Switch to plain code or the library you intended |
| Inconsistencies | Docstring/comment disagrees with the code | Align them |
| Minor syntax issues | Rare, but possible in some languages | Fix them |
| Outdated APIs | A call you don't recognize | Check the docs for *your* library version |
| Placeholders | "Your code here" stubs | Fill them in |

**Test levels for AI code**

| Level | Purpose | Example |
|---|---|---|
| Unit | Each AI-provided function, especially edge cases | Prime checker: prime, nonprime, 1, 0/negative, large prime |
| Integration | AI code working in context with the rest of the codebase | Does the function actually store the right data in the DB? Chain producer → consumer |
| End-to-end | The whole workflow from start to finish | Send a test request to the AI-written web route; check format and error handling |

How much testing you need depends on how critical and complex the code is, but even simple asserts beat nothing.

## Worked Example
**Taking ownership of an AI-generated prime checker.** The full loop below is reconstructed from the chapter's running example.

1. **Intent check.** You asked for a prime checker. The output also prints `Checking 7…` for each number. This is unrequested functionality, likely a tutorial pattern from training data. Remove it, or prompt the AI to remove it. You also notice it *prints* the result instead of *returning* it because your prompt didn't specify the output, so decide which one you want.
2. **Edge cases and assumptions.** Does it handle 1, 0, and negatives? Is the input assumed to be an integer? If the prompt didn't say, add checks or define the expected behavior.
3. **Readability pass.** Delete a comment like `# check if number is prime` that sits above a self-explanatory `if`, keep any comment that explains non-obvious logic, and run Black.
4. **Debug, if a test fails.** Reproduce it with the failing input and trace the loop. If the cause isn't obvious, tell the AI: "fails on input X (expected Y, got Z)". Then ask *why* it happened. If the cause was an unspecified edge case, put that edge case in future prompts and in your review checklist.
5. **Refactor.** Bring it in line with your style, give it real names, remove any stray `main` or test block, add a docstring in your project's format, and simplify verbose if/else returns.
6. **Test.** Ask "Write PyTest unit tests for the above function, covering edge cases," then review what comes back. It should cover a prime, a nonprime, 1, 0/negative (with the behavior defined), and a large prime. Once everything passes, the behavior is locked down.
7. **Integrate.** Commit it, optionally noting in the message that AI helped. From now on, edit it like any other code.

## Key Takeaways
1. Read every generation against your prompt: check each requirement, the extras, the edge cases, and the choices the AI made where your prompt was ambiguous.
2. Assume the AI gave you the *majority solution*, and check whether a context-specific alternative (algorithm, conventions, overflow handling) is needed.
3. Debug in six steps: reproduce, locate, check the prompt against the code, ask the AI, fix, retest. Always ask *why* the AI erred so your next prompt improves.
4. Refactor until nobody could tell an AI wrote it: style, naming, removals, docs, optimization, simplification.
5. Cover AI code with unit, integration, and E2E tests scaled to how critical it is. Tests guard against future AI edits.
6. Check provenance for large or obscure outputs by searching a unique string online. Common algorithms like quicksort are usually fine.
7. You own the final code. After review and testing, it's just code in your project.

## Connects To
- **Ch 2 (Art of the Prompt)**: problems found in review, such as unspecified edge cases or output format, feed back into better prompts.
- **Ch 3 (The 70% Problem)**: review, debugging, and testing are the human work in the last 30%.
- **Ch 4 (Beyond the 70%)**: the review and ownership habits behind sustainable AI-assisted development.
- **Ch 6 (AI-Driven Prototyping)**: the same refine-and-own loop is needed when turning prototypes into production code.
- **Ch 8 (Security, Maintainability, Reliability)**: goes deeper on the risks this review checklist begins to catch.
- **Ch 9 (Ethical Implications)**: licensing and copyright provenance of AI output, and attribution in commits.
- **Code review practice**: review AI output with the same rigor you'd apply to a colleague's pull request.
- **Test-driven development / regression testing**: tests as a behavioral contract that locks down AI-generated code.
