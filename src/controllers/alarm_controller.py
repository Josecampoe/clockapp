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

    Polls AlarmModel on each tick and triggers audio + visual notification
    when the alarm fires.  Supports snooze and auto-stop (handled by the
    model; the controller just reacts to state changes).
    """

    def __init__(
        self,
        model: AlarmModel,
        view: AlarmView,
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

        self._view.set_on_set(self._on_set_alarm)
        self._view.set_on_toggle(self._on_toggle_alarm)
        self._view.set_on_dismiss(self._on_dismiss_alarm)
        self._view.set_on_snooze(self._on_snooze_alarm)

        self._model.subscribe(self._on_model_update)
        logger.debug("AlarmController initialised.")

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def start(self) -> None:
        logger.info("AlarmController started.")
        self._tick()

    def stop(self) -> None:
        if self._after_id is not None:
            self._after_cancel_fn(self._after_id)
            self._after_id = None
        logger.info("AlarmController stopped.")

    # ------------------------------------------------------------------
    # Private
    # ------------------------------------------------------------------

    def _tick(self) -> None:
        self._model.update()
        self._after_id = self._after_fn(CLOCK_UPDATE_INTERVAL, self._tick)

    def _on_model_update(self) -> None:
        if self._model.triggered:
            self._audio.play()
            self._view.show_alert()
            self._view.update_status(f"⏰  ¡Alarma sonando — {self._model.format_time()}!")
        elif self._model.snooze_active:
            self._audio.stop()
            self._view.hide_alert()
            self._view.update_status(
                f"💤  Pospuesta hasta {self._model.format_snooze_until()}"
            )
        else:
            self._audio.stop()
            self._view.hide_alert()
            status = (
                f"✅  Alarma activa: {self._model.format_time()}"
                if self._model.enabled
                else "Alarma desactivada"
            )
            self._view.update_status(status)

    # ------------------------------------------------------------------
    # View callbacks
    # ------------------------------------------------------------------

    def _on_set_alarm(self) -> None:
        try:
            hour   = int(self._view.hour_value)
            minute = int(self._view.minute_value)
            self._model.set_time(hour, minute)
            self._view.update_status(f"✅  Alarma activa: {self._model.format_time()}")
        except ValueError as exc:
            logger.warning("Invalid alarm input: %s", exc)
            self._view.update_status(f"⚠️  Hora inválida: {exc}")

    def _on_toggle_alarm(self, enabled: bool) -> None:
        self._model.enabled = enabled
        if not enabled:
            self._audio.stop()
            self._view.hide_alert()

    def _on_dismiss_alarm(self) -> None:
        self._audio.stop()
        self._model.acknowledge()
        self._view.hide_alert()

    def _on_snooze_alarm(self) -> None:
        self._audio.stop()
        self._model.snooze()
        self._view.hide_alert()
