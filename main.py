from pathlib import Path
from typing import Annotated

import typer
from dotenv import find_dotenv
from dotenv import load_dotenv

from exchange_changelog.app import App
from exchange_changelog.config import load_config
from exchange_changelog.utils import configure_langfuse


def main(
    config_file: Annotated[Path, typer.Option("-c", "--config-file", help="config file")] = Path("config/default.yaml"),
    output_file: Annotated[Path, typer.Option("-o", "--output-file", help="output file")] = Path("changelog.md"),
) -> None:
    load_dotenv(find_dotenv())
    configure_langfuse()

    config = load_config(config_file)
    app = App(config=config, output_file=output_file)
    app.run()


if __name__ == "__main__":
    typer.run(main)
