from pathlib import Path
from typing import Annotated

import kabigon
import typer
from dotenv import find_dotenv
from dotenv import load_dotenv
from loguru import logger

from exchange_changelog import redis
from exchange_changelog.changelog import Changelog
from exchange_changelog.changelog import extract_changelog
from exchange_changelog.config import Config
from exchange_changelog.config import Document
from exchange_changelog.config import load_config
from exchange_changelog.slack import post_slack_message

loader = kabigon.Compose(
    [
        kabigon.HttpxLoader(),
        kabigon.PlaywrightLoader(timeout=50_000, wait_until="networkidle"),
        kabigon.PlaywrightLoader(timeout=10_000),
    ]
)


def extract_recent_changelog(api_doc: Document, cfg: Config) -> Changelog:
    text = loader.load(api_doc.url)
    logger.info("text length: {}", len(text))

    # trim text
    text = text[: cfg.trim_len]

    changelog = extract_changelog(text, prompt=cfg.prompt)

    # log parsed changes
    for change in changelog.changes:
        logger.info("change: {}", change)

    changelog.select_recent_changes(cfg.num_days)

    return changelog


def main(
    config_file: Annotated[Path, typer.Option("-c", "--config-file", help="config file")] = Path("config/default.yaml"),
    output_file: Annotated[Path, typer.Option("-o", "--output-file", help="output file")] = Path("changelog.md"),
    use_redis: Annotated[bool, typer.Option("-r", "--use-redis", help="use redis")] = False,
) -> None:
    load_dotenv(find_dotenv())

    logger.info("loading config file: {}", config_file)
    cfg = load_config(config_file)
    logger.info("prompt:\n{}", cfg.prompt)

    results: list[tuple[Document, Changelog]] = []
    for doc in cfg.docs:
        try:
            changelog = extract_recent_changelog(doc, cfg)
            if use_redis:
                # filter out already seen changes
                new_changes = []
                for change in changelog.changes:
                    key = f"changelog:{doc.name}:{change.date}"
                    if redis.exists(key):
                        logger.info("already seen change: {}", change)
                        continue

                    new_changes.append(change)
                    redis.set(key, len(change.items))
                changelog.changes = new_changes
            # post to slack
            if changelog.changes:
                post_slack_message(changelog.to_slack(doc.name, doc.url))
        except Exception as e:
            logger.error("unable to extract changelog for {}, got: {}", doc.name, e)
            post_slack_message(f"unable to extract changelog for {doc.name}, got: {e}")
            changelog = Changelog(changes=[], upcoming_changes="")

        results.append((doc, changelog))

    # output to file
    lines = []
    for doc, changelog in results:
        lines += [changelog.to_markdown(doc.name, doc.url)]
        logger.debug("changelog:\n{}", changelog.to_markdown(doc.name, doc.url))

    with output_file.open("w") as f:
        f.write("\n\n".join(lines))


if __name__ == "__main__":
    typer.run(main)
