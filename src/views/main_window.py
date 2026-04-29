"""MainWindow: root window using CustomTkinter for a modern look."""

import logging
import tkinter as tk
from abc import ABC, abstractmethod
from typing import Dict

import customtkinter as ctk

from src.utils.constants import APP_TITLE, APP_WIDTH, APP_HEIGHT

logger = logging.getLogger(__name__)

# Default appearance — dark mode, custom color theme
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class BaseView(ABC):
    """Abstract base for all view components."""

    def __init__(self) -> None:
        self._frame: tk.Widget = None  # type: ignore[assignment]

    @property
    def frame(self) -> tk.Widget:
        return self._frame

    @abstractmethod
    def build(self) -> None: ...

    @abstractmethod
    def apply_theme(self, colors: Dict[str, str]) -> None: ...


class MainWindow(BaseView):
    """Root CTk window."""

    def __init__(self) -> None:
        super().__init__()
        self._root = ctk.CTk()
        self._root.title(APP_TITLE)
        self._root.resizable(False, False)
        logger.debug("MainWindow created.")

    @property
    def root(self) -> ctk.CTk:
        return self._root

    def build(self) -> None:
        self._root.geometry(f"{APP_WIDTH}x{APP_HEIGHT}")
        self._frame = ctk.CTkFrame(self._root, corner_radius=0, fg_color="transparent")
        self._frame.pack(fill=tk.BOTH, expand=True)
        logger.debug("MainWindow built.")

    def apply_theme(self, colors: Dict[str, str]) -> None:
        self._root.configure(fg_color=colors["bg_window"])
        if self._frame:
            self._frame.configure(fg_color=colors["bg_window"])

    def set_on_close(self, callback) -> None:
        self._root.protocol("WM_DELETE_WINDOW", callback)

    def mainloop(self) -> None:
        logger.info("Entering mainloop.")
        self._root.mainloop()

    def destroy(self) -> None:
        logger.info("Destroying window.")
        self._root.destroy()

    def after(self, delay_ms: int, callback) -> str:
        return self._root.after(delay_ms, callback)

    def after_cancel(self, after_id: str) -> None:
        self._root.after_cancel(after_id)
