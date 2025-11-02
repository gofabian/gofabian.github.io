import json
import os
from datetime import datetime

import pandas as pd
from pandas import DataFrame


def df_exists(folder: str, symbol: str) -> bool:
    return os.path.exists(f"{folder}/{symbol}.json")


def df_write(folder: str, df: DataFrame):
    prefix = f"{folder}/{df.attrs['symbol']}"
    df.to_json(f"{prefix}.json", orient='records', force_ascii=False)
    dict_write(f"{prefix}_attrs.json", df.attrs)


def df_read(folder: str, symbol: str) -> DataFrame:
    prefix = f"{folder}/{symbol}"

    df = pd.read_json(f"{prefix}.json")
    df['date'] = pd.to_datetime(df["date"], utc=True).dt.tz_convert("America/New_York")

    df.attrs = dict_read(f"{prefix}_attrs.json")
    return df


def dict_write(path: str, d: dict):
    d = d.copy()
    for k, v in list(d.items()):
        if isinstance(v, datetime):
            d[k] = v.isoformat()

    with open(path, 'w', encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False, indent=2)


def dict_read(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        d = json.load(f)

    d = d.copy()
    for k, v in list(d.items()):
        if isinstance(v, str) and len(v) == 25:
            try:
                # yyyy-mm-ddTHH:MM:SS+00:00
                d[k] = datetime.fromisoformat(v)
            except ValueError:
                pass

    return d
