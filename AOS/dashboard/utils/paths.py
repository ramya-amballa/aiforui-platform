"""
Central path resolution for the AOS Command Center.

Every other module resolves paths through here rather than building its
own relative paths, so the dashboard can be relocated (or deployed to a
different host) by changing exactly one thing: the AOS_ROOT environment
variable, with a same-checkout fallback for local/dev use.
"""

import os
from pathlib import Path

DASHBOARD_DIR = Path(__file__).resolve().parent.parent

# In production (e.g. a container built from just AOS/dashboard/), set
# AOS_ROOT to point at the AOS/ checkout. Locally, AOS/ is the dashboard's
# own parent directory, so that's the default.
AOS_ROOT = Path(os.environ.get("AOS_ROOT", DASHBOARD_DIR.parent)).resolve()

REPO_ROOT = AOS_ROOT.parent


def aos_path(*parts: str) -> Path:
    """Resolve a path relative to AOS/, e.g. aos_path("orchestrator", "status.json")."""
    return AOS_ROOT.joinpath(*parts)


def dashboard_path(*parts: str) -> Path:
    """Resolve a path relative to AOS/dashboard/ itself."""
    return DASHBOARD_DIR.joinpath(*parts)


def exists(*parts: str) -> bool:
    return aos_path(*parts).exists()
