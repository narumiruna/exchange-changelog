from datetime import date
from datetime import timedelta
from pathlib import Path

import click
from dotenv import find_dotenv
from dotenv import load_dotenv
from loguru import logger

from changelog_helper.llm import set_sqlite_llm_cache
from changelog_helper.loaders import load_html_with_httpx
from changelog_helper.loaders import load_html_with_singlefile
from changelog_helper.tools import list_changelog

URLS = [
    ("woo", "https://docs.woox.io/#release-note", "httpx"),
    ("binance", "https://binance-docs.github.io/apidocs/spot/en/#change-log", "httpx"),
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
def main(output_file: Path) -> None:
    load_dotenv(find_dotenv())

    set_sqlite_llm_cache()

    changelogs = []
    for exchange, url, method in URLS:
        if method == "singlefile":
            text = load_html_with_singlefile(url)
        elif method == "httpx":
            text = load_html_with_httpx(url)
        else:
            raise ValueError(f"unknown method: {method}")

        # logger.debug("text: {}", text)

        from_date = date.today() - timedelta(days=7)
        to_date = date.today()

        resp = list_changelog(
            text,
            from_date=from_date,
            to_date=to_date,
        )
        logger.info("result: {}", resp)

        resp_string = ""
        for item in resp:
            if item["text"].strip() == "":
                continue
            resp_string += f"- {item['date']}: {item['text']}\n"

        if not resp_string:
            continue

        format_string = FORMAT_STRING_TEMPLATE.format(
            exchange=exchange,
            url=url,
            changelog=resp_string,
        )

        changelogs.append(format_string)
        logger.info("s: {}", format_string)

    with output_file.open("w") as f:
        f.write("\n\n".join(changelogs))


if __name__ == "__main__":
    main()
