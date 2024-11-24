from datetime import datetime, timedelta

import pandas as pd
import requests_cache
from pytz import utc, timezone
from yfinance import Ticker

session = requests_cache.CachedSession('yfinance.cache')
tz_new_york = timezone('America/New_York')
tz_berlin = timezone('Europe/Berlin')


def download_195m(stock, start, end):
    df_1d, df_15m = _download_195m_raw_data(stock, start, end)
    return _convert_df_1d_and_df_15m_into_df_195m(df_1d, df_15m)


def _download_195m_raw_data(stock, start, end):
    # ...1d data... <now-58d> ...15m data... <now>
    today = datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)
    threshold_1d_158m = today - timedelta(days=58)

    # fetch 15m data
    if end > threshold_1d_158m:
        start_15m = threshold_1d_158m if start < threshold_1d_158m else start
        end_15m = end
        df_15m = _yf_history(
            stock=stock,
            interval="15m",
            start=start_15m,  # api allows max 60 days in past for '15m'
            end=end_15m,
        )
    else:
        df_15m = None

    # fetch 1d data
    if start < threshold_1d_158m:
        start_1d = start.replace(hour=0, minute=0, second=0, microsecond=0)
        end_1d = threshold_1d_158m if end > threshold_1d_158m else end.replace(hour=23, minute=0, second=0,
                                                                               microsecond=0)
        df_1d = _yf_history(
            stock=stock,
            interval="1d",
            start=start_1d,  # api allows max 730 days in past for '1d'
            end=end_1d,
        )
    else:
        df_1d = None

    return df_1d, df_15m


def _yf_history(stock, interval, start, end):
    start = _harmonize_datetime(start)
    end = _harmonize_datetime(end)

    if start == end:
        df = pd.DataFrame()
    else:
        df = Ticker(stock, session).history(
            interval=interval,
            start=start,
            end=end,
            actions=False,
            raise_errors=True
        )

    df.attrs['stock'] = stock

    if df.empty:
        return df

    # filter by requested end afterwards
    df = df.loc[:(end.replace(tzinfo=utc) - timedelta(seconds=1))]

    # fix timezone
    df.index = df.index.tz_localize(None).tz_localize(tz_new_york).tz_convert(tz_berlin)

    # Fill na values
    if df['Close'].isnull().any():
        print(f'Found null values in stock {stock}')
    df['CloseBkp'] = df['Close'].values
    df['Close'] = df['Close'].ffill()

    # Drop volume column with na values
    df = df.drop(columns=['Volume'])

    return df


def _harmonize_datetime(dt):
    if dt.hour < 9:
        # no prices expected before 9:00
        dt = dt.replace(hour=9, minute=0, second=0, microsecond=0)
    if dt.hour >= 16:
        # no prices expected after 16:00
        dt = dt.replace(hour=9, minute=0, second=0, microsecond=0) + timedelta(days=1)
    if dt.weekday() > 4:
        # no prices expected at Saturday and Sunday
        dt = dt + timedelta(days=7 - dt.weekday())
    return dt


def _convert_df_1d_and_df_15m_into_df_195m(df_1d, df_15m):
    if df_1d is None:
        return convert_15m_to_195m(df_15m)
    if df_15m is None:
        return convert_1d_to_195m(df_1d)

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
        "CloseBkp": []
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
            data["Close"].append(None)
            data["CloseBkp"].append(None)

        if row["High"] > data["High"][index]:
            data["High"][index] = row["High"]
        if row["Low"] < data["Low"][index]:
            data["Low"][index] = row["Low"]
        data["Close"][index] = row["Close"]
        data["CloseBkp"][index] = row["CloseBkp"]

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
    df_195m = df_195m.reindex(range(df_195m.index.min(), df_195m.index.max() + 2))
    df_195m['Datetime'] = df_195m['Datetime'].interpolate()
    df_195m['Close'] = df_195m['Close'].interpolate()
    df_195m.loc[df_195m.index % 2 == 1, 'CloseBkp'] = df_195m['CloseBkp'].interpolate()[1::2]
    return df_195m
