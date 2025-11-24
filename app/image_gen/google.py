from __future__ import annotations

import base64
import os
from pathlib import Path
from typing import List

from .base import ImageProvider, ImagePrompt, ImageGenResult
from ..logging_conf import get_logger

logger = get_logger(__name__)


class GoogleImageProvider:
    """Google Vertex AI Imagen 2 image provider.

    Requires ADC (Application Default Credentials) via:
    - gcloud auth application-default login, or
    - GOOGLE_APPLICATION_CREDENTIALS pointing to a service account JSON.

    Also requires:
    - GOOGLE_CLOUD_PROJECT (or gcloud default project)
    - VERTEX_LOCATION (default: us-central1)
    """

    def __init__(self, *, project: str | None = None, location: str | None = None, model_name: str | None = None) -> None:
        self.project = project or os.getenv("GOOGLE_CLOUD_PROJECT")
        self.location = location or os.getenv("VERTEX_LOCATION", "us-central1")
        self.model_name = model_name or os.getenv("VERTEX_IMAGEN_MODEL", "imagen-3.0-generate-001")
        if not self.project:
            raise RuntimeError("GOOGLE_CLOUD_PROJECT not set; cannot use Vertex AI")

    def generate_images(
        self,
        prompts: List[ImagePrompt],
        out_dir: Path,
        *,
        size: str = "1024x1024",
        seed: int | None = None,
        skip_existing: bool = True,
    ) -> List[ImageGenResult]:
        """Generate images using Vertex AI Imagen 2 (imagegeneration@006 model).

        For prompts with `attachment`, we use edit mode (reference image + mask).
        Without attachment, we use text-to-image generation.
        """
        try:
            from vertexai.preview.vision_models import ImageGenerationModel
            import vertexai
        except ImportError as exc:
            raise RuntimeError("google-cloud-aiplatform not installed; run: uv add google-cloud-aiplatform") from exc

        vertexai.init(project=self.project, location=self.location)
        # Load model from environment or constructor parameter
        try:
            model = ImageGenerationModel.from_pretrained(self.model_name)
        except Exception as exc:
            raise RuntimeError(
                f"Failed to load Imagen model '{self.model_name}' in project={self.project}, location={self.location}. "
                f"Ensure Vertex AI is enabled and the model is available in your region. "
                f"Try: gcloud services enable aiplatform.googleapis.com --project {self.project}"
            ) from exc

        out_dir.mkdir(parents=True, exist_ok=True)
        results: List[ImageGenResult] = []

        # Parse size into aspect ratio string
        # Imagen 3.0 supported aspect ratios: 1:1, 3:4, 4:3, 9:16, 16:9
        if "x" in size.lower():
            parts = size.lower().split("x")
            width = int(parts[0])
            height = int(parts[1])
        else:
            width = height = 1024
        
        # Map dimensions to supported Imagen 3.0 aspect ratios
        aspect_ratio_map = {
            (1024, 1024): "1:1",
            (896, 1280): "3:4",
            (1280, 896): "4:3",
            (768, 1408): "9:16",
            (1408, 768): "16:9",
        }
        
        aspect_ratio = aspect_ratio_map.get((width, height))
        if not aspect_ratio:
            # Fallback: try to match by ratio
            from math import gcd
            aspect_gcd = gcd(width, height)
            calculated_ratio = f"{width // aspect_gcd}:{height // aspect_gcd}"
            
            # Check if calculated ratio matches supported ones
            supported_ratios = {"1:1", "3:4", "4:3", "9:16", "16:9"}
            if calculated_ratio in supported_ratios:
                aspect_ratio = calculated_ratio
            else:
                logger.warning(
                    "Unsupported aspect ratio %s (calculated: %s). Falling back to 1:1. "
                    "Supported: 1:1 (1024x1024), 3:4 (896x1280), 4:3 (1280x896), 9:16 (768x1408), 16:9 (1408x768)",
                    f"{width}x{height}", calculated_ratio
                )
                aspect_ratio = "1:1"

        for p in prompts:
            filename = p.target_filename or f"{p.index:03d}__{p.code}.png"
            out_path = out_dir / filename
            if skip_existing and out_path.exists():
                logger.info("img-gen skip  | code=%s target=%s (exists)", p.code, filename)
                results.append(ImageGenResult(prompt=p, path=out_path))
                continue

            logger.info("img-gen start | code=%s target=%s project=%s location=%s", p.code, filename, self.project, self.location)

            # Build prompt and optional reference image
            prompt_text = p.positive_prompt
            if p.negative_prompt:
                prompt_text += f"\nNegative: {p.negative_prompt}"

            generation_params = {
                "prompt": prompt_text,
                "number_of_images": 1,
                "aspect_ratio": aspect_ratio,
            }
            if seed is not None:
                generation_params["seed"] = seed

            # Note: For grouped/sequential images with attachments, we rely on the prompt text to maintain consistency.
            # Vertex AI Imagen's edit_image/variations APIs either don't support prompts or have quality/policy issues.
            # The best approach is to craft prompts that explicitly reference the previous image (e.g., "same character").
            # The attachment field is logged for reference but not used in the API call.
            if p.attachment:
                logger.info("img-gen chained | code=%s (prompt references previous image: %s)", p.code, p.attachment)
            
            # Always use text-to-image generation with detailed prompts
            # Retry on rate limit errors (ResourceExhausted)
            max_retries = 3
            retry_delay = 2  # seconds
            last_error = None
            
            for attempt in range(max_retries):
                try:
                    images = model.generate_images(**generation_params)
                    break  # Success, exit retry loop
                except Exception as e:
                    last_error = e
                    error_str = str(e)
                    # Check if it's a rate limit error
                    if "ResourceExhausted" in error_str or "Quota exceeded" in error_str or "429" in error_str:
                        if attempt < max_retries - 1:
                            import time
                            wait_time = retry_delay * (2 ** attempt)  # Exponential backoff
                            logger.warning(
                                "img-gen retry | code=%s attempt=%d/%d rate_limit_hit, waiting %ds...",
                                p.code, attempt + 1, max_retries, wait_time
                            )
                            time.sleep(wait_time)
                            continue
                    # Not a rate limit error, or we're out of retries
                    raise
            else:
                # All retries exhausted
                raise last_error

            if not images or len(images.images) == 0:
                raise RuntimeError(f"No images returned from Vertex AI for prompt {p.code}")

            # Save first image
            img_bytes = images.images[0]._image_bytes
            out_path.write_bytes(img_bytes)
            logger.info("img-gen done   | code=%s wrote=%s", p.code, str(out_path))
            results.append(ImageGenResult(prompt=p, path=out_path))

        return results


