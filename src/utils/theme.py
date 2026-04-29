"""Theme management for light and dark modes."""

import logging
from typing import Dict, Callable, List

from src.utils.constants import THEME_LIGHT, THEME_DARK, LIGHT_THEME, DARK_THEME

logger = logging.getLogger(__name__)


class ThemeManager:
    """Manages application-wide light/dark theme switching.

    Implements the Observer pattern: views register callbacks that are
    invoked whenever the active theme changes.

    Attributes:
        _current_theme: Name of the currently active theme.
        _observers: List of callables notified on theme change.
    """

    def __init__(self, initial_theme: str = THEME_LIGHT) -> None:
        """Initialise the ThemeManager.

        Args:
            initial_theme: Starting theme name ('light' or 'dark').
        """
        self._current_theme: str = initial_theme
        self._observers: List[Callable[[Dict[str, str]], None]] = []
        logger.debug("ThemeManager initialised with theme '%s'.", initial_theme)

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def current_theme(self) -> str:
        """Return the name of the active theme."""
        return self._current_theme

    @property
    def colors(self) -> Dict[str, str]:
        """Return the color dictionary for the active theme."""
        return LIGHT_THEME if self._current_theme == THEME_LIGHT else DARK_THEME

    # ------------------------------------------------------------------
    # Observer management
    # ------------------------------------------------------------------

    def subscribe(self, callback: Callable[[Dict[str, str]], None]) -> None:
        """Register a callback to be notified on theme changes.

        Args:
            callback: A callable that accepts a color dictionary.
        """
        if callback not in self._observers:
            self._observers.append(callback)

    def unsubscribe(self, callback: Callable[[Dict[str, str]], None]) -> None:
        """Remove a previously registered callback.

        Args:
            callback: The callable to remove.
        """
        if callback in self._observers:
            self._observers.remove(callback)

    def _notify_observers(self) -> None:
        """Notify all registered observers with the current color palette."""
        colors = self.colors
        for callback in self._observers:
            try:
                callback(colors)
            except Exception as exc:  # pylint: disable=broad-except
                logger.error("Error notifying theme observer: %s", exc)

    # ------------------------------------------------------------------
    # Theme switching
    # ------------------------------------------------------------------

    def toggle(self) -> str:
        """Toggle between light and dark themes.

        Returns:
            The name of the newly active theme.
        """
        self._current_theme = (
            THEME_DARK if self._current_theme == THEME_LIGHT else THEME_LIGHT
        )
        logger.info("Theme switched to '%s'.", self._current_theme)
        self._notify_observers()
        return self._current_theme

    def set_theme(self, theme_name: str) -> None:
        """Set a specific theme by name.

        Args:
            theme_name: Either 'light' or 'dark'.

        Raises:
            ValueError: If theme_name is not recognised.
        """
        if theme_name not in (THEME_LIGHT, THEME_DARK):
            raise ValueError(
                f"Unknown theme '{theme_name}'. Expected 'light' or 'dark'."
            )
        if self._current_theme != theme_name:
            self._current_theme = theme_name
            logger.info("Theme set to '%s'.", theme_name)
            self._notify_observers()

    def is_dark(self) -> bool:
        """Return True if the dark theme is currently active."""
        return self._current_theme == THEME_DARK
