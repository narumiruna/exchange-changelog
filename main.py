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
from exchange_changelog.tools.changelog import ChangelogList
from exchange_changelog.tools.changelog import extract_changelog
from exchange_changelog.tools.changelog import select_recent_changelogs


def load_html(url: str, method: Literal["httpx", "singlefile"]) -> str:
    if method == "singlefile":
        return load_html_with_singlefile(url)
    elif method == "httpx":
        return load_html_with_httpx(url)
    else:
        raise ValueError(f"unknown method: {method}")


def extract_recent_changelog(api_doc: APIDoc, cfg: Config) -> ChangelogList:
    text = load_html(api_doc.url, api_doc.method)
    logger.info("text length: {}", len(text))

    # trim text
    text = text[: cfg.trim_len]

    changelogs = extract_changelog(text)
    if changelogs is None:
        logger.info("no changelogs found for {}", api_doc.name)
        return ""

    # log parsed changelogs
    for changelog in changelogs.items:
        logger.info("changelog: {}", changelog)

    recent_changelogs = select_recent_changelogs(changelogs, cfg.num_days)

    return recent_changelogs


@click.command()
@click.option("-c", "--config-file", type=click.Path(path_type=Path), default="config/default.yaml", help="config file")
@click.option("-o", "--output-file", type=click.Path(path_type=Path), default="changelog.md", help="output file")
def main(config_file: Path, output_file: Path) -> None:
    load_dotenv(find_dotenv())

    logger.info("loading config file: {}", config_file)
    cfg = load_config(config_file)

    output_string = ""
    for doc in cfg.docs:
        changelogs = extract_recent_changelog(doc, cfg)

        if changelogs.items:
            logger.debug("info:\n{}", changelogs.pritty_repr(doc.name, doc.url))
            post_slack_message(changelogs.pritty_repr(doc.name, doc.url))

        output_string += changelogs.pritty_repr(doc.name, doc.url) + "\n\n"

        with output_file.open("w") as f:
            f.write(output_string)


if __name__ == "__main__":
    main()
