# Stock Screener

Scans charts of S&P 500 stocks for short and long signals according to PJM training.

## Generated website

<img src="ui1.jpeg" width=300> <img src="ui2.jpeg" width=300> <img src="ui3.jpeg" width=300>


## Structure

`/docs/`: generated website

`/templates/`: html templates

`/build.py`: build script

`/finance.py`: generation logic

`/main.py`: demo runner

`/stocks.py`: list of S&P stocks to be scanned


## todos

- Requests an API innerhalb CI reduzieren
- tickers anhand Marktkapitalisierung reduzieren
- 