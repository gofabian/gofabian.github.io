import csv

GICS_TO_ETF = {
    "Information Technology": "XLK",
    "Health Care": "XLV",
    "Financials": "XLF",
    "Consumer Discretionary": "XLY",
    "Communication Services": "XLC",
    "Industrials": "XLI",
    "Energy": "XLE",
    "Consumer Staples": "XLP",
    "Utilities": "XLU",
    "Materials": "XLB",
    "Real Estate": "XLRE",
}

SECTOR_SYMBOLS = list(set(GICS_TO_ETF.values()))


# used to generate the constant
def _generate_stock_sector_mapping() -> dict[str, str]:
    stocks_dict = {}
    unknown_sectors = []

    # https://raw.githubusercontent.com/datasets/s-and-p-500-companies/master/data/constituents.csv
    with open("constituents.csv", newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            symbol = row['Symbol'].replace(".", " ").strip()
            gics_sector = row['GICS Sector'].strip()
            sector_etf = GICS_TO_ETF.get(gics_sector, None)
            if sector_etf is None:
                unknown_sectors.append(gics_sector)
            stocks_dict[symbol] = sector_etf

    if len(unknown_sectors) > 0:
        raise ValueError("Unknown sectors", unknown_sectors)

    return stocks_dict


STOCK_SECTOR_MAPPING = {
    'MMM': 'XLI', 'AOS': 'XLI', 'ABT': 'XLV', 'ABBV': 'XLV', 'ACN': 'XLK', 'ADBE': 'XLK', 'AMD': 'XLK', 'AES': 'XLU',
    'AFL': 'XLF', 'A': 'XLV', 'APD': 'XLB', 'ABNB': 'XLY', 'AKAM': 'XLK', 'ALB': 'XLB', 'ARE': 'XLRE', 'ALGN': 'XLV',
    'ALLE': 'XLI', 'LNT': 'XLU', 'ALL': 'XLF', 'GOOGL': 'XLC', 'GOOG': 'XLC', 'MO': 'XLP', 'AMZN': 'XLY', 'AMCR': 'XLB',
    'AEE': 'XLU', 'AEP': 'XLU', 'AXP': 'XLF', 'AIG': 'XLF', 'AMT': 'XLRE', 'AWK': 'XLU', 'AMP': 'XLF', 'AME': 'XLI',
    'AMGN': 'XLV', 'APH': 'XLK', 'ADI': 'XLK', 'AON': 'XLF', 'APA': 'XLE', 'APO': 'XLF', 'AAPL': 'XLK', 'AMAT': 'XLK',
    'APTV': 'XLY', 'ACGL': 'XLF', 'ADM': 'XLP', 'ANET': 'XLK', 'AJG': 'XLF', 'AIZ': 'XLF', 'T': 'XLC', 'ATO': 'XLU',
    'ADSK': 'XLK', 'ADP': 'XLI', 'AZO': 'XLY', 'AVB': 'XLRE', 'AVY': 'XLB', 'AXON': 'XLI', 'BKR': 'XLE', 'BALL': 'XLB',
    'BAC': 'XLF', 'BAX': 'XLV', 'BDX': 'XLV', 'BRK B': 'XLF', 'BBY': 'XLY', 'TECH': 'XLV', 'BIIB': 'XLV', 'BLK': 'XLF',
    'BX': 'XLF', 'XYZ': 'XLF', 'BK': 'XLF', 'BA': 'XLI', 'BKNG': 'XLY', 'BSX': 'XLV', 'BMY': 'XLV', 'AVGO': 'XLK',
    'BR': 'XLI', 'BRO': 'XLF', 'BF B': 'XLP', 'BLDR': 'XLI', 'BG': 'XLP', 'BXP': 'XLRE', 'CHRW': 'XLI', 'CDNS': 'XLK',
    'CZR': 'XLY', 'CPT': 'XLRE', 'CPB': 'XLP', 'COF': 'XLF', 'CAH': 'XLV', 'KMX': 'XLY', 'CCL': 'XLY', 'CARR': 'XLI',
    'CAT': 'XLI', 'CBOE': 'XLF', 'CBRE': 'XLRE', 'CDW': 'XLK', 'COR': 'XLV', 'CNC': 'XLV', 'CNP': 'XLU', 'CF': 'XLB',
    'CRL': 'XLV', 'SCHW': 'XLF', 'CHTR': 'XLC', 'CVX': 'XLE', 'CMG': 'XLY', 'CB': 'XLF', 'CHD': 'XLP', 'CI': 'XLV',
    'CINF': 'XLF', 'CTAS': 'XLI', 'CSCO': 'XLK', 'C': 'XLF', 'CFG': 'XLF', 'CLX': 'XLP', 'CME': 'XLF', 'CMS': 'XLU',
    'KO': 'XLP', 'CTSH': 'XLK', 'COIN': 'XLF', 'CL': 'XLP', 'CMCSA': 'XLC', 'CAG': 'XLP', 'COP': 'XLE', 'ED': 'XLU',
    'STZ': 'XLP', 'CEG': 'XLU', 'COO': 'XLV', 'CPRT': 'XLI', 'GLW': 'XLK', 'CPAY': 'XLF', 'CTVA': 'XLB', 'CSGP': 'XLRE',
    'COST': 'XLP', 'CTRA': 'XLE', 'CRWD': 'XLK', 'CCI': 'XLRE', 'CSX': 'XLI', 'CMI': 'XLI', 'CVS': 'XLV', 'DHR': 'XLV',
    'DRI': 'XLY', 'DDOG': 'XLK', 'DVA': 'XLV', 'DAY': 'XLI', 'DECK': 'XLY', 'DE': 'XLI', 'DELL': 'XLK', 'DAL': 'XLI',
    'DVN': 'XLE', 'DXCM': 'XLV', 'FANG': 'XLE', 'DLR': 'XLRE', 'DG': 'XLP', 'DLTR': 'XLP', 'D': 'XLU', 'DPZ': 'XLY',
    'DASH': 'XLY', 'DOV': 'XLI', 'DOW': 'XLB', 'DHI': 'XLY', 'DTE': 'XLU', 'DUK': 'XLU', 'DD': 'XLB', 'EMN': 'XLB',
    'ETN': 'XLI', 'EBAY': 'XLY', 'ECL': 'XLB', 'EIX': 'XLU', 'EW': 'XLV', 'EA': 'XLC', 'ELV': 'XLV', 'EMR': 'XLI',
    'ENPH': 'XLK', 'ETR': 'XLU', 'EOG': 'XLE', 'EPAM': 'XLK', 'EQT': 'XLE', 'EFX': 'XLI', 'EQIX': 'XLRE', 'EQR': 'XLRE',
    'ERIE': 'XLF', 'ESS': 'XLRE', 'EL': 'XLP', 'EG': 'XLF', 'EVRG': 'XLU', 'ES': 'XLU', 'EXC': 'XLU', 'EXE': 'XLE',
    'EXPE': 'XLY', 'EXPD': 'XLI', 'EXR': 'XLRE', 'XOM': 'XLE', 'FFIV': 'XLK', 'FDS': 'XLF', 'FICO': 'XLK',
    'FAST': 'XLI', 'FRT': 'XLRE', 'FDX': 'XLI', 'FIS': 'XLF', 'FITB': 'XLF', 'FSLR': 'XLK', 'FE': 'XLU', 'FISV': 'XLF',
    'F': 'XLY', 'FTNT': 'XLK', 'FTV': 'XLI', 'FOXA': 'XLC', 'FOX': 'XLC', 'BEN': 'XLF', 'FCX': 'XLB', 'GRMN': 'XLY',
    'IT': 'XLK', 'GE': 'XLI', 'GEHC': 'XLV', 'GEV': 'XLI', 'GEN': 'XLK', 'GNRC': 'XLI', 'GD': 'XLI', 'GIS': 'XLP',
    'GM': 'XLY', 'GPC': 'XLY', 'GILD': 'XLV', 'GPN': 'XLF', 'GL': 'XLF', 'GDDY': 'XLK', 'GS': 'XLF', 'HAL': 'XLE',
    'HIG': 'XLF', 'HAS': 'XLY', 'HCA': 'XLV', 'DOC': 'XLRE', 'HSIC': 'XLV', 'HSY': 'XLP', 'HPE': 'XLK', 'HLT': 'XLY',
    'HOLX': 'XLV', 'HD': 'XLY', 'HON': 'XLI', 'HRL': 'XLP', 'HST': 'XLRE', 'HWM': 'XLI', 'HPQ': 'XLK', 'HUBB': 'XLI',
    'HUM': 'XLV', 'HBAN': 'XLF', 'HII': 'XLI', 'IBM': 'XLK', 'IEX': 'XLI', 'IDXX': 'XLV', 'ITW': 'XLI', 'INCY': 'XLV',
    'IR': 'XLI', 'PODD': 'XLV', 'INTC': 'XLK', 'ICE': 'XLF', 'IFF': 'XLB', 'IP': 'XLB', 'IPG': 'XLC', 'INTU': 'XLK',
    'ISRG': 'XLV', 'IVZ': 'XLF', 'INVH': 'XLRE', 'IQV': 'XLV', 'IRM': 'XLRE', 'JBHT': 'XLI', 'JBL': 'XLK',
    'JKHY': 'XLF', 'J': 'XLI', 'JNJ': 'XLV', 'JCI': 'XLI', 'JPM': 'XLF', 'K': 'XLP', 'KVUE': 'XLP', 'KDP': 'XLP',
    'KEY': 'XLF', 'KEYS': 'XLK', 'KMB': 'XLP', 'KIM': 'XLRE', 'KMI': 'XLE', 'KKR': 'XLF', 'KLAC': 'XLK', 'KHC': 'XLP',
    'KR': 'XLP', 'LHX': 'XLI', 'LH': 'XLV', 'LRCX': 'XLK', 'LW': 'XLP', 'LVS': 'XLY', 'LDOS': 'XLI', 'LEN': 'XLY',
    'LII': 'XLI', 'LLY': 'XLV', 'LIN': 'XLB', 'LYV': 'XLC', 'LKQ': 'XLY', 'LMT': 'XLI', 'L': 'XLF', 'LOW': 'XLY',
    'LULU': 'XLY', 'LYB': 'XLB', 'MTB': 'XLF', 'MPC': 'XLE', 'MKTX': 'XLF', 'MAR': 'XLY', 'MRSH': 'XLF', 'MLM': 'XLB',
    'MAS': 'XLI', 'MA': 'XLF', 'MTCH': 'XLC', 'MKC': 'XLP', 'MCD': 'XLY', 'MCK': 'XLV', 'MDT': 'XLV', 'MRK': 'XLV',
    'META': 'XLC', 'MET': 'XLF', 'MTD': 'XLV', 'MGM': 'XLY', 'MCHP': 'XLK', 'MU': 'XLK', 'MSFT': 'XLK', 'MAA': 'XLRE',
    'MRNA': 'XLV', 'MHK': 'XLY', 'MOH': 'XLV', 'TAP': 'XLP', 'MDLZ': 'XLP', 'MPWR': 'XLK', 'MNST': 'XLP', 'MCO': 'XLF',
    'MS': 'XLF', 'MOS': 'XLB', 'MSI': 'XLK', 'MSCI': 'XLF', 'NDAQ': 'XLF', 'NTAP': 'XLK', 'NFLX': 'XLC', 'NEM': 'XLB',
    'NWSA': 'XLC', 'NWS': 'XLC', 'NEE': 'XLU', 'NKE': 'XLY', 'NI': 'XLU', 'NDSN': 'XLI', 'NSC': 'XLI', 'NTRS': 'XLF',
    'NOC': 'XLI', 'NCLH': 'XLY', 'NRG': 'XLU', 'NUE': 'XLB', 'NVDA': 'XLK', 'NVR': 'XLY', 'NXPI': 'XLK', 'ORLY': 'XLY',
    'OXY': 'XLE', 'ODFL': 'XLI', 'OMC': 'XLC', 'ON': 'XLK', 'OKE': 'XLE', 'ORCL': 'XLK', 'OTIS': 'XLI', 'PCAR': 'XLI',
    'PKG': 'XLB', 'PLTR': 'XLK', 'PANW': 'XLK', 'PSKY': 'XLC', 'PH': 'XLI', 'PAYX': 'XLI', 'PAYC': 'XLI', 'PYPL': 'XLF',
    'PNR': 'XLI', 'PEP': 'XLP', 'PFE': 'XLV', 'PCG': 'XLU', 'PM': 'XLP', 'PSX': 'XLE', 'PNW': 'XLU', 'PNC': 'XLF',
    'POOL': 'XLY', 'PPG': 'XLB', 'PPL': 'XLU', 'PFG': 'XLF', 'PG': 'XLP', 'PGR': 'XLF', 'PLD': 'XLRE', 'PRU': 'XLF',
    'PEG': 'XLU', 'PTC': 'XLK', 'PSA': 'XLRE', 'PHM': 'XLY', 'PWR': 'XLI', 'QCOM': 'XLK', 'DGX': 'XLV', 'RL': 'XLY',
    'RJF': 'XLF', 'RTX': 'XLI', 'O': 'XLRE', 'REG': 'XLRE', 'REGN': 'XLV', 'RF': 'XLF', 'RSG': 'XLI', 'RMD': 'XLV',
    'RVTY': 'XLV', 'ROK': 'XLI', 'ROL': 'XLI', 'ROP': 'XLK', 'ROST': 'XLY', 'RCL': 'XLY', 'SPGI': 'XLF', 'CRM': 'XLK',
    'SBAC': 'XLRE', 'SLB': 'XLE', 'STX': 'XLK', 'SRE': 'XLU', 'NOW': 'XLK', 'SHW': 'XLB', 'SPG': 'XLRE', 'SWKS': 'XLK',
    'SJM': 'XLP', 'SW': 'XLB', 'SNA': 'XLI', 'SOLV': 'XLV', 'SO': 'XLU', 'LUV': 'XLI', 'SWK': 'XLI', 'SBUX': 'XLY',
    'STT': 'XLF', 'STLD': 'XLB', 'STE': 'XLV', 'SYK': 'XLV', 'SMCI': 'XLK', 'SYF': 'XLF', 'SNPS': 'XLK', 'SYY': 'XLP',
    'TMUS': 'XLC', 'TROW': 'XLF', 'TTWO': 'XLC', 'TPR': 'XLY', 'TRGP': 'XLE', 'TGT': 'XLP', 'TEL': 'XLK', 'TDY': 'XLK',
    'TER': 'XLK', 'TSLA': 'XLY', 'TXN': 'XLK', 'TPL': 'XLE', 'TXT': 'XLI', 'TMO': 'XLV', 'TJX': 'XLY', 'TKO': 'XLC',
    'TTD': 'XLC', 'TSCO': 'XLY', 'TT': 'XLI', 'TDG': 'XLI', 'TRV': 'XLF', 'TRMB': 'XLK', 'TFC': 'XLF', 'TYL': 'XLK',
    'TSN': 'XLP', 'USB': 'XLF', 'UBER': 'XLI', 'UDR': 'XLRE', 'ULTA': 'XLY', 'UNP': 'XLI', 'UAL': 'XLI', 'UPS': 'XLI',
    'URI': 'XLI', 'UNH': 'XLV', 'UHS': 'XLV', 'VLO': 'XLE', 'VTR': 'XLRE', 'VLTO': 'XLI', 'VRSN': 'XLK', 'VRSK': 'XLI',
    'VZ': 'XLC', 'VRTX': 'XLV', 'VTRS': 'XLV', 'VICI': 'XLRE', 'V': 'XLF', 'VST': 'XLU', 'VMC': 'XLB', 'WRB': 'XLF',
    'GWW': 'XLI', 'WAB': 'XLI', 'WBA': 'XLP', 'WMT': 'XLP', 'DIS': 'XLC', 'WBD': 'XLC', 'WM': 'XLI', 'WAT': 'XLV',
    'WEC': 'XLU', 'WFC': 'XLF', 'WELL': 'XLRE', 'WST': 'XLV', 'WDC': 'XLK', 'WY': 'XLRE', 'WSM': 'XLY', 'WMB': 'XLE',
    'WTW': 'XLF', 'WDAY': 'XLK', 'WYNN': 'XLY', 'XEL': 'XLU', 'XYL': 'XLI', 'YUM': 'XLY', 'ZBRA': 'XLK', 'ZBH': 'XLV',
    'ZTS': 'XLV', 'APP': 'XLK', 'HOOD': 'XLF', 'EME': 'XLI', 'IBKR': 'XLF'
}

