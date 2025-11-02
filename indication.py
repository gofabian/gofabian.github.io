from pandas import DataFrame, Series


def analyze(df: DataFrame) -> DataFrame:
    df = df.copy()
    df['ema5'] = ema(df['close'], 5)
    df['ema20'] = ema(df['close'], 20)
    df['rsi'] = rsi(df['close'])
    df['rsi_sma'] = df['rsi'].rolling(14).mean()
    df['ema30_high'] = ema(df['high'], 30)
    df['ema30_low'] = ema(df['low'], 30)
    df['hl_band'] = hl_band(df)
    return df


def ema(column: Series, n: int) -> Series:
    return column.ewm(span=n, adjust=False).mean()


def rsi(column: Series) -> Series:
    #
    # Calculate RSI (>=200 Datenpunkte notwendig)
    #

    change = column.diff()
    gain = change.mask(change < 0, 0.0)
    loss = -change.mask(change > 0, -0.0)

    def rma(col, n):
        return col.ewm(alpha=1 / n, min_periods=n, adjust=False).mean()

    avg_gain = rma(gain, 14)
    avg_loss = rma(loss, 14)
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))


def hl_band(df: DataFrame) -> Series:
    def get_trend(row: Series) -> str:
        if row['close'] > row['ema30_high']:
            return 'up'
        elif row['close'] < row['ema30_low']:
            return 'down'
        else:
            return 'sideways'

    return df.apply(get_trend, axis=1)
