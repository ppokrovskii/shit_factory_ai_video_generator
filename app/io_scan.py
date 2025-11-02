from pathlib import Path
from typing import Iterable, List


SUPPORTED_SUFFIXES = {".png", ".jpg", ".jpeg", ".webp"}


def _natural_key(path: Path) -> List[object]:
    import re

    parts: List[object] = []
    for chunk in re.split(r"(\d+)", path.stem):
        if chunk.isdigit():
            parts.append(int(chunk))
        else:
            parts.append(chunk.lower())
    # include suffix to disambiguate
    parts.append(path.suffix.lower())
    return parts


def discover_images(src_dir: Path) -> List[Path]:
    if not src_dir.exists() or not src_dir.is_dir():
        raise FileNotFoundError(f"Source directory not found: {src_dir}")

    images = [
        p
        for p in src_dir.iterdir()
        if p.is_file() and p.suffix.lower() in SUPPORTED_SUFFIXES
    ]
    images.sort(key=_natural_key)
    return images


