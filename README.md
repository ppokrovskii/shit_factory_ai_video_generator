# AI Image & Video Generator CLI

AI-powered command-line tools for image generation, editing, and video transitions.

## Install

```bash
uv pip install -e .
```

## Configuration

Minimal `.env`:
```bash
GOOGLE_API_KEY=your-key-here              # For Gemini (default)
```

Full `.env`:
```bash
# Image providers
GOOGLE_API_KEY=your-key                   # Gemini (Nano Banana & Nano Banana Pro)
OPENAI_API_KEY=your-key                   # OpenAI
GOOGLE_CLOUD_PROJECT=your-project-id      # Imagen 3.0 (Vertex AI)
VERTEX_LOCATION=us-central1

# Image generation presets (optional overrides)
IMAGE_PRESET_FAST_PROVIDER=openai
IMAGE_PRESET_FAST_MODEL=gpt-image-1-mini
IMAGE_PRESET_FAST_SIZE=1024x1024

IMAGE_PRESET_REGULAR_PROVIDER=gemini
IMAGE_PRESET_REGULAR_MODEL=gemini-2.5-flash-image
IMAGE_PRESET_REGULAR_SIZE=1024x1024

IMAGE_PRESET_ULTRA_PROVIDER=gemini-pro
IMAGE_PRESET_ULTRA_MODEL=gemini-3-pro-image-preview
IMAGE_PRESET_ULTRA_SIZE=2K

# Video generation
VERTEX_VEO_OUTPUT_BUCKET=gs://bucket/videos/

# Video generation presets (optional overrides)
VIDEO_PRESET_FAST_PROVIDER=mock
VIDEO_PRESET_FAST_DURATION=3

VIDEO_PRESET_REGULAR_PROVIDER=veo
VIDEO_PRESET_REGULAR_DURATION=5

VIDEO_PRESET_ULTRA_PROVIDER=veo
VIDEO_PRESET_ULTRA_DURATION=8
```

**Get keys**: [Google AI](https://aistudio.google.com/apikey) · [OpenAI](https://platform.openai.com/api-keys) · [GCloud](https://cloud.google.com/sdk/gcloud/reference/auth/application-default/login)

## Image CLI

### Simple Presets (Recommended)

```bash
# Fast - Cheapest, fastest generation (~$0.01-0.02, <5s)
uv run image-cli generate fast "sunset over ocean" --output sunset.png

# Regular - Best value, default (~$0.04-0.06, ~10s)
uv run image-cli generate "sunset over ocean" --output sunset.png

# Ultra - Highest quality, 4K (~$0.10-0.15, ~30s)
uv run image-cli generate ultra "sunset over ocean" --output sunset.png
```

### Other Commands

```bash
# Refine (AI editing)
uv run image-cli refine photo.png "make it darker" --output dark.png

# Upscale
uv run image-cli upscale small.png --size 3000x3000 --output large.png
```

### Advanced: Manual Provider Selection

```bash
# Override preset with specific provider
uv run image-cli generate "prompt" --provider gemini-pro --size 2K
uv run image-cli generate "prompt" --provider openai
```

### Providers

| Provider | Model | Flag | Best For | Price |
|----------|-------|------|----------|-------|
| `gemini` (default) | gemini-2.5-flash-image (Nano Banana) | `--provider gemini` | Fast, 1K resolution | ~$0.04-0.06 |
| `gemini-pro` | gemini-3-pro-image-preview (Nano Banana Pro) | `--provider gemini-pro` | Professional, up to 4K | ~$0.10-0.15 |
| `google` | imagen-3.0-generate-001 | `--provider google` | Specific aspect ratios | ~$0.04 |
| `openai` | gpt-image-1-mini | `--provider openai` | Cheapest, stable | ~$0.01-0.02 |

```bash
# Using presets (simple)
uv run image-cli generate fast "prompt"     # Cheap & fast
uv run image-cli generate "prompt"          # Default (regular)
uv run image-cli generate ultra "prompt"    # High quality

# Override provider (advanced)
uv run image-cli generate "prompt" --provider gemini-pro --size 4K
```

**Nano Banana models** (official Google branding):
- **Gemini 2.5 Flash Image**: Fast generation, 1024px resolution, optimized for high-volume
- **Gemini 3 Pro Image Preview**: Professional quality, up to 4K, with "thinking" mode for better composition

[Official docs](https://ai.google.dev/gemini-api/docs/image-generation)

## Video CLI

### Simple Presets (Recommended)

```bash
# Fast - Quick testing with mock provider (3s duration)
uv run python -m app.cli --src ./images --video-preset fast

# Regular - Standard production quality (5s duration, default)
uv run python -m app.cli --src ./images --video-preset regular

# Ultra - High quality, longer duration (8s)
uv run python -m app.cli --src ./images --video-preset ultra
```

### Basic Usage

```bash
# From existing images (uses regular preset)
uv run python -m app.cli --src ./images

# From JSON prompts (generates images + videos)
uv run python -m app.cli --prompts prompts.json

# Dry run
uv run python -m app.cli --prompts prompts.json --dry-run

# Images only
uv run python -m app.cli --prompts prompts.json --images-only
```

### Advanced: Manual Provider Selection

```bash
# Override preset with specific provider
uv run python -m app.cli --src ./images --provider veo --duration 10

# Override duration while using preset
uv run python -m app.cli --src ./images --video-preset ultra --duration 12
```

### Providers

| Provider | Flag | Use |
|----------|------|-----|
| `veo` (default) | `--provider veo` | Production (requires GCS bucket) |
| `mock` | `--provider mock` | Testing only |

## Prompt Schema

```json
{
  "images": [
    {"code": "S01", "filename": "scene01.png", "prompt": "description", "reference": null},
    {"code": "S02", "filename": "scene02.png", "prompt": "description", "reference": "scene01.png"}
  ],
  "videos": [
    {"from": "scene01.png", "to": "scene02.png", "prompt": "transition"}
  ]
}
```

## Common Workflows

```bash
# Fast iteration: cheap & fast
uv run image-cli generate fast "cat" --output v1.png
uv run image-cli generate fast "cat with glasses" --output v2.png

# Production: regular preset
uv run image-cli generate "cinematic portrait" --output hero.png
uv run image-cli refine hero.png "add dramatic lighting" --output hero_v2.png

# High-quality: ultra preset with upscale
uv run image-cli generate ultra "product photo" --output product.png
uv run image-cli upscale product.png --size 4096x4096 --output product_4k.png
```

## Key Flags

| Flag | Description |
|------|-------------|
| `--provider` / `-p` | AI provider (gemini/gemini-pro/google/openai) |
| `--img-provider` | Image provider for video-cli |
| `--output` / `-o` | Output file path |
| `--size` / `-s` | Image dimensions |
| `--dry-run` | Preview without API calls |
| `--images-only` | Skip video generation |
| `--verbose` / `-v` | Debug logging |

## Help

```bash
uv run image-cli --help
uv run python -m app.cli --help
```

## Output

- **Images**: PNG files
- **Videos**: `<idx>__<start>__to__<end>.mp4`
- **Manifest**: `manifest.json`

## Testing

```bash
uv run pytest -q
```
