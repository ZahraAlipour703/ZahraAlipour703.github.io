#!/usr/bin/env python3
"""
Entry point for running the cube tracking application.

Usage:
    python scripts/run_tracking.py
"""

import sys
from pathlib import Path

# Allow running directly from a source checkout without installing the package.
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from cube_tracking.app import main  # noqa: E402

if __name__ == "__main__":
    main()
