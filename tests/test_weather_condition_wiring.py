"""Execute production weather properties without a Home Assistant installation.

The real properties and condition mappings are compiled from their source AST.
Only the framework base and clock are replaced. This is an offline wiring test,
not a running Home Assistant integration test.
"""

import ast
import asyncio
from datetime import datetime, timezone
import importlib.util
from pathlib import Path
from types import SimpleNamespace
import unittest

ROOT = Path(__file__).resolve().parents[1] / "custom_components/bureau_of_meteorology"
spec = importlib.util.spec_from_file_location(
    "bom_conditions_wiring", ROOT / "conditions.py"
)
conditions = importlib.util.module_from_spec(spec)
spec.loader.exec_module(conditions)


def mapping(path, name):
    for node in ast.parse(path.read_text(encoding="utf-8")).body:
        if (
            isinstance(node, ast.AnnAssign)
            and isinstance(node.target, ast.Name)
            and node.target.id == name
        ):
            return ast.literal_eval(node.value)
        if isinstance(node, ast.Assign) and any(
            isinstance(t, ast.Name) and t.id == name for t in node.targets
        ):
            return ast.literal_eval(node.value)
    raise AssertionError(f"Mapping {name} not found")


class WeatherWiringTests(unittest.TestCase):
    def setUp(self):
        self.now = datetime(2026, 10, 22, 15, 30, tzinfo=timezone.utc)
        tree = ast.parse((ROOT / "weather.py").read_text(encoding="utf-8"))
        node = next(
            n
            for n in tree.body
            if isinstance(n, ast.ClassDef) and n.name == "WeatherBase"
        )
        wanted = {
            "_current_condition",
            "condition",
            "icon",
            "extra_state_attributes",
            "available",
        }
        node.body = [
            n for n in node.body if isinstance(n, ast.FunctionDef) and n.name in wanted
        ]
        node.bases = []
        namespace = {
            "datetime": SimpleNamespace(now=lambda zone: self.now),
            "timezone": timezone,
            "resolve_condition": conditions.resolve_condition,
            "MAP_CONDITION": mapping(ROOT / "const.py", "MAP_CONDITION"),
            "MAP_MDI_ICON": mapping(ROOT / "PyBoM/const.py", "MAP_MDI_ICON"),
        }
        exec(
            compile(
                ast.Module(body=[node], type_ignores=[]),
                "<production weather properties>",
                "exec",
            ),
            namespace,
        )
        self.weather = namespace["WeatherBase"]()
        self.weather.coordinator = SimpleNamespace(last_update_success=True)
        self.weather.collector = SimpleNamespace(
            locations_data={"data": {"timezone": "Australia/Perth"}},
            daily_forecasts_data={
                "data": [{"date": "2026-10-21T16:00:00Z", "icon_descriptor": None}]
            },
            hourly_forecasts_data={
                "data": [{"time": "2026-10-22T15:00:00Z", "icon_descriptor": "rain"}]
            },
            _cache={
                k: {"timestamp": self.now.timestamp()}
                for k in ("daily_forecasts", "hourly_forecasts")
            },
        )

    def test_current_hour_flows_through_condition_icon_and_provenance(self):
        self.assertEqual(self.weather.condition, "rainy")
        self.assertEqual(self.weather.icon, "mdi:weather-pouring")
        self.assertEqual(
            self.weather.extra_state_attributes, {"condition_source": "hourly"}
        )
        self.assertTrue(self.weather.available)

    def test_missing_data_does_not_become_sunny(self):
        self.weather.collector.hourly_forecasts_data = None
        self.assertIsNone(self.weather.condition)
        self.assertIsNone(self.weather.icon)
        self.assertEqual(
            self.weather.extra_state_attributes, {"condition_source": "unavailable"}
        )

    def test_daily_icon_is_preferred_when_present(self):
        self.weather.collector.daily_forecasts_data["data"][0]["icon_descriptor"] = (
            "clear"
        )
        self.assertEqual(self.weather.condition, "clear-night")
        self.assertEqual(self.weather.icon, "mdi:weather-night")
        self.assertEqual(
            self.weather.extra_state_attributes, {"condition_source": "daily"}
        )

    def test_failed_update_marks_weather_unavailable_and_recovery_restores_it(self):
        self.weather.coordinator.last_update_success = False
        self.assertFalse(self.weather.available)
        self.weather.coordinator.last_update_success = True
        self.assertTrue(self.weather.available)

    def test_expired_fallback_cannot_be_presented_as_current(self):
        self.weather.collector._cache["hourly_forecasts"]["timestamp"] -= 901
        self.assertIsNone(self.weather.condition)
        self.assertEqual(
            self.weather.extra_state_attributes, {"condition_source": "unavailable"}
        )

    def test_raw_nighttime_sunny_icon_is_formatted_before_hourly_fallback(self):
        # This shape matches the live BOM 2026-10-26 hourly response: the raw
        # descriptor can be sunny while is_night is true. Use the real formatter.
        tree = ast.parse((ROOT / "PyBoM/collector.py").read_text(encoding="utf-8"))
        formatter = next(
            n
            for n in ast.walk(tree)
            if isinstance(n, ast.AsyncFunctionDef)
            and n.name == "format_hourly_forecast_data"
        )
        helper_tree = ast.parse((ROOT / "PyBoM/helpers.py").read_text(encoding="utf-8"))
        flatten = next(
            n
            for n in helper_tree.body
            if isinstance(n, ast.FunctionDef) and n.name == "flatten_dict"
        )
        namespace = {"MAP_MDI_ICON": mapping(ROOT / "PyBoM/const.py", "MAP_MDI_ICON")}
        exec(
            compile(
                ast.Module(body=[flatten, formatter], type_ignores=[]),
                "<production BOM formatter>",
                "exec",
            ),
            namespace,
        )
        self.weather.collector.hourly_forecasts_data["data"][0].update(
            {
                "icon_descriptor": "sunny",
                "is_night": True,
                "rain": {"amount": {"min": 0, "max": None}, "chance": 0},
                "wind": {"speed_kilometre": 5},
            }
        )
        asyncio.run(namespace["format_hourly_forecast_data"](self.weather.collector))
        self.assertEqual(self.weather.condition, "clear-night")
        self.assertEqual(self.weather.icon, "mdi:weather-night")
        self.assertEqual(
            self.weather.extra_state_attributes, {"condition_source": "hourly"}
        )


if __name__ == "__main__":
    unittest.main()
