import os
from datetime import datetime, timedelta, time
from time import sleep

from pytz import timezone

from screener import generate
from stocks import stocks

end_times = [
    # time(hour=12, minute=0),  # PJM
    time(hour=12, minute=45),  # 1st 195m candle
    # time(hour=15, minute=0),  # PJM
    time(hour=16, minute=0)  # 2nd 195m candle
]

tz_new_york = timezone('America/New_York')
tz_berlin = timezone('Europe/Berlin')


def get_previous_end():
    previous_start = datetime.fromisoformat(
        sorted([f for f in os.listdir("docs") if os.path.isdir(f"docs/{f}")])[-1]
    )
    previous_start = tz_berlin.localize(previous_start).astimezone(tz_new_york).replace(tzinfo=None)
    return previous_start + timedelta(minutes=195)


previous_end = get_previous_end()

end_times = sorted(end_times, reverse=True)
next_end = None
for i, end_time in enumerate(end_times):
    if previous_end.time() >= end_time:
        next_end = datetime.combine(previous_end.date(), end_times[i - 1])
        if next_end.time() < previous_end.time():
            next_end += timedelta(days=1)
        if next_end.weekday() > 4:
            next_end += timedelta(days=7 - next_end.weekday())
        break

now = datetime.now(tz=tz_new_york).replace(tzinfo=None)

print(f'Next report time: {next_end}')

if now >= next_end:
    print(f'Report overdue -> generate')
    generate(stocks, next_end)
elif now + timedelta(minutes=15) > next_end:
    while True:
        now = datetime.now(tz=tz_new_york).replace(tzinfo=None)
        print(f'Waiting now={now} until={next_end.time()}...')
        if now >= next_end:
            break
        sleep(60)
    print(f'Report due now -> generate')
    generate(stocks, next_end)
