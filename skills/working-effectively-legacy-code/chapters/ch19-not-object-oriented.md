# Chapter 19: My Project Is Not Object Oriented

## Core Idea

Procedural languages (C, COBOL, FORTRAN, Pascal, BASIC) are the hardest legacy
environment to test, because they lack the **object seams (40)** that
object-oriented and many functional languages give you for free. The whole
discipline rests on the definition that **legacy code = code without tests**:
you want to get code under test before you change it, but procedural code
"often just doesn't have the seams." So in non-OO code, the *type* of seam you
reach for matters more than anywhere else. Without objects, you fall back to the
two seam types from Chapter 4 that survive in procedural code: the
**link seam (36)** and, where the language has a macro preprocessor, the
**preprocessing seam (33)**.

The practitioner's mental shift: stop trying to inject a fake *object* and start
thinking about *where in the build pipeline* you can substitute a definition —
at link time, or at preprocess time. Each such location is a **seam** with an
**enabling point** (the place you flip to choose the test behavior). Because
breaking dependencies one-by-one in procedural code is so tedious, the default
strategy is to find a **pinch point (180)**, use a link seam to sever the worst
dependencies, and pull a *large chunk* of code into a test harness at once —
then write **characterization tests** to pin existing behavior before touching
anything.

## Frameworks Introduced

**Link seam in C.** Build a separate library containing **fakes** — functions
with the *same names and signatures* as the real ones but empty or stubbed
bodies — and link against it for the test build. The production code is
recompiled unchanged; the linker resolves `ksr_notify` to your fake instead of
the vendor's. The enabling point is the build/link configuration. Best when many
peripheral functions need silencing at once. Weakness: link-time substitution
gives you exactly **one** definition per executable, so per-test variation
requires conditional logic inside the fake body — pure **separation**, awkward
**sensing**.

**Preprocessing seam.** In C only, use the macro preprocessor. Wrap a
`#define` in `#ifdef TESTING` to *redefine a function call out of existence* or
to swap in a stub at compile time. The enabling point is whether `TESTING` is
defined at build time. Restrict macro abuse to test-only code and it stays safe.

**Definition Completion / Define Function.** When you need a real (not empty)
test behavior, *complete the definition* of a function in a test file — provide
a body, often guarded by `#ifdef TESTING` and included via file inclusion. This
keeps production source visually close to the original (just one trailing
`#include "testscanner.tst"`), separating tests from production while still
compiling them together when `TESTING` is set.

**Function-pointer substitution.** Wrap external calls in a `struct` of function
pointers. Point them at real functions in production, at fakes in tests. This is
the closest procedural analog to dependency injection / an object seam, and it
is *not* C-specific — it works in any language with function pointers.

## Key Concepts

- **Easy case vs. hard case.** Easy: a free function you can call directly in a
  harness — set inputs (e.g. the `jiffies` global), build a `buffer_head`, call,
  assert on the result. Hard: a function that calls a function that eventually
  hits I/O or a vendor library with a **bad side effect** (e.g. `ksr_notify`
  sending a real notification to a third-party system).
- **Sensing vs. separation.** Link-seam fakes excel at *separation* (stopping a
  side effect) but are poor at *sensing* (reading what was passed). For sensing
  in procedural code, the analog of a mock is a **global recording structure** —
  a global the fake writes into, which the test inspects after the call.
- **Bias toward new functions.** Adding behavior? Write a *new* function rather
  than growing an old one, so you can test the new code. Apply **TDD (88)**.
- **Extract pure logic.** Split computation from dependency. `form_command`
  holds testable logic and returns a value; the thin `send_command` wrapper just
  binds that result to `mart_key_send`. Test the logic, leave a tiny wrapper.

## Mental Models

- **"It's all object oriented."** Every procedural program is already
  object-oriented — it just contains *one giant object*. Wrap all 100 function
  declarations in `class program { ... }`, prefix each definition with
  `program::`, and write a `main` that instantiates it. Behavior is identical;
  it's mechanical. From there, **Encapsulate Global References (339)** carves
  smaller objects out of the monolith.
- **The build pipeline is a seam catalog.** Compile time (preprocessor), link
  time (linker), runtime (function pointers) are three distinct substitution
  points. Pick by what the language offers.

## Anti-patterns

- **Think hard, patch, and hope.** The pandemic procedural habit: edit without
  tests and pray the change was right.
- **Macros in production paths.** Macro replacement is powerful but easily
  misused — keep it confined to code that runs only under test.
- **Forcing link fakes to do sensing.** Stuffing per-test conditionals into a
  single link-time fake body gets messy fast; reach for function pointers or the
  preprocessor instead.
