from datetime import datetime

from finance import generate
from stocks import stocks

end = datetime.today().replace(hour=12, minute=45, second=0, microsecond=0)
generate(stocks, end)
