import os
from datetime import datetime

import pandas as pd
from pandas import DataFrame

import fileio
import source
from log import log

FOLDER = 'data'


# update data folder
def update_data(symbols: list[str], end: datetime):
    log(f"Updating data: symbols={len(symbols)} folder='{FOLDER}' end={end}")
    os.makedirs(FOLDER, exist_ok=True)

    # update data for existing symbols
    symbols_old = [symbol for symbol in symbols if fileio.df_exists(FOLDER, symbol)]
    log(f"Update data for symbols={len(symbols_old)} duration=3 D")
    dfs_plus = source.download_symbols_in_parallel(symbols_old, end, '3 D')
    for df_plus in dfs_plus:
        symbol = df_plus.attrs['symbol']
        df_base = fileio.df_read(FOLDER, symbol)
        df = _concat_dfs(df_base, df_plus)
        fileio.df_write(FOLDER, df)

    # add data for new symbols
    symbols_new = [symbol for symbol in symbols if symbol not in symbols_old]
    log(f"Create data for symbols={len(symbols_new)} duration=100 D")
    for symbol in symbols_new:
        df = source.download_symbol(symbol, end, '1 Y')
        fileio.df_write(FOLDER, df)

    log(f"Updated data")


def _concat_dfs(df_base: DataFrame, df_plus: DataFrame) -> DataFrame:
    # check overlapping between old and new data
    last_old_ts = df_base["date"].iloc[-1]
    first_new_ts = df_plus["date"].iloc[0]

    if last_old_ts < first_new_ts:
        symbol = df_base.attrs['symbol']
        raise Exception(f"Found gap between old and new data: symbol={symbol}, "
                        f"old_end={last_old_ts.isoformat()}, new_start={first_new_ts.isoformat()}")

    # remove overlapping rows in old data
    df = df_base[df_base["date"] < first_new_ts]

    # # remove very old data
    # last_new_ts = df_plus["date"].iloc[-1]
    # df = df[df["date"] >= last_new_ts - pd.DateOffset(years=1)]

    # add new rows to old data
    df = pd.concat([df, df_plus], ignore_index=True)

    # combine attributes
    attrs = df_base.attrs.copy()
    attrs.update(df_plus.attrs)
    df.attrs = attrs
    return df
