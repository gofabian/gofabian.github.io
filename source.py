from datetime import datetime

import pandas as pd
from ib_async import *


def req_historical_data(
        ib: IB,
        symbol: str,
        end_datetime: datetime = '',
        duration_str: str = '30 D'
) -> pd.DataFrame:
    # access interactive broker api
    bars = ib.reqHistoricalData(
        Stock(symbol, 'SMART', 'USD'),
        endDateTime=end_datetime,
        durationStr=duration_str,
        barSizeSetting='15 mins',
        whatToShow='TRADES',
        useRTH=True
    )

    # switch to pandas world
    df_15 = util.df(bars)
    # print(df.to_string())

    # convert 15min candles to 195min candles
    df_15 = df_15.set_index('date')

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

    df_195 = df_15.groupby(df_15.index.date, group_keys=False).apply(aggregate_daily)
    df_195 = df_195.reset_index(drop=True)

    # nutze Börsenzeitzone (immer -04:00)
    df_195['date'] = df_195['date'].dt.tz_convert('-04:00')
    # print(df_195.to_string())

    return df_195
