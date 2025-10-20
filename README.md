# Stock Screener

Scans charts of S&P 500 stocks for short and long signals according to PJM training.

## Market hours

    09:30 - 16:00 -04:00 USA
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

pro symbol

- generate(from, until)
- duration=100D + days(until-from)/7*5
- req_historical_data (end_datetime=until, duration="200 D" + days(until-from)/7*5)
- Indikatoren generieren
- Signale für df.tail(-180)
- L/S suchen in from..until
- an entsprechendem Ort chart.html/metadata.json/data.json exportieren
- report.html neu generieren
- index.html neu generieren
- in git hochladen

Progress auf Webseite anzeigen

- grün: Generierung abgeschlossen
- gelb: Generierung läuft
- rot: Fehler in Generierung

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
