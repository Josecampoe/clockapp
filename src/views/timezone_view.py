"""TimezoneView: world clock panel with CTk styling."""

import logging
import tkinter as tk
from typing import Dict, Callable, Optional, List

import customtkinter as ctk

from src.views.main_window import BaseView

logger = logging.getLogger(__name__)


class TimezoneView(BaseView):
    """World clock with a CTkOptionMenu selector."""

    def __init__(self, parent: tk.Widget) -> None:
        super().__init__()
        self._parent = parent
        self._tz_var   = tk.StringVar()
        self._time_var = tk.StringVar(value="--:--:--")
        self._on_change_callback: Optional[Callable[[str], None]] = None
        self._option_menu: Optional[ctk.CTkOptionMenu] = None
        self._time_label: Optional[ctk.CTkLabel] = None
        logger.debug("TimezoneView initialised.")

    def set_on_change(self, cb: Callable[[str], None]) -> None:
        self._on_change_callback = cb

    def build(self) -> None:
        self._frame = ctk.CTkFrame(self._parent, corner_radius=16)
        self._frame.pack(fill=tk.X, padx=20, pady=8)

        ctk.CTkLabel(
            self._frame, text="🌍  Reloj Mundial",
            font=ctk.CTkFont(size=15, weight="bold"),
        ).pack(anchor=tk.W, padx=16, pady=(14, 6))

        # Selector row
        sel_row = ctk.CTkFrame(self._frame, fg_color="transparent")
        sel_row.pack(fill=tk.X, padx=16, pady=4)

        ctk.CTkLabel(sel_row, text="Zona horaria:", font=ctk.CTkFont(size=12)).pack(side=tk.LEFT, padx=(0, 8))

        self._option_menu = ctk.CTkOptionMenu(
            sel_row,
            variable=self._tz_var,
            values=[],
            width=200,
            command=self._on_selection_changed,
            font=ctk.CTkFont(size=12),
        )
        self._option_menu.pack(side=tk.LEFT)

        # Time display
        self._time_label = ctk.CTkLabel(
            self._frame, textvariable=self._time_var,
            font=ctk.CTkFont(family="Courier New", size=40, weight="bold"),
        )
        self._time_label.pack(pady=(6, 16))

        logger.debug("TimezoneView built.")

    def apply_theme(self, colors: Dict[str, str]) -> None:
        self._frame.configure(fg_color=colors["bg_card"])
        if self._time_label:
            self._time_label.configure(text_color=colors["accent2"])

    def populate_timezones(self, names: List[str]) -> None:
        if self._option_menu and names:
            self._option_menu.configure(values=names)
            self._option_menu.set(names[0])
            self._tz_var.set(names[0])

    def update_time(self, time_str: str) -> None:
        self._time_var.set(time_str)

    @property
    def selected_timezone(self) -> str:
        return self._tz_var.get()

    def _on_selection_changed(self, value: str) -> None:
        if self._on_change_callback:
            self._on_change_callback(value)
