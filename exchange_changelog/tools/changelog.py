from datetime import date
from datetime import datetime
from datetime import timedelta
from enum import Enum

from loguru import logger
from pydantic import BaseModel

from ..llm.openai import parse_completion

SYSTEM_PROMPT = r"""
Extract and summarize the first ten sets of changelog or release notes according to their dates. Extract and summarize upcoming changes. If the main heading "Upcoming Changes" is present, extract and summarize the content beneath it; if not, leave the output blank.

For MAX Exchange, ensure to include relevant details from the changelog and release notes that highlight significant updates, improvements, or changes in functionality.

Steps:
- Identify and extract the first ten sets of changelog or release notes based on their dates.
- Standardize the date format to 'YYYY-MM-DD'.
- Summarize the key updates, improvements, or changes in functionality for each extracted entry.
- Check for the presence of the "Upcoming Changes" section.
- If present, extract and summarize the content beneath it; if not, leave the output blank.

Notes:
- Ensure that the summaries capture all updates without missing any.
- Validate that the date formats are consistent and correctly formatted.
- If there are fewer than ten entries, only include those available.
""".strip()  # noqa


class Category(str, Enum):
    BREAKING_CHANGES = "BREAKING_CHANGES"
    NEW_FEATURES = "NEW_FEATURES"
    DEPRECATIONS = "DEPRECATIONS"
    BUG_FIXES = "BUG_FIXES"
    PERFORMANCE_IMPROVEMENTS = "PERFORMANCE_IMPROVEMENTS"
    SECURITY_UPDATES = "SECURITY_UPDATES"


class Changelog(BaseModel):
    date: str
    markdown_content: str
    keywords: list[str]
    categories: list[Category]

    def pritty_repr(self) -> str:
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

    def pritty_repr(self) -> str:
        s = self.markdown_content + "\n"
        if self.categories:
            s += f"Categories: {', '.join(self.categories)}\n"
        return s


class ChangelogList(BaseModel):
    items: list[Changelog]
    upcoming_changes: list[UpcomingChange]

    def pritty_repr(self, name: str | None, url: str | None = None) -> str:
        s = ""
        if name and url:
            s += f"# [{name}]({url})\n"

        if self.upcoming_changes:
            s += "*Upcoming Changes*\n"
            for upcoming_change in self.upcoming_changes:
                s += upcoming_change.pritty_repr()

        for changelog in self.items:
            s += changelog.pritty_repr()

        return s


def select_recent_changelogs(changelog_list: ChangelogList, num_days: int) -> ChangelogList:
    new_changelog_list: ChangelogList = ChangelogList(items=[], upcoming_changes=changelog_list.upcoming_changes)
    for item in changelog_list.items:
        try:
            item_date = datetime.strptime(item.date, "%Y-%m-%d").date()
        except ValueError as e:
            logger.warning("unable to parse date: {} got error: {}", item.date, e)
            continue
        if item_date >= date.today() - timedelta(days=num_days):
            new_changelog_list.items.append(item)
    return new_changelog_list


def extract_changelog(text: str) -> ChangelogList | None:
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
            response_format=ChangelogList,
        )
    except Exception as e:
        logger.error("unable to parse the changelog: {}", e)
        return None
