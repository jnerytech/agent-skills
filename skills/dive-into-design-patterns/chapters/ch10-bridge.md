# Chapter 10: BRIDGE

## Core Idea
Bridge is a structural pattern that splits a large class (or set of closely related classes) into two separate hierarchies — Abstraction and Implementation — that can be developed independently, replacing inheritance with composition.

## Frameworks Introduced
- **Bridge**: extract one of two orthogonal dimensions into its own hierarchy; the original class holds a reference to it (the "bridge") and delegates work.
  - When to use: Use when you want to divide/organize a monolithic class with several variants of functionality (e.g., works with various DB servers); when you need to extend a class in several orthogonal (independent) dimensions; or when you need to switch implementations at runtime.
  - How: (1) Identify orthogonal dimensions (abstraction/platform, domain/infrastructure, front-end/back-end). (2) Define operations the client needs in the base Abstraction. (3) Declare primitive operations the abstraction needs in the Implementation interface. (4) Create Concrete Implementations for each platform following that interface. (5) Add an implementation reference field inside the abstraction; delegate work to it. (6) Create Refined Abstractions for variants of high-level logic. (7) Client passes an implementation into the abstraction's constructor.

## Key Concepts
- **Abstraction** (interface): high-level control layer; does no real work, delegates to implementation.
- **Implementation** (platform): interface declaring primitive operations common to all concrete implementations.
- **Concrete Implementation**: platform-specific code.
- **Refined Abstraction**: variant of control logic extending the base abstraction.
- **Client**: works with the abstraction; links it to an implementation object.

## Mental Models
- **Real-World Analogy (from text)**: GUI (abstraction) calling the OS API (implementation) — several GUIs and several APIs (Windows/Linux/macOS) can vary independently.
- Think of Shape × Color: instead of BlueCircle/RedSquare combinations, Shape holds a reference to a Color object.
- The reference field IS the "bridge" between the two hierarchies.

## Anti-patterns
- **Class-combination explosion**: extending in two dimensions via inheritance (BlueCircle, RedSquare, BlueTriangle...) grows in geometric progression — the problem Bridge fixes.
- **Applying Bridge to a highly cohesive class**: adds needless complexity when there are no real orthogonal dimensions.
- **Confusing Bridge with Strategy**: runtime swapping resembles Strategy, but Bridge communicates a different intent (structuring two stable hierarchies up-front).

## Code Examples
```
// Abstraction: holds a reference to implementation, delegates work.
class RemoteControl is
    protected field device: Device
    constructor RemoteControl(device) is this.device = device
    method togglePower() is
        if (device.isEnabled()) device.disable()
        else device.enable()
    method volumeUp() is device.setVolume(device.getVolume() + 10)

// Refined Abstraction: extends independently of devices.
class AdvancedRemoteControl extends RemoteControl is
    method mute() is device.setVolume(0)

// Implementation interface: primitive ops only.
interface Device is
    method enable(); method disable()
    method getVolume(); method setVolume(percent)
    method getChannel(); method setChannel(channel)

class Tv implements Device is ...
class Radio implements Device is ...

// Client links abstraction to implementation.
remote = new AdvancedRemoteControl(new Radio())
```
- **What it demonstrates**: remotes (abstraction) and devices (implementation) evolve separately; any remote works with any device via the common Device interface.

## Reference Tables
| Pros | Cons |
|------|------|
| Platform-independent classes and apps | Can over-complicate a highly cohesive class |
| Client works with high-level abstractions, hidden from platform details | |
| Open/Closed: add abstractions and implementations independently | |
| Single Responsibility: high-level logic vs. platform details separated | |

## Worked Example
A monolithic app manages devices and their remote controls. As written, hundreds of conditionals tangle every remote type with every device type. Bridge divides it: Device classes (Tv, Radio) become the Implementation hierarchy exposing primitive operations; RemoteControl and AdvancedRemoteControl become the Abstraction hierarchy. The remote keeps a `device` reference and builds higher-level operations (togglePower, volumeUp) on the primitives. Adding a new device = one new Device subclass; adding a new remote = one new RemoteControl subclass — neither touches the other.

## Key Takeaways
1. Bridge turns one exploding hierarchy into two independent hierarchies linked by a reference.
2. Abstraction = high-level control; Implementation = low-level primitives; their interfaces need not match.
3. Switch from inheritance to composition to handle orthogonal dimensions.
4. Implementations are interchangeable and can be swapped at runtime.
5. Usually designed up-front, unlike Adapter which retrofits existing code.

## Connects To
- **Adapter**: retrofits existing incompatible classes; Bridge is planned up-front for independent development.
- **State/Strategy/Adapter**: similar composition-based structure, different problems.
- **Abstract Factory**: can encapsulate relations when some abstractions only work with specific implementations.
- **Builder**: director acts as the abstraction, builders act as implementations.
