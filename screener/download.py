from datetime import datetime, timedelta

import pandas as pd
import requests_cache
from pytz import utc, timezone
from yfinance import Ticker


def download_195m(stocks, start, end):
    dfs_1d, dfs_15m = _download_195m_raw_data(stocks, start, end)
    return [_convert_df_1d_and_df_15m_into_df_195m(df_1d, dfs_15m[i]) for i, df_1d in enumerate(dfs_1d)]


def _download_195m_raw_data(stocks, start, end):
    # ...1d data... <now-58d> ...15m data... <now>
    today = datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)
    threshold_1d_158m = today - timedelta(days=58)

    # fetch 15m data
    if end > threshold_1d_158m:
        start_15m = threshold_1d_158m if start < threshold_1d_158m else start.replace(hour=0, minute=0, second=0,
                                                                                      microsecond=0)
        end_15m = end
        dfs_15m = _download_15m(stocks, start_15m, end_15m)
    else:
        dfs_15m = []

    # fetch 1d data
    if start < threshold_1d_158m:
        start_1d = start.replace(hour=0, minute=0, second=0, microsecond=0)
        end_1d = threshold_1d_158m if end > threshold_1d_158m else end.replace(hour=0, minute=0, second=0,
                                                                               microsecond=0)
        dfs_1d = _download_1d(stocks, start_1d, end_1d)
    else:
        dfs_1d = []

    return dfs_1d, dfs_15m


def _download_15m(stocks, start, end):
    print(f'Requesting 15m intervals, start={start}, end: {end}...')
    return _yf_download(
        stocks=stocks,
        interval="15m",
        start=start,  # api allows max 60 days in past for '15m'
        end=end,
    )


def _download_1d(stocks, start, end):
    print(f'Requesting 1d intervals, start={start}, end: {end}...')
    return _yf_download(
        stocks=stocks,
        interval="1d",
        start=start,  # api allows max 730 days in past for '1d'
        end=end,
    )


def _yf_download(stocks, interval, start, end):
    session = requests_cache.CachedSession('yfinance.cache')
    tz_new_york = timezone('America/New_York')
    tz_berlin = timezone('Europe/Berlin')

    finished = -1

    def progress(stock):
        nonlocal finished
        finished += 1
        print(f'\rProgress: {finished}/{len(stocks)} {stock}', end='')

    progress('')

    def _yf_history(stock):
        df = Ticker(stock, session).history(
            interval=interval,
            start=start,
            end=end,
            raise_errors=True
        )
        df.attrs['stock'] = stock

        # filter by requested end afterwards
        df = df.loc[:(end.replace(tzinfo=utc) - timedelta(seconds=1))]

        # fix timezone
        df.index = df.index.tz_localize(None).tz_localize(tz_new_york).tz_convert(tz_berlin)

        # Fill na values
        df['Close'] = df['Close'].ffill()

        progress(stock)
        return df

    dfs = [_yf_history(stock) for stock in stocks]
    print()
    return dfs


def _convert_df_1d_and_df_15m_into_df_195m(df_1d, df_15m):
    df_195m_from_1d = convert_1d_to_195m(df_1d)
    df_195m_from_15m = convert_15m_to_195m(df_15m)
    df_195m = pd.concat([df_195m_from_1d, df_195m_from_15m])
    df_195m.reset_index(inplace=True, drop=True)
    return df_195m


def convert_15m_to_195m(df_15m):
    data = {
        "Datetime": [],
        "Open": [],
        "High": [],
        "Low": [],
        "Close": [],
    }

    index = 0
    count_source = 0

    for timestamp, row in df_15m.iterrows():
        if pd.isna(row['Close']):
            print(f'Skipping nan values of {df_15m.attrs["stock"]} {timestamp}... {row.to_string()}')
            continue

        if count_source == 0:
            data["Datetime"].append(timestamp)
            data["Open"].append(row["Open"])
            data["High"].append(-1)
            data["Low"].append(99999999)
            data["Close"].append(-1)

        if row["High"] > data["High"][index]:
            data["High"][index] = row["High"]
        if row["Low"] < data["Low"][index]:
            data["Low"][index] = row["Low"]
        data["Close"][index] = row["Close"]

        count_source += 1
        if count_source >= (195 / 15):
            count_source = 0
            index += 1

    df_195m = pd.DataFrame(data)
    df_195m.attrs = df_15m.attrs
    return df_195m


def convert_1d_to_195m(df_1d):
    df_195m = df_1d.copy()
    df_195m['Datetime'] = df_195m.index
    df_195m.reset_index(inplace=True, drop=True)
    df_195m.index *= 2
    df_195m = df_195m.reindex(range(df_195m.index.min(), df_195m.index.max()))
    df_195m.interpolate(inplace=True)
    return df_195m
