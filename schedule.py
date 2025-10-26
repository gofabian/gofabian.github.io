import json
import os
from datetime import datetime, timedelta, timezone, time

TZ = timezone(timedelta(hours=-4))

VALID_TIMES = sorted([
    time(hour=12, minute=0),  # 18:00
    time(hour=12, minute=45),  # 18:45
    time(hour=15, minute=0),  # 21:00
    time(hour=16, minute=0),  # 22:00
])


def get_due_timestamps() -> list[datetime]:
    now = datetime.now(tz=TZ)
    previous = read_timestamp() or get_previous_timestamp(get_previous_timestamp(now))

    timestamps = []

    while previous < now:
        previous = get_next_timestamp(previous)
        if previous <= now:
            timestamps.append(previous)

    return timestamps


def get_next_timestamp(dt: datetime) -> datetime:
    next_timestamp: datetime | None = None

    for valid_time in VALID_TIMES:
        if dt.time() < valid_time:
            # e.g. <12:45 -> 12:45
            # e.g. <16:00 -> 16:00
            next_timestamp = datetime.combine(dt.date(), valid_time, tzinfo=TZ)
            break

    if next_timestamp is None:
        # e.g. >=16:00 -> nächster Tag 12:45
        next_timestamp = dt + timedelta(days=1)
        next_timestamp = datetime.combine(next_timestamp, VALID_TIMES[0], tzinfo=TZ)

    if next_timestamp.weekday() > 4:
        # Samstag/Sonntag -> Montag 12:45
        next_timestamp += timedelta(days=7 - dt.weekday())
        next_timestamp = datetime.combine(next_timestamp.date(), VALID_TIMES[0], tzinfo=TZ)

    return next_timestamp


def get_previous_timestamp(dt: datetime) -> datetime:
    previous_timestamp: datetime | None = None

    for valid_time in sorted(VALID_TIMES, reverse=True):
        if dt.time() > valid_time:
            # e.g. >16:00 -> 16:00
            # e.g. >12:45 -> 12:45
            previous_timestamp = datetime.combine(dt.date(), valid_time, tzinfo=TZ)
            break

    if previous_timestamp is None:
        # g.g. <=12:45 -> vorheriger Tag 16:00
        previous_timestamp = dt - timedelta(days=1)
        previous_timestamp = datetime.combine(previous_timestamp.date(), VALID_TIMES[-1], tzinfo=TZ)

    if previous_timestamp.weekday() > 4:
        # Samstag/Sonntag -> Freitag 16:00
        previous_timestamp -= timedelta(days=dt.weekday() - 4)
        previous_timestamp = datetime.combine(previous_timestamp.date(), VALID_TIMES[-1], tzinfo=TZ)

    return previous_timestamp


def read_timestamp() -> datetime | None:
    if not os.path.exists('docs/metadata.json'):
        return None
    with open('docs/metadata.json', 'r') as f:
        metadata = json.load(f)
        return datetime.fromisoformat(metadata["timestamp"])


def write_timestamp(dt: datetime):
    metadata = {"timestamp": dt.isoformat()}
    with open('docs/metadata.json', 'w', encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)
