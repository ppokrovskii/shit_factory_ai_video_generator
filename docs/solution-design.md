# Solution Design

## Overview
AI-powered CLI tools for image generation, manipulation, and video transitions. Two commands: `image-cli` (standalone) and `video-cli` (image-to-video).

## Stack

**Core**: Python 3.9+ · uv · Typer · Pillow  
**Testing**: pytest (80%+ coverage target, pre-commit hooks)  
**Config**: python-dotenv

## Providers

| Type | Provider | Model | Implementation | Auth |
|------|----------|-------|----------------|------|
| Image | `gemini` (default) | gemini-2.5-flash-image (Nano Banana) | google-generativeai | GOOGLE_API_KEY |
| Image | `gemini-pro` | gemini-3-pro-image-preview (Nano Banana Pro) | google-generativeai | GOOGLE_API_KEY |
| Image | `google` | imagen-3.0-generate-001 | Vertex AI | GOOGLE_CLOUD_PROJECT + ADC |
| Image | `openai` | gpt-image-1-mini | OpenAI REST | OPENAI_API_KEY |
| Video | `veo` (default) | veo-2.0-generate-001 | Vertex AI REST | GOOGLE_CLOUD_PROJECT + ADC + GCS |
| Video | `mock` | N/A | Testing stub | None |

**Size support**: 
- Gemini 2.5 Flash (Nano Banana): 1024px (10 aspect ratios: 1:1, 2:3, 3:2, 3:4, 4:3, 4:5, 5:4, 9:16, 16:9, 21:9)
- Gemini 3 Pro (Nano Banana Pro): 1K/2K/4K configurable (10 aspect ratios)
- Imagen 3.0: 1:1/3:4/4:3/9:16/16:9 via Vertex AI
- OpenAI: 1024x1024/512x512/1792x1024

**Pricing** (per image, approximate):
- OpenAI gpt-image-1-mini: $0.01-0.02 (cheapest)
- Gemini 2.5 Flash (Nano Banana): ~$0.04-0.06 (fast, 1K)
- Imagen 3.0: $0.04-0.08 (Vertex AI)
- Gemini 3 Pro (Nano Banana Pro): ~$0.10-0.15 (professional, up to 4K)

**Nano Banana models** are official Google branding for Gemini's image generation:
- **Nano Banana** = Gemini 2.5 Flash Image (optimized for speed/volume)
- **Nano Banana Pro** = Gemini 3 Pro Image Preview (professional quality, "thinking" mode, up to 4K)

[Official docs](https://ai.google.dev/gemini-api/docs/image-generation)

## Architecture

```
app/
  cli.py                 # video CLI entry
  image_cli.py           # image CLI entry
  engine.py              # job orchestration + retry
  core_pairs.py          # image pairing logic
  io_scan.py             # image discovery
  manifest.py            # output tracking
  prompt_schema.py       # JSON validation (v1/v2)
  providers/             # video generation
    veo.py, mock.py
  image_gen/             # image generation
    gemini.py, google.py, openai.py, mock.py
    scheduler.py         # grouped concurrency
tests/                   # 19 test files
```

**Design patterns**:
- Protocol-based abstraction (pluggable providers)
- Lazy loading (defer heavy imports)
- Grouped scheduling (sequential within chains, concurrent across groups)
- Retry with exponential backoff (0.5s * 2^attempt, max 4s, 2 retries)

## Data Flow

1. **Input**: Scan directory OR generate from JSON prompts
2. **Pairing**: Consecutive `(i, i+1)` OR explicit transitions
3. **Generation**: Sequential jobs with retry
4. **Output**: `<idx>__<start>__to__<end>.mp4` + `manifest.json`

## Prompt Schema (V2)

```json
{
  "images": [
    {"code": "S01", "filename": "s01.png", "prompt": "desc", "reference": null},
    {"code": "S02", "filename": "s02.png", "prompt": "desc", "reference": "s01.png"}
  ],
  "videos": [
    {"from": "s01.png", "to": "s02.png", "prompt": "transition"}
  ]
}
```

**Note**: `reference`/`attachment` creates dependency chains (sequential processing).

## Configuration

```bash
# Image providers
GOOGLE_API_KEY=...
GOOGLE_CLOUD_PROJECT=...
OPENAI_API_KEY=...

# Video
VERTEX_VEO_OUTPUT_BUCKET=gs://bucket/

# Optional overrides
GEMINI_IMAGE_MODEL=gemini-2.5-flash-image
GEMINI_PRO_IMAGE_MODEL=gemini-3-pro-image-preview
VERTEX_IMAGEN_MODEL=imagen-3.0-generate-001
OPENAI_IMAGE_MODEL=gpt-image-1-mini
VERTEX_VEO_MODEL=veo-2.0-generate-001
VERTEX_LOCATION=us-central1
```

## CLI Usage

**Image CLI**:
```bash
image-cli generate "prompt" --output img.png --provider gemini
image-cli refine img.png "changes" --output refined.png
image-cli upscale img.png --size 3000x3000 --output large.png
```

**Video CLI**:
```bash
python -m app.cli --src ./images --duration 5 --provider veo
python -m app.cli --prompts prompts.json --img-provider gemini
python -m app.cli --prompts prompts.json --dry-run
```

**Key flags**:
- `--provider`: veo | mock (video)
- `--img-provider`: gemini | gemini-pro | google | openai (images)
- `--pair-source`: prompts-only | existing | all
- `--dry-run`, `--images-only`, `--force-regen`, `--verbose`

## Testing

**Unit tests**: Core functions, mock providers (`@pytest.mark.unit`)  
**Integration tests**: Subprocess CLI invocations (`@pytest.mark.integration`)  
**Coverage**: 42%+ (excludes thin wrappers: `cli.py`, `veo.py`, `gemini.py`)

Run: `uv run pytest -q`

## Non-Functional

- **Cross-platform**: pathlib, platform-agnostic tools
- **Security**: Env vars only, no secrets in logs/manifest
- **Performance**: Lazy imports, concurrent groups (default: 2)
- **Observability**: Structured logging (1=info, 2=debug)
- **Determinism**: Natural sort, reproducible names, optional seed
- **Resilience**: Bounded retries, exponential backoff, continue-on-failure

## Package Management

```bash
uv pip install -e .        # Install
uv add package-name        # Add dependency
uv run pytest -q           # Test
uv run image-cli generate "prompt"
```

**Entry points** (`pyproject.toml`): `image-cli` → `app.image_cli:app`, `video-cli` → `app.cli:app`
