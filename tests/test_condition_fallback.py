"""Offline condition regressions, including the WA midnight data gap."""

from datetime import datetime, timezone, timedelta
import importlib.util
from pathlib import Path
import unittest

PATH = (
    Path(__file__).resolve().parents[1]
    / "custom_components/bureau_of_meteorology/conditions.py"
)
spec = importlib.util.spec_from_file_location("bom_conditions_under_test", PATH)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class ConditionTests(unittest.TestCase):
    def setUp(self):
        self.now = datetime(2026, 10, 22, 15, 30, tzinfo=timezone.utc)
        self.cache = {
            key: {"timestamp": self.now.timestamp() - 60}
            for key in ("daily_forecasts", "hourly_forecasts")
        }
        self.daily = {
            "data": [{"date": "2026-10-21T16:00:00Z", "icon_descriptor": None}]
        }
        self.hourly = {
            "data": [
                {"time": "2026-10-22T14:00:00Z", "icon_descriptor": "sunny"},
                {"time": "2026-10-22T15:00:00Z", "icon_descriptor": "rain"},
                {"time": "2026-10-22T16:00:00Z", "icon_descriptor": "cloudy"},
            ]
        }

    def resolve(self):
        return module.resolve_condition(
            self.daily,
            self.hourly,
            self.cache,
            "Australia/Perth",
            {"sunny", "rain", "cloudy"},
            self.now,
        )

    def test_midnight_gap_uses_current_hour_not_first_hour(self):
        self.assertEqual(self.resolve(), ("rain", "hourly"))

    def test_daily_condition_takes_precedence(self):
        self.daily["data"][0]["icon_descriptor"] = "cloudy"
        self.assertEqual(self.resolve(), ("cloudy", "daily"))

    def test_previous_day_daily_data_does_not_override_current_hour(self):
        self.daily["data"][0]["icon_descriptor"] = "sunny"
        self.now += timedelta(minutes=31)
        self.cache = {k: {"timestamp": self.now.timestamp()} for k in self.cache}
        self.assertEqual(self.resolve(), ("cloudy", "hourly"))

    def test_stale_hourly_forecast_is_not_relabelled_current(self):
        self.cache["hourly_forecasts"]["timestamp"] = self.now.timestamp() - 901
        self.assertEqual(self.resolve(), (None, "unavailable"))

    def test_future_fetch_timestamp_is_not_accepted(self):
        self.cache["hourly_forecasts"]["timestamp"] = self.now.timestamp() + 1
        self.assertEqual(self.resolve(), (None, "unavailable"))

    def test_future_hour_is_not_used_early(self):
        self.hourly["data"] = self.hourly["data"][2:]
        self.assertEqual(self.resolve(), (None, "unavailable"))

    def test_missing_and_unknown_icons_do_not_invent_clear_weather(self):
        self.hourly["data"][1]["icon_descriptor"] = "unrecognised"
        self.assertEqual(self.resolve(), (None, "unavailable"))

    def test_naive_or_invalid_time_is_not_assumed_utc(self):
        self.hourly["data"][1]["time"] = "2026-10-22T15:00:00"
        self.assertEqual(self.resolve(), (None, "unavailable"))
        self.hourly["data"][1]["time"] = "invalid"
        self.assertEqual(self.resolve(), (None, "unavailable"))

    def test_empty_payloads_remain_unknown(self):
        self.daily = None
        self.hourly = None
        self.assertEqual(self.resolve(), (None, "unavailable"))

    def test_malformed_rows_are_ignored(self):
        self.daily = {"data": None}
        self.hourly["data"].insert(0, None)
        self.hourly["data"].insert(1, "invalid")
        self.assertEqual(self.resolve(), ("rain", "hourly"))

    def test_invalid_timezone_does_not_assume_a_calendar_date(self):
        self.assertEqual(
            module.resolve_condition(
                self.daily,
                self.hourly,
                self.cache,
                "Invalid/Timezone",
                {"rain"},
                self.now,
            ),
            (None, "unavailable"),
        )

    def test_non_finite_cache_timestamp_is_rejected(self):
        for value in (float("nan"), float("inf"), float("-inf")):
            with self.subTest(value=value):
                self.cache["hourly_forecasts"]["timestamp"] = value
                self.assertEqual(self.resolve(), (None, "unavailable"))

    def test_hour_boundary_drops_previous_hour(self):
        self.now = self.now.replace(minute=0) + timedelta(hours=1)
        self.cache = {k: {"timestamp": self.now.timestamp()} for k in self.cache}
        self.assertEqual(self.resolve(), ("cloudy", "hourly"))


if __name__ == "__main__":
    unittest.main()
