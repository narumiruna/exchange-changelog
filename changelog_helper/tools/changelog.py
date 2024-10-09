import os
from datetime import date
from datetime import datetime
from datetime import timedelta

from openai import OpenAI
from pydantic import BaseModel

PROMPT_TEMPLATE = r"""
Extract and summarize the first ten sets of ChangeLog or Release Notes based on the date.

Rules:
- Ensure compliance with the JSON schema.
- All entries must be directly derived from the provided context, avoiding placeholder examples.
- Ignore any upcoming changes that lack explicit dates.
- Convert dates formatted as '2024-Sep-20' to '2024-09-20'.
- Present the results in Markdown format.

Context:
{context}

Changelog:
"""  # noqa


class ChangeLog(BaseModel):
    date: str
    changelog: str


class ChangeLogList(BaseModel):
    items: list[ChangeLog]

    def pritty_repr(self) -> str:
        format_string = ""

        prev_date = None
        for changelog in self.items:
            if prev_date != changelog.date:
                prev_date = changelog.date
                format_string += f"## {changelog.date}\n"
            format_string += f"{changelog.changelog}\n"

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
    # TODO: Handle edge cases
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
        return None

    return completion.choices[0].message.parsed
