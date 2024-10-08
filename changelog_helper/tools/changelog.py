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
    parts: list[ChangeLog]


def extract_changelog(text: str) -> ChangeLogList | None:
    client = OpenAI()

    completion = client.beta.chat.completions.parse(
        model="gpt-4o-mini",
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
