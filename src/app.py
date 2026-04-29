"""App: main application controller — wires all components together."""

import logging
import os
import tkinter as tk
from typing import Dict

from src.models.clock import ClockModel
from src.models.alarm import AlarmModel
from src.models.stopwatch import StopwatchModel
from src.models.timer import TimerModel

from src.views.main_window import MainWindow
from src.views.analog_clock import AnalogClockView
from src.views.digital_clock import DigitalClockView
from src.views.alarm_view import AlarmView
from src.views.stopwatch_view import StopwatchView
from src.views.timer_view import TimerView
from src.views.timezone_view import TimezoneView

from src.controllers.clock_controller import ClockController
from src.controllers.alarm_controller import AlarmController
from src.controllers.stopwatch_controller import StopwatchController
from src.controllers.timer_controller import TimerController

from src.utils.theme import ThemeManager
from src.utils.audio import AudioService
from src.utils.constants import (
    THEME_LIGHT,
    APP_TITLE,
    APP_WIDTH,
)

logger = logging.getLogger(__name__)

# Resolve the assets directory relative to this file's location
_ASSETS_DIR = os.path.join(os.path.dirname(__file__), "..", "assets")
_ALARM_SOUND = os.path.join(_ASSETS_DIR, "alarm_sound.wav")


class App:
    """Top-level application controller.

    Instantiates all models, views, controllers, and utility services,
    then wires them together using dependency injection.

    Attributes:
        _window: The MainWindow (root Tk wrapper).
        _theme: The ThemeManager instance.
        _audio: The AudioService instance.
        _clock_model: ClockModel instance.
        _alarm_model: AlarmModel instance.
        _stopwatch_model: StopwatchModel instance.
        _timer_model: TimerModel instance.
    """

    def __init__(self) -> None:
        """Initialise the application and build the full UI."""
        logger.info("Initialising %s.", APP_TITLE)

        # --- Window ---
        self._window = MainWindow()
        self._window.build()
        self._window.set_on_close(self._on_close)

        # --- Theme ---
        self._theme = ThemeManager(initial_theme=THEME_LIGHT)

        # --- Audio ---
        self._audio = AudioService(sound_path=_ALARM_SOUND)

        # --- Models ---
        self._clock_model = ClockModel()
        self._alarm_model = AlarmModel()
        self._stopwatch_model = StopwatchModel()
        self._timer_model = TimerModel()

        # --- Build UI layout ---
        self._build_ui()

        # --- Controllers ---
        after_fn = self._window.after
        cancel_fn = self._window.after_cancel

        self._clock_ctrl = ClockController(
            model=self._clock_model,
            analog_view=self._analog_view,
            digital_view=self._digital_view,
            timezone_view=self._timezone_view,
            after_fn=after_fn,
            after_cancel_fn=cancel_fn,
        )
        self._alarm_ctrl = AlarmController(
            model=self._alarm_model,
            view=self._alarm_view,
            audio=self._audio,
            after_fn=after_fn,
            after_cancel_fn=cancel_fn,
        )
        self._stopwatch_ctrl = StopwatchController(
            model=self._stopwatch_model,
            view=self._stopwatch_view,
            after_fn=after_fn,
            after_cancel_fn=cancel_fn,
        )
        self._timer_ctrl = TimerController(
            model=self._timer_model,
            view=self._timer_view,
            audio=self._audio,
            after_fn=after_fn,
            after_cancel_fn=cancel_fn,
        )

        # Wire timezone view callback
        self._timezone_view.set_on_change(self._clock_ctrl.on_timezone_changed)
        self._timezone_view.populate_timezones(self._clock_model.get_timezone_names())

        # Register theme observers
        self._theme.subscribe(self._apply_theme_to_all)

        # Apply initial theme
        self._apply_theme_to_all(self._theme.colors)

        logger.info("App initialised successfully.")

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        """Create the scrollable main frame and all view panels."""
        root_frame = self._window.frame

        # ---- Top bar: title + theme toggle ----
        top_bar = tk.Frame(root_frame)
        top_bar.pack(fill=tk.X, padx=16, pady=(8, 0))

        self._title_label = tk.Label(
            top_bar,
            text=APP_TITLE,
            font=("Helvetica", 16, "bold"),
        )
        self._title_label.pack(side=tk.LEFT)

        self._theme_btn = tk.Button(
            top_bar,
            text="🌙 Dark Mode",
            command=self._toggle_theme,
            relief=tk.FLAT,
            padx=8,
        )
        self._theme_btn.pack(side=tk.RIGHT)

        # ---- Scrollable canvas for the main content ----
        canvas_container = tk.Frame(root_frame)
        canvas_container.pack(fill=tk.BOTH, expand=True)

        self._scroll_canvas = tk.Canvas(canvas_container, highlightthickness=0)
        scrollbar = tk.Scrollbar(
            canvas_container, orient=tk.VERTICAL,
            command=self._scroll_canvas.yview
        )
        self._scroll_canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self._scroll_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self._content_frame = tk.Frame(self._scroll_canvas)
        self._canvas_window = self._scroll_canvas.create_window(
            (0, 0), window=self._content_frame, anchor=tk.NW
        )

        self._content_frame.bind("<Configure>", self._on_frame_configure)
        self._scroll_canvas.bind("<Configure>", self._on_canvas_configure)

        # Bind mouse wheel scrolling
        self._scroll_canvas.bind_all("<MouseWheel>", self._on_mousewheel)

        # ---- Analog clock ----
        self._analog_view = AnalogClockView(self._content_frame)
        self._analog_view.build()

        # ---- Digital clock ----
        self._digital_view = DigitalClockView(self._content_frame)
        self._digital_view.build()

        # ---- Separator ----
        tk.Frame(self._content_frame, height=1).pack(fill=tk.X, padx=16, pady=2)

        # ---- Alarm ----
        self._alarm_view = AlarmView(self._content_frame)
        self._alarm_view.build()

        # ---- Stopwatch ----
        self._stopwatch_view = StopwatchView(self._content_frame)
        self._stopwatch_view.build()

        # ---- Timer ----
        self._timer_view = TimerView(self._content_frame)
        self._timer_view.build()

        # ---- Timezone ----
        self._timezone_view = TimezoneView(self._content_frame)
        self._timezone_view.build()

        # Bottom padding
        tk.Frame(self._content_frame, height=12).pack()

        self._top_bar = top_bar
        self._canvas_container = canvas_container

    # ------------------------------------------------------------------
    # Theme management
    # ------------------------------------------------------------------

    def _toggle_theme(self) -> None:
        """Toggle between light and dark themes."""
        new_theme = self._theme.toggle()
        self._theme_btn.configure(
            text="☀️ Light Mode" if self._theme.is_dark() else "🌙 Dark Mode"
        )
        logger.info("Theme toggled to '%s'.", new_theme)

    def _apply_theme_to_all(self, colors: Dict[str, str]) -> None:
        """Apply the given color palette to every view and widget.

        Args:
            colors: Theme color dictionary.
        """
        bg = colors["bg_window"]
        fg = colors["text_primary"]
        btn_bg = colors["button_bg"]
        btn_fg = colors["button_fg"]

        self._window.apply_theme(colors)
        self._scroll_canvas.configure(bg=bg)
        self._content_frame.configure(bg=bg)
        self._canvas_container.configure(bg=bg)
        self._top_bar.configure(bg=bg)
        self._title_label.configure(bg=bg, fg=fg)
        self._theme_btn.configure(
            bg=btn_bg, fg=btn_fg,
            activebackground=btn_bg, activeforeground=btn_fg,
        )

        self._analog_view.apply_theme(colors)
        self._digital_view.apply_theme(colors)
        self._alarm_view.apply_theme(colors)
        self._stopwatch_view.apply_theme(colors)
        self._timer_view.apply_theme(colors)
        self._timezone_view.apply_theme(colors)

        # Redraw analog clock with new colors immediately
        try:
            h, m, s = self._clock_model.get_hand_angles()
            self._analog_view.draw(h, m, s)
        except Exception as exc:
            logger.debug("Theme redraw skipped: %s", exc)

    # ------------------------------------------------------------------
    # Scroll helpers
    # ------------------------------------------------------------------

    def _on_frame_configure(self, _event: tk.Event) -> None:
        """Update scroll region when the content frame resizes."""
        self._scroll_canvas.configure(
            scrollregion=self._scroll_canvas.bbox("all")
        )

    def _on_canvas_configure(self, event: tk.Event) -> None:
        """Keep the content frame width in sync with the canvas."""
        self._scroll_canvas.itemconfig(self._canvas_window, width=event.width)

    def _on_mousewheel(self, event: tk.Event) -> None:
        """Handle mouse wheel scrolling."""
        self._scroll_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    # ------------------------------------------------------------------
    # Application lifecycle
    # ------------------------------------------------------------------

    def run(self) -> None:
        """Start all controllers and enter the tkinter event loop."""
        self._clock_ctrl.start()
        self._alarm_ctrl.start()
        self._stopwatch_ctrl.start()
        self._timer_ctrl.start()
        logger.info("All controllers started. Entering mainloop.")
        self._window.mainloop()

    def _on_close(self) -> None:
        """Gracefully shut down all controllers and destroy the window."""
        logger.info("Shutting down application.")
        self._clock_ctrl.stop()
        self._alarm_ctrl.stop()
        self._stopwatch_ctrl.stop()
        self._timer_ctrl.stop()
        self._window.destroy()
