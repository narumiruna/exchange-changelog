from pathlib import Path
from typing import Literal

import click
from dotenv import find_dotenv
from dotenv import load_dotenv
from loguru import logger

from exchange_changelog.config import load_config
from exchange_changelog.loaders import load_html_with_httpx
from exchange_changelog.loaders import load_html_with_singlefile
from exchange_changelog.slack import post_slack_message
from exchange_changelog.tools.changelog import extract_changelog
from exchange_changelog.tools.changelog import select_recent_changelogs


def load_html(url: str, method: Literal["httpx", "singlefile"]) -> str:
    if method == "singlefile":
        return load_html_with_singlefile(url)
    elif method == "httpx":
        return load_html_with_httpx(url)
    else:
        raise ValueError(f"unknown method: {method}")


@click.command()
@click.option("-c", "--config-file", type=click.Path(path_type=Path), default="config/default.yaml", help="config file")
@click.option("-o", "--output-file", type=click.Path(path_type=Path), default="changelog.md", help="output file")
def main(config_file: Path, output_file: Path) -> None:
    load_dotenv(find_dotenv())

    logger.info("loading config file: {}", config_file)
    cfg = load_config(config_file)

    output_string = ""
    for doc in cfg.docs:
        output_string += f"# [{doc.name}]({doc.url})\n\n"

        text = load_html(doc.url, doc.method)
        logger.info("text length: {}", len(text))

        # trim text
        text = text[: cfg.trim_len]

        changelog_list = extract_changelog(text)
        if changelog_list is None:
            logger.info("no changelogs found for {}", doc.name)
            continue

        # log parsed changelogs
        for changelog in changelog_list.items:
            logger.info("changelog: {}", changelog)

        changelog_list = select_recent_changelogs(changelog_list, cfg.num_days)

        output_string += changelog_list.pritty_repr() + "\n\n"

        with output_file.open("w") as f:
            f.write(output_string)

    post_slack_message(output_string)


if __name__ == "__main__":
    main()
