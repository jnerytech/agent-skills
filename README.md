# agent-skills

Personal collection of 50 agent skills (Claude Code, GitHub Copilot CLI, Amp, Codex, OpenCode and other Agent Skills hosts). Most are knowledge bases generated from technical and finance books with [book-to-skill](https://github.com/virgiliojr94/book-to-skill). The rest are study and investing tools.

## Install

```bash
npx skills add jnerytech/agent-skills --list                    # list skills without installing
npx skills add jnerytech/agent-skills --skill kafka-in-action    # install one
npx skills add jnerytech/agent-skills -s google-sre -s accelerate  # install several
```

### Claude Code

`-a claude-code` installs straight into Claude Code's skills folder and skips the agent picker:

```bash
# project-level → ./.claude/skills/<name>
npx skills add jnerytech/agent-skills -a claude-code -s apache-kafka-docs -y

# user-level (every project) → ~/.claude/skills/<name>
npx skills add jnerytech/agent-skills -a claude-code -s apache-kafka-docs -g -y

# everything
npx skills add jnerytech/agent-skills -a claude-code -s '*' -g -y
```

Restart Claude Code (or open a new session) to pick up the new skills; they appear under `/skills`. To update later: `npx skills update`.

Each skill lives in `skills/<name>/` with its own `SKILL.md`. The knowledge-base skills also contain `chapters/`, `glossary.md`, `patterns.md` and `cheatsheet.md`.

## Tools (6)

| Skill | What it does |
|---|---|
| [`anki-deck-audit`](skills/anki-deck-audit) | Audits an Anki flashcard deck (the TSV produced by pareto-study-kit / book-to-anki, or any Front/Back TSV) for the defects that make a deck expensive to study: … |
| [`aporte-dividendos`](skills/aporte-dividendos) | Analisa uma carteira de dividendos a partir de uma planilha XLSX de posição (ex.: export da B3 com abas de Ações e FIIs) e decide como distribuir um valor dispo… |
| [`book-study-kit`](skills/book-study-kit) | Generates ONE Anki flashcard file and ONE multiple-choice quiz file (plus its Anki-importable version) for an entire book, by triaging its chapters into real co… |
| [`book-to-anki`](skills/book-to-anki) | Builds the complete Anki study kit for an ENTIRE book: one flashcard file, one plain-text quiz and one Anki-importable quiz, by triaging chapters into real cont… |
| [`pareto-study-kit`](skills/pareto-study-kit) | Generates Anki-importable flashcards and 4-option multiple-choice quiz files from a chapter (PDF or Markdown), focused on the 20% of the content that drives 80%… |
| [`pdf-chapter-splitter`](skills/pdf-chapter-splitter) | Splits a PDF book into one PDF per chapter, using the PDF's own embedded bookmarks/outline to find chapter boundaries. |

## Knowledge bases — books (39)

| Skill | Source |
|---|---|
| [`accelerate`](skills/accelerate) | *Accelerate: The Science of Lean Software and DevOps* — Nicole Forsgren, Jez Humble & Gene Kim |
| [`ai-agents-and-applications`](skills/ai-agents-and-applications) | *AI Agents and Applications With LangChain, LangGraph, and MCP* — Roberto Infante |
| [`art-of-unit-testing`](skills/art-of-unit-testing) | *The Art of Unit Testing, Third Edition — with examples in JavaScript* — Roy Osherove |
| [`barsi-dividendos`](skills/barsi-dividendos) | *O Rei dos Dividendos: A Saga* — Luiz Barsi Filho |
| [`beck-tdd`](skills/beck-tdd) | *TDD: Desenvolvimento Guiado por Testes (Test Driven Development: By Example)* — Kent Beck |
| [`beyond-vibe-coding`](skills/beyond-vibe-coding) | *Beyond Vibe Coding: From Coding by Instinct to Coding with Purpose* — Addy Osmani |
| [`brownfield-dotnet`](skills/brownfield-dotnet) | *Brownfield Application Development in .NET* — Kyle Baley & Donald Belcham |
| [`clean-code-in-python`](skills/clean-code-in-python) | *Clean Code in Python, 2nd Edition* — Mariano Anaya |
| [`cohn-user-stories`](skills/cohn-user-stories) | *User Stories Applied: For Agile Software Development* — Mike Cohn |
| [`crafting-user-stories`](skills/crafting-user-stories) | *The Art of Crafting User Stories* — Christopher Lee |
| [`cwalina-framework-design`](skills/cwalina-framework-design) | *Framework Design Guidelines, 3rd Edition* — Krzysztof Cwalina, Jeremy Barton & Brad Abrams |
| [`dependency-injection-principles`](skills/dependency-injection-principles) | *Dependency Injection Principles, Practices, and Patterns* — Steven van Deursen & Mark Seemann |
| [`dive-into-design-patterns`](skills/dive-into-design-patterns) | *Dive Into Design Patterns* — Alexander Shvets |
| [`dive-into-refactoring`](skills/dive-into-refactoring) | *Dive Into Refactoring* — Alexander Shvets |
| [`dobovizki-csharp-concurrency`](skills/dobovizki-csharp-concurrency) | *C# Concurrency* — Nir Dobovizki |
| [`docs-for-developers`](skills/docs-for-developers) | *Docs for Developers: An Engineer's Field Guide to Technical Writing* — Jared Bhatti, Zachary Sarah Corleissen, Jen Lambourne, David Nunez & Heidi Waterhouse |
| [`dornelas-fiis`](skills/dornelas-fiis) | *Aprenda a Investir em Fundos Imobiliários* — Eric Dornelas |
| [`enterprise-vibe-coding`](skills/enterprise-vibe-coding) | *Enterprise Vibe Coding for Agentic Engineering* — Valentina Alto |
| [`fifty-quick-ideas-tests`](skills/fifty-quick-ideas-tests) | *Fifty Quick Ideas to Improve Your Tests* — Gojko Adzic, David Evans & Tom Roden |
| [`fowler-refactoring`](skills/fowler-refactoring) | *Refatoração: Aperfeiçoando o Projeto de Código Existente, 2ª ed* — Martin Fowler |
| [`google-sre`](skills/google-sre) | *Site Reliability Engineering: How Google Runs Production Systems* — Betsy Beyer, Chris Jones, Jennifer Petoff & Niall Richard Murphy |
| [`hohpe-eip`](skills/hohpe-eip) | *Enterprise Integration Patterns* — Gregor Hohpe & Bobby Woolf |
| [`huyen-ai-engineering`](skills/huyen-ai-engineering) | *AI Engineering: Building Applications with Foundation Models* — Chip Huyen |
| [`kafka-in-action`](skills/kafka-in-action) | *Apache Kafka in Action* — Anatoly Zelenin & Alexander Kropp |
| [`khorikov-unit-testing`](skills/khorikov-unit-testing) | *Unit Testing Principles, Practices, and Patterns* — Vladimir Khorikov |
| [`kubernetes-month-of-lunches`](skills/kubernetes-month-of-lunches) | *Learn Kubernetes in a Month of Lunches* — Elton Stoneman |
| [`kubernetes-secrets-handbook`](skills/kubernetes-secrets-handbook) | *Kubernetes Secrets Handbook* — Emmanouil Gkatziouras, Rom Adams & Chen Xi |
| [`metzgar-dotnet-core`](skills/metzgar-dotnet-core) | *.NET Core in Action* — Dustin Metzgar |
| [`o-segredo`](skills/o-segredo) | *O Segredo (The Secret)* — Rhonda Byrne |
| [`padroes-implementacao`](skills/padroes-implementacao) | *Padrões de Implementação* — Kent Beck |
| [`pro-dotnet-memory-management`](skills/pro-dotnet-memory-management) | *Pro .NET Memory Management, 2nd Edition* — Konrad Kokosa, Christophe Nasarre & Kevin Gosse |
| [`programacao-extrema`](skills/programacao-extrema) | *Programação eXtrema (XP) Explicada: Acolha as Mudanças* — Kent Beck |
| [`prompt-engineering-generative-ai`](skills/prompt-engineering-generative-ai) | *Prompt Engineering for Generative AI: Future-Proof Inputs for Reliable AI Outputs at Scale* — James Phoenix & Mike Taylor |
| [`reengineering-legacy-software`](skills/reengineering-legacy-software) | *Re-Engineering Legacy Software* — Chris Birchall |
| [`specification-by-example`](skills/specification-by-example) | *Specification by Example: How Successful Teams Deliver the Right Software* — Gojko Adzic |
| [`the-kubernetes-book`](skills/the-kubernetes-book) | *The Kubernetes Book (2024)* — Nigel Poulton |
| [`unix-linux-sysadmin`](skills/unix-linux-sysadmin) | *UNIX and Linux System Administration Handbook, 5th ed (2017)* — Nemeth, Snyder, Hein, Whaley & Mackin |
| [`vibe-coding-architecture-at-scale`](skills/vibe-coding-architecture-at-scale) | *Vibe Coding Architecture at Scale* — Peter Isberg |
| [`working-effectively-legacy-code`](skills/working-effectively-legacy-code) | *Working Effectively with Legacy Code* — Michael C. Feathers |

## Knowledge bases — documentation and articles (5)

| Skill | Source |
|---|---|
| [`apache-kafka-docs`](skills/apache-kafka-docs) | *Apache Kafka 4.3 Documentation* |
| [`claude-code-docs`](skills/claude-code-docs) | the Claude Code documentation on memory, skills, subagents and hooks |
| [`aws-agentcore-guides`](skills/aws-agentcore-guides) | Hidekazu Konishi's 15-article series on Amazon Bedrock AgentCore and enterprise AI agents |
| [`supabase-docs`](skills/supabase-docs) | the full Supabase documentation |
| [`supabase-self-hosting`](skills/supabase-self-hosting) | the Supabase Self-Hosting guides (Docker) |

## Notes

- The knowledge-base skills contain **synthesized summaries**: frameworks, principles, techniques and anti-patterns, organized for an agent to consult. They do not reproduce the original text and do not replace the works. All rights to the books and their content belong to their authors and publishers. Read the originals.
- `apache-kafka-docs` derives from the Apache Kafka documentation (Apache License 2.0). `supabase-*` derive from the public Supabase documentation. `claude-code-docs` derives from the public Claude Code documentation (code.claude.com/docs).
- Some tool skills (`aporte-dividendos`, `book-to-anki`) were built for a specific local setup and reference paths and agents from that environment. Adjust them before use.
- Investment-related skills (`aporte-dividendos`, `barsi-dividendos`, `dornelas-fiis`) are study material, not financial advice.
