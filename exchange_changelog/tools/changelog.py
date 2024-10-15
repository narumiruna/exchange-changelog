from datetime import date
from datetime import datetime
from datetime import timedelta
from enum import Enum

from loguru import logger
from pydantic import BaseModel

from ..llm.openai import parse_completion

SYSTEM_PROMPT = r"""
Extract and summarize the first ten sets of changelog or release notes according to their dates.
Extract and summarize upcoming changes. If the main heading "Upcoming Changes" is present, extract and summarize the content beneath it; if not, leave the output blank.

For MAX Exchange, ensure to include relevant details from the changelog and release notes that highlight significant updates, improvements, or changes in functionality.

**Guidelines:**
- Ensure the output adheres to the specified JSON schema.
- Use only information directly from the provided context; avoid placeholder or generic examples.
- Standardize and validate date formats to 'YYYY-MM-DD' (e.g., convert '2024-Sep-20' to '2024-09-20').
- If no changelog or release note is available for a given date, skip the extraction for that date.
- Present the results in Markdown format.

# Output Format

The resulting output should be formatted as a JSON object containing:
- an array of objects, each including:
  - `date`: a string in 'YYYY-MM-DD' format
  - `markdown_content`: a string summarizing the changelog details in a bullet-point list
  - `keywords`: an array of keywords related to each changelog entry (excluding categories)
  - `categories`: an array of strings indicating the categories associated with the update (e.g., BREAKING_CHANGES, NEW_FEATURES, BUG_FIXES, DEPRECATIONS, PERFORMANCE_IMPROVEMENTS, SECURITY_UPDATES)

# Examples

**Input:**
```plaintext
2024-09-20
- Added user authentication features.
- Improved dashboard performance.

2024-09-18:
- Fixed bug in payment processing.
```

**Output:** 
```json
{
  "items": [
    {
      "date": "2024-09-20",
      "markdown_content": "- Added user authentication features.\n- Improved dashboard performance.",
      "keywords": ["authentication", "dashboard", "performance"],
      "categories": ["NEW_FEATURES", "PERFORMANCE_IMPROVEMENTS"]
    },
    {
      "date": "2024-09-18",
      "markdown_content": "- Fixed bug in payment processing.",
      "keywords": ["payment processing"],
      "categories": ["BUG_FIXES"]
    }
  ],
  "upcoming_changes": []
}
```

(NOTE: Real examples should contain more elaborate changelog details and diverse keywords.)
"""  # noqa


class Category(str, Enum):
    BREAKING_CHANGES = "BREAKING_CHANGES"
    NEW_FEATURES = "NEW_FEATURES"
    DEPRECATIONS = "DEPRECATIONS"
    BUG_FIXES = "BUG_FIXES"
    PERFORMANCE_IMPROVEMENTS = "PERFORMANCE_IMPROVEMENTS"
    SECURITY_UPDATES = "SECURITY_UPDATES"


class ChangeLog(BaseModel):
    date: str
    markdown_content: str
    keywords: list[str]
    categories: list[Category]


class UpcomingChange(BaseModel):
    markdown_content: str
    categories: list[Category]


class ChangeLogList(BaseModel):
    items: list[ChangeLog]
    upcoming_changes: list[UpcomingChange]

    def pritty_repr(self) -> str:
        result = []

        if self.upcoming_changes:
            result.append("## Upcoming Changes")
            for upcoming_change in self.upcoming_changes:
                result.append(upcoming_change.markdown_content)

                if upcoming_change.categories:
                    result.append(f"Categories: {', '.join(upcoming_change.categories)}")

        prev_date = None
        for changelog in self.items:
            if prev_date != changelog.date:
                prev_date = changelog.date
                result.append(f"## {changelog.date}")
            result.append(changelog.markdown_content)

            if changelog.keywords:
                result.append(f"Keywords: {', '.join(changelog.keywords)}")

            if changelog.categories:
                result.append(f"Categories: {', '.join(changelog.categories)}")

        return "\n\n".join(result)


def select_recent_changelogs(changelog_list: ChangeLogList, num_days: int) -> ChangeLogList:
    new_changelog_list: ChangeLogList = ChangeLogList(items=[], upcoming_changes=changelog_list.upcoming_changes)
    for item in changelog_list.items:
        try:
            item_date = datetime.strptime(item.date, "%Y-%m-%d").date()
        except ValueError as e:
            logger.warning("unable to parse date: {} got error: {}", item.date, e)
            continue
        if item_date >= date.today() - timedelta(days=num_days):
            new_changelog_list.items.append(item)
    return new_changelog_list


def extract_changelog(text: str) -> ChangeLogList | None:
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
            response_format=ChangeLogList,
        )
    except Exception as e:
        logger.error("unable to parse the changelog: {}", e)
        return None
