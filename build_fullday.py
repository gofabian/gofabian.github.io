from datetime import datetime

from finance import generate
from stocks import stocks

end = datetime.today().replace(hour=16, minute=0, second=0, microsecond=0)
generate(stocks, end)
