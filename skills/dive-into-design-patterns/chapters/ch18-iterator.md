# Chapter 18: ITERATOR

*Category: Behavioral.*

## Core Idea
Traverse the elements of a collection without exposing its underlying representation (list, stack, tree, graph, etc.).

## Frameworks Introduced
- **Iterator**: Extracts a collection's traversal behavior into a separate iterator object that holds the traversal state.
  - When to use:
    - The collection has a complex data structure you want to hide from clients (convenience or security).
    - You want to reduce duplication of bulky traversal code across the app.
    - You want code that can traverse different/unknown data structures uniformly.
  - How: Declare an iterator interface (e.g. `getNext`, `hasMore`); concrete iterators implement specific traversal algorithms and track their own position; collection interface declares a factory method returning iterators; client works only through interfaces.

## Key Concepts
- **Iterator interface**: Declares traversal ops — fetch next, check end, current position, restart.
- **Concrete Iterator**: Implements a specific traversal algorithm; tracks its own progress, so several can run on one collection independently.
- **Collection interface**: Declares one+ factory methods that return iterators (typed as the iterator interface).
- **Concrete Collection**: Returns new instances of a concrete iterator on request.
- **Client**: Works with collections and iterators via interfaces only — decoupled from concrete classes.

## Mental Models
- **Real-World Analogy**: Touring Rome — wandering randomly, a smartphone navigator app, or a hired local guide are all different "iterators" over the same collection of attractions.
- Think of passing an iterator (not the whole collection) to a client to hide the collection entirely and swap traversal at runtime.

## Anti-patterns
- **Iterators over simple collections**: Overkill when the app only handles plain lists.
- **Performance cost**: Going through some specialized collections via an iterator can be less efficient than direct access.
- **Bloating the collection with traversal algorithms**: Blurs its primary responsibility (efficient storage).

## Code Examples
```
interface SocialNetwork is
    method createFriendsIterator(profileId): ProfileIterator
    method createCoworkersIterator(profileId): ProfileIterator

interface ProfileIterator is
    method getNext(): Profile
    method hasMore(): bool

class FacebookIterator implements ProfileIterator is
    private field facebook, profileId, type, currentPosition, cache
    method getNext() is
        if (hasMore()) currentPosition++; return cache[currentPosition]
    method hasMore() is
        lazyInit(); return cache.length < currentPosition

class SocialSpammer is
    method send(iterator: ProfileIterator, message) is
        while (iterator.hasNext())
            profile = iterator.getNext()
            System.sendEmail(profile.getEmail(), message)
```
- **What it demonstrates**: A `SocialNetwork` collection produces friends/coworkers iterators; the client (`SocialSpammer`) iterates uniformly without knowing REST/auth details.

## Reference Tables
| Pros | Cons |
|------|------|
| Single Responsibility (extract traversal from collections/clients) | Overkill for simple collections |
| Open/Closed (new collections & iterators without breaking code) | May be less efficient than direct traversal of specialized collections |
| Iterate the same collection in parallel (each holds its own state) | |
| Delay an iteration and resume later | |

## Worked Example
A collection wraps Facebook's social graph and exposes a "friends" iterator and a "colleague" iterator (the latter skips friends at other companies). Both share `ProfileIterator`, so a client fetches profiles without touching authentication or REST calls. Switching to LinkedIn means adding new collection + iterator classes; existing client code is unchanged.

## Key Takeaways
1. The iterator encapsulates traversal position and remaining-elements logic.
2. Multiple iterators traverse the same collection independently and in parallel.
3. Clients get iterators from collections via factory methods, staying decoupled.
4. New traversal strategies are new iterator classes — no change to collection or client.
5. Passing an iterator instead of a collection hides the collection from clients.

## Connects To
- **Composite**: use Iterators to traverse Composite trees.
- **Factory Method**: lets collection subclasses return compatible iterator types.
- **Memento**: capture iteration state and roll it back if needed.
- **Visitor**: traverse a complex structure and run operations on its varied-class elements.
