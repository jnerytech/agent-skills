# Chapter 13: FACADE

## Core Idea
Facade is a structural pattern that provides a simplified interface to a library, framework, or any complex set of classes, hiding their moving parts behind one convenient entry point.

## Frameworks Introduced
- **Facade**: A class offering a simple, narrow interface to a complex subsystem.
  - When to use:
    - Use when you need a limited but straightforward interface to a complex subsystem (a shortcut to the most-used features).
    - Use when you want to structure a subsystem into layers — create a facade as the entry point to each level, reducing coupling by forcing subsystems to talk only through facades.
  - How: declare a new class exposing only what clients care about; redirect its calls to the right subsystem objects; make the facade own subsystem initialization and lifecycle; route all client code through it.

## Key Concepts
- **Facade**: Knows where to direct each client request and how to operate the subsystem's parts.
- **Additional Facade**: A second refined facade extracted to keep unrelated features out of one bloated facade; usable by clients and other facades.
- **Complex Subsystem**: Dozens of objects requiring correct init order and proper data formats; unaware the facade exists.
- **Client**: Uses the facade instead of calling subsystem objects directly.
- **God object**: The failure mode — a facade that grows coupled to every class in the app.

## Mental Models
- **Real-World Analogy**: Phone-ordering at a shop. The operator is your facade to all departments — order system, payment gateways, delivery — giving you one simple voice interface.
- Think of the facade as a **TV remote**: a few buttons in front of vast internal electronics.
- Think of it as a **wrapper over a subsystem**, not a single object (that distinguishes it from Adapter).

## Anti-patterns
- **Letting the facade become a god object**: when it ends up coupled to all app classes, it stops simplifying and becomes another complexity center — split it into refined facades.
- **Using Facade when you only need to hide object creation**: prefer Abstract Factory for that.

## Code Examples
```
// Facade hiding a complex 3rd-party video framework
class VideoConverter is
    method convert(filename, format):File is
        file = new VideoFile(filename)
        sourceCodec = new CodecFactory.extract(file)
        if (format == "mp4")
            destinationCodec = new MPEG4CompressionCodec()
        else
            destinationCodec = new OggCompressionCodec()
        buffer = BitrateReader.read(filename, sourceCodec)
        result = BitrateReader.convert(buffer, destinationCodec)
        result = (new AudioMixer()).fix(result)
        return new File(result)

class Application is
    method main() is
        convertor = new VideoConverter()
        mp4 = convertor.convert("youtubevideo.ogg", "mp4")
        mp4.save()
```
- **What it demonstrates**: One `convert()` call hides VideoFile, CodecFactory, BitrateReader, AudioMixer — the app depends on the facade, not a billion framework classes.

## Reference Tables
| Pros | Cons |
|------|------|
| Isolates your code from subsystem complexity | A facade can become a god object coupled to all classes of an app |

## Worked Example
An app uploads short cat videos to social media. It could use a heavyweight professional video-conversion library with dozens of features, but all it really needs is `encode(filename, format)`. Wrapping the library in a `VideoConverter` facade hides VideoFile, codecs, BitrateReader, and AudioMixer. The app calls one method; switching or upgrading the underlying framework later means rewriting only the facade. The subsystem can also be split into video and audio layers, each fronted by its own facade.

## Key Takeaways
1. Facade trades full functionality for simplicity — it exposes only what most clients need.
2. It defines a new simplified interface but adds no new behavior; the subsystem stays unaware of it.
3. Route all client code through the facade so subsystem changes only ripple to the facade.
4. Use additional/layered facades to avoid one god object and to decouple multiple subsystems.
5. It wraps an entire subsystem (vs Adapter, which usually wraps one object).

## Connects To
- **Adapter**: Adapter makes an existing interface usable (usually wrapping one object); Facade defines a new interface over a whole subsystem.
- **Abstract Factory**: an alternative when you only want to hide how subsystem objects are created.
- **Flyweight**: makes many small objects; Facade makes one object representing a whole subsystem.
- **Mediator**: similar goal of organizing tightly-coupled classes, but Mediator centralizes component communication while a subsystem stays unaware of its Facade.
- **Singleton**: a Facade is often turned into a Singleton (one instance usually suffices).
- **Proxy**: both buffer and lazily init a complex entity, but Proxy shares the service's interface (interchangeable); Facade does not.
