"""Article deduplication processor."""

from difflib import SequenceMatcher

from ..models.article import Article


class Deduplicator:
    """Removes duplicate articles based on URL and title similarity."""

    def __init__(self, title_similarity_threshold: float = 0.8):
        """Initialize deduplicator.

        Args:
            title_similarity_threshold: Minimum similarity ratio for titles
                to be considered duplicates (0.0 to 1.0).
        """
        self._threshold = title_similarity_threshold

    def deduplicate(self, articles: list[Article]) -> list[Article]:
        """Remove duplicate articles.

        Deduplication is based on:
        1. Exact URL match
        2. High title similarity

        Args:
            articles: List of articles to deduplicate.

        Returns:
            List of unique articles.
        """
        if not articles:
            return []

        seen_urls: set[str] = set()
        seen_titles: list[str] = []
        unique_articles: list[Article] = []

        for article in articles:
            url_str = str(article.url)

            # Check exact URL match
            if url_str in seen_urls:
                continue

            # Check title similarity
            if self._is_similar_to_existing(article.title, seen_titles):
                continue

            # Article is unique
            seen_urls.add(url_str)
            seen_titles.append(article.title)
            unique_articles.append(article)

        return unique_articles

    def _is_similar_to_existing(self, title: str, existing_titles: list[str]) -> bool:
        """Check if title is similar to any existing title.

        Args:
            title: Title to check.
            existing_titles: List of existing titles.

        Returns:
            True if title is similar to an existing one.
        """
        title_lower = title.lower()
        for existing in existing_titles:
            ratio = SequenceMatcher(None, title_lower, existing.lower()).ratio()
            if ratio >= self._threshold:
                return True
        return False
