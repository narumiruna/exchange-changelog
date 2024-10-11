import os
from datetime import date
from datetime import datetime
from datetime import timedelta

from loguru import logger
from openai import OpenAI
from pydantic import BaseModel

PROMPT_TEMPLATE = r"""
Extract and summarize the first ten sets of ChangeLogs or Release Notes based on their dates.

Guidelines:
- Ensure the output conforms to the specified JSON schema.
- Only use information directly from the provided context; avoid placeholder or generic examples.
- Exclude any upcoming changes that lack explicit dates.
- Standardize dates formatted as '2024-Sep-20' to '2024-09-20'.
- If no changelog or release note exists for a particular date, skip the extraction for that date.
- Output the results in Markdown format.

Context:
{context}

Changelog:
"""


class ChangeLog(BaseModel):
    date: str
    content: str
    keywords: list[str]


class ChangeLogList(BaseModel):
    items: list[ChangeLog]

    def pritty_repr(self) -> str:
        format_string = ""

        prev_date = None
        for changelog in self.items:
            if prev_date != changelog.date:
                prev_date = changelog.date
                format_string += f"## {changelog.date}\n"
            format_string += f"{changelog.content}\n"

            if changelog.keywords:
                format_string += "Keywords: "
                format_string += ", ".join(changelog.keywords)
                format_string += "\n"

            format_string += "\n"
        return format_string


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
                    "role": "user",
                    "content": PROMPT_TEMPLATE.format(
                        context=text,
                    ),
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
