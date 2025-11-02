import os
from datetime import datetime

import plotly.graph_objects as go
from jinja2 import Environment, FileSystemLoader, select_autoescape
from pandas import DataFrame
from plotly.subplots import make_subplots

import fileio

WEEKDAYS = ['Montag', 'Dienstag', 'Mittwoch', 'Donnerstag', 'Freitag', 'Samstag', 'Sonntag']


def write_index_html():
    folders = [f for f in os.listdir("docs") if os.path.isdir(f"docs/{f}")]
    folders.sort(reverse=True)

    reports = []
    for folder in folders:
        metadata = fileio.dict_read(f'docs/{folder}/metadata.json')
        metadata['folder'] = folder
        metadata['title'] = WEEKDAYS[metadata["timestamp_start"].weekday()] + ', ' + metadata[
            "timestamp_start"].strftime('%d.%m.%Y %H:%M')
        reports.append(metadata)

    with open(f'docs/index.html', 'w', encoding="utf-8") as f:
        env = Environment(loader=FileSystemLoader("templates"), autoescape=select_autoescape())
        template = env.get_template('index.html.jinja')
        html = template.render(
            reports=reports,
            datetime=datetime
        )
        f.write(html)


def write_report_html(metadata: dict, folder: str):
    metadata = metadata.copy()
    metadata['title'] = WEEKDAYS[metadata["timestamp_start"].weekday()] + ', ' + metadata["timestamp_start"].strftime(
        '%d.%m.%Y %H:%M')

    with open(f'{folder}/index.html', 'w', encoding="utf-8") as f:
        env = Environment(loader=FileSystemLoader("templates"), autoescape=select_autoescape())
        template = env.get_template('report.html.jinja')
        html = template.render(metadata)
        f.write(html)


def write_chart_html(symbol: str, df: DataFrame, path: str):
    with open(path, 'w', encoding="utf-8") as f:
        fig = generate_plot(symbol, df)
        config = {
            'displayModeBar': False,  # Toolbar ausblenden
            'scrollZoom': False,  # kein Scroll-Zoom
            'doubleClick': False,  # kein Reset/Zoom per Doppelklick
        }
        f.write(fig.to_html(include_plotlyjs='cdn', config=config))


def generate_plot(symbol: str, df: DataFrame) -> go.Figure:
    fig = make_subplots(rows=4, cols=1, shared_xaxes=True, vertical_spacing=0.02,
                        specs=[[{"rowspan": 2}], [None], [{}], [{}]])
    fig.add_trace(
        go.Candlestick(
            name='candle',
            x=df.index,
            open=df['open'],
            high=df['high'],
            low=df['low'],
            close=df['close'],
        ),
        row=1, col=1
    )
    fig.add_trace(
        go.Scatter(name='EMA5', x=df.index, y=df['ema5'], mode='lines', line_color='rgba(24,72,204,0.6)'),
        row=1, col=1
    )
    fig.add_trace(
        go.Scatter(name='EMA20', x=df.index, y=df['ema20'], mode='lines', line_color='rgba(0,0,0,0.6)'),
        row=1, col=1
    )
    fig.add_trace(
        go.Scatter(name='RSI', x=df.index, y=df['rsi'], mode='lines', line_color='rgba(103,58,183,0.7)'),
        row=3, col=1
    )
    fig.add_trace(
        go.Scatter(name='RSI SMA', x=df.index, y=df['rsi_sma'], mode='lines', line_color='rgba(0,0,0,0.9)'),
        row=3, col=1
    )

    df_long = df[df['signal_long'] != ""].copy()
    df_long['y'] = 'signals'
    fig.add_trace(
        go.Scatter(name='long', x=df_long.index, y=df_long['y'], text=df_long['signal_long'],
                   mode='markers+text', line_color='rgba(0,200,0,1)', marker_symbol='triangle-up', marker_size=20,
                   textposition='bottom center'),
        row=4, col=1
    )

    df_short = df[df['signal_short'] != ""].copy()
    df_short['y'] = 'signals'
    fig.add_trace(
        go.Scatter(name='short', x=df_short.index, y=df_short['y'], text=df_short['signal_short'],
                   mode='markers+text', line_color='rgba(255,0,0,1)', marker_symbol='triangle-down', marker_size=20,
                   textposition='bottom center'),
        row=4, col=1
    )

    fig.update_layout(
        xaxis=dict(
            tickmode='array',
            tickvals=df.index,
            ticktext=df['date'].dt.strftime('%Y-%m-%d %H:%M'),
            rangeslider=dict(visible=False)
        ),
        hovermode='x unified',
        dragmode=False,
        title_text=symbol
    )
    fig.update_traces(xaxis='x1')

    return fig
