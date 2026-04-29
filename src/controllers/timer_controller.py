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
    """Drives the countdown timer feature, including preset selection."""

    def __init__(
        self,
        model: TimerModel,
        view: TimerView,
        audio: AudioService,
        after_fn,
        after_cancel_fn,
    ) -> None:
        self._model           = model
        self._view            = view
        self._audio           = audio
        self._after_fn        = after_fn
        self._after_cancel_fn = after_cancel_fn
        self._after_id: Optional[str] = None
        self._alert_playing: bool = False

        self._view.set_on_set(self._on_set)
        self._view.set_on_start(self._on_start)
        self._view.set_on_pause(self._on_pause)
        self._view.set_on_reset(self._on_reset)
        self._view.set_on_dismiss(self._on_dismiss)
        self._view.set_on_preset(self._on_preset)

        self._model.subscribe(self._on_model_update)
        logger.debug("TimerController initialised.")

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def start(self) -> None:
        logger.info("TimerController started.")
        self._tick()

    def stop(self) -> None:
        if self._after_id is not None:
            self._after_cancel_fn(self._after_id)
            self._after_id = None
        logger.info("TimerController stopped.")

    # ------------------------------------------------------------------
    # Private
    # ------------------------------------------------------------------

    def _tick(self) -> None:
        self._model.update()
        self._after_id = self._after_fn(TIMER_UPDATE_INTERVAL, self._tick)

    def _on_model_update(self) -> None:
        self._view.update_remaining(self._model.format_remaining())
        self._view.update_progress(self._model.progress)
        self._view.set_running_state(self._model.running)
        if self._model.finished and not self._alert_playing:
            self._alert_playing = True
            self._audio.play()
            self._view.show_alert()

    # ------------------------------------------------------------------
    # View callbacks
    # ------------------------------------------------------------------

    def _on_set(self) -> None:
        try:
            h = int(self._view.hours_value   or "0")
            m = int(self._view.minutes_value or "0")
            s = int(self._view.seconds_value or "0")
            self._model.set_duration(h, m, s)
            self._view.update_remaining(self._model.format_remaining())
            self._view.hide_alert()
            self._alert_playing = False
        except ValueError as exc:
            logger.warning("Invalid timer input: %s", exc)

    def _on_start(self) -> None:
        self._model.start()

    def _on_pause(self) -> None:
        self._model.pause()

    def _on_reset(self) -> None:
        self._model.reset()
        self._view.update_remaining(self._model.format_remaining())
        self._view.update_progress(0.0)
        self._view.hide_alert()
        self._audio.stop()
        self._alert_playing = False

    def _on_dismiss(self) -> None:
        self._audio.stop()
        self._model.acknowledge()
        self._view.hide_alert()
        self._alert_playing = False

    def _on_preset(self, preset_index: int) -> None:
        """Apply a quick-set preset by index."""
        try:
            self._model.apply_preset(preset_index)
            self._view.update_remaining(self._model.format_remaining())
            self._view.hide_alert()
            self._alert_playing = False
        except (IndexError, ValueError) as exc:
            logger.warning("Preset error: %s", exc)
