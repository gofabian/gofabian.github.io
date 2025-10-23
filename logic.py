import json
import os
import time
from datetime import datetime
from typing import Tuple

from pandas import DataFrame

import indication
import signals
import source
from htmlgen import write_chart_html, write_report_html, write_index_html
from log import log

WEEKDAYS = ['Montag', 'Dienstag', 'Mittwoch', 'Donnerstag', 'Freitag', 'Samstag', 'Sonntag']


def export_charts(symbols: list[str], end_datetime: datetime):
    folder = f"docs/{end_datetime.strftime('%Y-%m-%dT%H%M')}"
    log(f"Target: {folder}")
    os.makedirs(folder, exist_ok=True)

    symbols_signal = []
    symbols_long = []
    symbols_short = []

    for i, symbol in enumerate(symbols):
        log(f"=== {symbol} {i + 1}/{len(symbols)} ===")
        metadata_symbol, df = analyze_symbol(symbol, end_datetime)

        if "L" in metadata_symbol["signals_long"]:
            export_chart(metadata_symbol, df, f"{folder}/{symbol}")
            symbols_long.append(symbol)
            symbols_signal.append(symbol)
        elif "S" in metadata_symbol["signals_short"]:
            export_chart(metadata_symbol, df, f"{folder}/{symbol}")
            symbols_short.append(symbol)
            symbols_signal.append(symbol)
        # else:
        #     export_chart(metadata_symbol, df, f"{folder}/{symbol}")
        #     symbols_signal.append(symbol)

        if (i + 1) < len(symbols):
            # Max. 60 Requests pro 10 Minuten -> 1 Request pro 10 Sekunden
            time.sleep(10)

    # report
    metadata = {
        "timestamp": end_datetime,
        'title': WEEKDAYS[end_datetime.weekday()] + ', ' + end_datetime.strftime('%d.%m.%Y %H:%M'),
        'symbols': symbols,
        'symbols_signal': symbols_signal,
        'symbols_long': symbols_long,
        'symbols_short': symbols_short,
    }
    with open(f'{folder}/metadata.json', 'w') as f:
        md = metadata.copy()
        md['timestamp'] = md['timestamp'].isoformat()
        json.dump(md, f, indent=2)

    write_report_html(metadata, folder)
    write_index_html()


def analyze_symbol(symbol: str, end_datetime: datetime) -> Tuple[dict, DataFrame]:
    log(f"Requesting historical data for {symbol}...")
    df = source.req_historical_data(symbol=symbol, end_datetime=end_datetime, duration_str='100 D')

    log(f"Analyzing data for {symbol}...")
    indication.analyze(df)
    df_tail = df.tail(30).copy().reset_index()
    # df_tail = df.copy()
    signals.find_signals(df_tail)

    # metadata
    dt_last_candle = df_tail['date'].iloc[-1]
    signals_long = df_tail['signal_long'].iloc[-1]
    if signals_long is None:
        signals_long = ""
    signals_short = df_tail['signal_short'].iloc[-1]
    if signals_short is None:
        signals_short = ""

    metadata = {
        "timestamp": dt_last_candle,
        "symbol": symbol,
        "signals_long": signals_long,
        "signals_short": signals_short
    }
    return metadata, df_tail


def export_chart(metadata: dict, df: DataFrame, folder: str):
    log(f"Exporting data for {metadata['symbol']}...")
    os.makedirs(folder, exist_ok=True)

    # chart.html
    write_chart_html(metadata["symbol"], df, f"{folder}/chart.html")

    # data.json
    df.to_json(f"{folder}/data.json", orient='records')

    # metadata.json
    with open(f'{folder}/metadata.json', 'w') as f:
        md = metadata.copy()
        md['timestamp'] = md['timestamp'].isoformat()
        json.dump(md, f, indent=2)
