# Chapter 2: Working with Feedback

## Core Idea
Tests are a **software vise** that clamps behavior in place so you change only what you intend. The fast feedback of localized unit tests — not careful planning — is what makes change safe.

## Frameworks Introduced
- **Edit and Pray vs. Cover and Modify**: two ways to change software.
  - *Edit and Pray* (industry standard): plan carefully, edit, then poke around hoping nothing broke. Care ≠ safety ("a surgeon with a butter knife").
  - *Cover and Modify*: cover code with tests (a safety net / cloak), then change with fast feedback.
- **The Legacy Code Change Algorithm** ← the spine of the whole book.
  1. Identify change points
  2. Find test points
  3. Break dependencies
  4. Write tests
  5. Make changes and refactor
  - When to use: every time you must change a legacy code base.
  - Why it works: each episode delivers a feature *and* its tests; tested areas grow like islands rising from the ocean into continents.

## Key Concepts
- **Software vise**: tests that detect change fix behavior in place, so you change one behavior at a time, in control.
- **Regression testing / testing to detect change**: run known-good-behavior tests to see if software still works as before — most valuable at a *fine-grained* (unit), not just application, level.
- **Test harness**: generic term for testing code that exercises software plus the code needed to run it (e.g. xUnit, FIT).
- **The Legacy Code Dilemma**: to change code safely you need tests; to get tests in place you often must change code first.
- **Dependency**: classes depending directly on things hard to use in a test are hard to modify. Breaking dependencies is the core of legacy work.

## Mental Models
- Use tests as a vise, not as after-the-fact QA. Feedback in a minute beats feedback overnight.
- Treat dependency-breaking incisions like surgical scars: a little ugliness now; heal it later once tests cover the area.

## Anti-patterns
- **Application-level-only regression testing**: overnight runs, error localization is a debugging hunt across many people's changes ("Daiva from testing called…").
- **Slow "unit" tests**: a test taking 1/10s is *slow*; 30,000 such tests ≈ an hour.

## Reference Tables
A test is **NOT a unit test** if it:
1. Talks to a database
2. Communicates across a network
3. Touches the file system
4. Needs special environment setup (e.g. editing config files)

Qualities of a good unit test: **runs fast** + **helps localize problems**.

## Worked Example
Two scenarios changing a complex function. (A) Edit & Pray: call QA, schedule overnight regression, next morning tests AE1021/AE1029 fail — debug to find whose change broke them. (B) Cover & Modify: ~20 unit tests already exist, all pass. Refactor in tiny steps, run the suite after each; an inverted condition fails a test and is recovered in ~1 minute. Make the change confidently, add tests for new behavior. Same care — radically different feedback loop.

## Key Takeaways
1. Memorize the 5-step Legacy Code Change Algorithm — every later chapter serves a step.
2. Cover before you modify; the vise lets you change one behavior at a time.
3. Unit tests must run fast and localize errors, or they get skipped.
4. The Legacy Code Dilemma is real — break dependencies conservatively to escape it.
5. Dependencies are the #1 impediment to getting tests in place.

## Connects To
- **Ch 5**: the xUnit/FIT tools that host these tests.
- **Ch 9 & 10**: getting a class / method into a harness (steps 2–3).
- **Ch 13**: characterization tests (step 4 in legacy code).
- **Ch 25**: the dependency-breaking catalog referenced by step 3.
