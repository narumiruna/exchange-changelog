from loguru import logger

from .cloudscraper import CloudscraperLoader
from .httpx import HttpxLoader
from .loader import Loader
from .loader import LoaderError
from .playwright import PlaywrightLoader
from .singlefile import SinglefileLoader


class PipelineLoader:
    def __init__(self) -> None:
        self.loaders: list[Loader] = [
            CloudscraperLoader(),
            HttpxLoader(),
            PlaywrightLoader(),
            SinglefileLoader(),
        ]

    def load(self, url: str) -> str:
        for loader in self.loaders:
            logger.info("[{}] Loading URL: {}", loader.__class__.__name__, url)
            try:
                text = loader.load(url)
                if len(text) == 0:
                    logger.info("[{}] Text length is 0", loader.__class__.__name__)
                    continue
                return text
            except Exception as e:
                logger.info("[{}] Failed to load URL: {}, got error: {}", loader.__class__.__name__, url, e)

        raise LoaderError(f"Failed to load URL: {url}")
