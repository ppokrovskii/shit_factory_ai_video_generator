from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict, Any


@dataclass
class PairRecord:
    start: str
    end: str


@dataclass
class OutputRecord:
    pair_index: int
    start: str
    end: str
    status: str  # "success" | "failed"
    path: Optional[str]
    error: Optional[str]


@dataclass
class Manifest:
    inputs: List[str]
    pairs: List[PairRecord]
    outputs: List[OutputRecord]
    provider: str
    params: Dict[str, Any]
    created_at: str

    def to_json(self) -> str:
        return json.dumps(asdict(self), indent=2)


def write_manifest(
    out_dir: Path,
    inputs: List[Path],
    pairs: List[tuple[Path, Path]],
    outputs: List[OutputRecord],
    provider: str,
    params: Dict[str, Any],
) -> Path:
    manifest = Manifest(
        inputs=[str(p) for p in inputs],
        pairs=[PairRecord(start=str(a), end=str(b)) for a, b in pairs],
        outputs=outputs,
        provider=provider,
        params=params,
        created_at=datetime.utcnow().isoformat() + "Z",
    )
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / "manifest.json"
    path.write_text(manifest.to_json(), encoding="utf-8")
    return path


