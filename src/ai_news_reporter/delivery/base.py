"""Abstract base class for delivery methods."""

from abc import ABC, abstractmethod

from ..models.report import Report


class BaseDelivery(ABC):
    """Abstract base class for report delivery."""

    @abstractmethod
    async def deliver(self, report: Report) -> bool:
        """Deliver a report.

        Args:
            report: Report to deliver.

        Returns:
            True if delivery was successful.
        """
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """Get the delivery method name."""
        pass
