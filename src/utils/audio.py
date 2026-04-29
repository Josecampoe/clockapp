"""Audio service wrapping pygame for alarm sound playback."""

import logging
import os
from typing import Optional

logger = logging.getLogger(__name__)

_PYGAME_AVAILABLE = False
try:
    import pygame  # type: ignore
    _PYGAME_AVAILABLE = True
except ImportError:
    logger.warning("pygame is not installed. Alarm audio will be disabled.")


class AudioService:
    """Wraps pygame mixer to play alarm sounds.

    Provides a safe interface that degrades gracefully when pygame is
    unavailable or the sound file cannot be loaded.

    Attributes:
        _sound_path: Absolute path to the WAV/MP3 alarm file.
        _initialised: Whether pygame mixer was successfully initialised.
        _sound: Loaded pygame Sound object, or None.
    """

    def __init__(self, sound_path: str) -> None:
        """Initialise the AudioService.

        Args:
            sound_path: Path to the alarm sound file (WAV or MP3).
        """
        self._sound_path: str = sound_path
        self._initialised: bool = False
        self._sound: Optional[object] = None
        self._init_pygame()

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _init_pygame(self) -> None:
        """Attempt to initialise pygame mixer."""
        if not _PYGAME_AVAILABLE:
            return
        try:
            pygame.mixer.init()
            self._initialised = True
            logger.debug("pygame mixer initialised.")
            self._load_sound()
        except pygame.error as exc:
            logger.error("Failed to initialise pygame mixer: %s", exc)

    def _load_sound(self) -> None:
        """Load the sound file if it exists."""
        if not self._initialised:
            return
        if not os.path.isfile(self._sound_path):
            logger.warning("Alarm sound file not found: %s", self._sound_path)
            return
        try:
            self._sound = pygame.mixer.Sound(self._sound_path)
            logger.debug("Alarm sound loaded from '%s'.", self._sound_path)
        except pygame.error as exc:
            logger.error("Failed to load alarm sound: %s", exc)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    @property
    def is_ready(self) -> bool:
        """Return True if audio is initialised and a sound is loaded."""
        return self._initialised and self._sound is not None

    def play(self) -> None:
        """Play the alarm sound once.

        Falls back to a terminal bell if pygame is unavailable.
        """
        if self.is_ready:
            try:
                self._sound.play()  # type: ignore[union-attr]
                logger.info("Alarm sound playing.")
            except pygame.error as exc:
                logger.error("Error playing alarm sound: %s", exc)
        else:
            # Fallback: terminal bell
            print("\a", end="", flush=True)
            logger.info("Alarm triggered (terminal bell fallback).")

    def stop(self) -> None:
        """Stop any currently playing alarm sound."""
        if self.is_ready:
            try:
                self._sound.stop()  # type: ignore[union-attr]
                logger.debug("Alarm sound stopped.")
            except pygame.error as exc:
                logger.error("Error stopping alarm sound: %s", exc)

    def set_volume(self, volume: float) -> None:
        """Set playback volume.

        Args:
            volume: Float between 0.0 (silent) and 1.0 (full volume).

        Raises:
            ValueError: If volume is outside [0.0, 1.0].
        """
        if not 0.0 <= volume <= 1.0:
            raise ValueError(f"Volume must be between 0.0 and 1.0, got {volume}.")
        if self.is_ready:
            self._sound.set_volume(volume)  # type: ignore[union-attr]

    def reload_sound(self, sound_path: str) -> None:
        """Load a different sound file at runtime.

        Args:
            sound_path: Path to the new sound file.
        """
        self._sound_path = sound_path
        self._sound = None
        self._load_sound()
