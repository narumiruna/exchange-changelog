from typing import Literal

from loguru import logger
from playwright.sync_api import TimeoutError
from playwright.sync_api import sync_playwright

from .loader import Loader
from .utils import html_to_markdown


class PlaywrightLoader(Loader):
    def __init__(
        self,
        timeout: int = 10_000,
        wait_until: Literal["commit", "domcontentloaded", "load", "networkidle"] = "networkidle",
    ) -> None:
        self.timeout = timeout
        self.wait_until = wait_until

    def load(self, url: str) -> str:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            page = browser.new_page()

            try:
                page.goto(url, timeout=self.timeout, wait_until=self.wait_until)
            except TimeoutError as e:
                logger.error("TimeoutError: {}", e)
                page.goto(url)

            content = page.content()
            browser.close()

        return html_to_markdown(content)