- **Editing logic buried next to an I/O call.** If the only place to observe the
  result is right at the `mart_key_send` call, you've coupled logic to a
  dependency — extract the logic out first.

## Code Examples

```c
/* Preprocessing seam: define the side-effecting call out of existence */
#include "ksrlib.h"

#ifdef TESTING
#define ksr_notify(code, packet)   /* expands to nothing under test */
#endif

int scan_packets(struct rnode_packet *packet, int flag) {
    struct rnode_packet *current = packet;
    int scan_result, err = 0;
    while (current) {
        scan_result = loc_scan(current->body, flag);
        if (scan_result & INVALID_PORT) {
            ksr_notify(scan_result, current);   /* no-op when TESTING */
        }
        current = current->next;
    }
    return err;
}

#ifdef TESTING
#include <assert.h>
void test_port_invalid() {
    struct rnode_packet packet; packet.body = /* ... */;
    int err = scan_packets(&packet, DUP_SCAN);
    assert(err & INVALID_PORT);
}
#endif
```

- **What it demonstrates**: A **preprocessing seam (33)** whose **enabling
  point** is the `TESTING` define. The same source compiles two ways — with the
  real `ksr_notify` for production, and with the call erased for test — giving
  **separation** from a bad side effect without editing the production logic.
  The alternative link-seam version achieves the same by linking a fake:
  `void ksr_notify(int c, struct rnode_packet *p) { }` built in a test library.

## Worked Example

We must change `scan_packets`, but it calls `ksr_notify`, which writes a
notification to a third-party system — unacceptable during tests.

1. **Diagnose the hard case.** The dependency is a side-effecting vendor call
   reachable through the function. We want to pin current behavior with a
   **characterization test** before changing anything.
2. **Pick a seam.** Two options survive in C. *Link seam:* compile a fakes
   library with an empty `ksr_notify` and link it for the test build — cheap if
   many `ksr` calls are peripheral, but only one fake definition per executable.
   *Preprocessing seam:* `#define ksr_notify(code,packet)` under `#ifdef
   TESTING` — finer control, no separate link config.
3. **Keep tests out of the way.** Move the `#ifdef TESTING` block into
   `testscanner.tst` and end the production file with `#include
   "testscanner.tst"`. Now production source reads almost normally; define
   `TESTING` and build the file alone to produce the test executable.
4. **Need to sense, not just separate?** Replace the empty fake with one that
   records into a **global recording structure** the test can assert on — the
   procedural analog of a **mock**.
5. **Have a migration path to OO?** Compile under C++, wrap `ksr_notify` in a
   `ResultNotifier` class using **Preserve Signatures (312)**, introduce a
   `globalResultNotifier`, then **Encapsulate Global References (339)** and
   **Parameterize Constructor (379)** so `Scanner` takes the notifier you
   supply — a real notifier in production, a fake in tests. Now you have a true
   **object seam (40)**, which also improves design, not just testability.

Throughout, follow the **Legacy Code Change Algorithm**: identify change points,
find seams (here: preprocessing/link), break dependencies, write tests, then
make changes and refactor.

## Key Takeaways

- In non-OO code, **seam choice is everything**: with no object seams, lean on
  **link seam (36)** and **preprocessing seam (33)**.
- The default strategy: find a **pinch point (180)**, use a link seam to get a
  *large* area under test, then write characterization tests.
- Link fakes are great for **separation**, weak for **sensing**; for sensing use
  a **global recording structure** or **function pointers**.
- Function-pointer structs give a runtime, OO-style seam that works in most
  procedural languages.
- For new behavior, **bias toward new functions** and use **TDD (88)**; extract
  pure logic from I/O so the logic is testable and the wrapper stays trivial.
- Every procedural program is one big object; if your language has an OO
  successor, migrate — **Encapsulate Global References (339)** turns the
  monolith into testable objects, and object seams improve design beyond tests.

## Connects To

- **Chapter 4 (Seams).** This chapter is Chapter 4 applied with the **object
  seam** removed from the toolbox — only preprocessing and link seams (plus
  their enabling points) remain, plus runtime function pointers.
- **Chapter 8 (How Do I Add a Feature?).** Source of **TDD (88)** and the
  bias-toward-new-functions discipline used in "Adding New Behavior."
- **Chapter 12 (Many Changes in One Area).** Supplies the **pinch point (180)**
  strategy for getting a big chunk of procedural code under test at once.
- **Chapter 20 (This Class Is Too Big).** Where to go after Encapsulate Global
  References starts subdividing the one-big-object program into real classes.
- **Refactorings referenced:** Encapsulate Global References (339), Preserve
  Signatures (312), Parameterize Constructor (379).
