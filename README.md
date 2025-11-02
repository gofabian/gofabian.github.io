# Stock Screener

Scans charts of S&P 500 stocks for short and long signals according to PJM training.

## Market hours

    09:30 - 16:00 -04:00 Eastern time summer
    09:30 - 16:00 -05:00 Eastern time winter
    15:30 - 22:00 +02:00 Germany summer
    14:30 - 21:00 +01:00 Germany winter

195 min:

    09:30 - 12:45
    12:45 - 16:00

## Development

Look at Github actions workflow to find out how to start IB gateway and the Python script locally.

Either run IB gateway application directly or the docker container (see ./ibgateway.sh).

## IB Gateway

https://github.com/gnzsnz/ib-gateway-docker

## todos

Progress-Timestamp separieren oder gar nicht?

UI

- landing page
    - links to 10 latest timestamp pages
    - link to months page
    - link to symbols page
- timestamp page
    - all symbols at timestamp with L or S signal -> link to chart + trading view
- chart page
    - chart at timestamp of symbol
- months page
    - links to each month
- month page
    - links to all timestamp pages of this month
- symbols page
    - links to each symbol page
- symbol page
    - links to all charts where symbol had L or S signals -> link to chart + trading view
