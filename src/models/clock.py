"""ClockModel: provides current time and timezone-aware time."""

import logging
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, List, Callable, Tuple

import pytz

from src.utils.constants import TIMEZONE_LIST

logger = logging.getLogger(__name__)


class BaseModel(ABC):
    """Abstract base class for all domain models.

    Implements the Observer pattern so views can subscribe to state changes.
    """

    def __init__(self) -> None:
        """Initialise the observer list."""
        self._observers: List[Callable[[], None]] = []

    def subscribe(self, callback: Callable[[], None]) -> None:
        """Register an observer callback.

        Args:
            callback: A zero-argument callable invoked on state change.
        """
        if callback not in self._observers:
            self._observers.append(callback)

    def unsubscribe(self, callback: Callable[[], None]) -> None:
        """Remove a previously registered observer.

        Args:
            callback: The callable to remove.
        """
        if callback in self._observers:
            self._observers.remove(callback)

    def _notify(self) -> None:
        """Notify all registered observers."""
        for callback in self._observers:
            try:
                callback()
            except Exception as exc:  # pylint: disable=broad-except
                logger.error("Observer notification error: %s", exc)

    @abstractmethod
    def update(self) -> None:
        """Refresh internal state. Called periodically by the controller."""


class ClockModel(BaseModel):
    """Provides the current local time and timezone-aware secondary time.

    Attributes:
        _local_time: Most recently computed local datetime.
        _selected_timezone: pytz timezone currently selected for secondary display.
        _timezone_time: Most recently computed datetime in the selected timezone.
    """

    def __init__(self) -> None:
        """Initialise ClockModel with the default timezone (UTC)."""
        super().__init__()
        self._local_time: datetime = datetime.now()
        self._selected_timezone: pytz.BaseTzInfo = pytz.utc
        self._timezone_time: datetime = datetime.now(tz=pytz.utc)
        logger.debug("ClockModel initialised.")

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def local_time(self) -> datetime:
        """Return the most recently computed local datetime."""
        return self._local_time

    @property
    def selected_timezone(self) -> pytz.BaseTzInfo:
        """Return the currently selected secondary timezone."""
        return self._selected_timezone

    @property
    def timezone_time(self) -> datetime:
        """Return the current time in the selected secondary timezone."""
        return self._timezone_time

    # ------------------------------------------------------------------
    # Public methods
    # ------------------------------------------------------------------

    def update(self) -> None:
        """Refresh local time and timezone time, then notify observers."""
        self._local_time = datetime.now()
        self._timezone_time = datetime.now(tz=self._selected_timezone)
        self._notify()

    def set_timezone(self, tz_name: str) -> None:
        """Change the secondary display timezone.

        Args:
            tz_name: A valid pytz timezone string (e.g. 'America/Bogota').

        Raises:
            pytz.exceptions.UnknownTimeZoneError: If tz_name is invalid.
        """
        self._selected_timezone = pytz.timezone(tz_name)
        self._timezone_time = datetime.now(tz=self._selected_timezone)
        logger.info("Secondary timezone set to '%s'.", tz_name)
        self._notify()

    def get_hand_angles(self) -> Tuple[float, float, float]:
        """Calculate clock hand angles in degrees from 12 o'clock (clockwise).

        Returns:
            A tuple of (hour_angle, minute_angle, second_angle) in degrees.
        """
        now = self._local_time
        seconds = now.second + now.microsecond / 1_000_000
        minutes = now.minute + seconds / 60.0
        hours = (now.hour % 12) + minutes / 60.0

        hour_angle = hours * 30.0          # 360 / 12
        minute_angle = minutes * 6.0       # 360 / 60
        second_angle = seconds * 6.0       # 360 / 60

        return hour_angle, minute_angle, second_angle

    def get_timezone_names(self) -> List[str]:
        """Return the list of supported timezone names.

        Returns:
            List of timezone name strings.
        """
        return list(TIMEZONE_LIST)

    def format_local_time(self) -> str:
        """Return local time formatted as HH:MM:SS.

        Returns:
            Time string in HH:MM:SS format.
        """
        return self._local_time.strftime("%H:%M:%S")

    def format_local_date(self) -> str:
        """Return local date formatted as DD Month YYYY.

        Returns:
            Date string, e.g. '28 April 2026'.
        """
        return self._local_time.strftime("%d %B %Y")

    def format_local_weekday(self) -> str:
        """Return the full weekday name for the local date.

        Returns:
            Weekday string, e.g. 'Tuesday'.
        """
        return self._local_time.strftime("%A")

    def format_timezone_time(self) -> str:
        """Return the secondary timezone time formatted as HH:MM:SS.

        Returns:
            Time string in HH:MM:SS format.
        """
        return self._timezone_time.strftime("%H:%M:%S")

    def format_timezone_label(self) -> str:
        """Return a human-readable label for the selected timezone.

        Returns:
            Timezone name string, e.g. 'America/Bogota'.
        """
        return str(self._selected_timezone)
