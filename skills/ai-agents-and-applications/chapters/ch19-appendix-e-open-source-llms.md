# Appendix E: Open source LLMs

## Core Idea
Open source LLMs are a practical alternative to hosted APIs like OpenAI's, trading some setup effort for lower cost, data privacy, and transparency; consumer hardware can run them locally via quantization and inference engines that often expose an OpenAI-compatible REST API, making it possible to swap a proprietary LLM for a local one with minimal code change.

## Key Concepts
- **Quantization**: reducing weight precision (typically from 16/32-bit float to 4-bit integer) to shrink model size and speed up inference at some cost to accuracy — e.g., Llama 2 7B drops from 13.5 GB to 3.9 GB at 4-bit.
- **GGUF / GGML**: Georgi Gerganov's model formats and tooling for running quantized LLMs efficiently on CPUs; GGUF is the newer, broader-support format.
- **llama.cpp**: the foundational C++ inference engine, originally built for running Llama on Apple silicon via 4-bit quantization; now cross-platform and the backend behind Ollama, llamafile, GPT4All, and LM Studio.
- **Ollama**: a batteries-included local LLM host (Windows/macOS/Linux) with an interactive CLI (`ollama run <model>`) and a REST server on port 11434; its native API is proprietary (not OpenAI-compatible), though its `/api/chat` payload mirrors OpenAI's structure.
- **vLLM**: a high-performance, GPU/Linux-focused inference library (PagedAttention, continuous batching, tensor parallelism) intended for production-grade serving of unquantized or quantized models, with an OpenAI-compatible server.
- **llamafile**: packages a GGUF model plus the llama.cpp executable into a single cross-platform file (via Cosmopolitan-Libc) that runs with no installation.
- **LM Studio**: a user-friendly desktop app with Hugging Face-integrated model search/download, a chat UI, and an OpenAI-compatible local server.
- **LocalAI**: a Go-based router that exposes OpenAI-compatible endpoints while dispatching requests to backends such as llama.cpp or vLLM; distributed as Docker/Podman/Kubernetes images.
- **GPT4All**: a llama.cpp-based desktop engine with a graphical interface, language bindings, an OpenAI-compatible local server, and an optional LocalDocs RAG plugin (SBERT + embedded vector DB).
- **OpenAI-compatible REST API**: the `/v1/chat/completions`-style endpoint pattern that many inference engines implement, letting existing OpenAI client code or LangChain's `ChatOpenAI`/`OpenAI` wrappers point at `localhost:<port>` instead of OpenAI's servers.

## Mental Models
Proprietary (OpenAI) vs. open source LLMs is a trade-off along four axes:
- **Transparency**: proprietary models are black boxes (a compliance risk in regulated industries); open source models can be inspected, audited, and modified, but that shifts accountability for flaws onto the user and raises open-access security risks.
- **Privacy**: proprietary public-cloud APIs risk exposing sensitive data or IP; open source models can be deployed on-premises or in a private cloud, keeping data inside the corporate network and easing compliance with privacy regulations.
- **Cost**: open source avoids licensing fees but requires up-front capital (hardware) or ongoing cloud compute costs; total cost of ownership is usually lower medium-to-long-term, but for low, sporadic usage a pay-as-you-go proprietary model is often cheaper. High-token-volume tasks (e.g., large-document summarization) favor open source; low-text-volume patterns like RAG often favor proprietary APIs.
- **Control/community vs. turnkey SLAs**: open source favors organizations wanting customization and community-driven innovation; proprietary favors those wanting strict SLAs and a turnkey solution.
- **Development workflow**: a common pattern is prototyping against OpenAI during proof-of-concept, then transitioning to a local open source LLM in production once costs or privacy demand it — feasible with near-zero code change *if* the local inference engine exposes an OpenAI-compatible API.

## Code Examples
```python
# OpenAI Python library pointed at a local inference engine instead of OpenAI's API
from openai import OpenAI
port_number = '8080'
client = OpenAI(
    base_url=f'http://localhost:{port_number}/v1',
    api_key = "NO_KEY_NEEDED"
)
completion = client.chat.completions.create(
    model="mistral",
    messages=[
        { "role": "system", "content": "You are a helpful AI assistant." },
        { "role": "user", "content": "How many Greek temples are there in Paestum?" }
    ],
    temperature=0.7
)
print(completion.choices[0].message.content)
```
- **What it demonstrates**: switching from OpenAI's hosted API to any local OpenAI-compatible engine (Ollama, LM Studio, llama.cpp, vLLM, LocalAI, GPT4All, llamafile) only requires setting `base_url` to the local server and dropping the real API key.

```python
# LangChain's OpenAI wrapper against a local engine
from langchain_openai import ChatOpenAI
port_number = '8080'
llm = ChatOpenAI(openai_api_base=f'http://localhost:{port_number}/v1')
response = llm.invoke("How many Greek temples are there in Paestum?")
print(response.content)
```
- **What it demonstrates**: LangChain's `ChatOpenAI` needs only a `base_url`/`openai_api_base` change to target a local model instead of OpenAI, so downstream chains (e.g., a summarization engine) require no further rewrites.

```python
# vLLM offline batched inference (unique to vLLM among the engines covered)
from vllm import LLM, SamplingParams
prompts = [
    "How many temples are there in Paestum?",
    "Who built the aqueduct in Segovia?",
    "Is LeBron James better than Michael Jordan?",
    "Summarize the Lord of The Rings in three sentences.",
]
sampling_params = SamplingParams(temperature=0.7, top_p=0.95)
llm = LLM(model="mistralai/Mistral-7B-v0.1")
outputs = llm.generate(prompts, sampling_params)
for output in outputs:
    prompt = output.prompt
    llm_response = output.outputs[0].text
    print(f"Prompt: {prompt!r}, LLM response: {llm_response!r}")
```
- **What it demonstrates**: vLLM's offline batched-generation API processes a list of prompts in one call, a production-oriented capability not offered by the other consumer-focused engines.

