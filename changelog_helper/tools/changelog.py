import json
from datetime import date

from loguru import logger

from ..gemini import Gemini

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
