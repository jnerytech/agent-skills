# Chapter 4: The Seam Model

## Core Idea
A **seam** is a place where you can alter behavior without editing in that place — and every seam has an **enabling point** where you choose which behavior runs. Seeing code as a web of seams (not a flat sheet of text) is how you find the testing opportunities already present.

## Frameworks Introduced
- **Seam** *(the book's most important concept)*: a place where you can alter behavior in your program **without editing in that place**.
  - **Enabling point**: every seam has one — the place where you decide to use one behavior or another. A seam with no enabling point is not a seam.
  - Rule: source code must be identical in test and production; you change behavior only via the enabling point.
- **The three seam types** (found by walking the build pipeline — each step exposes a seam):

  | Seam | Where behavior varies | Enabling point | When to prefer |
  |------|----------------------|----------------|----------------|
  | **Preprocessing seam** | text before compile (`#define`, `#include`) | a preprocessor define (e.g. `TESTING`) | C/C++ only; pervasive deps, no better option |
  | **Link seam** | resolved symbols at link/classpath | build script / classpath | replacing a third-party library littered through code |
  | **Object seam** | which method a call dispatches to | where the object is created / passed in | **default in OO languages** — most explicit, most maintainable |

## Key Concepts
- **A program is not a sheet of text**: the naïve view ("change a little text, change the meaning") misses that behavior at a call site can vary without touching that site.
- **Not every call is a seam**: `new FormulaCell(...); cell.Recalculate();` in one method is *not* a seam — no enabling point, the class is fixed at creation. Pass `cell` in as a parameter and the same call *becomes* an object seam.
- **Static methods can be seams**: drop `static`, widen `private`→`protected`, and a subclass can override it in test.

## Code Examples
One call site, three seams. To neutralize `PostReceiveError(...)` under test without editing `Init()`:
```cpp
// Object seam: add a virtual method, subclass overrides it to no-op
class CAsyncSslRec {
  virtual void PostReceiveError(UINT type, UINT errorcode);  // delegates to ::PostReceiveError
};
class TestingAsyncSslRec : public CAsyncSslRec {
  virtual void PostReceiveError(UINT type, UINT errorcode) { }  // nulled out in test
};
```
- **What it demonstrates**: the *same* line can be intercepted by a link seam (stub library, enabling point = makefile), a preprocessing seam (`#define`, enabling point = `TESTING`), or an object seam (enabling point = where the object is created).

## Mental Models
- "Where can I change this behavior **without** editing here?" — that question finds seams.
- Walk the build: text → preprocess → compile → link → run. Each transition is a chance to substitute.

## Anti-patterns
- **Excessive preprocessing in production** (`#ifdef`/`#ifndef`/`#if`): forces you to maintain several programs in one source file; macros hide obscure bugs.
- **Hidden link seams**: enabling point lives outside the source (build script), so testers can't see it — make the test/prod difference obvious.

## Worked Example
The `db_update` C example: a function that talks straight to a database. Add `#include "localdefs.h"` after the declaration; inside, guarded by `#ifdef TESTING`, define a macro `db_update(account_no,item)` that just records `last_item`/`last_account_no`. Now tests assert the right args were passed — the `#include` is a preprocessing seam, `TESTING` its enabling point. Same source compiles unchanged in production.

## Key Takeaways
1. Seam = alter behavior without editing in place; the *enabling point* is where you choose.
2. Three seam types: preprocessing, link, object — found by walking the build steps.
3. Prefer **object seams** in OO code: explicit and maintainable; reserve link/preprocessing seams for pervasive deps.
4. A method call is only a seam if there's an enabling point to vary it.
5. Modify legacy code as *little* as possible to get tests in — seams let you avoid invasive edits.

## Connects To
- **Ch 3**: seams are how you inject the fakes that do sensing.
- **Ch 25**: most dependency-breaking techniques create or exploit an object seam.
- **Ch 5**: tools that exercise code through these seams.
