# Chapter 15: My Application Is All API Calls

## Core Idea

Some applications look like nothing but repeated calls into a third-party library (JavaMail, J2EE, .NET, a vendor SDK). The temptation is to say "there's nothing real here to test — we're just calling someone else's methods." That's how legacy projects start. The code grows, the API calls get tangled with real logic, and soon you can't change anything without running the whole app to see if it still works. You're back in the central dilemma: changes are uncertain, you didn't write the library, but you must maintain the glue.

API-intensive code is *harder* than homegrown code for two reasons. First, you can't see a design — all you see are API calls, so the hints that would normally suggest structure aren't there. Second, **you don't own the API**: you can't rename its classes, add methods, or reshape its interfaces to make your intent clearer.

The way out: nearly every system has a **computational core** that can be peeled away from the API calls. Write a one-sentence description of what the program *does for you*, list the responsibilities behind that sentence, and notice which responsibilities are genuinely tied to the API and which only seem to be. Then drive a seam between your logic and the library so you can test the logic with a fake in place of the real API.

## Frameworks Introduced

### Skin and Wrap the API

**What:** Make interfaces that mirror the API as closely as possible, then build thin wrapper classes that delegate to the real library. In production the wrapper forwards to the real API class; in tests you substitute a fake that implements the same interface. To minimize mistakes while you build the wrappers, **Preserve Signatures** — copy parameter lists verbatim so you can't transpose or drop an argument.

**When to use:**
- The API is **relatively small**.
- You want to **completely separate** your code from a third-party library (you may need to swap it later — see Ch. 14).
- You have **no tests and can't write them**, because you can't currently test *through* the API.

**How:** For each API class you depend on, define an interface and a wrapper that holds and delegates to the real instance. After this, all your code except a thin delegation layer can be put under test. **Limitation:** you can only wrap what you can subclass/intercept. In the mailing-list code, `Transport` is obtained from `Session`, and `Session` is a `final` class — Java won't let you subclass it, so a clean wrapper is awkward. A complicated API makes skinning expensive.

### Responsibility-Based Extraction

**What:** Identify the responsibilities the code performs *around* the API and extract methods (then classes) for them. You name an extracted method for the higher-level thing it accomplishes ("send a message") rather than the low-level API mechanics. Your code then depends on your own higher-level interfaces instead of raw API calls.

**When to use:**
- The API is **more complicated** (wrapping it all would be heavy).
- You have a **safe extract-method refactoring tool**, or you're confident you can extract by hand without breaking behavior.

**How:** Take a snippet (e.g., the SMTP-send block), ask "what is its overall goal and what does it need?", and extract it into a method on a new class. Example: pull `getTransport`/`connect`/`sendMessage` into a `MailSender.sendMessage(Message)` method, with a private `getSMTPSession()` helper. **Trade-off:** because you often drag some API objects along to get a higher-level name, the extracted method may itself stay hard to test — you've improved layering but not necessarily testability of that piece.

## Key Concepts

- **Computational core:** the real work the program does, distinct from input/output and API plumbing. Find it by writing a plain-language description of the program's purpose.
- **Responsibility separation:** treat the whole app as one big object and apply the responsibility-splitting heuristics from Ch. 20 ("This Class Is Too Big"). Even if you can't refactor immediately, naming the responsibilities improves every later decision.
- **Seam + enabling point:** the wrapper interface (or extracted interface) is an object seam; choosing the fake vs. the real implementation at construction is the enabling point.
- **Fake:** `FakeMailSender implements MailService` lets you exercise `MessageForwarder` in a harness without ever sending mail — pure *separation* (break the dependency) plus *sensing* (the fake records what it was asked to send).
- **Layering is unavoidable:** you can't break a system into smaller pieces without some ending up "higher level" than others. That's a feature — the high-level piece (`MessageForwarder`) is where the logic worth testing lives.

## Mental Models

- **"It's just API calls" is a lie the code tells you.** Behind the calls there is almost always a thread that sleeps and wakes, messages being *constructed and altered* (not merely relayed), and rules (subject-line marking, loop headers, roster filtering). That is real, testable logic.
- **Tied vs. only-seems-tied.** Walk each responsibility: receiving mail and sending mail are genuinely API-bound; *building* a forwarded message merely *uses* API message classes and can be tested with dummy messages; the periodic-wakeup timer has nothing to do with mail at all.
- **Two layers of wrapper, by intent.** A *thin* wrapper exists for testing (isolate the API); a *higher-level* wrapper exists to present a nicer interface to your application. They serve different goals.

## Anti-patterns

