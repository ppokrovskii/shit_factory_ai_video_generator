from __future__ import annotations

import base64
import os
from pathlib import Path
from typing import List

import requests

from .base import ImageProvider, ImagePrompt, ImageGenResult
from ..logging_conf import get_logger

logger = get_logger(__name__)


class OpenAIImageProvider:
    """Generate images via OpenAI Images API (DALL·E/Images.generate).

    Requires OPENAI_API_KEY in env. Writes PNG files to out_dir.
    """

    def __init__(self, *, model: str | None = None) -> None:
        # Allow override via env: OPENAI_IMAGE_MODEL
        # gpt-image-1-mini is cheapest (~80% less than gpt-image-1), ideal for dev
        # Options: gpt-image-1-mini (cheapest) | dall-e-2 | dall-e-3 | gpt-image-1 (highest quality)
        self.model = (model or os.getenv("OPENAI_IMAGE_MODEL") or "gpt-image-1-mini").lower()

    def generate_images(
        self,
        prompts: List[ImagePrompt],
        out_dir: Path,
        *,
        size: str = "1024x1024",
        seed: int | None = None,
        skip_existing: bool = True,
    ) -> List[ImageGenResult]:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY not set")

        out_dir.mkdir(parents=True, exist_ok=True)

        results: List[ImageGenResult] = [None] * len(prompts)  # type: ignore

        def task(prompt: ImagePrompt, skip_if_exists: bool = True) -> ImageGenResult | None:
            # Check if image already exists
            filename = prompt.target_filename or f"{prompt.index:03d}__{prompt.code}.png"
            out_path = out_dir / filename
            if skip_if_exists and out_path.exists():
                logger.info(
                    "img-gen skip  | code=%s target=%s (already exists)",
                    prompt.code,
                    filename,
                )
                return ImageGenResult(prompt=prompt, path=out_path)
            
            # Compose full prompt
            # Prompts are self-contained with detailed descriptions including any continuity
            full_prompt = prompt.positive_prompt
            if prompt.negative_prompt:
                full_prompt += f"\nNegative prompt: {prompt.negative_prompt}"

            body = {
                "model": self.model,
                "prompt": full_prompt,
                "size": size,
                **({"seed": seed} if seed is not None else {}),
            }
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            }
            org = os.getenv("OPENAI_ORG") or os.getenv("OPENAI_ORG_ID")
            project = os.getenv("OPENAI_PROJECT") or os.getenv("OPENAI_PROJECT_ID")
            if org:
                headers["OpenAI-Organization"] = org
            if project:
                headers["OpenAI-Project"] = project

            logger.info(
                "img-gen start | code=%s target=%s size=%s",
                prompt.code,
                filename,
                size,
            )
            r = requests.post(
                "https://api.openai.com/v1/images/generations",
                json=body,
                headers=headers,
                timeout=60,
            )
            try:
                r.raise_for_status()
            except requests.HTTPError as http_err:  # enrich error with body
                snippet = ""
                try:
                    snippet = ": " + r.text[:200]
                except Exception:
                    pass
                raise requests.HTTPError(str(http_err) + snippet) from http_err
            data = r.json()
            # Handle both base64 and URL responses
            try:
                if "b64_json" in data["data"][0]:
                    # Base64 response (typical for generations)
                    image_b64 = data["data"][0]["b64_json"]
                    img_bytes = base64.b64decode(image_b64)
                elif "url" in data["data"][0]:
                    # URL response (typical for variations)
                    image_url = data["data"][0]["url"]
                    img_response = requests.get(image_url, timeout=60)
                    img_response.raise_for_status()
                    img_bytes = img_response.content
                else:
                    raise RuntimeError(f"Response contains neither b64_json nor url: {data}")
            except Exception as exc:  # noqa: BLE001
                raise RuntimeError(f"Unexpected OpenAI response: {data}") from exc
            out_path.write_bytes(img_bytes)
            logger.info(
                "img-gen done   | code=%s wrote=%s",
                prompt.code,
                str(out_path),
            )
            return ImageGenResult(prompt=prompt, path=out_path)

        # Sequential processing: generate images in order
        # Prompts are self-contained, no dependencies between images
        for p in prompts:
            res = task(p, skip_if_exists=skip_existing)
            if res is not None:
                results[p.index] = res

        # type: ignore[return-value]
        return results


