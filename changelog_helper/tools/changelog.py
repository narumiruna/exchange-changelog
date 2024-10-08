from datetime import date

from ..chain import get_chain
from ..utils import ai_message_repr

PROMPT_TEMPLATE = r"""According to the article, list changelog from {from_date} to {to_date}.

Rules:
- If there is no changelog between {from_date} and {to_date}, please return an empty string.
- Convert 2024-Sep-20 to 2024-09-20.

Example:
2024-10-08
- Added feature A.
- Fixed bug B.

Article:
{article}

Changelog:
"""


def list_changelog(text: str, from_date: date, to_date: date) -> str:
    chain = get_chain(PROMPT_TEMPLATE)
    ai_message = chain.invoke(
        {
            "article": text,
            "from_date": from_date,
            "to_date": to_date,
        },
    )
    return ai_message_repr(ai_message)
