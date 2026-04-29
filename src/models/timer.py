"""TimerModel: countdown timer with preset support."""

import logging
import time
from typing import List, Tuple

from src.models.clock import BaseModel

logger = logging.getLogger(__name__)

# Built-in quick-set presets (label, hours, minutes, seconds)
TIMER_PRESETS: List[Tuple[str, int, int, int]] = [
    ("1 min",  0, 1,  0),
    ("3 min",  0, 3,  0),
    ("5 min",  0, 5,  0),
    ("10 min", 0, 10, 0),
    ("15 min", 0, 15, 0),
    ("30 min", 0, 30, 0),
    ("1 hora", 1, 0,  0),
]


class TimerModel(BaseModel):
    """Countdown timer from a user-specified duration to zero.

    Uses ``time.monotonic()`` for accurate countdown regardless of
    system-clock changes.

    Attributes:
        _total_seconds: Original countdown duration in seconds.
        _remaining:     Seconds remaining when last paused.
        _running:       Whether the timer is currently counting down.
        _finished:      Whether the timer has reached zero.
        _start_time:    Monotonic timestamp of the most recent start/resume.
    """

    def __init__(self) -> None:
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
        return self._running

    @property
    def finished(self) -> bool:
        return self._finished

    @property
    def total_seconds(self) -> float:
        return self._total_seconds

    @property
    def remaining_seconds(self) -> float:
        """Seconds remaining (never negative)."""
        if self._running:
            elapsed = time.monotonic() - self._start_time
            return max(0.0, self._remaining - elapsed)
        return max(0.0, self._remaining)

    @property
    def progress(self) -> float:
        """Completion fraction in [0.0, 1.0] (0 = full, 1 = done)."""
        if self._total_seconds <= 0:
            return 0.0
        return 1.0 - (self.remaining_seconds / self._total_seconds)

    # ------------------------------------------------------------------
    # Configuration
    # ------------------------------------------------------------------

    def set_duration(self, hours: int, minutes: int, seconds: int) -> None:
        """Set the countdown duration.

        Args:
            hours:   0–23.
            minutes: 0–59.
            seconds: 0–59.

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
        logger.debug("Timer set to %02d:%02d:%02d.", hours, minutes, seconds)
        self._notify()

    def apply_preset(self, preset_index: int) -> None:
        """Apply one of the built-in presets by index.

        Args:
            preset_index: Index into ``TIMER_PRESETS``.

        Raises:
            IndexError: If *preset_index* is out of range.
        """
        _, h, m, s = TIMER_PRESETS[preset_index]
        self.set_duration(h, m, s)

    # ------------------------------------------------------------------
    # Controls
    # ------------------------------------------------------------------

    def start(self) -> None:
        """Start or resume the countdown."""
        if not self._running and not self._finished and self._remaining > 0:
            self._start_time = time.monotonic()
            self._running = True
            logger.info("Timer started. Remaining: %.1f s.", self._remaining)
            self._notify()

    def pause(self) -> None:
        """Pause the countdown, preserving remaining time."""
        if self._running:
            elapsed = time.monotonic() - self._start_time
            self._remaining = max(0.0, self._remaining - elapsed)
            self._running = False
            logger.info("Timer paused. Remaining: %.1f s.", self._remaining)
            self._notify()

    def reset(self) -> None:
        """Stop and reset to the original duration."""
        self._running = False
        self._finished = False
        self._remaining = self._total_seconds
        logger.info("Timer reset.")
        self._notify()

    def acknowledge(self) -> None:
        """Dismiss the finished state."""
        self._finished = False
        logger.debug("Timer acknowledged.")
        self._notify()

    # ------------------------------------------------------------------
    # Tick
    # ------------------------------------------------------------------

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

    # ------------------------------------------------------------------
    # Formatting
    # ------------------------------------------------------------------

    def format_remaining(self) -> str:
        """Return remaining time as ``HH:MM:SS``."""
        total = int(self.remaining_seconds)
        h = total // 3600
        m = (total % 3600) // 60
        s = total % 60
        return f"{h:02d}:{m:02d}:{s:02d}"
