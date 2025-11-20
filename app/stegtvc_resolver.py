import json
from .config import load_stegtv_config

def stegtvc_resolve(use_case="general", module="unknown", importance="normal"):
    """
    Simple model resolver used by Hybrid-Collab-Bridge.
    """
    cfg = load_stegtv_config()

    # For now: always pick the first provider with highest priority
    provider = sorted(cfg["providers"], key=lambda p: p["priority"])[0]

    return {
        "use_case": use_case,
        "module": module,
        "provider": provider
    }
