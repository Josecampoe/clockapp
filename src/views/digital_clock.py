"""DigitalClockView: displays current time, date, and weekday."""

import logging
import tkinter as tk
from typing import Dict

from src.views.main_window import BaseView
from src.utils.constants import (
    DIGITAL_TIME_FONT_SIZE,
    DIGITAL_DATE_FONT_SIZE,
    DIGITAL_DAY_FONT_SIZE,
)

logger = logging.getLogger(__name__)


class DigitalClockView(BaseView):
    """Shows the current time in HH:MM:SS, the date, and the weekday.

    Attributes:
        _parent: Parent tkinter widget.
        _time_var: StringVar bound to the time label.
        _date_var: StringVar bound to the date label.
        _day_var: StringVar bound to the weekday label.
    """

    def __init__(self, parent: tk.Widget) -> None:
        """Initialise DigitalClockView.

        Args:
            parent: The parent tkinter widget.
        """
        super().__init__()
        self._parent = parent
        self._time_var: tk.StringVar = tk.StringVar(value="00:00:00")
        self._date_var: tk.StringVar = tk.StringVar(value="")
        self._day_var: tk.StringVar = tk.StringVar(value="")
        self._time_label: tk.Label = None  # type: ignore[assignment]
        self._date_label: tk.Label = None  # type: ignore[assignment]
        self._day_label: tk.Label = None  # type: ignore[assignment]
        logger.debug("DigitalClockView initialised.")

    # ------------------------------------------------------------------
    # BaseView implementation
    # ------------------------------------------------------------------

    def build(self) -> None:
        """Create and lay out the time, date, and weekday labels."""
        self._frame = tk.Frame(self._parent)
        self._frame.pack(fill=tk.X, padx=20, pady=(4, 8))

        self._time_label = tk.Label(
            self._frame,
            textvariable=self._time_var,
            font=("Courier", DIGITAL_TIME_FONT_SIZE, "bold"),
        )
        self._time_label.pack()

        self._date_label = tk.Label(
            self._frame,
            textvariable=self._date_var,
            font=("Helvetica", DIGITAL_DATE_FONT_SIZE),
        )
        self._date_label.pack()

        self._day_label = tk.Label(
            self._frame,
            textvariable=self._day_var,
            font=("Helvetica", DIGITAL_DAY_FONT_SIZE),
        )
        self._day_label.pack()
        logger.debug("DigitalClockView built.")

    def apply_theme(self, colors: Dict[str, str]) -> None:
        """Apply theme colors to all labels.

        Args:
            colors: Theme color dictionary.
        """
        bg = colors["bg_window"]
        self._frame.configure(bg=bg)
        self._time_label.configure(
            bg=bg,
            fg=colors["text_primary"],
        )
        self._date_label.configure(
            bg=bg,
            fg=colors["text_secondary"],
        )
        self._day_label.configure(
            bg=bg,
            fg=colors["text_secondary"],
        )

    # ------------------------------------------------------------------
    # Update methods
    # ------------------------------------------------------------------

    def update_time(self, time_str: str) -> None:
        """Update the displayed time string.

        Args:
            time_str: Time in HH:MM:SS format.
        """
        self._time_var.set(time_str)

    def update_date(self, date_str: str) -> None:
        """Update the displayed date string.

        Args:
            date_str: Date string, e.g. '28 April 2026'.
        """
        self._date_var.set(date_str)

    def update_day(self, day_str: str) -> None:
        """Update the displayed weekday string.

        Args:
            day_str: Weekday name, e.g. 'Tuesday'.
        """
        self._day_var.set(day_str)
