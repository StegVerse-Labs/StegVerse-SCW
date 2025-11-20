"""
StegVerse Core Registry (v1.0)

This module provides a central place to describe:
- core modules (SCW, TVC, HCB, Continuity)
- external endpoints (in other repos)
- worker classes and their basic responsibilities

It is intentionally lightweight and importable from any script.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass
class ModuleRef:
    name: str           # e.g. "StegTVC"
    repo: str           # e.g. "StegVerse-Labs/TVC"
    role: str           # short human description
    api_url: Optional[str] = None  # optional HTTP endpoint
    notes: str = ""


@dataclass
class WorkerClass:
    code: str           # e.g. "infra", "builder"
    description: str
    default_priority: int  # 1-10 (10 = highest)


class StegVerseCore:
    """
    Central definition of StegVerse core modules and worker classes.
    This is *declarative*, not an execution engine.
    """

    def __init__(self) -> None:
        self.modules: Dict[str, ModuleRef] = {}
        self.worker_classes: Dict[str, WorkerClass] = {}
        self._init_modules()
        self._init_workers()

    # ------------------------------------------------------------------ #
    # Core module registry
    # ------------------------------------------------------------------ #
    def _init_modules(self) -> None:
        self.register_module(
            ModuleRef(
                name="SCW",
                repo="StegVerse-Labs/StegVerse-SCW",
                role="Self-healing control plane and autopatch hub.",
                notes="This repo. Source of truth for manifests and policies.",
            )
        )
        self.register_module(
            ModuleRef(
                name="TVC",
                repo="StegVerse-Labs/TVC",
                role="Model resolver / router with cost awareness.",
            )
        )
        self.register_module(
            ModuleRef(
                name="TV",
                repo="StegVerse-Labs/TV",
                role="Token vault / identity / permissions (StegTV core).",
            )
        )
        self.register_module(
            ModuleRef(
                name="HCB",
                repo="StegVerse-Labs/hybrid-collab-bridge",
                role="AI workforce gateway. Runs entity jobs.",
            )
        )
        self.register_module(
            ModuleRef(
                name="Continuity",
                repo="StegVerse-Labs/Continuity",
                role="Global timeline + intent + audit logs.",
            )
        )

    def register_module(self, module: ModuleRef) -> None:
        self.modules[module.name] = module

    # ------------------------------------------------------------------ #
    # Worker class registry
    # ------------------------------------------------------------------ #
    def _init_workers(self) -> None:
        self.register_worker(
            WorkerClass(
                code="infra",
                description="Fix workflows, layout, dependencies, and repo health.",
                default_priority=8,
            )
        )
        self.register_worker(
            WorkerClass(
                code="builder",
                description="Build features, modules, docs, and tests.",
                default_priority=7,
            )
        )
        self.register_worker(
            WorkerClass(
                code="compliance",
                description="Apply compliance rules, safeguard data & finance.",
                default_priority=9,
            )
        )
        self.register_worker(
            WorkerClass(
                code="economy",
                description="Handle payments, wallets, ledgers, and fraud signals.",
                default_priority=9,
            )
        )

    def register_worker(self, wc: WorkerClass) -> None:
        self.worker_classes[wc.code] = wc

    # ------------------------------------------------------------------ #
    # Convenience
    # ------------------------------------------------------------------ #
    def list_modules(self) -> List[ModuleRef]:
        return list(self.modules.values())

    def list_worker_classes(self) -> List[WorkerClass]:
        return list(self.worker_classes.values())


# Small helper for scripts
CORE = StegVerseCore()
