from datetime import timedelta

from screener.cache import download_195m
from screener.finance import generate_analysis
from screener.htmlgen import update_website
from screener.progress import Progress


def generate(stocks, end):
    start = end - timedelta(days=200)

    print(f'Stocks: {", ".join(stocks)}\n')
    print(f'Start: {start}')
    print(f'End: {end}\n')

    progress_download = Progress('Download', stocks)
    dfs_195m = [progress_download.next(lambda: download_195m(stock, start, end)) for stock in stocks]

    progress_analysis = Progress('Analysis', stocks)
    dfs = [progress_analysis.next(lambda: generate_analysis(df_195m)) for df_195m in dfs_195m]

    update_website(dfs)
