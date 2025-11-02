# Image CLI - Standalone Image Generation Tool

A command-line interface for AI-powered image generation, refinement, and upscaling. This tool can be used independently of the video generation pipeline.

## Installation

### Install the package

After installing the package, you can use the `image-cli` command from anywhere on your system:

```bash
# Install with uv (recommended)
uv pip install -e .

# Or with pip
pip install -e .
```

### Set up credentials

Create a `.env` file in your project root or set environment variables:

```bash
# For Gemini (default, recommended)
GOOGLE_API_KEY=your-google-api-key

# For OpenAI (alternative)
OPENAI_API_KEY=your-openai-api-key
OPENAI_IMAGE_MODEL=gpt-image-1-mini  # optional, default
OPENAI_IMAGE_SIZE=1024x1024           # optional, default

# For Google Vertex AI (alternative)
GOOGLE_CLOUD_PROJECT=your-project-id
VERTEX_LOCATION=us-central1
```

Get your Google API key from: https://aistudio.google.com/apikey

## Quick Start

### Generate an image
```bash
image-cli generate "a cat in a steampunk city"
```

### Refine an existing image
```bash
image-cli refine cat.png "add brass goggles and a top hat"
```

### Upscale an image
```bash
image-cli upscale cat.png --size 3000x3000
```

## Commands

### `generate` - Create a new image

Generate a new image from a text prompt.

```bash
image-cli generate PROMPT [OPTIONS]
```

**Arguments:**
- `PROMPT` - Text description of the image to generate

**Options:**
- `--output`, `-o` - Output file path (default: `output.png`)
- `--provider`, `-p` - Image provider: `gemini`, `openai`, or `google` (default: `gemini`)
- `--size`, `-s` - Image size like `1024x1024` (default: `1024x1024`)
- `--seed` - Random seed for reproducibility
- `--negative`, `-n` - Negative prompt (what to avoid)
- `--verbose`, `-v` - Show detailed debug logs

**Examples:**

```bash
# Basic generation
image-cli generate "a cat in a steampunk city"

# With custom output path
image-cli generate "a cat" --output my_cat.png

# With negative prompt
image-cli generate "a cat" --negative "blurry, low quality, distorted"

# Using specific provider and size
image-cli generate "a cat" --provider openai --size 512x512

# With seed for reproducibility
image-cli generate "a cat" --seed 42

# Verbose output
image-cli generate "a cat" --verbose
```

**Slavic Steampunk Style:**

Following the project's theme, use descriptive visual terms:

```bash
image-cli generate "character portrait, hybrid 2D/3D animation style, \
cel-shaded rendering, bold dynamic outlines, Victorian-era clothing \
with brass mechanisms, steam-powered clockwork details, Orthodox \
architecture in background, weathered surfaces, copper and bronze \
materials, post-apocalyptic atmosphere"
```

### `refine` - Modify an existing image

Refine or modify an existing image using AI and a text prompt. The original image is used as a reference for the generation.

```bash
image-cli refine IMAGE PROMPT [OPTIONS]
```

**Arguments:**
- `IMAGE` - Path to input image
- `PROMPT` - Refinement instructions (e.g., "make it more colorful")

**Options:**
- `--output`, `-o` - Output file path (default: `refined.png`)
- `--provider`, `-p` - Image provider (default: `gemini`)
- `--size`, `-s` - Output image size (default: `1024x1024`)
- `--seed` - Random seed
- `--verbose`, `-v` - Show detailed logs

**Examples:**

```bash
# Add details to an image
image-cli refine cat.png "add brass goggles and a top hat"

# Change style
image-cli refine cat.png "convert to cel-shaded animation style"

# Modify colors
image-cli refine cat.png "make colors more vibrant and add orange glow"

# With custom output
image-cli refine cat.png "add steam effects" --output cat_steamy.png

# Using different provider
image-cli refine cat.png "enhance details" --provider openai
```

**Tips for refinement:**
- Be specific about what you want to change
- Start with the generated image, then refine iteratively
- Use descriptive technical terms for better results

### `upscale` - Increase image resolution

Upscale an image to a higher resolution using high-quality resampling algorithms.

```bash
image-cli upscale IMAGE [OPTIONS]
```

**Arguments:**
- `IMAGE` - Path to input image

