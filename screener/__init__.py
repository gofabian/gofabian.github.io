from screener.download import download_195m
from screener.finance import generate_analysis
from screener.htmlgen import update_website


def generate(stocks, end):
    dfs_195m = download_195m(stocks, end)
    dfs = [generate_analysis(df_195m) for df_195m in dfs_195m]
    update_website(dfs)
