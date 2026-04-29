"""MainWindow: root tkinter window setup and layout."""

import logging
import tkinter as tk
from abc import ABC, abstractmethod
from typing import Dict

from src.utils.constants import APP_TITLE, APP_WIDTH, APP_HEIGHT

logger = logging.getLogger(__name__)


class BaseView(ABC):
    """Abstract base class for all view components.

    Attributes:
        _frame: The tkinter container widget for this view.
    """

    def __init__(self) -> None:
        """Initialise the base view."""
        self._frame: tk.Widget = None  # type: ignore[assignment]

    @property
    def frame(self) -> tk.Widget:
        """Return the root widget of this view."""
        return self._frame

    @abstractmethod
    def build(self) -> None:
        """Construct and lay out all child widgets."""

    @abstractmethod
    def apply_theme(self, colors: Dict[str, str]) -> None:
        """Apply a color palette to all widgets in this view.

        Args:
            colors: Dictionary mapping color role names to hex strings.
        """


class MainWindow(BaseView):
    """Root application window.

    Wraps the tk.Tk instance and provides a scrollable notebook for the
    different clock panels.

    Attributes:
        _root: The tk.Tk root window.
        _notebook: ttk.Notebook holding the tab panels.
    """

    def __init__(self) -> None:
        """Initialise MainWindow and create the root Tk instance."""
        super().__init__()
        self._root: tk.Tk = tk.Tk()
        self._root.title(APP_TITLE)
        self._root.resizable(False, False)
        logger.debug("MainWindow created.")

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def root(self) -> tk.Tk:
        """Return the underlying tk.Tk root window."""
        return self._root

    # ------------------------------------------------------------------
    # BaseView implementation
    # ------------------------------------------------------------------

    def build(self) -> None:
        """Configure the root window geometry and main frame."""
        self._root.geometry(f"{APP_WIDTH}x{APP_HEIGHT}")
        self._frame = tk.Frame(self._root)
        self._frame.pack(fill=tk.BOTH, expand=True)
        logger.debug("MainWindow built.")

    def apply_theme(self, colors: Dict[str, str]) -> None:
        """Apply background color to the root window and main frame.

        Args:
            colors: Theme color dictionary.
        """
        bg = colors["bg_window"]
        self._root.configure(bg=bg)
        if self._frame:
            self._frame.configure(bg=bg)

    # ------------------------------------------------------------------
    # Window management
    # ------------------------------------------------------------------

    def set_on_close(self, callback) -> None:  # type: ignore[type-arg]
        """Register a callback for the window close event.

        Args:
            callback: Zero-argument callable invoked when the user closes
                the window.
        """
        self._root.protocol("WM_DELETE_WINDOW", callback)

    def mainloop(self) -> None:
        """Start the tkinter event loop."""
        logger.info("Entering tkinter mainloop.")
        self._root.mainloop()

    def destroy(self) -> None:
        """Destroy the root window and exit the event loop."""
        logger.info("Destroying main window.")
        self._root.destroy()

    def after(self, delay_ms: int, callback) -> str:  # type: ignore[type-arg]
        """Schedule a callback after a delay.

        Args:
            delay_ms: Delay in milliseconds.
            callback: Zero-argument callable to invoke.

        Returns:
            An identifier that can be passed to after_cancel().
        """
        return self._root.after(delay_ms, callback)

    def after_cancel(self, after_id: str) -> None:
        """Cancel a scheduled after() callback.

        Args:
            after_id: The identifier returned by after().
        """
        self._root.after_cancel(after_id)
