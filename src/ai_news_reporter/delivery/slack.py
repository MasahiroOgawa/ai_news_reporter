"""Slack webhook delivery method."""

import httpx

from ..core.exceptions import DeliveryError
from ..models.report import Report
from .base import BaseDelivery


class SlackDelivery(BaseDelivery):
    """Delivers reports to Slack via webhook."""

    def __init__(self, webhook_url: str):
        """Initialize Slack delivery.

        Args:
            webhook_url: Slack incoming webhook URL.
        """
        if not webhook_url:
            raise DeliveryError("Slack webhook URL is required")
        self._webhook_url = webhook_url

    @property
    def name(self) -> str:
        return "Slack"

    async def deliver(self, report: Report) -> bool:
        """Send report to Slack.

        Args:
            report: Report to send.

        Returns:
            True if message was sent successfully.
        """
        blocks = self._format_blocks(report)
        payload = {
            "text": f"{report.title} - {report.date}",
            "blocks": blocks,
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self._webhook_url,
                    json=payload,
                    timeout=30,
                )
                response.raise_for_status()
                return True

        except httpx.HTTPError as e:
            raise DeliveryError(f"Failed to send Slack message: {e}") from e

    def _format_blocks(self, report: Report) -> list[dict]:
        """Format report as Slack blocks.

        Args:
            report: Report to format.

        Returns:
            List of Slack block elements.
        """
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"{report.title}",
                    "emoji": True,
                },
            },
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": f"*Date:* {report.date} | *Articles:* {report.article_count}",
                    }
                ],
            },
            {"type": "divider"},
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": self._truncate_text(report.summary, 2900),
                },
            },
            {"type": "divider"},
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*Top Sources:*\n"
                    + "\n".join(
                        f"• <{a.url}|{self._truncate_text(a.title, 50)}>"
                        for a in report.articles[:5]
                    ),
                },
            },
        ]

        return blocks

    def _truncate_text(self, text: str, max_length: int) -> str:
        """Truncate text to maximum length.

        Args:
            text: Text to truncate.
            max_length: Maximum length.

        Returns:
            Truncated text.
        """
        if len(text) <= max_length:
            return text
        return text[: max_length - 3] + "..."