**Options:**
- `--output`, `-o` - Output file path (default: `upscaled.png`)
- `--size`, `-s` - Target size like `3000x3000` (default: `3000x3000`)
- `--method`, `-m` - Upscaling method: `lanczos`, `bicubic`, `nearest`, `bilinear` (default: `lanczos`)
- `--verbose`, `-v` - Show detailed logs

**Examples:**

```bash
# Upscale to 3000x3000
image-cli upscale cat.png --size 3000x3000

# Upscale with custom output
image-cli upscale cat.png --size 2048x2048 --output cat_large.png

# Use different upscaling method
image-cli upscale cat.png --size 4096x4096 --method bicubic

# Upscale to ultra-high resolution
image-cli upscale cat.png --size 8000x8000
```

**Upscaling methods:**
- `lanczos` - Highest quality, best for photos (default)
- `bicubic` - Good quality, faster than Lanczos
- `bilinear` - Smooth results, fast
- `nearest` - Pixel art style, preserves hard edges

## Workflow Examples

### Generate → Refine → Upscale

Create an image, refine it, then upscale to high resolution:

```bash
# Step 1: Generate base image
image-cli generate "steampunk cat engineer" --output cat_base.png

# Step 2: Refine details
image-cli refine cat_base.png "add brass goggles, clockwork details, \
steam effects" --output cat_refined.png

# Step 3: Upscale to final resolution
image-cli upscale cat_refined.png --size 3000x3000 --output cat_final.png
```

### Batch processing with shell

Generate multiple variations:

```bash
# Generate base image
image-cli generate "steampunk workshop" --output workshop.png

# Create variations
for style in "add steam effects" "add more brass details" "add vintage lighting"; do
    filename=$(echo $style | tr ' ' '_')
    image-cli refine workshop.png "$style" --output "workshop_${filename}.png"
done

# Upscale all variations
for img in workshop_*.png; do
    image-cli upscale "$img" --size 2048x2048 --output "hires_${img}"
done
```

### Iterative refinement

Refine an image multiple times:

```bash
# Start with base
image-cli generate "character portrait" --output step1.png

# Iteration 1: Add style
image-cli refine step1.png "cel-shaded animation style" --output step2.png

# Iteration 2: Add details
image-cli refine step2.png "add brass mechanisms and goggles" --output step3.png

# Iteration 3: Enhance atmosphere
image-cli refine step3.png "add steam effects and warm lighting" --output step4.png

# Final upscale
image-cli upscale step4.png --size 3000x3000 --output final.png
```

## Advanced Usage

### Using as a Python module

You can also import and use the CLI programmatically:

```python
from app.image_cli import app
from typer.testing import CliRunner

runner = CliRunner()
result = runner.invoke(app, ["generate", "a cat", "--output", "cat.png"])
print(result.stdout)
```

### Custom providers

The tool supports multiple AI providers:

**Gemini (default):**
- Fast generation
- Good quality
- Supports reference images
- Simple API key setup

**OpenAI:**
- DALL-E models
- Multiple size options
- Consistent results

**Google Vertex:**
- Imagen 2/3 models
- Enterprise features
- Requires Google Cloud setup

### Environment variables

```bash
# Provider credentials
GOOGLE_API_KEY=...           # For Gemini
OPENAI_API_KEY=...           # For OpenAI
GOOGLE_CLOUD_PROJECT=...     # For Vertex AI
GOOGLE_APPLICATION_CREDENTIALS=... # Service account

# Model selection
GEMINI_IMAGE_MODEL=gemini-2.5-flash-image
OPENAI_IMAGE_MODEL=gpt-image-1-mini
VERTEX_IMAGEN_MODEL=imagen-3.0-generate-001

# Default settings
OPENAI_IMAGE_SIZE=1024x1024
VERTEX_LOCATION=us-central1
```

## Tips & Best Practices

### Writing good prompts

1. **Be specific and descriptive:**
   ```bash
   # Bad
   image-cli generate "a cat"
   
   # Good
   image-cli generate "orange tabby cat with green eyes, sitting on \
   brass clockwork gears, Victorian-era workshop background, warm lighting"
   ```

2. **Use technical art terms:**
   - Animation: cel-shaded, hand-drawn, painterly
   - Visual effects: chromatic aberration, motion blur, halftone patterns
   - Style: bold outlines, high contrast, film grain

