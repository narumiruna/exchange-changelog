import os
import re
import subprocess
import tempfile
from pathlib import Path

import httpx
from loguru import logger
from markdownify import markdownify

from .utils import load_text


def remove_base64_image(markdown_text: str) -> str:
    pattern = r"!\[.*?\]\(data:image\/.*?;base64,.*?\)"
    cleaned_text = re.sub(pattern, "", markdown_text)
    return cleaned_text


def save_html_with_singlefile(url: str, cookies_file: str | None = None) -> str:
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
    text = remove_base64_image(text)
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
    text = remove_base64_image(text)

    return text


def load_url_with_playwright(url: str) -> str:
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(url, wait_until="networkidle")
        text = page.content()
        browser.close()

    text = markdownify(text, strip=["a", "img"])
    return text
