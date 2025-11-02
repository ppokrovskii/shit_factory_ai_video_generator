from __future__ import annotations

from pathlib import Path

from .base import Provider


class MockVideoProvider:
    def generate_transition(
        self,
        start_path: Path,
        end_path: Path,
        duration_s: float,
        out_path: Path,
        *,
        fps: int = 24,
        video_prompt: str | None = None,
    ) -> None:
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_bytes(b"MOCKMP4")


