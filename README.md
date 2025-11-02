# AI Video & Image Generator

Two powerful CLI tools:

1. **Video CLI** - Generate short transition videos between ordered images using a pluggable provider abstraction. Default provider `veo` uses **Google Veo 3.1-fast-generate-preview** for image-to-video transitions **(8 seconds per video, duration not configurable)**. Images generated with **Gemini 2.5 Flash Image** for **Slavic Steampunk post-apocalyptic** visuals.

2. **Image CLI** - Standalone tool for AI-powered image generation, refinement, and upscaling. Can be used independently or to prepare images for video generation.

**⚠️ Important:** Veo 3.1 generates 8-second videos by default. The `--duration` parameter is passed to the API but currently ignored by Google.

## Quickstart

### Video Generation

1) **Set up environment:**
```bash
uv venv
uv pip install -e .
video-cli --help
```

2) **Generate everything (images + videos):**
```bash
# With installed CLI (recommended)
video-cli

# Or with uv run
uv run python -m app.cli

# Or directly with Python
python -m app.cli
```

That's it! By default:
- Looks for `./.src/video_prompts.json` (auto-generates images)
- Generates videos from image transitions
- Outputs to `./.out/`

3) **Test with first N videos:**
```bash
uv run python -m app.cli --limit 3
```

4) **See detailed debug logs:**
```bash
uv run python -m app.cli --verbose
```

5) **Dry run (preview without generating):**
```bash
uv run python -m app.cli --dry-run
```

6) **Only generate images (skip videos):**
```bash
uv run python -m app.cli --images-only
```

7) **Only generate videos from existing images:**
```bash
uv run python -m app.cli --prompts ""
# Empty prompts means: use existing images in ./.src/
```

### Advanced Options

- **Custom prompts file:**
```bash
uv run python -m app.cli --prompts path/to/prompts.json
```

- **Change image provider:**
```bash
uv run python -m app.cli --img-provider google   # Vertex Imagen
uv run python -m app.cli --img-provider openai   # DALL-E
# Default: gemini (Gemini 2.5 Flash)
```

- **Force regenerate all images:**
```bash
uv run python -m app.cli --force-regen
```

- **Merge generated + existing images:**
```bash
uv run python -m app.cli --pair-source all
```

- **Image size and model:** controlled via `.env` (see below)
- **Grouped image generation:** prompts can include `group` field for sequential dependencies within groups, concurrent across groups (flag: `--img-concurrency`)

### Provider credentials

#### Google Veo 3 (default video provider)
- `veo` uses Google Veo 3 via the Gemini API for video generation
- Requires `GOOGLE_API_KEY` in `.env`:
```
# Get your API key from https://aistudio.google.com/apikey
GOOGLE_API_KEY=your_api_key_here
# Optional: specify Veo model (default: veo-3.0-generate-preview)
VEO_MODEL=veo-3.0-generate-preview
```
- **Note**: Veo 3 is priced at $0.75 per second of video generated
- Videos are generated asynchronously; the system polls until completion (timeout: 60 minutes)

#### OpenAI Images (alternative image provider)
```
OPENAI_API_KEY=...
# Model options (cheapest to most expensive):
# gpt-image-1-mini (default, ~80% cheaper, ideal for dev)
# dall-e-2, dall-e-3, gpt-image-1 (highest quality for prod)
OPENAI_IMAGE_MODEL=gpt-image-1-mini
# Image size: 1024x1024 (square) | 1024x1536 (portrait) | 1536x1024 (landscape) | auto
# Note: Smaller sizes not supported; use gpt-image-1-mini for cost savings instead
OPENAI_IMAGE_SIZE=1024x1024
```

#### Google Gemini 2.5 Flash Image (default image provider)
- **Simpler setup:** Just API key, no gcloud/ADC needed!
- **Get API key:** https://aistudio.google.com/apikey
- Set in `.env`:
```
GOOGLE_API_KEY=your-api-key-here
GEMINI_IMAGE_MODEL=gemini-2.5-flash-image  # optional, this is default
```
- **Features:**
  - ✅ Multi-image fusion
  - ✅ Better character/style consistency with reference images
  - ✅ Conversational editing support
  - ✅ Simpler authentication (just API key)
  - ✅ No gcloud CLI or ADC setup required

