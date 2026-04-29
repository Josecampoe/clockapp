"""DigitalClockView: modern digital time/date display."""

import logging
import tkinter as tk
from typing import Dict

import customtkinter as ctk

from src.views.main_window import BaseView

logger = logging.getLogger(__name__)


class DigitalClockView(BaseView):
    """Shows HH:MM:SS, date, and weekday with a modern CTk style."""

    def __init__(self, parent: tk.Widget) -> None:
        super().__init__()
        self._parent = parent
        self._time_var = tk.StringVar(value="00:00:00")
        self._date_var = tk.StringVar(value="")
        self._day_var  = tk.StringVar(value="")
        self._time_label = None
        self._date_label = None
        self._day_label  = None
        logger.debug("DigitalClockView initialised.")

    def build(self) -> None:
        self._frame = ctk.CTkFrame(self._parent, fg_color="transparent")
        self._frame.pack(fill=tk.X, pady=(2, 6))

        self._time_label = ctk.CTkLabel(
            self._frame,
            textvariable=self._time_var,
            font=ctk.CTkFont(family="Courier New", size=38, weight="bold"),
        )
        self._time_label.pack()

        self._date_label = ctk.CTkLabel(
            self._frame,
            textvariable=self._date_var,
            font=ctk.CTkFont(family="Helvetica", size=13),
        )
        self._date_label.pack()

        self._day_label = ctk.CTkLabel(
            self._frame,
            textvariable=self._day_var,
            font=ctk.CTkFont(family="Helvetica", size=12),
        )
        self._day_label.pack()
        logger.debug("DigitalClockView built.")

    def apply_theme(self, colors: Dict[str, str]) -> None:
        self._frame.configure(fg_color="transparent")
        if self._time_label:
            self._time_label.configure(text_color=colors["accent"])
        if self._date_label:
            self._date_label.configure(text_color=colors["text_primary"])
        if self._day_label:
            self._day_label.configure(text_color=colors["text_secondary"])

    def update_time(self, time_str: str) -> None:
        self._time_var.set(time_str)

    def update_date(self, date_str: str) -> None:
        self._date_var.set(date_str)

    def update_day(self, day_str: str) -> None:
        self._day_var.set(day_str)
