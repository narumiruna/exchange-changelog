import cloudscraper

from .loader import Loader
from .utils import html_to_markdown


class CloudscraperLoader(Loader):
    def load(self, url: str) -> str:
        client = cloudscraper.create_scraper()
        response = client.get(url, allow_redirects=True)
        response.raise_for_status()
        return html_to_markdown(response.text)
