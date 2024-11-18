import json
import os

import plotly.graph_objects as go
from jinja2 import Environment, select_autoescape, FileSystemLoader
from plotly.subplots import make_subplots


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


def update_website(dfs):
    write_record_html(dfs)
    write_index_html()


def write_record_html(dfs):
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


def write_index_html():
    timestamps = [f for f in os.listdir("docs") if os.path.isdir(f"docs/{f}")]
    timestamps.sort(reverse=True)

    reports = []
    for timestamp in timestamps:
        with open(f'docs/{timestamp}/data.json', 'r') as f:
            d = json.load(f)
            reports.append({
                'title': f"{d['title']}",
                'link': f'{timestamp}/index.html',
                'summary': f"{len(d['long_signals'])}x Long, {len(d['short_signals'])}x Short"
            })

    with open(f'docs/index.html', 'w') as f:
        env = Environment(loader=FileSystemLoader("templates"), autoescape=select_autoescape())
        template = env.get_template('index.html.jinja')
        html = template.render(reports=reports)
        f.write(html)
