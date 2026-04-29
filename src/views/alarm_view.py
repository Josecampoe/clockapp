"""AlarmView: modern alarm panel with snooze support."""

import logging
import tkinter as tk
from typing import Callable, Dict, Optional

import customtkinter as ctk

from src.views.main_window import BaseView

logger = logging.getLogger(__name__)


class AlarmView(BaseView):
    """Alarm configuration panel with set/enable/snooze/dismiss controls."""

    def __init__(self, parent: tk.Widget) -> None:
        super().__init__()
        self._parent = parent
        self._hour_var    = tk.StringVar(value="07")
        self._minute_var  = tk.StringVar(value="00")
        self._enabled_var = tk.BooleanVar(value=False)
        self._status_var  = tk.StringVar(value="Alarma desactivada")

        self._on_set_callback:     Optional[Callable[[], None]]     = None
        self._on_toggle_callback:  Optional[Callable[[bool], None]] = None
        self._on_dismiss_callback: Optional[Callable[[], None]]     = None
        self._on_snooze_callback:  Optional[Callable[[], None]]     = None

        self._alert_frame: Optional[ctk.CTkFrame] = None
        self._switch:      Optional[ctk.CTkSwitch] = None
        self._status_label: Optional[ctk.CTkLabel] = None
        logger.debug("AlarmView initialised.")

    # ── Callback registration ──────────────────────────────────────────
    def set_on_set(self,     cb: Callable[[], None])     -> None: self._on_set_callback     = cb
    def set_on_toggle(self,  cb: Callable[[bool], None]) -> None: self._on_toggle_callback  = cb
    def set_on_dismiss(self, cb: Callable[[], None])     -> None: self._on_dismiss_callback = cb
    def set_on_snooze(self,  cb: Callable[[], None])     -> None: self._on_snooze_callback  = cb

    # ── Build ──────────────────────────────────────────────────────────
    def build(self) -> None:
        self._frame = ctk.CTkFrame(self._parent, corner_radius=16)
        self._frame.pack(fill=tk.X, padx=20, pady=8)

        # ── Header ────────────────────────────────────────────────────
        ctk.CTkLabel(
            self._frame, text="⏰  Configurar Alarma",
            font=ctk.CTkFont(size=15, weight="bold"),
        ).pack(anchor=tk.W, padx=16, pady=(14, 6))

        # ── Time inputs ───────────────────────────────────────────────
        row = ctk.CTkFrame(self._frame, fg_color="transparent")
        row.pack(fill=tk.X, padx=16, pady=4)

        ctk.CTkLabel(row, text="Hora", font=ctk.CTkFont(size=12)).pack(side=tk.LEFT)
        ctk.CTkEntry(
            row, textvariable=self._hour_var, width=56,
            justify="center", font=ctk.CTkFont(size=16, weight="bold"),
            validate="key",
            validatecommand=(self._parent.register(self._validate_hour), "%P"),
        ).pack(side=tk.LEFT, padx=(6, 16))

        ctk.CTkLabel(row, text="Minuto", font=ctk.CTkFont(size=12)).pack(side=tk.LEFT)
        ctk.CTkEntry(
            row, textvariable=self._minute_var, width=56,
            justify="center", font=ctk.CTkFont(size=16, weight="bold"),
            validate="key",
            validatecommand=(self._parent.register(self._validate_minute), "%P"),
        ).pack(side=tk.LEFT, padx=(6, 16))

        ctk.CTkButton(
            row, text="Establecer", width=110, height=34,
            corner_radius=17, font=ctk.CTkFont(size=12, weight="bold"),
            command=self._on_set_clicked,
        ).pack(side=tk.LEFT)

        # ── Enable switch ─────────────────────────────────────────────
        sw_row = ctk.CTkFrame(self._frame, fg_color="transparent")
        sw_row.pack(fill=tk.X, padx=16, pady=(6, 4))

        self._switch = ctk.CTkSwitch(
            sw_row, text="Activar alarma",
            variable=self._enabled_var,
            command=self._on_toggle_clicked,
            font=ctk.CTkFont(size=12),
        )
        self._switch.pack(side=tk.LEFT)

        # ── Status label ──────────────────────────────────────────────
        self._status_label = ctk.CTkLabel(
            self._frame, textvariable=self._status_var,
            font=ctk.CTkFont(size=11),
        )
        self._status_label.pack(anchor=tk.W, padx=16, pady=(0, 8))

        # ── Alert banner (hidden until alarm fires) ───────────────────
        self._alert_frame = ctk.CTkFrame(
            self._frame, corner_radius=12, fg_color="#EF4444",
        )
        alert_inner = ctk.CTkFrame(self._alert_frame, fg_color="transparent")
        alert_inner.pack(fill=tk.X, padx=12, pady=10)

        ctk.CTkLabel(
            alert_inner, text="⏰  ¡ALARMA!",
            font=ctk.CTkFont(size=15, weight="bold"), text_color="white",
        ).pack(side=tk.LEFT, padx=(0, 16))

        ctk.CTkButton(
            alert_inner, text="💤  Posponer 5 min",
            width=140, height=30, corner_radius=15,
            fg_color="white", text_color="#EF4444", hover_color="#FEE2E2",
            font=ctk.CTkFont(size=11, weight="bold"),
            command=self._on_snooze_clicked,
        ).pack(side=tk.LEFT, padx=(0, 8))

        ctk.CTkButton(
            alert_inner, text="✕  Descartar",
            width=110, height=30, corner_radius=15,
            fg_color="#C53030", text_color="white",
            hover_color="#9B2C2C",
            font=ctk.CTkFont(size=11),
            command=self._on_dismiss_clicked,
        ).pack(side=tk.LEFT)

        logger.debug("AlarmView built.")

    # ── Theme ──────────────────────────────────────────────────────────
    def apply_theme(self, colors: Dict[str, str]) -> None:
        self._frame.configure(fg_color=colors["bg_card"])
        if self._status_label:
            self._status_label.configure(text_color=colors["text_secondary"])

    # ── Public API ─────────────────────────────────────────────────────
    def update_status(self, message: str) -> None:
        self._status_var.set(message)

    def show_alert(self) -> None:
        self._alert_frame.pack(fill=tk.X, padx=16, pady=(0, 12))

    def hide_alert(self) -> None:
        self._alert_frame.pack_forget()

    def set_enabled_state(self, enabled: bool) -> None:
        self._enabled_var.set(enabled)

    @property
    def hour_value(self) -> str:
        return self._hour_var.get().strip()

    @property
    def minute_value(self) -> str:
        return self._minute_var.get().strip()

    # ── Input validation ───────────────────────────────────────────────
    @staticmethod
    def _validate_hour(value: str) -> bool:
        if value == "":
            return True
        try:
            return 0 <= int(value) <= 23 and len(value) <= 2
        except ValueError:
            return False

    @staticmethod
    def _validate_minute(value: str) -> bool:
        if value == "":
            return True
        try:
            return 0 <= int(value) <= 59 and len(value) <= 2
        except ValueError:
            return False

    # ── Internal handlers ─────────────────────────────────────────────
    def _on_set_clicked(self) -> None:
        if self._on_set_callback: self._on_set_callback()

    def _on_toggle_clicked(self) -> None:
        if self._on_toggle_callback: self._on_toggle_callback(self._enabled_var.get())

    def _on_dismiss_clicked(self) -> None:
        if self._on_dismiss_callback: self._on_dismiss_callback()

    def _on_snooze_clicked(self) -> None:
        if self._on_snooze_callback: self._on_snooze_callback()
