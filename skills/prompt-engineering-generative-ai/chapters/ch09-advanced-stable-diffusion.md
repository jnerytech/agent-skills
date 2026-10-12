# Chapter 9: Advanced Techniques for Image Generation with Stable Diffusion

## Core Idea
Stable Diffusion is open source, so you can run it yourself and get control that hosted tools don't give you: weighted and switched prompts, Img2Img, upscaling, inpainting, ControlNet conditioning, SAM masks, and fine-tuning with DreamBooth. The authors drive almost all of this through the AUTOMATIC1111 web UI. Every technique is presented as a way to apply one of the Five Principles.

## Frameworks Introduced
- **Prompt Weights (AUTOMATIC1111 syntax)**: `(term)` multiplies attention by 1.1. `((term))` gives 1.1 × 1.1 = 1.21. `(term:1.5)` sets the weight directly. `[term]` lowers it to 0.9, the same as `(term:0.9)`.
  - When to use: one concept is too weak or too strong in the output, or a negative prompt alone doesn't remove something.
  - How: wrap the key tokens in parentheses or brackets. Weights also work in the negative prompt, where they push harder to remove a concept.
  - Principle(s): Give Direction.
  - Why it works / failure mode: it shifts the model's attention without rewriting the prompt. `[term]` is **not** a negative prompt. The concept stays in the image, just weaker.
- **Prompt Editing / Prompt Switching**: `[from:to:when]`. `when` is a step count or a fraction of the steps. `[A | B]` alternates between A and B on every step.
  - When to use: you want to blend concepts. Example: a face that feels familiar but isn't any one celebrity, which is safer ethically and legally. Another use is to start with something easy for the model and switch to the hard subject for the detail phase.
  - How: the early diffusion steps set the rough shapes and the later steps fill in detail. Choose the switch point to control which prompt shapes which part.
  - Principle(s): Give Direction ("Providing Direction").
  - Failure mode: the authors call it "something of a dark art" and got limited use out of it. Expect a lot of trial and error.
- **Img2Img**: uploads a base image as guidance, the counterpart of Midjourney's image prompt. It adds the **Denoising Strength** setting. At 0 the output equals the input. At 1 the input is fully replaced by noise, which is the same as plain txt2img.
  - When to use: you need control over style or composition starting from an existing image.
  - How: start with the Euler sampler, 50 steps, and CFG 20–30. Then try different combinations of denoising, CFG, and seed.
- **X/Y/Z Plot**: a script that renders a grid over up to three parameters, for example denoising × CFG.
  - When to use: to see what a parameter does and where its best value lies.
  - Principle(s): Evaluate Quality. The authors say this is one of the main advantages of running locally.
- **SD Upscale**: Img2Img → Scripts → SD Upscale. It splits the image into tiles, spreads them apart, and fills the gaps from the prompt plus the surrounding pixels.
  - How: use a generic prompt such as `highly detailed`, **not** your original prompt, or each tile gets inpainted with the whole scene. Use 150–200+ steps, CFG 8–15, and denoising 0.1–0.2. The default upscaler is R-ESRGAN 4x+, which can look cartoonish. One run doubles the size (512→1024). Send the result back to Img2Img to double it again.
  - Principle(s): Specify Format. Upscaling gets you any size or resolution you need for real-world use.
- **Interrogate CLIP**: works the prompt backward from an image. It's the counterpart of Midjourney's Describe.
- **SD Inpainting**: Img2Img → Inpaint subtab. You paint a mask with a brush, and a dedicated inpainting model is optional (`sd-v1-5-inpainting.ckpt`).
  - When to use: to fix or replace one area without touching the rest of the image.
  - How: set Inpaint area to **Whole picture**. It still paints only the mask. Reuse the seed if the image was AI-generated. Describe the whole image but **change the subject to the new element** (castle → statue). For small fixes, use Masked content = Original with denoising 0.2–0.4. To replace an element, use Latent Noise with denoising up to 0.8, but expect hallucinations above 0.4. Fill matches the surrounding colors. Raise Mask Blur (default 4) if you see seams. Fix one artifact at a time and repeat.
  - Principle(s): Give Direction ("Providing Direction").
- **"Poor man's outpainting"**: a script that runs with Resize mode set to Resize and fill and a high denoising strength. It extends pixels on the sides you pick and inpaints them. It's "inpainting with extra steps" and hallucinates a lot.
- **ControlNet**: a family of models that condition generation on a preprocessed input image: edges, depth, pose, and others. From Zhang, Rao & Agrawala, 2023. Install the `sd-webui-controlnet` extension.
  - When to use: prompting and Img2Img copy the style, but the pose, composition, or structure drifts.
  - How: upload an image, click Enable, then choose a **preprocessor and a model that match each other** (a Canny preprocessor goes with `control_v11p_sd15_canny`). The ControlNet model must also match your SD version. Check Low VRAM if you have less than 6 GB. Control Weight works like a prompt weight. Starting and Ending Control Step set when ControlNet applies, like prompt editing. For example, Ending = 0.8 gives the model freedom in the fine details. Control Mode balances ControlNet against the prompt. A simple or empty prompt is enough to reproduce the image. Use a full prompt to change it.
  - Principle(s): Provide Examples. You show the composition with an image instead of describing it.
  - Why it works / failure mode: you pass structure in directly. If the model is too detailed for the job, it locks the output in place. A SoftEdge map of a cat may be too fine to turn into a lion, so pick a coarser model.
