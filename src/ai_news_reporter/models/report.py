"""Report data model."""

from datetime import date

from pydantic import BaseModel

from .article import Article


class Report(BaseModel):
    """Represents a generated news report."""

    title: str
    date: date
    articles: list[Article]
    summary: str
    content_markdown: str
    content_html: str = ""
    content_text: str = ""
    recipients: list[str] = []

    @property
    def article_count(self) -> int:
        """Get number of articles in report."""
        return len(self.articles)
