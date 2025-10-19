import json
import os
from datetime import datetime, timedelta, timezone


def get_next_timestamps() -> list[datetime]:
    now = datetime.now(tz=timezone(timedelta(hours=-4)))
    previous = read_timestamp() or get_previous_timestamp(get_previous_timestamp(now))

    timestamps = []

    while previous < now:
        previous = get_next_timestamp(previous)
        if previous <= now:
            timestamps.append(previous)

    return timestamps


def get_next_timestamp(dt: datetime) -> datetime:
    if (dt.hour < 9) or (dt.hour == 9 and dt.minute < 30):
        # <09:30 -> 09:30
        dt = dt.replace(hour=9, minute=30, second=0, microsecond=0)
    elif dt.hour < 16:
        # <16:00 -> 16:00
        dt = dt.replace(hour=16, minute=0, second=0, microsecond=0)
    else:
        # >=16:00 -> nächster Tag 09:30
        dt += timedelta(days=1)
        dt = dt.replace(hour=9, minute=30, second=0, microsecond=0)

    if dt.weekday() > 4:
        # Samstag/Sonntag -> Montag 09:30
        dt += timedelta(days=7 - dt.weekday())
        dt = dt.replace(hour=9, minute=30, second=0, microsecond=0)

    return dt


def get_previous_timestamp(dt: datetime) -> datetime:
    if dt.hour > 16:
        # >16:00 -> 16:00
        dt = dt.replace(hour=16, minute=0, second=0, microsecond=0)
    elif (dt.hour > 9) or (dt.hour == 9 and dt.minute > 30):
        # >09:30 -> 09:30
        dt = dt.replace(hour=9, minute=30, second=0, microsecond=0)
    else:
        # <=09:30 -> vorheriger Tag 16:00
        dt -= timedelta(days=1)
        dt = dt.replace(hour=16, minute=0, second=0, microsecond=0)

    if dt.weekday() > 4:
        # Samstag/Sonntag -> Freitag 16:00
        dt -= timedelta(days=dt.weekday() - 4)
        dt = dt.replace(hour=16, minute=0, second=0, microsecond=0)

    return dt


def read_timestamp() -> datetime | None:
    if not os.path.exists('docs/metadata.json'):
        return None
    with open('docs/metadata.json', 'r') as f:
        metadata = json.load(f)
        return datetime.fromisoformat(metadata["timestamp"])


def write_timestamp(dt: datetime):
    metadata = {"timestamp": dt.isoformat()}
    with open('docs/metadata.json', 'w') as f:
        json.dump(metadata, f, indent=2)
