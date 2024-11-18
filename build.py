from datetime import datetime, timedelta

from screener import generate
from stocks import stocks

now = datetime.today()

if now > now.replace(hour=22, minute=0, second=0, microsecond=0):  # tz=Berlin
    end = now.replace(hour=16, minute=0, second=0, microsecond=0)  # tz=New York
elif now > now.replace(hour=18, minute=45, second=0, microsecond=0):  # tz=Berlin
    end = now.replace(hour=12, minute=45, second=0, microsecond=0)  # tz=New York
else:
    end = now.replace(hour=16, minute=0, second=0, microsecond=0) - timedelta(days=1)  # tz=New York

print(f'Generating report for {end}...')
generate(stocks, end)
