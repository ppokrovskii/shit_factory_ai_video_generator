from __future__ import annotations

import os
from pathlib import Path
from typing import List

from .base import ImageProvider, ImagePrompt, ImageGenResult
from ..logging_conf import get_logger

logger = get_logger(__name__)


class ImagenImageProvider:
    """Google Imagen 4 image provider via Gemini API.

    Uses the google-generativeai SDK (not Vertex AI).
    
    Requires:
    - GOOGLE_API_KEY (from Google AI Studio)
    
    Features:
    - High-fidelity image generation
    - SynthID watermarking
    - 1K and 2K resolution support
    
    Reference: https://ai.google.dev/gemini-api/docs/imagen
    """

    def __init__(self, *, model_name: str | None = None) -> None:
        self.api_key = os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise RuntimeError(
                "GOOGLE_API_KEY not set; cannot use Imagen. "
                "Get your key from: https://aistudio.google.com/apikey"
            )
        
        # Default to Imagen 4 standard model
        self.model_name = model_name or os.getenv("IMAGEN_MODEL", "imagen-4.0-generate-001")
        
        # Configure the SDK
        try:
            from google import genai
            self.client = genai.Client(api_key=self.api_key)
        except ImportError as exc:
            raise RuntimeError(
                "google-generativeai not installed; run: uv add google-generativeai"
            ) from exc

    def generate_images(
        self,
        prompts: List[ImagePrompt],
        out_dir: Path,
        *,
        size: str = "1024x1024",
        seed: int | None = None,
        skip_existing: bool = True,
    ) -> List[ImageGenResult]:
        """Generate images using Imagen 4.

        Args:
            prompts: List of image generation prompts
            out_dir: Output directory for generated images
            size: Image size - supports 1K (1024x1024) and 2K (2048x2048)
            seed: Random seed (currently not supported by Imagen)
            skip_existing: Skip generation if output file already exists

        Returns:
            List of ImageGenResult with generation status
        """
        from google.genai import types
        
        out_dir.mkdir(parents=True, exist_ok=True)
        results = []

        # Parse size for Imagen config
        # Imagen 4 supports 1K and 2K for Standard/Ultra models
        image_size = None
        if "2048" in size or "2K" in size.upper():
            image_size = "2K"
        elif "1024" in size or "1K" in size.upper():
            image_size = "1K"
        
        # Parse aspect ratio
        aspect_ratio = "1:1"  # default
        if "x" in size.lower():
            parts = size.lower().split("x")
            try:
                width = int(parts[0])
                height = int(parts[1])
                from math import gcd
                aspect_gcd = gcd(width, height)
                aspect_ratio = f"{width // aspect_gcd}:{height // aspect_gcd}"
            except (ValueError, IndexError):
                pass

        for p in prompts:
            filename = p.target_filename or f"{p.index:03d}__{p.code}.png"
            out_path = out_dir / filename

            if skip_existing and out_path.exists():
                logger.info(
                    "img-gen skip  | idx=%d code=%s file=%s (exists)",
                    p.index,
                    p.code,
                    filename,
                )
                results.append(ImageGenResult(prompt=p, path=out_path))
                continue

            # Build prompt with negative prompt if provided
            full_prompt = p.positive_prompt
            if p.negative_prompt:
                full_prompt += f" [Avoid: {p.negative_prompt}]"
            
            logger.info(
                "img-gen start | idx=%d code=%s file=%s model=%s size=%s aspect=%s",
                p.index,
                p.code,
                filename,
                self.model_name,
                image_size or "default",
                aspect_ratio,
            )

            try:
                # Configure generation
                config_params = {
                    "number_of_images": 1,
                    "aspect_ratio": aspect_ratio,
                }
                
                # Add image size only for Standard/Ultra models (not Fast)
                if image_size and ("ultra" in self.model_name.lower() or self.model_name.endswith("generate-001")):
                    # Fast model doesn't support image_size parameter
                    if "fast" not in self.model_name.lower():
                        config_params["image_size"] = image_size
                
                config = types.GenerateImagesConfig(**config_params)
                
                # Generate image
                response = self.client.models.generate_images(
                    model=self.model_name,
                    prompt=full_prompt,
                    config=config,
                )
                
                # Debug: Check response structure
                logger.debug("Response type: %s, has generated_images: %s", 
                           type(response), hasattr(response, 'generated_images'))
                
                if hasattr(response, 'generated_images'):
                    logger.debug("generated_images count: %d", len(response.generated_images) if response.generated_images else 0)
                    if response.generated_images:
                        for idx, gen_img in enumerate(response.generated_images):
                            logger.debug("Image %d: type=%s, has image=%s", 
                                       idx, type(gen_img), hasattr(gen_img, 'image'))
                            if hasattr(gen_img, 'image'):
                                logger.debug("Image %d image attrs: %s", idx, dir(gen_img.image))
                
                # Save first generated image
                image_saved = False
                if hasattr(response, 'generated_images') and response.generated_images:
                    for generated_image in response.generated_images:
                        if hasattr(generated_image, 'image') and generated_image.image:
                            # Try different attribute names
                            image_bytes = None
                            if hasattr(generated_image.image, 'image_bytes'):
                                image_bytes = generated_image.image.image_bytes
                            elif hasattr(generated_image.image, '_image_bytes'):
                                image_bytes = generated_image.image._image_bytes
                            elif hasattr(generated_image.image, 'data'):
                                image_bytes = generated_image.image.data
                            else:
                                logger.error("No image_bytes/data attribute found. Available: %s", 
                                           dir(generated_image.image))
                                continue
                            
                            if not image_bytes or len(image_bytes) == 0:
                                logger.error(
                                    "img-gen error | idx=%d code=%s error=Empty image data received",
                                    p.index,
                                    p.code,
                                )
                                continue
                            
                            out_path.write_bytes(image_bytes)
                            file_size_kb = out_path.stat().st_size / 1024
                            
                            logger.info(
                                "img-gen done  | idx=%d code=%s file=%s size=%.1fKB",
                                p.index,
                                p.code,
                                filename,
                                file_size_kb,
                            )
                            results.append(ImageGenResult(prompt=p, path=out_path))
                            image_saved = True
                            break
                
                if not image_saved:
                    logger.error(
                        "img-gen error | idx=%d code=%s error=No images in response or failed to extract image bytes",
                        p.index,
                        p.code,
                    )
                    results.append(ImageGenResult(prompt=p, path=out_path))
                    
            except Exception as exc:
                logger.error(
                    "img-gen error | idx=%d code=%s error=%s",
                    p.index,
                    p.code,
                    str(exc),
                )
                results.append(ImageGenResult(prompt=p, path=out_path))

        return results

