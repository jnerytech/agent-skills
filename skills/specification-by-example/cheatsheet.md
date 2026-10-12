# Cheatsheet — Specification by Example

The decisions Adzic would make. One line each; act, don't recite.

## Decision rules

- **A requirement arrives as a solution** → ask "how would that be useful?" and "what's an alternative?" — derive scope from the *goal*, because solutions disguise assumptions.
- **About to write a yes/no example** → reject it; the underlying concept isn't defined yet — make the example concrete and quantified.
- **Tempted to invent test data** → don't; get real examples from customers — invented data hides real edge cases (esp. data-driven projects).
- **Example is exploding into every combination** → stop; keep only the **key examples** that pin the rule — exhaustive cases are tests, not documentation.
- **Spec reads like UI steps / a recorded script** → rewrite — "scripts are not specifications"; describe business intent, not mechanics.
- **Setup is cluttering the spec** → push defaults into the **automation layer**; state only what matters to the rule.
- **Test goes through the UI to check business logic** → move it **below the skin**; check UI logic only with UI specs.
- **Business logic appears in the automation layer** → remove it; the layer is glue, not a second implementation.
- **A test waits on a timer/sleep** → wait for an **event** instead — timers cause flakiness.
- **Sign-off requested** → sign off on **scope** or **exported living documentation**, not individual specs.
- **Adopting in a change-resistant org** → avoid the word "agile"; sell it as "a better way to do acceptance testing".
- **Docs are painful to organize/read** → "listen to your living documentation" — the pain points at a design or scope problem.

## Choosing a collaboration model (Ch 6)

| Situation | Use |
|---|---|
| Just starting with SBE | Big, all-team **workshops** |
| Domain needs frequent clarification | Small **Three Amigos** workshops |
| Mature product, stable team | **Pair-writing** |
| Analysts write tests | Devs **review tests** before iteration |
| Stakeholders readily available | **Informal conversations** |
| Remote stakeholders | Detailed prep + review up front |

## The four qualities of a good example (Ch 7)

| Quality | Tell it's missing |
|---|---|
| **Precise** | yes/no answers, abstract "any valid X" |
| **Complete** | reviewer asks "what about…?" |
| **Realistic** | data is made-up / round numbers |
| **Easy to understand** | needs a paragraph to explain one row |

## Three-layer automation model (Ch 9)

```
Specification  (business language — never changes for the tool)
    ↓
Automation layer (glue/fixtures/defaults — first-class code, no business logic)
    ↓
System under test (drive below the skin, along boundaries)
```

## Adoption warning signs (Ch 4) — smells

- Tests that **change frequently** → specs coupled to implementation.
- **Boomerangs** (stories returning) → sign-off without shared understanding.
- **Organizational misalignment** → teams optimizing locally, not for the goal.
- **Just-in-case code** → scope not driven by goals.
- **Shotgun surgery** → one change ripples across many specs → poor structure.

## The 7 patterns as a loop

goals → **scope** → collaborate → **examples** → refine → **automate** → validate frequently → **living documentation** → (feeds next goals)

## Defaults & rules of thumb

- Spec format: **descriptive title + one-sentence goal + Given-When-Then examples**.
- Keep specs in **version control** alongside code.
- One artifact = spec **and** test **and** documentation — if it's only a test, you've lost the payoff.
- Don't make **test automation the end goal**; the goal is shared understanding + living documentation.
