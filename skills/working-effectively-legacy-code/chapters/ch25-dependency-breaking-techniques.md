# Chapter 25: Dependency-Breaking Techniques (Catalog)

## Core Idea
This is the reference catalog the rest of the book points to — 24 named, behavior-preserving refactorings designed to be applied *without* tests, just well enough to get a seam in place and the first test running. They deliberately leave a less-than-ideal design (some will make you flinch); you clean up *after* tests exist. Pick a technique by matching the obstacle in front of you to the language seam (object, interface, link, preprocessor) you can actually exploit. Always pair with Ch 23 ("How Do I Know That I'm Not Breaking Anything?") and Preserve Signatures to apply them safely.

## How to Choose

| Obstacle | Reach for |
|---|---|
| Irritating / un-fakeable constructor param | **Extract Interface**, **Adapt Parameter** (when you can't extract from the param's type) |
| Object built in constructor (hard-coded `new`) | **Parameterize Constructor**, **Extract and Override Factory Method** (not C++ ctors), **Extract and Override Getter** (C++), **Supersede Instance Variable** (C++) |
| Object built inside a method | **Parameterize Method** |
| Single bad method call / static call side effect | **Extract and Override Call**, **Subclass and Override Method** |
| Many bad methods on one object | **Extract and Override Getter** |
| Global / singleton dependency | **Introduce Static Setter**, **Encapsulate Global References**, **Replace Global Reference with Getter** |
| Static utility method you must swap | **Introduce Instance Delegator**, **Expose Static Method** |
| Long method, can't instantiate the class | **Break Out Method Object**, **Expose Static Method** (if no instance data) |
| Cluster of good methods trapped with bad deps | **Pull Up Feature** |
| Pervasive bad deps mixed into the class | **Push Down Dependency** |
| Class too expensive to instantiate at all | **Primitivize Parameter** (last resort) |
| Want to extract interface but name is taken | **Extract Implementer** |
| C function dependency | **Link Substitution**, **Definition Completion** (C/C++), **Replace Function with Function Pointer** (C) |
| Dependency inside C++ template code | **Template Redefinition** |
| Interpreted language (Ruby etc.) | **Text Redefinition** |

## The Catalog

### Adapt Parameter
- **Use when**: A method takes a fat/library/low-level parameter type you can't Extract Interface from or can't easily fake (e.g. `HttpServletRequest`).
- **How**: Define a new narrow interface expressing only what the method needs; write a production implementer that wraps the real type and a fake for tests; change the method to use the new interface.
- **Trade-off**: You do *not* Preserve Signatures here — a too-different simplified interface risks subtle bugs; bias toward changes you trust.

### Break Out Method Object
- **Use when**: A long method (using instance data/methods) blocks you, and making its class instantiable in a harness is too much work.
- **How**: Create a new class whose constructor takes the original method's args (plus a ref to the original class if needed); copy the body into a run/execute method; Lean on the Compiler to expose needed members; delegate from the old method; Extract Interface to cut the back-reference.
- **Trade-off**: Forces previously private members public and leaves an odd structure — only a first step until the class is testable.

### Definition Completion *(C/C++ only)*
- **Use when**: You must replace a class's method definitions under test in C/C++ and have no better seam.
- **How**: Verify definitions live in a source file (not header); include the header in the test file; drop the real source from the build; build and supply alternate (null or sensing) definitions in the test file until it links.
- **Trade-off**: Two duplicate definition sets and a separate test executable — a maintenance/debugger burden; use only in worst cases and exit fast.

### Encapsulate Global References
- **Use when**: Code depends on globals (data or free functions) scattered across methods/classes that you want to decouple.
- **How**: Bundle related globals into a new class (good name matters), copy them in, comment out the originals, declare a global instance, Lean on the Compiler, and prefix each broken reference with the instance; for free functions, make an interface with fake + delegating production subclasses.
- **Trade-off**: Leaves uglier code referencing a global instance; only a first step — follow with Introduce Static Setter / Parameterize Constructor or Method.

### Expose Static Method
- **Use when**: A method that uses no instance data sits on a class you can't instantiate, and you need it under test.
- **How**: Write a test calling it as a public static; extract the body to a static method (Preserve Signatures, name it from a param, e.g. `validatePacket`); compile and make any needed dependencies static too.
- **Trade-off**: Breaks encapsulation slightly and the method may really belong elsewhere — treat the static area as a "staging area" until you relocate it.

