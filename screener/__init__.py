from screener.download import download_195m
from screener.finance import generate_analysis
from screener.htmlgen import update_website
from datetime import timedelta


def generate(stocks, end):
    start = end - timedelta(days=200)
    dfs_195m = download_195m(stocks, start, end)
    dfs = [generate_analysis(df_195m) for df_195m in dfs_195m]
    update_website(dfs)
