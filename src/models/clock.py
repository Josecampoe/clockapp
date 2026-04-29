"""ClockModel: current time, timezone support, and manual hand-drag offset."""

import logging
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import Callable, List, Tuple

import pytz

from src.utils.constants import TIMEZONE_LIST

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Base
# ---------------------------------------------------------------------------

class BaseModel(ABC):
    """Observer-pattern base for all domain models.

    Subclasses call ``_notify()`` whenever their state changes so that
    registered callbacks (views / controllers) can react.
    """

    def __init__(self) -> None:
        self._observers: List[Callable[[], None]] = []

    def subscribe(self, callback: Callable[[], None]) -> None:
        """Register *callback* to be called on every state change."""
        if callback not in self._observers:
            self._observers.append(callback)

    def unsubscribe(self, callback: Callable[[], None]) -> None:
        """Remove a previously registered *callback*."""
        if callback in self._observers:
            self._observers.remove(callback)

    def _notify(self) -> None:
        for cb in self._observers:
            try:
                cb()
            except Exception as exc:          # noqa: BLE001
                logger.error("Observer error: %s", exc)

    @abstractmethod
    def update(self) -> None:
        """Refresh internal state (called periodically by the controller)."""


# ---------------------------------------------------------------------------
# ClockModel
# ---------------------------------------------------------------------------

class ClockModel(BaseModel):
    """Tracks local time and an optional secondary timezone.

    Manual adjustment
    -----------------
    The user can drag clock hands to shift the displayed time.  Each drag
    call stores a ``timedelta`` offset that is added to ``datetime.now()``
    on every subsequent tick.  ``reset_offset()`` returns to wall-clock time.

    Attributes:
        _offset:             Accumulated manual time shift.
        _local_time:         Most-recently computed (offset-adjusted) datetime.
        _selected_timezone:  pytz timezone for the secondary display.
        _timezone_time:      Most-recently computed secondary-tz datetime.
    """

    def __init__(self) -> None:
        super().__init__()
        self._offset: timedelta = timedelta(0)
        self._local_time: datetime = datetime.now()
        self._selected_timezone: pytz.BaseTzInfo = pytz.utc
        self._timezone_time: datetime = datetime.now(tz=pytz.utc)
        logger.debug("ClockModel initialised.")

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def local_time(self) -> datetime:
        """Return the offset-adjusted local datetime."""
        return self._local_time

    @property
    def selected_timezone(self) -> pytz.BaseTzInfo:
        """Return the currently selected secondary timezone."""
        return self._selected_timezone

    @property
    def timezone_time(self) -> datetime:
        """Return the current time in the selected secondary timezone."""
        return self._timezone_time

    @property
    def has_manual_offset(self) -> bool:
        """Return True when a non-zero manual offset is active."""
        return self._offset != timedelta(0)

    # ------------------------------------------------------------------
    # Tick
    # ------------------------------------------------------------------

    def update(self) -> None:
        """Advance the clock by reading wall time + offset, then notify."""
        self._local_time    = datetime.now() + self._offset
        self._timezone_time = datetime.now(tz=self._selected_timezone) + self._offset
        self._notify()

    # ------------------------------------------------------------------
    # Manual hand-drag  (absolute-angle → new offset)
    # ------------------------------------------------------------------

    def set_time_from_hour_angle(self, angle_deg: float) -> None:
        """Shift the offset so the hour hand sits at *angle_deg*.

        The minute and second components of the current time are preserved.
        AM/PM is inferred from the current (offset-adjusted) time.

        Args:
            angle_deg: Desired hour-hand angle in degrees [0, 360) from
                       12 o'clock, clockwise.
        """
        now = datetime.now() + self._offset
        total_minutes = (angle_deg / 360.0) * 12 * 60   # 0 … 719
        new_hour = int(total_minutes // 60) % 12
        if now.hour >= 12:
            new_hour += 12
        try:
            target = now.replace(hour=new_hour)
        except ValueError:
            return
        self._offset    += target - now
        self._local_time = datetime.now() + self._offset
        self._notify()

    def set_time_from_minute_angle(self, angle_deg: float) -> None:
        """Shift the offset so the minute hand sits at *angle_deg*.

        Takes the shortest path (≤ 30 min) to avoid large jumps.

        Args:
            angle_deg: Desired minute-hand angle in degrees [0, 360).
        """
        now            = datetime.now() + self._offset
        new_minute     = (angle_deg / 360.0) * 60          # 0 … 59.99
        current_minute = now.minute + now.second / 60.0
        delta          = new_minute - current_minute
        if delta > 30:
            delta -= 60
        elif delta < -30:
            delta += 60
        self._offset    += timedelta(minutes=delta)
        self._local_time = datetime.now() + self._offset
        self._notify()

    def set_time_from_second_angle(self, angle_deg: float) -> None:
        """Shift the offset so the second hand sits at *angle_deg*.

        Takes the shortest path (≤ 30 s).

        Args:
            angle_deg: Desired second-hand angle in degrees [0, 360).
        """
        now            = datetime.now() + self._offset
        new_second     = (angle_deg / 360.0) * 60
        current_second = now.second + now.microsecond / 1_000_000
        delta          = new_second - current_second
        if delta > 30:
            delta -= 60
        elif delta < -30:
            delta += 60
        self._offset    += timedelta(seconds=delta)
        self._local_time = datetime.now() + self._offset
        self._notify()

    def reset_offset(self) -> None:
        """Clear the manual offset and return to real wall-clock time."""
        self._offset = timedelta(0)
        logger.debug("Clock offset cleared.")

    # ------------------------------------------------------------------
    # Timezone
    # ------------------------------------------------------------------

    def set_timezone(self, tz_name: str) -> None:
        """Change the secondary display timezone.

        Args:
            tz_name: A valid pytz timezone string, e.g. ``'America/Bogota'``.

        Raises:
            pytz.exceptions.UnknownTimeZoneError: If *tz_name* is invalid.
        """
        self._selected_timezone = pytz.timezone(tz_name)
        self._timezone_time     = datetime.now(tz=self._selected_timezone) + self._offset
        logger.info("Secondary timezone → '%s'.", tz_name)
        self._notify()

    # ------------------------------------------------------------------
    # Computed values for views
    # ------------------------------------------------------------------

    def get_hand_angles(self) -> Tuple[float, float, float]:
        """Return ``(hour_angle, minute_angle, second_angle)`` in degrees [0, 360)."""
        now     = self._local_time
        seconds = now.second + now.microsecond / 1_000_000
        minutes = now.minute + seconds / 60.0
        hours   = (now.hour % 12) + minutes / 60.0
        return hours * 30.0, minutes * 6.0, seconds * 6.0

    def get_timezone_names(self) -> List[str]:
        """Return the list of supported timezone name strings."""
        return list(TIMEZONE_LIST)

    def format_local_time(self) -> str:
        """Return local time as ``HH:MM:SS``."""
        return self._local_time.strftime("%H:%M:%S")

    def format_local_date(self) -> str:
        """Return local date as ``DD Month YYYY``."""
        return self._local_time.strftime("%d %B %Y")

    def format_local_weekday(self) -> str:
        """Return the full weekday name, e.g. ``'Tuesday'``."""
        return self._local_time.strftime("%A")

    def format_timezone_time(self) -> str:
        """Return the secondary-timezone time as ``HH:MM:SS``."""
        return self._timezone_time.strftime("%H:%M:%S")

    def format_timezone_label(self) -> str:
        """Return a human-readable label for the selected timezone."""
        return str(self._selected_timezone)
