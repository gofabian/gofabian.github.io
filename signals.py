#
# Find signals
#
import pandas as pd


def find_signals(df: pd.DataFrame):
    df_prev = df.shift()

    # long
    rsi_crossing_sma_up = (df['rsi'] > df['rsi_sma']) & (df_prev['rsi'] <= df_prev['rsi_sma'])
    close_crossing_ema20_up = (df['close'] > df['ema20']) & (df_prev['close'] <= df_prev['ema20'])
    ema5_crossing_ema20_up = (df['ema5'] > df['ema20']) & (df_prev['ema5'] <= df_prev['ema20'])

    # short
    rsi_crossing_sma_down = (df['rsi'] < df['rsi_sma']) & (df_prev['rsi'] >= df_prev['rsi_sma'])
    close_crossing_ema20_down = (df['close'] < df['ema20']) & (df_prev['close'] >= df_prev['ema20'])
    ema5_crossing_ema20_down = (df['ema5'] < df['ema20']) & (df_prev['ema5'] >= df_prev['ema20'])

    # Neue Spalten initialisieren
    df['signal_long'] = None
    df['signal_short'] = None

    # Finde Signale
    rsi_crossed_sma_up = False
    price_crossed_ema20_up = False
    ema5_crossed_ema20_up = False
    rsi_crossed_sma_down = False
    price_crossed_ema20_down = False
    ema5_crossed_ema20_down = False

    # todo: ohne Schleife möglich? Effizienter über Data-Frame-Funktionen
    # todo: Ergebnis mit generiertem Chart und TradingView-Vergleich prüfen

    for index in df.index:
        signal_long = []
        if not rsi_crossed_sma_up:
            rsi_crossed_sma_up = rsi_crossing_sma_up.loc[index]
            if rsi_crossed_sma_up:
                signal_long.append('1')
        if not price_crossed_ema20_up:
            price_crossed_ema20_up = close_crossing_ema20_up.loc[index]
            if price_crossed_ema20_up:
                signal_long.append('2')
        if not ema5_crossed_ema20_up:
            ema5_crossed_ema20_up = ema5_crossing_ema20_up.loc[index]
            if ema5_crossed_ema20_up:
                signal_long.append('3')

        signal_short = []
        if not rsi_crossed_sma_down:
            rsi_crossed_sma_down = rsi_crossing_sma_down.loc[index]
            if rsi_crossed_sma_down:
                signal_short.append('1')
        if not price_crossed_ema20_down:
            price_crossed_ema20_down = close_crossing_ema20_down.loc[index]
            if price_crossed_ema20_down:
                signal_short.append('2')
        if not ema5_crossed_ema20_down:
            ema5_crossed_ema20_down = ema5_crossing_ema20_down.loc[index]
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
            df.loc[index, 'signal_long'] = '<br>'.join(signal_long)
        if len(signal_short) > 0:
            df.loc[index, 'signal_short'] = '<br>'.join(signal_short)
