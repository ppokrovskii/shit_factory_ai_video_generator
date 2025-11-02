# Installation Guide

This guide shows how to install and use the image CLI tools from anywhere on your system.

## Quick Install

### Option 1: Install with uv (Recommended)

```bash
# Clone the repository
git clone <repository-url>
cd shit_factory_ai_video_generator

# Install in development mode
uv pip install -e .

# Verify installation
image-cli --help
video-cli --help
```

### Option 2: Install with pip

```bash
# Clone the repository
git clone <repository-url>
cd shit_factory_ai_video_generator

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e .

# Verify installation
image-cli --help
video-cli --help
```

### Option 3: Install from source (system-wide)

```bash
# Clone the repository
git clone <repository-url>
cd shit_factory_ai_video_generator

# Install system-wide (requires admin/sudo)
pip install .

# Now available globally
image-cli --help
```

## Set Up Credentials

Create a `.env` file in your home directory or project directory:

```bash
# For Gemini (default, recommended)
GOOGLE_API_KEY=your-google-api-key

# For OpenAI (alternative)
OPENAI_API_KEY=your-openai-api-key
```

Get your Google API key from: https://aistudio.google.com/apikey

## Verify Installation

Test that everything works:

```bash
# Check version and help
image-cli --help
video-cli --help

# Generate a test image (requires API key)
image-cli generate "test image" --output test.png

# Upscale an image (no API key needed)
image-cli upscale test.png --size 2048x2048 --output test_large.png
```

## Using from Anywhere

Once installed, you can use the CLI from any directory:

```bash
# Generate images in your home directory
cd ~
image-cli generate "a cat" --output cat.png

# Generate images in a project
cd /path/to/my/project
image-cli generate "logo concept" --output logo.png
image-cli upscale logo.png --size 4096x4096 --output logo_hd.png

# Use in scripts
#!/bin/bash
for i in {1..5}; do
    image-cli generate "scene $i" --output "scene_$i.png" --seed $i
done
```

## Shell Aliases (Optional)

Add these to your `.bashrc`, `.zshrc`, or PowerShell profile:

### Bash/Zsh

```bash
# ~/.bashrc or ~/.zshrc
alias imggen='image-cli generate'
alias imgref='image-cli refine'
alias imgup='image-cli upscale'
```

Usage:
```bash
imggen "a cat" --output cat.png
imgref cat.png "add goggles" --output cat2.png
imgup cat2.png --size 3000x3000 --output cat_hd.png
```

### PowerShell

```powershell
# $PROFILE
function imggen { image-cli generate $args }
function imgref { image-cli refine $args }
function imgup { image-cli upscale $args }
```

## Docker (Alternative Installation)

If you prefer Docker:

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY . /app

RUN pip install -e .

ENTRYPOINT ["image-cli"]
```

Build and use:
```bash
docker build -t image-cli .
docker run -e GOOGLE_API_KEY=$GOOGLE_API_KEY image-cli generate "a cat"
```

## Troubleshooting

### Command not found

If you get "command not found" errors:

1. **Check installation:**
   ```bash
   pip list | grep shit-factory
   ```

2. **Check PATH:**
   ```bash
   # Find where scripts are installed
   python -c "import sys; print(sys.prefix + '/bin')"
   
   # Add to PATH if needed (Bash/Zsh)
   export PATH="$HOME/.local/bin:$PATH"
   
   # Or on Windows
   set PATH=%USERPROFILE%\AppData\Local\Programs\Python\Python311\Scripts;%PATH%
   ```

3. **Reinstall:**
   ```bash
   pip uninstall shit-factory-ai-video-generator
   pip install -e .
   ```

### Import errors

If you get import errors:

```bash
# Reinstall dependencies
uv pip install -e .
# Or
pip install -r requirements.txt
```

### API key not found

If you get API key errors:

1. **Check .env file exists:**
   ```bash
   ls -la .env
   cat .env
   ```

2. **Set environment variable:**
   ```bash
   # Bash/Zsh
   export GOOGLE_API_KEY=your-key
   
   # PowerShell
   $env:GOOGLE_API_KEY="your-key"
   
   # CMD
   set GOOGLE_API_KEY=your-key
   ```

3. **Use .env in current directory:**
   Create `.env` file in the directory where you run the command.

## Uninstall

To remove the tools:

```bash
pip uninstall shit-factory-ai-video-generator
```

## Next Steps

- See [IMAGE_CLI.md](IMAGE_CLI.md) for complete usage documentation
- See [README.md](README.md) for video generation documentation
- Check [.cursorrules](.cursorrules) for project style guidelines

