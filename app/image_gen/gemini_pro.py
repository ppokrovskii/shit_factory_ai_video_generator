"""Gemini 3 Pro Image Provider (Nano Banana Pro).

This module provides high-quality image generation using Google's Gemini 3 Pro
image model, which supports up to 4K resolution and advanced "thinking" mode
for better composition.

Model: gemini-3-pro-image-preview
Features:
- Up to 4K resolution (1K/2K/4K configurable)
- Professional quality
- Multi-image fusion with consistency
- Conversational editing
- "Thinking" mode for complex compositions

Reference: https://ai.google.dev/gemini-api/docs/image-generation
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import List

from .base import ImageProvider, ImagePrompt, ImageGenResult
from ..logging_conf import get_logger

logger = get_logger(__name__)


class GeminiProImageProvider:
    """Google Gemini 3 Pro Image provider (Nano Banana Pro).

    Uses the google-generativeai SDK (not Vertex AI).
    
    Requires:
    - GOOGLE_API_KEY (from Google AI Studio)
    
    Features:
    - Professional quality image generation
    - Up to 4K resolution support
    - Multi-image fusion with character consistency
    - Thinking mode for complex compositions
    - Conversational editing
    
    Resolution options:
    - "1K" or "1024x1024" → 1024px square
    - "2K" or "2048x2048" → 2048px square  
    - "4K" or "4096x4096" → 4096px square
    - Standard formats like "1024x768", "16:9" also supported
    """

    def __init__(self, *, model_name: str | None = None) -> None:
        self.api_key = os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise RuntimeError(
                "GOOGLE_API_KEY not set; cannot use Gemini Pro. "
                "Get your key from: https://aistudio.google.com/apikey"
            )
        
        self.model_name = model_name or os.getenv("GEMINI_PRO_IMAGE_MODEL", "gemini-3-pro-image-preview")
        
        # Configure the SDK
        try:
            import google.generativeai as genai
            genai.configure(api_key=self.api_key)
            self.genai = genai
        except ImportError as exc:
            raise RuntimeError(
                "google-generativeai not installed; run: uv add google-generativeai"
            ) from exc

    def _normalize_size(self, size: str) -> str:
        """Normalize size parameter to format Gemini Pro expects.
        
        Args:
            size: Size string like "1K", "2K", "4K", "1024x1024", etc.
            
        Returns:
            Normalized size string for API
        """
        size_upper = size.upper()
        
        # Map shorthand to full resolution
        size_map = {
            "1K": "1024x1024",
            "2K": "2048x2048",
            "4K": "4096x4096",
        }
        
        return size_map.get(size_upper, size)

    def generate_images(
        self,
        prompts: List[ImagePrompt],
        out_dir: Path,
        *,
        size: str = "1024x1024",
        seed: int | None = None,
        skip_existing: bool = True,
    ) -> List[ImageGenResult]:
        """Generate images using Gemini 3 Pro Image.

        Args:
            prompts: List of image generation prompts
            out_dir: Output directory for generated images
            size: Image size (1K, 2K, 4K, or standard format like 1024x1024)
            seed: Random seed (currently not supported by Gemini)
            skip_existing: Skip generation if output file already exists

        Returns:
            List of ImageGenResult with generation status
        """
        out_dir.mkdir(parents=True, exist_ok=True)
        model = self.genai.GenerativeModel(self.model_name)
        results = []
        
        normalized_size = self._normalize_size(size)

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
            
            # If attachment provided, load the reference image
            generation_config = {}
            input_parts = [full_prompt]
            
            if p.attachment:
                from PIL import Image
                attachment_path = out_dir / p.attachment
                if attachment_path.exists():
                    try:
                        # Load reference image
                        ref_image = Image.open(attachment_path)
                        input_parts.insert(0, ref_image)  # Add image before prompt
                        logger.info(
                            "img-gen start | idx=%d code=%s file=%s model=%s size=%s (with reference: %s)",
                            p.index,
                            p.code,
                            filename,
                            self.model_name,
                            normalized_size,
                            p.attachment,
                        )
                    except Exception as e:
                        logger.warning(
                            "img-gen start | idx=%d code=%s file=%s model=%s size=%s (failed to load reference %s: %s, generating without)",
                            p.index,
                            p.code,
                            filename,
                            self.model_name,
                            normalized_size,
                            p.attachment,
                            str(e),
                        )
                else:
                    logger.warning(
                        "img-gen start | idx=%d code=%s file=%s model=%s size=%s (reference %s not found, generating without)",
                        p.index,
                        p.code,
                        filename,
                        self.model_name,
                        normalized_size,
                        p.attachment,
                    )
            else:
                logger.info(
                    "img-gen start | idx=%d code=%s file=%s model=%s size=%s",
                    p.index,
                    p.code,
                    filename,
                    self.model_name,
                    normalized_size,
                )

            try:
                # Generate content with Gemini Pro
                response = model.generate_content(input_parts)
                
                # Extract image from response
                image_saved = False
                for candidate in response.candidates:
                    for part in candidate.content.parts:
                        if part.inline_data is not None:
                            # Save the image directly from bytes
                            image_data = part.inline_data.data
                            
                            # Check if we got valid image data
                            if not image_data or len(image_data) == 0:
                                logger.error(
                                    "img-gen error | idx=%d code=%s error=Empty image data received from API",
                                    p.index,
                                    p.code,
                                )
                                continue
                            
                            out_path.write_bytes(image_data)
                            
                            file_size_kb = out_path.stat().st_size / 1024
                            
                            # Verify file was written correctly
                            if file_size_kb < 1.0:
                                logger.error(
                                    "img-gen error | idx=%d code=%s error=Generated file too small (%.1fKB), likely corrupted",
                                    p.index,
                                    p.code,
                                    file_size_kb,
                                )
                                out_path.unlink(missing_ok=True)  # Delete corrupted file
                                continue
                            
                            logger.info(
                                "img-gen done  | idx=%d code=%s file=%s size=%.1fKB resolution=%s",
                                p.index,
                                p.code,
                                filename,
                                file_size_kb,
                                normalized_size,
                            )
                            results.append(ImageGenResult(prompt=p, path=out_path))
                            image_saved = True
                            break
                    if image_saved:
                        break
                
                if not image_saved:
                    # Log more details about why generation failed
                    error_msg = "No image data in response"
                    if hasattr(response, 'prompt_feedback'):
                        error_msg += f" | prompt_feedback={response.prompt_feedback}"
                    if hasattr(response, 'candidates') and response.candidates:
                        for cand in response.candidates:
                            if hasattr(cand, 'finish_reason'):
                                error_msg += f" | finish_reason={cand.finish_reason}"
                            if hasattr(cand, 'safety_ratings'):
                                error_msg += f" | safety_ratings={cand.safety_ratings}"
                    
                    logger.error(
                        "img-gen error | idx=%d code=%s error=%s",
                        p.index,
                        p.code,
                        error_msg,
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

