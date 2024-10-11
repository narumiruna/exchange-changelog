from __future__ import annotations

import json
import os
from datetime import date

from google.generativeai import GenerationConfig
from google.generativeai import GenerativeModel
from google.generativeai import configure
from google.generativeai.types import ContentsType
from google.generativeai.types import GenerateContentResponse
from google.generativeai.types import HarmBlockThreshold
from google.generativeai.types import HarmCategory
from loguru import logger
from typing_extensions import TypedDict

PROMPT_TEMPLATE = r"""
Based on the context provided, generate the changelog or release notes for the period from {from_date} to {to_date}. Ensure compliance with the JSON schema and summarize the changelog in Markdown format.

Rules:
- Include only changelog or release notes with confirmed dates within {from_date} and {to_date}.
- All entries must be directly derived from the provided context, avoiding placeholder examples.
- Ignore any upcoming changes that lack explicit dates.
- If no changelog or release notes are available for the specified date range, return an empty string.
- Convert dates formatted as '2024-Sep-20' to '2024-09-20'.
- Present the results in Markdown format.

Context:
{context}

Changelog:
"""  # noqa


class ChangeLog(TypedDict):
    date: str
    text: str


class Gemini:
    def __init__(
        self,
        model: str = "gemini-1.5-pro",
        temperature: float = 0,
    ) -> None:
        self.model = model
        self.temperature = temperature

        generation_config = GenerationConfig(
            response_mime_type="application/json",
            response_schema=list[ChangeLog],
        )

        configure(api_key=os.environ["GOOGLE_API_KEY"])
        self.client = GenerativeModel(
            model_name=model,
            generation_config=generation_config,
        )

        self.safety_settings = {
            HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
        }

    def __call__(self, contents: ContentsType) -> GenerateContentResponse:
        return self.client.generate_content(
            contents=contents,
            # safety_settings=self.safety_settings,
        )


def list_changelog(text: str, from_date: date, to_date: date) -> dict:
    gemini = Gemini()
    response = gemini(
        [
            PROMPT_TEMPLATE.format(
                context=text,
                from_date=from_date,
                to_date=to_date,
            ),
        ],
    )

    if not response.parts:
        return {}

    try:
        return json.loads(response.text)
    except json.JSONDecodeError as e:
        logger.error(e)
        return {}
