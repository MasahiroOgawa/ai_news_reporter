"""Abstract base class for data collectors."""

from abc import ABC, abstractmethod

from ..models.article import Article


class BaseCollector(ABC):
    """Abstract base class for all data collectors."""

    @abstractmethod
    async def collect(self, query: str, **kwargs) -> list[Article]:
        """Collect articles based on query.

        Args:
            query: Search query or URL to collect from.
            **kwargs: Additional parameters specific to the collector.

        Returns:
            List of collected articles.
        """
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """Get the collector name."""
        pass
