from __future__ import annotations

from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
CONFIG_DIR = PROJECT_ROOT / "config"
LOGS_DIR = PROJECT_ROOT / "logs"


def initialize_dirs() ->None:
    for directory in [DATA_DIR, CONFIG_DIR, LOGS_DIR]:
        directory.mkdir(parents=True, exist_ok=True)
