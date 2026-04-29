"""Unit tests for AlarmModel."""

import sys
import os
import unittest
from unittest.mock import patch
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.models.alarm import AlarmModel


class TestAlarmModelSetTime(unittest.TestCase):
    """Tests for AlarmModel time setting and validation."""

    def test_set_valid_time(self):
        model = AlarmModel()
        model.set_time(8, 30)
        self.assertEqual(model.hour, 8)
        self.assertEqual(model.minute, 30)

    def test_set_invalid_hour_raises(self):
        model = AlarmModel()
        with self.assertRaises(ValueError):
            model.set_time(24, 0)

    def test_set_invalid_minute_raises(self):
        model = AlarmModel()
        with self.assertRaises(ValueError):
            model.set_time(8, 60)

    def test_set_negative_hour_raises(self):
        model = AlarmModel()
        with self.assertRaises(ValueError):
            model.set_time(-1, 0)

    def test_format_time(self):
        model = AlarmModel()
        model.set_time(7, 5)
        self.assertEqual(model.format_time(), "07:05")


class TestAlarmModelTrigger(unittest.TestCase):
    """Tests for AlarmModel trigger logic."""

    def _make_alarm_at(self, hour: int, minute: int) -> AlarmModel:
        model = AlarmModel()
        model.set_time(hour, minute)
        model.enabled = True
        return model

    def test_alarm_triggers_at_correct_time(self):
        model = self._make_alarm_at(9, 0)
        fixed_dt = datetime(2026, 4, 28, 9, 0, 0)
        with patch("src.models.alarm.datetime") as mock_dt:
            mock_dt.now.return_value = fixed_dt
            model.update()
        self.assertTrue(model.triggered)

    def test_alarm_does_not_trigger_at_wrong_time(self):
        model = self._make_alarm_at(9, 0)
        fixed_dt = datetime(2026, 4, 28, 9, 1, 0)
        with patch("src.models.alarm.datetime") as mock_dt:
            mock_dt.now.return_value = fixed_dt
            model.update()
        self.assertFalse(model.triggered)

    def test_alarm_does_not_trigger_when_disabled(self):
        model = self._make_alarm_at(9, 0)
        model.enabled = False
        fixed_dt = datetime(2026, 4, 28, 9, 0, 0)
        with patch("src.models.alarm.datetime") as mock_dt:
            mock_dt.now.return_value = fixed_dt
            model.update()
        self.assertFalse(model.triggered)

    def test_alarm_does_not_trigger_twice_in_same_minute(self):
        model = self._make_alarm_at(9, 0)
        fixed_dt = datetime(2026, 4, 28, 9, 0, 0)
        with patch("src.models.alarm.datetime") as mock_dt:
            mock_dt.now.return_value = fixed_dt
            model.update()
        self.assertTrue(model.triggered)
        model.acknowledge()
        # Second update in the same minute should NOT re-trigger
        with patch("src.models.alarm.datetime") as mock_dt:
            mock_dt.now.return_value = fixed_dt
            model.update()
        self.assertFalse(model.triggered)

    def test_acknowledge_clears_triggered(self):
        model = self._make_alarm_at(9, 0)
        fixed_dt = datetime(2026, 4, 28, 9, 0, 0)
        with patch("src.models.alarm.datetime") as mock_dt:
            mock_dt.now.return_value = fixed_dt
            model.update()
        model.acknowledge()
        self.assertFalse(model.triggered)


class TestAlarmModelObserver(unittest.TestCase):
    """Tests for AlarmModel observer notifications."""

    def test_observer_called_on_enable(self):
        model = AlarmModel()
        calls = []
        model.subscribe(lambda: calls.append(1))
        model.enabled = True
        self.assertGreater(len(calls), 0)

    def test_observer_called_on_set_time(self):
        model = AlarmModel()
        calls = []
        model.subscribe(lambda: calls.append(1))
        model.set_time(10, 30)
        self.assertGreater(len(calls), 0)


if __name__ == "__main__":
    unittest.main()
