#!/usr/bin/env python3
"""Launch web dashboard — use `regime-dashboard` after pip install."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

APP = Path(__file__).parent / "src" / "regime_engine" / "dashboard_app.py"

if __name__ == "__main__":
    raise SystemExit(
        subprocess.call([sys.executable, "-m", "streamlit", "run", str(APP)])
    )
