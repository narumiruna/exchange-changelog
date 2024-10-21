from datetime import date
from datetime import datetime
from datetime import timedelta
from enum import Enum

from loguru import logger
from pydantic import BaseModel

from .llm.openai import parse_completion

SYSTEM_PROMPT = r"""
Extract the first ten sets of changes or release notes according to their dates from changelog or release note page.
Extract and summarize upcoming changes. If the main heading "Upcoming Changes" is present, extract and summarize the content beneath it; if not, leave the output blank.

For MAX Exchange, ensure to include relevant details from the changes and release notes that highlight significant updates, improvements, or changes in functionality.

**Guidelines:**
- Ensure the output adheres to the specified JSON schema.
- Use only information directly from the provided context; avoid placeholder or generic examples.
- Standardize and validate date formats to 'YYYY-MM-DD' (e.g., convert '2024-Sep-20' to '2024-09-20').
- If no change or release note is available for a given date, skip the extraction for that date.
- Present the results in Markdown format.

# Output Format

The resulting output should be formatted as a JSON object containing:
- an array of objects, each including:
  - `date`: a string in 'YYYY-MM-DD' format
  - `markdown_content`: a string summarizing the change details in a bullet-point list
  - `keywords`: an array of keywords related to each change entry (excluding categories)
  - `categories`: an array of strings indicating the categories associated with the update (e.g., BREAKING_CHANGES, NEW_FEATURES, BUG_FIXES, DEPRECATIONS, PERFORMANCE_IMPROVEMENTS, SECURITY_UPDATES)

(NOTE: Real examples should contain more elaborate change details and diverse keywords.)
""".strip()  # noqa


class Category(str, Enum):
    BREAKING_CHANGES = "breaking changes"
    NEW_FEATURES = "new features"
    DEPRECATIONS = "deprecations"
    BUG_FIXES = "bug fixes"
    PERFORMANCE_IMPROVEMENTS = "performance improvements"
    SECURITY_UPDATES = "security updates"


class Change(BaseModel):
    date: str
    markdown_content: str
    keywords: list[str]
    categories: list[Category]

    def pretty_repr(self) -> str:
        s = f"*{self.date}*\n"
        s += self.markdown_content + "\n"
        if self.keywords:
            s += f"Keywords: {', '.join(self.keywords)}\n"
        if self.categories:
            s += f"Categories: {', '.join(self.categories)}\n"
        return s


class UpcomingChange(BaseModel):
    markdown_content: str
    categories: list[Category]

    def pretty_repr(self) -> str:
        s = self.markdown_content + "\n"
        if self.categories:
            s += f"Categories: {', '.join(self.categories)}\n"
        return s


class Changelog(BaseModel):
    changes: list[Change]
    upcoming_changes: list[UpcomingChange]

    def pretty_repr(self, name: str | None, url: str | None = None) -> str:
        s = ""
        if name and url:
            s += f"# [{name}]({url})\n"

        if self.upcoming_changes:
            s += "*Upcoming Changes*\n"
            for upcoming_change in self.upcoming_changes:
                s += upcoming_change.pretty_repr()

        for changelog in self.changes:
            s += changelog.pretty_repr()

        return s

    def select_recent_changes(self, num_days: int) -> None:
        recent_changes = []

        for change in self.changes:
            try:
                item_date = datetime.strptime(change.date, "%Y-%m-%d").date()
            except ValueError as e:
                logger.warning("unable to parse date: {} got error: {}", change.date, e)
                continue
            if item_date >= date.today() - timedelta(days=num_days):
                recent_changes.append(change)

        self.changes = recent_changes


def extract_changelog(text: str, prompt: str | None = None) -> Changelog:
    # https://platform.openai.com/docs/guides/structured-outputs
    prompt = prompt or SYSTEM_PROMPT

    return parse_completion(
        messages=[
            {
                "role": "system",
                "content": prompt.strip(),
            },
            {
                "role": "user",
                "content": f'Input:\n"""\n{text}\n"""\n',
            },
        ],
        response_format=Changelog,
    )
