from datetime import datetime, timedelta

import pandas as pd
import requests_cache
import yfinance as yf
from pytz import utc, timezone


def download_195m(stocks, end):
    dfs_1d, dfs_15m = _download_195m_raw_data(stocks, end)
    return [_convert_df_1d_and_df_15m_into_df_195m(df_1d, dfs_15m[i]) for i, df_1d in enumerate(dfs_1d)]


def _download_195m_raw_data(stocks, end):
    session = requests_cache.CachedSession('yfinance.cache')
    tz_new_york = timezone('America/New_York')
    tz_berlin = timezone('Europe/Berlin')

    #
    # fetch previous 60..<start> days historical stock data from Yahoo Finance API
    #

    today = datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)
    start_15m = today - timedelta(days=58)
    end_15m = end
    print(f'Requesting 15m intervals, start={start_15m}, end: {end_15m}...')
    dfs_15m = yf.download(
        tickers=stocks,
        interval="15m",
        start=start_15m,  # api allows max 60 days for '15m'
        end=today if end_15m < today else end_15m,  # fetch with same end more often to hit the buffer
        group_by='ticker',
        session=session,
        threads=False  # threads do not work with session
    )

    # filter by requested end afterwards
    dfs_15m = dfs_15m.loc[:(end_15m.replace(tzinfo=utc) - timedelta(seconds=1))]

    # fix timezone
    dfs_15m.index = dfs_15m.index.tz_localize(None).tz_localize(tz_new_york).tz_convert(tz_berlin)

    # convert multi-level data frame to separate data frames by ticker
    dfs_15m_temp = []
    for stock in stocks:
        df_15m = dfs_15m[stock].copy()
        df_15m.attrs['stock'] = stock
        dfs_15m_temp.append(df_15m)
    dfs_15m = dfs_15m_temp

    # Fill na values
    for df_15m in dfs_15m:
        df_15m['Close'] = df_15m['Close'].ffill()

    #
    # fetch previous 140..60 days historical stock data from Yahoo Finance API
    #

    start_1d = start_15m - timedelta(days=140)
    end_1d = start_15m
    print(f'Requesting 1d intervals, start={start_1d}, end: {end_1d}...')
    dfs_1d = yf.download(
        tickers=stocks,
        interval="1d",
        start=start_1d,  # api allows max 730 days for '1d'
        end=end_1d,
        group_by='ticker',
        session=session,
        threads=False  # threads do not work with session
    )

    # fix timezone
    dfs_1d.index = dfs_1d.index.tz_localize(None).tz_localize(tz_berlin)

    # convert multi-level data frame to separate data frames by ticker
    dfs_1d_temp = []
    for stock in stocks:
        df_1d = dfs_1d[stock].copy()
        df_1d.attrs['stock'] = stock
        dfs_1d_temp.append(df_1d)
    dfs_1d = dfs_1d_temp

    return dfs_1d, dfs_15m


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
