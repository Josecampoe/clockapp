"""App: main application controller — wires all components together."""

import logging
import os
import tkinter as tk
from typing import Dict, Optional

import customtkinter as ctk

from src.models.clock     import ClockModel
from src.models.alarm     import AlarmModel
from src.models.stopwatch import StopwatchModel
from src.models.timer     import TimerModel

from src.views.main_window    import MainWindow
from src.views.analog_clock   import AnalogClockView
from src.views.digital_clock  import DigitalClockView
from src.views.alarm_view     import AlarmView
from src.views.stopwatch_view import StopwatchView
from src.views.timer_view     import TimerView
from src.views.timezone_view  import TimezoneView

from src.controllers.clock_controller     import ClockController
from src.controllers.alarm_controller     import AlarmController
from src.controllers.stopwatch_controller import StopwatchController
from src.controllers.timer_controller     import TimerController

from src.utils.theme     import ThemeManager
from src.utils.audio     import AudioService
from src.utils.constants import THEME_DARK, THEME_LIGHT, APP_TITLE, APP_VERSION

logger = logging.getLogger(__name__)

_ASSETS_DIR  = os.path.join(os.path.dirname(__file__), "..", "assets")
_ALARM_SOUND = os.path.join(_ASSETS_DIR, "alarm_sound.wav")

# Screen keys
SCREEN_CLOCK     = "clock"
SCREEN_ALARM     = "alarm"
SCREEN_STOPWATCH = "stopwatch"
SCREEN_TIMER     = "timer"
SCREEN_WORLD     = "world"
SCREEN_SETTINGS  = "settings"

_NAV_ITEMS = [
    (SCREEN_CLOCK,     "🕐", "Reloj"),
    (SCREEN_ALARM,     "⏰", "Alarma"),
    (SCREEN_STOPWATCH, "⏱", "Cronómetro"),
    (SCREEN_TIMER,     "⏳", "Temporizador"),
    (SCREEN_WORLD,     "🌍", "Mundial"),
    (SCREEN_SETTINGS,  "⚙️", "Ajustes"),
]


