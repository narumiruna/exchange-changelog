from openai import OpenAI
from pydantic import BaseModel

PROMPT_TEMPLATE = r"""
Extract the first five sets of ChangeLog or Release Notes based on the specified date.
Ensure compliance with the JSON schema.

Rules:
- All entries must be directly derived from the provided context, avoiding placeholder examples.
- Ignore any upcoming changes that lack explicit dates.
- If there are no changelogs or release notes available for the specified date range, return an empty string.
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
    parts: list[ChangeLog]


def extract_changelog(text: str) -> ChangeLog:
    client = OpenAI()

    completion = client.beta.chat.completions.parse(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Extract the changelog or release notes from the provided context."},
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
        return {}

    response = completion.choices[0].message.parsed

    return response
