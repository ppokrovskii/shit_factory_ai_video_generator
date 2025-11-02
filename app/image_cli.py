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
    prompt: str = typer.Argument(..., help="Text prompt for image generation"),
    output: Path = typer.Option("output.png", "--output", "-o", help="Output image path"),
    provider: str = typer.Option("gemini", "--provider", "-p", help="Image provider: gemini | openai | google"),
    size: str = typer.Option("1024x1024", "--size", "-s", help="Image size (e.g., 1024x1024, 512x512)"),
    seed: Optional[int] = typer.Option(None, "--seed", help="Random seed for reproducibility"),
    negative: Optional[str] = typer.Option(None, "--negative", "-n", help="Negative prompt (what to avoid)"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show detailed debug logs"),
):
    """Generate a new image from a text prompt.
    
    Examples:
        # Basic generation
        image-cli generate "a cat in a steampunk city"
        
        # With custom output path
        image-cli generate "a cat" --output my_cat.png
        
        # With negative prompt
        image-cli generate "a cat" --negative "blurry, low quality"
        
        # Using specific provider and size
        image-cli generate "a cat" --provider openai --size 512x512
    """
    load_dotenv()
    configure_logging(2 if verbose else 1)
    
    from .image_gen.base import ImagePrompt
    
    # Create image prompt
    img_prompt = ImagePrompt(
        index=0,
        code="gen",
        positive_prompt=prompt,
        negative_prompt=negative,
        target_filename=output.name,
    )
    
    # Select provider
    provider_instance = _get_image_provider(provider)
    
    # Generate image
    logger.info("Generating image with prompt: %s", prompt[:100])
    output.parent.mkdir(parents=True, exist_ok=True)
    
    results = provider_instance.generate_images(
        [img_prompt],
        output.parent,
        size=size,
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
    provider: str = typer.Option("gemini", "--provider", "-p", help="Image provider: gemini | openai | google"),
    size: str = typer.Option("1024x1024", "--size", "-s", help="Image size"),
    seed: Optional[int] = typer.Option(None, "--seed", help="Random seed"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show detailed logs"),
):
    """Refine an existing image with a text prompt.
    
    This uses the image as a reference/attachment for the generation,
    allowing you to modify or enhance existing images.
    
    Examples:
        # Refine an image
        image-cli refine cat.png "make it more fluffy"
        
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
    provider_instance = _get_image_provider(provider)
    
    # Generate refined image
    logger.info("Refining image: %s with prompt: %s", input_path, prompt[:100])
    
    results = provider_instance.generate_images(
        [img_prompt],
        output.parent,
        size=size,
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


def _get_image_provider(provider_name: str):
    """Get image provider instance by name."""
    if provider_name == "openai":
        from .image_gen.openai import OpenAIImageProvider
        return OpenAIImageProvider()
    elif provider_name == "google":
        from .image_gen.google import GoogleImageProvider
        return GoogleImageProvider()
    elif provider_name == "gemini":
        from .image_gen.gemini import GeminiImageProvider
        return GeminiImageProvider()
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

