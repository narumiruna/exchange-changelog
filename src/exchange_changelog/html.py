import os
import subprocess
import tempfile
from pathlib import Path
from typing import Literal

import cloudscraper
import httpx
from loguru import logger
from markdownify import markdownify
from playwright.sync_api import TimeoutError
from playwright.sync_api import sync_playwright

from .loaders import PipelineLoader
from .utils import load_text


def save_html_with_singlefile(url: str, cookies_file: str | None = None, timeout: int = 10_000) -> str:
    logger.info("Downloading HTML by SingleFile: {}", url)

    filename = tempfile.mktemp(suffix=".html")

    singlefile_path = os.getenv("SINGLEFILE_PATH", "single-file")

    cmds = [singlefile_path]

    if cookies_file is not None:
        if not Path(cookies_file).exists():
            raise FileNotFoundError("cookies file not found")

        cmds += [
            "--browser-cookies-file",
            cookies_file,
        ]

    cmds += [
        "--browser-load-max-time",
        str(timeout),
        "--filename-conflict-action",
        "overwrite",
        url,
        filename,
    ]

    subprocess.run(cmds)

    return filename


def load_html_with_singlefile(url: str) -> str:
    f = save_html_with_singlefile(url)

    text = markdownify(load_text(f), strip=["a", "img"])
    return text


def load_html_with_httpx(url: str) -> str:
    logger.info("Loading HTML: {}", url)

    headers = {
        "Accept-Language": "zh-TW,zh;q=0.9,ja;q=0.8,en-US;q=0.7,en;q=0.6",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36",  # noqa
    }

    resp = httpx.get(url=url, headers=headers, follow_redirects=True)
    resp.raise_for_status()

    text = markdownify(resp.text, strip=["a", "img"])
    return text


def load_url_with_playwright(url: str) -> str:
    content = ""
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()

        try:
            page.goto(url, timeout=10_000, wait_until="networkidle")
        except TimeoutError as e:
            logger.error("TimeoutError: {}", e)
            page.goto(url)

        content = page.content()
        browser.close()

    md_content = markdownify(content, strip=["a", "img"])
    return md_content.strip()


def load_html_with_cloudscraper(url: str) -> str:
    headers = {
        "Accept-Language": "zh-TW,zh;q=0.9,ja;q=0.8,en-US;q=0.7,en;q=0.6",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36",  # noqa
    }

    scraper = cloudscraper.create_scraper()
    resp = scraper.get(url, headers=headers)
    resp.raise_for_status()

    text = markdownify(resp.text, strip=["a", "img"])
    return text


def load_html(url: str, method: Literal["httpx", "singlefile", "playwright", "cloudscraper"]) -> str:
    # match method:
    #     case "singlefile":
    #         return load_html_with_singlefile(url)
    #     case "httpx":
    #         return load_html_with_httpx(url)
    #     case "playwright":
    #         return load_url_with_playwright(url)
    #     case "cloudscraper":
    #         return load_html_with_cloudscraper(url)
    #     case _:
    #         raise ValueError(f"unknown method: {method}")

    return PipelineLoader().load(url)
