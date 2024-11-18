import json
import os
from datetime import datetime, timedelta

import pandas as pd
import plotly.graph_objects as go
import requests_cache
import yfinance as yf
from jinja2 import Environment, select_autoescape, FileSystemLoader
from plotly.subplots import make_subplots
from pytz import timezone


def generate_data(stock, df_old_1d, df_15m):
    df_15m = df_15m.copy()

    # Drop last row if contains na values
    if pd.isna(df_15m['Close'].iloc[-1]):
        df_15m.drop(df_15m.index[-1], inplace=True)
    # Fill na values
    df_15m['Close'] = df_15m['Close'].ffill()

    #
    # convert 1d into 195m chart
    #

    df_old_195m = df_old_1d.copy()
    df_old_195m['Datetime'] = df_old_195m.index
    df_old_195m.reset_index(inplace=True, drop=True)
    df_old_195m.index *= 2
    df_old_195m = df_old_195m.reindex(range(df_old_195m.index.min(), df_old_195m.index.max()))
    df_old_195m.interpolate(inplace=True)

    #
    # convert 15m into 195m chart
    #

    data = {
        "Datetime": [],
        "Open": [],
        "High": [],
        "Low": [],
        "Close": [],
    }

    index = 0
    count_source = 0
    tz_new_york = timezone('America/New_York')
    tz_berlin = timezone('Europe/Berlin')

    for timestamp, row in df_15m.iterrows():
        if pd.isna(row['Close']):
            print(f'Skipping nan values of {stock} {timestamp}... {row.to_string()}')
            continue

        # remove timezone, set US timezone, convert to German timezone
        timestamp = tz_new_york.localize(timestamp.replace(tzinfo=None)).astimezone(tz_berlin)

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

    #
    # Combine old and new data
    #

    df_195m = pd.concat([df_old_195m, df_195m])
    df_195m.reset_index(inplace=True, drop=True)

    #
    # Calculate EMA5 and EMA20
    #

    df_195m['EMA5'] = df_195m['Close'].ewm(span=5, adjust=False).mean()
    df_195m['EMA20'] = df_195m['Close'].ewm(span=20, adjust=False).mean()

    #
    # Calculate RSI (>=200 Datenpunkte notwendig)
    #

    df_195m['change'] = df_195m['Close'].diff()
    df_195m['gain'] = df_195m.change.mask(df_195m.change < 0, 0.0)
    df_195m['loss'] = -df_195m.change.mask(df_195m.change > 0, -0.0)

    def rma(column, n):
        return column.ewm(alpha=1 / n, min_periods=n, adjust=False).mean()

    df_195m['avg_gain'] = rma(df_195m.gain, 14)
    df_195m['avg_loss'] = rma(df_195m.loss, 14)
    df_195m['rs'] = df_195m.avg_gain / df_195m.avg_loss
    df_195m['rsi'] = 100 - (100 / (1 + df_195m.rs))

    df_195m['rsi_sma'] = df_195m['rsi'].rolling(14).mean()

    #
    # Find signals
    #

    df_195m_previous = df_195m.shift()

    # long
    df_195m['rsi_crossing_sma_up'] = (
            (df_195m['rsi'] > df_195m['rsi_sma']) & (df_195m_previous['rsi'] <= df_195m_previous['rsi_sma'])
    )
    df_195m['price_crossing_ema20_up'] = (
            (df_195m['Close'] > df_195m['EMA20']) & (df_195m_previous['Close'] <= df_195m_previous['EMA20'])
    )
    df_195m['ema5_crossing_ema20_up'] = (
            (df_195m['EMA5'] > df_195m['EMA20']) & (df_195m_previous['EMA5'] <= df_195m_previous['EMA20'])
    )

    # short
    df_195m['rsi_crossing_sma_down'] = (
            (df_195m['rsi'] < df_195m['rsi_sma']) & (df_195m_previous['rsi'] >= df_195m_previous['rsi_sma'])
    )
    df_195m['price_crossing_ema20_down'] = (
            (df_195m['Close'] < df_195m['EMA20']) & (df_195m_previous['Close'] >= df_195m_previous['EMA20'])
    )
    df_195m['ema5_crossing_ema20_down'] = (
            (df_195m['EMA5'] < df_195m['EMA20']) & (df_195m_previous['EMA5'] >= df_195m_previous['EMA20'])
    )

    df_195m['signal_long'] = None
    rsi_crossed_sma_up = False
    price_crossed_ema20_up = False
    ema5_crossed_ema20_up = False
    df_195m['signal_short'] = None
    rsi_crossed_sma_down = False
    price_crossed_ema20_down = False
    ema5_crossed_ema20_down = False
    for index, row in df_195m.tail(20).iterrows():
        signal_long = []
        if not rsi_crossed_sma_up:
            rsi_crossed_sma_up = row['rsi_crossing_sma_up']
            if rsi_crossed_sma_up:
                signal_long.append('1')
        if not price_crossed_ema20_up:
            price_crossed_ema20_up = row['price_crossing_ema20_up']
            if price_crossed_ema20_up:
                signal_long.append('2')
        if not ema5_crossed_ema20_up:
            ema5_crossed_ema20_up = row['ema5_crossing_ema20_up']
            if ema5_crossed_ema20_up:
                signal_long.append('3')

        signal_short = []
        if not rsi_crossed_sma_down:
            rsi_crossed_sma_down = row['rsi_crossing_sma_down']
            if rsi_crossed_sma_down:
                signal_short.append('1')
        if not price_crossed_ema20_down:
            price_crossed_ema20_down = row['price_crossing_ema20_down']
            if price_crossed_ema20_down:
                signal_short.append('2')
        if not ema5_crossed_ema20_down:
            ema5_crossed_ema20_down = row['ema5_crossing_ema20_down']
            if ema5_crossed_ema20_down:
                signal_short.append('3')

        if '1' in signal_short or '3' in signal_short:
            rsi_crossed_sma_up = False
            price_crossed_ema20_up = False
            ema5_crossed_ema20_up = False
        if '1' in signal_long or '3' in signal_long:
            rsi_crossed_sma_down = False
            price_crossed_ema20_down = False
            ema5_crossed_ema20_down = False

        if rsi_crossed_sma_up and price_crossed_ema20_up and ema5_crossed_ema20_up:
            signal_long.append('L')
            rsi_crossed_sma_up = False
            price_crossed_ema20_up = False
            ema5_crossed_ema20_up = False
        if rsi_crossed_sma_down and price_crossed_ema20_down and ema5_crossed_ema20_down:
            signal_short.append('S')
            rsi_crossed_sma_down = False
            price_crossed_ema20_down = False
            ema5_crossed_ema20_down = False

        if len(signal_long) > 0:
            df_195m.loc[index, 'signal_long'] = '<br>'.join(signal_long)
        if len(signal_short) > 0:
            df_195m.loc[index, 'signal_short'] = '<br>'.join(signal_short)

    #
    # fix timezone
    #
    # df_195m['Datetime'] = df_195m['Datetime'].apply(lambda x: x.tz_convert(tz='Europe/Berlin'))

    df_195m.attrs['stock'] = stock

    return df_195m.tail(30).reset_index(drop=True)


