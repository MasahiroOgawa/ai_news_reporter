"""Email (SMTP) delivery method."""

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from ..core.exceptions import DeliveryError
from ..models.report import Report
from .base import BaseDelivery


class EmailDelivery(BaseDelivery):
    """Delivers reports via email using SMTP."""

    def __init__(
        self,
        host: str,
        port: int,
        user: str,
        password: str,
        recipients: list[str],
        subject_prefix: str = "[AI News Weekly]",
    ):
        """Initialize email delivery.

        Args:
            host: SMTP server host.
            port: SMTP server port.
            user: SMTP username.
            password: SMTP password.
            recipients: List of email recipients.
            subject_prefix: Prefix for email subject.
        """
        self._host = host
        self._port = port
        self._user = user
        self._password = password
        self._recipients = recipients
        self._subject_prefix = subject_prefix

    @property
    def name(self) -> str:
        return "Email"

    async def deliver(self, report: Report) -> bool:
        """Send report via email.

        Args:
            report: Report to send.

        Returns:
            True if email was sent successfully.
        """
        if not self._recipients:
            raise DeliveryError("No email recipients configured")

        if not self._user or not self._password:
            raise DeliveryError("SMTP credentials not configured")

        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = f"{self._subject_prefix} {report.title} - {report.date}"
            msg["From"] = self._user
            msg["To"] = ", ".join(self._recipients)

            # Attach plain text version
            msg.attach(MIMEText(report.content_text, "plain", "utf-8"))

            # Attach HTML version
            msg.attach(MIMEText(report.content_html, "html", "utf-8"))

            with smtplib.SMTP(self._host, self._port) as server:
                server.starttls()
                server.login(self._user, self._password)
                server.send_message(msg)

            return True

        except smtplib.SMTPException as e:
            raise DeliveryError(f"Failed to send email: {e}") from e
