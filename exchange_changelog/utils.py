from pathlib import Path

import yaml


def load_yaml(f: str | Path) -> dict:
    with open(f) as fp:
        return yaml.safe_load(fp)
