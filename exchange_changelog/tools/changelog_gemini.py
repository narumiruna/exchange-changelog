from __future__ import annotations

from typing import TypedDict

from ..llm.gemini import generate_content
from .changelog import ChangeLogList

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
      "keywords": ["bug fix", "payment processing"],
      "categories": ["BUG_FIXES"]
    }
  ]
}
```

(NOTE: Real examples should contain more elaborate changelog details and diverse keywords.)
"""  # noqa


class ChangeLogDict(TypedDict):
    date: str
    markdown_content: str
    keywords: list[str]

    def pritty_repr(self) -> str:
        result = []

        prev_date = None
        for changelog in self.items:
            if prev_date != changelog["date"]:
                prev_date = changelog["date"]
                result.append(f"## {changelog["date"]}")
            result.append(changelog["markdown_content"])

            if changelog["keywords"]:
                result.append(f"Keywords: {', '.join(changelog["keywords"])}")

        return "\n\n".join(result)


class ChangeLogListDict(TypedDict):
    items: list[ChangeLogDict]


def extract_changelog(text: str) -> ChangeLogList:
    d = generate_content(
        contents=[
            SYSTEM_PROMPT,
            "Input: " + text,
        ],
        response_schema=ChangeLogListDict,
    )

    return ChangeLogList.model_validate(d)
