# Quick Start - Image CLI

Get started with the image CLI in 3 steps!

## 1. Install

```bash
cd C:\Users\MI\GitHub\shit_factory_ai_video_generator
uv pip install -e .
```

## 2. Set up API key

```bash
# Create .env file in project root
echo "GOOGLE_API_KEY=your-api-key-here" > .env
```

Get your API key from: https://aistudio.google.com/apikey

## 3. Use the CLI

### From project directory

```bash
# Generate an image
uv run image-cli generate "a cat in a steampunk city" --output cat.png

# Refine it
uv run image-cli refine cat.png "add brass goggles" --output cat_refined.png

# Upscale to high resolution
uv run image-cli upscale cat_refined.png --size 3000x3000 --output cat_hd.png
```

### From ANY directory

After installation, you can use it from anywhere:

```bash
# Go to any directory
cd ~/Desktop

# Generate image
uv run image-cli generate "a logo" --output logo.png

# Upscale it
uv run image-cli upscale logo.png --size 4096x4096 --output logo_hd.png
```

## Available Commands

### Generate
```bash
uv run image-cli generate PROMPT [--output PATH] [--provider gemini|openai|google]
```

### Refine
```bash
uv run image-cli refine IMAGE PROMPT [--output PATH]
```

### Upscale
```bash
uv run image-cli upscale IMAGE [--size WIDTHxHEIGHT] [--output PATH]
```

## Examples

### Basic generation
```bash
uv run image-cli generate "a cat" --output cat.png
```

### With style
```bash
uv run image-cli generate "character portrait, cel-shaded, \
steampunk clothing with brass mechanisms, Victorian-era background" \
--output character.png
```

### With negative prompt
```bash
uv run image-cli generate "a cat" \
--negative "blurry, low quality, distorted" \
--output cat.png
```

### Refine existing image
```bash
uv run image-cli refine cat.png "make it more fluffy and orange" \
--output cat_fluffy.png
```

### Upscale to print quality
```bash
uv run image-cli upscale cat.png --size 3000x3000 --output cat_print.png
```

### Full workflow
```bash
# Step 1: Generate
uv run image-cli generate "steampunk cat" --output step1.png --seed 42

# Step 2: Refine
uv run image-cli refine step1.png "add brass goggles and top hat" --output step2.png

# Step 3: Enhance
uv run image-cli refine step2.png "add steam effects" --output step3.png

# Step 4: Upscale
uv run image-cli upscale step3.png --size 3000x3000 --output final.png
```

## Tips

1. **Use `--seed` for reproducible results:**
   ```bash
   uv run image-cli generate "a cat" --seed 42 --output cat1.png
   uv run image-cli generate "a cat" --seed 42 --output cat2.png
   # cat1.png and cat2.png will be similar
   ```

2. **Use smaller sizes for testing:**
   ```bash
   uv run image-cli generate "test" --size 512x512 --output test.png
   ```

3. **Upscale doesn't need API key:**
   ```bash
   # Works without GOOGLE_API_KEY
   uv run image-cli upscale myimage.png --size 2048x2048
   ```

4. **Check help for all options:**
   ```bash
   uv run image-cli --help
   uv run image-cli generate --help
   uv run image-cli refine --help
   uv run image-cli upscale --help
   ```

## Troubleshooting

### Command not found
Use `uv run image-cli` instead of just `image-cli`

### API key error
Check your `.env` file contains:
```
GOOGLE_API_KEY=your-actual-key-here
```

### Import error
Reinstall the package:
```bash
uv pip install -e .
```

## More Information

- **Complete guide**: [IMAGE_CLI.md](IMAGE_CLI.md)
- **Installation help**: [INSTALL.md](INSTALL.md)
- **Project README**: [README.md](README.md)

## Batch Processing Example

```bash
# Generate multiple images
for i in {1..5}; do
    uv run image-cli generate "scene $i" --output "scene_$i.png" --seed $i
done

# Upscale all of them
for img in scene_*.png; do
    uv run image-cli upscale "$img" --size 2048x2048 --output "hd_$img"
done
```

## Success!

You're now ready to generate, refine, and upscale AI images from anywhere on your system! 🎉

