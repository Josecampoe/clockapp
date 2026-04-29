"""AlarmModel: single alarm with snooze and auto-dismiss support."""

import logging
from datetime import datetime, timedelta
from typing import Optional

from src.models.clock import BaseModel

logger = logging.getLogger(__name__)

_SNOOZE_MINUTES = 5
_AUTO_STOP_SECONDS = 60          # silence alarm after this many seconds


class AlarmModel(BaseModel):
    """Stores alarm configuration and determines when it should fire.

    Improvements over the original:
    - Snooze: delays the alarm by ``_SNOOZE_MINUTES`` minutes.
    - Auto-stop: the alarm silences itself after ``_AUTO_STOP_SECONDS``.
    - Robust trigger guard: uses a full ``datetime`` stamp instead of a
      minute-ID so the alarm cannot re-fire if the app is suspended.

    Attributes:
        _hour:              Alarm hour (0–23).
        _minute:            Alarm minute (0–59).
        _enabled:           Whether the alarm is active.
        _triggered:         True while the alarm is ringing.
        _trigger_stamp:     ``datetime`` of the most recent trigger.
        _snooze_until:      ``datetime`` after which the alarm may re-fire,
                            or ``None`` when snooze is not active.
        _fire_time:         ``datetime`` of the next scheduled fire, or
                            ``None`` when the alarm is disabled.
    """

    def __init__(self) -> None:
        super().__init__()
        self._hour: int = 7
        self._minute: int = 0
        self._enabled: bool = False
        self._triggered: bool = False
        self._trigger_stamp: Optional[datetime] = None
        self._snooze_until: Optional[datetime] = None
        logger.debug("AlarmModel initialised.")

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def hour(self) -> int:
        return self._hour

    @hour.setter
    def hour(self, value: int) -> None:
        if not 0 <= value <= 23:
            raise ValueError(f"Alarm hour must be 0–23, got {value}.")
        self._hour = value
        self._reset_trigger()
        self._notify()

    @property
    def minute(self) -> int:
        return self._minute

    @minute.setter
    def minute(self, value: int) -> None:
        if not 0 <= value <= 59:
            raise ValueError(f"Alarm minute must be 0–59, got {value}.")
        self._minute = value
        self._reset_trigger()
        self._notify()

    @property
    def enabled(self) -> bool:
        return self._enabled

    @enabled.setter
    def enabled(self, value: bool) -> None:
        self._enabled = value
        if not value:
            self._triggered = False
            self._snooze_until = None
        logger.info("Alarm %s.", "enabled" if value else "disabled")
        self._notify()

    @property
    def triggered(self) -> bool:
        """True while the alarm is actively ringing."""
        return self._triggered

    @property
    def snooze_active(self) -> bool:
        """True when the alarm is snoozed and waiting to re-fire."""
        return self._snooze_until is not None

    # ------------------------------------------------------------------
    # Tick
    # ------------------------------------------------------------------

    def update(self) -> None:
        """Check whether the alarm should fire or auto-stop."""
        if not self._enabled:
            return

        now = datetime.now()

        # Auto-stop after _AUTO_STOP_SECONDS
        if self._triggered and self._trigger_stamp is not None:
            elapsed = (now - self._trigger_stamp).total_seconds()
            if elapsed >= _AUTO_STOP_SECONDS:
                logger.info("Alarm auto-stopped after %ds.", _AUTO_STOP_SECONDS)
                self.acknowledge()
                return

        if self._triggered:
            return   # already ringing; wait for dismiss/snooze

        # Snooze guard
        if self._snooze_until is not None and now < self._snooze_until:
            return

        # Fire condition: same hour:minute, not already fired this minute
        if now.hour == self._hour and now.minute == self._minute:
            if self._trigger_stamp is None or (
                now - self._trigger_stamp
            ).total_seconds() >= 60:
                self._triggered = True
                self._trigger_stamp = now
                self._snooze_until = None
                logger.info("Alarm fired at %02d:%02d.", self._hour, self._minute)
                self._notify()

    # ------------------------------------------------------------------
    # Actions
    # ------------------------------------------------------------------

    def acknowledge(self) -> None:
        """Dismiss the alarm (stop ringing, keep enabled for tomorrow)."""
        self._triggered = False
        self._snooze_until = None
        logger.debug("Alarm acknowledged.")
        self._notify()

    def snooze(self) -> None:
        """Snooze the alarm for ``_SNOOZE_MINUTES`` minutes."""
        self._triggered = False
        self._snooze_until = datetime.now() + timedelta(minutes=_SNOOZE_MINUTES)
        logger.info("Alarm snoozed until %s.", self._snooze_until.strftime("%H:%M"))
        self._notify()

    def set_time(self, hour: int, minute: int) -> None:
        """Set both alarm hour and minute atomically.

        Args:
            hour:   0–23.
            minute: 0–59.

        Raises:
            ValueError: If either value is out of range.
        """
        if not 0 <= hour <= 23:
            raise ValueError(f"Alarm hour must be 0–23, got {hour}.")
        if not 0 <= minute <= 59:
            raise ValueError(f"Alarm minute must be 0–59, got {minute}.")
        self._hour = hour
        self._minute = minute
        self._reset_trigger()
        logger.debug("Alarm time set to %02d:%02d.", hour, minute)
        self._notify()

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _reset_trigger(self) -> None:
        self._triggered = False
        self._trigger_stamp = None
        self._snooze_until = None

    def format_time(self) -> str:
        """Return the alarm time as ``HH:MM``."""
        return f"{self._hour:02d}:{self._minute:02d}"

    def format_snooze_until(self) -> str:
        """Return the snooze-until time as ``HH:MM``, or empty string."""
        if self._snooze_until is None:
            return ""
        return self._snooze_until.strftime("%H:%M")