- **Segment Anything Model (SAM)**: Meta's open-source segmentation model, trained on 11M images and 1.1B masks. You click 1–3 positive points, or right-click to add negative points, or let it mask every object automatically. The extension is `sd-webui-segment-anything` and the weights are `sam_vit_l_0b3195.pth`, 1.25 GB.
  - When to use: to cut out a person or object cleanly for inpainting, ControlNet, or a base image, without brushing it by hand.
  - How: add points, click Preview, and pick one of three masks (0–2). Check "Copy to Inpaint Upload & img2img ControlNet Inpainting" and click "Switch to Inpaint Upload". The authors found this handoff unreliable.
  - Principle(s): Divide Labor. You split the image into masks, work on each one separately, then put them back together.
- **DreamBooth Fine-Tuning**: from Ruiz et al., 2022. It updates the model's weights to teach it a new subject or style. It takes about 45–60 minutes on one GPU, or a few hours on free Colab with v1.5, and outputs a roughly 2 GB checkpoint.
  - When to use: you need a specific person, product, character, or style the base model doesn't know.
  - How: train **one concept** at a time, because several concepts hurt performance. Pick a rare token as the instance prompt (`ukj`, `zwx`), e.g. "photo of ukj person". Set the class prompt to "photo of a person" and add class/regularization images. Supply 5 images at minimum and 20–30 as standard. Generate 20 shots of a Consistent Character from Ch 8 and train on them. Convert the result to `.ckpt` and drop it into `models/Stable-diffusion`. Community DreamBooth models need their trigger word in the prompt, e.g. `nvinkpunk`.
  - Principle(s): Provide Examples, plus Divide Labor (there is no single model that does everything).
- **SDXL Base + Refiner**: the base model sets the overall composition and the refiner adds fine detail. The "Switch at" setting is the fraction of steps that run on the base. 0.6 × 30 steps means 18 base steps, then 12 refiner steps.
  - How: switch somewhere between 0.4 and 1.0 (1.0 means base only), with 20–50 steps. The authors' best results came from 0.6 at 30 steps.
  - Principle(s): Divide Labor.

## Key Concepts
- **Inference pipeline**: the object that runs the model, e.g. `StableDiffusionPipeline.from_pretrained(...)` from Hugging Face `diffusers`.
- **CFG Scale (Classifier-Free Guidance)**: how strictly the image follows the prompt. It's the same thing as `guidance_scale`. High values make images grainy and less varied.
- **Ancestral samplers**: samplers with an "a" in the name (`Euler a`). They inject noise at each step, so the image never converges and results aren't reproducible.
- **Denoising Strength**: how much noise is added to the input in Img2Img and inpainting. Low keeps the input. High replaces it.
- **Seed**: makes outputs reproducible. Set it to -1 for a new random image each run.
- **.safetensors vs .ckpt**: safetensors is the safer format because it can't run code when loaded.
- **PNG Info**: the tab that reads back the prompt and settings AUTOMATIC1111 saves in every image's metadata. This works only if the metadata hasn't been stripped.
- **Instance prompt / class prompt**: in DreamBooth, the instance prompt is the rare-token trigger for the new concept ("photo of ukj person"). The class prompt is the general category it builds from ("photo of a person"), used for prior preservation.
- **Textual Inversion / LoRA / Hypernetworks**: other fine-tuning methods. Textual Inversion finds a token embedding without touching the weights and performs much worse. LoRA (Hu et al., 2021) trains small added layers. Hypernetworks train parameters that generate those layers. LoRA and Hypernetworks were under 10% of Civitai models at the time of writing and rated lower.
- **Resize Mode**: what happens when the input's aspect ratio differs from the output's. Options are Just Resize, Crop and Resize, Resize and Fill, and Just Resize (latent upscale).

