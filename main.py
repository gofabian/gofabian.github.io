from datetime import datetime

from pytz import timezone

from finance import generate
from stocks import stocks

# pjm
# end = datetime(year=2024, month=11, day=11, hour=12, minute=00, second=0, microsecond=0)
# end = datetime(year=2024, month=11, day=11, hour=15, minute=00, second=0, microsecond=0)

# tv
# end = datetime(year=2024, month=11, day=14, hour=12, minute=45, second=0, microsecond=0)
# end = datetime(year=2024, month=11, day=12, hour=16, minute=00, second=0, microsecond=0)

end = datetime(year=2024, month=11, day=12, hour=12, minute=45, second=0, microsecond=0)
generate(stocks, end)


# todo: timezone mismatch


def abc():
    tz_new_york = timezone('America/New_York')

    end = datetime(year=2024, month=11, day=11, hour=12, minute=00, second=0, microsecond=0)
    print(end)

    tz_berlin = timezone('Europe/Berlin')
    end2 = tz_new_york.localize(end)
    print(end2)
    end3 = end2.astimezone(tz_berlin)
    print(end3)
