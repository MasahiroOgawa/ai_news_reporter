"""Article data model."""

from datetime import datetime

from pydantic import BaseModel, HttpUrl


class Article(BaseModel):
    """Represents a collected news article."""

    title: str
    url: HttpUrl
    content: str
    summary: str | None = None
    source: str
    image_url: str | None = None
    published_at: datetime | None = None
    collected_at: datetime = datetime.now()
    keywords: list[str] = []
    score: float | None = None

    def __hash__(self) -> int:
        """Hash based on URL for deduplication."""
        return hash(str(self.url))

    def __eq__(self, other: object) -> bool:
        """Equality based on URL."""
        if not isinstance(other, Article):
            return False
        return str(self.url) == str(other.url)
