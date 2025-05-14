import asyncio
import os
from pathlib import Path
from typing import Annotated

import kabigon
import logfire
import typer
from dotenv import find_dotenv
from dotenv import load_dotenv
from loguru import logger
from redis.asyncio import Redis

from exchange_changelog.changelog import Changelog
from exchange_changelog.changelog import extract_changelog
from exchange_changelog.config import Config
from exchange_changelog.config import Document
from exchange_changelog.config import load_config
from exchange_changelog.slack import post_slack_message
from exchange_changelog.utils import configure_langfuse


class App:
    def __init__(self, config: Config, output_file: str | Path) -> None:
        self.config = config
        self.output_file = Path(output_file)

        # Setup redis
        self.redis = None
        redis_url = os.getenv("REDIS_URL")
        if redis_url is not None:
            self.redis = Redis.from_url(redis_url)

        self.lock = asyncio.Lock()
        self.results: list[tuple[Document, Changelog]] = []
        self.loader = kabigon.Compose(
            [
                # kabigon.HttpxLoader(),
                kabigon.PlaywrightLoader(timeout=50_000, wait_until="networkidle"),
                kabigon.PlaywrightLoader(timeout=10_000),
            ]
        )

    async def extract_recent_changelog(self, api_doc: Document) -> Changelog:
        text = await self.loader.async_load(api_doc.url)
        logger.info("text length: {}", len(text))

        # trim text
        text = text[: self.config.trim_len]

        changelog = await extract_changelog(text, prompt=self.config.prompt)

        # log parsed changes
        for change in changelog.changes:
            logger.info("change: {}", change)

        changelog.select_recent_changes(self.config.num_days)

        return changelog

    async def process_doc(self, doc: Document) -> None:
        try:
            with logfire.span(f"processing {doc.name}"):
                changelog = await self.extract_recent_changelog(doc)
        except Exception as e:
            logger.error("unable to extract changelog for {}, got: {}", doc.name, e)
            post_slack_message(f"unable to extract changelog for {doc.name}, got: {e}")
            changelog = Changelog(changes=[], upcoming_changes="")

        async with self.lock:
            self.results.append((doc, changelog))

    def write_file(self) -> None:
        with self.output_file.open("w", encoding="utf-8") as f:
            f.write(
                "\n\n".join(
                    [
                        changelog.to_markdown(
                            doc.name,
                            doc.url,
                        )
                        for doc, changelog in self.results
                    ]
                )
            )

    async def post_slack_message(self) -> None:
        for doc, changelog in self.results:
            if self.redis is not None:
                # filter out already seen changes
                new_changes = []
                for change in changelog.changes:
                    key = f"changelog:{doc.name}:{change.date}"

                    if await self.redis.exists(key):
                        logger.info("already seen change: {}", change)
                        continue

                    new_changes.append(change)
                    await self.redis.set(key, len(change.items))
                changelog.changes = new_changes
            # post to slack
            if changelog.changes:
                post_slack_message(changelog.to_slack(doc.name, doc.url))

    async def _run(self) -> None:
        tasks = [self.process_doc(doc) for doc in self.config.docs]
        await asyncio.gather(*tasks)

        self.write_file()
        await self.post_slack_message()

    def run(self) -> None:
        asyncio.run(self._run())


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