- **"No tests needed, it's simple."** The opening rationalization that grows every legacy API-glue monster.
- **One giant `main`/`process`/`doMessage`** where config parsing, polling, message construction, and transport are interleaved and nothing is reachable from a test.
- **Mirroring a huge, awkward API class-for-class** when Responsibility-Based Extraction would give cleaner, higher-level seams for far less work.
- **Forcing a wrapper around an unwrappable type** (e.g., a `final` class you can't subclass) instead of switching strategy.
- **Extracting for a pretty name but pretending the result is testable** when you dragged untestable API objects into the extracted method.

## Code Examples

Original send logic, buried inline among everything else:

```java
Session smtpSession = Session.getDefaultInstance(props, null);
Transport transport = smtpSession.getTransport("smtp");
transport.connect(host.smtpHost, host.smtpUser, host.smtpPassword);
transport.sendMessage(forward, roster.getAddresses());
```

After Responsibility-Based Extraction into its own class:

```java
public class MailSender {
    private HostInformation host;
    private Roster roster;

    public MailSender(HostInformation host, Roster roster) {
        this.host = host; this.roster = roster;
    }

    public void sendMessage(Message message) throws Exception {
        Transport transport = getSMTPSession().getTransport("smtp");
        transport.connect(host.smtpHost, host.smtpUser, host.smtpPassword);
        transport.sendMessage(message, roster.getAddresses());
    }

    private Session getSMTPSession() {
        Properties props = new Properties();
        props.put("mail.smtp.host", host.smtpHost);
        return Session.getDefaultInstance(props, null);
    }
}
```

## Worked Example

Start from the mailing-list server: one `main` that parses 8 command-line args, opens a roster file, loops forever, connects POP3, fetches INBOX, builds a forwarded `MimeMessage`, marks the subject with `[list]`, BCCs the roster, sends over SMTP, and sleeps.

1. **State the purpose in one sentence:** "It reads config and a roster, periodically checks for mail, and forwards each new message to everyone on the roster."
2. **List the responsibilities:**
   1. Receive each incoming message and feed it in.
   2. Send out a mail message.
   3. Build a new message per incoming message, based on the roster.
   4. Sleep, then wake periodically to check for mail.
3. **Classify by API-ties:** (1) and (2) are firmly JavaMail-bound. (3) uses message classes but is testable with dummy incoming messages — this is the real logic. (4) is just a timer; no mail involved.
4. **Design the seams** (Figure 15.1): `ListDriver` owns the timer thread and tells `MailReceiver` to check; `MailReceiver` reads mail and hands messages one at a time to a `MessageForwarder`; `MessageForwarder` builds per-recipient messages and sends them via a `MailSender`. Two interfaces — `MessageProcessor` and `MailService` — let the classes be tested independently.
5. **Choose the technique.** Try Skin and Wrap first: wrap `Transport`. But `Transport` comes from `Session`, and `Session` is `final` — can't subclass it cleanly. With refactoring tools available, switch to Responsibility-Based Extraction and pull out `MailSender` (above).
6. **Get the core under test.** Write `FakeMailSender implements MailService`, inject it into `MessageForwarder`, and now you can characterize the subject-marking and roster-fanout logic in a harness without ever touching a network — logic that was previously buried and unapproachable.

## Key Takeaways

- Legacy code is code without tests; "all API calls" is not an excuse — there is almost always a computational core to extract and cover.
- Write the one-sentence purpose, list responsibilities, and mark which are truly API-tied vs. only superficially.
- **Skin and Wrap the API** when the API is small or you must isolate from a third-party library and currently can't test through it; **Responsibility-Based Extraction** when the API is large and you have safe extract-method support.
- **Decision rule:** *Small/stable API or need full vendor isolation, no refactoring tools → Skin and Wrap. Large/complex API with reliable extract-method refactoring → Responsibility-Based Extraction.* When you can't wrap a type (e.g., it's `final`), fall back to extraction. Many teams do both — a thin wrapper for tests plus a higher-level wrapper for a cleaner app interface.
- A fake behind your own interface buys you separation and sensing at once; expect — and accept — that splitting produces higher- and lower-level pieces.

## Connects To

- **Ch. 14 (Dependencies on Libraries Are Killing Me):** the isolation motive behind Skin and Wrap, and swapping vendors.
- **Ch. 20 (This Class Is Too Big):** the responsibility-separation heuristics applied to "one big object."
- **Preserve Signatures (p. 312):** the safety move while hand-building wrappers.
- **Sensing & separation; fakes/mocks (Ch. 3–5):** object seams and enabling points that make the extracted core testable.
- **Legacy Code Change Algorithm:** identify change points → find test points → break dependencies → write characterization tests → change and refactor; this chapter is the "break dependencies / find test points" step for API-saturated code.
