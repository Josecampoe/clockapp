"""AlarmController: mediates between AlarmModel, AlarmView, and AudioService."""

import logging
from typing import Optional

from src.controllers.clock_controller import BaseController
from src.models.alarm import AlarmModel
from src.views.alarm_view import AlarmView
from src.utils.audio import AudioService
from src.utils.constants import CLOCK_UPDATE_INTERVAL

logger = logging.getLogger(__name__)


class AlarmController(BaseController):
    """Drives the alarm feature.

    Polls the AlarmModel on each tick and triggers audio + visual
    notification when the alarm fires.

    Attributes:
        _model: The AlarmModel instance.
        _view: The AlarmView instance.
        _audio: The AudioService instance.
        _after_fn: Callable for scheduling.
        _after_cancel_fn: Callable for cancelling scheduled calls.
        _after_id: Identifier of the pending after() call.
    """

    def __init__(
        self,
        model: AlarmModel,
        view: AlarmView,
        audio: AudioService,
        after_fn,
        after_cancel_fn,
    ) -> None:
        """Initialise AlarmController.

        Args:
            model: The AlarmModel to drive.
            view: The AlarmView to update.
            audio: The AudioService for playing alarm sounds.
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
        self._view.set_on_set(self._on_set_alarm)
        self._view.set_on_toggle(self._on_toggle_alarm)
        self._view.set_on_dismiss(self._on_dismiss_alarm)

        # Subscribe to model changes
        self._model.subscribe(self._on_model_update)
        logger.debug("AlarmController initialised.")

    # ------------------------------------------------------------------
    # BaseController implementation
    # ------------------------------------------------------------------

    def start(self) -> None:
        """Begin the alarm polling loop."""
        logger.info("AlarmController started.")
        self._tick()

    def stop(self) -> None:
        """Stop the alarm polling loop."""
        if self._after_id is not None:
            self._after_cancel_fn(self._after_id)
            self._after_id = None
        logger.info("AlarmController stopped.")

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _tick(self) -> None:
        """Poll the model and schedule the next tick."""
        self._model.update()
        self._after_id = self._after_fn(CLOCK_UPDATE_INTERVAL, self._tick)

    def _on_model_update(self) -> None:
        """React to model state changes."""
        if self._model.triggered:
            self._audio.play()
            self._view.show_alert()
            self._view.update_status(
                f"⏰ Alarm fired at {self._model.format_time()}!"
            )
        else:
            status = (
                f"Alarm set: {self._model.format_time()}"
                if self._model.enabled
                else "Alarm off"
            )
            self._view.update_status(status)

    # ------------------------------------------------------------------
    # View event handlers
    # ------------------------------------------------------------------

    def _on_set_alarm(self) -> None:
        """Handle 'Set Alarm' button click."""
        try:
            hour = int(self._view.hour_value)
            minute = int(self._view.minute_value)
            self._model.set_time(hour, minute)
            logger.info("Alarm time set to %02d:%02d.", hour, minute)
        except ValueError as exc:
            logger.warning("Invalid alarm time input: %s", exc)
            self._view.update_status(f"Invalid time: {exc}")

    def _on_toggle_alarm(self, enabled: bool) -> None:
        """Handle enable/disable toggle.

        Args:
            enabled: New enabled state from the checkbox.
        """
        self._model.enabled = enabled
        if not enabled:
            self._audio.stop()
            self._view.hide_alert()

    def _on_dismiss_alarm(self) -> None:
        """Handle alarm dismissal."""
        self._audio.stop()
        self._model.acknowledge()
        self._view.hide_alert()
        self._view.update_status(
            f"Alarm set: {self._model.format_time()}"
            if self._model.enabled
            else "Alarm off"
        )
