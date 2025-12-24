"""Standalone CLI for image generation, refinement, and upscaling.

This module provides a simple command-line interface for AI image operations
that can be used independently of the video generation pipeline.

Usage:
    # Generate a new image
    uv run python -m app.image_cli generate "a cat" --output cat.png
    
    # Refine an existing image
    uv run python -m app.image_cli refine cat.png "make it more fluffy" --output cat_fluffy.png
    
    # Upscale an image
    uv run python -m app.image_cli upscale cat.png --size 3000x3000 --output cat_large.png
    
    # Chain operations
    uv run python -m app.image_cli generate "a cat" | uv run python -m app.image_cli refine - "make it fluffy"
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Optional

import typer
from dotenv import load_dotenv

from .logging_conf import configure_logging, get_logger

app = typer.Typer(
    add_completion=False,
    pretty_exceptions_enable=False,
    rich_markup_mode=None,
    help="AI Image CLI - Generate, refine, and upscale images",
)
logger = get_logger(__name__)


@app.command()
def generate(
    preset_or_prompt: str = typer.Argument(..., help="Preset (fast/regular/ultra) or text prompt"),
    prompt: Optional[str] = typer.Argument(None, help="Text prompt (if preset specified)"),
    output: Path = typer.Option("output.png", "--output", "-o", help="Output image path"),
    provider: Optional[str] = typer.Option(None, "--provider", "-p", help="Override provider: gemini | gemini-pro | openai | google | imagen"),
    model: Optional[str] = typer.Option(None, "--model", "-m", help="Override model name (e.g., gpt-image-1-mini, dall-e-3, gemini-2.5-flash-image)"),
    size: Optional[str] = typer.Option(None, "--size", "-s", help="Override image size (e.g., 1024x1024, 2K, 4K)"),
    seed: Optional[int] = typer.Option(None, "--seed", help="Random seed for reproducibility"),
    negative: Optional[str] = typer.Option(None, "--negative", "-n", help="Negative prompt (what to avoid)"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show detailed debug logs"),
):
    """Generate a new image from a text prompt.
    
    Examples:
        # Using presets (recommended)
        image-cli generate fast "a cat"
        image-cli generate "a cat"  # uses fast preset (default)
        image-cli generate ultra "a cat in 4K"
        
        # Override preset with specific provider and model
        image-cli generate "a cat" --provider openai --model dall-e-3
        image-cli generate "a cat" --provider openai --model gpt-image-1
        
        # With custom output path
        image-cli generate fast "a cat" --output my_cat.png
        
        # With negative prompt
        image-cli generate "a cat" --negative "blurry, low quality"
    """
    load_dotenv()
    configure_logging(2 if verbose else 1)
    
    from .image_gen.base import ImagePrompt
    from .preset_config import load_image_preset
    
    # Determine if first arg is a preset or a prompt
    preset_names = ["fast", "regular", "ultra"]
    if preset_or_prompt.lower() in preset_names:
        # First arg is preset, second arg must be prompt
        if prompt is None:
            typer.echo("[ERROR] Prompt required after preset", err=True)
            raise typer.Exit(code=1)
        preset_name = preset_or_prompt.lower()
        actual_prompt = prompt
    else:
        # First arg is the prompt, use default preset
        preset_name = "fast"
        actual_prompt = preset_or_prompt
    
    # Resolve configuration: explicit flags override preset
    resolved_model = None
    if provider:
        # Explicit provider overrides preset
        from .preset_config import get_default_model_for_provider
        resolved_provider = provider
        resolved_model = model or get_default_model_for_provider(provider)
        resolved_size = size or "1024x1024"
        logger.info("Using explicit provider: %s, model: %s (overrides preset)", provider, resolved_model)
    else:
        # Load preset configuration
        try:
            preset_config = load_image_preset(preset_name)
            resolved_provider = preset_config.provider
            resolved_model = model or preset_config.model
            resolved_size = size or preset_config.size
            logger.info("Using preset: %s (provider=%s, model=%s, size=%s)", preset_name, resolved_provider, resolved_model, resolved_size)
        except ValueError as e:
            typer.echo(f"[ERROR] {e}", err=True)
            raise typer.Exit(code=1)
    
    # Create image prompt
    img_prompt = ImagePrompt(
        index=0,
        code="gen",
        positive_prompt=actual_prompt,
        negative_prompt=negative,
        target_filename=output.name,
    )
    
    # Select provider
    provider_instance = _get_image_provider(resolved_provider, model=resolved_model)
    
    # Generate image
    logger.info("Generating image with prompt: %s", actual_prompt[:100])
    output.parent.mkdir(parents=True, exist_ok=True)
    
    results = provider_instance.generate_images(
        [img_prompt],
        output.parent,
        size=resolved_size,
        seed=seed,
        skip_existing=False,
    )
    
    if results and results[0].path.exists():
        typer.echo(f"[OK] Image generated: {results[0].path}")
        typer.echo(f"     Size: {_get_image_size(results[0].path)}")
    else:
        typer.echo("[ERROR] Image generation failed", err=True)
        raise typer.Exit(code=1)


@app.command()
def refine(
    image: str = typer.Argument(..., help="Input image path (or '-' to read from stdin)"),
    prompt: str = typer.Argument(..., help="Refinement prompt (e.g., 'make it more colorful')"),
    output: Path = typer.Option("refined.png", "--output", "-o", help="Output image path"),
    provider: Optional[str] = typer.Option(None, "--provider", "-p", help="Override provider: gemini | gemini-pro | openai | google | imagen"),
    model: Optional[str] = typer.Option(None, "--model", "-m", help="Override model name"),
    preset: str = typer.Option("fast", "--preset", help="Quality preset: fast | regular | ultra"),
    size: Optional[str] = typer.Option(None, "--size", "-s", help="Override image size"),
    seed: Optional[int] = typer.Option(None, "--seed", help="Random seed"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show detailed logs"),
):
    """Refine an existing image with a text prompt.
    
    This uses the image as a reference/attachment for the generation,
    allowing you to modify or enhance existing images.
    
    Examples:
        # Refine an image with regular preset
        image-cli refine cat.png "make it more fluffy"
        
        # Use ultra preset for high quality
        image-cli refine cat.png "add glasses" --preset ultra
        
        # With custom output
        image-cli refine cat.png "add glasses" --output cat_glasses.png
        
        # Chain with generation
        image-cli generate "a cat" --output temp.png && image-cli refine temp.png "make it fluffy"
    """
    load_dotenv()
    configure_logging(2 if verbose else 1)
    
    # Handle stdin input
    if image == "-":
        typer.echo("Reading from stdin not yet implemented", err=True)
        raise typer.Exit(code=1)
    
    input_path = Path(image)
    if not input_path.exists():
        typer.echo(f"[ERROR] Input image not found: {input_path}", err=True)
        raise typer.Exit(code=1)
    
    from .image_gen.base import ImagePrompt
    from .preset_config import load_image_preset
    
    # Resolve configuration: explicit flags override preset
    resolved_model = None
    if provider:
        from .preset_config import get_default_model_for_provider
        resolved_provider = provider
        resolved_model = model or get_default_model_for_provider(provider)
        resolved_size = size or "1024x1024"
        logger.info("Using explicit provider: %s, model: %s (overrides preset)", provider, resolved_model)
    else:
        try:
            preset_config = load_image_preset(preset)
            resolved_provider = preset_config.provider
            resolved_model = model or preset_config.model
            resolved_size = size or preset_config.size
            logger.info("Using preset: %s (provider=%s, model=%s, size=%s)", preset, resolved_provider, resolved_model, resolved_size)
        except ValueError as e:
            typer.echo(f"[ERROR] {e}", err=True)
            raise typer.Exit(code=1)
    
    # Create refinement prompt with attachment
    img_prompt = ImagePrompt(
        index=0,
        code="refine",
        positive_prompt=prompt,
        target_filename=output.name,
        attachment=input_path.name,  # Reference the input image
    )
    
    # Copy input to output directory for attachment reference
    output.parent.mkdir(parents=True, exist_ok=True)
    import shutil
    temp_ref = output.parent / input_path.name
    if temp_ref != input_path:
        shutil.copy(input_path, temp_ref)
    
    # Select provider
    provider_instance = _get_image_provider(resolved_provider, model=resolved_model)
    
    # Generate refined image
    logger.info("Refining image: %s with prompt: %s", input_path, prompt[:100])
    
    results = provider_instance.generate_images(
        [img_prompt],
        output.parent,
        size=resolved_size,
        seed=seed,
        skip_existing=False,
    )
    
    # Clean up temp reference if needed
    if temp_ref != input_path and temp_ref.exists():
        temp_ref.unlink()
    
    if results and results[0].path.exists():
        typer.echo(f"[OK] Image refined: {results[0].path}")
        typer.echo(f"     Size: {_get_image_size(results[0].path)}")
    else:
        typer.echo("[ERROR] Image refinement failed", err=True)
        raise typer.Exit(code=1)


@app.command()
def crop(
    image: str = typer.Argument(..., help="Input image path"),
    output: Path = typer.Option("cropped.png", "--output", "-o", help="Output image path"),
    aspect: Optional[str] = typer.Option(None, "--aspect", "-a", help="Target aspect ratio (e.g., 9:16, 16:9, 1:1)"),
    x: Optional[int] = typer.Option(None, "--x", help="Crop starting X coordinate (left edge)"),
    y: Optional[int] = typer.Option(None, "--y", help="Crop starting Y coordinate (top edge)"),
    width: Optional[int] = typer.Option(None, "--width", "-w", help="Crop width in pixels"),
    height: Optional[int] = typer.Option(None, "--height", "-h", help="Crop height in pixels"),
    position: str = typer.Option("center", "--position", "-p", help="Crop position when using aspect ratio: center, top, bottom, left, right"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show detailed logs"),
):
    """Crop an image to a specific size or aspect ratio.
    
    Two modes:
    1. Aspect ratio mode: Automatically crops to aspect ratio from center (or specified position)
    2. Manual mode: Crop from specific coordinates with exact dimensions
    
    Examples:
        # Crop to 9:16 aspect ratio from center
        image-cli crop image.png --aspect 9:16 --output vertical.png
        
        # Crop to 16:9 from top
        image-cli crop image.png --aspect 16:9 --position top --output horizontal.png
        
        # Manual crop from specific coordinates
        image-cli crop image.png --x 100 --y 200 --width 1080 --height 1920 --output custom.png
        
        # Generate large image first, then crop multiple versions
        image-cli generate "prompt" --output large.png --size 1536x1536
        image-cli crop large.png --aspect 9:16 --output vertical.png
        image-cli crop large.png --aspect 16:9 --output horizontal.png
    """
    load_dotenv()
    configure_logging(2 if verbose else 1)
    
    input_path = Path(image)
    if not input_path.exists():
        typer.echo(f"[ERROR] Input image not found: {input_path}", err=True)
        raise typer.Exit(code=1)
    
    try:
        from PIL import Image
        
        # Open image
        img = Image.open(input_path)
        original_width, original_height = img.size
        
        logger.info("Cropping %s (size: %dx%d)", input_path, original_width, original_height)
        
        # Mode 1: Aspect ratio based cropping
        if aspect:
            # Parse aspect ratio
            try:
                aspect_parts = aspect.split(':')
                if len(aspect_parts) != 2:
                    raise ValueError("Invalid aspect ratio format")
                aspect_w = int(aspect_parts[0])
                aspect_h = int(aspect_parts[1])
            except (ValueError, IndexError):
                typer.echo(f"[ERROR] Invalid aspect ratio: {aspect}. Use format like '9:16' or '16:9'", err=True)
                raise typer.Exit(code=1)
            
            # Calculate crop dimensions to fit aspect ratio
            target_ratio = aspect_w / aspect_h
            current_ratio = original_width / original_height
            
            if current_ratio > target_ratio:
                # Image is wider than target - crop width
                crop_height = original_height
                crop_width = int(crop_height * target_ratio)
            else:
                # Image is taller than target - crop height
                crop_width = original_width
                crop_height = int(crop_width / target_ratio)
            
            # Calculate crop position
            if position == "center":
                crop_x = (original_width - crop_width) // 2
                crop_y = (original_height - crop_height) // 2
            elif position == "top":
                crop_x = (original_width - crop_width) // 2
                crop_y = 0
            elif position == "bottom":
                crop_x = (original_width - crop_width) // 2
                crop_y = original_height - crop_height
            elif position == "left":
                crop_x = 0
                crop_y = (original_height - crop_height) // 2
            elif position == "right":
                crop_x = original_width - crop_width
                crop_y = (original_height - crop_height) // 2
            else:
                typer.echo(f"[ERROR] Invalid position: {position}. Use: center, top, bottom, left, right", err=True)
                raise typer.Exit(code=1)
            
            logger.info("Cropping to aspect ratio %s from position '%s': %dx%d at (%d,%d)",
                       aspect, position, crop_width, crop_height, crop_x, crop_y)
        
        # Mode 2: Manual coordinate-based cropping
        elif x is not None and y is not None and width is not None and height is not None:
            crop_x = x
            crop_y = y
            crop_width = width
            crop_height = height
            
            # Validate coordinates
            if crop_x < 0 or crop_y < 0:
                typer.echo("[ERROR] Crop coordinates cannot be negative", err=True)
                raise typer.Exit(code=1)
            
            if crop_x + crop_width > original_width or crop_y + crop_height > original_height:
                typer.echo(f"[ERROR] Crop region ({crop_x},{crop_y},{crop_width},{crop_height}) exceeds image bounds ({original_width}x{original_height})", err=True)
                raise typer.Exit(code=1)
            
            logger.info("Manual crop: %dx%d at (%d,%d)", crop_width, crop_height, crop_x, crop_y)
        
        else:
            typer.echo("[ERROR] Either specify --aspect OR all of (--x, --y, --width, --height)", err=True)
            raise typer.Exit(code=1)
        
        # Perform crop
        crop_box = (crop_x, crop_y, crop_x + crop_width, crop_y + crop_height)
        cropped = img.crop(crop_box)
        
        # Save
        output.parent.mkdir(parents=True, exist_ok=True)
        cropped.save(output, optimize=True)
        
        typer.echo(f"[OK] Image cropped: {output}")
        typer.echo(f"     Original: {original_width}x{original_height}")
        typer.echo(f"     Cropped: {crop_width}x{crop_height}")
        typer.echo(f"     Position: ({crop_x}, {crop_y})")
        
    except Exception as e:
        logger.error("Cropping failed: %s", str(e))
        typer.echo(f"[ERROR] Cropping failed: {e}", err=True)
        raise typer.Exit(code=1)


@app.command()
def upscale(
    image: str = typer.Argument(..., help="Input image path"),
    output: Path = typer.Option("upscaled.png", "--output", "-o", help="Output image path"),
    size: str = typer.Option("3000x3000", "--size", "-s", help="Target size (e.g., 3000x3000, 2048x2048)"),
    method: str = typer.Option("lanczos", "--method", "-m", help="Upscaling method: lanczos | bicubic | nearest"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show detailed logs"),
):
    """Upscale an image to a higher resolution.
    
    Uses high-quality resampling algorithms to increase image size
    while maintaining quality.
    
    Examples:
        # Upscale to 3000x3000
        image-cli upscale cat.png --size 3000x3000
        
        # Upscale with custom method
        image-cli upscale cat.png --size 2048x2048 --method bicubic
        
        # Chain with generation
        image-cli generate "a cat" --output cat.png && image-cli upscale cat.png --size 3000x3000
    """
    load_dotenv()
    configure_logging(2 if verbose else 1)
    
    input_path = Path(image)
    if not input_path.exists():
        typer.echo(f"[ERROR] Input image not found: {input_path}", err=True)
        raise typer.Exit(code=1)
    
    # Parse target size
    try:
        width, height = map(int, size.lower().split('x'))
    except ValueError:
        typer.echo(f"[ERROR] Invalid size format: {size}. Use format like '3000x3000'", err=True)
        raise typer.Exit(code=1)
    
    # Upscale image
    logger.info("Upscaling %s to %dx%d using %s", input_path, width, height, method)
    
    try:
        from PIL import Image
        
        # Open image
        img = Image.open(input_path)
        original_size = img.size
        
        # Select resampling filter
        resample_map = {
            "lanczos": Image.Resampling.LANCZOS,
            "bicubic": Image.Resampling.BICUBIC,
            "nearest": Image.Resampling.NEAREST,
            "bilinear": Image.Resampling.BILINEAR,
        }
        
        if method.lower() not in resample_map:
            typer.echo(f"[ERROR] Unknown method: {method}. Use: lanczos, bicubic, nearest, bilinear", err=True)
            raise typer.Exit(code=1)
        
        resample_filter = resample_map[method.lower()]
        
        # Upscale
        logger.info("Upscaling from %dx%d to %dx%d", *original_size, width, height)
        upscaled = img.resize((width, height), resample=resample_filter)
        
        # Save
        output.parent.mkdir(parents=True, exist_ok=True)
        upscaled.save(output, optimize=True)
        
        typer.echo(f"[OK] Image upscaled: {output}")
        typer.echo(f"     Original: {original_size[0]}x{original_size[1]}")
        typer.echo(f"     New size: {width}x{height}")
        typer.echo(f"     Method: {method}")
        
    except Exception as e:
        logger.error("Upscaling failed: %s", str(e))
        typer.echo(f"[ERROR] Upscaling failed: {e}", err=True)
        raise typer.Exit(code=1)


def _get_image_provider(provider_name: str, model: Optional[str] = None):
    """Get image provider instance by name.
    
    Args:
        provider_name: Provider name (openai, google, gemini, gemini-pro, imagen)
        model: Optional model name to override provider default
    
    Returns:
        Provider instance configured with the specified model
    """
    if provider_name == "openai":
        from .image_gen.openai import OpenAIImageProvider
        return OpenAIImageProvider(model=model) if model else OpenAIImageProvider()
    elif provider_name == "google":
        from .image_gen.google import GoogleImageProvider
        return GoogleImageProvider(model_name=model) if model else GoogleImageProvider()
    elif provider_name == "gemini":
        from .image_gen.gemini import GeminiImageProvider
        return GeminiImageProvider(model_name=model) if model else GeminiImageProvider()
    elif provider_name == "gemini-pro":
        from .image_gen.gemini_pro import GeminiProImageProvider
        return GeminiProImageProvider(model_name=model) if model else GeminiProImageProvider()
    elif provider_name == "imagen":
        from .image_gen.imagen import ImagenImageProvider
        return ImagenImageProvider(model_name=model) if model else ImagenImageProvider()
    else:
        typer.echo(f"[ERROR] Unknown provider: {provider_name}", err=True)
        raise typer.Exit(code=1)


def _get_image_size(path: Path) -> str:
    """Get image dimensions as string."""
    try:
        from PIL import Image
        with Image.open(path) as img:
            return f"{img.size[0]}x{img.size[1]}"
    except Exception:
        return "unknown"


if __name__ == "__main__":
    app()

