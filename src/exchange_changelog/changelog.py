from datetime import date
from datetime import datetime
from datetime import timedelta
from enum import Enum

from loguru import logger
from pydantic import BaseModel

from .lazy import lazy_run_sync

SYSTEM_PROMPT = """
You will be provided with content from an API documentation page in Markdown format. Your task is to extract and summarize up to 10 changes or release notes, prioritizing them by date as found in sections such as changelog or release notes. Additionally, extract and summarize upcoming changes only if the main heading "Upcoming Changes" is present; otherwise, leave the corresponding field blank.

Please follow these instructions step by step for high-quality output:

1. Identify and extract up to 10 distinct changes or release notes that are each associated with a specific date.
    - Only include entries with real, non-placeholder dates for which substantive information is provided.
    - Ignore entries that lack content, use placeholder dates, or serve as examples.
2. Normalize all dates to the 'YYYY-MM-DD' format (e.g., convert '2024-Sep-20' to '2024-09-20'). Validate that each date is real and correctly formatted.
3. For each extracted entry, summarize the change or release note in clear, plain text.
4. Identify and list relevant keywords that summarize the main points (excluding generic category names).
5. List the categories associated with each entry.
6. If the "Upcoming Changes" main heading is present, extract and summarize the section beneath it. If not, leave the upcoming_changes field blank.
7. Use only information directly provided in the content. Do not fabricate or add any placeholders.

Output Format:
For each extracted change, use the following structure:

- date: The change or release date in 'YYYY-MM-DD' format.
- items: A list of strings, each summarizing a change or release note in plain text.
- keywords: An array of relevant keywords summarizing the main points of each entry, excluding category names.
- categories: An array of strings representing the update categories.
- upcoming_changes: A summary of the "Upcoming Changes" section if present; otherwise, leave this field blank.

Think step by step to ensure that each instruction is carefully followed and that your output is accurate, complete, and adheres strictly to the provided context.
""".strip()  # noqa


class Step(BaseModel):
    explanation: str
    output: str


class Reasoning(BaseModel):
    steps: list[Step]
    final_output: str


class Category(str, Enum):
    BREAKING_CHANGES = "BREAKING_CHANGES"
    NEW_FEATURES = "NEW_FEATURES"
    DEPRECATIONS = "DEPRECATIONS"
    BUG_FIXES = "BUG_FIXES"
    PERFORMANCE_IMPROVEMENTS = "PERFORMANCE_IMPROVEMENTS"
    SECURITY_UPDATES = "SECURITY_UPDATES"

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
    reasoning: Reasoning
    date: str
    items: list[str]
    keywords: list[str]
    categories: list[Category]

    def to_markdown(self) -> str:
        lines = [
            f"📅*{self.date}*",
            "\n".join([f"- {item}" for item in self.items]),
            " ".join([f"🏷️{keyword}" for keyword in self.keywords]),
            " ".join([category.get_emoji() + category for category in self.categories]),
        ]
        return "\n\n".join(lines)

    def to_slack(self) -> str:
        lines = [
            f"📅*<{self.date}>*",
            "\n".join([f"- {item}" for item in self.items]),
            " ".join([f"🏷️{keyword}" for keyword in self.keywords]),
            " ".join([category.get_emoji() + category for category in self.categories]),
        ]
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
    return lazy_run_sync(
        input=text,
        instructions=prompt.strip(),
        output_type=Changelog,
    )
