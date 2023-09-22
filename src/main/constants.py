import os
from enum import Enum
from pathlib import Path

ROOT_DIR = Path(os.path.dirname(os.path.realpath(__file__)))


def make_absolute_path(relative_path: str) -> str:
    return os.path.join(ROOT_DIR, relative_path)


class TranslatorMode(str, Enum):
    client = "CLIENT"
    proxy = "PROXY"
