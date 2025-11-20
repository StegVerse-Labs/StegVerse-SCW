from __future__ import annotations

import datetime as dt
from pathlib import Path
from typing import Optional

from .entity_models import Entity


def append_memory(entity: Entity, heading: str, body: str, *, kind: str = "note") -> None:
    """
    Append a markdown entry to an entity's memory file.
    kind: 'note' | 'run' | 'error' etc.
    """
    path: Path = entity.memory_path
    path.parent.mkdir(parents=True, exist_ok=True)

    ts = dt.datetime.utcnow().isoformat(timespec="seconds") + "Z"

    lines = [
        f"## [{kind.upper()}] {heading}",
        f"- entity: `{entity.id}`",
        f"- when: `{ts}`",
        "",
        body.strip(),
        "",
        "---",
        "",
    ]
    with path.open("a", encoding="utf-8") as f:
        f.write("\n".join(lines))
