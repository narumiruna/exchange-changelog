from __future__ import annotations

import functools
import json
import os

from google.generativeai import GenerationConfig
from google.generativeai import GenerativeModel
from google.generativeai import configure
from google.generativeai.types import ContentsType
from google.generativeai.types import HarmBlockThreshold
from google.generativeai.types import HarmCategory
from loguru import logger


@functools.cache
def get_gemini_model() -> str:
    model = os.getenv("GOOGLE_MODEL")
    if not model:
        logger.warning("GOOGLE_MODEL environment variable is not set, using gemini-1.5-pro")
        model = "gemini-1.5-pro"


@functools.cache
def get_gemini_client() -> GenerativeModel:
    api_key = os.environ["GOOGLE_API_KEY"]
    if not api_key:
        logger.error("GOOGLE_API_KEY is not set")
        return
    configure(api_key=api_key)

    model = get_gemini_model()
    return GenerativeModel(model_name=model)


def generate_content(contents: ContentsType, response_schema) -> dict:
    temperature = float(os.getenv("GOOGLE_TEMPERATURE", 0))

    generation_config = GenerationConfig(
        response_mime_type="application/json",
        response_schema=response_schema,
        temperature=temperature,
    )

    client = get_gemini_client()

    response = client.generate_content(
        contents=contents,
        generation_config=generation_config,
        safety_settings={
            HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
        },
    )

    if not response.parts:
        return {}

    try:
        return json.loads(response.text)
    except json.JSONDecodeError as e:
        logger.error(e)
        return {}
