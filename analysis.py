from dataclasses import dataclass
from datetime import datetime, timedelta

import pandas as pd
from pandas import DataFrame

import indication
import pjm
import source
from log import log


@dataclass
class IndexAnalysis:
    df_1d: DataFrame
    df_1w: DataFrame


@dataclass
class StockAnalysis:
    df_195m: DataFrame
    df_1d: DataFrame
    df_1w: DataFrame


def analyze_stock(df: DataFrame, start: datetime, end: datetime) -> StockAnalysis:
    log(f"Analyzing stock {df.attrs['symbol']}")
    start = start.replace(hour=9, minute=30)

    def analyze_195m(df_195m: DataFrame) -> DataFrame:
        # add indicators
        start_indication = start - timedelta(days=100 // 5 * 7)
        df_195m = df_195m[(df_195m["date"] >= start_indication) & (df_195m["date"] <= end)]
        df_195m = indication.analyze(df_195m)
        # add signals
        start_signals = start - timedelta(days=30)
        df_195m = df_195m[start_signals <= df_195m["date"]]
        return pjm.find_signals(df_195m)

    analysis_1d1w = analyze_index(df, start, end)

    return StockAnalysis(
        df_195m=analyze_195m(df),
        df_1d=analysis_1d1w.df_1d,
        df_1w=analysis_1d1w.df_1w,
    )


def analyze_index(df: DataFrame, start: datetime, end: datetime) -> IndexAnalysis:
    log(f"Analyzing index {df.attrs['symbol']}")
    start = start.replace(hour=9, minute=30)

    def analyze_1d(df_195m: DataFrame) -> DataFrame:
        start_indication = start - timedelta(days=150 // 5 * 7)
        df_195m = df_195m[(df_195m["date"] >= start_indication) & (df_195m["date"] <= end)]
        # convert 195m -> 1d
        df_1d = source.aggregate_candles(df_195m, lambda dt: dt.date())
        # add indicators
        df_1d = indication.analyze(df_1d)
        start_result = start - timedelta(days=30)
        return df_1d[start_result <= df_1d["date"]]

    def analyze_1w(df_195m: DataFrame) -> DataFrame:
        start_indication = start - timedelta(weeks=150)
        df_195m = df_195m[(df_195m["date"] >= start_indication) & (df_195m["date"] <= end)]
        # convert 195m -> 1w
        df_1w = source.aggregate_candles(df_195m, lambda dt: (dt - pd.Timedelta(days=dt.weekday())).date())
        # add indicators
        df_1w = indication.analyze(df_1w)
        start_result = start - timedelta(days=30)
        return df_1w[start_result <= df_1w["date"]]

    return IndexAnalysis(
        df_1d=analyze_1d(df),
        df_1w=analyze_1w(df),
    )
