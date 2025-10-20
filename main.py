from logic import export_charts
from schedule import get_next_timestamps, write_timestamp

# s&p500 MK>70B
symbols = ["NVDA", "MSFT", "AAPL", "GOOG", "AMZN", "META", "AVGO", "TSLA", "BRK B", "ORCL", "JPM", "WMT",
           "LLY", "V", "NFLX", "MA", "XOM", "JNJ", "PLTR", "COST", "ABBV", "HD", "BAC", "AMD", "PG", "UNH", "GE", "CVX",
           "KO", "CSCO", "IBM", "TMUS", "WFC", "PM", "MS", "GS", "CRM", "CAT", "ABT", "AXP", "MU", "MCD", "LIN", "MRK",
           "RTX", "PEP", "APP", "DIS", "TMO", "UBER", "BX", "NOW", "BLK", "ANET", "T", "INTU", "C", "GEV", "AMAT",
           "QCOM", "INTC", "LRCX", "NEE", "BKNG", "SCHW", "VZ", "BA", "ACN", "TXN", "AMGN", "TJX", "ISRG", "APH", "DHR",
           "GILD", "SPGI", "ETN", "PANW", "ADBE", "BSX", "PFE", "SYK", "PGR", "KLAC", "UNP", "COF", "LOW", "HON",
           "CRWD", "HOOD", "MDT", "IBKR", "CEG", "DE", "LMT", "DASH", "ADI", "ADP", "CB", "COP", "MO", "CMCSA", "SO",
           "KKR", "VRTX", "DELL", "MMC", "NKE", "CVS", "NEM", "DUK", "CME", "HCA", "MCK", "TT", "PH", "COIN", "SBUX",
           "ICE", "CDNS", "GD", "BMY", "NOC", "WM", "ORLY", "MCO", "SNPS", "RCL", "SHW", "MMM", "MDLZ", "ELV", "CI",
           "ECL", "HWM", "WMB", "AJG", "AON", "MSI", "CTAS", "BK", "ABNB", "PNC", "GLW", "TDG", "EMR", "USB", "MAR",
           "ITW", "VST", "NSC", "UPS", "APO"]
# symbols = ["HD"]

timestamps = get_next_timestamps()
for timestamp in timestamps:
    # todo log
    print(timestamp.isoformat())

for timestamp in timestamps:
    export_charts(symbols, timestamp)

if len(timestamps) > 0:
    write_timestamp(timestamps[-1])
