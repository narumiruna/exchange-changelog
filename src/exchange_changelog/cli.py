from typing import Annotated

import typer
from dotenv import find_dotenv
from dotenv import load_dotenv

from .app import App
from .config import load_config
from .utils import configure_langfuse


def run(
    config_file: Annotated[str, typer.Option("-c", "--config-file", help="config file")] = "config/default.yaml",
    output_file: Annotated[str, typer.Option("-o", "--output-file", help="output file")] = "changelog.md",
) -> None:
    load_dotenv(find_dotenv())
    configure_langfuse()

    config = load_config(config_file)
    app = App(config=config, output_file=output_file)
    app.run()


def main() -> None:
    typer.run(run)
