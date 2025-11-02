import json
import os
from datetime import datetime, timedelta, time
from zoneinfo import ZoneInfo

TZ = ZoneInfo("America/New_York")

SCHEDULE_TIMES = [
    time(hour=12, minute=0),
    time(hour=12, minute=45),
    time(hour=15, minute=15),
    time(hour=16, minute=0),
]

CANDLE_START_TIMES = [
    time(hour=9, minute=30),
    time(hour=12, minute=45),
]

CANDLE_END_TIMES = [
    time(hour=12, minute=45),
    time(hour=16, minute=0),
]


def get_end_timestamp() -> datetime:
    now = datetime.now(tz=TZ)
    return get_previous_timestamp(now, SCHEDULE_TIMES)


def get_start_timestamp() -> datetime:
    previous_end = read_schedule_timestamp()
    if previous_end is None:
        # -> current candle start
        return get_previous_timestamp(get_end_timestamp(), CANDLE_START_TIMES)

    previous_start = get_previous_timestamp(previous_end, CANDLE_START_TIMES)

    if matches_any_time(previous_end, CANDLE_END_TIMES):
        # complete -> do not generate same candle again, jump to next
        return get_next_timestamp(previous_start, CANDLE_START_TIMES)
    else:
        # incomplete -> regenerate same candle with new data
        return previous_start


def matches_any_time(dt: datetime, times: list[time]) -> bool:
    return any([dt.time() == t for t in times])


def get_next_timestamp(dt: datetime, times: list[time]) -> datetime:
    next_timestamp: datetime | None = None

    for valid_time in times:
        if dt.time() < valid_time:
            # e.g. <12:45 -> 12:45
            # e.g. <16:00 -> 16:00
            next_timestamp = datetime.combine(dt.date(), valid_time, tzinfo=TZ)
            break

    if next_timestamp is None:
        # e.g. >=16:00 -> nächster Tag 12:45
        next_timestamp = dt + timedelta(days=1)
        next_timestamp = datetime.combine(next_timestamp, times[0], tzinfo=TZ)

    if next_timestamp.weekday() > 4:
        # Samstag/Sonntag -> Montag 12:45
        next_timestamp += timedelta(days=7 - next_timestamp.weekday())
        next_timestamp = datetime.combine(next_timestamp.date(), times[0], tzinfo=TZ)

    return next_timestamp


def get_previous_timestamp(dt: datetime, times: list[time]) -> datetime:
    previous_timestamp: datetime | None = None

    for valid_time in sorted(times, reverse=True):
        if dt.time() > valid_time:
            # e.g. >16:00 -> 16:00
            # e.g. >12:45 -> 12:45
            previous_timestamp = datetime.combine(dt.date(), valid_time, tzinfo=TZ)
            break

    if previous_timestamp is None:
        # g.g. <=12:45 -> vorheriger Tag 16:00
        previous_timestamp = dt - timedelta(days=1)
        previous_timestamp = datetime.combine(previous_timestamp.date(), times[-1], tzinfo=TZ)

    if previous_timestamp.weekday() > 4:
        # Samstag/Sonntag -> Freitag 16:00
        previous_timestamp -= timedelta(days=previous_timestamp.weekday() - 4)
        previous_timestamp = datetime.combine(previous_timestamp.date(), times[-1], tzinfo=TZ)

    return previous_timestamp


def read_schedule_timestamp() -> datetime | None:
    if not os.path.exists('docs/metadata.json'):
        return None
    with open('docs/metadata.json', 'r') as f:
        metadata = json.load(f)
        return datetime.fromisoformat(metadata["timestamp"])


def write_schedule_timestamp(dt: datetime):
    metadata = {"timestamp": dt.isoformat()}
    with open('docs/metadata.json', 'w', encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)
