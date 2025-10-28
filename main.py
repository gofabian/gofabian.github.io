from datetime import datetime, timedelta
from time import sleep

from batch import batch
from github import git_commit_and_push
from logic import export_charts
from schedule import get_due_timestamps, write_timestamp, get_next_timestamp, TZ

# s&p500 MK>70B
symbols = ["NVDA", "MSFT", "AAPL", "GOOG", "AMZN", "META", "AVGO", "TSLA", "BRK B", "ORCL", "JPM", "WMT",
           "LLY", "V", "NFLX", "MA", "XOM", "JNJ", "PLTR", "COST", "ABBV", "HD", "BAC", "AMD", "PG", "UNH", "GE", "CVX",
           "KO", "CSCO", "IBM", "TMUS", "WFC", "PM", "MS", "GS", "CRM", "CAT", "ABT", "AXP", "MU", "MCD", "LIN", "MRK",
           "RTX", "PEP", "APP", "DIS", "TMO", "UBER", "BX", "NOW", "BLK", "ANET", "T", "INTU", "C", "GEV", "AMAT",
           "QCOM", "INTC", "LRCX", "NEE", "BKNG", "SCHW", "VZ", "BA", "ACN", "TXN", "AMGN", "TJX", "ISRG", "APH", "DHR",
           "GILD", "SPGI", "ETN", "PANW", "ADBE", "BSX", "PFE", "SYK", "PGR", "KLAC", "UNP", "COF", "LOW", "HON",
           "CRWD", "HOOD", "MDT", "IBKR", "CEG", "DE", "LMT", "DASH", "ADI", "ADP", "CB", "COP", "MO", "CMCSA", "SO",
           "KKR", "VRTX", "DELL", "MMC", "NKE", "CVS", "NEM", "DUK", "CME", "HCA", "MCK", "TT", "PH", "COIN", "SBUX",
           "ICE", "CDNS", "GD", "BMY", "NOC", "WM", "ORLY", "MCO", "SNPS", "RCL", "SHW", "MMM", "MDLZ", "ELV", "CI",
           "ECL", "HWM", "WMB", "AJG", "AON", "MSI", "CTAS", "BK", "ABNB", "PNC", "GLW", "TDG", "EMR", "USB", "MAR",
           "ITW", "VST", "NSC", "UPS", "APO"]

# symbols = ["NVDA"]


def get_batch_fn(ts: datetime):
    def batch_fn(symbols_batch: list[str], batch_i: int, batch_all: int):
        progress = ((batch_i + 1) * 100) // batch_all
        export_charts(symbols_batch, ts, progress)
        write_timestamp(ts)
        git_commit_and_push()

    return batch_fn


# process timestamps in the past
timestamps = get_due_timestamps()
for timestamp in timestamps:
    # todo log
    print(timestamp.isoformat())

if len(timestamps) > 0:
    next_timestamp = timestamps[0]
    batch(symbols, 55, 600, get_batch_fn(next_timestamp))
else:
    # process "near" next timestamp
    now = datetime.now(tz=TZ)
    next_timestamp = get_next_timestamp(now)
    if now + timedelta(minutes=15) > next_timestamp:
        while True:
            now = datetime.now(tz=TZ)
            print(f'Waiting... now={now} until={next_timestamp.time()}')
            if now >= next_timestamp:
                break
            sleep(60)

        print(f'Report due now -> generate')
        batch(symbols, 55, 600, get_batch_fn(next_timestamp))
