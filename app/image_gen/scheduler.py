from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Dict, List, Tuple

from .base import ImageProvider, ImagePrompt, ImageGenResult
from ..logging_conf import get_logger


logger = get_logger(__name__)


def _group_prompts(prompts: List[ImagePrompt]) -> Dict[str, List[ImagePrompt]]:
    groups: Dict[str, List[ImagePrompt]] = {}
    for p in prompts:
        gid = p.group if p.group else f"single__{p.index}"
        groups.setdefault(gid, []).append(p)
    # Ensure in-order processing within each group
    for gid, items in groups.items():
        items.sort(key=lambda x: x.index)
    return groups


def _process_group(
    provider: ImageProvider,
    gid: str,
    items: List[ImagePrompt],
    out_dir: Path,
    *,
    size: str,
    seed: int | None,
    skip_existing: bool,
) -> List[ImageGenResult]:
    logger.info("img-gen group start | group=%s count=%d", gid, len(items))
    group_results: List[ImageGenResult] = []
    prev_result: ImageGenResult | None = None
    for prompt in items:
        # Chain previous output as attachment when not explicitly provided
        if prompt.attachment is None and prev_result is not None:
            prompt.attachment = prev_result.path.name
        res = provider.generate_images([prompt], out_dir, size=size, seed=seed, skip_existing=skip_existing)
        if not res or len(res) != 1:
            raise RuntimeError("Provider must return exactly one result per single prompt call")
        prev_result = res[0]
        group_results.append(prev_result)
    logger.info("img-gen group done  | group=%s", gid)
    return group_results


def generate_grouped_images(
    provider: ImageProvider,
    prompts: List[ImagePrompt],
    out_dir: Path,
    *,
    size: str = "1024x1024",
    seed: int | None = None,
    skip_existing: bool = True,
    max_concurrent_groups: int = 2,
) -> List[ImageGenResult]:
    """Generate images with per-group sequential ordering and cross-group concurrency.

    Prompts sharing the same `group` are processed strictly in index order, with
    each prompt optionally using the previous group's output as `attachment` when
    not explicitly provided. Independent groups are processed concurrently up to
    `max_concurrent_groups`.
    """

    grouped = _group_prompts(prompts)
    # Pre-size results to original length to preserve order by prompt.index
    results: List[ImageGenResult | None] = [None] * len(prompts)

    with ThreadPoolExecutor(max_workers=max_concurrent_groups) as executor:
        futures = {
            executor.submit(
                _process_group,
                provider,
                gid,
                items,
                out_dir,
                size=size,
                seed=seed,
                skip_existing=skip_existing,
            ): (gid, items)
            for gid, items in grouped.items()
        }
        for fut in as_completed(futures):
            gid, items = futures[fut]
            group_results = fut.result()
            # Map results back to their indices
            for r in group_results:
                results[r.prompt.index] = r

    # type: ignore[return-value]
    return results




