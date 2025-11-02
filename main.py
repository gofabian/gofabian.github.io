import time
from datetime import datetime, timedelta

import data
import schedule
import website
from log import log

SYMBOLS_SP500 = [
    "NVDA", "MSFT", "AAPL", "GOOG", "AMZN", "META", "AVGO", "TSLA", "BRK B", "ORCL", "JPM", "WMT", "LLY", "V", "NFLX",
    "MA", "XOM", "JNJ", "PLTR", "COST", "ABBV", "HD", "BAC", "AMD", "PG", "UNH", "GE", "CVX", "KO", "CSCO", "IBM",
    "TMUS", "WFC", "PM", "MS", "GS", "CRM", "CAT", "ABT", "AXP", "MU", "MCD", "LIN", "MRK", "RTX", "PEP", "APP", "DIS",
    "TMO", "UBER", "BX", "NOW", "BLK", "ANET", "T", "INTU", "C", "GEV", "AMAT", "QCOM", "INTC", "LRCX", "NEE", "BKNG",
    "SCHW", "VZ", "BA", "ACN", "TXN", "AMGN", "TJX", "ISRG", "APH", "DHR", "GILD", "SPGI", "ETN", "PANW", "ADBE", "BSX",
    "PFE", "SYK", "PGR", "KLAC", "UNP", "COF", "LOW", "HON", "CRWD", "HOOD", "MDT", "IBKR", "CEG", "DE", "LMT", "DASH",
    "ADI", "ADP", "CB", "COP", "MO", "CMCSA", "SO", "KKR", "VRTX", "DELL", "MMC", "NKE", "CVS", "NEM", "DUK", "CME",
    "HCA", "MCK", "TT", "PH", "COIN", "SBUX", "ICE", "CDNS", "GD", "BMY", "NOC", "WM", "ORLY", "MCO", "SNPS", "RCL",
    "SHW", "MMM", "MDLZ", "ELV", "CI", "ECL", "HWM", "WMB", "AJG", "AON", "MSI", "CTAS", "BK", "ABNB", "PNC", "GLW",
    "TDG", "EMR", "USB", "MAR", "ITW", "VST", "NSC", "UPS", "APO"
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
    data.update_data(symbols, request_end, '3 D')
    website.update_website(symbols, request_start, request_end)


cicd(SYMBOLS_SP500)
