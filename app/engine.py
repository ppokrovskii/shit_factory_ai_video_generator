from __future__ import annotations

import time
from dataclasses import dataclass
from pathlib import Path
from typing import List, Tuple, Callable, Optional

from .logging_conf import get_logger
from .manifest import OutputRecord


logger = get_logger(__name__)


@dataclass
class Job:
    index: int
    start: Path
    end: Path
    out_path: Path


def build_output_name(idx: int, start: Path, end: Path) -> str:
    return f"{idx:03d}__{start.stem}__to__{end.stem}.mp4"


def run_jobs(
    pairs: List[Tuple[Path, Path]],
    out_dir: Path,
    provider_generate: Callable[[Path, Path, float, Path, str | None], None],
    *,
    duration_s: float,
    retries: int = 2,
    video_prompts: dict[Tuple[Path, Path], str | None] | None = None,
) -> List[OutputRecord]:
    out_dir.mkdir(parents=True, exist_ok=True)

    jobs: List[Job] = []
    for i, (a, b) in enumerate(pairs):
        jobs.append(Job(index=i, start=a, end=b, out_path=out_dir / build_output_name(i, a, b)))

    results: List[Optional[OutputRecord]] = [None] * len(jobs)

    def task(job: Job) -> OutputRecord:
        # Get video prompt for this specific pair
        video_prompt = None
        if video_prompts:
            video_prompt = video_prompts.get((job.start, job.end))
        
        attempt = 0
        while True:
            try:
                provider_generate(job.start, job.end, duration_s, job.out_path, video_prompt)
                return OutputRecord(
                    pair_index=job.index,
                    start=str(job.start),
                    end=str(job.end),
                    status="success",
                    path=str(job.out_path),
                    error=None,
                )
            except Exception as exc:  # noqa: BLE001
                attempt += 1
                if attempt > retries:
                    return OutputRecord(
                        pair_index=job.index,
                        start=str(job.start),
                        end=str(job.end),
                        status="failed",
                        path=None,
                        error=str(exc),
                    )
                sleep_s = min(4.0, 0.5 * (2 ** (attempt - 1)))
                logger.warning("Job %s failed (attempt %s/%s): %s; retrying in %.1fs", job.index, attempt, retries, exc, sleep_s)
                time.sleep(sleep_s)

    # Run sequentially to simplify resource control and determinism
    for job in jobs:
        try:
            result = task(job)
            results[job.index] = result
        except Exception as exc:  # noqa: BLE001
            results[job.index] = OutputRecord(
                pair_index=job.index,
                start=str(job.start),
                end=str(job.end),
                status="failed",
                path=None,
                error=str(exc),
            )

    # type: ignore[arg-type]
    return list(results)  # filled in index order


