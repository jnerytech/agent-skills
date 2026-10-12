# Chapter 14: Dependencies on Libraries Are Killing Me

## Core Idea
This is a short chapter — more cautionary essay than technique catalog. Code reuse is good: a vendor library can cut real time off a project. The danger is over-reliance. When you litter direct calls to library classes throughout your code, you become structurally married to that vendor — and separating out those calls later "would've amounted to a rewrite." Feathers cites a team that nearly went under when a vendor raised royalties and switching was impossible. Every hard-coded use of a library class is a place where you *could have had a seam* but didn't.

## Frameworks Introduced
No new dependency-breaking algorithm is introduced. The chapter frames a strategic choice between two existing moves:

- **Skin and Wrap the API** — write a thin wrapper you own over the library classes you need, isolating the vendor behind an interface you control. Best when the library is hostile to testing (concrete classes, `final`/`sealed`, non-virtual methods) and you mostly need to *separate* from it.
- **Responsibility-Based Extraction** — rather than wrapping the API one-for-one, extract the work your code actually does into methods/classes organized by responsibility, calling the library only where genuinely needed. Better when you understand the domain and want a layer shaped by *your* needs, not the vendor's surface.

(Both are detailed in the Ch 25 dependency-breaking-techniques catalog; this chapter only chooses between them.)

## Key Concepts
- **Seam + enabling point:** a hard-coded library call has no seam, so there is no enabling point at which to substitute a fake. Wrapping creates one.
- **Sensing vs separation:** here the goal is usually *separation* — getting the library out of the way so the code compiles and runs under test — more than sensing.
- **Fake/mock:** if the library class is concrete, `final`/`sealed`, or has non-virtual key methods, you cannot fake it directly. A thin wrapper restores the ability to inject a fake/mock.
- **The "once" dilemma:** a library assuming a single instance (singleton) can defeat Introduce Static Setter and similar tricks; wrapping the singleton may be the only option.
- **The "restricted override" dilemma:** non-virtual / non-overridable methods block sensing and separation. Treat a public method as non-virtual in production but override it selectively in test to get both worlds.

## Mental Models
- **A thin layer you own is insurance.** Keep your own seam between you and any code you cannot change. The premium (one wrapper) is tiny; the payout (swapping vendors, faking under test) is huge.
- **Self-fulfilling prophecy.** "We'll never change this library" — said often enough while spreading direct calls everywhere — *makes* the library unchangeable.
- **Coding convention ≈ language constraint.** Pretending a method is non-virtual by convention is often as good as the compiler enforcing it, and it leaves you free to override under test. Think about what your tests need.

## Anti-patterns
- Littering direct vendor calls promiscuously throughout the codebase.
- Assuming you'll never switch libraries and designing as if locked in.
- Library *designers* using `final`/`sealed`/non-virtual to enforce design — they forget good code also runs in a **test** environment, and constraints tuned for production can make testing nearly impossible.

## Key Takeaways
- Don't spread direct library calls; concentrate them behind a thin layer you own.
- Choose **Skin and Wrap the API** when the library resists testing and you mainly need separation; choose **Responsibility-Based Extraction** when you want a layer shaped by your domain responsibilities.
- The cost of coupling to a library you can't fake shows up later — as a rewrite, a royalty trap, or untestable code.
- And: "Make sure that you write your vendor and give them grief about making your development work difficult."

## Connects To
- **Ch 15 (My Application Is All API Calls):** the natural sequel — once calls are *already* littered everywhere, how do you get changes (and tests) into code that is nothing but library calls.
- **Ch 25 (Dependency-Breaking Techniques catalog):** full write-ups of Skin and Wrap the API, Extract Interface, Introduce Static Setter, and the other moves referenced here.
- **Legacy Code Change Algorithm:** identify change points, find test points — this chapter is about why those test points often *don't exist* when a library is involved, and how a wrapper creates them.
- **"Legacy code = code without tests":** a library you can't fake silently turns code that uses it into legacy code; characterization tests on a wrapper are how you climb back out.