3. **Use negative prompts to avoid unwanted elements:**
   ```bash
   image-cli generate "character portrait" \
     --negative "blurry, low quality, distorted, watermark"
   ```

### Optimizing quality

1. **Start small, refine, then upscale:**
   - Generate at 1024x1024 for speed
   - Refine details at same size
   - Final upscale to 3000x3000+

2. **Use Lanczos for upscaling photos and art:**
   ```bash
   image-cli upscale photo.png --size 3000x3000 --method lanczos
   ```

3. **Use reproducible seeds for consistency:**
   ```bash
   image-cli generate "a cat" --seed 42
   ```

### Performance tips

1. **Use gpt-image-1-mini for rapid iteration:**
   ```bash
   export OPENAI_IMAGE_MODEL=gpt-image-1-mini
   image-cli generate "test prompt" --provider openai
   ```

2. **Use Gemini for best balance of speed/quality:**
   ```bash
   image-cli generate "prompt" --provider gemini  # default
   ```

3. **Batch operations in parallel:**
   ```bash
   # Linux/Mac
   echo "prompt1\nprompt2\nprompt3" | \
     xargs -P 3 -I {} image-cli generate "{}"
   ```

## Troubleshooting

### API key errors

```
✗ RuntimeError: GOOGLE_API_KEY not set
```
**Solution:** Set your API key in `.env` or environment:
```bash
export GOOGLE_API_KEY=your-key-here
```

### Image quality issues

**Problem:** Generated images are blurry or low quality

**Solutions:**
1. Use more descriptive prompts
2. Add negative prompts to exclude unwanted artifacts
3. Try different providers (`--provider gemini|openai|google`)
4. Use higher quality models (set in environment)

### Upscaling artifacts

**Problem:** Upscaled images have artifacts or blur

**Solutions:**
1. Try different upscaling methods (`--method lanczos|bicubic`)
2. Don't upscale more than 4-8x original size
3. Start with higher quality source images

### Refinement not working as expected

**Problem:** Refine command doesn't preserve original style

**Solutions:**
1. Use more specific prompts that reference the original
2. Try different providers
3. Refine in smaller steps instead of large changes

## Integration with Video Pipeline

The image CLI can be used to prepare high-quality images for the video generation pipeline:

```bash
# Generate images for video
for i in {1..5}; do
    image-cli generate "scene $i: steampunk city" \
      --output ".src/scene_${i}.png" \
      --seed $i
done

# Generate videos from images
video-cli --src .src --duration 5
```

## API Reference

### Exit Codes

- `0` - Success
- `1` - Error (file not found, generation failed, etc.)
- `2` - Invalid arguments or configuration

### File Formats

**Supported input formats:**
- PNG (recommended)
- JPEG/JPG
- WEBP

**Output format:**
- PNG (always, for maximum quality)

## Examples Gallery

### Slavic Steampunk Character

```bash
image-cli generate "character portrait, hybrid 2D/3D animation, \
cel-shaded, bold dynamic outlines, Victorian-era clothing with \
Slavic embroidery, brass goggles, leather straps, gear accessories, \
Orthodox architecture background, steam clouds, warm amber lighting, \
weathered metal textures, post-apocalyptic atmosphere" \
--output character.png --seed 42

image-cli upscale character.png --size 3000x3000 --output character_hd.png
```

### Steampunk Workshop

```bash
image-cli generate "interior workshop scene, brass mechanisms, \
copper pipes, steam vents, clockwork gears, Victorian-era tools, \
aged wood workbench, Orthodox icons on walls, warm coal ember glow, \
film grain texture, high contrast lighting" \
--output workshop.png

image-cli refine workshop.png "add more steam effects and glowing dials" \
--output workshop_enhanced.png
```

### Post-Apocalyptic Cityscape

```bash
image-cli generate "cityscape, Orthodox onion domes with brass plating, \
steam-pipe spires, mechanical bell towers, ruins, weathered surfaces, \
nature reclaiming technology, clockwork elements, copper tarnish, \
dramatic sky, cinematic composition" \
--output city.png --size 1024x1536

image-cli upscale city.png --size 3000x4500 --output city_hd.png
```

## See Also

- [README.md](README.md) - Main project documentation
- [video_generation_guide.md](video_generation_guide.md) - Video generation guide
- [.cursorrules](.cursorrules) - Project style guidelines