def generate_plot(stock, df_195m):
    hover_texts = []
    for i in range(len(df_195m.Close)):
        hover_texts.append(
            df_195m.Datetime[i].strftime('%Y-%m-%d %H:%M') +
            '<br><br>Open: ' + str(round(df_195m.Open[i], 2)) + '<br>High: ' + str(round(df_195m.High[i], 2)) +
            '<br>Low: ' + str(round(df_195m.Low[i], 2)) + '<br>Close: ' + str(round(df_195m.Close[i], 2))
        )

    fig = make_subplots(rows=4, cols=1, shared_xaxes=True, vertical_spacing=0.02,
                        specs=[[{"rowspan": 2}], [None], [{}], [{}]])
    fig.add_trace(
        go.Candlestick(
            name='price',
            x=df_195m.index,
            open=df_195m['Open'],
            high=df_195m['High'],
            low=df_195m['Low'],
            close=df_195m['Close'],
            hoverinfo='text',
            text=hover_texts,
        ),
        row=1, col=1
    )
    fig.add_trace(
        go.Scatter(name='EMA5', x=df_195m.index, y=df_195m['EMA5'], mode='lines', line_color='rgba(24,72,204,0.6)'),
        row=1, col=1
    )
    fig.add_trace(
        go.Scatter(name='EMA20', x=df_195m.index, y=df_195m['EMA20'], mode='lines', line_color='rgba(0,0,0,0.6)'),
        row=1, col=1
    )
    fig.add_trace(
        go.Scatter(name='RSI', x=df_195m.index, y=df_195m['rsi'], mode='lines', line_color='rgba(103,58,183,0.7)'),
        row=3, col=1
    )
    fig.add_trace(
        go.Scatter(name='RSI SMA', x=df_195m.index, y=df_195m['rsi_sma'], mode='lines', line_color='rgba(0,0,0,0.9)'),
        row=3, col=1
    )

    df_195m_long = df_195m[df_195m['signal_long'].notna()].copy()
    df_195m_long['y'] = 'signals'
    fig.add_trace(
        go.Scatter(name='long', x=df_195m_long.index, y=df_195m_long['y'], text=df_195m_long['signal_long'],
                   mode='markers+text', line_color='rgba(0,200,0,1)', marker_symbol='triangle-up', marker_size=20,
                   textposition='bottom center'),
        row=4, col=1
    )

    df_195m_long = df_195m[df_195m['signal_short'].notna()].copy()
    df_195m_long['y'] = 'signals'
    fig.add_trace(
        go.Scatter(name='short', x=df_195m_long.index, y=df_195m_long['y'], text=df_195m_long['signal_short'],
                   mode='markers+text', line_color='rgba(255,0,0,1)', marker_symbol='triangle-down', marker_size=20,
                   textposition='bottom center'),
        row=4, col=1
    )

    fig.update_layout(xaxis=dict(rangeslider=dict(visible=False)))
    fig.update_layout(hovermode="x unified")
    fig.update_layout(title_text=stock)
    fig.update_traces(xaxis='x1')

    return fig


