import os
from datetime import timedelta

import pandas as pd
from pytz import timezone

import screener.download as download

os.makedirs('cache', exist_ok=True)

tz_new_york = timezone('America/New_York')
tz_berlin = timezone('Europe/Berlin')


def download_195m(stock, start, end):
    df_cache = _read_cache(stock)

    if df_cache is None:
        df = download.download_195m(stock, start, end)
    else:
        # filter
        df_cache = df_cache[
            (df_cache['Datetime'] >= tz_berlin.localize(start)) & (df_cache['Datetime'] < tz_berlin.localize(end))]
        start_cache = df_cache['Datetime'].iloc[0].astimezone(tz_new_york).replace(tzinfo=None)
        end_cache = df_cache['Datetime'].iloc[-1].astimezone(tz_new_york).replace(tzinfo=None) + timedelta(minutes=195)

        df_before_cache = download.download_195m(stock, start, start_cache) if start < start_cache else None
        df_after_cache = download.download_195m(stock, end_cache, end) if end > end_cache else None

        df = _concat_dfs([df_before_cache, df_cache, df_after_cache])

    _write_cache(df)
    return df


def _read_cache(stock):
    try:
        with open(f'cache/{stock}.csv', 'r') as f:
            df = pd.read_csv(f, parse_dates=['Datetime'])
            df.attrs['stock'] = stock
            return df
    except:
        print(f'No cache found for {stock}')
        return None


def _write_cache(df):
    with open(f'cache/{df.attrs["stock"]}.csv', 'w') as f:
        df.to_csv(f, index=False)


def _concat_dfs(dfs):
    dfs_filtered = [df for df in dfs if df is not None]
    df = pd.concat(dfs_filtered)
    df.reset_index(inplace=True, drop=True)
    return df
