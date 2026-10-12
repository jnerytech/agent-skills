# Cheatsheet — Prompt Engineering for Generative AI

## Diagnose a bad output → principle to apply
| Symptom | Likely cause | Do this |
|---|---|---|
| Generic, "average of the internet" | Vague direction | Add persona/style, rules, retrieved context, user interview answers |
| Format flips between runs, preamble breaks parser | Unspecified format | Example payload + "only return valid JSON/YAML" + parse/validate/retry |
| Right format, wrong style or edge cases | No examples | Add 1–3 diverse examples (image: base image / ControlNet) |
| "It worked when I tried it" | No evaluation | Blind A/B, 10+ runs × several cases, before shipping |
| Can't tell which instruction fails | Mega-prompt | Split into a chain; evaluate each link |
| Model invents facts | No grounding | Reference text + "I could not find an answer" fallback → RAG |

## Decision rules
- **When** a prompt is one-off → naive is fine. **When** reused/shipped → engineer against all five principles, because errors compound at scale.
- **When** choosing between direction and examples → direction first (cheaper; examples are hard to collect).
- **When** you have >3 examples → test count *and* diversity; look-alike examples kill creativity.
- **When** structure nests beyond 2 levels → drop regex for JSON/YAML; prefer YAML if escaping hurts.
- **When** you ask for counts ("10 items", "1,000 words") → validate in code; LLMs are bad at math.
- **When** grading with an LLM → validate the judge on known cases (FP/FN) and run programmatic checks first.
- **When** a cheaper/open model is tempting → GPT-4 references + exact-match/pairwise evals; switch on evidence.
- **When** text exceeds the window → Stuff (fits) · Refine (progressive extraction) · Map Reduce (scale, order irrelevant) · Map Re-rank (need best single answer).
- **When** knowledge is private/large/recent → RAG; **when** context is static → few-shot in the prompt.
- **When** the query names attributes (author, date, price) → metadata filter / self-querying retriever (temp 0).
- **When** one definitive or parallel action → function calling; **when** sequential tools + reflection → ReAct.
- **When** chains are slow → move them off the real-time path (server/batch).
- **When** end users write image prompts → rewrite them with an LLM first.
- **When** you want an artist's look → unbundle the style; avoid naming living artists.
- **When** `--no` isn't enough → negative `::` weights; tune several weights by grid search.
- **When** style copies but composition drifts → ControlNet; need a specific subject → DreamBooth.
- **When** an idea is unproven → Gradio prototype before full stack.

## Thresholds & defaults
| Item | Value |
|---|---|
| Token | ≈ ¾ word; 100 tokens ≈ 75 words |
| Few-shot | 1–3 safe; >3–5 test carefully |
| A/B runs | ≥5 per variant to start; 10+ per case, several cases, before trusting |
| Fine-tuning | ≥50 samples to try (OpenAI); beats prompting at a few thousand |
| RAG budget | (context − ~3K prompt/response) ÷ chunk size = k (e.g., 8K → 5 × 1,000) |
| Splitter example | chunk 1,500 / overlap 400 tokens (ch10); 500/50 (ch04) |
| Agent caps | set `max_iterations` (SQL agent default 15) + `max_execution_time` |
| CFG | 1 ignore · 3 creative · **7 balanced** · 15 adhere · 30 strict |
| Sampler | DPM++ 2M Karras / UniPC, 20–30 steps; avoid ancestral "a" for reproducibility |
| Img2Img | Euler, 50 steps, CFG 20–30 |
| SD Upscale | generic prompt "highly detailed", 150–200 steps, CFG 8–15, denoise 0.1–0.2 |
| Inpaint | fix: Original, denoise 0.2–0.4; replace: Latent Noise ≤0.8 (risky >0.4) |
| SDXL refiner | switch at 0.6, 30 steps (range 0.4–1.0, 20–50) |
| DreamBooth | 1 concept, rare token, 5 min / 20–30 images, ~1 GPU-hour |
| SD resolution | v1.5 512²; SDXL 1024² |

## Trade-off matrix — image models (2024)
| Need | DALL-E 3 | Midjourney | Stable Diffusion |
|---|---|---|---|
| Composition / ChatGPT convenience | ★★★ | ★★ | ★★ |
| Aesthetics out of the box | ★★ | ★★★ | ★★ |
| Parameter control / extensions / fine-tune | ★ | ★ | ★★★ |
| API / build products | ★★ | — (Discord) | ★★★ (self-host) |

## Tells & smells
- Long instruction list, no examples, never tested → **blind prompting**.
- "Sure, here's the JSON:" in output → missing format contract.
- Agent loops or calls tools for chit-chat → too many tools / ReAct without caps.
- Retrieved context looks relevant but answer is wrong → chunking or embedding-model mismatch.
- Image has frames/walls you didn't ask for → format pulled in correlated content; use `--no`.
- Inpainted region doesn't match → denoising too high or "Only masked" area.
