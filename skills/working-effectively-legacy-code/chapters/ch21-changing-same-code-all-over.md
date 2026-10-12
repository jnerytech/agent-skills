# Chapter 21: I'm Changing the Same Code All Over the Place

## Core Idea

One of the most frustrating symptoms in a legacy system: you plan a small change, then discover you have to make the *same* change in a dozen near-identical places. The instinct is to call for a grand reengineering effort — but Feathers' point is that you don't need one. Duplication is removed in small, mechanical, test-backed chunks *as you work*, and the payoff is disproportionate: every piece of duplication you eliminate collapses N change points into one. Fewer places to change means less to remember, fewer chances to miss a spot, and lower risk on every future edit.

The deeper claim of the chapter is that **duplication removal is design**. You are not "just cleaning up" — by extracting the repeated bits and naming them, you distill abstractions that were already latent in the code (a *field*, a *command body*). Designs *emerge* from this process; you mostly notice what is already there and move the code closer to its essence. The end state naturally satisfies the **Open/Closed Principle**: open for extension, closed to modification.

## Frameworks Introduced

**Removing duplication drives abstraction.** When you squeeze duplication out of an area, the extracted methods and classes correspond to real concepts. In the worked example, repeated string/null writes become a `writeField` concept; the repeated middle of two `write` methods becomes a `writeBody` concept; the list of arguments each command sends becomes a `fields` collection. None of these concepts were planned. Each appeared because the code was *already* treating certain variables the same way. The only creative act is choosing names — everything else is mechanical (move method, pull up, extract method).

