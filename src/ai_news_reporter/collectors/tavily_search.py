"""Tavily API collector for news search."""

from datetime import datetime

from tavily import TavilyClient

from ..core.exceptions import CollectorError
from ..models.article import Article
from .base import BaseCollector


class TavilyCollector(BaseCollector):
    """Collector that uses Tavily API for news search."""

    def __init__(self, api_key: str):
        """Initialize Tavily collector.

        Args:
            api_key: Tavily API key.
        """
        if not api_key:
            raise CollectorError("Tavily API key is required")
        self._client = TavilyClient(api_key=api_key)

    @property
    def name(self) -> str:
        return "Tavily Search"

    async def collect(
        self,
        query: str,
        time_range: str = "week",
        max_results: int = 10,
        include_domains: list[str] | None = None,
        exclude_domains: list[str] | None = None,
        **kwargs,
    ) -> list[Article]:
        """Search for news articles using Tavily API.

        Args:
            query: Search query.
            time_range: Time range for search (day, week, month, year).
            max_results: Maximum number of results.
            include_domains: Only include results from these domains.
            exclude_domains: Exclude results from these domains.

        Returns:
            List of articles found.
        """
        try:
            # Tavily search is synchronous, but we wrap it for async interface
            response = self._client.search(
                query=query,
                topic="news",
                days=self._time_range_to_days(time_range),
                max_results=max_results,
                include_domains=include_domains or [],
                exclude_domains=exclude_domains or [],
                include_images=True,
            )

            articles = []
            for result in response.get("results", []):
                # Extract image URL from result
                image_url = None
                if result.get("images"):
                    image_url = result["images"][0] if result["images"] else None
                elif result.get("image"):
                    image_url = result["image"]

                article = Article(
                    title=result.get("title", "Untitled"),
                    url=result.get("url"),
                    content=result.get("content", ""),
                    source="Tavily Search",
                    image_url=image_url,
                    published_at=self._parse_date(result.get("published_date")),
                    collected_at=datetime.now(),
                    keywords=[query],
                    score=result.get("score"),
                )
                articles.append(article)

            return articles

        except Exception as e:
            raise CollectorError(f"Tavily search failed: {e}") from e

    def _time_range_to_days(self, time_range: str) -> int:
        """Convert time range string to days."""
        mapping = {
            "day": 1,
            "week": 7,
            "month": 30,
            "year": 365,
        }
        return mapping.get(time_range, 7)

    def _parse_date(self, date_str: str | None) -> datetime | None:
        """Parse date string to datetime."""
        if not date_str:
            return None
        try:
            return datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        except ValueError:
            return None
