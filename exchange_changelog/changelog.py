from datetime import date
from datetime import datetime
from datetime import timedelta
from enum import Enum

from loguru import logger
from pydantic import BaseModel

from .llm.openai import parse_completion

SYSTEM_PROMPT = r"""
從變更日誌或發行說明頁面中根據日期抽取前五個變更或發行說明。
如果標題 "Upcoming Changes" 存在，則抽取 upcoming changes 並總結其內容；否則，將輸出留空。

指南:
- 僅使用提供的上下文中的信息；避免使用佔位符或通用示例。
- 將日期格式標準化並驗證為 'YYYY-MM-DD'（例如，將 '2024-Sep-20' 轉換為 '2024-09-20'）。
- 如果某個日期沒有變更或發佈說明，則跳過該日期的提取。
- 以 Markdown 格式呈現結果。
- 真實示例應包含更精細的變更細節和多樣化的關鍵字。
- 日期應該是實際的日期，而不是示例中的日期。

步驟:
- 提取所有按日期組織的條目，確保獲得前五個日期的記錄。
- 如果日期尚未是 'YYYY-MM-DD' 格式，則進行轉換。
- 對於每個條目，提取日期、變更摘要、關鍵字和類別。
- 查詢標題為 "Upcoming Changes" 的部分，如果存在，提取摘要和類別；否則，將此部分的輸出設為空白。

輸出值:
針對相對應的 key，抽取對應的 value。
- "date": 格式為 "YYYY-MM-DD" 的字符
- "markdown_content": 以項目符號列表形式包含變更細節的字符串
- "keywords": 與每個變更條目（不包括類別）相關的關鍵字數組
- "categories": 指示與更新相關的類別的字符串數組（例如，BREAKING_CHANGES、NEW_FEATURES、BUG_FIXES、DEPRECATIONS、PERFORMANCE_IMPROVEMENTS、SECURITY_UPDATES）
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


class Changelog(BaseModel):
    changes: list[Change]
    upcoming_changes: list[UpcomingChange]

    def pritty_repr(self, name: str | None, url: str | None = None) -> str:
        s = ""
        if name and url:
            s += f"# [{name}]({url})\n"

        if self.upcoming_changes:
            s += "*Upcoming Changes*\n"
            for upcoming_change in self.upcoming_changes:
                s += upcoming_change.pritty_repr()

        for changelog in self.changes:
            s += changelog.pritty_repr()

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


def extract_changelog(text: str) -> Changelog:
    # https://platform.openai.com/docs/guides/structured-outputs
    return parse_completion(
        messages=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT,
            },
            {
                "role": "user",
                "content": f'Input:\n"""\n{text}\n"""\n',
            },
        ],
        response_format=Changelog,
    )
