"""Isolate native Aer execution from Streamlit's background script thread."""

import json
import os
import subprocess
import sys
from pathlib import Path


def execute(config):
    from dataclasses import asdict

    result = subprocess.run(
        [sys.executable, "-m", "quantum.worker"],
        input=json.dumps(asdict(config)),
        text=True,
        capture_output=True,
        cwd=Path(__file__).resolve().parents[1],
        timeout=120,
        env={**os.environ, "OMP_NUM_THREADS": "1"},
    )
    if result.returncode:
        raise RuntimeError(
            f"Aer worker failed (exit {result.returncode}): {result.stderr[-2000:]}"
        )
    return json.loads(result.stdout)


if __name__ == "__main__":
    from quantum.simulator import Config, run

    print(json.dumps(run(Config(**json.load(sys.stdin)))))
