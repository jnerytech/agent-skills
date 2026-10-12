# Chapter 8: Standard Practices for Image Generation with Midjourney

## Core Idea
Image models imitate their training data. They don't try to make *good* images unless you ask. You steer them with a vocabulary of modifiers (format, art style, quality boosters), with control syntax (negative prompts, weights, image prompts), and with editing workflows (inpainting, outpainting). On top of that sit meta-techniques that use an LLM or the community to write and analyze prompts. Examples use Midjourney v5, but the techniques are meant to transfer to any model.

## Frameworks Introduced
- **Format Modifiers**: name the medium or format of the image first ("a stock photo of…", "an oil painting of…", "an ancient Egyptian hieroglyph of…"), and add technique terms for precision (e.g. *impasto*, "textured oil-on-canvas using thick impasto and swirling dynamic brushstrokes").
  - When to use: always. It is the most basic practice and it decides the look of the whole image.
  - How: `<format> of <subject>`, plus specific art or photography technique terms if you know them.
  - Principle(s): **Specify Format**. It changes the result significantly and makes the prompt more reliable at producing the visual type you need.
  - Why it works / failure mode: the format pulls in everything associated with it in training. Content changes too, not just style: oil paintings of a meeting have no computers, and hieroglyph participants wear Egyptian headdresses. Combine it with other techniques to get back the elements you need.

- **Art Style Modifiers**: "in the style of <artist / art movement / work>" (e.g. "illustration of a dragon, in the style of Alice's Adventures in Wonderland by Lewis Carroll").
  - When to use: you want a specific aesthetic and the artist or movement is well represented in training data.
  - How: name the artist, the movement (Post-impressionism, Surrealism, Cubism) or the specific work.
  - Principle(s): **Give Direction**. The name is a shortcut to one region of latent space, and you can explore nearby from there.
  - Caution: legal gray area for living artists. The authors' rule of thumb is to prefer artists who died at least a year ago, and to get legal counsel before commercial use.

- **Reverse Engineering Prompts (/describe)**: upload any image (AI-generated or real) with Midjourney `/describe`. It returns 4 candidate prompts with artists, styles and subjects. Pick one to regenerate in that style. The open source equivalent is CLIP Interrogator, which is weaker.
  - When to use: you like an image but lack the vocabulary to describe it.

- **Quality Boosters**: append words associated with quality in the training data, such as `4k`, `very beautiful`, `trending on artstation`.
  - How: subject first, then the booster after a comma: `a space whale, trending on artstation`.
  - Principle(s): **Give Direction**. One or two words improve aesthetics without changing the style much.
  - Failure mode: the source site's style can leak in. ArtStation has a lot of spaceship art, so the space whale looks somewhat like a spaceship.

- **Negative Prompts (`--no`)**: comma-separated concepts after `--no` are subtracted from the image.
  - When to use: to separate concepts that are intertwined in training data. Oil paintings tend to bring frames and walls (`oil painting in the style of Rembrandt --no frame, wall`).
  - Creative uses: negate a celebrity to remove their associated features (`a Scottish female astronaut --no Karen Gillan` gives less red hair and a less conventionally feminine look), or separate inseparable concepts (`Homer Simpson --no cartoon`).
  - Principle(s): **Give Direction**. Not fully reliable, because some concepts are too strongly correlated.
  - Legacy use: `nsfw, elongated body, too many digits, not enough fingers, teeth` to fix anatomy. This is still needed for Stable Diffusion v1.5 but mostly solved from Midjourney v5 and SDXL onward.

- **Weighted Terms (`::`)**: split the prompt with `::` followed by a weight (default 1). Words earlier in the prompt carry more weight, so put the subject first.
  - How: `painting of the Golden Gate Bridge::1 in the style of Van Gogh::0.8, in the style of Dali::0.2`. Weights above 1 emphasize and negative weights remove. `--no` is shorthand for `::-0.5`. If `--no` isn't strong enough, use a stronger negative weight (`Van Gogh::-1, Dali::5`).
  - Principle(s): **Evaluate Quality**. Run a **grid search** over weight combinations (e.g. 0.2 steps from 0 to 1 between two artists) instead of trying them one at a time.

- **Prompting with an Image (Img2Img)**: give a base image, either as a link at the start of the Midjourney prompt or via Img2Img in Stable Diffusion, then add text.
  - How: upload the image to Discord, use Copy Link, then `<link> in the style of The Great Gatsby`. The text can be shorter because the picture carries most of the information. `/blend` merges several images, and `--iw` sets the image weight (the same as `::` weighting). This is also common in AI video (RunwayML, Pika Labs).
  - Principle(s): **Provide Examples**. It works like a one-shot prompt in text generation.
  - Caution: copyright when uploading images you don't own.

