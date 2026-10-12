# Chapter 14: FLYWEIGHT

## Core Idea
Flyweight (a.k.a. Cache) is a structural pattern that lets you fit more objects into available RAM by sharing the common parts of state between many objects instead of duplicating that data in each one.

## Frameworks Introduced
- **Flyweight**: An object that stores only the shared intrinsic state, reused across many contexts.
  - When to use:
    - Use only when your program must support a huge number of objects that barely fit into available RAM.
    - Most useful when: (a) the app spawns a huge number of similar objects, (b) this drains all RAM on the target device, and (c) the objects contain duplicate state that can be extracted and shared.
  - How: split fields into intrinsic vs extrinsic; keep intrinsic immutable inside the object; pass extrinsic state into methods as parameters; optionally add a factory to pool and reuse flyweights; store extrinsic state in a context or container.

## Key Concepts
- **Intrinsic state**: Constant, shareable data living inside the flyweight (e.g. color, sprite/texture); read-only to others.
- **Extrinsic state**: Contextual data unique to each object and altered from outside (e.g. coordinates, vector, speed); moved out of the flyweight.
- **Flyweight**: An object holding only intrinsic state — a configurable template.
- **Context**: An object holding the extrinsic state plus a reference to a flyweight; together they represent one full original object.
- **Flyweight Factory**: Manages a pool; returns an existing flyweight matching the requested intrinsic state, or creates and caches a new one.
- **Immutability**: Flyweights must initialize state once via constructor and expose no setters/public fields, since the same instance is shared everywhere.

## Mental Models
- Think of a flyweight as a **rubber stamp**: one stamp (intrinsic) pressed at many positions (extrinsic) on a page.
- Think of the context as a **lightweight pointer + coordinates** that borrows the heavy shared data instead of copying it.

## Anti-patterns
- **Applying Flyweight prematurely**: it is merely an optimization — don't use it unless you've confirmed a real RAM problem that can't be solved more simply.
- **Mutable flyweights**: exposing setters corrupts every context sharing the instance.
- **Recomputing context data on every call**: you may trade saved RAM for extra CPU cycles, and the code becomes much harder for new team members to understand.

## Code Examples
```
class TreeType is                      // FLYWEIGHT: intrinsic state
    field name; field color; field texture
    method draw(canvas, x, y) is ...   // extrinsic x,y passed in

class TreeFactory is                   // pools & reuses flyweights
    static field treeTypes
    static method getTreeType(name, color, texture) is
        type = treeTypes.find(name, color, texture)
        if (type == null)
            type = new TreeType(name, color, texture)
            treeTypes.add(type)
        return type

class Tree is                          // CONTEXT: extrinsic state
    field x, y
    field type: TreeType
    method draw(canvas) is type.draw(canvas, this.x, this.y)
```
- **What it demonstrates**: heavy shared data (texture/color) lives once per TreeType; billions of tiny Tree contexts hold just coordinates + a reference.

## Reference Tables
| Pros | Cons |
|------|------|
| Saves lots of RAM when there are tons of similar objects | May trade RAM for CPU if context data is recalculated each call |
|  | Code becomes much more complicated; the state split puzzles newcomers |

## Worked Example
A shoot-em-up game renders vast clouds of bullets, missiles, and shrapnel. Each particle was a full object storing color + sprite (huge) plus coordinates, vector, speed. At peak carnage, new particles no longer fit in RAM and the game crashes on a weaker machine. Solution: extract the constant color/sprite into flyweight particle objects — only three are needed (bullet, missile, shrapnel). The unique coordinates/vector/speed move into a context (or parallel arrays in the Game container). A thousand tiny contexts now reference one heavy flyweight instead of copying its data a thousand times. The same idea renders millions of trees: TreeType is the flyweight, Tree the context, TreeFactory the pool, Forest the client.

## Key Takeaways
1. Separate immutable intrinsic state (shared) from mutable extrinsic state (per-object, passed as method params).
2. Flyweight is purely a memory optimization — measure before applying.
3. A factory enforces reuse: clients request flyweights by intrinsic state, never `new` directly.
4. Extrinsic state lives in the client/container, often packaged in a context class.
5. Flyweights must be immutable because one instance serves many contexts.

## Connects To
- **Composite**: shared leaf nodes of a Composite tree can be implemented as Flyweights to save RAM.
- **Facade**: Flyweight makes many little shared objects; Facade makes one object fronting a subsystem.
- **Singleton**: resembles Flyweight if all shared state collapses to one object, but a Singleton has exactly one (possibly mutable) instance, whereas Flyweight allows many immutable instances with different intrinsic states.
