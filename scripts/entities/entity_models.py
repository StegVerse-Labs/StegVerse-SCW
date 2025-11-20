from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Dict, Any, Optional

ROOT = Path(__file__).resolve().parents[2]
REGISTRY_PATH = ROOT / "entities" / "registry.json"
PERMISSIONS_DIR = ROOT / "entities" / "permissions"


@dataclass
class PermissionsProfile:
    id: str
    allowed_actions: List[str] = field(default_factory=list)
    forbidden_actions: List[str] = field(default_factory=list)

    @classmethod
    def load(cls, profile_id: str) -> "PermissionsProfile":
        path = PERMISSIONS_DIR / f"{profile_id}.json"
        if not path.exists():
            return cls(id=profile_id, allowed_actions=[], forbidden_actions=[])
        data = json.loads(path.read_text(encoding="utf-8"))
        return cls(
            id=data.get("id", profile_id),
            allowed_actions=data.get("allowed_actions", []),
            forbidden_actions=data.get("forbidden_actions", []),
        )


@dataclass
class Entity:
    id: str
    name: str
    role: str
    enabled: bool
    repos: List[str]
    tasks: List[str]
    memory_file: str
    permissions_profile: str

    permissions: PermissionsProfile = field(init=False)

    def __post_init__(self):
        self.permissions = PermissionsProfile.load(self.permissions_profile)

    @property
    def memory_path(self) -> Path:
        return ROOT / self.memory_file


def load_registry() -> Dict[str, Entity]:
    if not REGISTRY_PATH.exists():
        raise RuntimeError(f"Entity registry not found at {REGISTRY_PATH}")
    raw = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    ent_dict: Dict[str, Entity] = {}
    for e in raw.get("entities", []):
        entity = Entity(
            id=e["id"],
            name=e["name"],
            role=e["role"],
            enabled=bool(e.get("enabled", True)),
            repos=e.get("repos", []),
            tasks=e.get("tasks", []),
            memory_file=e.get("memory_file", f"memory/entities/{e['id']}.md"),
            permissions_profile=e.get("permissions_profile", "default_worker"),
        )
        ent_dict[entity.id] = entity
    return ent_dict


def get_entity(entity_id: str) -> Entity:
    ents = load_registry()
    if entity_id not in ents:
        raise RuntimeError(f"Entity {entity_id!r} not found in registry.")
    return ents[entity_id]
