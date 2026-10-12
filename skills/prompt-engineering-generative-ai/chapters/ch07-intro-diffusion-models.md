# Chapter 7: Introduction to Diffusion Models for Image Generation

## Core Idea
Diffusion models are trained to reverse a noising process, conditioned on a text description, so they can turn random noise into an image that matches a prompt. Prompt engineering for images can therefore be seen as **navigating latent space** to find the image that matches your vision. The three main vendors (OpenAI DALL-E, Midjourney, Stable Diffusion) made very different choices about business model and features, so you choose a model per task.

## Frameworks Introduced
- **Diffusion (noise → denoise) process**: during training, random noise is added to images over many steps, and the model learns to predict how to remove it, conditioned on the caption. If the result doesn't match the description, the weights are adjusted. At inference, the model starts from random noise and denoises toward the prompt.
  - When to use: as the mental model for why parameters such as seed, denoising strength, and guidance (Classifier Free Guidance) change the output.
  - Why it works / failure mode: the approach comes from physics simulations of particles diffusing through a medium. The model learns patterns rather than storing copies. A diffusion model is only a few GB, and a researcher attempt to reproduce 350,000 training images from Stable Diffusion succeeded for only 109 (Carlini et al., 2023). Because it learned from billions of scraped image-caption pairs, though, it can mimic popular styles and artists, which is the source of the copyright controversy.
- **Encode → generate → decode pipeline**: the prompt is encoded into vectors (embeddings), the diffusion model generates an image matching those vectors in latent space, and the result is decoded back into pixels.
- **Prompt engineering as latent-space navigation**: each prompt is an address in the model's map of every possible image. Similar images sit close together, and the space is continuous, so you can **interpolate** between two points and still get coherent images (e.g. dog → bowl of fruit).
  - How: iterate on word combinations (and later, in Ch 8–9, on modifiers, weights, and negative prompts) to move toward the region of latent space you want.
