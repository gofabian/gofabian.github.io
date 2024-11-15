from datetime import datetime, timedelta

from finance import generate
from stocks import stocks

now = datetime.today()

if now > now.replace(hour=18, minute=45, second=0, microsecond=0):
    end = now.replace(hour=12, minute=45, second=0, microsecond=0)
elif now > now.replace(hour=22, minute=0, second=0, microsecond=0):
    end = now.replace(hour=16, minute=0, second=0, microsecond=0)
else:
    end = now.replace(hour=16, minute=0, second=0, microsecond=0) - timedelta(days=1)

generate(stocks, end)
