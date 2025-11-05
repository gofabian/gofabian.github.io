import os
from datetime import datetime

import pandas as pd
from pandas import DataFrame, Series

import analysis
import fileio
import htmlgen
import schedule
import sector
from log import log


def update_website(symbols: list[str], start: datetime, end: datetime):
    write_candle_pages(symbols, start, end)
    write_timestamp_pages(symbols, start, end)
    htmlgen.write_index_html()
    schedule.write_schedule_timestamp(end)


def write_candle_pages(stock_symbols: list[str], start: datetime, end: datetime):
    log(f"Writing candle pages for {start.isoformat()}...{end.isoformat()}")

    index_analysis_map = {}
    for index_symbol in (sector.SECTOR_SYMBOLS + ["SPY"]):
        df_195m = fileio.df_read("data", index_symbol)
        index_analysis = analysis.analyze_index(df_195m, start, end)
        index_analysis_map[index_symbol] = index_analysis

    for stock_symbol in stock_symbols:
        df_195m = fileio.df_read("data", stock_symbol)
        stock_analysis = analysis.analyze_stock(df_195m, start, end)
        df_195m = stock_analysis.df_195m
        df_1d = stock_analysis.df_1d
        df_1w = stock_analysis.df_1w

        # for each symbol+timestamp -> generate chart.html and metadata.json
        df_195m_focus = df_195m[df_195m["date"] >= start]
        for candle_195m in df_195m_focus.itertuples():
            if 'L' in candle_195m.signal_long:
                advice = 'buy'
            elif 'S' in candle_195m.signal_short:
                advice = 'sell'
            else:
                advice = ''

            if advice == '':
                continue

            if candle_195m.Index == df_195m.index[-1]:
                candle_end = end
            else:
                candle_end = schedule.get_next_timestamp(candle_195m.date, schedule.CANDLE_END_TIMES)

            if schedule.matches_any_time(candle_end, schedule.CANDLE_END_TIMES):
                candle_state = "complete"
            else:
                candle_state = "incomplete"

            candle_1d = _select_candle_1d(df_1d, candle_195m)
            candle_1w = _select_candle_1w(df_1w, candle_195m)
            candle_1d_spy = _select_candle_1d(index_analysis_map['SPY'].df_1d, candle_195m)
            candle_1w_spy = _select_candle_1w(index_analysis_map['SPY'].df_1w, candle_195m)
            sector_name = sector.STOCK_SECTOR_MAPPING[stock_symbol]
            candle_1d_sector = _select_candle_1d(index_analysis_map[sector_name].df_1d, candle_195m)
            candle_1w_sector = _select_candle_1w(index_analysis_map[sector_name].df_1w, candle_195m)

            metadata = {
                "symbol": df_195m.attrs['symbol'],
                "timestamp_start": candle_195m.date,
                "timestamp_end": candle_end,
                "state": candle_state,
                "advice": advice,
                "trend_1d": candle_1d['hl_band'],
                "trend_1w": candle_1w['hl_band'],
                "spy_trend_1d": candle_1d_spy['ema_cross'],
                "spy_trend_1w": candle_1w_spy['ema_cross'],
                "sector": sector_name,
                "sector_trend_1d": candle_1d_sector['hl_band'],
                "sector_trend_1w": candle_1w_sector['hl_band'],
            }

            candle_df = df_195m[df_195m['date'] <= candle_195m.date].tail(30).reset_index(drop=True)
            write_candle_page(metadata, candle_df)


def _select_candle_1d(df_1d, candle_195m):
    return df_1d[df_1d['date'].dt.date == candle_195m.date.date()].squeeze()


def _select_candle_1w(df_1w, candle_195m):
    def make_monday(ts: Series) -> Series:
        return ts - pd.Timedelta(days=ts.weekday())

    return df_1w[df_1w['date'].dt.date == make_monday(candle_195m.date).date()].squeeze()


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

            if metadata["advice"] == "buy":
                symbols_signal.append(symbol)
                symbols_long.append(symbol)
            elif metadata["advice"] == "sell":
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
