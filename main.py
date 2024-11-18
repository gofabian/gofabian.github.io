from datetime import datetime

from screener import generate
from stocks import stocks

# pjm
# end = datetime(year=2024, month=11, day=11, hour=12, minute=00, second=0, microsecond=0)
# end = datetime(year=2024, month=11, day=11, hour=15, minute=00, second=0, microsecond=0)

# trading view
# end = datetime(year=2024, month=11, day=14, hour=12, minute=45, second=0, microsecond=0)
# end = datetime(year=2024, month=11, day=12, hour=16, minute=00, second=0, microsecond=0)

end = datetime(year=2024, month=11, day=15, hour=16, minute=0, second=0, microsecond=0)
generate(stocks, end)
