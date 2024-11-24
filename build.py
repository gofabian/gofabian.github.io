import os
import time
from datetime import datetime, timedelta

from pytz import timezone

from screener import generate
from stocks import stocks

previous_start = datetime.fromisoformat(
    sorted([f for f in os.listdir("docs") if os.path.isdir(f"docs/{f}")])[-1]
)
tz_new_york = timezone('America/New_York')
tz_berlin = timezone('Europe/Berlin')
previous_start = tz_berlin.localize(previous_start).astimezone(tz_new_york)

if previous_start.hour >= 12:
    next_start = previous_start.replace(hour=9, minute=30) + timedelta(days=1)
    if next_start.weekday() > 4:
        next_start += timedelta(days=7 - next_start.weekday())
else:
    next_start = previous_start.replace(hour=12, minute=45)

next_end = next_start.replace(tzinfo=None) + timedelta(minutes=195)
now = datetime.now(tz=tz_new_york).replace(tzinfo=None)

print(f'Next report time: {next_end}')

if now >= next_end:
    print(f'Report overdue -> generate')
    generate(stocks, next_end)
elif now + timedelta(minutes=15) > next_end:
    while True:
        now = datetime.now(tz=tz_new_york).replace(tzinfo=None)
        print(f'Waiting now={now.time()} until={next_end.time()}...')
        if now >= next_end:
            break
        time.sleep(60)
    print(f'Report due now -> generate')
    generate(stocks, next_end)
