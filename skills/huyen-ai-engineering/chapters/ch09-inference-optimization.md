# Chapter 9: Inference Optimization

## Core Idea
Inference optimization makes models faster and cheaper (without ideally changing quality) by attacking computational bottlenecks at three levels — model, hardware, and service. The dominant transformer/autoregressive bottlenecks are model size, sequential decoding, and the attention mechanism, and most workloads today are memory bandwidth-bound rather than compute-bound.

## Frameworks Introduced
- **Roofline / arithmetic intensity classification**: every operation is either compute-bound or memory bandwidth-bound based on arithmetic intensity (arithmetic ops per byte of memory access).
  - When to use: before choosing an optimization — profile (e.g., NVIDIA Nsight roofline chart) to know which wall you hit.
  - How: compute-bound → add chips / higher FLOP/s; memory bandwidth-bound → higher-bandwidth chips, quantization, KV cache reduction. Prefill is compute-bound; decode is memory bandwidth-bound.
- **Three-level optimization model (archery analogy)**: model-level (better arrows), hardware-level (stronger archer), service-level (refine the whole shooting process).
  - When to use: framing any optimization effort; production usually combines levels.
  - How: model-level may alter behavior; service-level keeps the model intact and shouldn't change output quality.
- **Accelerator selection (3 questions)**: Can the hardware run your workload? How long does it take? How much does it cost?
  - How: evaluate FLOP/s (compute), memory size (fit), memory bandwidth (speed); cloud pricing is usage-based and similar across providers.
- **Speculative decoding**: a fast draft (proposal) model generates K tokens; the target model verifies all K in parallel and accepts the longest agreeing prefix, then emits one extra token.
  - When to use: latency-critical decode; structured/predictable text (code) raises acceptance rate. Skip if MFU is already maxed (no idle FLOPs for free verification).
  - How: pick draft model sharing target's vocab/tokenizer; tune K (high K = fewer verify calls but lower acceptance). Turns decode's profile into prefill's.

## Key Concepts
- **TTFT (time to first token)**: latency of the prefill step; how fast the first token appears.
- **TPOT (time per output token)**: how fast each subsequent token is generated; total latency = TTFT + TPOT × output tokens.
- **Throughput / goodput**: output tokens/s across all requests; goodput = requests/s that meet the SLO (latency objectives).
- **MFU (Model FLOP/s Utilization)**: observed throughput ÷ theoretical peak FLOP/s throughput — the useful utilization metric, unlike nvidia-smi GPU utilization (just % time busy).
- **MBU (Model Bandwidth Utilization)**: (params × bytes/param × tokens/s) ÷ theoretical bandwidth.
- **KV cache**: stores key/value vectors of prior tokens to avoid recomputation during decode; grows linearly with sequence length and batch size (inference-only).
- **Quantization / distillation / pruning**: model-compression techniques — reduce precision, train a small mimic model, or zero/remove parameters.
- **Continuous (in-flight) batching**: completed responses return immediately and new requests fill freed batch slots.
- **Prompt cache (prefix/context cache)**: caches overlapping prompt segments (e.g., system prompt) so they're processed once.
- **Kernel / compiler / lowering**: a kernel is hardware-specific optimized code; a compiler lowers a model into hardware-compatible kernels.

## Mental Models
- Batching = bus vs. cars: more throughput per trip, but each rider's journey may get longer (latency/throughput trade-off).
- Prefill vs. decode are different beasts (compute-bound vs. bandwidth-bound) — running both on one machine makes them fight; decouple them onto separate instances.
- Decode is bandwidth-bound because each token requires loading all model weights from HBM while using few FLOPs — there are idle FLOPs that speculative/parallel decoding spends "for free."
- Utilization is a means, not an end: a higher MFU/MBU means nothing if cost and latency both rise.

## Anti-patterns
- **Optimizing for nvidia-smi "GPU utilization"**: it only measures % time busy, not efficiency — a chip can report 100% while doing 1 of 100 possible ops.
- **Reporting average latency**: outliers (one 3,000 ms request) skew the mean; use p50/p90/p95/p99 percentiles.
- **Static batching for variable-length LLM outputs**: short responses wait for the longest in the batch; prefer continuous batching.
- **Chasing highest utilization as the goal**: the real goal is jobs done faster and cheaper.
- **Pruning as a first move**: hard to do, hardware may not exploit sparsity, and gains are usually smaller than quantization/distillation.

## Code Examples
None in this chapter. (Notes that speculative decoding is implementable in ~50 lines of PyTorch and is built into vLLM, TensorRT-LLM, and llama.cpp.)

## Reference Tables

KV cache size = `2 × B × S × L × H × M` (batch, seq len, layers, model dim, bytes/value).

| Technique | Level | Bottleneck attacked | Quality impact |
|---|---|---|---|
| Quantization (weight-only) | Model | Memory/bandwidth | Small, usually safe |
| Distillation | Model | Model size | Behavior-approximating |
| Speculative / parallel decoding (Medusa, Lookahead) | Model | Autoregressive decode | None / verified |
| Inference with reference | Model | Decode (overlap input↔output) | Lossless |
| KV cache opt (PagedAttention, GQA/MQA, local windowed, cross-layer) | Model | Attention / KV memory | Architectural (train-time) |
| FlashAttention (kernel) | Model/HW | Attention compute | None |
| Continuous batching | Service | Throughput | None |
| Prefill/decode decoupling | Service | TTFT vs TPOT contention | None |
| Prompt caching | Service | Repeated prefill | None |
| Tensor / pipeline / replica parallelism | Service/HW | Fit + latency/throughput | None |

## Worked Example
Cost from throughput: hardware costs $2/h; decode throughput 100 tokens/s → $5.556 per 1M output tokens. If each request averages 200 output tokens, decoding 1K requests = $1.11. If prefill does 100 requests/min at $2/h, prefilling 1K requests = $0.33. Total per 1K requests = $1.11 + $0.33 = **$1.44**.

MBU check: a 7B model in FP16 (2 bytes/param) at 100 tokens/s uses 7B × 2 × 100 = 700 GB/s. On an A100-80GB (2 TB/s peak), MBU = 700 / 2000 = **70%**. Fewer bytes/param (quantization) directly frees bandwidth.

## Key Takeaways
1. Know your bottleneck first: prefill is compute-bound (drives TTFT), decode is memory bandwidth-bound (drives TPOT); most LLM inference today is bandwidth-bound.
2. There is an inherent latency/throughput trade-off — you can 2–3× throughput by sacrificing TTFT/TPOT; optimize for goodput (SLO-satisfying requests), not raw throughput.
3. Use MFU/MBU and latency percentiles, not nvidia-smi utilization or average latency.
4. The most impactful, broadly-applicable techniques: quantization, tensor parallelism, replica parallelism, and attention optimization.
5. Service-level techniques (continuous batching, prefill/decode decoupling, prompt caching) preserve model quality; model-level techniques can change behavior.
6. Match the technique to the workload: KV-cache opts for long context, prompt caching for long/overlapping prompts and multi-turn chat, replica parallelism when latency > cost.

## Connects To
- **Ch 2**: prefill/decode steps, attention, and KV cache mechanics originate here.
- **Ch 7**: quantization and numerical precision (TF32/FP16/FP8) underpin model compression and bandwidth savings.
- **Ch 8**: distillation as a compression technique reused here.
- **Ch 10**: integrating these optimizations into a cohesive production AI system.