## Reference Tables

**Table E.1 — Popular open source LLMs (selected columns)**

| Model | Developer | Type | Size (B params) | Context (K tokens) | License |
|---|---|---|---|---|---|
| DeepSeek-V3 | DeepSeek AI | Foundation | 671 | 128 | MIT |
| Qwen2.5-72B-Instruct | Qwen | Instruct | 72 | 128 | Qwen License |
| Qwen2.5-Coder-32B | Qwen | Code | 32 | 32 | Apache 2.0 |
| Qwen2.5-Math-7B | Qwen | Domain-specific (Math) | 7 | 32 | Apache 2.0 |
| Llama-3.3-70B-Instruct | Meta Llama | Instruct | 70 | 128 | Llama 3.3 Community License |
| Mixtral-8x22B-Instruct-v0.1 | Mistral AI | Instruct | 141 | 64 | Apache 2.0 |
| Mistral-7B-v0.3 | Mistral AI | Foundation | 7 | 32 | Apache 2.0 |
| Gemma-2-27b-it | Google | Foundation | 27 | 8 | Gemma License |
| Falcon3-10B-Base | TII-UAE | Foundation | 10 | 32 | Falcon LLM License |
| Phi-3.5-MoE-instruct | Microsoft | Instruct | 41.9 | 128 | MIT |

Model types: Foundation (raw, general-purpose, best for fine-tuning/research), Instruct (tuned to follow instructions/QA), Code (generate/explain/debug code), Domain-specific (specialized industry/business use).

**Table E.3 — Local inference engine comparison**

| Engine | Backend | Installer | OS | OpenAI REST compat | Native bindings | Desktop UI |
|---|---|---|---|---|---|---|
| llama.cpp | llama.cpp | No (build from source) | macOS, Linux, Windows | Yes | Python, Java, C#, Go, Scala, Ruby, Rust, JS/Node.js | No |
| Ollama | llama.cpp | Yes | macOS, Linux, Windows | No (proprietary API; `/api/chat` OpenAI-like payload) | Python, JavaScript | No |
| vLLM | vLLM | Yes (pip) | Linux | Yes | Python | No |
| llamafile | llama.cpp | Yes (single file) | macOS, Linux, Windows | Yes | N/A | No |
| LocalAI | llama.cpp and vLLM | Docker image | Any Docker host | Yes | N/A | No |
| GPT4All | llama.cpp | Yes | macOS, Linux (Ubuntu), Windows | Yes | Python | Yes |
| LM Studio | llama.cpp | Yes | macOS, Linux (Ubuntu), Windows | Yes | Python | Yes |

## Worked Example
The appendix converts the chapter 4 research summarization engine from OpenAI to a local LLM:
1. **Duplicate the project**: copy the `ch04` folder to `apE` to compare both versions side by side.
2. **Choose an engine**: pick a user-friendly, OpenAI-compatible engine — the author uses LM Studio (GPT4All is an equivalent alternative).
3. **Start the local server**: in LM Studio, open the Server menu, set a port (e.g., 8080), and start the server so it accepts OpenAI-compatible requests.
4. **Modify `get_llm()`** in `llm_models.py`. Original:
   ```python
   from langchain.llms.openai import OpenAI
   openai_api_key = 'YOUR_OPENAI_API_KEY'
   def get_llm():
       return OpenAI(openai_api_key=openai_api_key, model="gpt-4o-mini")
   ```
   Modified to target the local server:
   ```python
   def get_llm():
       port_number = '8080'
       client = OpenAI(
           base_url=f'http://localhost:{port_number}/v1',
           api_key = 'NO-KEY-NEEDED',
           model='mistral'
       )
       return client
   ```
   A configurable variant adds an `is_llm_local` flag to switch between the OpenAI client and the local client at runtime, without touching the rest of the pipeline.
5. **Run and compare**: executing `chain_try_5_1.py` against the local LLM produces output of similar accuracy to the OpenAI version for this summarization task, but noticeably slower inference — especially without a GPU — confirming that a quantized local LLM suits development/experimentation, while production would need better hardware (GPU-backed LM Studio) or a production-grade engine like vLLM.

## Key Takeaways
1. Design LLM-calling code (e.g., a `get_llm()` factory) around the OpenAI client/LangChain `ChatOpenAI` interface from the start, so switching between OpenAI and a local model is a `base_url`/`api_key`/`model` change, not a rewrite.
2. Match the inference engine to the goal: llamafile or Ollama for first experiments, LM Studio/GPT4All for a GUI-driven workflow, vLLM or llama.cpp for production control and high-end GPU deployments.
3. Quantization (4-bit via GGUF/GGML, GPTQ, NF4, etc.) is what makes multi-billion-parameter models runnable on 16-32 GB consumer laptops without a dedicated GPU.
4. Ollama's native REST API is not OpenAI-compatible — reach for its `/api/chat` endpoint or its Python/LangChain wrappers directly rather than reusing OpenAI client code unmodified.
5. Expect a real accuracy/speed trade-off: local quantized models can match hosted-API output quality on straightforward tasks (e.g., summarization) but run substantially slower, particularly on CPU-only hardware.
6. Open source vs. proprietary is a cost/privacy/control decision, not a strictly technical one — weigh expected token volume, data sensitivity, and in-house deployment skill before committing to either path.

## Connects To
- **Ch 1**: Which LLMs to choose
- **Appendix C**: Choosing an LLM