def download_data(stocks, end):
    #
    # download
    #

    session = requests_cache.CachedSession('yfinance.cache')

    # fetch previous 60..<start> days historical stock data from Yahoo Finance API
    start_15m = datetime.today().replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=58)
    end_15m = end
    print(f'Requesting 15m intervals, start={start_15m}, end: {end_15m}...')
    dfs_15m = yf.download(
        tickers=stocks,
        interval="15m",
        start=start_15m,  # api allows max 60 days for '15m'
        end=end_15m,
        group_by='ticker',
        session=session,
        threads=False  # threads do not work with session
    )

    # fetch previous 140..60 days historical stock data from Yahoo Finance API
    start_1d = start_15m - timedelta(days=140)
    end_1d = start_15m
    print(f'Requesting 1d intervals, start={start_1d}, end: {end_1d}...')
    dfs_old_1d = yf.download(
        tickers=stocks,
        interval="1d",
        start=start_1d,  # api allows max 730 days for '1d'
        end=end_1d,
        group_by='ticker',
        session=session,
        threads=False  # threads do not work with session
    )

    return dfs_old_1d, dfs_15m


def generate_html(dfs):
    dt_last_candle = dfs[-1]['Datetime'].iloc[-1]

    # signal in last value?
    dfs_long = [df for df in dfs if (df.signal_long.iloc[-1] and 'L' in df.signal_long.iloc[-1])]
    dfs_short = [df for df in dfs if (df.signal_short.iloc[-1] and 'S' in df.signal_short.iloc[-1])]
    # filter by current signals
    dfs = dfs_long + dfs_short

    folder = f"docs/{dt_last_candle.strftime('%Y-%m-%dT%H:%M')}"
    print(f'Generating into folder: {folder}...')
    os.makedirs(folder)

    for index, df_195m in enumerate(dfs):
        stock = df_195m.attrs['stock']
        with open(f'{folder}/{stock}.html', 'w') as f:
            fig = generate_plot(stock, df_195m)
            f.write(fig.to_html(include_plotlyjs='cdn'))

    weekdays = ['Montag', 'Dienstag', 'Mittwoch', 'Donnerstag', 'Freitag', 'Samstag', 'Sonntag']

    raw_data = {
        'timestamp': dt_last_candle,
        'title': weekdays[dt_last_candle.weekday()] + ', ' + dt_last_candle.strftime('%d.%m.%Y %H:%M'),
        'long_signals': [df.attrs['stock'] for df in dfs_long],
        'short_signals': [df.attrs['stock'] for df in dfs_short],
    }
    with open(f'{folder}/data.json', 'w') as f:
        d = raw_data.copy()
        d['timestamp'] = d['timestamp'].isoformat()
        json.dump(d, f, indent=2)

    with open(f'{folder}/index.html', 'w') as f:
        env = Environment(loader=FileSystemLoader("templates"), autoescape=select_autoescape())
        template = env.get_template('report.html.jinja')
        html = template.render(raw_data)
        f.write(html)

    # data.json
    timestamps = [f for f in os.listdir("docs") if os.path.isdir(f"docs/{f}")]
    timestamps.sort(reverse=True)

    reports = []
    for timestamp in timestamps:
        try:
            with open(f'docs/{timestamp}/data.json', 'r') as f:
                d = json.load(f)
                reports.append({
                    'title': f"{d['title']}",
                    'link': f'{timestamp}/index.html',
                    'summary': f"{len(d['long_signals'])}x Long, {len(d['short_signals'])}x Short"
                })
        except:
            timestamp_parsed = datetime.fromisoformat(timestamp)
            reports.append({
                'title': weekdays[timestamp_parsed.weekday()] + ', ' + timestamp_parsed.strftime('%d.%m.%Y %H:%M'),
                'link': f'{timestamp}/index.html',
                'summary': ''
            })

    with open(f'docs/index.html', 'w') as f:
        env = Environment(loader=FileSystemLoader("templates"), autoescape=select_autoescape())
        template = env.get_template('index.html.jinja')
        html = template.render(reports=reports)
        f.write(html)


def generate(stocks, end):
    dfs_old_1d, dfs_15m = download_data(stocks, end)
    dfs = [generate_data(stock, dfs_old_1d[stock], dfs_15m[stock]) for stock in stocks]
    generate_html(dfs)
