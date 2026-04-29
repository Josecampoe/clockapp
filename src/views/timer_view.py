"""TimerView: UI panel for the countdown timer feature."""

import logging
import tkinter as tk
from typing import Dict, Callable, Optional

from src.views.main_window import BaseView

logger = logging.getLogger(__name__)


class TimerView(BaseView):
    """Provides input fields and controls for the countdown timer.

    Attributes:
        _parent: Parent tkinter widget.
        _remaining_var: StringVar bound to the countdown display.
        _hours_var: StringVar for the hours input.
        _minutes_var: StringVar for the minutes input.
        _seconds_var: StringVar for the seconds input.
    """

    def __init__(self, parent: tk.Widget) -> None:
        """Initialise TimerView.

        Args:
            parent: The parent tkinter widget.
        """
        super().__init__()
        self._parent = parent
        self._remaining_var: tk.StringVar = tk.StringVar(value="00:00:00")
        self._hours_var: tk.StringVar = tk.StringVar(value="0")
        self._minutes_var: tk.StringVar = tk.StringVar(value="5")
        self._seconds_var: tk.StringVar = tk.StringVar(value="0")
        self._on_set_callback: Optional[Callable[[], None]] = None
        self._on_start_callback: Optional[Callable[[], None]] = None
        self._on_pause_callback: Optional[Callable[[], None]] = None
        self._on_reset_callback: Optional[Callable[[], None]] = None
        self._on_dismiss_callback: Optional[Callable[[], None]] = None
        self._start_btn: Optional[tk.Button] = None
        self._pause_btn: Optional[tk.Button] = None
        self._alert_frame: Optional[tk.Frame] = None
        self._remaining_label: Optional[tk.Label] = None
        self._btn_row: Optional[tk.Frame] = None
        logger.debug("TimerView initialised.")

    # ------------------------------------------------------------------
    # Callback registration
    # ------------------------------------------------------------------

    def set_on_set(self, callback: Callable[[], None]) -> None:
        """Register callback for the 'Set' button."""
        self._on_set_callback = callback

    def set_on_start(self, callback: Callable[[], None]) -> None:
        """Register callback for the 'Start' button."""
        self._on_start_callback = callback

    def set_on_pause(self, callback: Callable[[], None]) -> None:
        """Register callback for the 'Pause' button."""
        self._on_pause_callback = callback

    def set_on_reset(self, callback: Callable[[], None]) -> None:
        """Register callback for the 'Reset' button."""
        self._on_reset_callback = callback

    def set_on_dismiss(self, callback: Callable[[], None]) -> None:
        """Register callback for the dismiss button."""
        self._on_dismiss_callback = callback

    # ------------------------------------------------------------------
    # BaseView implementation
    # ------------------------------------------------------------------

    def build(self) -> None:
        """Create and lay out all timer widgets."""
        self._frame = tk.LabelFrame(self._parent, text=" Countdown Timer ", padx=8, pady=6)
        self._frame.pack(fill=tk.X, padx=16, pady=4)

        # Duration input row
        input_row = tk.Frame(self._frame)
        input_row.pack(fill=tk.X)

        tk.Label(input_row, text="H:").pack(side=tk.LEFT)
        tk.Entry(input_row, textvariable=self._hours_var, width=4,
                 justify=tk.CENTER).pack(side=tk.LEFT, padx=(0, 4))
        tk.Label(input_row, text="M:").pack(side=tk.LEFT)
        tk.Entry(input_row, textvariable=self._minutes_var, width=4,
                 justify=tk.CENTER).pack(side=tk.LEFT, padx=(0, 4))
        tk.Label(input_row, text="S:").pack(side=tk.LEFT)
        tk.Entry(input_row, textvariable=self._seconds_var, width=4,
                 justify=tk.CENTER).pack(side=tk.LEFT, padx=(0, 8))
        tk.Button(input_row, text="Set", command=self._on_set_clicked).pack(side=tk.LEFT)

        # Countdown display
        self._remaining_label = tk.Label(
            self._frame,
            textvariable=self._remaining_var,
            font=("Courier", 22, "bold"),
        )
        self._remaining_label.pack(pady=(4, 0))

        # Control buttons
        self._btn_row = tk.Frame(self._frame)
        self._btn_row.pack(pady=(4, 0))

        self._start_btn = tk.Button(
            self._btn_row, text="Start", width=7, command=self._on_start_clicked
        )
        self._start_btn.pack(side=tk.LEFT, padx=4)

        self._pause_btn = tk.Button(
            self._btn_row, text="Pause", width=7, command=self._on_pause_clicked
        )
        self._pause_btn.pack(side=tk.LEFT, padx=4)

        tk.Button(
            self._btn_row, text="Reset", width=7, command=self._on_reset_clicked
        ).pack(side=tk.LEFT, padx=4)

        # Alert frame (hidden until timer finishes)
        self._alert_frame = tk.Frame(self._frame)
        tk.Label(
            self._alert_frame,
            text="⏱  Time's up!  ⏱",
            font=("Helvetica", 12, "bold"),
        ).pack(side=tk.LEFT, padx=(0, 10))
        tk.Button(
            self._alert_frame, text="Dismiss", command=self._on_dismiss_clicked
        ).pack(side=tk.LEFT)

        self._input_row = input_row
        logger.debug("TimerView built.")

    def apply_theme(self, colors: Dict[str, str]) -> None:
        """Apply theme colors to all timer widgets.

        Args:
            colors: Theme color dictionary.
        """
        frame_bg = colors["frame_bg"]
        fg = colors["text_primary"]
        btn_bg = colors["button_bg"]
        btn_fg = colors["button_fg"]
        entry_bg = colors["entry_bg"]
        entry_fg = colors["entry_fg"]

        self._frame.configure(bg=frame_bg, fg=fg)
        if self._remaining_label:
            self._remaining_label.configure(bg=frame_bg, fg=colors["accent"])
        self._apply_children_theme(self._frame, frame_bg, fg, btn_bg, btn_fg,
                                   entry_bg, entry_fg)

    def _apply_children_theme(
        self, parent: tk.Widget, bg: str, fg: str,
        btn_bg: str, btn_fg: str, entry_bg: str, entry_fg: str
    ) -> None:
        """Recursively apply theme to child widgets."""
        for widget in parent.winfo_children():
            try:
                if isinstance(widget, tk.Button):
                    widget.configure(bg=btn_bg, fg=btn_fg,
                                     activebackground=btn_bg, activeforeground=btn_fg)
                elif isinstance(widget, tk.Entry):
                    widget.configure(bg=entry_bg, fg=entry_fg,
                                     insertbackground=entry_fg)
                elif isinstance(widget, (tk.Label, tk.Frame)):
                    kw: dict = {"bg": bg}
                    if isinstance(widget, tk.Label):
                        kw["fg"] = fg
                    widget.configure(**kw)
            except tk.TclError:
                pass
            self._apply_children_theme(widget, bg, fg, btn_bg, btn_fg, entry_bg, entry_fg)

    # ------------------------------------------------------------------
    # Public update methods
    # ------------------------------------------------------------------

    def update_remaining(self, remaining_str: str) -> None:
        """Update the countdown display.

        Args:
            remaining_str: Formatted remaining time string (HH:MM:SS).
        """
        self._remaining_var.set(remaining_str)

    def show_alert(self) -> None:
        """Show the 'Time's up' alert row."""
        self._alert_frame.pack(fill=tk.X, pady=(4, 0))

    def hide_alert(self) -> None:
        """Hide the alert row."""
        self._alert_frame.pack_forget()

    def set_running_state(self, running: bool) -> None:
        """Update button states to reflect running/paused state.

        Args:
            running: True if the timer is currently counting down.
        """
        if self._start_btn and self._pause_btn:
            self._start_btn.configure(
                state=tk.DISABLED if running else tk.NORMAL
            )
            self._pause_btn.configure(
                state=tk.NORMAL if running else tk.DISABLED
            )

    # ------------------------------------------------------------------
    # Accessors
    # ------------------------------------------------------------------

    @property
    def hours_value(self) -> str:
        """Return the raw text from the hours entry."""
        return self._hours_var.get().strip()

    @property
    def minutes_value(self) -> str:
        """Return the raw text from the minutes entry."""
        return self._minutes_var.get().strip()

    @property
    def seconds_value(self) -> str:
        """Return the raw text from the seconds entry."""
        return self._seconds_var.get().strip()

    # ------------------------------------------------------------------
    # Internal event handlers
    # ------------------------------------------------------------------

    def _on_set_clicked(self) -> None:
        if self._on_set_callback:
            self._on_set_callback()

    def _on_start_clicked(self) -> None:
        if self._on_start_callback:
            self._on_start_callback()

    def _on_pause_clicked(self) -> None:
        if self._on_pause_callback:
            self._on_pause_callback()

    def _on_reset_clicked(self) -> None:
        if self._on_reset_callback:
            self._on_reset_callback()

    def _on_dismiss_clicked(self) -> None:
        if self._on_dismiss_callback:
            self._on_dismiss_callback()
