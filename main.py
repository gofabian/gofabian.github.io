import time
from datetime import datetime, timedelta

import data
import schedule
import sector
import website
from log import log


SYMBOLS_SP500 = [
    "AAPL","MSFT","NVDA","GOOG","GOOGL","AMZN","META","TSLA","AVGO","LLY",
    "BRK B","WMT","JPM","V","MU","JNJ","AMD","XOM","MA","ABBV",
    "COST","KO","CVX","PG","PLTR","CSCO","HD","MRK","BAC","GE",
    "ORCL","UNH","PANW","PM","INTC","RTX","MS","AMGN","TMO","CAT",
    "NFLX","TXN","WFC","LIN","AMAT","GS","IBM","LRCX","GILD","CRWD",
    "DIS","AXP","ANET","MCD","VZ","PEP","GEV","C","ABT","DELL",
    "BLK","WELL","NEE","APH","QCOM","UNP","TMUS","DE","KLAC","CRM",
    "PFE","SCHW","TJX","DHR","COP","ADI","T","ISRG","BX","CB",
    "VRTX","ACN","LMT","PGR","UBER","SPGI","LOW","BA","MO","IBKR",
    "SYK","BMY","APP","ADP","MCK","SBUX","PLD","ETN","MDT","PH",

    "MRVL","CME","BKNG","SO","COF","STX","MAR","NEM","CVS","MRSH",
    "DUK","HCA","REGN","ABNB","WDC","ICE","FTNT","BNY","WM","MMM",
    "GD","EQIX","NOW","UPS","CSX","MPC","PSX","CMCSA","USB","ADBE",
    "CTAS","VLO","MRNA","MSI","TT","PNC","SHW","ECL","EMR","GLW",
    "MDLZ","AMT","PWR","ELV","HWM","KKR","MCO","RCL","TRV","MNST",
    "CEG","WMB","SNDK","JCI","HLT","ITW","CDNS","CL","NOC","ORLY",
    "TGT","SNPS","RSG","EOG","SPG","AJG","CVNA","AON","NSC","FDX",
    "INTU","DASH","CI","SLB","APO","HON","GM","ROST","KMI","APD",
    "AEP","FCX","COR","KMB","ALL","VRT","GWW","CAH","BSX","CRH",
    "AFL","PSA","DLR","URI","MET","TDG","TRGP","EW","FAST","NXPI",

    "TEL","BDX","D","NDAQ","HOOD","CMI","TFC","MPWR","O","PCAR",
    "DDOG","IDXX","NUE","AZO","DAL","OKE","NKE","GRMN","OXY","HPE",
    "XEL","AME","SRE","ADSK","ETR","EBAY","VMRK","A","FANG","HONA",
    "FERG","LHX","HUM","KDP","F","DVN","EXC","WAB","PYPL","ROP",
    "CMG","VTR","VYLR","FITB","XYZ","BKR","MSCI","KEYS","BE","YUM",
    "ED","WAT","CARR","STT","VEEV","AMP","WDAY","LITE","LYV","AIG",
    "TTWO","PAYX","ROK","DHI","PRU","IQV","KR","VST","SYY","CBRE",
    "EL","WEC","BIIB","COHR","FIX","MLM","GEHC","CCL","PEG","VMC",
    "HIG","CBOE","HSY","TKO","ACGL","ODFL","CCI","FOX","FOXA","OKTA",
    "RMD","CIEN","UAL","ZTS","EXR","MTD","SKYD","TER","WTW","NTAP",

    "EQT","CNC","FISV","IR","AEE","ADM","DXCM","PCG","P","KHC",
    "RJF","IRM","MTB","MCHP","STLD","CPRT","DG","AWK","NTRS","ILMN",
    "LH","OTIS","HBAN","ARES","CINF","ATO","WRB","VLTO","DGX","CPAY",
    "TDY","VRSN","DTE","DLTR","EXPE","CTSH","HPQ","AXON","TWLO","VICI",
    "FE","EME","PPG","ES","ULTA","DRI","COIN","DOV","CHD","CNP",
    "PPL","VRSK","HAL","BRO","WST","CFG","CASY","CHTR","EXPD","GPN",
    "STE","TPR","INCY","ECHO","LVS","WSM","PHM","OMC","FLEX","EIX",
    "ON","STZ","RF","RL","JBL","PFG","VTRS","Q","HUBB","CMS",
    "L","LUV","XYL","TROW","TSN","PKG","EFX","SW","CDW","NI",
    "IFF","DOW","BBY","KEY","SYF","PTC","JBHT","BR","AMCR","TSCO",

    "ZBH","LEN","EVRG","DD","EXE","FTV","GIS","NRG","SWKS","LNT",
    "SNA","LYB","ROL","SBAC","ESS","TPL","FFIV","GEN","NDSN","FDXF",
    "RDDT","BALL","KIM","CF","BEN","GPC","HST","IP","J","BG",
    "CHRW","RVTY","TYL","MAS","IEX","SWK","ALLE","EG","INVH","AIZ",
    "LDOS","NVR","CRL","FSLR","HAS","APA","SMCI","FICO","ZBRA","WY",
    "SOLV","DOC","NWS","NWSA","AVY","FIS","BAX","SJM","REG","BF B",
    "MAA","TXT","CSGP","MKC","CLX","CPT","ERIE","AKAM","GDDY","HRL",
    "JKHY","TRMB","PNW","LULU","IVZ","GNRC","LII","DPZ","COO","HII",
    "GL","IT","ALGN","PNR","UDR","FDS","TECH","DECK","UHS","AES",
    "DVA","BXP","PODD","FRT","HSIC","ALB","AOS","WYNN","MGM","NCLH",

    "APTV","ARE","MOS"
]


def cicd(symbols: list[str]):
    request_start = schedule.get_start_timestamp()
    request_end = schedule.get_end_timestamp()
    log(f"start={request_start.isoformat()} end={request_end.isoformat()}")

    # past candles?
    if request_start < request_end:
        update(symbols, request_start, request_end)
        return

    # next candle soon?
    now = datetime.now(tz=schedule.TZ)
    request_end = schedule.get_next_timestamp(now, schedule.SCHEDULE_TIMES)
    if request_end - timedelta(minutes=15) > now:
        log("Cancelled.")
        return

    # next candle soon
    while True:
        now = datetime.now(tz=schedule.TZ)
        log(f'Waiting... now={now} until={request_end.isoformat()}')
        if now >= request_end:
            break
        time.sleep(60)

    # next candle now
    log(f"start={request_start.isoformat()} end={request_end.isoformat()}")
    request_start = schedule.get_previous_timestamp(request_end, schedule.CANDLE_START_TIMES)
    update(symbols, request_start, request_end)


def update(symbols: list[str], request_start: datetime, request_end: datetime):
    symbols_update = symbols + sector.SECTOR_SYMBOLS + ["SPY"]
    data.update_data(symbols_update, request_end)
    website.update_website(symbols, request_start, request_end)


cicd(SYMBOLS)

#start = datetime.fromisoformat("2025-01-01T09:30:00-05:00")
#end = schedule.get_end_timestamp() #datetime.fromisoformat("2026-10-07T16:00:00-04:00")
#update(SYMBOLS_SP500, start, end)

#start = datetime.fromisoformat("2025-01-01T09:30:00-05:00")
#end = datetime.fromisoformat("2026-11-25T16:00:00-05:00")

#website.write_timestamp_pages(SYMBOLS_SP500, start, end)
