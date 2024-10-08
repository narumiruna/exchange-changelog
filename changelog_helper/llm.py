import functools
import os
from pathlib import Path

from langchain.globals import set_llm_cache
from langchain_community.cache import SQLiteCache
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_google_genai.chat_models import ChatGoogleGenerativeAI
from langchain_openai.chat_models import ChatOpenAI
from loguru import logger


@functools.cache
def get_llm_from_env() -> BaseChatModel:
    model = os.getenv("MODEL", "gemini-1.5-pro")
    # model = os.getenv("MODEL", "gpt-4o-mini")
    temperature = float(os.getenv("TEMPERATURE", 0.0))
    logger.info("language model: {}, temperature: {}", model, temperature)

    if model.startswith("gpt-"):
        return ChatOpenAI(model=model, temperature=temperature)
    elif model.startswith("gemini-"):
        return ChatGoogleGenerativeAI(model=model, temperature=temperature)
    else:
        raise ValueError("No API key found in environment variables")


def set_sqlite_llm_cache() -> None:
    database_path = Path.home() / ".cache" / ".langchain.db"
    logger.info("Using SQLite cache: {}", database_path)

    cache = SQLiteCache(database_path.as_posix())

    set_llm_cache(cache)
