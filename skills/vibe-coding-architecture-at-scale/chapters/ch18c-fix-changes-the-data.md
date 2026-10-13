# Chapter 18c: When the Fix Changes the Data

## Core Idea
Some bugs carry weight: if a value has been encoded, encrypted, hashed or serialized incorrectly for long enough, the incorrect behavior *is* the format. "Fixing" the logic orphans every persisted record, silently, and no test exercising fresh input will notice. Before fixing an encoding path, ask one question: does correct data exist under the old behavior? If it does, the fix is a breaking data-format change. It needs expand-contract and a human owner, and an agent may propose it but must never merge it.

## Frameworks Introduced
- **The Data-at-Rest Test: "Does correct data exist under the old behavior?"**
  - When to use: before applying any fix to encoding, encryption, hashing, serialization, validation or decoding logic whose output is persisted or consumed downstream.
  - How: trace whether the current code path could ever have produced output that something downstream reads *successfully*, meaning *without error*, not necessarily *as originally intended*. **If no** (the old path only ever produced garbage, exceptions, or a state nothing could rely on), there's no meaning to preserve, so fix it in place in the same commit as the test that caught it. **If yes**, it's a breaking change to a data format: it needs a new encoding version, a migration path, and a human who owns the decision. The test deliberately **doesn't ask whether the old behavior was intended**. Intent is irrelevant. Only the existence of dependents on the current mapping counts.
