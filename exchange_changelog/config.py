from __future__ import annotations

from pathlib import Path
from typing import Literal

from pydantic import BaseModel

from .utils import load_yaml


def load_config(f: str | Path) -> Config:
    data = load_yaml(f)
    return Config.model_validate(data)


class APIDoc(BaseModel):
    name: str
    url: str
    method: Literal["httpx", "singlefile", "playwright"]


class Config(BaseModel):
    docs: list[APIDoc] = []
    num_days: int = 14
    trim_len: int = 20000
    slack_channel: str | None = None
