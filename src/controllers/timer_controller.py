"""TimerController: mediates between TimerModel, TimerView, and AudioService."""

import logging
from typing import Optional

from src.controllers.clock_controller import BaseController
from src.models.timer import TimerModel
from src.views.timer_view import TimerView
from src.utils.audio import AudioService
from src.utils.constants import TIMER_UPDATE_INTERVAL

logger = logging.getLogger(__name__)


class TimerController(BaseController):
    """Drives the countdown timer feature.

    Attributes:
        _model: The TimerModel instance.
        _view: The TimerView instance.
        _audio: The AudioService for playing the finish alert.
        _after_fn: Callable for scheduling.
        _after_cancel_fn: Callable for cancelling scheduled calls.
        _after_id: Identifier of the pending after() call.
    """

    def __init__(
        self,
        model: TimerModel,
        view: TimerView,
        audio: AudioService,
        after_fn,
        after_cancel_fn,
    ) -> None:
        """Initialise TimerController.

        Args:
            model: The TimerModel to drive.
            view: The TimerView to update.
            audio: The AudioService for the finish sound.
            after_fn: root.after(delay_ms, callback) callable.
            after_cancel_fn: root.after_cancel(id) callable.
        """
        self._model = model
        self._view = view
        self._audio = audio
        self._after_fn = after_fn
        self._after_cancel_fn = after_cancel_fn
        self._after_id: Optional[str] = None

        # Wire view callbacks
        self._view.set_on_set(self._on_set)
        self._view.set_on_start(self._on_start)
        self._view.set_on_pause(self._on_pause)
        self._view.set_on_reset(self._on_reset)
        self._view.set_on_dismiss(self._on_dismiss)

        # Subscribe to model changes
        self._model.subscribe(self._on_model_update)
        logger.debug("TimerController initialised.")

    # ------------------------------------------------------------------
    # BaseController implementation
    # ------------------------------------------------------------------

    def start(self) -> None:
        """Begin the timer display update loop."""
        logger.info("TimerController started.")
        self._tick()

    def stop(self) -> None:
        """Stop the display update loop."""
        if self._after_id is not None:
            self._after_cancel_fn(self._after_id)
            self._after_id = None
        logger.info("TimerController stopped.")

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _tick(self) -> None:
        """Refresh the model and schedule the next tick."""
        self._model.update()
        self._after_id = self._after_fn(TIMER_UPDATE_INTERVAL, self._tick)

    def _on_model_update(self) -> None:
        """Push remaining time and finished state to the view."""
        self._view.update_remaining(self._model.format_remaining())
        self._view.set_running_state(self._model.running)
        if self._model.finished:
            self._audio.play()
            self._view.show_alert()

    # ------------------------------------------------------------------
    # View event handlers
    # ------------------------------------------------------------------

    def _on_set(self) -> None:
        """Handle 'Set' button click — parse duration from view inputs."""
        try:
            hours = int(self._view.hours_value or "0")
            minutes = int(self._view.minutes_value or "0")
            seconds = int(self._view.seconds_value or "0")
            self._model.set_duration(hours, minutes, seconds)
            self._view.update_remaining(self._model.format_remaining())
            self._view.hide_alert()
            logger.info("Timer duration set to %02d:%02d:%02d.", hours, minutes, seconds)
        except ValueError as exc:
            logger.warning("Invalid timer input: %s", exc)

    def _on_start(self) -> None:
        """Handle Start button click."""
        self._model.start()

    def _on_pause(self) -> None:
        """Handle Pause button click."""
        self._model.pause()

    def _on_reset(self) -> None:
        """Handle Reset button click."""
        self._model.reset()
        self._view.update_remaining(self._model.format_remaining())
        self._view.hide_alert()
        self._audio.stop()

    def _on_dismiss(self) -> None:
        """Handle dismiss button click after timer finishes."""
        self._audio.stop()
        self._model.acknowledge()
        self._view.hide_alert()
