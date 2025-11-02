from __future__ import annotations

from pathlib import Path
from typing import List

from .base import ImageProvider, ImagePrompt, ImageGenResult


class MockImageProvider:
    def generate_images(
        self,
        prompts: List[ImagePrompt],
        out_dir: Path,
        *,
        size: str = "1024x1024",
        seed: int | None = None,
        skip_existing: bool = True,
    ) -> List[ImageGenResult]:
        out_dir.mkdir(parents=True, exist_ok=True)
        results: List[ImageGenResult] = []
        for p in prompts:
            filename = p.target_filename or f"{p.index:03d}__{p.code}.png"
            path = out_dir / filename
            if skip_existing and path.exists():
                results.append(ImageGenResult(prompt=p, path=path))
                continue
            # write tiny PNG header-like bytes (not a valid image, but adequate for tests)
            path.write_bytes(b"MOCKPNG")
            results.append(ImageGenResult(prompt=p, path=path))
        return results


