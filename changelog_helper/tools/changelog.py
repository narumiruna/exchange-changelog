from datetime import date

from ..chain import get_chain
from ..utils import ai_message_repr

PROMPT_TEMPLATE = r"""
Based on the extracted text, provide the changelog or release notes from {from_date} to {to_date}.

Rules:
- If no changelog is found between {from_date} and {to_date}, return an empty string.
- Convert dates formatted like '2024-Sep-20' to '2024-09-20'.
- Output the results in Markdown format.

Example:
- (2024-10-08) Added feature A.
- (2024-09-10) Fixed bug B.

Extracted Text:
{extracted_text}

Changelog:
"""


def list_changelog(text: str, from_date: date, to_date: date) -> str:
    chain = get_chain(PROMPT_TEMPLATE)
    ai_message = chain.invoke(
        {
            "extracted_text": text,
            "from_date": from_date,
            "to_date": to_date,
        },
    )
    return ai_message_repr(ai_message)
