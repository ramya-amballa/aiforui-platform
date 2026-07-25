"""
Runs an existing AOS runtime script as its own subprocess, exactly the
way AOS/orchestrator/orchestrator.py's own run_attempt() invokes every
employee: `python3 <script>`, run from the script's own directory,
stdout/stderr captured, never imported in-process. The dashboard never
duplicates or re-executes any employee's business logic — it only
shells out to the same entry point a human would run by hand, and
displays whatever that script already writes to disk.
"""

import subprocess
import sys
import time
from dataclasses import dataclass

from utils.paths import aos_path


@dataclass
class RunResult:
    ok: bool
    returncode: int | None
    stdout: str
    stderr: str
    duration_seconds: float
    timed_out: bool = False


def run_script(script_relpath: str, cwd_relpath: str, timeout_seconds: int = 300) -> RunResult:
    script_path = aos_path(script_relpath)
    cwd_path = aos_path(cwd_relpath)

    if not script_path.exists():
        return RunResult(ok=False, returncode=None, stdout="", stderr=f"Script not found: {script_path}",
                          duration_seconds=0.0)

    started = time.monotonic()
    try:
        result = subprocess.run(
            [sys.executable, str(script_path)],
            cwd=str(cwd_path),
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
        )
        duration = round(time.monotonic() - started, 2)
        return RunResult(
            ok=result.returncode == 0,
            returncode=result.returncode,
            stdout=result.stdout or "",
            stderr=result.stderr or "",
            duration_seconds=duration,
        )
    except subprocess.TimeoutExpired as exc:
        duration = round(time.monotonic() - started, 2)
        return RunResult(
            ok=False, returncode=None,
            stdout=(exc.stdout or "") if isinstance(exc.stdout, str) else "",
            stderr=f"Timed out after {timeout_seconds}s",
            duration_seconds=duration, timed_out=True,
        )
