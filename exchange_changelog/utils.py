from pathlib import Path

import yaml


def load_yaml(f: str | Path) -> dict:
    with open(f) as fp:
        return yaml.safe_load(fp)


def load_text(f: str | Path) -> str:
    with open(f) as fp:
        return fp.read()


def save_text(text: str, f: str | Path) -> None:
    with open(f, "w") as fp:
        return fp.write(text)
