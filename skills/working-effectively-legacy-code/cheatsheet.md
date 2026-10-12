# Cheatsheet — Working Effectively with Legacy Code (Feathers)

The author's judgment, distilled to decisions. For full procedures see chapters; for the technique catalog see ch25.

## First principles (decision rules)
- **No change without a covering test** — if you can't test it, your first job is to make it testable, not to make the change.
- **Legacy code = code without tests.** Quality of writing is irrelevant; without tests you can't change it safely.
- **Change a little, preserve a lot** — the risk is the behavior you *keep*, not the line you edit.
- **Feedback in a minute beats feedback overnight** — drive toward fast, localized unit tests.
- **Break dependencies conservatively** — when getting the first test in, modify as little as possible; clean up *after* tests exist.

## The loop (always)
1. Identify change points → 2. Find test points → 3. Break dependencies → 4. Write tests → 5. Make changes & refactor. *(Ch 2)*

## Is this a unit test? (smell)
NOT a unit test if it: talks to a **DB**, crosses a **network**, touches the **filesystem**, or needs **special env setup**. A "unit test" taking 1/10s is **slow**.

## Why am I breaking this dependency?
- Can't **see** the effect → **Sensing** → use a **Fake** (or Mock if many).
- Can't **run** the code at all → **Separation** → extract interface / inject.

## Which seam? *(Ch 4)*
| Language situation | Prefer |
|---|---|
| OO code | **Object seam** (default — explicit, maintainable) |
| C/C++, pervasive deps, no object seam | Link seam or Preprocessing seam (reserve for these) |
Every seam needs an **enabling point** — if there's no place to choose the behavior, it's not a seam.

## Adding a feature — which technique? *(Ch 6, 8)*
```
Need the change tested, class is testable? ........... TDD directly
Can't test the class now, adding a sub-step? ......... Sprout Method
  ...and can't even instantiate the class? ........... Sprout Class
Adding behavior BEFORE/AFTER existing work? .......... Wrap Method
  ...behavior fully independent / class too big? ..... Wrap Class (Decorator if many callers)
A subclass cleanly expresses the difference? ......... Programming by Difference (then refactor away)
```

## "I can't get this CLASS into a harness" → *(Ch 9 / 25)*
| Tell | Technique |
|---|---|
| Irritating constructor param | Extract Interface / Adapt Parameter |
| Object `new`-ed in constructor | Parameterize Constructor; Extract & Override Factory (≠C++); Extract & Override Getter or Supersede Instance Variable (C++) |
| Global/Singleton dep | Introduce Static Setter / Encapsulate Global References |
| Construction is a blob | Extract & Override Getter; Supersede Instance Variable |

## "I can't run this METHOD in a harness" → *(Ch 10 / 25)*
- Side-effecting call → **Extract and Override Call** (one call) / **Subclass and Override Method** (behavior in a method).
- Object made in the method → **Parameterize Method**.
- Private method blocks you → test through a public one; if too complex, make it protected or move to a new class. **Don't** loosen access just for convenience without thought.

## Monster method? *(Ch 22)*
- **Bulleted** (sequential, flat) → extract sequences; easier.
- **Snarled** (deep nesting) → Introduce Sensing Variable, Extract What You Know, or Break Out Method Object.
- **Lean on automated refactoring tools**; keep indentation as your map.

## Don't understand it? *(Ch 16)* → **Scratch Refactor and THROW IT AWAY.** Sketch. Mark up a printout. Delete dead code.

## Editing without good tests — stay safe *(Ch 23)*
- **Lean on the Compiler**: break a declaration on purpose → fix every error it lists → undo the break.
- **Preserve Signatures**: copy whole parameter lists verbatim.
- **Single-Goal Editing** + **Hyperaware Editing** (pair / TDD).

## Smells → what it means
- Touching the **same code all over** → duplication; remove it to cut change points *(Ch 21, Open/Closed)*.
- Class keeps **growing** → SRP violated; **Extract Class** to stop the bleeding *(Ch 20)*.
- App is **all API calls** → Skin-and-Wrap (small API) or Responsibility-Based Extraction (large API) *(Ch 15)*.
- **Build takes forever** → invert dependencies, Extract Interface to cut compile coupling *(Ch 7)*.
- Team feels **overwhelmed** → pick high-churn/high-value areas, grow tested islands, celebrate small wins *(Ch 24)*.

## Characterization test (the legacy testing move) *(Ch 13)*
1. Write a test asserting a value you *guess*. 2. Run it; the failure reveals the **actual** behavior. 3. Change the assertion to expect the real value. 4. Repeat to pin behavior. 5. Found a "bug"? Check who depends on it **before** fixing.

## Where to write tests *(Ch 11, 12)*
Sketch effects → find an **interception point** → prefer a **pinch point** (one test covers many classes) → start there, then push tests down to units.
