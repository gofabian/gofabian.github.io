def generate_analysis(df_195m):
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

    return df_195m.tail(30).reset_index(drop=True)

