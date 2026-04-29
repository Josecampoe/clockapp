"""StopwatchModel: tracks elapsed time for the stopwatch feature."""

import logging
import time

from src.models.clock import BaseModel

logger = logging.getLogger(__name__)


class StopwatchModel(BaseModel):
    """Manages stopwatch state: running, paused, and elapsed time.

    Elapsed time is tracked using monotonic clock timestamps to avoid
    drift caused by system clock adjustments.

    Attributes:
        _running: Whether the stopwatch is currently counting.
        _elapsed: Total elapsed seconds accumulated before the last start.
        _start_time: Monotonic timestamp of the most recent start call.
    """

    def __init__(self) -> None:
        """Initialise StopwatchModel in a stopped, zeroed state."""
        super().__init__()
        self._running: bool = False
        self._elapsed: float = 0.0
        self._start_time: float = 0.0
        logger.debug("StopwatchModel initialised.")

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def running(self) -> bool:
        """Return True if the stopwatch is currently running."""
        return self._running

    @property
    def elapsed_seconds(self) -> float:
        """Return total elapsed time in seconds (including current run)."""
        if self._running:
            return self._elapsed + (time.monotonic() - self._start_time)
        return self._elapsed

    # ------------------------------------------------------------------
    # Public methods
    # ------------------------------------------------------------------

    def start(self) -> None:
        """Start or resume the stopwatch.

        Has no effect if already running.
        """
        if not self._running:
            self._start_time = time.monotonic()
            self._running = True
            logger.info("Stopwatch started.")
            self._notify()

    def stop(self) -> None:
        """Pause the stopwatch, preserving elapsed time.

        Has no effect if already stopped.
        """
        if self._running:
            self._elapsed += time.monotonic() - self._start_time
            self._running = False
            logger.info("Stopwatch stopped. Elapsed: %.3f s.", self._elapsed)
            self._notify()

    def reset(self) -> None:
        """Stop and reset the stopwatch to zero."""
        self._running = False
        self._elapsed = 0.0
        self._start_time = 0.0
        logger.info("Stopwatch reset.")
        self._notify()

    def update(self) -> None:
        """Notify observers so the view can refresh the display."""
        if self._running:
            self._notify()

    def format_elapsed(self) -> str:
        """Return elapsed time formatted as HH:MM:SS:ms.

        Returns:
            String in HH:MM:SS:ms format where ms is centiseconds (00–99).
        """
        total = self.elapsed_seconds
        hours = int(total // 3600)
        remaining = total - hours * 3600
        minutes = int(remaining // 60)
        seconds = int(remaining % 60)
        centiseconds = int((total % 1) * 100)
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}:{centiseconds:02d}"
