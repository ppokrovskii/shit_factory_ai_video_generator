# Windows Installation Guide

Quick guide to install and use the image CLI on Windows (CMD).

## Installation

```cmd
cd C:\Users\MI\GitHub\shit_factory_ai_video_generator
uv pip install -e .
```

## Make CLI Globally Available

### Option 1: Add to PATH (Recommended)

**One-time setup:**
```cmd
setx PATH "%PATH%;C:\Users\MI\GitHub\shit_factory_ai_video_generator\.venv\Scripts"
```

**Restart your CMD window**, then use directly:
```cmd
image-cli --help
video-cli --help
```

### Option 2: Create Batch Wrappers

Create wrapper files in `C:\Windows\`:

```cmd
echo @echo off > C:\Windows\image-cli.bat
echo C:\Users\MI\GitHub\shit_factory_ai_video_generator\.venv\Scripts\image-cli.exe %%* >> C:\Windows\image-cli.bat

echo @echo off > C:\Windows\video-cli.bat
echo C:\Users\MI\GitHub\shit_factory_ai_video_generator\.venv\Scripts\video-cli.exe %%* >> C:\Windows\video-cli.bat
```

Use from anywhere:
```cmd
image-cli generate "prompt" --output output.png
```

### Option 3: Use UV Run (No Setup Needed)

Works immediately without PATH changes:

```cmd
uv run image-cli generate "prompt" --output output.png
uv run image-cli refine image.png "prompt" --output refined.png
uv run image-cli upscale image.png --size 3000x3000 --output large.png
```

## Usage Examples

### Generate Image
```cmd
uv run image-cli generate "Slavic steampunk cat" --output cat.png
```

### With Negative Prompt
```cmd
uv run image-cli generate "portrait" --negative "blur, low quality" --output portrait.png
```

### Refine Image
```cmd
uv run image-cli refine cat.png "add brass goggles" --output cat_refined.png
```

### Upscale
```cmd
uv run image-cli upscale cat.png --size 3000x3000 --output cat_hd.png
```

## Troubleshooting

### "command not found"
- Make sure you restarted CMD after adding to PATH
- Or use `uv run image-cli` instead

### "python not found"
- Python 3.11+ must be installed
- Run: `python --version` to verify

### "module not found"
- Reinstall: `uv pip install -e .`

## Quick Reference

| Command | Description |
|---------|-------------|
| `image-cli generate` | Create new image from prompt |
| `image-cli refine` | Modify existing image |
| `image-cli upscale` | Increase resolution |
| `--output` or `-o` | Specify output path |
| `--provider` or `-p` | Choose AI provider (gemini/openai/google) |
| `--size` or `-s` | Set image size |
| `--negative` or `-n` | Negative prompt |
| `--verbose` or `-v` | Show detailed logs |

## Full Example

```cmd
:: Generate
uv run image-cli generate "steampunk workshop" --output step1.png --seed 42

:: Refine
uv run image-cli refine step1.png "add steam effects" --output step2.png

:: Upscale
uv run image-cli upscale step2.png --size 3000x3000 --output final.png
```