The byproduct is **orthogonality** (Feathers' word for independence): one knob per behavior. Picture the system as a box with knobs on the outside. If exactly one knob controls each behavior, change is easy. Rampant duplication gives you many knobs for one behavior — change one, miss the rest, ship a bug. After refactoring, want to change how a field terminates? Edit `writeField` in one place. Need a command that nests other commands? Override `writeBody` in a new subclass. Behavior is localized in single, focused methods, so it is trivial to replace or extend.

**Open/Closed Principle** (first articulated by Bertrand Meyer): code should be *open for extension but closed to modification*. Good design means you barely change existing code to add features. After this chapter's refactoring, a brand-new command is just a `Command` subclass — no edits to existing classes, no copy/paste, no risk of mis-wiring variables. Feathers' tie-in: **when you remove duplication, code naturally starts to fall in line with the Open/Closed Principle**. You don't pursue OCP directly; it falls out of zealous duplication removal (plus the discipline of refactoring away any new duplication that subclassing introduces — "Programming by Difference").

## Key Concepts

- **Duplication and design are linked.** More duplication = more change points = more risk. Less duplication = abstractions surface = fewer, single-purpose change points.
- **Start small.** Remove tiny pieces of duplication first; it makes larger areas of duplication visible and the overall structure clearer.
- **Where you start doesn't dictate the destination.** Given `a(); a(); b(); a(); b(); b();`, you could group as `aa(); b(); a(); bb();` or `a(); ab(); ab(); b();`. Both beat the original and either can be refactored into the other later. Decide by which grouping yields a *nameable* concept.
- **Extract the differences.** When two methods look roughly the same, extract what differs into its own method. Often this makes the two methods *exactly* the same, so you delete one (pull it up to a superclass).
- **Designs emerge.** You don't plan most of the knobs; they appear as you distill duplication.

## Mental Models

- **The knob box.** Each behavior should have exactly one knob. Hunting for "all the places that write a field" is the smell of too many knobs.
- **Distillation, not invention.** Removing duplication "distills" the design that was already dissolved in the code. The concept of a *field* existed implicitly because some variables were already treated alike — refactoring just gives it a name.
- **Knobs happen naturally.** You can add knobs deliberately (e.g., splitting `write` into `writeHeader`/`writeBody`/`writeFooter`), but it's better when they fall out of duplication removal on their own.

## Anti-patterns

- **Copy/paste/modify to add a feature.** Cloning an existing command and changing variables introduces more duplication, is error-prone (you can mis-edit a variable), and is actually *slower* than subclassing in a de-duplicated design.
- **Over-thinking the target structure up front.** Feathers' first reaction is to step back and imagine the final classes — then he catches himself over-thinking. Remove small duplication first; the big picture clarifies itself.
- **Inconsistent names and abbreviations.** `XXXXMgr` vs. `XXXXMngr` forced a lookup every time; guessing was wrong >50% of the time. Abbreviations are okay only when used consistently; prefer full, consistent names (rename `AddEmployeeCmd` → `AddEmployeeCommand`).
- **Refactoring without tests.** Every step here runs the characterization tests. *Legacy code is code without tests*; you write them first, then refactor under their cover.

## Code Examples

Latent concept extracted by naming a repeated pair of writes:

```java
void writeField(OutputStream outputStream, String field) {
    outputStream.write(field.getBytes());
    outputStream.write(0x00);            // the terminating null, once
}
```

Extending behavior without modifying existing code (Open/Closed in action) — a command that nests other commands, added purely by subclassing:

```java
public class AggregateCommand extends Command {
    private List commands = new ArrayList();
    protected char[] getCommandChar() { return new char[] { 0x03 }; }
    public void appendCommand(Command newCommand) { commands.add(newCommand); }
    protected void writeBody(OutputStream out) {
        out.write(commands.getSize());
        for (Iterator it = commands.iterator(); it.hasNext(); ) {
            Command innerCommand = (Command) it.next();
            innerCommand.write(out);
        }
    }
}
// Everything else just works.
```

## Worked Example

Two Java command classes — `AddEmployeeCmd` and `LoginCommand` — each serialize to a stream: write `header`, `getSize()`, `commandChar`, a series of `string + 0x00` fields, then `footer`. The amount of code is small, but heavily duplicated. With characterization tests in place (cut for brevity but always running between steps), Feathers removes duplication in small moves:

1. **Extract `writeField`.** Each field write is `bytes` + `0x00`. Pull that pair into `writeField(outputStream, field)` and replace every string/null pair in `LoginCommand.write`.
2. **Introduce a `Command` superclass.** `AddEmployeeCmd` has the same string/null pattern, so create `Command`, **pull up** `writeField`, and have both subclasses use it.
3. **Extract `writeBody`.** Both `write` methods now share the same shape: header, size, command char, *some fields*, footer. Extract the differing part into `writeBody()`. Now both `write` methods are textually identical — but they can't be pulled up yet because they still read subclass data (`header`, `footer`, `commandChar`).
4. **Pull up common data.** `header`, `footer`, `SIZE_LENGTH`, `CMD_BYTE_LENGTH` have identical values in both classes — pull them up to `Command` (made `protected` temporarily to recompile and test).
5. **Abstract the difference.** Only `commandChar` differs (`0x01` vs `0x02`). Replace the field with an abstract `getCommandChar()` on `Command`, overridden per subclass. Now `write` reads nothing subclass-specific, so **pull up `write`** (introducing abstract `writeBody`).
6. **Pull up `getSize`.** The two `getSize` methods differ only in the per-field sums. Extract `getBodySize()`; the remainder becomes identical, so pull `getSize` up with abstract `getBodySize` per subclass.
7. **Extract `getFieldSize`.** Each body-size term is `field.getBytes().length + 1`. Extract `getFieldSize(field)` and pull it up; both `getBodySize` methods become a sum of `getFieldSize(...)` calls.
8. **Generalize with a `fields` list.** The last difference: each subclass enumerates its own arguments. Declare `protected List fields` in `Command`; each constructor just `fields.add(...)`s its arguments. Now `getBodySize` and `writeBody` iterate the list identically — **pull both up** and make all internal methods `private`.

Result: `Command` holds *all* the behavior. The subclasses are shells — a constructor that adds fields and a one-line `getCommandChar()`:

```java
public class LoginCommand extends Command {
    public LoginCommand(String userName, String passwd) {
        fields.add(userName);
        fields.add(passwd);
    }
    protected char[] getCommandChar() { return new char[] { 0x01 }; }
}
```

Feathers then plays out change scenarios to test the payoff: a new command = one subclass (vs. error-prone copy/paste before); a non-string argument = convert in the constructor (already solved — `yearlySalary` is an int turned into a string); a nesting command = override `writeBody` (the `AggregateCommand` above). Each change touches one place. That is orthogonality, and that is the Open/Closed Principle, arrived at not by design ambition but by removing duplication zealously.

## Key Takeaways

- Duplication removal is small, incremental, and test-backed — not reengineering. Do it as you work.
- Removing duplication **drives out abstractions**: the extracted methods/classes are concepts that were already latent in the code; you just name and place them.
- The concrete payoff is **fewer change points**: one knob per behavior (orthogonality) means changes are localized, faster, and lower-risk.
- De-duplicated code naturally satisfies the **Open/Closed Principle** — extend by subclassing/overriding, with little or no modification to existing code.
- Use names as your guide: extract a grouping only when you can name it; prefer full, consistent names over abbreviations.
- Always work under characterization tests — *legacy code is code without tests*, and refactoring without them is just changing code and hoping.

## Connects To

- **Chapter 8 (How Do I Add a Feature?):** *Programming by Difference* — add behavior by subclassing, then integrate by refactoring away the duplication that subclassing creates. This chapter is the "refactor away" half.
- **Chapter 13 (I Need to Make a Change, but I Don't Know What Tests to Write):** characterization tests are the safety net that makes this whole mechanical progression safe.
- **The Legacy Code Change Algorithm** (identify change points → find test points → break dependencies → write tests → make changes and refactor): duplication removal is the refactoring that follows once tests are in place.
- **Seams and enabling points (Chapter 4):** introducing the `Command` superclass and abstract methods (`getCommandChar`, `writeBody`) creates object seams — subclass overrides become enabling points where behavior can vary without editing the base.
- **Chapters 22–25 (refactoring under the radar / Sprout & Wrap):** shares the same discipline of small, safe, test-protected structural moves.
