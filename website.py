import os
from datetime import datetime, timedelta

from pandas import DataFrame

import fileio
import htmlgen
import indication
import schedule
import signals
from log import log


def update_website(symbols: list[str], start: datetime, end: datetime):
    write_candle_pages(symbols, start, end)
    write_timestamp_pages(symbols, start, end)
    htmlgen.write_index_html()
    schedule.write_schedule_timestamp(end)


def analyze(df: DataFrame, start: datetime, end: datetime) -> DataFrame:
    log(f"Analyzing data for {df.attrs['symbol']}")

    # add indicators
    start_indication = start - timedelta(days=100 // 5 * 7)
    df = df[(df["date"] >= start_indication) & (df["date"] <= end)]
    df = indication.analyze(df)

    # add signals
    start_signals = start - timedelta(days=30)  # >30 candles
    df = df[start_signals <= df["date"]]
    df = signals.find_signals(df)

    return df


def write_candle_pages(symbols: list[str], start: datetime, end: datetime):
    log(f"Writing candle pages for {start.isoformat()}...{end.isoformat()}")

    for symbol in symbols:
        df = fileio.df_read("data", symbol)
        df = analyze(df, start, end)

        # for each symbol+timestamp -> generate chart.html and metadata.json
        df_focus = df[df["date"] >= start]
        for candle in df_focus.itertuples():
            if "L" not in candle.signal_long and "S" not in candle.signal_short:
                continue

            if candle.Index == df.index[-1]:
                candle_end = end
            else:
                candle_end = schedule.get_next_timestamp(candle.date, schedule.CANDLE_END_TIMES)

            if schedule.matches_any_time(candle_end, schedule.CANDLE_END_TIMES):
                candle_state = "complete"
            else:
                candle_state = "incomplete"

            metadata = {
                "symbol": df.attrs['symbol'],
                "timestamp_start": candle.date,
                "timestamp_end": candle_end,
                "state": candle_state,
                "signal_long": candle.signal_long,
                "signal_short": candle.signal_short,
            }

            candle_df = df[df['date'] <= candle.date].tail(30).reset_index(drop=True)
            write_candle_page(metadata, candle_df)


def write_candle_page(metadata: dict, df: DataFrame):
    log(f"Writing candle page {metadata['timestamp_start'].isoformat()} {metadata['symbol']}")

    folder = get_candle_folder(metadata['timestamp_start'], metadata['symbol'])
    os.makedirs(folder, exist_ok=True)

    htmlgen.write_chart_html(metadata["symbol"], df, f"{folder}/chart.html")
    fileio.dict_write(f'{folder}/metadata.json', metadata)


def write_timestamp_pages(symbols: list[str], start: datetime, end: datetime):
    candle_start = start
    while candle_start < end:
        candle_end = schedule.get_next_timestamp(candle_start, schedule.CANDLE_END_TIMES)
        if candle_end > end:
            candle_end = end

        write_timestamp_page(symbols, candle_start, candle_end)

        candle_start = schedule.get_next_timestamp(candle_start, schedule.CANDLE_START_TIMES)


def write_timestamp_page(symbols: list[str], start: datetime, end: datetime):
    log(f"Writing timestamp page start={start.isoformat()} end={end.isoformat()}")

    symbols_signal = []
    symbols_long = []
    symbols_short = []

    for symbol in symbols:
        folder = get_candle_folder(start, symbol)
        if os.path.isdir(folder):
            metadata = fileio.dict_read(f"{folder}/metadata.json")

            if "L" in metadata["signal_long"]:
                symbols_signal.append(symbol)
                symbols_long.append(symbol)
            if "S" in metadata["signal_short"]:
                symbols_signal.append(symbol)
                symbols_short.append(symbol)

    if schedule.matches_any_time(end, schedule.CANDLE_END_TIMES):
        state = 'complete'
    else:
        state = 'incomplete'

    metadata = {
        "timestamp_start": start,
        "timestamp_end": end,
        "state": state,
        'symbols': symbols,
        'symbols_signal': symbols_signal,
        'symbols_long': symbols_long,
        'symbols_short': symbols_short,
    }

    folder = get_timestamp_folder(start)
    os.makedirs(folder, exist_ok=True)

    htmlgen.write_report_html(metadata, folder)
    fileio.dict_write(f'{folder}/metadata.json', metadata)


def get_candle_folder(timestamp, symbol) -> str:
    return f"{get_timestamp_folder(timestamp)}/{symbol}"


def get_timestamp_folder(timestamp: datetime) -> str:
    return f"docs/{timestamp.strftime('%Y-%m-%dT%H%M')}"
