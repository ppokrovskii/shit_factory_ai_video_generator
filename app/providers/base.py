from __future__ import annotations

from pathlib import Path
from typing import Protocol


class Provider(Protocol):
    def generate_transition(
        self,
        start_path: Path,
        end_path: Path,
        duration_s: float,
        out_path: Path,
        *,
        fps: int = 24,
    ) -> None:
        """Generate a transition video from start_path to end_path.

        Implementations must write an MP4 file to out_path or raise on failure.
        """


