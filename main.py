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

URLS = [
    ("woo", "https://docs.woox.io/#release-note", "httpx"),
    ("binance", "https://binance-docs.github.io/apidocs/spot/en/#change-log", "httpx"),  # too long
    ("binance", "https://developers.binance.com/docs/binance-spot-api-docs/CHANGELOG", "httpx"),
    ("binance", "https://developers.binance.com/docs/margin_trading/change-log", "httpx"),
    ("binance", "https://developers.binance.com/docs/derivatives/change-log", "httpx"),
    ("coinbase", "https://docs.cdp.coinbase.com/exchange/docs/changelog/", "singlefile"),
    ("coinbase", "https://docs.cdp.coinbase.com/exchange/docs/upcoming-changes", "singlefile"),
    (
        "max",
        "https://docs.google.com/document/d/1iLwjhU-AHSLB4UnZh3cPbkYL-M3-R0jW0MEL6iWt410/edit?tab=t.0#heading=h.z31cougdyqo7",
        "singlefile",
    ),
    (
        "bybit",
        "https://bybit-exchange.github.io/docs/changelog/v5",
        "httpx",
    ),
    (
        "bitget",
        "https://www.bitget.com/api-doc/common/changelog",
        "httpx",
    ),
    (
        "okx",
        "https://www.okx.com/docs-v5/log_en/#upcoming-changes",
        "httpx",
    ),
]


FORMAT_STRING_TEMPLATE = r"""
# {exchange}

{url}

CHANGELOG:
{changelog}
"""


@click.command()
@click.option("-o", "--output-file", type=click.Path(path_type=Path), default="changelog.md", help="output file")
@click.option("-d", "--num-days", type=int, default=14, help="number of days to look back")
def main(output_file: Path, num_days: int) -> None:
    load_dotenv(find_dotenv())

    output_string = ""
    for exchange, url, method in URLS:
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
            logger.info("no changelogs found for {}", exchange)
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
            exchange=exchange,
            url=url,
            changelog=resp_string,
        )
        logger.info("format_string: {}", format_string)

        output_string += format_string + "\n\n"

        with output_file.open("w") as f:
            f.write(output_string)


if __name__ == "__main__":
    main()
