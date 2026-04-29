"""StopwatchView: full-screen stopwatch with lap tracking."""

import logging
import tkinter as tk
from typing import Callable, Dict, List, Optional, Tuple

import customtkinter as ctk

from src.views.main_window import BaseView

logger = logging.getLogger(__name__)


class StopwatchView(BaseView):
    """Large stopwatch display with Iniciar/Detener/Vuelta/Reiniciar controls
    and a scrollable lap list."""

    def __init__(self, parent: tk.Widget) -> None:
        super().__init__()
        self._parent = parent
        self._elapsed_var = tk.StringVar(value="00:00:00:00")
        self._on_start_callback: Optional[Callable[[], None]] = None
        self._on_stop_callback:  Optional[Callable[[], None]] = None
        self._on_reset_callback: Optional[Callable[[], None]] = None
        self._on_lap_callback:   Optional[Callable[[], None]] = None
        self._start_btn: Optional[ctk.CTkButton] = None
        self._stop_btn:  Optional[ctk.CTkButton] = None
        self._lap_btn:   Optional[ctk.CTkButton] = None
        self._lap_frame: Optional[ctk.CTkScrollableFrame] = None
        logger.debug("StopwatchView initialised.")

    # ── Callbacks ─────────────────────────────────────────────────────
    def set_on_start(self, cb: Callable[[], None]) -> None: self._on_start_callback = cb
    def set_on_stop(self,  cb: Callable[[], None]) -> None: self._on_stop_callback  = cb
    def set_on_reset(self, cb: Callable[[], None]) -> None: self._on_reset_callback = cb
    def set_on_lap(self,   cb: Callable[[], None]) -> None: self._on_lap_callback   = cb

    # ── Build ──────────────────────────────────────────────────────────
    def build(self) -> None:
        self._frame = ctk.CTkFrame(self._parent, fg_color="transparent")
        self._frame.pack(fill=tk.BOTH, expand=True)

        # ── Time display card ─────────────────────────────────────────
        self._card = ctk.CTkFrame(self._frame, corner_radius=24)
        self._card.pack(padx=24, pady=(8, 4), fill=tk.X)

        self._elapsed_label = ctk.CTkLabel(
            self._card,
            textvariable=self._elapsed_var,
            font=ctk.CTkFont(family="Courier New", size=54, weight="bold"),
        )
        self._elapsed_label.pack(pady=(18, 2))

        self._hint_label = ctk.CTkLabel(
            self._card, text="hh : mm : ss : cs",
            font=ctk.CTkFont(size=11),
        )
        self._hint_label.pack(pady=(0, 16))

        # ── Buttons ───────────────────────────────────────────────────
        btn_row = ctk.CTkFrame(self._frame, fg_color="transparent")
        btn_row.pack(pady=12)
        self._btn_row = btn_row

        self._start_btn = ctk.CTkButton(
            btn_row, text="▶  Iniciar", width=120, height=44,
            corner_radius=22, font=ctk.CTkFont(size=13, weight="bold"),
            command=self._on_start_clicked,
        )
        self._start_btn.pack(side=tk.LEFT, padx=6)

        self._stop_btn = ctk.CTkButton(
            btn_row, text="⏸  Detener", width=120, height=44,
            corner_radius=22, font=ctk.CTkFont(size=13, weight="bold"),
            state="disabled",
            command=self._on_stop_clicked,
        )
        self._stop_btn.pack(side=tk.LEFT, padx=6)

        self._lap_btn = ctk.CTkButton(
            btn_row, text="⚑  Vuelta", width=110, height=44,
            corner_radius=22, font=ctk.CTkFont(size=13, weight="bold"),
            state="disabled",
            command=self._on_lap_clicked,
        )
        self._lap_btn.pack(side=tk.LEFT, padx=6)

        self._reset_btn = ctk.CTkButton(
            btn_row, text="↺  Reiniciar", width=120, height=44,
            corner_radius=22, font=ctk.CTkFont(size=13, weight="bold"),
            command=self._on_reset_clicked,
        )
        self._reset_btn.pack(side=tk.LEFT, padx=6)

        # ── Lap list ──────────────────────────────────────────────────
        lap_header = ctk.CTkFrame(self._frame, fg_color="transparent")
        lap_header.pack(fill=tk.X, padx=24, pady=(8, 2))

        ctk.CTkLabel(
            lap_header, text="Vueltas",
            font=ctk.CTkFont(size=13, weight="bold"),
        ).pack(side=tk.LEFT)

        self._lap_count_label = ctk.CTkLabel(
            lap_header, text="",
            font=ctk.CTkFont(size=11),
        )
        self._lap_count_label.pack(side=tk.LEFT, padx=8)

        self._lap_frame = ctk.CTkScrollableFrame(
            self._frame, corner_radius=12, height=140,
        )
        self._lap_frame.pack(fill=tk.X, padx=24, pady=(0, 8))

        logger.debug("StopwatchView built.")

    # ── Theme ──────────────────────────────────────────────────────────
    def apply_theme(self, colors: Dict[str, str]) -> None:
        self._frame.configure(fg_color="transparent")
        if hasattr(self, "_card"):
            self._card.configure(fg_color=colors["bg_card"])
        if self._elapsed_label:
            self._elapsed_label.configure(text_color=colors["accent"])
        if self._hint_label:
            self._hint_label.configure(text_color=colors["text_secondary"])
        if hasattr(self, "_lap_count_label"):
            self._lap_count_label.configure(text_color=colors["text_secondary"])
        if self._lap_frame:
            self._lap_frame.configure(fg_color=colors["bg_card"])
        if self._start_btn:
            self._start_btn.configure(fg_color=colors["success"], hover_color="#059669")
        if self._stop_btn:
            self._stop_btn.configure(fg_color=colors["warning"], hover_color="#D97706")
        if self._lap_btn:
            self._lap_btn.configure(
                fg_color=colors["accent2"], hover_color="#0891B2",
                text_color="white",
            )
        if self._reset_btn:
            self._reset_btn.configure(
                fg_color=colors["button2_bg"], text_color=colors["button2_fg"],
                hover_color=colors["entry_bg"],
            )

    # ── Public API ─────────────────────────────────────────────────────
    def update_elapsed(self, elapsed_str: str) -> None:
        self._elapsed_var.set(elapsed_str)

    def set_running_state(self, running: bool) -> None:
        if self._start_btn:
            self._start_btn.configure(state="disabled" if running else "normal")
        if self._stop_btn:
            self._stop_btn.configure(state="normal" if running else "disabled")
        if self._lap_btn:
            self._lap_btn.configure(state="normal" if running else "disabled")

    def update_laps(self, laps: List[Tuple[int, float, float]]) -> None:
        """Refresh the lap list display.

        Args:
            laps: List of (lap_num, split_seconds, total_seconds) tuples.
        """
        if self._lap_frame is None:
            return

        # Clear existing rows
        for widget in self._lap_frame.winfo_children():
            widget.destroy()

        if not laps:
            self._lap_count_label.configure(text="")
            return

        self._lap_count_label.configure(text=f"({len(laps)})")

        # Column headers
        hdr = ctk.CTkFrame(self._lap_frame, fg_color="transparent")
        hdr.pack(fill=tk.X, pady=(2, 4))
        for text, width in [("#", 60), ("Parcial", 130), ("Total", 130)]:
            ctk.CTkLabel(
                hdr, text=text, width=width,
                font=ctk.CTkFont(size=10, weight="bold"),
                anchor="center",
            ).pack(side=tk.LEFT)

        # Lap rows (most recent first)
        for num, split, total in reversed(laps):
            row = ctk.CTkFrame(self._lap_frame, fg_color="transparent")
            row.pack(fill=tk.X, pady=1)
            for text, width in [
                (str(num), 60),
                (self._fmt(split), 130),
                (self._fmt(total), 130),
            ]:
                ctk.CTkLabel(
                    row, text=text, width=width,
                    font=ctk.CTkFont(family="Courier New", size=11),
                    anchor="center",
                ).pack(side=tk.LEFT)

    @staticmethod
    def _fmt(seconds: float) -> str:
        h  = int(seconds // 3600)
        m  = int((seconds % 3600) // 60)
        s  = int(seconds % 60)
        cs = int((seconds % 1) * 100)
        return f"{h:02d}:{m:02d}:{s:02d}:{cs:02d}"

    # ── Handlers ──────────────────────────────────────────────────────
    def _on_start_clicked(self) -> None:
        if self._on_start_callback: self._on_start_callback()

    def _on_stop_clicked(self) -> None:
        if self._on_stop_callback: self._on_stop_callback()

    def _on_reset_clicked(self) -> None:
        if self._on_reset_callback: self._on_reset_callback()

    def _on_lap_clicked(self) -> None:
        if self._on_lap_callback: self._on_lap_callback()