#### Google Vertex Imagen 2/3 (alternative image provider)
- **To use:** `--img-provider google`
- Requires Application Default Credentials (ADC):
  - User credentials: `gcloud auth application-default login`
  - Or service account: Set `GOOGLE_APPLICATION_CREDENTIALS=path/to/key.json`
- Set in `.env`:
```
GOOGLE_CLOUD_PROJECT=your-project-id
VERTEX_LOCATION=us-central1
VERTEX_IMAGEN_MODEL=imagen-3.0-generate-001
# Optional if using service account:
# GOOGLE_APPLICATION_CREDENTIALS=C:\path\to\service-account-key.json
```
- Enable Vertex AI API: `gcloud services enable aiplatform.googleapis.com --project YOUR_PROJECT_ID`
- Default model is `imagen-3.0-generate-001` (Imagen 3.0). Other options: `imagegeneration@006` (Imagen 2).
- Used for text-to-image and edit mode (when `attachment` is provided).
- In unit tests, the provider is mocked and does not call external services.

### GCS Bucket Management (Video Generation)

**Required for Veo video generation:**
```env
# Create a GCS bucket first
VERTEX_VEO_OUTPUT_BUCKET=gs://your-bucket-name/videos/
VERTEX_VEO_MODEL=veo-2.0-generate-001  # or veo-3.1-fast-generate-preview
```

**Create GCS bucket with auto-cleanup:**

**Option 1: Use helper script (recommended)**
```bash
# Linux/Mac
./scripts/setup_gcs_lifecycle.sh YOUR_PROJECT_ID your-unique-bucket-name

# Windows PowerShell
.\scripts\setup_gcs_lifecycle.ps1 YOUR_PROJECT_ID your-unique-bucket-name
```

**Option 2: Manual setup**
```bash
# Create bucket
gsutil mb -p YOUR_PROJECT_ID -l us-central1 gs://your-unique-bucket-name

# Set lifecycle policy to auto-delete files after 7 days
echo '{"lifecycle":{"rule":[{"action":{"type":"Delete"},"condition":{"age":7}}]}}' > lifecycle.json
gsutil lifecycle set lifecycle.json gs://your-unique-bucket-name
```

**Smart features:**
- ✅ **Deterministic naming** - Videos named as `<output>_<model>.mp4` 
- ✅ **Resume interrupted runs** - If generation completed but download failed, reuses existing GCS video
- ✅ **No re-generation** - Same model + inputs = fetches from GCS instead of regenerating
- ✅ **Auto-cleanup after download** - Deletes from GCS immediately after successful download
- ✅ **Auto-cleanup for orphaned files** - GCS lifecycle policy deletes files older than 7 days (catches failures)
- ℹ️ **Directory structure handling** - Vertex AI may create directory structures in GCS; download logic automatically handles both direct files and nested directories

**Storage cost management:**
- Videos are deleted from GCS immediately after download (primary cleanup)
- GCS lifecycle policy auto-deletes any remaining files after 7 days (backup cleanup for failures)
- Zero manual intervention needed!

### Image Generation (Standalone)

Use the image CLI for standalone image operations:

```bash
# Generate an image
image-cli generate "a cat in a steampunk city" --output cat.png

# Refine an image with AI
image-cli refine cat.png "add brass goggles" --output cat_refined.png

# Upscale to high resolution
image-cli upscale cat.png --size 3000x3000 --output cat_hd.png
```

**See [IMAGE_CLI.md](IMAGE_CLI.md) for complete documentation and examples.**

## Testing
```bash
uv run pytest -q

# Run specific test file
uv run pytest tests/test_image_cli.py -v

# Run without coverage check
uv run pytest tests/test_image_cli.py --no-cov
```
