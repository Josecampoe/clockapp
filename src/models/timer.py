"""TimerModel: countdown timer logic."""

import logging
import time

from src.models.clock import BaseModel

logger = logging.getLogger(__name__)


class TimerModel(BaseModel):
    """Manages a countdown timer from a user-specified duration to zero.

    Uses monotonic timestamps for accurate countdown regardless of system
    clock changes.

    Attributes:
        _total_seconds: The original countdown duration in seconds.
        _remaining: Seconds remaining when the timer was last paused.
        _running: Whether the timer is currently counting down.
        _finished: Whether the timer has reached zero.
        _start_time: Monotonic timestamp of the most recent start/resume.
    """

    def __init__(self) -> None:
        """Initialise TimerModel in a stopped, zeroed state."""
        super().__init__()
        self._total_seconds: float = 0.0
        self._remaining: float = 0.0
        self._running: bool = False
        self._finished: bool = False
        self._start_time: float = 0.0
        logger.debug("TimerModel initialised.")

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def running(self) -> bool:
        """Return True if the timer is currently counting down."""
        return self._running

    @property
    def finished(self) -> bool:
        """Return True if the timer has reached zero."""
        return self._finished

    @property
    def total_seconds(self) -> float:
        """Return the original countdown duration in seconds."""
        return self._total_seconds

    @property
    def remaining_seconds(self) -> float:
        """Return the number of seconds remaining (never negative)."""
        if self._running:
            elapsed = time.monotonic() - self._start_time
            remaining = self._remaining - elapsed
            return max(0.0, remaining)
        return max(0.0, self._remaining)

    # ------------------------------------------------------------------
    # Public methods
    # ------------------------------------------------------------------

    def set_duration(self, hours: int, minutes: int, seconds: int) -> None:
        """Set the countdown duration.

        Args:
            hours: Hours component (0–23).
            minutes: Minutes component (0–59).
            seconds: Seconds component (0–59).

        Raises:
            ValueError: If any component is out of range or total is zero.
        """
        if not 0 <= hours <= 23:
            raise ValueError(f"Hours must be 0–23, got {hours}.")
        if not 0 <= minutes <= 59:
            raise ValueError(f"Minutes must be 0–59, got {minutes}.")
        if not 0 <= seconds <= 59:
            raise ValueError(f"Seconds must be 0–59, got {seconds}.")

        total = hours * 3600 + minutes * 60 + seconds
        if total == 0:
            raise ValueError("Timer duration must be greater than zero.")

        self._total_seconds = float(total)
        self._remaining = float(total)
        self._running = False
        self._finished = False
        logger.debug(
            "Timer duration set to %02d:%02d:%02d (%d s).",
            hours, minutes, seconds, total,
        )
        self._notify()

    def start(self) -> None:
        """Start or resume the countdown.

        Has no effect if already running or finished.
        """
        if not self._running and not self._finished and self._remaining > 0:
            self._start_time = time.monotonic()
            self._running = True
            logger.info("Timer started. Remaining: %.1f s.", self._remaining)
            self._notify()

    def pause(self) -> None:
        """Pause the countdown, preserving remaining time.

        Has no effect if already paused.
        """
        if self._running:
            elapsed = time.monotonic() - self._start_time
            self._remaining = max(0.0, self._remaining - elapsed)
            self._running = False
            logger.info("Timer paused. Remaining: %.1f s.", self._remaining)
            self._notify()

    def reset(self) -> None:
        """Stop and reset the timer to its original duration."""
        self._running = False
        self._finished = False
        self._remaining = self._total_seconds
        logger.info("Timer reset to %.1f s.", self._total_seconds)
        self._notify()

    def update(self) -> None:
        """Check for completion and notify observers."""
        if not self._running:
            return

        if self.remaining_seconds <= 0:
            elapsed = time.monotonic() - self._start_time
            self._remaining = max(0.0, self._remaining - elapsed)
            self._running = False
            self._finished = True
            logger.info("Timer finished.")
            self._notify()
        else:
            self._notify()

    def acknowledge(self) -> None:
        """Acknowledge the finished state so the alert is dismissed."""
        self._finished = False
        logger.debug("Timer finish acknowledged.")
        self._notify()

    def format_remaining(self) -> str:
        """Return remaining time formatted as HH:MM:SS.

        Returns:
            String in HH:MM:SS format.
        """
        total = int(self.remaining_seconds)
        hours = total // 3600
        minutes = (total % 3600) // 60
        seconds = total % 60
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
