from datetime import date
from datetime import datetime
from datetime import timedelta
from pathlib import Path

import click
from dotenv import find_dotenv
from dotenv import load_dotenv
from loguru import logger

from changelog_helper.loaders import load_html_with_httpx
from changelog_helper.loaders import load_html_with_singlefile
from changelog_helper.tools.changelog import ChangeLog
from changelog_helper.tools.changelog import extract_changelog
from changelog_helper.utils import load_yaml

FORMAT_STRING_TEMPLATE = r"""
# {exchange}

{url}

CHANGELOG:
{changelog}
"""


@click.command()
@click.option("-c", "--config-file", type=click.Path(path_type=Path), default="config/default.yaml", help="config file")
@click.option("-o", "--output-file", type=click.Path(path_type=Path), default="changelog.md", help="output file")
def main(config_file: Path, output_file: Path) -> None:
    load_dotenv(find_dotenv())

    logger.info("loading config file: {}", config_file)
    cfg = load_yaml(config_file)
    urls = cfg.get("urls", [])
    num_days = cfg.get("num_days", 14)

    output_string = ""
    for url_data in urls:
        name = url_data.get("name")
        url = url_data.get("url")
        method = url_data.get("method")

        if method == "singlefile":
            text = load_html_with_singlefile(url)
        elif method == "httpx":
            text = load_html_with_httpx(url)
        else:
            raise ValueError(f"unknown method: {method}")

        logger.info("text length: {}", len(text))

        # trim text
        text = text[:20000]

        resp = extract_changelog(text)
        if resp is None:
            logger.info("no changelogs found for {}", name)
            continue

        for part in resp.items:
            logger.info("part: {}", part)

        changelog_list: list[ChangeLog] = []

        # remove old changelogs
        for item in resp.items:
            item_date = datetime.strptime(item.date, "%Y-%m-%d").date()
            if item_date >= date.today() - timedelta(days=num_days):
                logger.info("item: {}", item)
                changelog_list.append(item)

        # if not changelog_list:
        #     logger.info("no changelogs found for {}", exchange)
        #     continue

        resp_string = ""
        for changelog in changelog_list:
            resp_string += f"- {changelog.date}: {changelog.changelog}\n"

        format_string = FORMAT_STRING_TEMPLATE.format(
            exchange=name,
            url=url,
            changelog=resp_string,
        )
        logger.info("format_string: {}", format_string)

        output_string += format_string + "\n\n"

        with output_file.open("w") as f:
            f.write(output_string)


if __name__ == "__main__":
    main()
