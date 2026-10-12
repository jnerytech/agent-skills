# Chapter 7: Finetuning

## Core Idea
Finetuning adapts a model by adjusting its weights (vs prompt-based methods that adapt via instructions/context); it is a form of transfer learning best used for *form* (behavior, style, syntax) while RAG handles *facts* (information). Because finetuning is memory-bound, most of its modern techniques (PEFT, LoRA, quantization) exist to shrink the memory footprint.

## Frameworks Introduced
- **Finetuning vs RAG decision framework**: diagnose whether failures are information-based or behavior-based.
  - When to use: after prompting is maxed out and the model still fails.
  - How: information-based failures (wrong/outdated/missing facts) → RAG; behavior-based failures (irrelevant-but-correct outputs, wrong format/syntax, unsafe) → finetuning. "Finetuning is for form, RAG is for facts." Start with RAG (easier, often bigger boost); combine both for max performance.
- **Adaptation workflow (escalation ladder)**: prompt → add examples (1–50) → RAG (term-based first, e.g. BM25) → branch: more advanced RAG (embedding-based) for info failures vs finetuning for behavior failures → combine. Define the eval pipeline *before* any step.
  - How: embedding retrieval adds inference complexity; finetuning adds model-development complexity but leaves inference unchanged.
- **PEFT (parameter-efficient finetuning)** (Houlsby et al., 2019): achieve near-full-finetuning quality while training orders of magnitude fewer parameters by inserting small trainable modules in the right places.
  - When to use: limited memory/data; serving many task-specific models on one base.
  - How: two buckets — adapter-based (additive) methods and soft prompt-based methods.
- **LoRA (Low-Rank Adaptation)** (Hu et al., 2021): for weight matrix W (n×m), learn W' = W + (α/r)·AB where A is n×r, B is r×m, rank r small.
  - When to use: default first finetuning method; multi-model serving on shared base.
  - How: freeze W, train only A and B. Apply to attention matrices Wq, Wk, Wv, Wo (Wq+Wv if only two); r typically 4–64; tune ratio α:r (≈1:8 to 8:1).
- **QLoRA** (Dettmers et al., 2023): store weights in 4-bit NF4, dequantize to BF16 for forward/backward pass; paged optimizers spill to CPU. Finetunes a 65B model on one 48GB GPU.
- **Model merging**: combine multiple (often finetuned) models into one — via summing (linear combo, SLERP), layer stacking (frankenmerging), or concatenation.

## Key Concepts
- **Transfer learning**: reuse knowledge from one task to accelerate a related task (Bozinovski & Fulgosi, 1976).
- **Sample efficiency**: learning target behavior from fewer examples (finetuning a base model may need hundreds vs millions from scratch).
- **Trainable vs frozen parameters**: parameters updated during finetuning vs kept unchanged; memory scales with trainable count.
- **Backpropagation**: training = forward pass (compute output) + backward pass (loss → gradients → optimizer updates weights).
- **Quantization**: convert values to a lower-bit format (FP32→FP16/INT8/INT4) to cut memory; PTQ (post-training) is most common.
- **Mixed precision**: keep a high-precision weight copy while computing gradients/activations in lower precision (AMP automates this).
- **Full vs partial finetuning**: update all parameters vs only some layers (partial is parameter-*inefficient* — needs ~25% of params for BERT-large to match full).
- **Low-rank factorization / intrinsic dimension**: pre-training compresses a model's intrinsic dimension, enabling few-parameter adaptation (Aghajanyan et al.).
- **Task vector (delta parameters)**: finetuned model minus base model; enables task arithmetic (add/subtract capabilities).
- **Catastrophic forgetting**: sequential multi-task finetuning makes a model forget earlier tasks; parallel-then-merge avoids it.
- **Continued pre-training**: self-supervised finetuning on cheap task-related data before expensive annotated data.

## Mental Models
- **Memory is the bottleneck.** Inference ≈ N×M×1.2 (weights + ~20% for activations/KV). Training = weights + activations + gradients + optimizer states; with Adam each trainable param adds 3 values. Every finetuning technique is a different lever on this equation: PEFT shrinks trainable-param count, quantization shrinks bits-per-value, gradient checkpointing trades compute for activation memory.
- **Finetuning is unlocking, not adding.** Per InstructGPT/Llama 3, post-training should make the model "know what it knows" — refine existing capability rather than inject new knowledge (that's RAG's job).
- **Modularity is LoRA's superpower.** Keeping W, A, B separate lets one base model serve hundreds of per-customer adapters (store 1 full matrix + many tiny adapters, swap tasks by loading only the adapter).
- **Merging > separate models** when you want one artifact with combined skills and lower memory, especially on-device.