- **Expand-Contract for Encodings** (from Ambler & Sadalage's *Refactoring Databases*):
  - When to use: the data-at-rest test says yes.
  - How: **Expand**: introduce the corrected behavior as a new, explicitly versioned encoding (a version tag, format byte or schema field) *alongside* the old one, so both can be decoded at the same time. **Migrate**: new writes use the corrected encoding, and a deliberate, reviewed backfill re-encodes existing values *where that's possible*. If it isn't possible, the bug is irreversible, and that goes prominently in the report to the owner. **Contract**: remove support for the old encoding only once nothing writes or expects it, as its own deliberate change.
- **The Rule for the Agent ("propose, don't merge" for data)**: if data at rest depends on the current behavior, an agent may propose the fix but may not merge it.
  - When to use: as a standing rule for any agent fixing bugs in persistence-adjacent code.
  - How: the agent runs the data-at-rest test itself and writes down the answer, with blast radius and migration needs. A human outside the diff signs off on whether anything downstream still needs yesterday's wrong answer. Add this to Ch 11b's no-AI list (crypto primitives, secret handling, safety-critical paths): *any fix whose correctness depends on what is already stored*.

## Key Concepts
- **Load-bearing bug**: a defect whose output has persisted long enough that downstream readers depend on it. Correcting it changes the meaning of existing data.
- **Orphaned data**: records written under the old mapping that the new code reads under a different one. Nothing crashes, and the answers are just silently wrong.
- **Restoring vs changing a mapping**: a fix that makes one stray path honor a convention the rest of the system already uses (restoring) is safe. A fix that changes the convention itself isn't.
- **Refactoring (Fowler)**: a structural change that leaves observable behavior unchanged. Changing what a stored value means alters observable behavior, so it's never a refactor, whatever the commit message says.
- **Hyrum's Law**: with enough users of an API, every observable behavior is depended on by somebody, whatever the contract promised.
- **Bug-for-bug compatibility**: Microsoft's discipline (Raymond Chen, *The Old New Thing*) of reproducing a known bug for apps written against it, treated as a first-class engineering decision.
- **Semantic Versioning**: any change to observable behavior is a major version, with no exception for "the old behavior was a bug."
- **Irreversible bug**: one where the original input can't be recovered from persisted output (e.g. modulus-reduced plaintext), so no migration can repair it.

## Mental Models
- Think of persisted output as a contract nobody signed. Once data exists, the encoding is a wire format (Ch 18), even if it began as a bug.
- Treat the agent's objective function ("make the failing test pass, make described behavior correct") as blind to the archive. A green unit test plus a closed ticket can still redefine six months of rows.
- Use the gene-renaming story as calibration. When HGNC renamed 27 human genes in 2020 (SEPT1 to SEPTIN1, MARCH1 to MARCHF1) because Excel auto-converts them to dates, they changed the data to match the bug. That's how high the bar sits for an agent quietly redefining stored values in a Tuesday commit.
- Data, unlike code, can't be `git reset --hard` to a known-good state (Ch 24). It has to be migrated forward by someone who understands what it meant before and after.

## Anti-patterns
- **Drive-by encoding fix**: correcting a decoder in place silently re-interprets every existing record. It's a data migration that got skipped.
- **Adding validation as a bugfix**: a new guard that rejects inputs that used to "succeed" breaks callers who rely on that, by accident or by undocumented design.
- **Judging safety by intent**: "nobody meant it to work that way" is irrelevant. Dependents on the current mapping are what matter.
- **Letting the agent answer the data-at-rest question unilaterally**: a confident, fluent "no" is cheap to produce and costs a lot to discover months later as numbers that don't add up.
- **Testing only fresh input**: no test that reads the archive means no signal on orphaned data.

## Worked Example
In the author's fully homomorphic encryption (FHE) library, where every persisted value is a ciphertext, three bugs turned up in one hunt:

| Bug | Fix | Correct data under old behavior? | Verdict |
|---|---|---|---|
| Key rotation decrypted negative residues as unsigned, so −5 came back as a ~150-digit positive integer | Apply the library's existing signed-decode convention (sign bit honored everywhere else) | **No.** No correctly rotated negative ciphertext ever existed | Fixed in place, same commit as the test |
| String encoding stops at the first `\0`, so `"\0abc"` round-trips as `"abc"` | Length-prefix strings (as the byte-array type already does) | **Yes.** Persisted ciphertexts with embedded NULs currently decode to truncated values consumers read | Not committed; written report to owner; needs a versioned encoding |
| Over-long plaintext is silently reduced modulo the key | Guard that rejects plaintexts too large for the key | **Yes.** Values "worked" and were consumed. Also irreversible: the original plaintext can't be recovered | Not committed; report flags breaking *and* irreversible |

The rotation fix restored a mapping the type's own contract already promised. The other two would have changed a mapping that live data depended on. All three were real bugs and all three fixes were correct engineering, but only one was a commit.

## Why It Works / Failure Mode
- **The data-at-rest test** works because it swaps an unanswerable judgment ("was this intended?") for a factual question an agent can investigate: could this path have produced output someone reads without error? It fails when the agent is trusted to resolve "yes" vs "no" on its own. That's exactly where a fluent wrong answer is cheapest and most expensive to discover.
- **Expand-contract for encodings** works because old and new mappings coexist under explicit versioning, so no record changes meaning in place. It breaks when the migrate step is assumed possible: some bugs destroy information, and the plan has to say so.

## Key Takeaways
1. Not every bug is safe to fix. Long-lived wrong encodings *are* the format.
2. Ask: "Does correct data exist under the old behavior?" No: fix in place. Yes: breaking change.
3. Ignore intent. Only dependents on the current mapping matter (Hyrum's Law).
4. A fix that changes what stored values mean isn't a refactor (Fowler) and is a major version (SemVer).
5. Ship breaking encoding fixes as expand-contract: a versioned new encoding, a reviewed backfill, and later retirement of the old one.
6. Agents may propose such fixes, with a written blast-radius report, but must not merge them.
7. Call out irreversible bugs explicitly. No migration can repair them.

## Connects To
- **Ch 1**: the agent's objective function, blind to the archive.
- **Ch 11b**: categories where the right constraint on the AI is its absence. This adds data-dependent fixes.
- **Ch 18**: expand/migrate/contract for schemas, generalized here to encodings.
- **Ch 18b**: "propose, don't install," extended to the meaning of stored bytes.
- **Ch 21**: proposal-not-merge at the CI gate.
- **Ch 24**: code reloads with git, and data can't.
- **Hyrum's Law** (Wright / Winters, *Software Engineering at Google*); **Fowler's *Refactoring***; **Ambler & Sadalage, *Refactoring Databases***; **Raymond Chen's bug-for-bug compatibility**; **SemVer**; **Ziemann et al. 2016 Excel gene-name corruption**.
