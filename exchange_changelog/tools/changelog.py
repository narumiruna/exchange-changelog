import os
from datetime import date
from datetime import datetime
from datetime import timedelta

from loguru import logger
from openai import OpenAI
from pydantic import BaseModel

SYSTEM_PROMPT = r"""
Extract and summarize the first ten sets of ChangeLogs or Release Notes according to their dates.

For MAX Exchange, ensure to include relevant details from the changelog and release notes that highlight significant updates, improvements, or changes in functionality.


Guidelines:
- Ensure the output adheres to the specified JSON schema.
- Use only information directly from the provided context; avoid placeholder or generic examples.
- Exclude upcoming changes that do not have explicit dates.
- Standardize date formats from '2024-Sep-20' to '2024-09-20'.
- If no changelog or release note is available for a given date, skip the extraction for that date.
- Present the results in Markdown format.
"""  # noqa


class ChangeLog(BaseModel):
    date: str
    markdown_content: str
    keywords: list[str]


class ChangeLogList(BaseModel):
    items: list[ChangeLog]

    def pritty_repr(self) -> str:
        result = []

        prev_date = None
        for changelog in self.items:
            if prev_date != changelog.date:
                prev_date = changelog.date
                result.append(f"## {changelog.date}")
            result.append(changelog.markdown_content)

            if changelog.keywords:
                result.append(f"Keywords: {', '.join(changelog.keywords)}")

            result.append("\n")

        return "\n".join(result)


def select_recent_changelogs(changelog_list: ChangeLogList, num_days: int) -> ChangeLogList:
    new_changelog_list: ChangeLogList = ChangeLogList(items=[])
    for item in changelog_list.items:
        item_date = datetime.strptime(item.date, "%Y-%m-%d").date()
        if item_date >= date.today() - timedelta(days=num_days):
            new_changelog_list.items.append(item)
    return new_changelog_list


def extract_changelog(text: str) -> ChangeLogList | None:
    client = OpenAI()

    # https://platform.openai.com/docs/guides/structured-outputs
    try:
        completion = client.beta.chat.completions.parse(
            model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            messages=[
                {
                    "role": "system",
                    "content": SYSTEM_PROMPT,
                },
                {
                    "role": "user",
                    "content": text,
                },
            ],
            response_format=ChangeLogList,
        )

        if not completion.choices:
            logger.warning("no completion choices")
            return None

        response = completion.choices[0].message
        if response.parsed:
            return response.parsed
        elif response.refusal:
            logger.warning("unable to parse the changelog: {}", response.refusal)
            return None
        else:
            logger.warning("no parsed response")
            return None
    except Exception as e:
        logger.error("unable to parse the changelog: {}", e)
        return None
