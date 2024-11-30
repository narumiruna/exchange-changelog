from pathlib import Path

import click
from dotenv import find_dotenv
from dotenv import load_dotenv
from loguru import logger

from exchange_changelog import redis
from exchange_changelog.changelog import Changelog
from exchange_changelog.changelog import extract_changelog
from exchange_changelog.config import APIDoc
from exchange_changelog.config import Config
from exchange_changelog.config import load_config
from exchange_changelog.html import load_html
from exchange_changelog.slack import post_slack_message


def extract_recent_changelog(api_doc: APIDoc, cfg: Config) -> Changelog:
    text = load_html(api_doc.url, api_doc.method)
    logger.info("text length: {}", len(text))

    # trim text
    text = text[: cfg.trim_len]

    changelog = extract_changelog(text, prompt=cfg.prompt)

    # log parsed changes
    for change in changelog.changes:
        logger.info("change: {}", change)

    changelog.select_recent_changes(cfg.num_days)

    return changelog


@click.command()
@click.option("-c", "--config-file", type=click.Path(path_type=Path), default="config/default.yaml", help="config file")
@click.option("-o", "--output-file", type=click.Path(path_type=Path), default="changelog.md", help="output file")
@click.option("-r", "--use-redis", is_flag=True, help="use redis")
def main(config_file: Path, output_file: Path, use_redis: bool) -> None:
    load_dotenv(find_dotenv())

    logger.info("loading config file: {}", config_file)
    cfg = load_config(config_file)
    logger.info("prompt:\n{}", cfg.prompt)

    results: list[tuple[APIDoc, Changelog]] = []
    for doc in cfg.docs:
        try:
            changelog = extract_recent_changelog(doc, cfg)
        except Exception as e:
            logger.error("unable to extract changelog: {}", e)
            post_slack_message(f"unable to extract changelog for {doc.name}, got error: {e}")
            changelog = Changelog(changes=[], upcoming_changes="")
        results.append((doc, changelog))

    # output to file
    lines = []
    for doc, changelog in results:
        lines += [changelog.to_markdown(doc.name, doc.url)]
        logger.debug("changelog:\n{}", changelog.to_markdown(doc.name, doc.url))

    with output_file.open("w") as f:
        f.write("\n\n".join(lines))

    # post to slack
    for doc, changelog in results:
        if use_redis:
            # filter out already seen changes
            new_changes = []
            for change in changelog.changes:
                key = f"changelog:{doc.name}:{change.date}"
                if redis.exists(key):
                    logger.info("already seen change: {}", change)
                    continue

                new_changes.append(change)
                redis.set(key, len(change.markdown_content))
            changelog.changes = new_changes

        if changelog.changes:
            post_slack_message(changelog.to_slack_format(doc.name, doc.url))


if __name__ == "__main__":
    main()
