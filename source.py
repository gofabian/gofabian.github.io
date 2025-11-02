import asyncio
import time
from datetime import datetime, timedelta

from ib_async import *
from pandas import DataFrame

from log import log

IB_HOST = '127.0.0.1'
IB_PORT = 4002
FAST_MAX_CONCURRENT = 4
SLOW_SECONDS_PER_REQUEST = 10


# for long durations > '1 W' (depends on bar size)
def download_symbol_slow(symbol: str, end: datetime, duration: str) -> DataFrame:
    dt_start = datetime.now()
    df = download_symbol(symbol, end, duration)
    seconds_rest = SLOW_SECONDS_PER_REQUEST - (datetime.now() - dt_start).total_seconds()
    log(f"Waiting {0 if seconds_rest < 0 else seconds_rest}s")
    if seconds_rest > 0:
        time.sleep(seconds_rest)
    return df


def download_symbol(symbol: str, end: datetime, duration: str) -> DataFrame:
    ib = IB()
    ib.connect(IB_HOST, IB_PORT, clientId=1)
    df = _download_symbol_sync(ib, symbol, end, duration)
    ib.disconnect()
    return df


# for short durations < '1 W' (depends on bar size)
def download_symbols_fast(symbols: list[str], end: datetime, duration: str) -> list[DataFrame]:
    return asyncio.run(_download_symbols_async(symbols, end, duration))


async def _download_symbols_async(symbols: list[str], end: datetime, duration: str):
    ib = IB()
    await ib.connectAsync(IB_HOST, IB_PORT, clientId=1)

    semaphore = asyncio.Semaphore(FAST_MAX_CONCURRENT)

    async def task_wrapper(symbol):
        async with semaphore:
            return await _download_symbol_async(ib, symbol, end, duration)

    tasks = [asyncio.create_task(task_wrapper(symbol)) for symbol in symbols]
    await asyncio.gather(*tasks)

    ib.disconnect()

    return [t.result() for t in tasks]


async def _download_symbol_async(ib: IB, symbol: str, end: datetime, duration: str) -> DataFrame:
    log(f"Downloading symbol={symbol} end={end.isoformat()}, duration={duration}")
    bars = await ib.reqHistoricalDataAsync(
        Stock(symbol, 'SMART', 'USD'),
        endDateTime=end,
        durationStr=duration,
        barSizeSetting='15 mins',
        whatToShow='TRADES',
        useRTH=True
    )
    log(f"Downloaded {symbol}")

    return _convert_bars15_to_df195(symbol, end, bars)


def _download_symbol_sync(ib: IB, symbol: str, end: datetime, duration: str) -> DataFrame:
    log(f"Downloading symbol={symbol} end={end.isoformat()}, duration={duration}")
    bars = ib.reqHistoricalData(
        Stock(symbol, 'SMART', 'USD'),
        endDateTime=end,
        durationStr=duration,
        barSizeSetting='15 mins',
        whatToShow='TRADES',
        useRTH=True
    )
    log(f"Downloaded {symbol}")

    return _convert_bars15_to_df195(symbol, end, bars)


def _convert_bars15_to_df195(symbol, end, bars) -> DataFrame:
    # switch to pandas world
    df_15 = util.df(bars)

    # convert 15min candles to 195min candles
    def aggregate_daily(group):
        n = 13  # 195 min / 15 min = 13 Zeilen
        grp = group.reset_index().groupby(group.reset_index().index // n)
        return grp.agg({
            'date': 'first',
            'open': 'first',
            'high': 'max',
            'low': 'min',
            'close': 'last',
            'volume': 'sum'
        })

    df_15 = df_15.set_index('date')
    df_195 = df_15.groupby(df_15.index.date, group_keys=False).apply(aggregate_daily)
    df_195 = df_195.reset_index(drop=True)

    # Börsenzeitzone
    df_195['date'] = df_195['date'].dt.tz_convert('America/New_York')

    start_last_candle = df_195['date'].iloc[-1]
    df_195.attrs["symbol"] = symbol
    df_195.attrs["timestamp_end"] = end
    df_195.attrs["last_candle"] = "complete" if start_last_candle + timedelta(minutes=195) == end else "incomplete",

    return df_195