## Anti-patterns
- **Finetuning before exhausting prompting**: high up-front + maintenance cost; most "prompting doesn't work" cases were minimal/unsystematic prompt experiments.
- **Assuming general models fail on domain tasks**: GPT-4-0314 beat the purpose-built BloombergGPT (50B, ~$1.3–2.6M to train) on financial benchmarks.
- **Finetuning one task in isolation**: degrades other tasks (alignment tax); finetune on all queries you care about, or use separate/merged models.
- **Loading a model in the wrong precision**: Llama 2 was BF16; loading as FP16 silently wrecked quality.
- **Cranking LoRA rank**: beyond a point r adds no quality and may overfit; the adapter memory is already negligible vs weights — quantize the base instead.
- **Concatenation merging**: doesn't reduce memory vs serving separately; rarely worth the extra params.

## Code Examples
None in this chapter. (PTQ is "a few lines" in PyTorch/TensorFlow/HF Transformers; finetuning frameworks named: LLaMA-Factory, unsloth, HF PEFT, Axolotl, LitGPT; distributed: DeepSpeed, PyTorch Distributed, ColossalAI.)

## Reference Tables

Memory per trainable parameter by optimizer (backward pass):

| Optimizer | Extra values/param (gradient + state) |
|---|---|
| SGD (vanilla) | 1 (grad only) |
| Momentum | 2 |
| Adam | 3 |

Finetuning vs RAG:

| Failure type | Symptom | Fix |
|---|---|---|
| Information-based | factually wrong, outdated, missing private data | RAG (start BM25) |
| Behavior-based | correct-but-irrelevant, wrong format/syntax, unsafe | Finetuning |

Numerical formats: FP32 (4B), FP16 (2B, more precision), BF16 (2B, more range/less precision), TF32 (19 bits, NVIDIA), INT8/INT4, NF4, FP8/FP4 minifloats, BitNet b1.58 (1.58 bits).

## Worked Example
**Can I full-finetune a 7B model on one GPU?** Weights in FP16 (16-bit) = 7B × 2 bytes = 14 GB. Full finetuning with Adam adds gradients + optimizer states = 7B × 3 × 2 bytes = 42 GB. Total = 56 GB (excluding activations) — exceeds consumer GPUs (12–48 GB). Switch to **LoRA**: apply r=2 to Wq, Wk → only ~3.28M trainable params (Llama-2-13B figure), so gradient+optimizer memory ≈ 3.28M × 3 × 2 ≈ ~20 MB and the adapter itself ≈ 6.55 MB. The 14 GB of frozen weights dominates — now feasible. Add **QLoRA** (4-bit NF4 base): weights drop to ~3.5 GB, fitting comfortably. The lever that mattered most was cutting *trainable* params (PEFT) and bits-per-value (quantization), not the adapter size.

## Key Takeaways
1. Start with prompting, then RAG; finetune only for behavioral/format problems and only after systematic prompt experiments.
2. "Finetuning is for form, RAG is for facts" — and RAG with the *base* model often beats RAG with a finetuned model on current-events QA (Ovadia et al.).
3. Memory footprint = f(total params, trainable params, bits-per-value); training needs far more than inference because of gradients + optimizer states.
4. PEFT/LoRA reach near-full-finetuning quality with orders of magnitude fewer trainable parameters (LoRA: 0.0027% of full for GPT-3) and are sample-efficient.
5. LoRA's modularity (separate A, B) makes multi-model serving cheap; r=4–64 usually suffices and higher r rarely helps.
6. Quantize the base model (QLoRA/NF4), don't chase smaller adapters — adapter memory is already negligible.
7. Model merging (parallel finetune → merge via summing/SLERP/stacking) gives multi-task models without catastrophic forgetting and enables on-device + upscaling use cases.
8. A small finetuned model can beat a much larger general model on a narrow task (Grammarly's Flan-T5 beat a GPT-3 variant at 1/60th the size).

## Connects To
- **Ch 2**: feature-based transfer, classifier heads, semantic parsing, transformer weight composition (which matrices LoRA targets).
- **Ch 4**: define the evaluation pipeline before adapting; model-selection criteria for choosing a base model.
- **Ch 5 & 6**: prompt engineering best practices that must precede finetuning; soft prompts as a prompting/finetuning crossover.
- **Ch 8**: distillation and acquiring/synthesizing instruction data — the real bottleneck of finetuning.
- **Ch 9**: inference optimization, prompt caching (which erased finetuning's token-saving edge), KV cache memory, training-vs-inference chip divergence.