### Extract and Override Call
- **Use when**: A localized single call (often to a global or static) causes side effects or needs sensing.
- **How**: Copy the called method's signature; create a local method with it that delegates to the original call; replace the call site; subclass and override the local method in tests.
- **Trade-off**: Adds an indirection method; if many calls hit the same global, prefer Replace Global Reference with Getter.

### Extract and Override Factory Method
- **Use when**: An object is hard-coded with `new` inside a constructor and its creation work shouldn't run in tests.
- **How**: Extract the creation into a protected factory method; subclass and override it to return a fake.
- **Trade-off**: Does **not** work in C++ (no virtual dispatch from constructors) — use Extract and Override Getter or Supersede Instance Variable there.

### Extract and Override Getter
- **Use when**: You need the C++ workaround for constructor-created objects, or one object has *many* problematic methods.
- **How**: Introduce a lazy getter that creates the object on first call; replace every direct use of the variable with the getter and init the field to null; subclass and override the getter to supply a fake.
- **Trade-off**: Risk of using the variable before init (route *all* access through the getter); watch object lifetime in non-GC languages. Overkill for a single bad method — use Extract and Override Call.

### Extract Implementer
- **Use when**: You want Extract Interface but the perfect interface name is already the class's name (and you lack rename tooling).
- **How**: Copy the class declaration to a new `Production…` class; strip the original down to public methods made pure-virtual/abstract (it becomes the interface); make the production copy implement it; redirect all instantiations to the production class.
- **Trade-off**: Many mechanical steps, and inheritance hierarchies make it tricky — often Extract Interface with a fresh name is more direct.

