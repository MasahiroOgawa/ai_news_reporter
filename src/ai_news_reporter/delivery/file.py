"""File output delivery method."""

import json
from pathlib import Path

from ..core.exceptions import DeliveryError
from ..models.report import Report
from .base import BaseDelivery


class FileDelivery(BaseDelivery):
    """Delivers reports as files (markdown, HTML, JSON)."""

    def __init__(
        self,
        output_dir: Path | str,
        formats: list[str] | None = None,
    ):
        """Initialize file delivery.

        Args:
            output_dir: Directory to save reports.
            formats: List of output formats (markdown, html, json).
        """
        self._output_dir = Path(output_dir)
        self._formats = formats or ["markdown"]
        self._output_dir.mkdir(parents=True, exist_ok=True)

    @property
    def name(self) -> str:
        return "File"

    async def deliver(self, report: Report) -> bool:
        """Save report to files.

        Args:
            report: Report to save.

        Returns:
            True if all files were saved successfully.
        """
        date_str = report.date.strftime("%Y%m%d")
        success = True

        for fmt in self._formats:
            try:
                if fmt == "markdown":
                    filepath = self._output_dir / f"report_{date_str}.md"
                    filepath.write_text(report.content_markdown, encoding="utf-8")
                elif fmt == "html":
                    filepath = self._output_dir / f"report_{date_str}.html"
                    filepath.write_text(report.content_html, encoding="utf-8")
                elif fmt == "json":
                    filepath = self._output_dir / f"report_{date_str}.json"
                    data = {
                        "title": report.title,
                        "date": report.date.isoformat(),
                        "summary": report.summary,
                        "article_count": report.article_count,
                        "articles": [
                            {
                                "title": a.title,
                                "url": str(a.url),
                                "source": a.source,
                                "published_at": (
                                    a.published_at.isoformat() if a.published_at else None
                                ),
                            }
                            for a in report.articles
                        ],
                    }
                    filepath.write_text(
                        json.dumps(data, indent=2, ensure_ascii=False),
                        encoding="utf-8",
                    )
                else:
                    continue

            except OSError as e:
                raise DeliveryError(f"Failed to write {fmt} file: {e}") from e

        return success

    @property
    def output_dir(self) -> Path:
        """Get the output directory."""
        return self._output_dir
