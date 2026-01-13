"""Slack Bot delivery method for sending DMs to users."""

import httpx

from ..core.exceptions import DeliveryError
from ..models.report import Report
from .base import BaseDelivery


class SlackDelivery(BaseDelivery):
    """Delivers reports to Slack users via Bot DM."""

    SLACK_API_URL = "https://slack.com/api/chat.postMessage"

    def __init__(self, bot_token: str, user_ids: list[str]):
        """Initialize Slack Bot delivery.

        Args:
            bot_token: Slack Bot OAuth token (xoxb-...).
            user_ids: List of Slack user IDs to send DMs to.
        """
        if not bot_token:
            raise DeliveryError("Slack Bot token is required")
        if not user_ids:
            raise DeliveryError("At least one Slack user ID is required")

        self._bot_token = bot_token
        self._user_ids = user_ids

    @property
    def name(self) -> str:
        return "Slack"

    async def deliver(self, report: Report) -> bool:
        """Send report to Slack users via DM.

        Args:
            report: Report to send.

        Returns:
            True if messages were sent successfully.
        """
        blocks = self._format_blocks(report)
        headers = {
            "Authorization": f"Bearer {self._bot_token}",
            "Content-Type": "application/json",
        }

        success_count = 0
        errors = []

        async with httpx.AsyncClient() as client:
            for user_id in self._user_ids:
                payload = {
                    "channel": user_id,  # User ID for DM
                    "text": f"{report.title} - {report.date}",
                    "blocks": blocks,
                }

                try:
                    response = await client.post(
                        self.SLACK_API_URL,
                        headers=headers,
                        json=payload,
                        timeout=30,
                    )
                    data = response.json()

                    if data.get("ok"):
                        success_count += 1
                    else:
                        errors.append(f"{user_id}: {data.get('error', 'Unknown error')}")

                except httpx.HTTPError as e:
                    errors.append(f"{user_id}: {e}")

        if errors:
            error_msg = "; ".join(errors)
            if success_count == 0:
                raise DeliveryError(f"Failed to send Slack DMs: {error_msg}")
            # Partial success - log warning but don't fail
            print(f"Warning: Some Slack DMs failed: {error_msg}")

        return success_count > 0

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
                    "text": "*Top Sources:*",
                },
            },
        ]

        # Add top articles with images
        for article in report.articles[:5]:
            if article.image_url:
                blocks.append(
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": f"*<{article.url}|{self._truncate_text(article.title, 100)}>*\n_{article.source}_",
                        },
                        "accessory": {
                            "type": "image",
                            "image_url": article.image_url,
                            "alt_text": article.title,
                        },
                    }
                )
            else:
                blocks.append(
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": f"• *<{article.url}|{self._truncate_text(article.title, 100)}>* - _{article.source}_",
                        },
                    }
                )

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
