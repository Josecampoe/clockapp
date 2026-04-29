"""AlarmView: UI panel for setting and managing the alarm."""

import logging
import tkinter as tk
from typing import Dict, Callable, Optional

from src.views.main_window import BaseView

logger = logging.getLogger(__name__)


class AlarmView(BaseView):
    """Provides input fields and controls for the alarm feature.

    Attributes:
        _parent: Parent tkinter widget.
        _hour_var: StringVar for the hour entry.
        _minute_var: StringVar for the minute entry.
        _enabled_var: BooleanVar for the enable/disable toggle.
        _status_var: StringVar for the status message label.
        _on_set_callback: Called when the user clicks 'Set Alarm'.
        _on_toggle_callback: Called when the enable checkbox changes.
        _on_dismiss_callback: Called when the user dismisses the alert.
    """

    def __init__(self, parent: tk.Widget) -> None:
        """Initialise AlarmView.

        Args:
            parent: The parent tkinter widget.
        """
        super().__init__()
        self._parent = parent
        self._hour_var: tk.StringVar = tk.StringVar(value="07")
        self._minute_var: tk.StringVar = tk.StringVar(value="00")
        self._enabled_var: tk.BooleanVar = tk.BooleanVar(value=False)
        self._status_var: tk.StringVar = tk.StringVar(value="Alarm off")
        self._on_set_callback: Optional[Callable[[], None]] = None
        self._on_toggle_callback: Optional[Callable[[bool], None]] = None
        self._on_dismiss_callback: Optional[Callable[[], None]] = None
        self._dismiss_button: Optional[tk.Button] = None
        self._alert_frame: Optional[tk.Frame] = None
        self._widgets: list = []
        logger.debug("AlarmView initialised.")

    # ------------------------------------------------------------------
    # Callback registration
    # ------------------------------------------------------------------

    def set_on_set(self, callback: Callable[[], None]) -> None:
        """Register callback for the 'Set Alarm' button.

        Args:
            callback: Zero-argument callable.
        """
        self._on_set_callback = callback

    def set_on_toggle(self, callback: Callable[[bool], None]) -> None:
        """Register callback for the enable/disable toggle.

        Args:
            callback: Callable receiving the new boolean state.
        """
        self._on_toggle_callback = callback

    def set_on_dismiss(self, callback: Callable[[], None]) -> None:
        """Register callback for the dismiss button.

        Args:
            callback: Zero-argument callable.
        """
        self._on_dismiss_callback = callback

    # ------------------------------------------------------------------
    # BaseView implementation
    # ------------------------------------------------------------------

    def build(self) -> None:
        """Create and lay out all alarm UI widgets."""
        self._frame = tk.LabelFrame(self._parent, text=" Alarm ", padx=8, pady=6)
        self._frame.pack(fill=tk.X, padx=16, pady=4)

        row = tk.Frame(self._frame)
        row.pack(fill=tk.X)

        tk.Label(row, text="Hour:").pack(side=tk.LEFT, padx=(0, 2))
        hour_entry = tk.Entry(row, textvariable=self._hour_var, width=4,
                              justify=tk.CENTER)
        hour_entry.pack(side=tk.LEFT, padx=(0, 8))

        tk.Label(row, text="Minute:").pack(side=tk.LEFT, padx=(0, 2))
        minute_entry = tk.Entry(row, textvariable=self._minute_var, width=4,
                                justify=tk.CENTER)
        minute_entry.pack(side=tk.LEFT, padx=(0, 8))

        set_btn = tk.Button(row, text="Set Alarm", command=self._on_set_clicked)
        set_btn.pack(side=tk.LEFT, padx=(0, 8))

        enable_chk = tk.Checkbutton(
            row, text="Enable",
            variable=self._enabled_var,
            command=self._on_toggle_clicked,
        )
        enable_chk.pack(side=tk.LEFT)

        status_label = tk.Label(self._frame, textvariable=self._status_var,
                                font=("Helvetica", 10))
        status_label.pack(anchor=tk.W, pady=(4, 0))

        # Alert frame (hidden until alarm fires)
        self._alert_frame = tk.Frame(self._frame)
        self._alert_label = tk.Label(
            self._alert_frame,
            text="⏰  ALARM!  ⏰",
            font=("Helvetica", 13, "bold"),
        )
        self._alert_label.pack(side=tk.LEFT, padx=(0, 10))
        self._dismiss_button = tk.Button(
            self._alert_frame, text="Dismiss", command=self._on_dismiss_clicked
        )
        self._dismiss_button.pack(side=tk.LEFT)

        self._widgets = [
            self._frame, row, hour_entry, minute_entry,
            set_btn, enable_chk, status_label,
        ]
        logger.debug("AlarmView built.")

    def apply_theme(self, colors: Dict[str, str]) -> None:
        """Apply theme colors to all alarm widgets.

        Args:
            colors: Theme color dictionary.
        """
        bg = colors["bg_window"]
        frame_bg = colors["frame_bg"]
        fg = colors["text_primary"]
        btn_bg = colors["button_bg"]
        btn_fg = colors["button_fg"]
        entry_bg = colors["entry_bg"]
        entry_fg = colors["entry_fg"]

        self._frame.configure(bg=frame_bg, fg=fg)
        for widget in self._frame.winfo_children():
            self._apply_widget_theme(widget, bg=frame_bg, fg=fg,
                                     btn_bg=btn_bg, btn_fg=btn_fg,
                                     entry_bg=entry_bg, entry_fg=entry_fg)

    def _apply_widget_theme(
        self, widget: tk.Widget, bg: str, fg: str,
        btn_bg: str, btn_fg: str, entry_bg: str, entry_fg: str
    ) -> None:
        """Recursively apply theme to a widget and its children."""
        try:
            if isinstance(widget, tk.Button):
                widget.configure(bg=btn_bg, fg=btn_fg,
                                 activebackground=btn_bg, activeforeground=btn_fg)
            elif isinstance(widget, tk.Entry):
                widget.configure(bg=entry_bg, fg=entry_fg,
                                 insertbackground=entry_fg)
            elif isinstance(widget, tk.Checkbutton):
                widget.configure(bg=bg, fg=fg,
                                 activebackground=bg, activeforeground=fg,
                                 selectcolor=bg)
            elif isinstance(widget, tk.Label):
                widget.configure(bg=bg, fg=fg)
            elif isinstance(widget, tk.Frame):
                widget.configure(bg=bg)
        except tk.TclError:
            pass
        for child in widget.winfo_children():
            self._apply_widget_theme(child, bg, fg, btn_bg, btn_fg, entry_bg, entry_fg)

    # ------------------------------------------------------------------
    # Public update methods
    # ------------------------------------------------------------------

    def update_status(self, message: str) -> None:
        """Update the status label text.

        Args:
            message: Status message to display.
        """
        self._status_var.set(message)

    def show_alert(self) -> None:
        """Show the alarm alert row."""
        self._alert_frame.pack(fill=tk.X, pady=(4, 0))

    def hide_alert(self) -> None:
        """Hide the alarm alert row."""
        self._alert_frame.pack_forget()

    def set_enabled_state(self, enabled: bool) -> None:
        """Sync the checkbox state without triggering the callback.

        Args:
            enabled: New checkbox state.
        """
        self._enabled_var.set(enabled)

    # ------------------------------------------------------------------
    # Accessors
    # ------------------------------------------------------------------

    @property
    def hour_value(self) -> str:
        """Return the raw text from the hour entry."""
        return self._hour_var.get().strip()

    @property
    def minute_value(self) -> str:
        """Return the raw text from the minute entry."""
        return self._minute_var.get().strip()

    # ------------------------------------------------------------------
    # Internal event handlers
    # ------------------------------------------------------------------

    def _on_set_clicked(self) -> None:
        """Invoke the set-alarm callback."""
        if self._on_set_callback:
            self._on_set_callback()

    def _on_toggle_clicked(self) -> None:
        """Invoke the toggle callback with the current checkbox state."""
        if self._on_toggle_callback:
            self._on_toggle_callback(self._enabled_var.get())

    def _on_dismiss_clicked(self) -> None:
        """Invoke the dismiss callback."""
        if self._on_dismiss_callback:
            self._on_dismiss_callback()
