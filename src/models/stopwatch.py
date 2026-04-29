"""StopwatchModel: elapsed-time tracking with lap support."""

import logging
import time
from typing import List, Tuple

from src.models.clock import BaseModel

logger = logging.getLogger(__name__)


class StopwatchModel(BaseModel):
    """Manages stopwatch state: running, paused, elapsed time, and laps.

    Uses ``time.monotonic()`` to avoid drift from system-clock adjustments.

    Attributes:
        _running:    Whether the stopwatch is currently counting.
        _elapsed:    Accumulated seconds before the most recent start.
        _start_time: Monotonic timestamp of the most recent start call.
        _laps:       List of (lap_number, lap_split, lap_total) tuples.
    """

    def __init__(self) -> None:
        super().__init__()
        self._running: bool = False
        self._elapsed: float = 0.0
        self._start_time: float = 0.0
        self._laps: List[Tuple[int, float, float]] = []
        logger.debug("StopwatchModel initialised.")

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def running(self) -> bool:
        return self._running

    @property
    def elapsed_seconds(self) -> float:
        """Total elapsed seconds including the current running segment."""
        if self._running:
            return self._elapsed + (time.monotonic() - self._start_time)
        return self._elapsed

    @property
    def laps(self) -> List[Tuple[int, float, float]]:
        """Return a copy of the lap list: [(lap_num, split_s, total_s), …]."""
        return list(self._laps)

    @property
    def lap_count(self) -> int:
        return len(self._laps)

    # ------------------------------------------------------------------
    # Controls
    # ------------------------------------------------------------------

    def start(self) -> None:
        """Start or resume the stopwatch."""
        if not self._running:
            self._start_time = time.monotonic()
            self._running = True
            logger.info("Stopwatch started.")
            self._notify()

    def stop(self) -> None:
        """Pause the stopwatch, preserving elapsed time."""
        if self._running:
            self._elapsed += time.monotonic() - self._start_time
            self._running = False
            logger.info("Stopwatch stopped. Elapsed: %.3f s.", self._elapsed)
            self._notify()

    def reset(self) -> None:
        """Stop and reset to zero, clearing all laps."""
        self._running = False
        self._elapsed = 0.0
        self._start_time = 0.0
        self._laps.clear()
        logger.info("Stopwatch reset.")
        self._notify()

    def lap(self) -> None:
        """Record a lap split (only while running)."""
        if not self._running:
            return
        total = self.elapsed_seconds
        prev_total = self._laps[-1][2] if self._laps else 0.0
        split = total - prev_total
        lap_num = len(self._laps) + 1
        self._laps.append((lap_num, split, total))
        logger.info("Lap %d: split=%.3f s, total=%.3f s.", lap_num, split, total)
        self._notify()

    # ------------------------------------------------------------------
    # Tick
    # ------------------------------------------------------------------

    def update(self) -> None:
        """Notify observers so the view can refresh the display."""
        if self._running:
            self._notify()

    # ------------------------------------------------------------------
    # Formatting
    # ------------------------------------------------------------------

    def format_elapsed(self) -> str:
        """Return elapsed time as ``HH:MM:SS:cs`` (centiseconds)."""
        return self._format_seconds(self.elapsed_seconds)

    def format_lap(self, lap_index: int) -> str:
        """Return a formatted string for a specific lap.

        Args:
            lap_index: Zero-based index into the laps list.

        Returns:
            ``'Lap N  split  total'`` string, or empty string if invalid.
        """
        if lap_index < 0 or lap_index >= len(self._laps):
            return ""
        num, split, total = self._laps[lap_index]
        return (
            f"Vuelta {num:>2}   "
            f"{self._format_seconds(split)}   "
            f"{self._format_seconds(total)}"
        )

    @staticmethod
    def _format_seconds(total: float) -> str:
        hours = int(total // 3600)
        rem   = total - hours * 3600
        mins  = int(rem // 60)
        secs  = int(rem % 60)
        cs    = int((total % 1) * 100)
        return f"{hours:02d}:{mins:02d}:{secs:02d}:{cs:02d}"
