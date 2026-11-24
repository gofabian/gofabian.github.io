import time
from datetime import datetime, timedelta

import data
import schedule
import sector
import website
from log import log

# S&P500
# nur Stammaktien
# Marktkapitalisierung > 70B
# Volumen 60D > 4M
SYMBOLS = [
    "AAPL", "NVDA", "MSFT", "GOOG", "GOOGL", "AMZN", "META", "TSLA", "AVGO", "BRK B", "WMT", "JPM", "V", "MU", "AMD",
    "JNJ", "XOM", "ABBV", "KO", "CVX", "PG", "PLTR", "CSCO", "HD", "MRK", "BAC", "ORCL", "GE", "UNH", "INTC", "PM",
    "PANW", "RTX", "MS", "AMAT", "LRCX", "WFC", "NFLX", "TXN", "GILD", "IBM", "CRWD", "ANET", "DIS", "MCD", "VZ", "PEP",
    "C", "DELL", "ABT", "APH", "TMUS", "NEE", "QCOM", "KLAC", "PFE", "SCHW", "DHR", "COP", "TJX", "CRM", "T", "ADI",
    "BX", "ACN", "UBER", "BA", "IBKR", "APP", "BMY", "MO", "MDT", "SBUX", "MRVL", "STX", "SO", "COF", "BKNG", "CVS",
    "NEM", "ABNB", "WDC", "DUK", "FTNT", "NOW", "UPS", "CSX", "MRNA", "CMCSA", "ADBE", "USB", "SNDK", "GLW", "MDLZ",
    "KKR", "MNST", "WMB", "JCI", "CL", "ORLY", "CVNA"
]


def cicd(symbols: list[str]):
    request_start = schedule.get_start_timestamp()
    request_end = schedule.get_end_timestamp()
    log(f"start={request_start.isoformat()} end={request_end.isoformat()}")

    # past candles?
    if request_start < request_end:
        update(symbols, request_start, request_end)
        return

    # next candle soon?
    now = datetime.now(tz=schedule.TZ)
    request_end = schedule.get_next_timestamp(now, schedule.SCHEDULE_TIMES)
    if request_end - timedelta(minutes=15) > now:
        log("Cancelled.")
        return

    # next candle soon
    while True:
        now = datetime.now(tz=schedule.TZ)
        log(f'Waiting... now={now} until={request_end.isoformat()}')
        if now >= request_end:
            break
        time.sleep(60)

    # next candle now
    log(f"start={request_start.isoformat()} end={request_end.isoformat()}")
    request_start = schedule.get_previous_timestamp(request_end, schedule.CANDLE_START_TIMES)
    update(symbols, request_start, request_end)


def update(symbols: list[str], request_start: datetime, request_end: datetime):
    symbols_update = symbols + sector.SECTOR_SYMBOLS + ["SPY"]
    data.update_data(symbols_update, request_end)
    website.update_website(symbols, request_start, request_end)


cicd(SYMBOLS)

#start = datetime.fromisoformat("2025-01-01T09:30:00-04:00")
#end = schedule.get_end_timestamp() #datetime.fromisoformat("2026-11-247T16:00:00-04:00")
#update(SYMBOLS, start, end)

# start = datetime.fromisoformat("2025-01-01T09:30:00-04:00")
# end = datetime.fromisoformat("2025-11-07T16:00:00-04:00")

# website.write_timestamp_pages(SYMBOLS_SP500, start, end)
