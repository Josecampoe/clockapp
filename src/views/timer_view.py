"""TimerView: countdown timer with presets and progress arc."""

import logging
import tkinter as tk
from typing import Callable, Dict, List, Optional

import customtkinter as ctk

from src.views.main_window import BaseView
from src.models.timer import TIMER_PRESETS

logger = logging.getLogger(__name__)


class TimerView(BaseView):
    """Countdown timer panel with quick-set presets and a progress bar."""

    def __init__(self, parent: tk.Widget) -> None:
        super().__init__()
        self._parent = parent
        self._remaining_var = tk.StringVar(value="00:00:00")
        self._hours_var     = tk.StringVar(value="0")
        self._minutes_var   = tk.StringVar(value="5")
        self._seconds_var   = tk.StringVar(value="0")

        self._on_set_callback:     Optional[Callable[[], None]]     = None
        self._on_start_callback:   Optional[Callable[[], None]]     = None
        self._on_pause_callback:   Optional[Callable[[], None]]     = None
        self._on_reset_callback:   Optional[Callable[[], None]]     = None
        self._on_dismiss_callback: Optional[Callable[[], None]]     = None
        self._on_preset_callback:  Optional[Callable[[int], None]]  = None

        self._start_btn:  Optional[ctk.CTkButton]      = None
        self._pause_btn:  Optional[ctk.CTkButton]      = None
        self._alert_frame: Optional[ctk.CTkFrame]      = None
        self._progress:   Optional[ctk.CTkProgressBar] = None
        logger.debug("TimerView initialised.")

    # ── Callbacks ─────────────────────────────────────────────────────
    def set_on_set(self,     cb: Callable[[], None])    -> None: self._on_set_callback     = cb
    def set_on_start(self,   cb: Callable[[], None])    -> None: self._on_start_callback   = cb
    def set_on_pause(self,   cb: Callable[[], None])    -> None: self._on_pause_callback   = cb
    def set_on_reset(self,   cb: Callable[[], None])    -> None: self._on_reset_callback   = cb
    def set_on_dismiss(self, cb: Callable[[], None])    -> None: self._on_dismiss_callback = cb
    def set_on_preset(self,  cb: Callable[[int], None]) -> None: self._on_preset_callback  = cb

    # ── Build ──────────────────────────────────────────────────────────
    def build(self) -> None:
        self._frame = ctk.CTkFrame(self._parent, corner_radius=16)
        self._frame.pack(fill=tk.X, padx=20, pady=8)

        # ── Header ────────────────────────────────────────────────────
        ctk.CTkLabel(
            self._frame, text="⏳  Temporizador",
            font=ctk.CTkFont(size=15, weight="bold"),
        ).pack(anchor=tk.W, padx=16, pady=(14, 6))

        # ── Preset buttons ────────────────────────────────────────────
        preset_row = ctk.CTkFrame(self._frame, fg_color="transparent")
        preset_row.pack(fill=tk.X, padx=16, pady=(0, 8))

        ctk.CTkLabel(
            preset_row, text="Rápido:",
            font=ctk.CTkFont(size=11),
        ).pack(side=tk.LEFT, padx=(0, 6))

        for idx, (label, *_) in enumerate(TIMER_PRESETS):
            ctk.CTkButton(
                preset_row, text=label,
                width=62, height=26, corner_radius=13,
                font=ctk.CTkFont(size=10),
                command=lambda i=idx: self._on_preset_clicked(i),
            ).pack(side=tk.LEFT, padx=2)

        # ── Custom duration inputs ────────────────────────────────────
        inp = ctk.CTkFrame(self._frame, fg_color="transparent")
        inp.pack(fill=tk.X, padx=16, pady=4)
        self._input_row = inp

        for lbl, var, validate_fn in [
            ("H", self._hours_var,   self._validate_hours),
            ("M", self._minutes_var, self._validate_minsec),
            ("S", self._seconds_var, self._validate_minsec),
        ]:
            ctk.CTkLabel(inp, text=lbl, font=ctk.CTkFont(size=13, weight="bold")).pack(side=tk.LEFT, padx=(0, 2))
            ctk.CTkEntry(
                inp, textvariable=var, width=52, justify="center",
                font=ctk.CTkFont(size=14, weight="bold"),
                validate="key",
                validatecommand=(self._parent.register(validate_fn), "%P"),
            ).pack(side=tk.LEFT, padx=(0, 10))

        ctk.CTkButton(
            inp, text="Establecer", width=110, height=32,
            corner_radius=16, font=ctk.CTkFont(size=12, weight="bold"),
            command=self._on_set_clicked,
        ).pack(side=tk.LEFT)

        # ── Countdown display ─────────────────────────────────────────
        self._remaining_label = ctk.CTkLabel(
            self._frame, textvariable=self._remaining_var,
            font=ctk.CTkFont(family="Courier New", size=44, weight="bold"),
        )
        self._remaining_label.pack(pady=(10, 4))

        # ── Progress bar ──────────────────────────────────────────────
        self._progress = ctk.CTkProgressBar(
            self._frame, height=8, corner_radius=4,
        )
        self._progress.set(0)
        self._progress.pack(fill=tk.X, padx=24, pady=(0, 8))

        # ── Control buttons ───────────────────────────────────────────
        btn_row = ctk.CTkFrame(self._frame, fg_color="transparent")
        btn_row.pack(pady=(4, 10))
        self._btn_row = btn_row

        self._start_btn = ctk.CTkButton(
            btn_row, text="▶  Iniciar", width=115, height=40,
            corner_radius=20, font=ctk.CTkFont(size=13, weight="bold"),
            command=self._on_start_clicked,
        )
        self._start_btn.pack(side=tk.LEFT, padx=6)

        self._pause_btn = ctk.CTkButton(
            btn_row, text="⏸  Pausar", width=115, height=40,
            corner_radius=20, font=ctk.CTkFont(size=13, weight="bold"),
            state="disabled", command=self._on_pause_clicked,
        )
        self._pause_btn.pack(side=tk.LEFT, padx=6)

        ctk.CTkButton(
            btn_row, text="↺  Reiniciar", width=115, height=40,
            corner_radius=20, font=ctk.CTkFont(size=13, weight="bold"),
            command=self._on_reset_clicked,
        ).pack(side=tk.LEFT, padx=6)

        # ── Alert banner ──────────────────────────────────────────────
        self._alert_frame = ctk.CTkFrame(self._frame, corner_radius=12, fg_color="#F59E0B")
        alert_inner = ctk.CTkFrame(self._alert_frame, fg_color="transparent")
        alert_inner.pack(fill=tk.X, padx=12, pady=10)

        ctk.CTkLabel(
            alert_inner, text="⏱  ¡Tiempo agotado!",
            font=ctk.CTkFont(size=14, weight="bold"), text_color="white",
        ).pack(side=tk.LEFT, padx=(0, 16))

        ctk.CTkButton(
            alert_inner, text="✕  Descartar",
            width=110, height=30, corner_radius=15,
            fg_color="white", text_color="#F59E0B", hover_color="#FEF3C7",
            font=ctk.CTkFont(size=11, weight="bold"),
            command=self._on_dismiss_clicked,
        ).pack(side=tk.LEFT)

        logger.debug("TimerView built.")

    # ── Theme ──────────────────────────────────────────────────────────
    def apply_theme(self, colors: Dict[str, str]) -> None:
        self._frame.configure(fg_color=colors["bg_card"])
        if self._remaining_label:
            self._remaining_label.configure(text_color=colors["accent"])
        if self._progress:
            self._progress.configure(
                progress_color=colors["accent"],
                fg_color=colors["entry_bg"],
            )
        if self._start_btn:
            self._start_btn.configure(fg_color=colors["success"], hover_color="#059669")
        if self._pause_btn:
            self._pause_btn.configure(fg_color=colors["warning"], hover_color="#D97706")

    # ── Public API ─────────────────────────────────────────────────────
    def update_remaining(self, s: str) -> None:
        self._remaining_var.set(s)

    def update_progress(self, fraction: float) -> None:
        """Update the progress bar (0.0 = empty, 1.0 = full/done)."""
        if self._progress:
            self._progress.set(max(0.0, min(1.0, fraction)))

    def show_alert(self) -> None:
        self._alert_frame.pack(fill=tk.X, padx=16, pady=(0, 12))

    def hide_alert(self) -> None:
        self._alert_frame.pack_forget()

    def set_running_state(self, running: bool) -> None:
        if self._start_btn:
            self._start_btn.configure(state="disabled" if running else "normal")
        if self._pause_btn:
            self._pause_btn.configure(state="normal" if running else "disabled")

    @property
    def hours_value(self) -> str:   return self._hours_var.get().strip()
    @property
    def minutes_value(self) -> str: return self._minutes_var.get().strip()
    @property
    def seconds_value(self) -> str: return self._seconds_var.get().strip()

    # ── Validation ────────────────────────────────────────────────────
    @staticmethod
    def _validate_hours(value: str) -> bool:
        if value == "": return True
        try: return 0 <= int(value) <= 23 and len(value) <= 2
        except ValueError: return False

    @staticmethod
    def _validate_minsec(value: str) -> bool:
        if value == "": return True
        try: return 0 <= int(value) <= 59 and len(value) <= 2
        except ValueError: return False

    # ── Handlers ──────────────────────────────────────────────────────
    def _on_set_clicked(self):
        if self._on_set_callback: self._on_set_callback()
    def _on_start_clicked(self):
        if self._on_start_callback: self._on_start_callback()
    def _on_pause_clicked(self):
        if self._on_pause_callback: self._on_pause_callback()
    def _on_reset_clicked(self):
        if self._on_reset_callback: self._on_reset_callback()
    def _on_dismiss_clicked(self):
        if self._on_dismiss_callback: self._on_dismiss_callback()
    def _on_preset_clicked(self, idx: int):
        if self._on_preset_callback: self._on_preset_callback(idx)
