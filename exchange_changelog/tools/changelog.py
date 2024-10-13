from datetime import date
from datetime import datetime
from datetime import timedelta

from loguru import logger
from pydantic import BaseModel

from .llm import parse_completion

SYSTEM_PROMPT = r"""
Extract and summarize the first ten sets of ChangeLogs or Release Notes according to their dates.

For MAX Exchange, ensure to include relevant details from the changelog and release notes that highlight significant updates, improvements, or changes in functionality.

**Guidelines:**
- Ensure the output adheres to the specified JSON schema.
- Use only information directly from the provided context; avoid placeholder or generic examples.
- Exclude upcoming changes that do not have explicit dates.
- Standardize and validate date formats to 'YYYY-MM-DD' (e.g., convert '2024-Sep-20' to '2024-09-20').
- If no changelog or release note is available for a given date, skip the extraction for that date.
- Present the results in Markdown format.

# Output Format

The resulting output should be formatted as a JSON object containing:
- an array of objects, each including:
  - `date`: a string in 'YYYY-MM-DD' format
  - `markdown_content`: a string summarizing the changelog details in a bullet-point list
  - `keywords`: an array of keywords related to each changelog entry

# Examples

**Input:** "Changelog dated 2024-Sep-20: - Added user authentication features. - Improved dashboard performance. Changelog dated 2024-Sep-18: - Fixed bug in payment processing."  
**Output:** 
```json
{
  "items": [
    {
      "date": "2024-09-20",
      "markdown_content": "- Added user authentication features.\n- Improved dashboard performance.",
      "keywords": ["authentication", "dashboard", "performance"]
    },
    {
      "date": "2024-09-18",
      "markdown_content": "- Fixed bug in payment processing.",
      "keywords": ["bug fix", "payment processing"]
    }
  ]
}
```

(NOTE: Real examples should contain more elaborate changelog details and diverse keywords.)
"""  # noqa


class ChangeLog(BaseModel):
    date: str
    markdown_content: str
    keywords: list[str]


class ChangeLogList(BaseModel):
    items: list[ChangeLog]

    def pritty_repr(self) -> str:
        result = []

        prev_date = None
        for changelog in self.items:
            if prev_date != changelog.date:
                prev_date = changelog.date
                result.append(f"## {changelog.date}")
            result.append(changelog.markdown_content)

            if changelog.keywords:
                result.append(f"Keywords: {', '.join(changelog.keywords)}")

        return "\n\n".join(result)


def select_recent_changelogs(changelog_list: ChangeLogList, num_days: int) -> ChangeLogList:
    new_changelog_list: ChangeLogList = ChangeLogList(items=[])
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
