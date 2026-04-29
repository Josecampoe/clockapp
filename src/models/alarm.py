"""AlarmModel: manages alarm state and trigger logic."""

import logging
from datetime import datetime
from typing import Optional

from src.models.clock import BaseModel

logger = logging.getLogger(__name__)


class AlarmModel(BaseModel):
    """Stores alarm configuration and determines when it should fire.

    Attributes:
        _hour: Alarm hour (0–23).
        _minute: Alarm minute (0–59).
        _enabled: Whether the alarm is active.
        _triggered: Whether the alarm has fired in the current minute.
        _last_trigger_minute: Tracks the last minute the alarm fired to
            prevent repeated triggers within the same minute.
    """

    def __init__(self) -> None:
        """Initialise AlarmModel with default values (disabled)."""
        super().__init__()
        self._hour: int = 7
        self._minute: int = 0
        self._enabled: bool = False
        self._triggered: bool = False
        self._last_trigger_minute: Optional[int] = None
        logger.debug("AlarmModel initialised.")

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def hour(self) -> int:
        """Return the alarm hour (0–23)."""
        return self._hour

    @hour.setter
    def hour(self, value: int) -> None:
        """Set the alarm hour.

        Args:
            value: Hour value between 0 and 23.

        Raises:
            ValueError: If value is outside [0, 23].
        """
        if not 0 <= value <= 23:
            raise ValueError(f"Alarm hour must be 0–23, got {value}.")
        self._hour = value
        self._triggered = False
        self._last_trigger_minute = None
        self._notify()

    @property
    def minute(self) -> int:
        """Return the alarm minute (0–59)."""
        return self._minute

    @minute.setter
    def minute(self, value: int) -> None:
        """Set the alarm minute.

        Args:
            value: Minute value between 0 and 59.

        Raises:
            ValueError: If value is outside [0, 59].
        """
        if not 0 <= value <= 59:
            raise ValueError(f"Alarm minute must be 0–59, got {value}.")
        self._minute = value
        self._triggered = False
        self._last_trigger_minute = None
        self._notify()

    @property
    def enabled(self) -> bool:
        """Return True if the alarm is enabled."""
        return self._enabled

    @enabled.setter
    def enabled(self, value: bool) -> None:
        """Enable or disable the alarm.

        Args:
            value: True to enable, False to disable.
        """
        self._enabled = value
        if not value:
            self._triggered = False
            self._last_trigger_minute = None
        logger.info("Alarm %s.", "enabled" if value else "disabled")
        self._notify()

    @property
    def triggered(self) -> bool:
        """Return True if the alarm has just fired."""
        return self._triggered

    # ------------------------------------------------------------------
    # Public methods
    # ------------------------------------------------------------------

    def update(self) -> None:
        """Check whether the alarm should fire right now."""
        if not self._enabled:
            return

        now = datetime.now()
        current_minute_id = now.hour * 60 + now.minute

        if (
            now.hour == self._hour
            and now.minute == self._minute
            and self._last_trigger_minute != current_minute_id
        ):
            self._triggered = True
            self._last_trigger_minute = current_minute_id
            logger.info("Alarm triggered at %02d:%02d.", self._hour, self._minute)
            self._notify()

    def acknowledge(self) -> None:
        """Acknowledge (dismiss) the alarm after it has fired."""
        self._triggered = False
        logger.debug("Alarm acknowledged.")
        self._notify()

    def set_time(self, hour: int, minute: int) -> None:
        """Set both alarm hour and minute atomically.

        Args:
            hour: Hour value between 0 and 23.
            minute: Minute value between 0 and 59.

        Raises:
            ValueError: If either value is out of range.
        """
        if not 0 <= hour <= 23:
            raise ValueError(f"Alarm hour must be 0–23, got {hour}.")
        if not 0 <= minute <= 59:
            raise ValueError(f"Alarm minute must be 0–59, got {minute}.")
        self._hour = hour
        self._minute = minute
        self._triggered = False
        self._last_trigger_minute = None
        logger.debug("Alarm time set to %02d:%02d.", hour, minute)
        self._notify()

    def format_time(self) -> str:
        """Return the alarm time as a formatted string.

        Returns:
            String in HH:MM format.
        """
        return f"{self._hour:02d}:{self._minute:02d}"
