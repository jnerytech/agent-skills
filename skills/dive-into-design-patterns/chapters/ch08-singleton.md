# Chapter 8: SINGLETON

*Category: Creational.*

## Core Idea
Singleton ensures a class has only one instance, while providing a global access point to this instance.

## Frameworks Introduced
- **Singleton**: A class whose constructor is hidden and whose single cached instance is obtained through a static creation method (`getInstance`).
  - When to use: Use it when a class in your program should have just a single instance available to all clients (for example, a single database object shared by different parts of the program). Use it when you need stricter control over global variables.
  - How: (1) Add a private static field for the instance. (2) Declare a public static creation method to get the instance. (3) Implement lazy initialization inside it — create on first call, return the same instance afterward. (4) Make the constructor private. (5) Replace all direct constructor calls in client code with calls to the static creation method.

## Key Concepts
- **Singleton class**: Declares the static `getInstance` returning the same instance of its own class.
- **Private constructor**: Prevents other objects from using `new` on the class.
- **Static instance field**: Caches the single created object.
- **Static creation method (`getInstance`)**: The only way to obtain the object; creates then caches it.
- **Global access point**: Like a global variable but protected from being overwritten.
- **Lazy initialization**: The instance is created only on first request.

## Mental Models
- **Real-World Analogy**: The government. A country has only one official government; regardless of who staffs it, "The Government of X" is a single global access point to whoever is in charge.
- Think of `getInstance` as a turnstile that always returns the same person.

## Anti-patterns
- **Using it as a glorified global variable**: it can mask bad design where components know too much about each other.
- **Ignoring threads**: in a multithreaded environment, naive lazy init can create several instances — needs locking (double-checked).
- **SRP violation by design**: it solves two problems at once (single instance + global access), violating the Single Responsibility Principle.
- **Hard to unit test**: private constructor + non-overridable static methods break mock frameworks that rely on inheritance.

## Code Examples
```
class Database is
    private static field instance: Database
    private constructor Database() is
        // connect to a database server ...

    public static method getInstance() is
        if (this.instance == null) then
            acquireThreadLock() and then
                if (this.instance == null) then   // double-check
                    this.instance = new Database()
        return this.instance

    public method query(sql) is
        // all queries go through here (good spot for throttling/caching)
```
- **What it demonstrates**: Lazy, thread-safe single-instance creation via a private constructor and double-checked locking; `Database.getInstance()` everywhere returns the same object.

## Reference Tables
| Pros | Cons |
|------|------|
| Guaranteed single instance of the class | Violates Single Responsibility Principle (solves two problems) |
| A global access point to that instance | Can mask bad design (components knowing too much) |
| Initialized lazily, on first request | Needs special treatment in multithreaded environments |
| | Hard to unit test (private ctor, static methods) |

## Worked Example
A database connection class as a Singleton. It has no public constructor; the only way to get an object is `getInstance()`, which caches the first instance and returns it on every later call. In `Application.main`, `foo = Database.getInstance()` and `bar = Database.getInstance()` yield the *same* object, so `foo.query(...)` and `bar.query(...)` hit one shared connection. The `getInstance` body can be relaxed later to allow N instances if needed.

## Key Takeaways
1. One instance + global access point, enforced via private constructor and static `getInstance`.
2. Use it for shared resources (DB, file) or stricter-than-global control.
3. Lazy initialization defers creation to first use.
4. It deliberately violates SRP and can hide design smells — use sparingly.
5. Multithreading requires locking; testing requires creative mocking.

## Connects To
- **Facade**: can often be turned into a Singleton, since one facade object usually suffices.
- **Flyweight**: resembles Singleton if all shared state collapses to one object, but Flyweight allows many immutable instances with different intrinsic state, whereas a Singleton has one (possibly mutable) instance.
- **Abstract Factory / Builder / Prototype**: can all be implemented as Singletons.
