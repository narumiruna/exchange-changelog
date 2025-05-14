from typing import Literal

from loguru import logger
from markdownify import markdownify as md
from playwright.async_api import async_playwright


def strip_empty_lines(text: str) -> str:
    lines = []
    for line in text.splitlines():
        stripped = line.strip()
        if stripped:
            lines += [stripped]
    return "\n".join(lines)


class PlaywrightScraper:
    def __init__(
        self,
        timeout: float | None = 0,
        wait_until: Literal["commit", "domcontentloaded", "load", "networkidle"] = "networkidle",
        browser_headless: bool = False,
    ) -> None:
        self.timeout = timeout
        self.wait_until = wait_until
        self.browser_headless = browser_headless

    async def __call__(self, url: str) -> str:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=self.browser_headless)
            context = await browser.new_context()
            page = await context.new_page()

            try:
                await page.goto(url, timeout=self.timeout, wait_until=self.wait_until)
            except Exception as e:
                logger.warning(
                    "Unable to load page: {}, falling back to default wait_until(load). Got error: {}", url, e
                )
                await page.goto(url, timeout=self.timeout)

            content = await page.content()
            await browser.close()

            return strip_empty_lines(md(content, strip=["a", "img"]))
