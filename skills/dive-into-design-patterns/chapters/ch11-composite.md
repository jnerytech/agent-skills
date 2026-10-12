# Chapter 11: COMPOSITE

## Core Idea
Composite (aka Object Tree) is a structural pattern that lets you compose objects into tree structures and then work with those structures as if they were individual objects, running behavior recursively over the whole tree.

## Frameworks Introduced
- **Composite**: define a common interface for both simple (leaf) and complex (container) elements; containers delegate work to their children recursively.
  - When to use: Use when you have to implement a tree-like object structure; and when you want client code to treat simple and complex elements uniformly.
  - How: (1) Make sure your core model is a tree of simple elements and containers (containers hold both). (2) Declare a component interface with methods meaningful to both. (3) Create leaf class(es) for simple elements. (4) Create a container class with an array field typed as the component interface; delegate most work to sub-elements. (5) Define add/remove child methods (declaring them in the component interface lets clients treat all elements equally, though it violates Interface Segregation — empty in leaves).

## Key Concepts
- **Component**: interface describing operations common to simple and complex elements.
- **Leaf**: basic element with no sub-elements; usually does the real work.
- **Container** (Composite): element with sub-elements (leaves or other containers); works with children only via the component interface and delegates to them.
- **Client**: works with all elements through the component interface, treating simple and complex alike.
- **Recursive composition**: a request passed down the tree, each container summing its children's results.

## Mental Models
- **Real-World Analogy**: a military hierarchy — army → divisions → brigades → platoons → squads → soldiers. Orders given at the top pass down each level until every soldier knows what to do.
- Think of an order made of Products and Boxes: a Box contains Products and smaller Boxes; total price = recursive sum.

## Anti-patterns
- **Forcing Composite when the model isn't a tree**: it only makes sense when the core model can be represented as a tree.
- **Over-generalizing the component interface**: when classes differ too much, a common interface becomes hard to comprehend.
- **Direct unwrapping/looping**: manually traversing classes, nesting levels, and types is awkward or impossible — the problem Composite solves.

## Code Examples
```
// Component interface common to simple and complex objects.
interface Graphic is
    method move(x, y)
    method draw()

// Leaf: end object, does the real work.
class Dot implements Graphic is
    field x, y
    method move(x, y) is this.x += x; this.y += y
    method draw() is // Draw a dot at X, Y.

class Circle extends Dot is
    field radius
    method draw() is // Draw a circle at X, Y, radius R.

// Composite: holds children, delegates and sums up.
class CompoundGraphic implements Graphic is
    field children: array of Graphic
    method add(child: Graphic) is ...
    method remove(child: Graphic) is ...
    method move(x, y) is
        foreach (child in children) child.move(x, y)
    method draw() is
        // Recursively draw each child; update bounding box.
```
- **What it demonstrates**: a CompoundGraphic exposes the same interface as a Dot, but forwards calls recursively to its children, so the client treats one shape and a group identically.

## Reference Tables
| Pros | Cons |
|------|------|
| Work with complex trees conveniently via polymorphism and recursion | Hard to give a common interface to classes whose functionality differs too much |
| Open/Closed: introduce new element types without breaking existing tree code | May force an over-generalized interface |

## Worked Example
A graphics editor stacks geometric shapes. Simple shapes (Dot, Circle) are leaves; CompoundGraphic is a container holding any number of sub-shapes, including other compound shapes. The client (ImageEditor) calls `all.draw()` on the top-level composite; each compound shape forwards `draw()`/`move()` recursively to its children and sums results (e.g., the bounding rectangle). `groupSelected()` moves selected components into a new CompoundGraphic — the editor never needs to know whether it holds a simple or complex shape.

## Key Takeaways
1. Composite represents part-whole hierarchies as trees with a uniform interface.
2. Leaves do the actual work; containers delegate to children and aggregate results.
3. The client is decoupled from concrete classes — simple and complex elements are interchangeable.
4. Recursion + polymorphism replace fragile manual tree traversal.
5. Only apply it when the model is genuinely tree-shaped.

## Connects To
- **Builder**: can construct complex Composite trees with recursive steps.
- **Chain of Responsibility**: a leaf can pass a request up through parent components to the root.
- **Iterator**: traverse Composite trees.
- **Visitor**: execute an operation over an entire Composite tree.
- **Flyweight**: implement shared leaf nodes to save RAM.
- **Decorator**: similar recursive-composition structure, but a Decorator has only one child and adds responsibilities (Composite just sums up children). They can cooperate.
- **Prototype**: clone complex Composite/Decorator structures instead of rebuilding them.
