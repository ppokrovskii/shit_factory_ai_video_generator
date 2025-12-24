# Requirements

## Goal
AI-powered CLI toolkit for automated image generation, manipulation, and video transition creation from image sequences.

## Philosophy
Simple command-line workflows that chain AI providers to transform text prompts and static images into dynamic video content.

## Use Cases

| UC | User Need | CLI Example | Acceptance |
|----|-----------|-------------|------------|
| UC-1 | Generate image (fast/cheap) | `image-cli generate fast "sunset" --output img.png` | PNG created, <5s, ~$0.01 cost |
| UC-2 | Generate image (default quality) | `image-cli generate "sunset" --output img.png` | PNG created, ~10s, ~$0.04 cost |
| UC-3 | Generate image (ultra quality) | `image-cli generate ultra "sunset" --output img.png` | PNG created, ~30s, ~$0.10 cost, up to 4K |
| UC-4 | Refine image with AI edits | `image-cli refine photo.png "darker" --output dark.png` | Modified version created |
| UC-5 | Upscale resolution | `image-cli upscale small.png --size 3000x3000 --output large.png` | Higher-res image created |
| UC-6 | Videos from images | `video-cli --src ./images --duration 5` | MP4 transitions created |
| UC-7 | Images + videos from JSON | `video-cli --prompts story.json` | All images + videos generated |
| UC-8 | Combine existing + generated | `video-cli --src ./existing --prompts new.json --pair-source all` | Mixed transitions created |
| UC-9 | Preview without API calls | `video-cli --prompts test.json --dry-run` | Plan displayed, no API calls |
| UC-10 | Generate images only | `video-cli --prompts test.json --images-only` | PNGs created, no MP4s |
| UC-11 | Automatic retry on failure | `video-cli --prompts test.json` | Completes despite transient errors |

## Providers

### Image Generation Presets (Recommended)

Users select quality presets instead of providers:

| Preset | Provider/Model | Price | Speed | Resolution | Use Case |
|--------|---------------|-------|-------|------------|----------|
| `fast` | openai/gpt-image-1-mini | ~$0.01-0.02 | <5s | 1024px | Testing, iterations, cheap |
| `regular` (default) | gemini/gemini-2.5-flash-image | ~$0.04-0.06 | ~10s | 1024px | Production, best value |
| `ultra` | gemini-pro/gemini-3-pro-image-preview | ~$0.10-0.15 | ~30s | up to 4K | High-quality, professional |

**Usage**:
```bash
image-cli generate fast "prompt"     # Use fast preset
image-cli generate "prompt"          # Use regular (default)
image-cli generate ultra "prompt"    # Use ultra preset
```

**Configuration** (optional, customize presets):
```bash
IMAGE_PRESET_FAST_PROVIDER=openai
IMAGE_PRESET_FAST_MODEL=gpt-image-1-mini

IMAGE_PRESET_REGULAR_PROVIDER=gemini
IMAGE_PRESET_REGULAR_MODEL=gemini-2.5-flash-image

IMAGE_PRESET_ULTRA_PROVIDER=gemini-pro
IMAGE_PRESET_ULTRA_MODEL=gemini-3-pro-image-preview
```

### Advanced: Manual Provider Selection

| Provider | Model | CLI Flag | Requires | Best For |
|----------|-------|----------|----------|----------|
| `gemini` | gemini-2.5-flash-image (Nano Banana) | `--provider gemini` | GOOGLE_API_KEY | Fast, 1024px, reference images |
| `gemini-pro` | gemini-3-pro-image-preview (Nano Banana Pro) | `--provider gemini-pro` | GOOGLE_API_KEY | Professional, up to 4K, thinking mode |
| `google` | imagen-3.0-generate-001 | `--provider google` | GOOGLE_CLOUD_PROJECT | Aspect ratios via Vertex AI |
| `openai` | gpt-image-1-mini | `--provider openai` | OPENAI_API_KEY | Stable quality |

[Official docs](https://ai.google.dev/gemini-api/docs/image-generation)

### Video Generation

| Provider | Model | CLI Flag | Requires | Use |
|----------|-------|----------|----------|-----|
| `veo` | veo-2.0-generate-001 | `--provider veo` | GOOGLE_CLOUD_PROJECT + GCS bucket | Production |
| `mock` | N/A | `--provider mock` | None | Testing |

## Output
- **Images**: PNG files with schema-defined names
- **Videos**: `<idx>__<start>__to__<end>.mp4`
- **Manifest**: `manifest.json` tracking metadata
