"""StopwatchView: UI panel for the stopwatch feature."""

import logging
import tkinter as tk
from typing import Dict, Callable, Optional

from src.views.main_window import BaseView

logger = logging.getLogger(__name__)


class StopwatchView(BaseView):
    """Displays elapsed time and Start/Stop/Reset controls.

    Attributes:
        _parent: Parent tkinter widget.
        _elapsed_var: StringVar bound to the elapsed time label.
        _on_start_callback: Called when Start is clicked.
        _on_stop_callback: Called when Stop is clicked.
        _on_reset_callback: Called when Reset is clicked.
    """

    def __init__(self, parent: tk.Widget) -> None:
        """Initialise StopwatchView.

        Args:
            parent: The parent tkinter widget.
        """
        super().__init__()
        self._parent = parent
        self._elapsed_var: tk.StringVar = tk.StringVar(value="00:00:00:00")
        self._on_start_callback: Optional[Callable[[], None]] = None
        self._on_stop_callback: Optional[Callable[[], None]] = None
        self._on_reset_callback: Optional[Callable[[], None]] = None
        self._start_btn: Optional[tk.Button] = None
        self._stop_btn: Optional[tk.Button] = None
        logger.debug("StopwatchView initialised.")

    # ------------------------------------------------------------------
    # Callback registration
    # ------------------------------------------------------------------

    def set_on_start(self, callback: Callable[[], None]) -> None:
        """Register the Start button callback."""
        self._on_start_callback = callback

    def set_on_stop(self, callback: Callable[[], None]) -> None:
        """Register the Stop button callback."""
        self._on_stop_callback = callback

    def set_on_reset(self, callback: Callable[[], None]) -> None:
        """Register the Reset button callback."""
        self._on_reset_callback = callback

    # ------------------------------------------------------------------
    # BaseView implementation
    # ------------------------------------------------------------------

    def build(self) -> None:
        """Create and lay out all stopwatch widgets."""
        self._frame = tk.LabelFrame(self._parent, text=" Stopwatch ", padx=8, pady=6)
        self._frame.pack(fill=tk.X, padx=16, pady=4)

        elapsed_label = tk.Label(
            self._frame,
            textvariable=self._elapsed_var,
            font=("Courier", 22, "bold"),
        )
        elapsed_label.pack()

        btn_row = tk.Frame(self._frame)
        btn_row.pack(pady=(4, 0))

        self._start_btn = tk.Button(
            btn_row, text="Start", width=7, command=self._on_start_clicked
        )
        self._start_btn.pack(side=tk.LEFT, padx=4)

        self._stop_btn = tk.Button(
            btn_row, text="Stop", width=7, command=self._on_stop_clicked
        )
        self._stop_btn.pack(side=tk.LEFT, padx=4)

        reset_btn = tk.Button(
            btn_row, text="Reset", width=7, command=self._on_reset_clicked
        )
        reset_btn.pack(side=tk.LEFT, padx=4)

        self._elapsed_label = elapsed_label
        self._btn_row = btn_row
        logger.debug("StopwatchView built.")

    def apply_theme(self, colors: Dict[str, str]) -> None:
        """Apply theme colors to all stopwatch widgets.

        Args:
            colors: Theme color dictionary.
        """
        frame_bg = colors["frame_bg"]
        fg = colors["text_primary"]
        btn_bg = colors["button_bg"]
        btn_fg = colors["button_fg"]

        self._frame.configure(bg=frame_bg, fg=fg)
        self._elapsed_label.configure(bg=frame_bg, fg=colors["accent"])
        self._btn_row.configure(bg=frame_bg)
        for widget in self._btn_row.winfo_children():
            if isinstance(widget, tk.Button):
                widget.configure(
                    bg=btn_bg, fg=btn_fg,
                    activebackground=btn_bg, activeforeground=btn_fg,
                )

    # ------------------------------------------------------------------
    # Public update methods
    # ------------------------------------------------------------------

    def update_elapsed(self, elapsed_str: str) -> None:
        """Update the elapsed time display.

        Args:
            elapsed_str: Formatted elapsed time string (HH:MM:SS:ms).
        """
        self._elapsed_var.set(elapsed_str)

    def set_running_state(self, running: bool) -> None:
        """Update button states to reflect running/stopped state.

        Args:
            running: True if the stopwatch is currently running.
        """
        if self._start_btn and self._stop_btn:
            self._start_btn.configure(
                state=tk.DISABLED if running else tk.NORMAL
            )
            self._stop_btn.configure(
                state=tk.NORMAL if running else tk.DISABLED
            )

    # ------------------------------------------------------------------
    # Internal event handlers
    # ------------------------------------------------------------------

    def _on_start_clicked(self) -> None:
        if self._on_start_callback:
            self._on_start_callback()

    def _on_stop_clicked(self) -> None:
        if self._on_stop_callback:
            self._on_stop_callback()

    def _on_reset_clicked(self) -> None:
        if self._on_reset_callback:
            self._on_reset_callback()
