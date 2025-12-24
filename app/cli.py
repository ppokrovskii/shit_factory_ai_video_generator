from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Optional

import typer
from dotenv import load_dotenv

from .logging_conf import configure_logging, get_logger
from .io_scan import discover_images
from .core_pairs import consecutive_pairs
from .engine import run_jobs
from .manifest import write_manifest
from .prompt_schema import load_prompts
from .image_gen.scheduler import generate_grouped_images

# Lazy imports for providers to avoid slow startup
# (VEOProvider imports google-cloud-sdk which is heavy)


app = typer.Typer(
    add_completion=False, 
    pretty_exceptions_enable=False,
    rich_markup_mode=None,
    no_args_is_help=False,
)
logger = get_logger(__name__)


@app.command()
def main(
    prompts: Optional[Path] = typer.Option(None, "--prompts", help="Path to prompts JSON (default: ./.src/video_prompts.json if exists)"),
    src: Path = typer.Option(Path("./.src"), "--src", exists=True, file_okay=False, dir_okay=True, readable=True, help="Image source directory (default: ./.src)"),
    out: Path = typer.Option(Path("./.out"), "--out", help="Output directory for videos (default: ./.out)"),
    provider: Optional[str] = typer.Option(None, "--provider", help="Override video provider: veo | mock"),
    video_preset: str = typer.Option("regular", "--video-preset", help="Video quality preset: fast | regular | ultra"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Preview plan without generating"),
    verbose: bool = typer.Option(False, "--verbose", help="Show detailed debug logs"),
    limit: Optional[int] = typer.Option(None, "--limit", min=1, help="Generate only first N videos (for testing)"),
    # Image generation options
    img_provider: Optional[str] = typer.Option(None, "--img-provider", help="Override image provider: gemini | gemini-pro | google | openai"),
    img_model: Optional[str] = typer.Option(None, "--img-model", help="Override image model (e.g., gpt-image-1-mini, dall-e-3)"),
    img_preset: str = typer.Option("fast", "--img-preset", help="Image quality preset: fast | regular | ultra"),
    img_concurrency: int = typer.Option(2, "--img-concurrency", min=1, help="Max concurrent image generation groups"),
    img_out: Path = typer.Option(Path("./.src"), "--img-out", help="Output directory for generated images (default: same as --src)"),
    pair_source: str = typer.Option("prompts-only", "--pair-source", help="Video pair source: prompts-only | existing | all"),
    seed: Optional[int] = typer.Option(None, "--seed", help="Random seed for image generation"),
    force_regen: bool = typer.Option(False, "--force-regen", help="Regenerate images even if they exist"),
    images_only: bool = typer.Option(False, "--images-only", help="Generate only images, skip videos"),
    # Advanced/rare options (hidden from main help but still available)
    duration: Optional[float] = typer.Option(None, "--duration", min=0.1, hidden=True, help="Video duration in seconds (overrides preset)"),
):
    # Load environment variables from .env if present
    load_dotenv()
    
    # verbose flag: False = level 1 (info), True = level 2 (debug)
    log_level = 2 if verbose else 1
    configure_logging(log_level)
    logger.info("AI Video Generator starting")

    # Default prompts to ./.src/video_prompts.json if it exists
    if prompts is None:
        default_prompts = Path("./.src/video_prompts.json")
        if default_prompts.exists():
            prompts = default_prompts
            logger.info("Using default prompts file: %s", prompts)
    
    # Auto-enable image generation if prompts JSON is provided
    img_gen = prompts is not None
    
    generated_images: list[Path] = []
    if img_gen:
        # Resolve image provider configuration: explicit --img-provider overrides preset
        from .preset_config import load_image_preset, get_default_model_for_provider
        
        resolved_img_model = None
        if img_provider:
            # Explicit provider overrides preset
            resolved_img_provider = img_provider
            resolved_img_model = img_model or get_default_model_for_provider(img_provider)
            img_size = os.getenv("OPENAI_IMAGE_SIZE", "1024x1024")
            logger.info("Using explicit image provider: %s, model: %s (overrides preset)", img_provider, resolved_img_model)
        else:
            # Use preset configuration
            try:
                preset_config = load_image_preset(img_preset)
                resolved_img_provider = preset_config.provider
                resolved_img_model = img_model or preset_config.model
                img_size = preset_config.size
                logger.info("Using image preset: %s (provider=%s, model=%s, size=%s)", img_preset, resolved_img_provider, resolved_img_model, img_size)
            except ValueError as e:
                typer.echo(f"[ERROR] {e}", err=True)
                raise typer.Exit(code=2)
        
        # validate JSON and load prompts
        prompt_file = load_prompts(prompts)
        if dry_run:
            # Simulate generated images without external calls
            typer.echo(f"Image generation enabled; preset={img_preset}; provider={resolved_img_provider}; concurrency={img_concurrency}")
            simulated: list[Path] = []
            for clip in prompt_file.clips:
                filename = clip.target_filename or f"{clip.index:03d}__{clip.code}.png"
                simulated.append(img_out / filename)
            generated_images = simulated
        else:
            # choose provider (lazy import to avoid slow startup)
            if resolved_img_provider == "openai":
                from .image_gen.openai import OpenAIImageProvider
                iprov = OpenAIImageProvider(model=resolved_img_model) if resolved_img_model else OpenAIImageProvider()
            elif resolved_img_provider == "google":
                from .image_gen.google import GoogleImageProvider
                iprov = GoogleImageProvider(model_name=resolved_img_model) if resolved_img_model else GoogleImageProvider()
            elif resolved_img_provider == "gemini":
                from .image_gen.gemini import GeminiImageProvider
                iprov = GeminiImageProvider(model_name=resolved_img_model) if resolved_img_model else GeminiImageProvider()
            elif resolved_img_provider == "gemini-pro":
                from .image_gen.gemini_pro import GeminiProImageProvider
                iprov = GeminiProImageProvider(model_name=resolved_img_model) if resolved_img_model else GeminiProImageProvider()
            else:
                typer.echo(f"Unknown image provider: {resolved_img_provider}", err=True)
                raise typer.Exit(code=2)
            # generate images with grouped scheduling: sequential within group, concurrent across groups
            skip_existing = not force_regen
            results = generate_grouped_images(
                iprov,
                prompt_file.clips,
                img_out,
                size=img_size,
                seed=seed,
                skip_existing=skip_existing,
                max_concurrent_groups=img_concurrency,
            )
            generated_images = [r.path for r in results]

    scanned_images = discover_images(src)

    if img_gen:
        if pair_source == "prompts-only":
            images = generated_images
        elif pair_source == "existing":
            images = scanned_images
        elif pair_source == "all":
            # merge unique preserving order: generated first in prompt order, then new from scan
            seen = set()
            images = []
            for p in generated_images + scanned_images:
                sp = str(p)
                if sp not in seen:
                    images.append(p)
                    seen.add(sp)
        else:
            typer.echo(f"Unknown --pair-source: {pair_source}", err=True)
            raise typer.Exit(code=2)
    else:
        images = scanned_images
    if not images:
        typer.echo("No supported images found in src directory", err=True)
        raise typer.Exit(code=2)

    # Import VideoPair for video generation
    from .core_pairs import consecutive_video_pairs, video_pairs_from_prompts
    
    # Get video prompts from prompt file if available
    video_prompts_dict = prompt_file.video_prompts if img_gen else {}
    
    # Create video pairs - use explicit prompts if available, otherwise consecutive
    if video_prompts_dict:
        video_pairs = video_pairs_from_prompts(images, video_prompts_dict)
        logger.info("Using %d video transitions from prompts JSON", len(video_pairs))
    else:
        video_pairs = consecutive_video_pairs(images, video_prompts_dict)
    
    # Apply limit if specified
    if limit is not None and limit < len(video_pairs):
        video_pairs = video_pairs[:limit]
        logger.info("Limited to first %d videos (--limit %d)", len(video_pairs), limit)
    
    if images_only:
        typer.echo("Images generated; skipping video generation (--images-only)")
        raise typer.Exit(code=0)
    if not video_pairs:
        if dry_run:
            typer.echo("No pairs to generate; dry-run exit")
            raise typer.Exit(code=0)
        typer.echo("Need at least 2 images to create transitions", err=True)
        raise typer.Exit(code=2)

    typer.echo(f"Discovered {len(images)} images in natural order:")
    for p in images:
        typer.echo(f" - {p.name}")
    typer.echo(f"Planned {len(video_pairs)} pairs{f' (limited to first {limit})' if limit else ''}")
    
    # Show which pairs have custom video prompts
    custom_prompt_count = sum(1 for vp in video_pairs if vp.video_prompt)
    if custom_prompt_count > 0:
        typer.echo(f" - {custom_prompt_count} pairs with custom video prompts")

    if dry_run:
        typer.echo("Dry-run requested; exiting without generating outputs")
        raise typer.Exit(code=0)

    # Resolve video provider configuration: explicit --provider overrides preset
    from .preset_config import load_video_preset
    
    if provider:
        # Explicit provider overrides preset
        resolved_provider = provider
        resolved_duration = duration if duration is not None else 5.0
        logger.info("Using explicit video provider: %s (overrides preset)", provider)
    else:
        # Use preset configuration
        try:
            video_preset_config = load_video_preset(video_preset)
            resolved_provider = video_preset_config.provider
            resolved_duration = duration if duration is not None else video_preset_config.duration
            logger.info("Using video preset: %s (provider=%s, duration=%.1fs)", video_preset, resolved_provider, resolved_duration)
        except ValueError as e:
            typer.echo(f"[ERROR] {e}", err=True)
            raise typer.Exit(code=2)

    # Lazy import video providers to avoid slow startup (VEOProvider imports google-cloud-sdk)
    if resolved_provider == "veo":
        from .providers.veo import VEOProvider
        prov = VEOProvider()
    elif resolved_provider == "mock":
        from .providers.mock import MockVideoProvider
        prov = MockVideoProvider()
    else:
        typer.echo(f"Unknown provider: {resolved_provider}", err=True)
        raise typer.Exit(code=2)

    def provider_generate(a: Path, b: Path, dur: float, out_path: Path, video_prompt: str | None = None) -> None:
        prov.generate_transition(a, b, dur, out_path, video_prompt=video_prompt)

    # Convert VideoPairs back to tuples for run_jobs (with prompts stored separately)
    legacy_pairs = [(vp.start_image, vp.end_image) for vp in video_pairs]
    video_prompts_by_pair = {(vp.start_image, vp.end_image): vp.video_prompt for vp in video_pairs}
    
    outputs = run_jobs(
        pairs=legacy_pairs,
        out_dir=out,
        provider_generate=provider_generate,
        duration_s=resolved_duration,
        video_prompts=video_prompts_by_pair,
    )

    any_failed = any(o.status != "success" for o in outputs)
    write_manifest(
        out_dir=out,
        inputs=images,
        pairs=legacy_pairs,
        outputs=outputs,
        provider=resolved_provider,
        params={
            "duration": resolved_duration,
            "video_preset": video_preset if not provider else None,
            # no concurrency
        },
    )

    if any_failed:
        typer.echo("One or more pairs failed; exiting with non-zero code", err=True)
        raise typer.Exit(code=1)
    else:
        typer.echo("All pairs generated successfully")
        raise typer.Exit(code=0)


if __name__ == "__main__":
    app()


