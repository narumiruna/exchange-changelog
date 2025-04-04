from datetime import date
from datetime import datetime
from datetime import timedelta
from enum import Enum

from loguru import logger
from pydantic import BaseModel

from .openai import parse_completion

SYSTEM_PROMPT = r"""
You will be provided with content from an API documentation page in Markdown format.
Extract up to 10 changes or release notes, prioritizing those based on their dates from the changelog or release notes section.
Also, extract upcoming changes: if the main heading "Upcoming Changes" is present, extract and summarize the content beneath it; if not, leave the output blank.

Instructions:
- Date Validation: Ensure all dates are in the format 'YYYY-MM-DD' (e.g., convert '2024-Sep-20' to '2024-09-20'). Dates must be real and not placeholders.
- Extraction Rules:
- Only extract dates that have actual changes or release notes associated with them.
- Skip entries without substantive information or dates that serve as examples or placeholders.
- Content Integrity: Use only the information directly provided in the context—do not fabricate or include placeholders.

Output Format:
For each extracted entry, provide the following:
- date: The release or change date.
- markdown_content: The content of the change or release note in Markdown format.
- keywords: An array of relevant keywords summarizing the main points of each entry (excluding category names).
- categories: An array of strings representing the categories related to the update.
""".strip()  # noqa


class Category(str, Enum):
    BREAKING_CHANGES = "breaking changes"
    NEW_FEATURES = "new features"
    DEPRECATIONS = "deprecations"
    BUG_FIXES = "bug fixes"
    PERFORMANCE_IMPROVEMENTS = "performance improvements"
    SECURITY_UPDATES = "security updates"

    def get_emoji(self) -> str:
        return {
            self.BREAKING_CHANGES: "💥",
            self.NEW_FEATURES: "✨",
            self.DEPRECATIONS: "🗑️",
            self.BUG_FIXES: "🐛",
            self.PERFORMANCE_IMPROVEMENTS: "⚡",
            self.SECURITY_UPDATES: "🔒",
        }[self]


class Change(BaseModel):
    date: str
    markdown_content: str
    keywords: list[str]
    categories: list[Category]

    def to_markdown(self) -> str:
        lines = [
            f"📅*{self.date}*",
            self.markdown_content,
        ]

        if self.keywords:
            lines += [f"Keywords: {', '.join(self.keywords)}"]

        if self.categories:
            lines += [f"Categories: {', '.join([category.get_emoji()+ category for category in self.categories])}"]

        return "\n\n".join(lines)

    def to_slack(self) -> str:
        lines = [
            f"📅*<{self.date}>*",
            self.markdown_content,
        ]

        if self.keywords:
            lines += [f"*Keywords:* {', '.join(self.keywords)}"]

        if self.categories:
            lines += [f"*Categories:* {', '.join([category.get_emoji()+ category for category in self.categories])}"]

        return "\n\n".join(lines)


class Changelog(BaseModel):
    changes: list[Change]
    upcoming_changes: str

    def to_markdown(self, name: str | None, url: str | None = None) -> str:
        lines = []

        if name and url:
            lines += [f"# [{name}]({url})"]

        if self.upcoming_changes:
            lines += ["🔜*Upcoming Changes*"]
            lines += [self.upcoming_changes]

        for changelog in self.changes:
            lines += [changelog.to_markdown()]

        return "\n\n".join(lines)

    def to_slack(self, name: str | None, url: str | None = None) -> str:
        lines = []

        if name and url:
            lines += [f"*<{url}|{name}>*"]

        if self.upcoming_changes:
            lines += ["🔜*Upcoming Changes*"]
            lines += [self.upcoming_changes]

        for changelog in self.changes:
            lines += [changelog.to_slack()]

        return "\n\n".join(lines)

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
                "content": text.strip(),
            },
        ],
        response_format=Changelog,
    )
