import pandas as pd


def analyze(df: pd.DataFrame):
    df['ema5'] = ema(df, 5)
    df['ema20'] = ema(df, 20)
    df['rsi'] = rsi(df)
    df['rsi_sma'] = df['rsi'].rolling(14).mean()


def ema(df, n) -> pd.Series:
    return df['close'].ewm(span=n, adjust=False).mean()


def rsi(df) -> pd.Series:
    #
    # Calculate RSI (>=200 Datenpunkte notwendig)
    #

    change = df['close'].diff()
    gain = change.mask(change < 0, 0.0)
    loss = -change.mask(change > 0, -0.0)

    def rma(column, n):
        return column.ewm(alpha=1 / n, min_periods=n, adjust=False).mean()

    avg_gain = rma(gain, 14)
    avg_loss = rma(loss, 14)
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))
