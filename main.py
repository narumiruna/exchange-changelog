from pathlib import Path
from typing import Literal

import click
from dotenv import find_dotenv
from dotenv import load_dotenv
from loguru import logger

from exchange_changelog.config import APIDoc
from exchange_changelog.config import Config
from exchange_changelog.config import load_config
from exchange_changelog.loaders import load_html_with_httpx
from exchange_changelog.loaders import load_html_with_singlefile
from exchange_changelog.slack import post_slack_message
from exchange_changelog.tools.changelog import Changelog
from exchange_changelog.tools.changelog import extract_changelog


def load_html(url: str, method: Literal["httpx", "singlefile"]) -> str:
    if method == "singlefile":
        return load_html_with_singlefile(url)
    elif method == "httpx":
        return load_html_with_httpx(url)
    else:
        raise ValueError(f"unknown method: {method}")


def extract_recent_changelog(api_doc: APIDoc, cfg: Config) -> Changelog:
    text = load_html(api_doc.url, api_doc.method)
    logger.info("text length: {}", len(text))

    # trim text
    text = text[: cfg.trim_len]

    try:
        changelog = extract_changelog(text)
    except Exception as e:
        logger.error("unable to extract changelog: {}", e)
        return Changelog(changes=[], upcoming_changes=[])

    # log parsed changes
    for change in changelog.changes:
        logger.info("change: {}", change)

    changelog.select_recent_changes(cfg.num_days)

    return changelog


@click.command()
@click.option("-c", "--config-file", type=click.Path(path_type=Path), default="config/default.yaml", help="config file")
@click.option("-o", "--output-file", type=click.Path(path_type=Path), default="changelog.md", help="output file")
def main(config_file: Path, output_file: Path) -> None:
    load_dotenv(find_dotenv())

    logger.info("loading config file: {}", config_file)
    cfg = load_config(config_file)

    output_string = ""
    for doc in cfg.docs:
        changelog = extract_recent_changelog(doc, cfg)

        if changelog.changes:
            logger.debug("info:\n{}", changelog.pritty_repr(doc.name, doc.url))
            post_slack_message(changelog.pritty_repr(doc.name, doc.url))

        output_string += changelog.pritty_repr(doc.name, doc.url) + "\n\n"

        with output_file.open("w") as f:
            f.write(output_string)


if __name__ == "__main__":
    main()