### Extract Interface
- **Use when**: You need to fake/substitute a collaborator and the language has interfaces — one of the safest techniques (compiler catches missteps).
- **How**: Create an empty interface; make the class implement it; change the reference at the test point to the interface type; Lean on the Compiler and add only the method declarations the errors demand.
- **Trade-off**: Beware non-virtual methods (C++/C#/Java statics) — pulling them into an interface can change which override runs; add a new virtual delegating method instead. You needn't cover every public method.

### Introduce Instance Delegator
- **Use when**: A problematic static/utility method (static cling) needs an object seam so tests can substitute behavior.
- **How**: Add an instance method (Preserve Signatures) that delegates to the static; at call sites, pass in an instance and call the instance method instead of the static.
- **Trade-off**: Leaves a weird-looking class of mostly delegating instance methods until you eventually move the static bodies into them.

### Introduce Static Setter
- **Use when**: A global or Singleton must be replaced with a fake for sensing/separation.
- **How**: Loosen the constructor protection (private→protected) so you can subclass; add a static setter that safely destroys the old instance and installs the new one; pass a fake/subclass via the setter (for global factories, delegate to a swappable server object).
- **Trade-off**: Mutates state shared across all tests (use setUp/tearDown to reset) and weakens access protection — invasive; the real goal is to reduce global references until the singleton can be a normal class.

### Link Substitution
- **Use when**: Procedural code (C, also Java) gives you no object seam — only the linker — to replace functions, especially external libraries.
- **How**: Build a dummy library of functions with identical signatures (recording calls in a global/file if sensing); adjust the build to link these instead of the production versions.
- **Trade-off**: Build/link changes can be nontrivial, and the seam isn't one you'd vary in production; best for pure "data sink" libraries (e.g. graphics).

### Parameterize Constructor
- **Use when**: A constructor creates an object internally and you want to pass a substitute in.
- **How**: Add a parameter for the object and assign it instead of `new`-ing; keep a same-signature convenience constructor that calls the new one with a real instance (or use a default argument where the language allows).
- **Trade-off**: Opens the door to wider dependence on the parameter's type via the new constructor; default args in C++ force extra header includes. Minor — a very common, easy refactoring.

### Parameterize Method
- **Use when**: A method creates an object internally that you want to sense or separate.
- **How**: Add a parameter for that object and assign it instead of creating; keep a same-name forwarding method (or `runWithX`) that calls the parameterized version with a real object.
- **Trade-off**: Like Parameterize Constructor, can spread new type dependencies into the interface — consider Extract and Override Factory Method if that worries you.

### Primitivize Parameter
- **Use when**: A class is so tangled it's ridiculously expensive to instantiate, but you must add a feature now.
- **How**: Write a free function that does the work over a simplified primitive representation (test that fully); add a thin method on the class that builds the representation and delegates to the free function.
- **Trade-off**: Leaves code in a genuinely poor state (exposed internals, duplicated/untested glue) — use only when you commit to bringing the class under test later; often a predecessor to Sprout Class.

### Pull Up Feature
- **Use when**: A cluster of methods you care about is fine on its own, but unrelated bad dependencies in the same class block instantiation.
- **How**: Create an abstract superclass; copy the wanted methods (and what they reference) up into it, Preserving Signatures and Leaning on the Compiler; leave the bad deps in the original; subclass the abstract class for tests.
- **Trade-off**: Spreads related features across two classes for test convenience — confusing if cohesion is weak; move toward proper delegation once tests exist.

### Push Down Dependency
- **Use when**: Bad dependencies are *pervasive* in a class (so Subclass and Override or repeated Extract Interface won't cut it).
- **How**: Make the current class abstract; create a production subclass and push all problematic deps (vars + methods, now protected/abstract in the parent) down into it; create a testing subclass that nulls them out.
- **Trade-off**: Uses inheritance purely for testability, not ideal design — a stepping stone toward extracting the deps into their own delegate class.

### Replace Function with Function Pointer *(C only)*
- **Use when**: You need to break a C function dependency and Link Substitution / Definition Completion are overkill.
- **How**: Declare a function pointer with the function's name beside its declaration; rename the original to `…_production`; initialize the pointer to the production function in a C file; rename the definition to match. Tests reassign the pointer.
- **Trade-off**: Function pointers are seen as unsafe (callable through bad memory) by some teams; consider migrating the file to C++ for richer seams.

### Replace Global Reference with Getter
- **Use when**: A class references a global (incl. `Class.getInstance()` static access) you want to override under test.
- **How**: Add a protected getter that returns the global; replace every global reference in the class with the getter; subclass and override the getter to return a fake.
- **Trade-off**: Requires loosening protection (e.g. singleton constructor private→protected) and only relocates the global access — pair with Extract Interface for deeper decoupling.

### Subclass and Override Method
- **Use when**: You want to nullify or sense behavior isolated in a method — the core OO technique many others build on.
- **How**: Find the smallest set of methods to override; make them overridable (virtual/non-final) and visible enough (≥protected in Java/C#; private OK in C++); create a testing subclass overriding them.
- **Trade-off**: Only as good as the class's factoring — a dependency buried in a huge method forces you to override too much; nulling a method can erase behavior you actually needed.

### Supersede Instance Variable *(C++ workaround)*
- **Use when**: An object is created in a C++ constructor *and used by it*, so Extract and Override Factory Method (no virtual ctor dispatch) won't work.
- **How**: Add a `supersedeXXX` method that safely deletes the existing instance variable and installs a new one; call it in tests after construction to inject a sensing object.
- **Trade-off**: Setters that swap base objects are generally poor practice (callers can mutate behavior mid-life) — prefer Extract and Override Factory Method in languages that allow virtual calls in constructors.

### Template Redefinition *(C++ / generics)*
- **Use when**: A C++ class has a hard dependency (e.g. a `CSocket` member) and you have generics + type aliasing, or the dep is already inside templatized code.
- **How**: Turn the class into a template parameterized on the dependency's type, move method bodies into the header, rename to `…Impl`, and add a `typedef` of the original name with the production type; tests instantiate the template with a fake type.
- **Trade-off**: Moves implementation into headers, increasing compile dependencies and rebuild churn; bias toward inheritance-based techniques unless the deps are already in template code.

### Text Redefinition *(Ruby / interpreted; C/C++ via preprocessor)*
- **Use when**: An interpreted language lets you redefine a method on the fly to neutralize it under test.
- **How**: In the test file, `require` the module and reopen the class, providing alternative definitions for just the methods you want to replace (the interpreter silently overwrites them).
- **Trade-off**: The redefinition persists for the whole program run — a forgotten override can corrupt later tests.

## Connects To
- **Ch 9 / 10**: "I can't get this class / method into a test harness" sends you here — constructor and hidden-dependency obstacles (Ch 9) map to the constructor/global techniques; method-side obstacles (Ch 10) map to Parameterize Method, Subclass and Override Method, Break Out Method Object, Pull Up Feature.
- **Ch 3 / 4**: These techniques *create the seams* (object, link, preprocessing seams from Ch 4) and enable the fake objects from Ch 3 — Extract Interface / Adapt Parameter / Push Down Dependency open object seams; Link Substitution and Definition Completion open link/preprocessing seams; the result is a place to insert a fake or sensing object.
