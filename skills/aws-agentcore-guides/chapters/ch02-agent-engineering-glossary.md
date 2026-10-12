# Chapter 2: AI Agent Engineering Glossary - Memory, Tools, Orchestration, and Protocols Explained

## Core Idea
This is a vendor-neutral vocabulary of 100 terms for the *agent layer* that sits above models and platforms. It is organized by stack layer so you know where to look: debugging → Foundation + Memory; extending → Tools + Protocols + Retrieval; scaling → Orchestration + Evaluation + Security + Lifecycle.

## Frameworks Introduced
- **Five-layer agent architecture**: Perception (ingest inputs and tool results) → Reasoning (decide) → Memory (persist what does not fit in the prompt) → Tools (act on the world) → Action (side effects, handoffs). **Observability** and **Guardrails** cut across every layer. *Use when* deciding which layer a bug or feature belongs to.
- **The agentic loop**: the model proposes an action → the action executes → the result goes back to the model → repeat until the goal is met. Frameworks mostly differ in *how* they implement this loop: as a graph (LangGraph), as a chat thread with tool calls, or as a managed runtime (AgentCore Runtime).
- **Memory hierarchy** (MemGPT): context window (fast, ephemeral) → session cache → persistent stores (vector, key/value, graph). Designing this hierarchy explicitly is what separates a chatbot from an agent that scales.
- **Single-agent first**: default to one agent with one toolset. Go multi-agent only when you can explain why: the subproblems differ enough that one prompt becomes unwieldy, or you need role/model specialization or parallelism.
- **Defense in depth**: the model *might try* anything, so bound what *can* happen with a sandbox, roots, strict tool permissions, and guardrails implemented *outside* the prompt.

## Key Concepts (thematic clusters)
**Reasoning patterns**: **ReAct** (Yao et al., 2022) alternates thought and action steps and remains the canonical baseline with a readable trace. **CoT** uses intermediate reasoning as a scratchpad. **ToT** explores branches with scoring and pruning, at higher cost, and helps where backtracking pays off. **Reflection / Self-Critique** spend one extra call on critique and revision, which is cheap and works best on verifiable outputs like code. **Plan-and-Execute** has a planner commit to a plan that executors follow, trading latency for reliability and inspectability.

**Memory**: **Short-term** holds the session's working state in the context window and is discarded unless it is persisted. **Long-term** survives across sessions and is fetched on demand (k/v, vector, graph). **Episodic** stores discrete past events ("what we decided yesterday"). **Semantic** stores generalized facts distilled by a background summarizer that overwrites older entries. **Compaction** continuously summarizes, deduplicates or evicts content to keep the window small.

**Tools**: **Tool definition** = name + description + schema, and the quality of the description predicts whether the model picks the tool at the right time. **Tool schema** is JSON Schema, and tight schemas (enums, required fields) reduce malformed calls. **Tool choice** forces or biases tool use and is the most reliable way to get structured output. **Tool error**: return failures to the model instead of crashing so it can self-correct.

**Protocols**: **MCP** (Anthropic, late 2024) covers agent↔tool via JSON-RPC with five primitives: tools, resources, prompts, sampling, roots. **A2A** (Google, 2025, now Linux Foundation, adopted by AgentCore) covers agent↔agent.

## Mental Models
- **MCP vs A2A**: MCP standardizes the agent-to-*tool* boundary, A2A the agent-to-*agent* boundary. Think of MCP as "LSP for LLM integrations".
- **Tool use vs function calling**: they are near-synonyms. "Function calling" is the OpenAI-flavored term, "tool use" the Anthropic-flavored one.
- **Computer use ⊃ browser use**: use them only when there is no API. The agent reads screenshots or the DOM and emits clicks and keystrokes.
- **Episodic vs semantic memory**: episodic is *what happened*, semantic is *what is true*.
- **Conversation buffer vs summary**: a buffer is faithful but grows linearly. A summary is compact but loses detail. Switch to summary or compaction before you hit the window.
- **Stdio vs Streamable HTTP**: use stdio when client and server are on the same machine (editors). Streamable HTTP (HTTP plus SSE on a single endpoint) is the recommended transport for remote servers and replaces the old separate SSE transport. WebSocket is *not* in the MCP spec.
- **Supervisor vs swarm**: a supervisor gives you one debuggable owner of routing and state. A swarm (peers using handoffs or a blackboard) is more resilient but has no single owner of the trajectory. **Hierarchical** = nested supervisors, where each level adds latency and another place for state to be miscommunicated.
- **Pipeline vs agent**: in a pipeline the code decides control flow; in an agent the model decides at runtime.
- **Faithfulness vs grounding**: faithfulness is the *metric* (is the output supported by the source?), grounding is the *design pattern* that aims for it. A faithful answer can still be wrong if the source is wrong.
- **Prompt injection vs jailbreak**: injection targets *task instructions*, jailbreak targets *safety policy*. **Indirect injection** arrives through retrieved content, so every data source becomes an attack surface.
- **Golden dataset vs evaluation set**: the golden set is the ground-truth subset with known-good outputs. An evaluation set can also include adversarial or long-tail cases without known answers.
- **Autonomy is a spectrum**: be autonomous by default and require human approval for high-impact actions (writes, payments, irreversible operations).

