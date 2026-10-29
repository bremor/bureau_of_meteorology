"""Choose a current condition without inventing weather from missing data."""

from datetime import datetime, timedelta
import math
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

MAX_CONDITION_CACHE_AGE = 15 * 60


def _timestamp(value):
    try:
        stamp = datetime.fromisoformat(value)
    except (TypeError, ValueError):
        return None
    return stamp if stamp.tzinfo is not None else None


def resolve_condition(daily, hourly, cache, location_timezone, valid_descriptors, now):
    """Prefer today's daily icon, then the current hour from a fresh fetch."""
    try:
        local_zone = ZoneInfo(location_timezone)
    except (TypeError, ValueError, ZoneInfoNotFoundError):
        return None, "unavailable"

    def fresh(key):
        fetched = cache.get(key, {}).get("timestamp")
        return (
            isinstance(fetched, (int, float))
            and math.isfinite(fetched)
            and 0 <= now.timestamp() - fetched <= MAX_CONDITION_CACHE_AGE
        )

    def rows(payload):
        data = payload.get("data") if isinstance(payload, dict) else None
        return (
            (row for row in data if isinstance(row, dict))
            if isinstance(data, list)
            else ()
        )

    if fresh("daily_forecasts"):
        for row in rows(daily):
            stamp = _timestamp(row.get("date"))
            descriptor = row.get("icon_descriptor")
            if (
                stamp is not None
                and stamp.astimezone(local_zone).date()
                == now.astimezone(local_zone).date()
                and descriptor is not None
                and descriptor in valid_descriptors
            ):
                return descriptor, "daily"

    if fresh("hourly_forecasts"):
        for row in rows(hourly):
            stamp = _timestamp(row.get("time"))
            descriptor = row.get("icon_descriptor")
            if (
                stamp is not None
                and stamp <= now < stamp + timedelta(hours=1)
                and descriptor is not None
                and descriptor in valid_descriptors
            ):
                return descriptor, "hourly"

    return None, "unavailable"