## Mental Models
- Think of the diffusion process as **coarse to fine**. Early steps set the overall shapes and late steps add detail. Prompt editing, ControlNet start/end steps, and the SDXL refiner switch all use this by changing what acts at which stage.
- Use the **lowest denoising strength that does the job**. Low values keep and polish the input. High values let the model replace it, and hallucinations start to appear above about 0.4.
- Use **hosted APIs** (Stability's DreamStudio) for quick programmatic generation. Use **local AUTOMATIC1111** when you need extensions, fine-tuning, or parameter grids. Hosted models can be deprecated under you, as v1.5 was.
- Think "**the right model for the job**", not one model to rule them all: SAM for masks, ControlNet for structure, DreamBooth for subjects, refiner for detail.

## Anti-patterns
- **Using your original prompt with SD Upscale**: every tile gets inpainted with the whole scene. Use a generic prompt like `highly detailed`.
- **Setting Inpaint area to "Only masked"**: the model tries to fit the whole scene into the masked area.
- **Pushing inpainting denoising above about 0.4 casually**: elements stop matching the rest of the image and the model hallucinates.
- **Training DreamBooth on several concepts at once**: it hurts quality. Train one subject or style, and merge models later in Checkpoint Merger if you need to.
- **Mismatched ControlNet preprocessor/model or SD version**: the result doesn't make sense.
- **Choosing a ControlNet model that's too detailed for a big change**: it gives ControlNet too much control. Canny can be noisy, and Normal can over-constrain faces.
- **Relying on a hosted model's features staying available**: vendors deprecate models (v1.5 was dropped in favor of 2.0/XL), which breaks tuned prompts and workflows.
- **Resetting AUTOMATIC1111 with `git checkout -f master` without a backup**: it deletes your customizations.

## Code Examples
```python
# create an inference pipeline
import torch
from diffusers import StableDiffusionPipeline
pipe = StableDiffusionPipeline.from_pretrained(
    "CompVis/stable-diffusion-v1-4",
    torch_dtype=torch.float16)
pipe = pipe.to("cuda")

# run inference on a prompt
prompt = "a photograph of an astronaut riding a horse"
generator = torch.Generator("cuda").manual_seed(1024)
image = pipe(prompt, num_inference_steps=50,
    guidance_scale=7, generator=generator
    ).images[0]  # image here is in PIL format
image.save(f"astronaut_rides_horse.png")
```
- **What it demonstrates**: running Stable Diffusion locally or in Colab with `diffusers` (pinned to `diffusers==0.11.1` in the book). float16 halves memory use. A fixed seed makes the output reproducible. `guidance_scale` is CFG. The model IDs and the library version are as of the 2024 edition.

```python
response = requests.post(
    f"{api_host}/v1/generation/{engine_id}/text-to-image",  # engine_id = "stable-diffusion-xl-1024-v1-0"
    headers={"Content-Type": "application/json",
             "Accept": "application/json",
             "Authorization": f"Bearer {api_key}"},
    json={"text_prompts": [{"text": prompt}],
          "cfg_scale": 7, "height": 1024, "width": 1024,
          "samples": 1, "steps": 30},
)
for i, image in enumerate(response.json()["artifacts"]):
    with open(f"./out/image-{i}.png", "wb") as f:
        f.write(base64.b64decode(image["base64"]))
```
- **What it demonstrates**: calling the hosted Stability AI (DreamStudio) REST API. Images come back base64-encoded under `artifacts`. The prompt is templated: `an illustration of {image_description}. in the style of corporate memphis, white background, professional, clean lines, warm pastel colors`. At the time, 1,000 credits cost $10, about 5,000 images.

```python
concepts_list = [{
    "instance_prompt": "photo of ukj person",
    "class_prompt":    "photo of a person",
    "instance_data_dir": "/content/data/ukj",
    "class_data_dir":    "/content/data/person"  # regularization images
}]
# !python3 train_dreambooth.py --pretrained_model_name_or_path=$MODEL_NAME \
#   --with_prior_preservation --prior_loss_weight=1.0 --resolution=512 \
#   --train_text_encoder --mixed_precision="fp16" --use_8bit_adam \
#   --learning_rate=1e-6 --num_class_images=50 --max_train_steps=800 \
#   --save_sample_prompt="photo of ukj person" --concepts_list="concepts_list.json"
```
- **What it demonstrates**: the DreamBooth setup using Shivam Shrirao's `diffusers` fork. The base model is `runwayml/stable-diffusion-v1-5`. It runs on Nvidia GPUs only. Afterwards, convert to `.ckpt` with `convert_diffusers_to_original_stable_diffusion.py --half`.

## Reference Tables

**CFG Scale rule of thumb**
| CFG | Meaning |
|---|---|
| 1 | Mostly ignore the prompt |
| 3 | Feel free to be creative |
| 7 | Good balance of prompt and creativity |
| 15 | Adhere to the prompt |
| 30 | Strictly follow the prompt |

**Samplers**
| Sampler | Trade-off |
|---|---|
| Euler | Simplest |
| DDIM | First sampler designed for diffusion. Higher quality but slower and more random at 10–15 steps |
| `… a` (ancestral, e.g. Euler a) | Adds noise every step, so it doesn't converge or reproduce |
| DPM++ 2M Karras, UniPC (20–30 steps) | Robust, stable, reproducible. The recommended default |
| DPM++ SDE Karras (10–15 steps) | Higher quality, slower, more random |

**Recommended settings by task**
| Task | Settings |
|---|---|
| Img2Img | Euler, 50 steps, CFG 20–30 |
| SD Upscale | 150–200+ steps, CFG 8–15, denoising 0.1–0.2, generic prompt |
| Inpaint, small fix | Masked content Original, denoising 0.2–0.4, Mask Blur 4 |
| Inpaint, replace element | Latent Noise, denoising up to 0.8 (risky above 0.4) |
| SDXL refiner | Switch at 0.6, 30 steps (range 0.4–1.0, 20–50 steps) |
| SDXL size | 1024×1024 (v1.5: 512×512) |

**ControlNet models**
| Model | What it extracts | Best for |
|---|---|---|
| Canny | Sharp high-contrast edges | Default choice. Transferring lots of detail in a new style, e.g. a city skyline |
| Depth | Depth map (white near, black far) | Keeping spatial layout and preventing merged objects |
| Normal | RGB surface-normal map | Texture and lighting. Can over-constrain faces |
| OpenPose | Skeleton: pose, hands, face | Copying human poses. Combine several skeletons for groups |
| M-LSD | Straight lines | Architecture and interiors. Poor for nature |
| SoftEdge (HED) | Smooth edges | Restyling and recoloring. Less noisy than Canny, better for faces |
| Segmentation | Regions of related segments | Outdoor and architectural scenes, changing time of day or era |
| Scribble | Your own rough drawing | Fast sketch-to-image |

**Aspect-ratio presets (sd-webui-ar `resolutions.txt`)**: SD 1:1 512×512 / XL 1024×1024. SD 3:2 768×512 / XL 1216×832. SD 9:16 403×716 / XL 768×1344.

## Worked Example
**Inpainting a statue into a castle courtyard** (Figures 9-15/9-16):
1. In the Img2Img → Inpaint tab, upload the castle image and brush out the center of the stone circle in the courtyard.
2. Set Inpaint area to *Whole picture* and keep the original seed.
3. Rewrite the prompt so it describes the whole scene but makes the **new subject** the statue instead of the castle: `statue of a king, texture, intricate, details, highly detailed, masterpiece, architecture, building, trending on artstation, focus, sharp focus, concept art, digital painting, fantasy, sunny, day, midday, in the style of high fantasy art`.
4. Choose masked content and denoising strength: Original at 0.2–0.4 for a small tweak, or Latent Noise up to 0.8 to add something new.
5. Generate. Fix any remaining artifacts one at a time, and raise Mask Blur if seams show.

Result: a statue of a king stands in the courtyard and the rest of the image doesn't change.

## Key Takeaways
1. Stable Diffusion's main advantage is that it's open source. You can run it locally (AUTOMATIC1111, or ComfyUI for complex flows), install community extensions, and fine-tune it, so no vendor deprecation can take it away.
2. Start with sampler and CFG choices: DPM++ 2M Karras or UniPC at 20–30 steps, CFG around 7. Use X/Y/Z Plot to find the best values by eye.
3. Prompt weights `(term:1.5)` / `[term]` and prompt editing `[from:to:when]` give you fine control over what the model attends to and when.
4. Denoising strength is the main setting in Img2Img, upscaling, and inpainting. Keep it low to preserve the input and raise it only when you need a replacement.
5. ControlNet copies structure from a reference image (Provide Examples), and SAM makes clean masks (Divide Labor). Together they make complex compositions possible.
6. DreamBooth teaches the model a new subject from 20–30 images in about an hour. Use a rare token and a class prompt, and train one concept per model.
7. SDXL splits the work between a base model for composition and a refiner for detail. Switching at 0.6 with 30 steps is the authors' best default.

## Connects To
- **Ch 1**: every technique here is labeled with one of the Five Principles: Give Direction (weights, prompt editing, inpainting), Specify Format (upscaling), Evaluate Quality (X/Y/Z plot), Provide Examples (ControlNet, DreamBooth), Divide Labor (SAM, refiner, specialized models).
- **Ch 7**: explains how diffusion works: denoising, CLIP embeddings, and the coarse-to-fine steps that prompt editing and the refiner rely on.
- **Ch 8**: Midjourney equivalents: `::` weights vs `()`, image prompts vs Img2Img, Describe vs Interrogate CLIP, negative prompts, outpainting, DALL-E inpainting. Consistent Characters produce DreamBooth training data.
- **Ch 10**: the blog-post generator uses API image generation, as in the Stability API snippet, with a consistent visual style.
- **LoRA (LLMs)**: the same low-rank adaptation idea used to fine-tune text models.