## Anti-patterns
- Putting guardrails *in the system prompt*. Implement them as separate models or rule engines so they cannot be jailbroken away.
- Trusting third-party MCP tool descriptions. In **tool poisoning**, whoever controls a tool description controls a slice of your system prompt. Limit blast radius with **MCP Roots**.
- Crashing on tool failures instead of returning a structured error to the model.
- Careless **parallel tool calls**, which amplify race conditions and rate-limit pressure.
- Shipping changes with no golden dataset or regression tests ("every change is a gamble").
- Evaluating only the final answer. **Trajectory evaluation** catches "right answer for the wrong reasons" and wasted tool calls.
- Treating a large context window as free. Cost and recall degrade well before the hard limit.

## Code Examples
JSON-RPC message shape carried by every MCP message (fields: `method`, `params`, `id`, `result`, `error`):
```json
{"jsonrpc": "2.0", "id": 1, "method": "tools/call", "params": {"name": "get_weather", "arguments": {"city": "Seattle"}}}
{"jsonrpc": "2.0", "id": 1, "result": {"content": [{"type": "text", "text": "Sunny"}]}}
```
*What it demonstrates*: MCP is transport-agnostic (stdio, Streamable HTTP, or WebSocket in practice) because everything is plain JSON-RPC.

## Reference Tables

**MCP primitives and mechanics**
| Term | What it is | Direction / purpose |
|---|---|---|
| Tool | callable function with a schema | client → server |
| Resource | URI-addressed data, read-only to the client | controlled read access |
| Prompt | named, parameterized template | shareable interaction patterns |
| Sampling | server asks the host to call an LLM, with user approval | *inverts* the direction; the host applies policy and consent |
| Roots | filesystem/URI scopes the server may touch | limit blast radius |
| Capability negotiation | handshake declaring optional features | keeps the core protocol small |
| MCP client | lives in the host, one per server | host arbitrates what the model sees |

**Retrieval toolbox (lift in roughly this order)**
| Technique | What it does | When it pays |
|---|---|---|
| Chunking | size, overlap, boundary policy | always; tune to the queries you serve, there is no universal best |
| Hybrid search | BM25 + dense with score fusion | exact terms and rare names *and* paraphrases |
| Reranker | cross-encoder re-scores top-k | "one of the highest-ROI moves" in production RAG |
| Query rewriting | cheap LLM call before retrieval | expand acronyms, split compound questions |
| HyDE | embed a hypothetical answer, not the query | the answer looks more like the target documents |
| Context compression | shrink passages before the model sees them | bridges high recall and a finite window |
| Knowledge graph | entities + typed relations (SPARQL/Cypher) | relationship traversal ("who reports to whom") |

**Frameworks**
| Framework | Idiom |
|---|---|
| LangGraph | explicit state graphs; persistence, streaming, human-in-the-loop |
| CrewAI | declarative crew of roles, goals, tasks; sequential or hierarchical |
| AutoGen (Microsoft Research) | conversational agents; two-agent solver/critic chat |
| Strands Agents (AWS) | lightweight, model-driven Python core; built-in MCP; used in AgentCore samples |
| Mastra | TypeScript agents and workflows with memory, RAG, evals |
| AgentCore Runtime | managed containerized microVMs; session isolation, MCP + A2A |

**Evaluation tools**: Ragas (RAG metrics: faithfulness, answer relevancy, context precision/recall), DeepEval (pytest-style tests for hallucination, bias, toxicity), Promptfoo (YAML matrix of prompts × models × test cases, used for regression in CI). Use **pairwise comparison** over absolute scores because pairwise judgments are more consistent. **LLM-as-a-Judge** risks: bias, inconsistency, cost.

**Observability**: **Trace** = one invocation end to end and the unit of debugging. **Span** = one named operation (LLM call, tool call, retrieval) with start time, duration, attributes and parent. **Session replay** re-runs a session deterministically, which only works if traces captured every non-deterministic input. **Token usage tracking** covers input, output, cached, reasoning and tool-result tokens. A **latency budget** sets sub-budgets for retrieval, model, tools and post-processing.

## Key Takeaways
1. An agent is defined by *model-decided control flow at runtime*. If the code decides, it is a pipeline.
2. Start single-agent with ReAct. Add Plan-and-Execute for inspectability, Reflection for verifiable outputs, and multi-agent only with a clear justification.
3. Design the memory hierarchy deliberately and run compaction continuously in long-running agents.
4. Tool description quality and schema tightness are your main levers on tool-call accuracy.
5. Treat all retrieved content and third-party tool descriptions as untrusted input. Sandbox and use roots.
6. Invest early in a golden dataset, regression tests in CI, and trajectory evaluation.
7. Latency budgets turn "it's slow" into architecture choices: caching, parallel calls, smaller routing models.

## Connects To
- ch01 Beginner's Guide: how AgentCore implements memory, MCP/A2A, sandbox and observability.
- ch03 Bedrock Glossary: model and platform layer terms (Knowledge Bases, Guardrails, embeddings).
- ch04 Impl Pt1: short- vs long-term memory strategies in AgentCore Memory.
- ch07 Impl Pt4 and ch09 Strands patterns: supervisor, swarm, graph, handoffs, agents-as-tools.
- ch06 and ch10: traces, spans, OTel, token and cost tracking.
- ch11 WAF: prompt and indirect injection defenses. ch12 Registry: tool and agent discovery governance (tool poisoning).
