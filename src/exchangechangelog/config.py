from __future__ import annotations

from pathlib import Path

from loguru import logger
from pydantic import BaseModel

from .utils import load_yaml


def load_config(f: str | Path) -> Config:
    logger.info("Loading config from {}", f)

    data = load_yaml(f)
    return Config.model_validate(data)


class Document(BaseModel):
    name: str
    url: str


class Config(BaseModel):
    docs: list[Document] = []
    num_days: int = 14
    trim_len: int = 20000
    slack_channel: str | None = None
    prompt: str = ""