- **Model selection by task** (the authors' own workflow): DALL-E 3 for composition and ChatGPT convenience, Midjourney for aesthetics, Stable Diffusion for flexibility, extensibility, and building products. Compare the same prompt across models (e.g. "a corgi on top of the Brandenburg Gate").

## Key Concepts
- **Diffusion model**: a generative model class (introduced in 2015) that creates images by iteratively denoising random noise, conditioned on text.
- **Denoising**: removing predicted noise step by step. As a Stable Diffusion parameter, it controls how much noise is added to a base image for the model to remove.
- **Latent space**: a continuous map of every image the model can generate. A vector (a list of numbers) is a location in it.
- **Embeddings**: the vector representation of a prompt or image. Similar concepts are near each other.
- **Interpolation**: moving between two latent points while still producing valid intermediate images.
- **Classifier Free Guidance (CFG)**: how closely the image follows the prompt.
- **Seed**: the starting random noise. Fixing it makes results reproducible.
- **Inpainting / Outpainting**: regenerate only a selected region / extend the image beyond its borders (added to DALL-E 2 in August 2022).
- **Negative prompting, weighted terms, Describe**: Midjourney features for removing concepts, increasing a concept's weight, and reverse-engineering a prompt from an uploaded image. Stable Diffusion later added equivalents.
- **ControlNet / Segment Anything**: Stable Diffusion extensions (April 2023), usually used through the AUTOMATIC1111 web UI. ControlNet matches the pose or composition of a reference image; Segment Anything makes an inpainting mask from a click on an element.

## Mental Models
- Think of a **diffusion model as an artist who studied every image on the internet** and learned the patterns behind each subject and style, not as a "complex collage tool" that pastes stored copies.
- Think of **a prompt as coordinates in latent space**. Rewording moves you around the map, and nearby wording gives nearby images.
- Use **Midjourney** when aesthetics matter most (fantasy or photorealism). Use **DALL-E 3** when composition and ChatGPT integration matter. Use **Stable Diffusion** when you need control over parameters, fine-tuning on your own data, extensions, self-hosting, or a base to build a product on.
- What you learn about image prompting **transfers directly to text-to-video** (AnimateDiff, Runway Gen-2, Stable Video Diffusion, Sora).

## Anti-patterns
- **Expecting models to render text or anatomy reliably**: early DALL-E 2 (and others) produced garbled text and deformed hands, feet, and eyes. Choose newer models (Midjourney v5+, SDXL, DeepFloyd for text) when this matters.
- **Assuming one model is best at everything**: each model has its own quirks from its architecture, training method, and data. Compare the same prompt across models.
- **Relying on closed models when you need control**: DALL-E gave users little control over parameters and no way to fine-tune. Midjourney had no API and was available only through Discord.
- **Ham-fisted bias fixes**: DALL-E 2 silently added words like "black" or "female" to prompts, and Gemini drew criticism for a clumsy attempt to promote diversity. Both show that dataset bias isn't fixed by rewriting prompts behind the user's back.

## Reference Tables

**Model comparison (as of the 2024 edition)**

| Model | Access / business model | Strengths | Limitations |
|---|---|---|---|
| OpenAI DALL-E (2021) → DALL-E 2 (Apr 2022) → DALL-E 3 (in ChatGPT) | Closed. Waitlist until Sep 2022; OpenAI initially kept the copyright | Composition; inpainting/outpainting; ChatGPT integration | Few user parameters, no fine-tuning; early versions had garbled text and deformed anatomy; heavy safety filtering |
| Midjourney (v3 Jul 2022; v4 Nov 2022; v5 Mar 2023; v6 Dec 2023) | Subscription; paying users own generated images; Discord-only and public by default (private mode only on the top plan) | Best aesthetics; community learning; negative prompts, weights, `/describe`; upscale clicks possibly used as RLHF-like feedback | No API; Discord is a barrier to mainstream adoption |
| Stable Diffusion (Aug 2022; v1.5 Oct 2022; v2.0 Nov 2022; SDXL 1.0) | Open source; runs locally on ~8GB VRAM; weights on Hugging Face | Most flexible and extendable; every parameter exposed (CFG, denoising, seed); fine-tuning; ControlNet, Segment Anything, AUTOMATIC1111; what most AI businesses build on | v2.0's NSFW filtering was seen as censorship and degraded anatomy; misuse concerns. SDXL has 6.6B parameters vs 0.98B for v1.5 |
| Google Imagen / Gemini (Dec 2023) | Imagen never released publicly; Gemini 1.5 | Large resources | Criticized for a clumsy diversity intervention. (Ex-Googlers founded Ideogram, Aug 2023) |

**Exposed Stable Diffusion parameters**

| Parameter | Controls |
|---|---|
| Classifier Free Guidance | How closely the image follows the prompt |
| Denoising | How much noise is added to the base image for the model to remove |
| Seed | The random noise the denoising starts from |

## Worked Example
**Same prompt, different models.** The authors run `a corgi on top of the Brandenburg Gate` through DALL-E, Midjourney, and Stable Diffusion (Figure 7-12). Each output has a recognizably different style, which shows that the models have each developed their own aesthetic and capabilities. The comparison grounds the authors' rule of thumb: DALL-E 3 for composition, Midjourney for aesthetics, Stable Diffusion for flexibility. A second sample prompt for Midjourney v5+ shows how much its quality and stylistic range improved, with the hand and eye problems largely gone: `a group of best friends women eating salads and laughing while high fiving in a coffee shop, cinematic lighting`.

## Key Takeaways
1. Diffusion models learn to denoise random noise into an image, conditioned on an encoded text prompt.
2. Prompts are coordinates in a continuous latent space. Prompt engineering is a search through that space.
3. The models learn patterns rather than storing copies (only 109 of 350,000 attempted training images were reproduced), but they still raise copyright and bias questions.
4. Vendors differ much more than in the LLM space. Pick the model by task: composition (DALL-E 3), aesthetics (Midjourney), control, extensibility, and products (Stable Diffusion).
5. Stable Diffusion's open parameters (CFG, denoising, seed) and extensions (ControlNet, Segment Anything) are what make the advanced techniques in later chapters possible. SD v1.5 is the base for the ControlNet examples.
6. Image prompting skills carry over to text-to-video.

## Connects To
- **Ch 1**: the Five Principles apply to image prompts too (e.g. Give Direction through style, Provide Examples through reference images).
- **Ch 5**: embeddings and vector similarity are the same idea as the latent-space addresses here.
- **Ch 8**: Midjourney practices such as format modifiers, art-style replication, negative prompts, weights, and Describe.
- **Ch 9**: Stable Diffusion in depth: AUTOMATIC1111, Img2Img, Inpainting/Outpainting, ControlNet, Segment Anything, DreamBooth fine-tuning.
- **Ch 10**: Stable Diffusion as the image backend of AI-powered applications.
- **RLHF**: Midjourney's upscale clicks and image ratings are thought to work as human-feedback training data, similar to RLHF for ChatGPT.
