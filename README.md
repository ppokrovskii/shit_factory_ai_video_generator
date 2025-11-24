# AI Image & Video Generator CLI

Command-line tools for AI-powered image generation, editing, and video creation.

## Quick Install

```bash
# Clone and install
git clone <repository-url>
cd shit_factory_ai_video_generator
uv pip install -e .

# Set up API key
echo "GOOGLE_API_KEY=your-key" > .env
```

Get your API key: https://aistudio.google.com/apikey

## Image CLI Commands

### Generate Image
```bash
uv run image-cli generate "your prompt" --output image.png
```

### Refine Image (AI-powered editing)
```bash
uv run image-cli refine input.png "make it brighter" --output refined.png
```

### Crop Image (for different aspect ratios)
```bash
# Smart crop to aspect ratio
uv run image-cli crop input.png --aspect 9:16 --output vertical.png
uv run image-cli crop input.png --aspect 16:9 --output horizontal.png

# Manual crop with coordinates
uv run image-cli crop input.png --x 100 --y 200 --width 1080 --height 1920 --output custom.png
```

### Upscale Image
```bash
uv run image-cli upscale input.png --size 3000x3000 --output large.png
```

## Common Workflows

### Workflow 1: Generate → Crop Multiple Formats
```bash
# Generate large square image
uv run image-cli generate "cinematic portrait, centered composition" --output base.png --size 1536x1536

# Crop for different platforms
uv run image-cli crop base.png --aspect 9:16 --output vertical.png    # Instagram/TikTok
uv run image-cli crop base.png --aspect 16:9 --output horizontal.png  # YouTube
uv run image-cli crop base.png --aspect 1:1 --output square.png       # Instagram post
```

### Workflow 2: Generate → Refine → Upscale
```bash
# Generate base
uv run image-cli generate "your prompt" --output step1.png

# Refine with AI
uv run image-cli refine step1.png "add more details" --output step2.png

# Upscale to high resolution
uv run image-cli upscale step2.png --size 3000x3000 --output final.png
```

## Video CLI (Image-to-Video)

Generate transition videos from image sequences:

```bash
# Generate videos from images in .src folder
uv run python -m app.cli --src ./.src --duration 5

# With custom prompts
uv run python -m app.cli --prompts ./.src/video_prompts.json
```

See [video_generation_guide.md](video_generation_guide.md) for details.

## Image Providers

Switch between AI providers with `--provider`:

```bash
# Gemini (default, fastest)
uv run image-cli generate "prompt" --provider gemini

# Google Imagen 3.0 (supports aspect ratios: 9:16, 16:9, 3:4, 4:3, 1:1)
uv run image-cli generate "prompt" --provider google --size 768x1408

# OpenAI (DALL-E)
uv run image-cli generate "prompt" --provider openai
```

**Supported aspect ratios (Google Imagen 3.0):**
- `768x1408` (9:16) - vertical for stories/shorts
- `1408x768` (16:9) - horizontal for YouTube
- `896x1280` (3:4) - portrait
- `1280x896` (4:3) - landscape
- `1024x1024` (1:1) - square

## Installation Options

### Option 1: Use with `uv run` (recommended)
```bash
uv run image-cli generate "prompt"
```

### Option 2: Add to PATH (Windows)
```bash
# One-time setup
setx PATH "%PATH%;C:\path\to\project\.venv\Scripts"

# Then use directly
image-cli generate "prompt"
```

### Option 3: Create batch wrapper
```cmd
echo @echo off > C:\Windows\image-cli.bat
echo C:\path\to\.venv\Scripts\image-cli.exe %%* >> C:\Windows\image-cli.bat
```

## Environment Variables

Create `.env` file:
```bash
# Required for image generation
GOOGLE_API_KEY=your-google-api-key

# Optional: OpenAI
OPENAI_API_KEY=your-openai-key

# Optional: Google Cloud (for Vertex AI)
GOOGLE_CLOUD_PROJECT=your-project-id
VERTEX_LOCATION=us-central1
VERTEX_IMAGEN_MODEL=imagen-3.0-generate-001
```

## Quick Reference

| Command | Description |
|---------|-------------|
| `generate` | Create image from text prompt |
| `refine` | Modify image with AI |
| `crop` | Cut image to size/aspect ratio |
| `upscale` | Increase resolution |
| `--output` / `-o` | Specify output path |
| `--provider` / `-p` | Choose AI provider |
| `--size` / `-s` | Set image size |
| `--aspect` / `-a` | Crop to aspect ratio |
| `--verbose` / `-v` | Show detailed logs |

## Social Media Sizes

**Instagram/TikTok/Shorts:** 1080x1920 (9:16)
```bash
uv run image-cli crop image.png --aspect 9:16 --output vertical.png
uv run image-cli upscale vertical.png --size 1080x1920 --output ig.png
```

**YouTube/Horizontal:** 1920x1080 (16:9)
```bash
uv run image-cli crop image.png --aspect 16:9 --output horizontal.png
uv run image-cli upscale horizontal.png --size 1920x1080 --output yt.png
```

**Instagram Post:** 1080x1080 (1:1)
```bash
uv run image-cli crop image.png --aspect 1:1 --output square.png
uv run image-cli upscale square.png --size 1080x1080 --output post.png
```

## Help

```bash
# General help
uv run image-cli --help

# Command-specific help
uv run image-cli generate --help
uv run image-cli crop --help
uv run image-cli upscale --help
```

## Documentation

- **[IMAGE_CLI.md](IMAGE_CLI.md)** - Complete image CLI guide with examples
- **[INSTALL.md](INSTALL.md)** - Detailed installation instructions
- **[INSTALL_WINDOWS.md](INSTALL_WINDOWS.md)** - Windows-specific setup
- **[QUICK_START.md](QUICK_START.md)** - Get started in 3 steps
- **[video_generation_guide.md](video_generation_guide.md)** - Video generation guide

## Testing

```bash
uv run pytest -q
```

## Project Info

Built with:
- **Image generation**: Google Gemini 2.5 Flash, Imagen 3.0, OpenAI DALL-E
- **Video generation**: Google Veo 3
- **CLI framework**: Typer
- **Package manager**: uv