- **Inpainting**: erase a region and regenerate only that region. Available as Stable Diffusion inpainting, Midjourney **Vary Region**, Photoshop **Generative Fill**, and DALL-E (the authors' preferred option, since it blends edges automatically so the mask can be rough).
  - How: the authors find that prompting **only for what goes in the erased area** works better than the common advice of describing the whole image.
  - Principle(s): **Divide Labor**. Pick the right model for each job: Midjourney for aesthetics, DALL-E for inpainting. Use several together.

- **Outpainting (Zoom Out / Custom Zoom)**: generate beyond the frame to add surrounding context, or to change the aspect ratio (portrait to landscape) by filling the gaps. Midjourney offers it on upscaled images. The Stable Diffusion extension is less reliable.
  - Principle(s): **Provide Examples**.

- **Consistent Characters**: generate `two images side by side, <character description> --ar 2:1`, upscale, mask one half with Vary Region, and reprompt that half for a new angle or situation (`side profile image, …`). Then crop.
  - Why it works: the half that stays visible anchors the character's features across generations.
  - Principle(s): **Provide Examples**. Advanced artists feed *generated* images back in as inputs for consistency.

- **Prompt Rewriting**: a form of **Meta Prompting** in which one model (ChatGPT) rewrites a user's raw prompt before it reaches the image model.
  - When to use: in production, where users aren't prompt engineers ("garbage in, garbage out").
  - How: template `{subject} in the style of {artist}`. Ask the LLM "What's the medium that the artist {artist} mostly used? Respond in 1-3 words only." Then rewrite to `{medium} of a {subject} in the style of {artist}`. You can extend this with quality boosters and negative prompts.
  - Principle(s): **Divide Labor**.
  - Limit: specialized prompt-generator models only reach average quality. They don't beat expert prompting.

- **Meme Unbundling** (term coined by Bakz T. Future): break an artist's style into its component "memes" (cultural units) and prompt with the description instead of the name.
  - How: (1) ask an LLM to "Briefly describe the characteristics and artistic style of <work> by <artist>, *without mentioning the artwork or the artist*". The exclusion is required. (2) Ask it to "Convert this description into a shortened prompt for an AI image generation model". (3) Add your subject and smooth the wording, since LLM output tends to read like instructions. (4) Remix individual memes (colors, elements) to make it your own.
  - Principle(s): **Give Direction**. It is more transformative, more original and arguably more ethical than naming the artist.
  - Limit: it only works for artists and works famous enough to be described from training data. Multimodal models should eventually allow image → description.

- **Meme Mapping**: systematically mine community prompts (Midjourney Discord, Reddit, Lexica.art) for recurring word patterns that reliably produce an effect, then reuse them on new subjects. For example, "as a Soviet factory worker" evokes gritty realism.
  - How: collect manually (spreadsheet or Notion) or scrape where the terms allow. Label at scale with Google Vision, GPT-4 Vision or n-gram analysis.

- **Prompt Analysis (/shorten)**: Midjourney's `/shorten` (click "show details") returns token-level weights so you can cut words that only add noise.
  - Principle(s): **Evaluate Quality**. Your assumptions about which words matter are often wrong.

## Key Concepts
- **Format modifier**: a word naming the medium or format (stock photo, oil painting, hieroglyph) that sets both style and content.
- **Impasto**: an oil technique with thick paint and visible brushstrokes. An example of precise art vocabulary improving results.
- **Latent space**: the multidimensional universe of possible outputs. Naming a style jumps to one region of it.
- **Quality boosters**: style-neutral words linked to high-quality training images (often from ArtStation, Behance, DeviantArt).
- **Negative prompt**: concepts to exclude. In Midjourney, `--no` equals a `::-0.5` weight.
- **Prompt weights**: `::N` sets the relative emphasis of a prompt section. Default is 1, and negative values subtract.
- **Img2Img / image prompt**: conditioning generation on a base image. `--iw` sets its weight.
- **Inpainting / Vary Region / Generative Fill**: regenerating a masked region in place.
- **Outpainting / Zoom Out**: extending the canvas beyond the original frame.
- **Meme**: any unit of cultural information copied from person to person. Here, a component of a style.

## Mental Models
- Think of an image model as a mirror of its training set, not a pursuer of quality. Any quality, format or style you want has to be asked for explicitly.
- Think of an artist's name as a teleport to a region of latent space. Unbundling gives you the coordinates, so you can move away from that region on purpose.
- Use negative weights when `--no` isn't strong enough. Use a grid search when you have more than one weight to tune.
- Use a second model as the prompt engineer whenever end users write the raw prompt.

## Anti-patterns
- **Format without compensation**: forgetting that the format carries content with it (no laptops in oil paintings). Add the missing elements explicitly.
- **Copying living artists' styles**: legal and ethical risk. Unbundle the memes instead.
- **Prompting the whole scene when inpainting**: in the authors' experience, describe only the masked region.
- **Ever-longer prompts**: every word perturbs the output and adds noise. Removing words can help as much as adding them. Use `/shorten`.
- **Relying on anatomy negatives in modern models**: mostly unnecessary from Midjourney v5 and SDXL onward.
- **Iterating weights one at a time**: slow. Grid-search them.
- **Trusting raw user prompts in production**: garbage in, garbage out. Rewrite them.
- **Letting the unbundling LLM name the artist or work**: the description becomes contaminated and works less well as a prompt.

## Code Examples
```text
# Weighted blend, then strip one influence with a negative weight
painting of the Golden Gate Bridge::1 in the style of Van Gogh::0.8, in the style of Dali::0.2
painting of the Golden Gate Bridge::1 in the style of Van Gogh::-1, in the style of Dali::5

# Negative prompt to separate intertwined concepts
oil painting in the style of Rembrandt --no frame, wall
```
- **What it demonstrates**: Midjourney control syntax. `::` sets weights and `--no` is a `::-0.5` shortcut.

```text
# Consistent character: generate a pair, then Vary Region one half
two images side by side, rockstar American rough and ready middle-age jawline actor man, photo booth portrait --ar 2:1
side profile image, rockstar American rough and ready middle-age jawline actor man, photo booth portrait --ar 2:1
```
- **What it demonstrates**: the visible half anchors the character's identity while the masked half is reprompted.

## Reference Tables

| Technique | Midjourney | Stable Diffusion | DALL-E / other | Principle |
|---|---|---|---|---|
| Negative prompt | `--no a, b` | negative prompt field | — | Give Direction |
| Weights | `::N` | (prompt weighting) | — | Evaluate Quality |
| Image prompt | link at start, `/blend`, `--iw` | Img2Img | RunwayML, Pika (video) | Provide Examples |
| Inpainting | Vary Region | inpainting | DALL-E (preferred), Photoshop Generative Fill | Divide Labor |
| Outpainting | Zoom Out / Custom Zoom | extension (less reliable) | DALL-E (legacy labs UI) | Provide Examples |
| Reverse engineer | `/describe` | CLIP Interrogator | — | — |
| Prompt analysis | `/shorten` (show details) | — | — | Evaluate Quality |

## Worked Example
**Meme Unbundling: Times Square à la Dali.**
1. Baseline: `a painting of Times Square in the style of "The Persistence of Memory" by Salvador Dali` gives good results, but it's a near-copy.
2. Ask ChatGPT-4: "Briefly describe the characteristics and artistic style of "The Persistence of Memory" by Salvador Dali, without mentioning the artwork or the artist". It returns paragraphs about Surrealist dream imagery, deceptive realism, melting objects against solid ones, and themes of time and the subconscious.
3. "Convert this description into a shortened prompt for an AI image generation model such as DALL-E". This yields: *Surrealist landscape with subdued colors of brown, blue, and yellow… barren, craggy shoreline and calm sea meeting a clear sky… amorphous, melting objects… Evoke a sense of stillness, dreamlike atmosphere, and quietude.*
4. Prefix the subject: `Painting of Times Square, surrealist landscape with subdued colors…`. The result resembles Dali's work but is filtered through the description, so it is more original.
5. Remix the memes: swap the colors to orange, red and green, and the scene to "imposing buildings and calm river meeting a stormy sky", with "the amorphous melting dripping clock in the center of the square". The outcome is a familiar but distinct style.

(Prompt Rewriting runs the same kind of pipeline. `a dachshund dog in the style of Banksy` puts the dog *next to* a mural. The LLM returns the medium "Street art", the rewrite becomes `street art of a dachshund dog in the style of Banksy`, and the dog is now *part of* the street art.)

## Key Takeaways
1. Start every image prompt with a format modifier, and remember that the format brings its own content with it.
2. Artist and movement names, quality boosters and `/describe` are shortcuts into latent space. Prefer unbundled descriptions to copying living artists.
3. Use `--no` to separate intertwined concepts. When it isn't enough, use explicit (negative) `::` weights tuned by grid search.
4. An image is the strongest example you can give (one-shot). Use image prompts, inpainting, outpainting and the side-by-side trick for consistency.
5. Combine models by strength (Divide Labor), including an LLM that rewrites user prompts before generation.
6. Mine community prompts (meme mapping) and prune with `/shorten`. Shorter, deliberate prompts beat long, noisy ones.

## Connects To
- **Ch 1**: every technique is tagged with one of the Five Principles. The Banksy/Dali examples echo the chapter's opening image-prompt demos.
- **Ch 3**: Prompt Rewriting is Meta Prompting from text generation applied to image prompts.
- **Ch 7**: diffusion and latent space mechanics explain why format, style and boosters work.
- **Ch 9**: Img2Img, inpainting, negative prompts and weights reappear with finer control in Stable Diffusion/AUTOMATIC1111 (ControlNet, DreamBooth).
- **Ch 10**: Prompt Rewriting and quality boosters are production patterns for user-facing image features.
- **Copyright / fair use**: the legal status of AI style imitation and image uploads was unresolved as of the 2024 edition.
