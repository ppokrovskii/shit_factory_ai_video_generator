from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List, Protocol


@dataclass()
class ImagePrompt:
    index: int
    code: str
    positive_prompt: str
    negative_prompt: str | None = None
    target_filename: str | None = None
    attachment: str | None = None
    # Optional logical group identifier. Prompts sharing the same group must be
    # generated sequentially, often using the previous image as attachment.
    group: str | None = None


@dataclass(frozen=True)
class ImageGenResult:
    prompt: ImagePrompt
    path: Path


class ImageProvider(Protocol):
    def generate_images(
        self,
        prompts: List[ImagePrompt],
        out_dir: Path,
        *,
        size: str = "1024x1024",
        seed: int | None = None,
        skip_existing: bool = True,
    ) -> List[ImageGenResult]:
        """Generate one image per prompt, writing files to out_dir and returning the paths."""


