from loguru import logger
from pydantic import BaseModel

from ..llm import parse_completion
from .changelog import Category

SYSTEM_PROMPT = """Summarize and itemize the upcoming changes from the provided markdown text under the heading "Upcoming Changes." Additionally, categorize each change using the predefined categories.

- Search for the heading "Upcoming Changes" in the provided markdown.
- If the heading is found, extract all content that follows it until the next heading or the end of the document.
- For each change, determine its category based on the content and assign it accordingly using the following categories:
  - **BREAKING_CHANGES**: Significant changes that may affect backward compatibility.
  - **NEW_FEATURES**: New functionalities being introduced.
  - **DEPRECATIONS**: Features that are being phased out.
  - **BUG_FIXES**: Corrections made to existing issues.
  - **PERFORMANCE_IMPROVEMENTS**: Enhancements aimed at improving efficiency.
  - **SECURITY_UPDATES**: Changes made to improve security.

- Present the extracted changes in a structured JSON format that can be parsed by the following class definitions.

# Notes

- Ensure that the extracted content is accurate and categorized correctly.
- If there are multiple changes, they should be listed individually with their respective categories.
"""  # noqa


class Change(BaseModel):
    content: str
    category: Category

    def __str__(self) -> str:
        return self.content + f" #{self.category.value}"


class UpcomingChanges(BaseModel):
    changes: list[Change]

    def pretty_repr(self) -> str:
        if not self.changes:
            return ""

        format_string = "## Upcoming Changes\n\n"

        for change in self.changes:
            format_string += f"- {change}\n"

        return format_string


def extract_upcoming_changes(text: str) -> UpcomingChanges | None:
    # https://platform.openai.com/docs/guides/structured-outputs
    try:
        return parse_completion(
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
            response_format=UpcomingChanges,
        )
    except Exception as e:
        logger.error("unable to parse the changelog: {}", e)
        return None
