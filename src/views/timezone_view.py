"""TimezoneView: secondary timezone display with dropdown selector."""

import logging
import tkinter as tk
from tkinter import ttk
from typing import Dict, Callable, Optional, List

from src.views.main_window import BaseView

logger = logging.getLogger(__name__)


class TimezoneView(BaseView):
    """Shows a secondary clock for a user-selected timezone.

    Attributes:
        _parent: Parent tkinter widget.
        _tz_var: StringVar bound to the combobox selection.
        _time_var: StringVar bound to the timezone time label.
        _on_change_callback: Called when the user selects a new timezone.
    """

    def __init__(self, parent: tk.Widget) -> None:
        """Initialise TimezoneView.

        Args:
            parent: The parent tkinter widget.
        """
        super().__init__()
        self._parent = parent
        self._tz_var: tk.StringVar = tk.StringVar()
        self._time_var: tk.StringVar = tk.StringVar(value="--:--:--")
        self._on_change_callback: Optional[Callable[[str], None]] = None
        self._combo: Optional[ttk.Combobox] = None
        self._time_label: Optional[tk.Label] = None
        self._tz_label: Optional[tk.Label] = None
        logger.debug("TimezoneView initialised.")

    # ------------------------------------------------------------------
    # Callback registration
    # ------------------------------------------------------------------

    def set_on_change(self, callback: Callable[[str], None]) -> None:
        """Register callback invoked when the timezone selection changes.

        Args:
            callback: Callable receiving the selected timezone name string.
        """
        self._on_change_callback = callback

    # ------------------------------------------------------------------
    # BaseView implementation
    # ------------------------------------------------------------------

    def build(self) -> None:
        """Create and lay out all timezone widgets."""
        self._frame = tk.LabelFrame(self._parent, text=" World Clock ", padx=8, pady=6)
        self._frame.pack(fill=tk.X, padx=16, pady=4)

        row = tk.Frame(self._frame)
        row.pack(fill=tk.X)

        tk.Label(row, text="Timezone:").pack(side=tk.LEFT, padx=(0, 6))

        self._combo = ttk.Combobox(
            row,
            textvariable=self._tz_var,
            state="readonly",
            width=22,
        )
        self._combo.pack(side=tk.LEFT)
        self._combo.bind("<<ComboboxSelected>>", self._on_selection_changed)

        self._tz_label = tk.Label(
            self._frame,
            textvariable=self._tz_var,
            font=("Helvetica", 10),
        )
        self._tz_label.pack(anchor=tk.W, pady=(2, 0))

        self._time_label = tk.Label(
            self._frame,
            textvariable=self._time_var,
            font=("Courier", 22, "bold"),
        )
        self._time_label.pack(anchor=tk.W)
        logger.debug("TimezoneView built.")

    def apply_theme(self, colors: Dict[str, str]) -> None:
        """Apply theme colors to all timezone widgets.

        Args:
            colors: Theme color dictionary.
        """
        frame_bg = colors["frame_bg"]
        fg = colors["text_primary"]
        secondary_fg = colors["text_secondary"]

        self._frame.configure(bg=frame_bg, fg=fg)
        for widget in self._frame.winfo_children():
            try:
                if isinstance(widget, tk.Label):
                    widget.configure(bg=frame_bg, fg=secondary_fg)
                elif isinstance(widget, tk.Frame):
                    widget.configure(bg=frame_bg)
                    for child in widget.winfo_children():
                        if isinstance(child, tk.Label):
                            child.configure(bg=frame_bg, fg=fg)
            except tk.TclError:
                pass

        if self._time_label:
            self._time_label.configure(bg=frame_bg, fg=colors["accent"])
        if self._tz_label:
            self._tz_label.configure(bg=frame_bg, fg=secondary_fg)

    # ------------------------------------------------------------------
    # Public methods
    # ------------------------------------------------------------------

    def populate_timezones(self, timezone_names: List[str]) -> None:
        """Populate the combobox with timezone options.

        Args:
            timezone_names: List of timezone name strings.
        """
        if self._combo:
            self._combo["values"] = timezone_names
            if timezone_names:
                self._combo.current(0)
                self._tz_var.set(timezone_names[0])

    def update_time(self, time_str: str) -> None:
        """Update the displayed timezone time.

        Args:
            time_str: Time string in HH:MM:SS format.
        """
        self._time_var.set(time_str)

    @property
    def selected_timezone(self) -> str:
        """Return the currently selected timezone name."""
        return self._tz_var.get()

    # ------------------------------------------------------------------
    # Internal event handlers
    # ------------------------------------------------------------------

    def _on_selection_changed(self, _event: tk.Event) -> None:
        """Handle combobox selection change."""
        selected = self._tz_var.get()
        logger.debug("Timezone selected: %s", selected)
        if self._on_change_callback:
            self._on_change_callback(selected)
