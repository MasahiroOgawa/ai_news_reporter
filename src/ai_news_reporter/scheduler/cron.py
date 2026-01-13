"""Cron-style scheduling using APScheduler."""

import asyncio
from collections.abc import Callable
from typing import Any

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from ..core.config import ScheduleConfig


class ReportScheduler:
    """Manages scheduled report generation."""

    def __init__(self, timezone: str = "UTC"):
        """Initialize scheduler.

        Args:
            timezone: Timezone for scheduling.
        """
        self._scheduler = AsyncIOScheduler(timezone=timezone)
        self._timezone = timezone

    def schedule_from_config(
        self,
        config: ScheduleConfig,
        job_func: Callable[[], Any],
    ) -> None:
        """Schedule job based on configuration.

        Args:
            config: Schedule configuration.
            job_func: Function to execute.
        """
        if not config.enabled:
            return

        # Parse time
        hour, minute = self._parse_time(config.time)

        if config.type == "weekly":
            trigger = CronTrigger(
                day_of_week=self._day_to_number(config.day_of_week),
                hour=hour,
                minute=minute,
                timezone=config.timezone or self._timezone,
            )
        elif config.type == "daily":
            trigger = CronTrigger(
                hour=hour,
                minute=minute,
                timezone=config.timezone or self._timezone,
            )
        else:
            # Default to weekly
            trigger = CronTrigger(
                day_of_week=0,
                hour=hour,
                minute=minute,
                timezone=config.timezone or self._timezone,
            )

        self._scheduler.add_job(job_func, trigger, id="report_job")

    def schedule_weekly(
        self,
        job_func: Callable[[], Any],
        day_of_week: str = "monday",
        hour: int = 9,
        minute: int = 0,
    ) -> None:
        """Schedule a weekly job.

        Args:
            job_func: Function to execute.
            day_of_week: Day of week (monday, tuesday, etc.).
            hour: Hour to run (0-23).
            minute: Minute to run (0-59).
        """
        trigger = CronTrigger(
            day_of_week=self._day_to_number(day_of_week),
            hour=hour,
            minute=minute,
            timezone=self._timezone,
        )
        self._scheduler.add_job(job_func, trigger, id="weekly_report")

    def schedule_daily(
        self,
        job_func: Callable[[], Any],
        hour: int = 9,
        minute: int = 0,
    ) -> None:
        """Schedule a daily job.

        Args:
            job_func: Function to execute.
            hour: Hour to run (0-23).
            minute: Minute to run (0-59).
        """
        trigger = CronTrigger(
            hour=hour,
            minute=minute,
            timezone=self._timezone,
        )
        self._scheduler.add_job(job_func, trigger, id="daily_report")

    def start(self) -> None:
        """Start the scheduler."""
        self._scheduler.start()

    def stop(self) -> None:
        """Stop the scheduler."""
        self._scheduler.shutdown()

    def run_forever(self) -> None:
        """Run scheduler in blocking mode."""
        self.start()
        try:
            asyncio.get_event_loop().run_forever()
        except (KeyboardInterrupt, SystemExit):
            self.stop()

    def _day_to_number(self, day: str) -> int:
        """Convert day name to number.

        Args:
            day: Day name (monday, tuesday, etc.).

        Returns:
            Day number (0=Monday, 6=Sunday).
        """
        days = {
            "monday": 0,
            "tuesday": 1,
            "wednesday": 2,
            "thursday": 3,
            "friday": 4,
            "saturday": 5,
            "sunday": 6,
        }
        return days.get(day.lower(), 0)

    def _parse_time(self, time_str: str) -> tuple[int, int]:
        """Parse time string to hour and minute.

        Args:
            time_str: Time in HH:MM format.

        Returns:
            Tuple of (hour, minute).
        """
        parts = time_str.split(":")
        hour = int(parts[0]) if len(parts) > 0 else 9
        minute = int(parts[1]) if len(parts) > 1 else 0
        return hour, minute
