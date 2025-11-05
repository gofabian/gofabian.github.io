import asyncio
from datetime import datetime
from typing import Callable

import pandas as pd
from ib_async import *
from pandas import DataFrame

from log import log

IB_HOST = '127.0.0.1'
IB_PORT = 4002
# IB_PORT = 7496
FAST_MAX_CONCURRENT = 4
SLOW_SECONDS_PER_REQUEST = 10

# fix asyncio even loop issues on Windows
util.patchAsyncio()


def download_symbol(symbol: str, end: datetime, duration: str) -> DataFrame:
    async def do_async() -> DataFrame:
        ib = IB()
        await ib.connectAsync(IB_HOST, IB_PORT, clientId=1)
        df = await _download_symbol_async(ib, symbol, end, duration)
        ib.disconnect()
        return df

    return asyncio.run(do_async())


# for short durations < '1 W' (depends on bar size)
def download_symbols_in_parallel(symbols: list[str], end: datetime, duration: str) -> list[DataFrame]:
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

    # switch to pandas world
    df = util.df(bars)
    df['date'] = df['date'].dt.tz_convert('America/New_York')
    df.attrs["symbol"] = symbol
    df.attrs["timestamp_end"] = end

    def floor_195min(ts):
        start_of_day = ts.normalize() + pd.Timedelta(hours=9, minutes=30)
        delta = ts - start_of_day
        return start_of_day + delta.floor("195min")

    return aggregate_candles(df, lambda dt: floor_195min(dt))


def aggregate_candles(df: DataFrame, group_func: Callable[[pd.Timestamp], object]):
    groups = df['date'].map(group_func)
    group = df.groupby(groups)

    df_result = group.agg({
        'date': 'first',
        'open': 'first',
        'high': 'max',
        'low': 'min',
        'close': 'last',
        'volume': 'sum'
    })
    df_result = df_result.reset_index(drop=True)

    df_result.attrs = df.attrs.copy()

    return df_result