class App:
    """Top-level application controller.

    Layout
    ------
    ┌──────────────────────────────────┐
    │  Top bar  (title + theme toggle) │
    ├──────────────────────────────────┤
    │   Content area  (swappable)      │
    ├──────────────────────────────────┤
    │  Bottom nav  (6 pill buttons)    │
    └──────────────────────────────────┘

    Keyboard shortcuts
    ------------------
    Space       — Start/Stop stopwatch (when on stopwatch screen)
    L           — Record lap (when stopwatch is running)
    R           — Reset stopwatch / timer
    1–6         — Switch to screen by nav index
    Ctrl+T      — Toggle theme
    """

    def __init__(self) -> None:
        logger.info("Initialising %s %s.", APP_TITLE, APP_VERSION)

        ctk.set_appearance_mode("dark")

        self._window = MainWindow()
        self._window.build()
        self._window.set_on_close(self._on_close)

        self._theme = ThemeManager(initial_theme=THEME_DARK)
        self._audio = AudioService(sound_path=_ALARM_SOUND)

        self._clock_model     = ClockModel()
        self._alarm_model     = AlarmModel()
        self._stopwatch_model = StopwatchModel()
        self._timer_model     = TimerModel()

        self._active_screen: str = SCREEN_CLOCK
        self._nav_buttons: Dict[str, ctk.CTkButton] = {}
        self._screens:     Dict[str, ctk.CTkFrame]  = {}

        self._build_ui()
        self._wire_controllers()
        self._bind_keyboard_shortcuts()

        self._theme.subscribe(self._apply_theme_to_all)
        self._apply_theme_to_all(self._theme.colors)
        self._show_screen(SCREEN_CLOCK)

        logger.info("App ready.")

    # ══════════════════════════════════════════════════════════════════
    # UI construction
    # ══════════════════════════════════════════════════════════════════

    def _build_ui(self) -> None:
        root = self._window.frame

        # ── Top bar ───────────────────────────────────────────────────
        self._top_bar = ctk.CTkFrame(root, height=50, corner_radius=0)
        self._top_bar.pack(side=tk.TOP, fill=tk.X)
        self._top_bar.pack_propagate(False)

        self._title_label = ctk.CTkLabel(
            self._top_bar, text=f"  {APP_TITLE}",
            font=ctk.CTkFont(size=16, weight="bold"),
        )
        self._title_label.pack(side=tk.LEFT, padx=10)

        # Offset indicator (shown when manual offset is active)
        self._offset_badge = ctk.CTkLabel(
            self._top_bar, text="⚠ Hora ajustada",
            font=ctk.CTkFont(size=10),
            text_color="#F59E0B",
        )
        # Not packed initially

        self._theme_btn = ctk.CTkButton(
            self._top_bar, text="☀️  Modo Claro",
            width=130, height=32, corner_radius=16,
            font=ctk.CTkFont(size=12),
            command=self._toggle_theme,
        )
        self._theme_btn.pack(side=tk.RIGHT, padx=12, pady=9)

        # ── Content area ──────────────────────────────────────────────
        self._content_area = ctk.CTkFrame(root, corner_radius=0, fg_color="transparent")
        self._content_area.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self._build_clock_screen()
        self._build_alarm_screen()
        self._build_stopwatch_screen()
        self._build_timer_screen()
        self._build_world_screen()
        self._build_settings_screen()

        # ── Bottom nav ────────────────────────────────────────────────
        self._nav_bar = ctk.CTkFrame(root, height=68, corner_radius=0)
        self._nav_bar.pack(side=tk.BOTTOM, fill=tk.X)
        self._nav_bar.pack_propagate(False)

        self._nav_sep = ctk.CTkFrame(self._nav_bar, height=1, corner_radius=0)
        self._nav_sep.pack(side=tk.TOP, fill=tk.X)

        nav_inner = ctk.CTkFrame(self._nav_bar, fg_color="transparent")
        nav_inner.pack(fill=tk.BOTH, expand=True)
        self._nav_inner = nav_inner

        for key, emoji, label in _NAV_ITEMS:
            col = ctk.CTkFrame(nav_inner, fg_color="transparent")
            col.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)
            btn = ctk.CTkButton(
                col,
                text=f"{emoji}\n{label}",
                font=ctk.CTkFont(size=9),
                width=80, height=56,
                corner_radius=0,
                fg_color="transparent",
                hover_color=None,
                command=lambda k=key: self._show_screen(k),
            )
            btn.pack(expand=True, fill=tk.BOTH)
            self._nav_buttons[key] = btn

    # ── Screen builders ────────────────────────────────────────────────

    def _make_screen(self, key: str) -> ctk.CTkScrollableFrame:
        frame = ctk.CTkScrollableFrame(
            self._content_area, corner_radius=0, fg_color="transparent",
        )
        self._screens[key] = frame
        return frame

    def _build_clock_screen(self) -> None:
        frame = self._make_screen(SCREEN_CLOCK)

        self._analog_view = AnalogClockView(frame)
        self._analog_view.build()

        self._digital_view = DigitalClockView(frame)
        self._digital_view.build()

        self._reset_time_btn = ctk.CTkButton(
            frame, text="↺  Restablecer hora real",
            width=200, height=30, corner_radius=15,
            font=ctk.CTkFont(size=11),
            command=self._reset_clock_offset,
        )
        self._reset_time_btn.pack(pady=(0, 10))

    def _build_alarm_screen(self) -> None:
        frame = self._make_screen(SCREEN_ALARM)
        ctk.CTkLabel(frame, text="Alarma",
                     font=ctk.CTkFont(size=22, weight="bold")).pack(pady=(20, 4))
        self._alarm_view = AlarmView(frame)
        self._alarm_view.build()

    def _build_stopwatch_screen(self) -> None:
        frame = self._make_screen(SCREEN_STOPWATCH)
        ctk.CTkLabel(frame, text="Cronómetro",
                     font=ctk.CTkFont(size=22, weight="bold")).pack(pady=(20, 4))
        self._stopwatch_view = StopwatchView(frame)
        self._stopwatch_view.build()

    def _build_timer_screen(self) -> None:
        frame = self._make_screen(SCREEN_TIMER)
        ctk.CTkLabel(frame, text="Temporizador",
                     font=ctk.CTkFont(size=22, weight="bold")).pack(pady=(20, 4))
        self._timer_view = TimerView(frame)
        self._timer_view.build()

    def _build_world_screen(self) -> None:
        frame = self._make_screen(SCREEN_WORLD)
        ctk.CTkLabel(frame, text="Reloj Mundial",
                     font=ctk.CTkFont(size=22, weight="bold")).pack(pady=(20, 4))
        self._timezone_view = TimezoneView(frame)
        self._timezone_view.build()

    def _build_settings_screen(self) -> None:
        frame = self._make_screen(SCREEN_SETTINGS)

        ctk.CTkLabel(frame, text="Ajustes",
                     font=ctk.CTkFont(size=22, weight="bold")).pack(pady=(20, 4))

        card = ctk.CTkFrame(frame, corner_radius=16)
        card.pack(fill=tk.X, padx=20, pady=8)
        self._settings_card = card

        ctk.CTkLabel(card, text="Apariencia",
                     font=ctk.CTkFont(size=14, weight="bold")).pack(anchor=tk.W, padx=16, pady=(14, 6))

        # Theme toggle inside settings
        theme_row = ctk.CTkFrame(card, fg_color="transparent")
        theme_row.pack(fill=tk.X, padx=16, pady=4)
        ctk.CTkLabel(theme_row, text="Tema oscuro",
                     font=ctk.CTkFont(size=12)).pack(side=tk.LEFT)
        self._dark_switch = ctk.CTkSwitch(
            theme_row, text="",
            command=self._toggle_theme,
        )
        self._dark_switch.select()   # dark by default
        self._dark_switch.pack(side=tk.RIGHT)

        ctk.CTkFrame(card, height=1, corner_radius=0).pack(fill=tk.X, padx=16, pady=8)

        # About section
        ctk.CTkLabel(card, text="Acerca de",
                     font=ctk.CTkFont(size=14, weight="bold")).pack(anchor=tk.W, padx=16, pady=(4, 6))

        about_text = (
            f"{APP_TITLE}  v{APP_VERSION}\n"
            "Reloj analógico y digital con alarma,\n"
            "cronómetro con vueltas y temporizador\n"
            "con presets.\n\n"
            "Atajos de teclado:\n"
            "  Espacio  →  Iniciar / Detener cronómetro\n"
            "  L        →  Registrar vuelta\n"
            "  R        →  Reiniciar\n"
            "  1–6      →  Cambiar pantalla\n"
            "  Ctrl+T   →  Cambiar tema"
        )
        ctk.CTkLabel(
            card, text=about_text,
            font=ctk.CTkFont(size=11),
            justify="left",
        ).pack(anchor=tk.W, padx=16, pady=(0, 16))

    # ══════════════════════════════════════════════════════════════════
    # Controller wiring
    # ══════════════════════════════════════════════════════════════════

    def _wire_controllers(self) -> None:
        after_fn  = self._window.after
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

        self._timezone_view.set_on_change(self._clock_ctrl.on_timezone_changed)
        self._timezone_view.populate_timezones(self._clock_model.get_timezone_names())

        # Show/hide offset badge when clock model changes
        self._clock_model.subscribe(self._update_offset_badge)

    # ══════════════════════════════════════════════════════════════════
    # Keyboard shortcuts
    # ══════════════════════════════════════════════════════════════════

    def _bind_keyboard_shortcuts(self) -> None:
        root = self._window.root
        root.bind("<space>",   self._kb_space)
        root.bind("<l>",       self._kb_lap)
        root.bind("<L>",       self._kb_lap)
        root.bind("<r>",       self._kb_reset)
        root.bind("<R>",       self._kb_reset)
        root.bind("<Control-t>", lambda _e: self._toggle_theme())
        for i, (key, *_) in enumerate(_NAV_ITEMS, start=1):
            root.bind(str(i), lambda _e, k=key: self._show_screen(k))

    def _kb_space(self, _event: tk.Event) -> None:
        """Space: start/stop stopwatch (regardless of active screen)."""
        if self._stopwatch_model.running:
            self._stopwatch_model.stop()
        else:
            self._stopwatch_model.start()

    def _kb_lap(self, _event: tk.Event) -> None:
        if self._stopwatch_model.running:
            self._stopwatch_model.lap()

    def _kb_reset(self, _event: tk.Event) -> None:
        if self._active_screen == SCREEN_STOPWATCH:
            self._stopwatch_model.reset()
        elif self._active_screen == SCREEN_TIMER:
            self._timer_model.reset()

    # ══════════════════════════════════════════════════════════════════
    # Navigation
    # ══════════════════════════════════════════════════════════════════

    def _show_screen(self, key: str) -> None:
        for k, frame in self._screens.items():
            if k == key:
                frame.pack(fill=tk.BOTH, expand=True)
            else:
                frame.pack_forget()
        self._active_screen = key
        self._update_nav_highlight(key)

    def _update_nav_highlight(self, active_key: str) -> None:
        colors = self._theme.colors
        for key, btn in self._nav_buttons.items():
            if key == active_key:
                btn.configure(
                    fg_color=colors["accent"],
                    text_color="#FFFFFF",
                    hover_color=colors["button_hover"],
                )
            else:
                btn.configure(
                    fg_color="transparent",
                    text_color=colors["text_secondary"],
                    hover_color=colors["nav_border"],
                )

    # ══════════════════════════════════════════════════════════════════
    # Theme
    # ══════════════════════════════════════════════════════════════════

    def _toggle_theme(self) -> None:
        self._theme.toggle()
        is_dark = self._theme.is_dark()
        ctk.set_appearance_mode("dark" if is_dark else "light")
        self._theme_btn.configure(
            text="☀️  Modo Claro" if is_dark else "🌙  Modo Oscuro"
        )
        # Sync settings switch
        if hasattr(self, "_dark_switch"):
            if is_dark:
                self._dark_switch.select()
            else:
                self._dark_switch.deselect()

    def _apply_theme_to_all(self, colors: Dict[str, str]) -> None:
        bg     = colors["bg_window"]
        nav_bg = colors["nav_bg"]
        card   = colors["bg_card"]

        self._window.apply_theme(colors)
        self._top_bar.configure(fg_color=card)
        self._title_label.configure(text_color=colors["text_primary"])
        self._theme_btn.configure(
            fg_color=colors["button2_bg"], text_color=colors["button2_fg"],
            hover_color=colors["entry_bg"],
        )

        self._content_area.configure(fg_color=bg)
        for frame in self._screens.values():
            frame.configure(fg_color=bg)
            for child in frame.winfo_children():
                if isinstance(child, ctk.CTkLabel):
                    try:
                        child.configure(text_color=colors["text_primary"])
                    except Exception:
                        pass

        self._nav_bar.configure(fg_color=nav_bg)
        self._nav_sep.configure(fg_color=colors["nav_border"])
        self._nav_inner.configure(fg_color=nav_bg)
        self._update_nav_highlight(self._active_screen)

        if hasattr(self, "_reset_time_btn"):
            self._reset_time_btn.configure(
                fg_color=colors["button2_bg"], text_color=colors["text_secondary"],
                hover_color=colors["entry_bg"],
            )
        if hasattr(self, "_settings_card"):
            self._settings_card.configure(fg_color=card)

        self._analog_view.apply_theme(colors)
        self._digital_view.apply_theme(colors)
        self._alarm_view.apply_theme(colors)
        self._stopwatch_view.apply_theme(colors)
        self._timer_view.apply_theme(colors)
        self._timezone_view.apply_theme(colors)

        try:
            h, m, s = self._clock_model.get_hand_angles()
            self._analog_view.draw(h, m, s)
        except Exception as exc:
            logger.debug("Theme redraw skipped: %s", exc)

    # ══════════════════════════════════════════════════════════════════
    # Clock offset badge
    # ══════════════════════════════════════════════════════════════════

    def _update_offset_badge(self) -> None:
        """Show/hide the 'Hora ajustada' badge in the top bar."""
        if self._clock_model.has_manual_offset:
            self._offset_badge.pack(side=tk.LEFT, padx=4)
        else:
            self._offset_badge.pack_forget()

    def _reset_clock_offset(self) -> None:
        self._clock_model.reset_offset()

    # ══════════════════════════════════════════════════════════════════
    # Lifecycle
    # ══════════════════════════════════════════════════════════════════

    def run(self) -> None:
        self._clock_ctrl.start()
        self._alarm_ctrl.start()
        self._stopwatch_ctrl.start()
        self._timer_ctrl.start()
        self._window.mainloop()

    def _on_close(self) -> None:
        self._clock_ctrl.stop()
        self._alarm_ctrl.stop()
        self._stopwatch_ctrl.stop()
        self._timer_ctrl.stop()
        self._window.destroy()
