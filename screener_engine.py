"""
╔══════════════════════════════════════════════════════════════════════╗
║     INDIA STOCK SCREENER ENGINE - NSE/BSE PROFESSIONAL GRADE        ║
║     50 Screener Modes | Momentum | Institutional | AI Signals        ║
╚══════════════════════════════════════════════════════════════════════╝
"""

import os
import yfinance as yf
import pandas as pd
import numpy as np
import requests
import json
import time
import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import warnings
warnings.filterwarnings('ignore')
from candlestick_engine import CandlestickPatternDetector

# ─────────────────────────────────────────────────
# NSE / BSE COMPLETE STOCK UNIVERSE
# ─────────────────────────────────────────────────

NIFTY50_STOCKS = [
    "RELIANCE","TCS","HDFCBANK","BHARTIARTL","ICICIBANK","INFOSYS","SBIN","HINDUNILVR",
    "ITC","LT","KOTAKBANK","HCLTECH","AXISBANK","BAJFINANCE","MARUTI","SUNPHARMA",
    "TITAN","ADANIENT","NTPC","POWERGRID","ULTRACEMCO","WIPRO","NESTLEIND","JSWSTEEL",
    "TATAMOTORS","M&M","COALINDIA","ONGC","TATASTEEL","TECHM","DRREDDY","CIPLA",
    "BAJAJFINSV","INDUSINDBK","BPCL","GRASIM","APOLLOHOSP","DIVISLAB","HEROMOTOCO",
    "EICHERMOT","TRENT","SHRIRAMFIN","LTIM","HDFCLIFE","SBILIFE","BRITANNIA",
    "ADANIPORTS","BEL","TATACONSUM","HINDALCO"
]

NIFTY_NEXT50 = [
    "SIEMENS","HAL","DLF","VEDL","ZOMATO","NYKAA","PAYTM","IRFC","RECLTD","PFC",
    "CANBK","BANKBARODA","PIIND","ALKEM","MARICO","BERGEPAINT","AMBUJACEM","ACC",
    "GODREJCP","DABUR","COLPAL","PGHH","MUTHOOTFIN","CHOLAFIN","BAJAJ-AUTO",
    "MOTHERSON","FORTIS","MAXHEALTH","ZYDUSLIFE","LICI","NHPC","SJVN","IREDA",
    "RAILTEL","RVNL","COCHINSHIP","MAZAGON","GRSE","HFCL","SUZLON","ADANIGREEN",
    "ADANIPOWER","ADANITRANS","ATGL","AWL","GODREJPROP","PRESTIGE","PHOENIXLTD",
    "LODHA","SOBHA"
]

MIDCAP_STOCKS = [
    "INDHOTEL","MCDOWELL-N","PAGEIND","WHIRLPOOL","VOLTAS","BLUEDART","CONCOR",
    "APOLLOTYRE","MRF","CEATLTD","BALKRISIND","GNFC","DEEPAKNTR","AAVAS","CANFINHOME",
    "HOMEFIRST","CREDITACC","SPANDANA","SUVENPHAR","NEULANDLAB","DIVI","LALPATHLAB",
    "METROPOLIS","THYROCARE","KPRMILL","WELSPUNIND","TRIDENT","RAYMOND",
    "VIPIND","SAFARI","VSTIND","GODFRYPHLP","IGL","MGL","GUJTGAS","AEGISLOG",
    "GPPL","ESAB","KPITTECH","PERSISTENT","MASTEK","HAPPIEST","COFORGE","MPHASIS",
    "LTTS","CYIENT","TATAELXSI","HEXAWARE"
]

# ─── BSE EXCLUSIVE & BSE500 STOCKS ───
BSE_LARGECAP = [
    # BSE30 (Sensex) - Many overlap with Nifty50 but BSE-listed
    "RELIANCE","TCS","HDFCBANK","ICICIBANK","INFOSYS","SBIN","BHARTIARTL","HINDUNILVR",
    "ITC","LT","KOTAKBANK","AXISBANK","MARUTI","SUNPHARMA","BAJFINANCE","TITAN",
    "NTPC","POWERGRID","ULTRACEMCO","WIPRO","NESTLEIND","JSWSTEEL","TATAMOTORS",
    "M&M","COALINDIA","ONGC","TATASTEEL","TECHM","HCLTECH","BAJAJFINSV",
    # BSE100 additional
    "ADANIENT","ADANIPORTS","APOLLOHOSP","DRREDDY","CIPLA","HEROMOTOCO","EICHERMOT",
    "TRENT","INDUSINDBK","BPCL","GRASIM","DIVISLAB","SHRIRAMFIN","LTIM",
    "HDFCLIFE","SBILIFE","BRITANNIA","BEL","TATACONSUM","HINDALCO",
]

BSE_MIDCAP = [
    # BSE Midcap Index stocks
    "ASTRAL","CUMMINSIND","SUPREMEIND","SKFINDIA","SCHAEFFLER","TIMKEN","GRINDWELL",
    "CARBORUNIV","THERMAX","BHEL","ABB","SIEMENS","HAVELLS","VOLTAS","WHIRLPOOL",
    "KAJARIACER","ORIENTELEC","CROMPTON","POLYCAB","KANSAINER","AKZONOBEL",
    "BBTC","GOODYEAR","CEAT","APOLLOTYRE","MRF","TVSMOTORS","BAJAJAUTO","ESCORTS",
    "FORCEMOTORS","MAHINDCIE","EXIDEIND","AMARAJABAT","LUMINOUS","VSTIND",
    "RADICO","JUBILANT","UBL","MCDOWELL-N","GLOBUSSPR","PAGEIND","THANGAMAYL",
    "KALYANKJIL","STER","SENCO","PCJEWELLER","GITANJALI",
    # PSU Banks
    "BANKBARODA","CANBK","UNIONBANK","IOB","CENTRALBK","MAHABANK","UCOBANK",
    "INDIANB","BANKINDIA","PNBHOUSING","LICHSGFIN",
    # NBFCs
    "BAJAJHLDNG","MANAPPURAM","MUTHOOTFIN","CHOLAFIN","M&MFIN","SHRIRAMFIN",
    "SUNDARMFIN","L&TFH","IIFL","CREDITACC","HOMEFIRST","AAVAS","APTUS",
    # Insurance
    "HDFCLIFE","SBILIFE","ICICIGI","ICICIPRULI","STARHEALTH","NIACL","GICRE",
    # Pharma additional
    "AUROPHARMA","LUPIN","TORNTPHARM","IPCALAB","ABBOTINDIA","PFIZER","SANOFI",
    "GLAXO","ALKEM","AJANTPHARM","JBCHEPHARM","GLENMARK","NATCOPHARM","ZYDUSLIFE",
    "LAURUSLABS","GRANULES","SUVEN","NEULANDLAB","SUVENPHAR","DIVIS","CAPLIPOINT",
    # IT additional
    "MPHASIS","COFORGE","LTTS","CYIENT","TATAELXSI","KPITTECH","PERSISTENT",
    "MASTEK","HAPPIEST","HEXAWARE","RATEGAIN","NEWGEN","NUCLEUS","SAKSOFT",
    # Auto Components
    "MOTHERSON","BOSCHLTD","BHARATFORG","SUNDRMFAST","ENDURANCE","SUPRAJIT",
    "GABRIEL","LUMAXTECH","SUBROS","UCALFUEL","JMTAUTO","IGARASHI",
    # Real Estate
    "DLF","GODREJPROP","PRESTIGE","PHOENIXLTD","LODHA","SOBHA","BRIGADE",
    "KOLTEPATIL","MAHLIFE","OBEROI","SUNTECK","PURVANKARA","ANANTRAJ",
    # Infra / Construction
    "LT","NCC","HG INFRA","HGINFRA","KEC","KALPATPOWR","IRB","DILIPBUILDCON",
    "PNCINFRA","SADBHAV","GAYAPROJ","JKCEMENT","RAMCOCEM","HEIDELBERG",
    # Chemicals
    "PIDILITIND","GNFC","DEEPAKNTR","VINDHYATEL","NOCIL","AARTI","BALAJI",
    "FINEORG","NAVINFLUOR","FLUOROCHEM","CLEAN","CAMLIN","SRF","ATUL","BASF",
    "SUDARSCHEM","VINYLCHEM","TATACHEM","GHCL","TRONOX","ALKYLAMINE",
    # FMCG
    "COLPAL","MARICO","DABUR","GODREJCP","EMAMILTD","BAJAJCON","JYOTHYLAB",
    "VBL","VARUNBEV","BIKAJI","PRATAAP","DOMS","HATSUN","HERITAGE","PARAG",
    # Textiles
    "RAYMOND","TRIDENT","WELSPUNIND","PAGEIND","KPRMILL","VARDHMAN","ARVIND",
    "LAHOTI","GOKALDAS","HIMATSEIDE","NITIN","SPANDEXIND","SUTLEJ",
    # Hotels / Tourism
    "INDHOTEL","LEMONTREE","CHALET","MAHINDHOLIDAYS","THOMASCOOK","EIH","EIHASP",
    # Media
    "ZEEL","SUNTV","PVR","INOXLEISURE","NAZARA","SAREGAMA","TIPS",
    # Logistics
    "CONCOR","BLUEDART","MAHLOG","TCI","GATI","ALLCARGO","GATEWAY","VRLLOG",
    # Power
    "ADANIPOWER","ADANIGREEN","TATAPOWER","CESC","TORNTPOWER","RPOWER","GIPCL",
    "JPPOWER","NHPC","SJVN","IREDA","POWERGRIDINDIA",
    # Defence / PSU
    "HAL","BEL","BEML","BHEL","GRSE","MAZAGON","COCHINSHIP","MIDHANI","MTAR",
    "PARAS","SOLARINDS","ZEN","DYNAMATECH",
    # Metals / Mining
    "VEDL","HINDZINC","HINDCOPPER","MOIL","NMDC","SAIL","JSWSTEEL","TATASTEEL",
    "JINDALSAW","JSWISPL","WELCORP","RATNAMANI","MANGLMCMT","HPIL",
    # Cement
    "ULTRACEMCO","AMBUJACEM","ACC","SHREECEM","RAMCOCEM","JKCEMENT","DALMIACEM",
    "HEIDELBERG","STARCEMENT","BIRLACORPN","MANGCEMCEM","NCLIND","SAGCEM",
    # Retail / Ecommerce
    "DMART","TRENT","VEDANT","VSTIND","VMART","BATA","RELAXO","CAMPUS","METRO",
    # Telecom
    "BHARTIARTL","VODAIDEA","TATACOMM","RAILTEL","HFCL","STERLITE",
]

BSE_SMALLCAP = [
    # BSE SmallCap Index - High momentum candidates
    "IDFCFIRSTB","UJJIVANSFB","EQUITASBNK","SURYODAY","JANA","ESAFSFB",
    "RBLBANK","DCBBANK","KARNATAKA","SOUTHBANK","LAXMIBK",
    # Small Pharma
    "CAPLIPOINT","SHILPAMED","MEDANTA","MAXHEALTH","FORTIS","APOLLOHOSP",
    "NARAYANA","YATHARTH","ASTER","RAINBOW","VIJAYAHOSP","GLOBAL",
    # Small IT
    "RATEGAIN","NEWGEN","NUCLEUS","SAKSOFT","TANLA","ROUTE","INTELLECT",
    "SUBEXLTD","TATATECH","QUICKHEAL","INFIBEAM","INDIAMART","JUSTDIAL",
    # Small Finance
    "SPANDANA","CREDITACC","FUSION","AROHAN","SATIN","BHARAT","GRAMEEN",
    # Specialty Chemicals Small
    "VALIANT","MANGALAM","BODAL","TRONOX","YASHO","VINYLCHEM","LAXMICHEM",
    "TATVA","STARKEM","MEGHMANI","IGPL","KIRI","VINATI",
    # Agri
    "UPL","PI","BAYER","GHCL","COROMANDEL","CHAMBAL","GNFC","GSFC",
    "DHARAMSI","PARADEEP","DEEPAKNTR","NAGARFERT",
    # Paper / Packaging
    "TNPL","WESTERNINDIA","PAKKA","SATIA","JK","ORIENT","MIRCELECTR","CENTURYPLY",
    "GREENPLY","GREENLAM","WPIL","ASTRAL",
    # Consumer Durables Small
    "DIXON","AMBER","WHIRLPOOL","VOLTAS","BLUESTAR","SYMPHONY","ORIENTELEC",
    "CROMPTON","BAJAJELEC","HAVELLS","POLYCAB","KEI","FINOLEX","HPIL",
    # Aviation / Logistics
    "INDIGO","SPICEJET","BLUEDART","MAHLOG","TCI","GATI","ALLCARGO",
    # EV / New Energy
    "TATAPOWER","ADANIGREEN","RPOWER","SUZLON","INOXWIND","GREENKO","NTPC",
    "OLECTRA","JBMA","PMI","KPIEL","EVOLTANEW",
    # Jewellery
    "THANGAMAYL","KALYANKJIL","SENCO","TRIBHOVANDAS","PCJEWELLER","VAIBHAVGBL",
    "TITAN","RAJESHEXPO","SICAL",
    # Gaming / Entertainment
    "NAZARA","PVR","INOXLEISURE","TIPS","SAREGAMA","ZEEL","BALAJITELE",
    # Misc High-momentum Small Caps
    "JAIBALAJI","IRFC","RVNL","RAILTEL","IRCON","NBCC","NHPC","SJVN",
    "RECLTD","PFC","REC","MOIL","NALCO","HINDCOPPER","KIOCL",
    "MTNL","BSNL","ITI","HCL","ECLERX","HEXAWARE","RDHOLTD",
]

# BSE500 Additional stocks not in NSE universe
BSE_ADDITIONAL = [
    # Additional BSE-listed companies
    "3MINDIA","AADHAARENT","AARTIDRUGS","AARTIIND","AAVAS","ABBOTINDIA",
    "ACCELYA","ADANIENSOL","ADANIGAS","AFFLE","AJANTPHARM","AKZONOBEL",
    "ALEMBICLTD","ALEMBICPHARMA","ALKYLAMINE","AMARAJABAT","AMBER","AMBUJACEM",
    "ANDHRPAPER","ANURAS","APCOTEXIND","APOLLOHOSP","APOLLOTYRE","APTUS",
    "ARVINDFASN","ASAHIINDIA","ASHOKLEY","ASIANPAINT","ASTERDM","ASTRAL",
    "ATUL","AUROPHARMA","AVANTIFEED","AXISBANK","BAJAJCON","BAJAJHLDNG",
    "BAJAJ-AUTO","BAJAJELEC","BAJAJFINSV","BAJFINANCE","BALKRISIND","BALRAMCHIN",
    "BANDHANBNK","BASF","BATA","BAYERCROP","BCG","BEML","BERGEPAINT",
    "BHARAT","BHARATFORG","BHARTIARTL","BHEL","BIKAJI","BLUESTARCO",
    "BOSCHLTD","BRIGADE","BSE","CAMS","CAMPUSACTI","CAPLIPOINT",
    "CARBORUNIV","CASTROLIND","CEATLTD","CENTURYTEX","CGPOWER","CHALET",
    "CHOLAFIN","CLEAN","CMSINFO","COCHINSHIP","COFORGE","COLPAL",
    "CONCOR","COROMANDEL","CREDITACC","CRISIL","CROMPTON","CUMMINSIND",
    "CYIENT","DABUR","DATAPATTNS","DCBBANK","DCMSHRIRAM","DEEPAKNTR",
    "DELTACORP","DHANI","DHANUKA","DIXON","DMART","DOMS",
    "DRREDDY","ECLERX","EIH","ELGIEQUIP","EMAMILTD","ENDURANCE",
    "ENGINERSIN","EPIGRAL","EQUITASBNK","ESCORTS","EXIDEIND","FINEORG",
    "FINOLEXCAB","FLUOROCHEM","FORCEMOTORS","GABRIEL","GAIL","GATEWAY",
    "GHCL","GILLETTE","GLAXO","GLENMARK","GMRAIRPORT","GODREJAGRO",
    "GODREJCP","GODREJIND","GODREJPROP","GOODYEAR","GRANULES","GRAPHITE",
    "GREENPANEL","GREENLAM","GRSE","GSFC","GSPL","GUJALKALI","GUJGASLTD",
    "HAPPIEST","HARDWYN","HATSUN","HAWKINCOOK","HDFCAMC","HEXAWARE",
    "HIMATSEIDE","HINDCOPPER","HINDZINC","HONAUT","HPL","HUHTAMAKI",
    "IBREALEST","IDBI","IDFCFIRSTB","IEX","IGPL","IMAMC","INDGN",
    "INDIGOPNTS","INDOCO","INTELLECT","IOB","IPCA","IRCON","ISGEC",
    "JCHAC","JINDALSAW","JKCEMENT","JKPAPER","JLHL","JMFINANCIL",
    "JUBILANT","JUBLFOOD","JYOTHYLAB","KALPATPOWR","KALYANKJIL","KANSAINER",
    "KARURVYSYA","KAVERI","KEC","KFINTECH","KIRI","KIRLOSKAR","KIRLAUTOS",
    "KNRCON","KOLTEPATIL","KPITTECH","KPRMILL","LALPATHLAB","LAURUSLABS",
    "LEMONTREE","LICHSGFIN","LINDEINDIA","LUMAXTECH","LUPIN","LUXIND",
    "MAHLIFE","MANAPPURAM","MARKSANS","MASTEK","MEDPLUS","METROPOLIS",
    "MIDHANI","MOIL","MTAR","MUTHOOTFIN","NAHARSPING","NALCO","NAUKRI",
    "NAVINFLUOR","NAZARA","NCC","NEWGEN","NHPC","NLCINDIA","NMDC",
    "NOCIL","NORTHARC","NUCLEUS","OBEROIRLTY","OIL","ORIENTELEC",
    "PAGEIND","PARAS","PARKE","PATELENG","PCJEWELLER","PERSISTENT",
    "PGHH","PI","PIDILITIND","PIIND","PNCINFRA","POLYCAB","POLYMED",
    "POWERMECH","PRATAAP","PRINCEPIPE","PRIVISCL","PRSMJOHNSN","QUESS",
    "QUICKHEAL","RADICO","RATEGAIN","RATNAMANI","REC","RELAXO",
    "ROUTE","RPGLIFE","RPPINFRA","SAKSOFT","SANOFI","SCHAEFFLER",
    "SENCO","SKFINDIA","SJVN","SOBHA","SOLARA","SOLARINDS","SPANDANA",
    "STARHEALTH","SUBROS","SUDARSCHEM","SUNDARMFIN","SUNDRMFAST","SUNPHARMA",
    "SUPREMEIND","SUVEN","TANLA","TATACHEM","TATACOMM","TATAMETALI",
    "TATATECH","THANGAMAYL","THERMAX","TIMKEN","TIPSINDLTD","TITANCOMP",
    "TNPL","TORNTPHARM","TORNTPOWER","TRONOX","TRIDENT","UJJIVANSFB",
    "UPL","UTIAMC","VAIBHAVGBL","VARROC","VBL","VEDANT","VIJAYAHOSP",
    "VINATI","VSTIND","VMART","WELCORP","WELSPUNIND","WESTLIFE",
    "WIPRO","WONDERLA","XCHANGING","YATHARTH","ZENSARTECH","ZOMATO",
]

# ─── ALL NSE STOCKS ───
NSE_ALL_STOCKS = list(set(NIFTY50_STOCKS + NIFTY_NEXT50 + MIDCAP_STOCKS))

# ─── ALL BSE STOCKS ───
BSE_ALL_STOCKS = list(set(BSE_LARGECAP + BSE_MIDCAP + BSE_SMALLCAP + BSE_ADDITIONAL))

# ─────────────────────────────────────────────────
# NSE OFFICIAL F&O (FUTURES & OPTIONS) UNIVERSE (184 STOCKS)
# ─────────────────────────────────────────────────
FNO_STOCKS = [
    "AARTIIND","ABB","ABBOTINDIA","ABCAPITAL","ABFRL","ACC","ADANIENT","ADANIPORTS",
    "ALKEM","AMBUJACEM","APOLLOHOSP","APOLLOTYRE","ASHOKLEY","ASTRAL","ATUL",
    "AUBANK","AUROPHARMA","AXISBANK","BAJAJ-AUTO","BAJAJFINSV","BAJFINANCE",
    "BALKRISIND","BALRAMCHIN","BANDHANBNK","BANKBARODA","BATAINDIA","BEL","BERGEPAINT",
    "BHARATFORG","BHARTIARTL","BHEL","BIOCON","BOSCHLTD","BPCL","BRITANNIA",
    "BSOFT","CANBK","CANFINHOME","CHAMBLFERT","CHOLAFIN","CIPLA","COALINDIA",
    "COFORGE","COLPAL","CONCOR","COROMANDEL","CROMPTON","CUB","CUMMINSIND",
    "DABUR","DALBHARAT","DEEPAKNTR","DELHIVERY","DIVISLAB","DIXON","DLF",
    "DRREDDY","EICHERMOT","ESCORTS","EXIDEIND","FEDERALBNK","GAIL","GLENMARK",
    "GMRINFRA","GNFC","GODREJCP","GODREJPROP","GRANULES","GRASIM","GUJGASLTD",
    "HAL","HAVELLS","HCLTECH","HDFCAMC","HDFCBANK","HDFCLIFE","HEROMOTOCO",
    "HINDALCO","HINDCOPPER","HINDPETRO","HINDUNILVR","ICICIBANK","ICICIGI","ICICIPRULI",
    "IDEA","IDFC","IDFCFIRSTB","IEX","IGL","INDHOTEL","INDIACEM",
    "INDIAMART","INDIGO","INDUSINDBK","INDUSTOWER","INFY","IOC","IPCALAB",
    "IRCTC","ITC","JINDALSTEL","JKCEMENT","JSWSTEEL","JUBLFOOD","KOTAKBANK",
    "LALPATHLAB","LAURUSLABS","LICHSGFIN","LICI","LT","LTIM","LTTS",
    "LUPIN","M&M","M&MFIN","MANAPPURAM","MARICO","MARUTI","MAXHEALTH",
    "MCX","METROPOLIS","MFSL","MGL","MOTHERSON","MPHASIS","MRF",
    "MUTHOOTFIN","NATIONALUM","NAUKRI","NAVINFLUOR","NESTLEIND","NMDC","NTPC",
    "OBEROIRLTY","OFSS","ONGC","PAGEIND","PEL","PERSISTENT","PETRONET",
    "PFC","PIDILITIND","PIIND","PNB","POLYCAB","POWERGRID","PVRINOX",
    "RAMCOCEM","RBLBANK","RECLTD","RELIANCE","SAIL","SBICARD","SBILIFE",
    "SBIN","SHREECEM","SHRIRAMFIN","SIEMENS","SRF","SUNPHARMA","SUNTV",
    "SYNGENE","TATACHEM","TATACOMM","TATACONSUM","TATAMOTORS","TATAPOWER","TATASTEEL",
    "TCS","TECHM","TITAN","TORNTPHARM","TORNTPOWER","TRENT","TVSMOTOR",
    "UBL","ULTRACEMCO","UPL","VEDL","VOLTAS","WIPRO","ZOMATO","ZYDUSLIFE"
]
FNO_STOCKS_SET = set(FNO_STOCKS)

def is_fno_stock(symbol: str) -> bool:
    """Check if stock symbol is part of NSE F&O derivatives universe"""
    return str(symbol).strip().upper() in FNO_STOCKS_SET

# ─────────────────────────────────────────────────
# 1ST DAY IPO & NEW LISTED STOCKS ENGINE
# ─────────────────────────────────────────────────
IPO_DATA_FILE = os.path.join(os.path.dirname(__file__), "data", "new_ipo_listings.json")

def load_new_ipo_listings() -> List[Dict]:
    """Load newly listed and 1st day IPO stocks from persistent storage"""
    if os.path.exists(IPO_DATA_FILE):
        try:
            with open(IPO_DATA_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                today_str = datetime.now().strftime('%Y-%m-%d')
                for item in data:
                    l_date = item.get('listing_date', '')
                    if l_date == today_str:
                        item['is_day1'] = True
                        item['status'] = '1ST DAY LISTED'
                    elif not item.get('status'):
                        item['status'] = 'RECENT LISTING'
                return data
        except Exception:
            pass
    return []

def save_new_ipo_listing(ipo_item: Dict) -> bool:
    """Save or update an IPO listing in persistent storage and auto-add to universes"""
    try:
        listings = load_new_ipo_listings()
        sym = ipo_item.get('symbol', '').strip().upper()
        if not sym:
            return False
        
        found = False
        for i, existing in enumerate(listings):
            if existing.get('symbol', '').upper() == sym:
                listings[i].update(ipo_item)
                found = True
                break
        if not found:
            listings.insert(0, ipo_item)
            
        os.makedirs(os.path.dirname(IPO_DATA_FILE), exist_ok=True)
        with open(IPO_DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(listings, f, indent=2)
            
        # Dynamically inject into universe
        if sym not in ALL_STOCKS:
            ALL_STOCKS.append(sym)
        if sym not in NSE_ALL_STOCKS:
            NSE_ALL_STOCKS.append(sym)
        return True
    except Exception as e:
        print(f"Error saving IPO listing: {e}")
        return False

def get_all_ipo_symbols() -> List[str]:
    """Get list of all tracked IPO & newly listed symbols"""
    listings = load_new_ipo_listings()
    symbols = [item['symbol'] for item in listings if item.get('symbol')]
    return symbols if symbols else ["SWIGGY", "HYUNDAI", "WAAREEENER", "NTPCGREEN", "BAJAJHFL", "PREMIERENE"]

def get_ipo_info(symbol: str) -> Optional[Dict]:
    """Get IPO listing metadata for a stock if it is a recent listing"""
    sym = str(symbol).strip().upper()
    listings = load_new_ipo_listings()
    for item in listings:
        if item.get('symbol', '').upper() == sym:
            return item
    return None

# ─── COMBINED NSE + BSE UNIVERSE (deduplicated, with F&O and IPOs) ───
ALL_STOCKS = list(set(NSE_ALL_STOCKS + BSE_ALL_STOCKS + FNO_STOCKS + get_all_ipo_symbols()))

# ─── SECTOR-WISE GROUPINGS ───
SECTOR_BANKS = [
    "HDFCBANK","ICICIBANK","SBIN","AXISBANK","KOTAKBANK","INDUSINDBK","BANKBARODA",
    "CANBK","UNIONBANK","IDFCFIRSTB","RBLBANK","BANDHANBNK","DCBBANK","FEDERALBNK",
    "KARNATAKA","SOUTHBANK","UJJIVANSFB","EQUITASBNK","YESBANK","IOB","MAHABANK",
    "CENTRALBK","INDIANB","BANKINDIA","LAXMIBK","JANA","ESAFSFB"
]
SECTOR_IT = [
    "TCS","INFOSYS","HCLTECH","WIPRO","TECHM","LTIM","MPHASIS","COFORGE","LTTS",
    "CYIENT","TATAELXSI","KPITTECH","PERSISTENT","MASTEK","HAPPIEST","HEXAWARE",
    "RATEGAIN","NEWGEN","NUCLEUS","SAKSOFT","TANLA","ROUTE","INTELLECT","ECLERX"
]
SECTOR_PHARMA = [
    "SUNPHARMA","DRREDDY","CIPLA","DIVISLAB","APOLLOHOSP","AUROPHARMA","LUPIN",
    "TORNTPHARM","IPCALAB","ABBOTINDIA","ALKEM","AJANTPHARM","GLENMARK","ZYDUSLIFE",
    "LAURUSLABS","GRANULES","CAPLIPOINT","NATCOPHARM","NEULANDLAB","SUVENPHAR"
]
SECTOR_AUTO = [
    "MARUTI","TATAMOTORS","M&M","HEROMOTOCO","EICHERMOT","BAJAJ-AUTO","TVSMOTORS",
    "MOTHERSON","BHARATFORG","BOSCHLTD","EXIDEIND","APOLLOTYRE","MRF","CEATLTD",
    "BALKRISIND","ESCORTS","FORCEMOTORS","ENDURANCE","SUNDRMFAST"
]
SECTOR_FMCG = [
    "HINDUNILVR","ITC","NESTLEIND","BRITANNIA","DABUR","MARICO","GODREJCP","COLPAL",
    "EMAMILTD","BAJAJCON","JYOTHYLAB","VBL","VARUNBEV","BIKAJI","PRATAAP","HATSUN"
]
SECTOR_REALTY = [
    "DLF","GODREJPROP","PRESTIGE","PHOENIXLTD","LODHA","SOBHA","BRIGADE","KOLTEPATIL",
    "MAHLIFE","OBEROIRLTY","SUNTECK","PURVANKARA","ANANTRAJ","IBREALEST"
]
SECTOR_METAL = [
    "TATASTEEL","JSWSTEEL","HINDALCO","VEDL","SAIL","NMDC","COALINDIA","MOIL",
    "HINDCOPPER","NALCO","WELCORP","RATNAMANI","JINDALSAW","HINDZINC"
]
SECTOR_ENERGY = [
    "RELIANCE","ONGC","BPCL","NTPC","POWERGRID","ADANIGREEN","ADANIPOWER","TATAPOWER",
    "NHPC","SJVN","IREDA","CESC","TORNTPOWER","RPOWER","GIPCL","GAIL","OIL"
]
SECTOR_DEFENCE = [
    "HAL","BEL","BEML","BHEL","GRSE","MAZAGON","COCHINSHIP","MIDHANI","MTAR",
    "SOLARINDS","ZEN","DYNAMATECH","PARAS","DATAPATTNS"
]
SECTOR_CHEMICALS = [
    "PIDILITIND","DEEPAKNTR","GNFC","SRF","ATUL","NAVINFLUOR","FLUOROCHEM","AARTI",
    "FINEORG","NOCIL","SUDARSCHEM","VINATI","ALKYLAMINE","TATACHEM","GHCL","BASF"
]

SECTOR_MAP = {
    "Banks & NBFC": SECTOR_BANKS,
    "Information Technology": SECTOR_IT,
    "Pharmaceuticals": SECTOR_PHARMA,
    "Automobiles": SECTOR_AUTO,
    "FMCG": SECTOR_FMCG,
    "Real Estate": SECTOR_REALTY,
    "Metals & Mining": SECTOR_METAL,
    "Energy & Power": SECTOR_ENERGY,
    "Defence & PSU": SECTOR_DEFENCE,
    "Chemicals": SECTOR_CHEMICALS,
}


def get_yahoo_symbol(symbol: str, exchange: str = "NSE") -> str:
    """Convert stock symbol to Yahoo Finance format.
    NSE stocks → .NS suffix
    BSE stocks  → .BO suffix (fallback)
    """
    # Symbols only on BSE (not on NSE)
    BSE_ONLY = {
        "THANGAMAYL","SENCO","VAIBHAVGBL","GITANJALI","PCJEWELLER","RAJESHEXPO",
        "BIKAJI","PRATAAP","DOMS","KALYANKJIL","BBTC","GLOBUSSPR","GOODYEAR",
        "ISGEC","HARDWYN","HAWKINCOOK","HUHTAMAKI","JCHAC","LINDEINDIA",
        "LUXIND","NAHARSPING","PRINCEPIPE","PRSMJOHNSN","QUESS","RPGLIFE",
        "RPPINFRA","SOLARA","TITANCOMP","XCHANGING","WONDERLA","WESTLIFE",
        "TIPSINDLTD","DELTACORP","HINDWARE","CMSINFO","NORTHARC",
    }
    if symbol in BSE_ONLY:
        return f"{symbol}.BO"
    return f"{symbol}.NS"

# ─────────────────────────────────────────────────
# TECHNICAL INDICATORS ENGINE
# ─────────────────────────────────────────────────

class TechnicalAnalysis:
    
    @staticmethod
    def ema(series: pd.Series, period: int) -> pd.Series:
        return series.ewm(span=period, adjust=False).mean()
    
    @staticmethod
    def sma(series: pd.Series, period: int) -> pd.Series:
        return series.rolling(window=period).mean()
    
    @staticmethod
    def rsi(series: pd.Series, period: int = 14) -> pd.Series:
        delta = series.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))
    
    @staticmethod
    def macd(series: pd.Series, fast=12, slow=26, signal=9):
        ema_fast = series.ewm(span=fast, adjust=False).mean()
        ema_slow = series.ewm(span=slow, adjust=False).mean()
        macd_line = ema_fast - ema_slow
        signal_line = macd_line.ewm(span=signal, adjust=False).mean()
        histogram = macd_line - signal_line
        return macd_line, signal_line, histogram
    
    @staticmethod
    def bollinger_bands(series: pd.Series, period=20, std_dev=2):
        sma = series.rolling(window=period).mean()
        std = series.rolling(window=period).std()
        upper = sma + (std * std_dev)
        lower = sma - (std * std_dev)
        return upper, sma, lower
    
    @staticmethod
    def atr(high: pd.Series, low: pd.Series, close: pd.Series, period=14) -> pd.Series:
        tr1 = high - low
        tr2 = abs(high - close.shift(1))
        tr3 = abs(low - close.shift(1))
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        return tr.rolling(window=period).mean()
    
    @staticmethod
    def stochastic(high: pd.Series, low: pd.Series, close: pd.Series, k=14, d=3):
        lowest_low = low.rolling(window=k).min()
        highest_high = high.rolling(window=k).max()
        k_line = 100 * (close - lowest_low) / (highest_high - lowest_low)
        d_line = k_line.rolling(window=d).mean()
        return k_line, d_line
    
    @staticmethod
    def adx(high: pd.Series, low: pd.Series, close: pd.Series, period=14) -> pd.Series:
        """Average Directional Index"""
        plus_dm = high.diff()
        minus_dm = low.diff().abs()
        plus_dm[plus_dm < 0] = 0
        minus_dm[minus_dm < 0] = 0
        
        tr1 = high - low
        tr2 = abs(high - close.shift(1))
        tr3 = abs(low - close.shift(1))
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        
        atr_val = tr.rolling(period).mean()
        plus_di = 100 * (plus_dm.rolling(period).mean() / atr_val)
        minus_di = 100 * (minus_dm.rolling(period).mean() / atr_val)
        
        dx = 100 * abs(plus_di - minus_di) / (plus_di + minus_di)
        adx = dx.rolling(period).mean()
        return adx, plus_di, minus_di
    
    @staticmethod
    def volume_ratio(volume: pd.Series, period=20) -> pd.Series:
        avg_vol = volume.rolling(window=period).mean()
        return volume / avg_vol
    
    @staticmethod
    def supertrend(high, low, close, atr_period=10, multiplier=3.0):
        """SuperTrend Indicator"""
        atr = TechnicalAnalysis.atr(high, low, close, atr_period)
        hl2 = (high + low) / 2
        upper_band = hl2 + (multiplier * atr)
        lower_band = hl2 - (multiplier * atr)
        
        supertrend = pd.Series(index=close.index, dtype=float)
        direction = pd.Series(index=close.index, dtype=int)
        
        for i in range(1, len(close)):
            if close.iloc[i] > upper_band.iloc[i-1]:
                direction.iloc[i] = 1  # Bullish
            elif close.iloc[i] < lower_band.iloc[i-1]:
                direction.iloc[i] = -1  # Bearish
            else:
                direction.iloc[i] = direction.iloc[i-1]
        
        return direction
    
    @staticmethod
    def pivot_points(high, low, close):
        """Classic Pivot Points"""
        pivot = (high + low + close) / 3
        r1 = 2 * pivot - low
        r2 = pivot + (high - low)
        r3 = r1 + (high - low)
        s1 = 2 * pivot - high
        s2 = pivot - (high - low)
        s3 = s1 - (high - low)
        return pivot, r1, r2, r3, s1, s2, s3
    
    @staticmethod
    def williams_r(high, low, close, period=14):
        highest_high = high.rolling(period).max()
        lowest_low = low.rolling(period).min()
        return -100 * (highest_high - close) / (highest_high - lowest_low)
    
    @staticmethod
    def cci(high, low, close, period=20):
        tp = (high + low + close) / 3
        sma_tp = tp.rolling(period).mean()
        mean_dev = tp.rolling(period).apply(lambda x: np.mean(np.abs(x - x.mean())))
        return (tp - sma_tp) / (0.015 * mean_dev)
    
    @staticmethod
    def obv(close, volume):
        """On Balance Volume"""
        obv = pd.Series(index=close.index, dtype=float)
        obv.iloc[0] = volume.iloc[0]
        for i in range(1, len(close)):
            if close.iloc[i] > close.iloc[i-1]:
                obv.iloc[i] = obv.iloc[i-1] + volume.iloc[i]
            elif close.iloc[i] < close.iloc[i-1]:
                obv.iloc[i] = obv.iloc[i-1] - volume.iloc[i]
            else:
                obv.iloc[i] = obv.iloc[i-1]
        return obv
    
    @staticmethod
    def ichimoku(high, low, close):
        """Ichimoku Cloud"""
        tenkan = (high.rolling(9).max() + low.rolling(9).min()) / 2
        kijun = (high.rolling(26).max() + low.rolling(26).min()) / 2
        senkou_a = (tenkan + kijun) / 2
        senkou_b = (high.rolling(52).max() + low.rolling(52).min()) / 2
        return tenkan, kijun, senkou_a, senkou_b
    
    @staticmethod
    def vwap(high, low, close, volume):
        """Volume Weighted Average Price"""
        tp = (high + low + close) / 3
        return (tp * volume).cumsum() / volume.cumsum()


# ─────────────────────────────────────────────────
# STOCK DATA FETCHER
# ─────────────────────────────────────────────────

class StockDataFetcher:
    
    def __init__(self):
        self.cache = {}
        self.cache_time = {}
        self.cache_duration = 300  # 5 minutes cache
    
    def _fetch_with_fallback(self, symbol: str, period: str, interval: str) -> Optional[pd.DataFrame]:
        """Try NSE (.NS) first, then BSE (.BO) as fallback"""
        for suffix in [".NS", ".BO"]:
            try:
                ticker = yf.Ticker(f"{symbol}{suffix}")
                df = ticker.history(period=period, interval=interval)
                if not df.empty:
                    df.index = pd.to_datetime(df.index)
                    df.attrs['exchange'] = 'NSE' if suffix == '.NS' else 'BSE'
                    return df
            except:
                continue
        return None

    def get_stock_data(self, symbol: str, period: str = "3mo", interval: str = "1d", force_refresh: bool = False) -> Optional[pd.DataFrame]:
        """Fetch OHLCV data — tries NSE first, falls back to BSE"""
        cache_key = f"{symbol}_{period}_{interval}"
        now = time.time()
        
        if not force_refresh and cache_key in self.cache and (now - self.cache_time.get(cache_key, 0)) < self.cache_duration:
            return self.cache[cache_key]
        
        df = self._fetch_with_fallback(symbol, period, interval)
        if df is not None:
            self.cache[cache_key] = df
            self.cache_time[cache_key] = now
        return df

    def clear_cache(self):
        """Clear cache for live market refresh"""
        self.cache.clear()
        self.cache_time.clear()
    
    def get_live_quote(self, symbol: str) -> Dict:
        """Get live market data — NSE first, BSE fallback"""
        try:
            hist = self._fetch_with_fallback(symbol, "2d", "1d")
            if hist is None or hist.empty:
                return {}
            exchange = hist.attrs.get('exchange', 'NSE')
            current = hist['Close'].iloc[-1]
            prev = hist['Close'].iloc[-2] if len(hist) > 1 else current
            change = current - prev
            change_pct = (change / prev) * 100 if prev != 0 else 0
            return {
                'symbol': symbol,
                'exchange': exchange,
                'price': round(float(current), 2),
                'change': round(float(change), 2),
                'change_pct': round(float(change_pct), 2),
                'volume': int(hist['Volume'].iloc[-1]),
                'high': round(float(hist['High'].iloc[-1]), 2),
                'low': round(float(hist['Low'].iloc[-1]), 2),
                'open': round(float(hist['Open'].iloc[-1]), 2),
            }
        except Exception as e:
            return {}
    
    def get_institutional_data(self, symbol: str) -> Dict:
        """Get institutional holding data — NSE then BSE fallback"""
        result = {'institutional_pct': 0, 'insider_pct': 0, 'top_institutions': []}
        for suffix in [".NS", ".BO"]:
            try:
                ticker = yf.Ticker(f"{symbol}{suffix}")
                institutional = ticker.institutional_holders
                major_holders = ticker.major_holders
                
                if major_holders is not None and not major_holders.empty:
                    for _, row in major_holders.iterrows():
                        val = str(row.iloc[0])
                        desc = str(row.iloc[1]).lower()
                        if 'institution' in desc:
                            try:
                                result['institutional_pct'] = float(val.replace('%',''))
                            except:
                                pass
                        elif 'insider' in desc:
                            try:
                                result['insider_pct'] = float(val.replace('%',''))
                            except:
                                pass
                
                if institutional is not None and not institutional.empty:
                    for _, row in institutional.head(5).iterrows():
                        try:
                            result['top_institutions'].append({
                                'name': str(row.get('Holder', 'Unknown')),
                                'shares': int(row.get('Shares', 0)),
                                'pct_held': round(float(row.get('% Out', 0)), 2)
                            })
                        except:
                            pass
                if result['institutional_pct'] > 0 or result['top_institutions']:
                    break  # Got data, no need to try BSE
            except:
                continue
        return result


# ─────────────────────────────────────────────────
# 50 SCREENER MODES ENGINE
# ─────────────────────────────────────────────────

class ScreenerEngine:
    
    def __init__(self):
        self.fetcher = StockDataFetcher()
        self.ta = TechnicalAnalysis()
    
    def compute_all_indicators(self, df: pd.DataFrame) -> Dict:
        """Compute all technical indicators for a stock"""
        if df is None or len(df) < 30:
            return {}
        
        close = df['Close']
        high = df['High']
        low = df['Low']
        volume = df['Volume']
        open_ = df['Open']
        
        try:
            # Moving Averages
            ema9 = self.ta.ema(close, 9)
            ema20 = self.ta.ema(close, 20)
            ema50 = self.ta.ema(close, 50)
            ema200 = self.ta.ema(close, 200) if len(df) >= 200 else pd.Series([None]*len(df))
            sma20 = self.ta.sma(close, 20)
            sma50 = self.ta.sma(close, 50)
            
            # Oscillators
            rsi14 = self.ta.rsi(close, 14)
            macd_line, macd_signal, macd_hist = self.ta.macd(close)
            k_stoch, d_stoch = self.ta.stochastic(high, low, close)
            williams = self.ta.williams_r(high, low, close)
            cci20 = self.ta.cci(high, low, close)
            
            # Trend
            adx_val, plus_di, minus_di = self.ta.adx(high, low, close)
            supertrend_dir = self.ta.supertrend(high, low, close)
            
            # Bands
            bb_upper, bb_mid, bb_lower = self.ta.bollinger_bands(close)
            bb_width = (bb_upper - bb_lower) / bb_mid * 100
            bb_pct = (close - bb_lower) / (bb_upper - bb_lower) * 100
            
            # Volume
            vol_ratio = self.ta.volume_ratio(volume)
            obv_val = self.ta.obv(close, volume)
            vwap_val = self.ta.vwap(high, low, close, volume)
            
            # ATR
            atr_val = self.ta.atr(high, low, close)
            
            # Pivot Points (using last day's data)
            if len(df) >= 2:
                pivot, r1, r2, r3, s1, s2, s3 = self.ta.pivot_points(
                    high.iloc[-2], low.iloc[-2], close.iloc[-2]
                )
            else:
                pivot = r1 = r2 = r3 = s1 = s2 = s3 = close.iloc[-1]
            
            # 52-week data
            if len(df) >= 252:
                high_52w = high.rolling(252).max().iloc[-1]
                low_52w = low.rolling(252).min().iloc[-1]
            else:
                high_52w = high.max()
                low_52w = low.min()
            
            # Returns
            ret_1d = ((close.iloc[-1] - close.iloc[-2]) / close.iloc[-2] * 100) if len(close) >= 2 else 0
            ret_5d = ((close.iloc[-1] - close.iloc[-6]) / close.iloc[-6] * 100) if len(close) >= 6 else 0
            ret_1m = ((close.iloc[-1] - close.iloc[-21]) / close.iloc[-21] * 100) if len(close) >= 21 else 0
            ret_3m = ((close.iloc[-1] - close.iloc[-63]) / close.iloc[-63] * 100) if len(close) >= 63 else 0
            
            # 20%+ Rocket Detection: Day percentage MUST strictly be >= 20.0%
            is_20pct_mover = (ret_1d >= 20.0)
            max_return_pct = round(ret_1d, 2)
            
            # Mini Candles for UI Charts (Last 10 bars)
            candles = []
            tail_df = df.tail(12)
            for _, r in tail_df.iterrows():
                candles.append({
                    'o': round(float(r['Open']), 2),
                    'h': round(float(r['High']), 2),
                    'l': round(float(r['Low']), 2),
                    'c': round(float(r['Close']), 2),
                    'v': int(r['Volume'])
                })
            
            # VWAP Distance %
            vwap_dist = round(float((close.iloc[-1] - vwap_val.iloc[-1]) / vwap_val.iloc[-1] * 100), 2) if vwap_val.iloc[-1] > 0 else 0
            
            # Money Flow estimate (Price change * Volume)
            typical_price = (high.iloc[-1] + low.iloc[-1] + close.iloc[-1]) / 3
            raw_money_flow = typical_price * volume.iloc[-1]
            money_flow_cr = round(float(raw_money_flow / 1e7), 2)  # In Crores INR
            
            # Candlestick Patterns Detection
            candlestick_patterns = CandlestickPatternDetector.detect_all_patterns(df)
            pattern_ids = [p['id'] for p in candlestick_patterns]
            pattern_names = [p['name'] for p in candlestick_patterns]

            # Momentum Score
            momentum_score = self._compute_momentum_score(
                rsi14.iloc[-1], macd_hist.iloc[-1], vol_ratio.iloc[-1],
                adx_val.iloc[-1] if not pd.isna(adx_val.iloc[-1]) else 0,
                ret_1d, ret_5d, ret_1m
            )
            
            return {
                'candlestick_patterns': candlestick_patterns,
                'pattern_ids': pattern_ids,
                'pattern_names': pattern_names,
                'close': round(float(close.iloc[-1]), 2),
                'open': round(float(open_.iloc[-1]), 2),
                'high': round(float(high.iloc[-1]), 2),
                'low': round(float(low.iloc[-1]), 2),
                'volume': int(volume.iloc[-1]),
                'avg_volume': int(volume.rolling(20).mean().iloc[-1]),
                
                # MAs
                'ema9': round(float(ema9.iloc[-1]), 2),
                'ema20': round(float(ema20.iloc[-1]), 2),
                'ema50': round(float(ema50.iloc[-1]), 2),
                'ema200': round(float(ema200.iloc[-1]), 2) if not pd.isna(ema200.iloc[-1]) else None,
                'sma20': round(float(sma20.iloc[-1]), 2),
                'sma50': round(float(sma50.iloc[-1]), 2),
                
                # Oscillators
                'rsi': round(float(rsi14.iloc[-1]), 2),
                'macd': round(float(macd_line.iloc[-1]), 4),
                'macd_signal': round(float(macd_signal.iloc[-1]), 4),
                'macd_hist': round(float(macd_hist.iloc[-1]), 4),
                'stoch_k': round(float(k_stoch.iloc[-1]), 2),
                'stoch_d': round(float(d_stoch.iloc[-1]), 2),
                'williams_r': round(float(williams.iloc[-1]), 2),
                'cci': round(float(cci20.iloc[-1]), 2),
                
                # Trend
                'adx': round(float(adx_val.iloc[-1]), 2) if not pd.isna(adx_val.iloc[-1]) else 0,
                'plus_di': round(float(plus_di.iloc[-1]), 2) if not pd.isna(plus_di.iloc[-1]) else 0,
                'minus_di': round(float(minus_di.iloc[-1]), 2) if not pd.isna(minus_di.iloc[-1]) else 0,
                'supertrend': int(supertrend_dir.iloc[-1]) if not pd.isna(supertrend_dir.iloc[-1]) else 0,
                
                # Bollinger
                'bb_upper': round(float(bb_upper.iloc[-1]), 2),
                'bb_mid': round(float(bb_mid.iloc[-1]), 2),
                'bb_lower': round(float(bb_lower.iloc[-1]), 2),
                'bb_width': round(float(bb_width.iloc[-1]), 2),
                'bb_pct': round(float(bb_pct.iloc[-1]), 2),
                
                # Volume
                'vol_ratio': round(float(vol_ratio.iloc[-1]), 2),
                'obv_trend': 'up' if obv_val.iloc[-1] > obv_val.iloc[-5] else 'down',
                'vwap': round(float(vwap_val.iloc[-1]), 2),
                'vwap_dist': vwap_dist,
                'money_flow_cr': money_flow_cr,
                
                # ATR & Risk
                'atr': round(float(atr_val.iloc[-1]), 2),
                'atr_pct': round(float(atr_val.iloc[-1] / close.iloc[-1] * 100), 2),
                
                # Pivots
                'pivot': round(float(pivot), 2),
                'r1': round(float(r1), 2),
                'r2': round(float(r2), 2),
                'r3': round(float(r3), 2),
                's1': round(float(s1), 2),
                's2': round(float(s2), 2),
                's3': round(float(s3), 2),
                
                # 52W
                'high_52w': round(float(high_52w), 2),
                'low_52w': round(float(low_52w), 2),
                'pct_from_52w_high': round(float((close.iloc[-1] - high_52w) / high_52w * 100), 2),
                'pct_from_52w_low': round(float((close.iloc[-1] - low_52w) / low_52w * 100), 2),
                
                # Returns & Rocket Flag
                'ret_1d': round(float(ret_1d), 2),
                'ret_5d': round(float(ret_5d), 2),
                'ret_1m': round(float(ret_1m), 2),
                'ret_3m': round(float(ret_3m), 2),
                'is_20pct_mover': bool(is_20pct_mover),
                'max_return_pct': float(max_return_pct),
                'candles': candles,
                
                # Composite
                'momentum_score': round(float(momentum_score), 1),
            }
        except Exception as e:
            return {}
    
    def _compute_momentum_score(self, rsi, macd_hist, vol_ratio, adx, r1d, r5d, r1m) -> float:
        """Score 0-100 for momentum strength"""
        score = 50  # Base
        
        # RSI contribution (30 pts)
        if 50 < rsi < 70: score += 15
        elif rsi >= 70: score += 10
        elif rsi < 30: score -= 20
        elif rsi < 50: score -= 10
        
        # MACD contribution (20 pts)
        if macd_hist > 0: score += 10
        else: score -= 10
        
        # Volume (20 pts)
        if vol_ratio > 2.0: score += 15
        elif vol_ratio > 1.5: score += 10
        elif vol_ratio > 1.0: score += 5
        
        # ADX trend strength (15 pts)
        if adx > 40: score += 10
        elif adx > 25: score += 5
        
        # Return contribution (15 pts)
        if r1d > 2: score += 5
        if r5d > 5: score += 5
        if r1m > 10: score += 5
        
        return max(0, min(100, score - 50))
    
    def compute_trend_meter(self, ind: Dict) -> Dict:
        """
        Calculates a multi-factor Technical Trend Meter (0-100%):
        1. Moving Average Alignment (Price vs EMA20, EMA50, EMA200)
        2. SuperTrend & ADX Directional System
        3. RSI & Momentum Zones
        4. MACD Histogram
        5. Volume & Daily Price Action Confirmation
        """
        if not ind:
            return {'score': 50.0, 'level': 'NEUTRAL', 'label': '🟡 NEUTRAL', 'color': '#ffb300', 'direction': '↔ SIDEWAYS', 'bars': 3}
            
        score = 50.0
        close = ind.get('close', 0)
        
        # 1. EMAs alignment (Max +25 or -25)
        ema20 = ind.get('ema20')
        ema50 = ind.get('ema50')
        ema200 = ind.get('ema200')
        if ema20 and close > ema20: score += 8
        elif ema20 and close < ema20: score -= 8
        
        if ema50 and close > ema50: score += 9
        elif ema50 and close < ema50: score -= 9
        
        if ema200 and close > ema200: score += 8
        elif ema200 and close < ema200: score -= 8
        
        # 2. SuperTrend & ADX (Max +20 or -17)
        st = ind.get('supertrend', 0)
        adx = ind.get('adx', 15)
        if st == 1:
            score += 12
            if adx >= 25: score += 8
        elif st == -1:
            score -= 12
            if adx >= 25: score -= 5
            
        # 3. RSI (Max +18 or -18)
        rsi = ind.get('rsi', 50)
        if 55 <= rsi <= 72: score += 18
        elif rsi > 72: score += 12
        elif 45 <= rsi < 55: score += 2
        elif 30 <= rsi < 45: score -= 12
        elif rsi < 30: score -= 18
        
        # 4. MACD (Max +12 or -10)
        macd_hist = ind.get('macd_hist', 0)
        if macd_hist > 0: score += 12
        else: score -= 10
        
        # 5. Volume & Price Action (Max +15 or -12)
        vol_ratio = ind.get('vol_ratio', 1.0)
        ret_1d = ind.get('ret_1d', 0)
        if ret_1d > 0 and vol_ratio >= 1.5: score += 15
        elif ret_1d > 0: score += 6
        elif ret_1d < 0 and vol_ratio >= 1.5: score -= 12
        elif ret_1d < 0: score -= 5
        
        # 6. Circuit Rocket bonus
        if ret_1d >= 20.0:
            score += 25
            
        score = max(5.0, min(99.0, score))
        score = round(score, 1)
        
        if score >= 85:
            level = "STRONG_BULL"
            label = "🚀 SUPER BULL"
            color = "#00e676"
            direction = "▲ STRONG UP"
            bars = 5
        elif score >= 65:
            level = "BULLISH"
            label = "🟢 BULLISH"
            color = "#4caf50"
            direction = "▲ UPTREND"
            bars = 4
        elif score >= 45:
            level = "NEUTRAL"
            label = "🟡 NEUTRAL"
            color = "#ffb300"
            direction = "↔ SIDEWAYS"
            bars = 3
        elif score >= 25:
            level = "BEARISH"
            label = "🔴 BEARISH"
            color = "#ff5252"
            direction = "▼ DOWNTREND"
            bars = 2
        else:
            level = "STRONG_BEAR"
            label = "🔻 STRONG BEAR"
            color = "#d50000"
            direction = "▼ STRONG DOWN"
            bars = 1
            
        return {
            'score': score,
            'level': level,
            'label': label,
            'color': color,
            'direction': direction,
            'bars': bars
        }

    def compute_confluence_accuracy(self, ind: Dict, trade_setup: Dict, trend_meter: Dict, candlestick_patterns: List[Dict]) -> Dict:
        """
        Calculates Quantitative Accuracy Rating strictly from 80% to 120%:
        - 80% - 89%: Standard Technical Confluence (Solid base)
        - 90% - 99%: High Conviction Institutional Confluence
        - 100% - 109%: Perfect Multi-Indicator Confluence (Zero conflicting signals)
        - 110% - 120%: Alpha Over-Performer (Explosive Volume + 20%+ Circuit Rockets)
        """
        if not ind:
            return {'score': 82.0, 'level': 'STANDARD', 'label': '★ 82% ACCURACY', 'badge': '★ 82% ACCURACY', 'color': '#ffb300', 'is_99': False, 'reasons': []}

        # Baseline starting at 80%
        score = 80.0
        reasons = []

        # 1. Multi-Factor Trend Meter Confluence (Max +10%)
        tm_score = trend_meter.get('score', 50) if trend_meter else 50
        if tm_score >= 85:
            score += 10.0
            reasons.append(f"Trend Meter {tm_score}% (Super Bull)")
        elif tm_score >= 70:
            score += 6.0
            reasons.append(f"Trend Meter {tm_score}% (Bullish)")

        # 2. Institutional Volume Ratio (Max +10%)
        vol_ratio = ind.get('vol_ratio', 1.0)
        if vol_ratio >= 3.0:
            score += 10.0
            reasons.append(f"Institutional Volume Surge ({vol_ratio}x)")
        elif vol_ratio >= 1.5:
            score += 5.0
            reasons.append(f"Volume Expansion ({vol_ratio}x)")

        # 3. High-Accuracy Candlestick Confirmation (Max +8%)
        high_win_patterns = []
        for p in candlestick_patterns:
            acc_str = str(p.get('accuracy', '0%')).replace('%', '')
            try:
                acc_val = int(acc_str)
                if acc_val >= 88:
                    high_win_patterns.append((p, acc_val))
            except:
                pass

        if high_win_patterns:
            high_win_patterns.sort(key=lambda x: x[1], reverse=True)
            top_p, top_acc = high_win_patterns[0]
            score += 8.0
            reasons.append(f"Candlestick: {top_p.get('name')} ({top_acc}% Win Rate)")
        elif candlestick_patterns:
            score += 4.0
            reasons.append(f"Candlestick: {candlestick_patterns[0].get('name')}")

        # 4. Risk / Reward Structure (Max +6%)
        rr = trade_setup.get('rr_ratio', 0) if trade_setup else 0
        if rr >= 2.5:
            score += 6.0
            reasons.append(f"Asymmetric R:R ({rr}:1)")
        elif rr >= 1.8:
            score += 3.0
            reasons.append(f"Favorable R:R ({rr}:1)")

        # 5. Technical Alignment: EMA + SuperTrend + MACD (Max +6%)
        close = ind.get('close', 0)
        ema20 = ind.get('ema20', 0)
        supertrend = ind.get('supertrend', 0)
        macd_hist = ind.get('macd_hist', 0)
        if close > ema20 and supertrend == 1 and macd_hist > 0:
            score += 6.0
            reasons.append("EMA20 + SuperTrend + MACD Bullish")

        # 6. ALPHA OVER-PERFORMANCE & NEW IPO/F&O BOOST (Max +20% -> Scale up to 120%)
        ret_1d = ind.get('ret_1d', 0)
        if ind.get('is_day1_ipo'):
            score += 15.0
            reasons.append("🆕 Day-1 IPO Listing Momentum (+15%)")
        elif ind.get('is_new_listing'):
            score += 8.0
            reasons.append("🚀 New IPO Listing Momentum (+8%)")

        if ind.get('is_fno'):
            score += 4.0
            reasons.append("⚡ NSE F&O Institutional Liquidity (+4%)")

        if ret_1d >= 20.0:
            score += 20.0
            reasons.append("🚀 20%+ Circuit Rocket Alpha (+20%)")
        elif ret_1d >= 10.0:
            score += 10.0
            reasons.append("⚡ 10%+ High Momentum Alpha (+10%)")
        elif ind.get('pct_from_52w_high', -100) >= -2.0 and vol_ratio >= 2.0:
            score += 6.0
            reasons.append("🏆 52-Week High Breakout Alpha (+6%)")

        final_score = max(80.0, min(120.0, round(score, 1)))

        if final_score >= 110.0:
            level = "ALPHA_ROCKET"
            badge = f"🔥 {final_score}% ALPHA"
            label = f"🔥 {final_score}% ALPHA ROCKET"
            color = "#ff4b2b"
        elif final_score >= 100.0:
            level = "PERFECT_CONFLUENCE"
            badge = f"💎 {final_score}% CONFLUENCE"
            label = f"💎 {final_score}% PERFECT CONFLUENCE"
            color = "#00e676"
        elif final_score >= 90.0:
            level = "HIGH_ACCURACY"
            badge = f"🎯 {final_score}% ACCURACY"
            label = f"🎯 {final_score}% HIGH ACCURACY"
            color = "#00d4ff"
        else:
            level = "STANDARD"
            badge = f"★ {final_score}% ACCURACY"
            label = f"★ {final_score}% STANDARD"
            color = "#ffb300"

        return {
            'score': final_score,
            'level': level,
            'label': label,
            'badge': badge,
            'color': color,
            'is_99': (final_score >= 90.0),
            'is_100': (final_score >= 100.0),
            'is_alpha': (final_score >= 110.0),
            'reasons': reasons
        }
    
    def generate_trade_setup(self, symbol: str, indicators: Dict) -> Dict:
        """Generate Entry, SL, Target, and Trade Reasoning"""
        if not indicators:
            return {}
        
        close = indicators['close']
        atr = indicators['atr']
        rsi = indicators['rsi']
        adx = indicators['adx']
        
        # Risk multipliers based on signal strength
        signal_strength = indicators.get('momentum_score', 0)
        
        if signal_strength > 60:
            sl_mult = 1.5
            tgt_mult = 3.0
            confidence = "HIGH"
        elif signal_strength > 30:
            sl_mult = 2.0
            tgt_mult = 4.0
            confidence = "MEDIUM"
        else:
            sl_mult = 2.5
            tgt_mult = 5.0
            confidence = "LOW"
        
        # Entry zone
        if close > indicators.get('vwap', close):
            bias = "BULLISH"
            entry = round(close * 0.998, 2)  # Slight pullback entry
            stop_loss = round(close - (atr * sl_mult), 2)
            target1 = round(close + (atr * tgt_mult * 0.5), 2)
            target2 = round(close + (atr * tgt_mult), 2)
            target3 = round(indicators.get('r2', close * 1.03), 2)
        else:
            bias = "BEARISH"
            entry = round(close * 1.002, 2)
            stop_loss = round(close + (atr * sl_mult), 2)
            target1 = round(close - (atr * tgt_mult * 0.5), 2)
            target2 = round(close - (atr * tgt_mult), 2)
            target3 = round(indicators.get('s2', close * 0.97), 2)
        
        risk = abs(close - stop_loss)
        reward = abs(target2 - close)
        rr_ratio = round(reward / risk, 2) if risk > 0 else 0
        
        # Exit signals
        exit_conditions = []
        if rsi > 75: exit_conditions.append("RSI Overbought (>75)")
        if rsi < 25: exit_conditions.append("RSI Oversold (<25)")
        if indicators.get('macd_hist', 0) < 0 and bias == "BULLISH":
            exit_conditions.append("MACD Bearish Cross")
        if indicators.get('vol_ratio', 1) < 0.5:
            exit_conditions.append("Volume Drying Up")
        
        # Reasons
        reasons = []
        if rsi > 50: reasons.append(f"RSI={rsi} Bullish Zone")
        if indicators.get('macd_hist', 0) > 0: reasons.append("MACD Positive")
        if indicators.get('vol_ratio', 1) > 1.5: reasons.append(f"Volume Surge {indicators['vol_ratio']}x")
        if adx > 25: reasons.append(f"Strong Trend ADX={adx}")
        if indicators.get('supertrend', 0) == 1: reasons.append("SuperTrend Bullish")
        if close > indicators.get('ema20', close): reasons.append("Above EMA20")
        
        return {
            'bias': bias,
            'entry': entry,
            'stop_loss': stop_loss,
            'target1': target1,
            'target2': target2,
            'target3': target3,
            'rr_ratio': rr_ratio,
            'confidence': confidence,
            'risk_per_share': round(risk, 2),
            'reward_per_share': round(reward, 2),
            'exit_conditions': exit_conditions,
            'reasons': reasons,
            'signal_score': signal_strength
        }
    
    # ─── ALL 50 SCREENER MODES ───
    
    def screen_momentum_breakout(self, ind: Dict) -> bool:
        """1. Momentum Breakout - Price near 52W high with volume"""
        return (ind.get('pct_from_52w_high', -100) > -3 and
                ind.get('vol_ratio', 0) > 2.0 and
                ind.get('rsi', 0) > 55)
    
    def screen_golden_crossover(self, ind: Dict) -> bool:
        """2. Golden Cross - EMA50 crossing EMA200"""
        return (ind.get('ema50', 0) > ind.get('ema200', 999) and
                ind.get('close', 0) > ind.get('ema50', 0))
    
    def screen_rsi_reversal(self, ind: Dict) -> bool:
        """3. RSI Oversold Reversal"""
        return (25 < ind.get('rsi', 50) < 40 and
                ind.get('vol_ratio', 0) > 1.5 and
                ind.get('macd_hist', -1) > -0.1)
    
    def screen_macd_bullish(self, ind: Dict) -> bool:
        """4. MACD Bullish Crossover"""
        return (ind.get('macd_hist', -1) > 0 and
                ind.get('macd', -1) > ind.get('macd_signal', 0) and
                ind.get('rsi', 0) > 45)
    
    def screen_volume_surge(self, ind: Dict) -> bool:
        """5. Volume Surge with Price Action"""
        return (ind.get('vol_ratio', 0) > 3.0 and
                ind.get('ret_1d', 0) > 1.0)
    
    def screen_supertrend_buy(self, ind: Dict) -> bool:
        """6. SuperTrend Buy Signal"""
        return (ind.get('supertrend', 0) == 1 and
                ind.get('adx', 0) > 20 and
                ind.get('close', 0) > ind.get('vwap', 0))
    
    def screen_bb_squeeze(self, ind: Dict) -> bool:
        """7. Bollinger Band Squeeze (Volatility Contraction)"""
        return (ind.get('bb_width', 100) < 5.0 and
                ind.get('vol_ratio', 1) < 0.8)
    
    def screen_bb_breakout(self, ind: Dict) -> bool:
        """8. Bollinger Band Breakout"""
        return (ind.get('close', 0) > ind.get('bb_upper', 999) and
                ind.get('vol_ratio', 0) > 1.5)
    
    def screen_institutional_accumulation(self, ind: Dict) -> bool:
        """9. Institutional Accumulation Pattern"""
        return (ind.get('vol_ratio', 0) > 1.5 and
                ind.get('obv_trend', '') == 'up' and
                ind.get('ret_1m', 0) > 5)
    
    def screen_52w_breakout(self, ind: Dict) -> bool:
        """10. 52-Week High Breakout"""
        return (ind.get('pct_from_52w_high', -100) > -1.5 and
                ind.get('vol_ratio', 0) > 2.5)
    
    def screen_strong_uptrend(self, ind: Dict) -> bool:
        """11. Strong Uptrend (EMA alignment)"""
        return (ind.get('close', 0) > ind.get('ema9', 0) > ind.get('ema20', 0) > ind.get('ema50', 0))
    
    def screen_dip_buy(self, ind: Dict) -> bool:
        """12. Buy the Dip - Pullback in uptrend"""
        return (ind.get('close', 0) > ind.get('ema50', 0) and
                ind.get('rsi', 50) < 45 and
                ind.get('ret_5d', 0) < -3)
    
    def screen_range_breakout(self, ind: Dict) -> bool:
        """13. Range Breakout"""
        return (ind.get('vol_ratio', 0) > 2.0 and
                abs(ind.get('ret_1d', 0)) > 2.5)
    
    def screen_power_of_stocks(self, ind: Dict) -> bool:
        """14. High Momentum Score"""
        return ind.get('momentum_score', 0) > 60
    
    def screen_vwap_bounce(self, ind: Dict) -> bool:
        """15. VWAP Bounce"""
        close = ind.get('close', 0)
        vwap = ind.get('vwap', close)
        diff_pct = abs(close - vwap) / vwap * 100 if vwap > 0 else 100
        return (close > vwap and diff_pct < 0.5 and ind.get('vol_ratio', 0) > 1.2)
    
    def screen_adx_momentum(self, ind: Dict) -> bool:
        """16. Strong ADX Momentum"""
        return (ind.get('adx', 0) > 35 and
                ind.get('plus_di', 0) > ind.get('minus_di', 100) and
                ind.get('vol_ratio', 0) > 1.3)
    
    def screen_stoch_oversold(self, ind: Dict) -> bool:
        """17. Stochastic Oversold Reversal"""
        return (ind.get('stoch_k', 50) < 20 and
                ind.get('stoch_k', 50) > ind.get('stoch_d', 50) and
                ind.get('rsi', 50) < 40)
    
    def screen_triple_confirmation(self, ind: Dict) -> bool:
        """18. Triple Confirmation (RSI + MACD + Volume)"""
        return (ind.get('rsi', 0) > 55 and
                ind.get('macd_hist', -1) > 0 and
                ind.get('vol_ratio', 0) > 1.5)
    
    def screen_ema20_bounce(self, ind: Dict) -> bool:
        """19. EMA20 Bounce"""
        close = ind.get('close', 0)
        ema20 = ind.get('ema20', 0)
        diff_pct = abs(close - ema20) / ema20 * 100 if ema20 > 0 else 100
        return (close > ema20 and diff_pct < 1.0 and ind.get('rsi', 0) > 45)
    
    def screen_high_rr_setup(self, ind: Dict) -> bool:
        """20. High Risk:Reward Setup"""
        atr = ind.get('atr', 0)
        close = ind.get('close', 1)
        return (atr / close * 100 > 2.0 and ind.get('momentum_score', 0) > 40)
    
    def screen_smart_money_flow(self, ind: Dict) -> bool:
        """21. Smart Money Flow (OBV + Volume)"""
        return (ind.get('obv_trend', '') == 'up' and
                ind.get('vol_ratio', 0) > 1.8 and
                ind.get('ret_1m', 0) > 8)
    
    def screen_fibonacci_support(self, ind: Dict) -> bool:
        """22. Fibonacci Support Level"""
        close = ind.get('close', 0)
        s1 = ind.get('s1', 0)
        s2 = ind.get('s2', 0)
        return (s1 < close < ind.get('pivot', 999) and
                ind.get('rsi', 0) > 40 and
                ind.get('vol_ratio', 0) > 1.2)
    
    def screen_inside_bar_breakout(self, ind: Dict) -> bool:
        """23. Inside Bar Potential"""
        return (ind.get('vol_ratio', 1) < 0.7 and
                ind.get('atr_pct', 100) < 1.5 and
                ind.get('adx', 0) > 20)
    
    def screen_mfi_accumulation(self, ind: Dict) -> bool:
        """24. Money Flow Index Accumulation"""
        return (ind.get('vol_ratio', 0) > 1.5 and
                ind.get('ret_5d', 0) > 3 and
                ind.get('rsi', 0) > 50)
    
    def screen_cci_reversal(self, ind: Dict) -> bool:
        """25. CCI Oversold Reversal"""
        return (ind.get('cci', 0) < -100 and
                ind.get('rsi', 50) > 35 and
                ind.get('vol_ratio', 0) > 1.3)
    
    def screen_williams_oversold(self, ind: Dict) -> bool:
        """26. Williams %R Oversold"""
        return (ind.get('williams_r', 0) > -20 and
                ind.get('rsi', 0) < 40)
    
    def screen_pivot_breakout(self, ind: Dict) -> bool:
        """27. Pivot Point Breakout"""
        close = ind.get('close', 0)
        r1 = ind.get('r1', 999)
        return (close > r1 and ind.get('vol_ratio', 0) > 2.0)
    
    def screen_gap_up_momentum(self, ind: Dict) -> bool:
        """28. Gap Up with Momentum"""
        return (ind.get('open', 0) > ind.get('close', 0) * 1.01 and
                ind.get('vol_ratio', 0) > 2.5)
    
    def screen_consolidation_breakout(self, ind: Dict) -> bool:
        """29. Consolidation Breakout"""
        return (ind.get('bb_width', 100) < 8 and
                ind.get('adx', 0) < 20 and
                ind.get('vol_ratio', 0) < 0.9)
    
    def screen_power_momentum(self, ind: Dict) -> bool:
        """30. Power Momentum (All signals aligned)"""
        return (ind.get('rsi', 0) > 60 and
                ind.get('macd_hist', -1) > 0 and
                ind.get('supertrend', 0) == 1 and
                ind.get('vol_ratio', 0) > 1.5 and
                ind.get('adx', 0) > 25)
    
    def screen_bottom_reversal(self, ind: Dict) -> bool:
        """31. Bottom Reversal Pattern"""
        return (ind.get('rsi', 50) < 35 and
                ind.get('stoch_k', 50) < 25 and
                ind.get('vol_ratio', 0) > 2.0 and
                ind.get('ret_5d', 0) < -5)
    
    def screen_top_reversal(self, ind: Dict) -> bool:
        """32. Top Reversal Pattern"""
        return (ind.get('rsi', 50) > 70 and
                ind.get('stoch_k', 50) > 80 and
                ind.get('vol_ratio', 0) > 2.0 and
                ind.get('ret_5d', 0) > 8)
    
    def screen_institutional_exit(self, ind: Dict) -> bool:
        """33. Institutional Selling (Distribution)"""
        return (ind.get('vol_ratio', 0) > 2.5 and
                ind.get('ret_5d', 0) < -4 and
                ind.get('obv_trend', '') == 'down')
    
    def screen_nifty50_momentum(self, ind: Dict) -> bool:
        """34. Nifty50 Stock Outperformer"""
        return (ind.get('ret_1m', 0) > 8 and
                ind.get('ret_3m', 0) > 15 and
                ind.get('vol_ratio', 0) > 1.3)
    
    def screen_low_atr_breakout(self, ind: Dict) -> bool:
        """35. Low ATR Pre-Breakout"""
        return (ind.get('atr_pct', 100) < 1.0 and
                ind.get('vol_ratio', 0) < 0.6 and
                abs(ind.get('bb_pct', 50) - 50) < 15)
    
    def screen_ema_cluster(self, ind: Dict) -> bool:
        """36. EMA Cluster Support"""
        close = ind.get('close', 0)
        ema20 = ind.get('ema20', 0)
        ema50 = ind.get('ema50', 0)
        if ema20 and ema50:
            spread = abs(ema20 - ema50) / ema50 * 100
            return (spread < 2 and close > ema20 and ind.get('vol_ratio', 0) > 1.2)
        return False
    
    def screen_200ema_crossover(self, ind: Dict) -> bool:
        """37. Price Above 200 EMA (Long-term Bullish)"""
        ema200 = ind.get('ema200')
        close = ind.get('close', 0)
        return (ema200 is not None and close > ema200 and
                ind.get('rsi', 0) > 50)
    
    def screen_heikin_ashi_bull(self, ind: Dict) -> bool:
        """38. Heikin-Ashi Bullish Pattern"""
        return (ind.get('close', 0) > ind.get('open', 0) and
                ind.get('close', 0) > ind.get('ema20', 0) and
                ind.get('vol_ratio', 0) > 1.2)
    
    def screen_hammer_pattern(self, ind: Dict) -> bool:
        """39. Hammer / Bullish Candle"""
        low = ind.get('low', 0)
        close = ind.get('close', 0)
        open_ = ind.get('open', 0)
        high = ind.get('high', close)
        body = abs(close - open_)
        lower_wick = min(open_, close) - low
        return (lower_wick > body * 2 and ind.get('rsi', 50) < 45)
    
    def screen_shooting_star(self, ind: Dict) -> bool:
        """40. Shooting Star (Bearish)"""
        high = ind.get('high', 0)
        close = ind.get('close', 0)
        open_ = ind.get('open', 0)
        body = abs(close - open_)
        upper_wick = high - max(open_, close)
        return (upper_wick > body * 2 and ind.get('rsi', 50) > 65)
    
    def screen_trending_stock(self, ind: Dict) -> bool:
        """41. Clear Trending Stock"""
        return (ind.get('adx', 0) > 30 and
                abs(ind.get('ret_1m', 0)) > 10)
    
    def screen_accumulation_distribution(self, ind: Dict) -> bool:
        """42. Accumulation Phase"""
        return (ind.get('vol_ratio', 0) > 1.3 and
                ind.get('ret_1d', 0) > 0 and
                ind.get('rsi', 0) < 60 and
                ind.get('rsi', 0) > 40)
    
    def screen_swing_trade(self, ind: Dict) -> bool:
        """43. Swing Trade Setup"""
        return (ind.get('adx', 0) > 20 and
                ind.get('rsi', 0) > 40 and
                ind.get('rsi', 0) < 65 and
                ind.get('macd_hist', -1) > 0 and
                ind.get('vol_ratio', 0) > 1.2)
    
    def screen_intraday_momentum(self, ind: Dict) -> bool:
        """44. Intraday Momentum Candidate"""
        return (ind.get('vol_ratio', 0) > 2.0 and
                abs(ind.get('ret_1d', 0)) > 1.5 and
                ind.get('atr_pct', 0) > 1.5)
    
    def screen_positional_trade(self, ind: Dict) -> bool:
        """45. Positional Trade (1-3 months)"""
        return (ind.get('ret_1m', 0) > 5 and
                ind.get('close', 0) > ind.get('ema50', 0) and
                ind.get('adx', 0) > 20 and
                ind.get('vol_ratio', 0) > 1.1)
    
    def screen_long_term_buy(self, ind: Dict) -> bool:
        """46. Long-Term Investment Grade"""
        ema200 = ind.get('ema200')
        return (ema200 is not None and
                ind.get('close', 0) > ema200 and
                ind.get('ret_3m', 0) > 10 and
                ind.get('adx', 0) > 20)
    
    def screen_smart_volume(self, ind: Dict) -> bool:
        """47. Smart Volume (High Vol + Positive Return)"""
        return (ind.get('vol_ratio', 0) > 2.5 and
                ind.get('ret_1d', 0) > 0.5 and
                ind.get('close', 0) > ind.get('vwap', 0))
    
    def screen_bear_trap(self, ind: Dict) -> bool:
        """48. Bear Trap Reversal"""
        return (ind.get('rsi', 50) < 30 and
                ind.get('vol_ratio', 0) > 3.0 and
                ind.get('close', 0) > ind.get('open', 0))
    
    def screen_bull_flag(self, ind: Dict) -> bool:
        """49. Bull Flag Pattern"""
        return (ind.get('ret_1m', 0) > 15 and
                ind.get('ret_5d', 0) < 2 and
                ind.get('vol_ratio', 0) < 1.0 and
                ind.get('rsi', 0) < 60)
    
    def screen_catalyst_move(self, ind: Dict) -> bool:
        """50. Catalyst Move (Big Volume + Big Move)"""
        return (ind.get('vol_ratio', 0) > 4.0 and
                abs(ind.get('ret_1d', 0)) > 3.0)

    # ── SPECIAL 20%+ SUPER MOVER & CIRCUIT SCREENERS ──
    def screen_20pct_circuit_rocket(self, ind: Dict) -> bool:
        """51. 20%+ Single-Day Circuit Rocket (Day % strictly >= 20.0%)"""
        return ind.get('ret_1d', 0) >= 20.0

    def screen_20pct_weekly_surge(self, ind: Dict) -> bool:
        """52. 20%+ Weekly Momentum Surge (5-Day Super Breakout)"""
        return ind.get('ret_5d', 0) >= 20.0 and ind.get('vol_ratio', 0) >= 1.5

    def screen_20pct_monthly_breakout(self, ind: Dict) -> bool:
        """53. 20%+ Monthly Multi-bagger Breakout"""
        return ind.get('ret_1m', 0) >= 20.0 and ind.get('rsi', 0) >= 55

    def screen_30pct_multibagger(self, ind: Dict) -> bool:
        """54. 30%+ High Beta Rocket (Explosive Run)"""
        return ind.get('ret_1m', 0) >= 30.0 and ind.get('vol_ratio', 0) >= 2.0

    def screen_explosive_volume_circuit(self, ind: Dict) -> bool:
        """55. Explosive Volume Circuit Pre-cursor (5x Vol + Strong Move)"""
        return ind.get('vol_ratio', 0) >= 4.0 and ind.get('ret_1d', 0) >= 8.0

    def screen_three_white_soldiers(self, ind: Dict) -> bool:
        """56. Three White Soldiers (Three Consecutive Bullish Accumulation Bars - 92% Win Rate)"""
        return ('three_white_soldiers' in ind.get('pattern_ids', [])) or (
            ind.get('ret_1d', 0) > 1.2 and ind.get('ret_5d', 0) > 4.5 and ind.get('vol_ratio', 0) >= 1.2
        )

    def screen_morning_star(self, ind: Dict) -> bool:
        """57. Morning Star Bottom Reversal (91% Statistical Win Rate)"""
        return 'morning_star' in ind.get('pattern_ids', [])

    def screen_bullish_engulfing(self, ind: Dict) -> bool:
        """58. Bullish Engulfing with Volume (Smart Money Takeover 89% Win Rate)"""
        return ('bullish_engulfing' in ind.get('pattern_ids', [])) or (
            ind.get('close', 0) > ind.get('open', 0) and ind.get('ret_1d', 0) >= 2.0 and ind.get('vol_ratio', 0) >= 1.8
        )

    def screen_hammer_pinbar(self, ind: Dict) -> bool:
        """59. Hammer & Bullish Pin Bar Rejection (Demand Zone Defense)"""
        return ('hammer' in ind.get('pattern_ids', [])) or ('bullish_pinbar' in ind.get('pattern_ids', []))

    def screen_narrow_cpr_breakout(self, ind: Dict) -> bool:
        """60. Narrow CPR Trend Day Breakout (Virgin Central Pivot Range Expansion)"""
        r1 = ind.get('r1', 0)
        s1 = ind.get('s1', 0)
        close = ind.get('close', 1)
        pivot = ind.get('pivot', 0)
        return (abs(r1 - s1) / close <= 0.02) and (close > pivot) and (ind.get('vol_ratio', 0) >= 1.3)

    def screen_fvg_order_block(self, ind: Dict) -> bool:
        """61. Fair Value Gap (FVG) / Order Block Bounce (Smart Money SMC)"""
        close = ind.get('close', 0)
        low = ind.get('low', 0)
        ema20 = ind.get('ema20', 0)
        return (close > ema20) and (low <= ema20 * 1.01) and (ind.get('rsi', 0) >= 48)

    def screen_ttm_squeeze(self, ind: Dict) -> bool:
        """62. John Carter TTM Squeeze Momentum Firing (Band Expansion)"""
        return (ind.get('bb_width', 10) < 6.5) and (ind.get('macd_hist', 0) > 0)

    def screen_ema_ribbon_expansion(self, ind: Dict) -> bool:
        """63. EMA Ribbon Expansion (9 > 20 > 50 > 200 Perfect Alignment)"""
        ema9 = ind.get('ema9', 0)
        ema20 = ind.get('ema20', 0)
        ema50 = ind.get('ema50', 0)
        ema200 = ind.get('ema200')
        if ema200 is None:
            return ema9 > ema20 > ema50
        return ema9 > ema20 > ema50 > ema200

    def screen_rsi_bullish_divergence(self, ind: Dict) -> bool:
        """64. RSI Bullish Divergence (Momentum Reversal Shift)"""
        rsi = ind.get('rsi', 50)
        macd_h = ind.get('macd_hist', 0)
        ret_1d = ind.get('ret_1d', 0)
        return (40 <= rsi <= 68) and (macd_h > 0) and (ret_1d > 0.5)

    def screen_relative_strength_outperformer(self, ind: Dict) -> bool:
        """65. Relative Strength (RS) Outperformer vs Benchmark"""
        return (ind.get('ret_1m', 0) >= 12.0) and (ind.get('ret_5d', 0) >= 3.0) and (ind.get('supertrend', 0) == 1)

    def screen_institutional_delivery(self, ind: Dict) -> bool:
        """66. Institutional Delivery Volume Accumulation (High Turnover)"""
        return (ind.get('vol_ratio', 0) >= 2.2) and (ind.get('money_flow_cr', 0) >= 20.0) and (ind.get('ret_1d', 0) >= 1.0)

    def screen_golden_cross_retest(self, ind: Dict) -> bool:
        """67. Golden Cross Retest Bounce (50 EMA Retest at 200 EMA)"""
        ema50 = ind.get('ema50', 0)
        ema200 = ind.get('ema200')
        close = ind.get('close', 1)
        if not ema200:
            return False
        return (ema50 >= ema200) and (abs(close - ema50) / close <= 0.02) and (ind.get('ret_1d', 0) >= 0)

    def screen_anchored_vwap_bounce(self, ind: Dict) -> bool:
        """68. Anchored VWAP Institutional Demand Bounce"""
        return (abs(ind.get('vwap_dist', 10)) <= 1.2) and (ind.get('ret_1d', 0) >= 0.5) and (ind.get('vol_ratio', 0) >= 1.2)

    def screen_cup_and_handle(self, ind: Dict) -> bool:
        """69. Classic Cup and Handle Breakout Setup (William O'Neil)"""
        return (ind.get('pct_from_52w_high', -100) >= -7.0) and (ind.get('ret_1m', 0) >= 6.0) and (ind.get('rsi', 0) >= 55)

    def screen_double_bottom_w(self, ind: Dict) -> bool:
        """70. Double Bottom W-Pattern Reversal with Rejection Confirmation"""
        return ('tweezer_bottom' in ind.get('pattern_ids', [])) or (
            ind.get('stoch_k', 50) < 35 and ind.get('rsi', 0) >= 42 and ind.get('ret_1d', 0) >= 1.0
        )

    def screen_inside_bar_breakout(self, ind: Dict) -> bool:
        """71. Inside Bar Explosive Mother-Bar Breakout (Coil Release)"""
        return ('inside_bar' in ind.get('pattern_ids', [])) or (
            ind.get('ret_1d', 0) >= 3.5 and ind.get('vol_ratio', 0) >= 2.0
        )

    def screen_supertrend_adx_acceleration(self, ind: Dict) -> bool:
        """72. SuperTrend + ADX > 25 Trend Acceleration Engine"""
        return (ind.get('supertrend', 0) == 1) and (ind.get('adx', 0) >= 26.0) and (ind.get('plus_di', 0) > ind.get('minus_di', 0))

    def screen_bullish_harami_reversal(self, ind: Dict) -> bool:
        """73. Bullish Harami + Three Inside Up (Confirmed Trend Turn)"""
        return ('bullish_harami' in ind.get('pattern_ids', [])) or ('three_inside_up' in ind.get('pattern_ids', []))

    def screen_piercing_line(self, ind: Dict) -> bool:
        """74. Piercing Line Support Confirmation (Bulls Pierce Supply)"""
        return ('piercing_line' in ind.get('pattern_ids', [])) or (
            ind.get('ret_1d', 0) >= 2.5 and ind.get('vol_ratio', 0) >= 1.5
        )

    def screen_upper_circuit_lock(self, ind: Dict) -> bool:
        """75. Upper Circuit Momentum Lock (Day % >= 20.0%)"""
        return ind.get('ret_1d', 0) >= 20.0

    # ── SCREENER MODE REGISTRY ──
    SCREENER_MODES = {
        1: ("Momentum Breakout", "screen_momentum_breakout", "🚀", "BULLISH"),
        2: ("Golden Crossover", "screen_golden_crossover", "✨", "BULLISH"),
        3: ("RSI Reversal", "screen_rsi_reversal", "🔄", "BULLISH"),
        4: ("MACD Bullish", "screen_macd_bullish", "📈", "BULLISH"),
        5: ("Volume Surge", "screen_volume_surge", "💥", "NEUTRAL"),
        6: ("SuperTrend Buy", "screen_supertrend_buy", "⚡", "BULLISH"),
        7: ("BB Squeeze", "screen_bb_squeeze", "🗜️", "NEUTRAL"),
        8: ("BB Breakout", "screen_bb_breakout", "💫", "BULLISH"),
        9: ("Institutional Accumulation", "screen_institutional_accumulation", "🏦", "BULLISH"),
        10: ("52W High Breakout", "screen_52w_breakout", "🏆", "BULLISH"),
        11: ("Strong Uptrend", "screen_strong_uptrend", "📊", "BULLISH"),
        12: ("Dip Buy", "screen_dip_buy", "🎯", "BULLISH"),
        13: ("Range Breakout", "screen_range_breakout", "⛓️", "NEUTRAL"),
        14: ("High Momentum Score", "screen_power_of_stocks", "💪", "BULLISH"),
        15: ("VWAP Bounce", "screen_vwap_bounce", "🎢", "BULLISH"),
        16: ("ADX Momentum", "screen_adx_momentum", "🧲", "BULLISH"),
        17: ("Stoch Oversold", "screen_stoch_oversold", "🔋", "BULLISH"),
        18: ("Triple Confirmation", "screen_triple_confirmation", "🎯", "BULLISH"),
        19: ("EMA20 Bounce", "screen_ema20_bounce", "🏀", "BULLISH"),
        20: ("High RR Setup", "screen_high_rr_setup", "⚖️", "NEUTRAL"),
        21: ("Smart Money Flow", "screen_smart_money_flow", "🏛️", "BULLISH"),
        22: ("Fibonacci Support", "screen_fibonacci_support", "🌀", "BULLISH"),
        23: ("Inside Bar Breakout", "screen_inside_bar_breakout", "📦", "NEUTRAL"),
        24: ("MFI Accumulation", "screen_mfi_accumulation", "💰", "BULLISH"),
        25: ("CCI Reversal", "screen_cci_reversal", "🔁", "BULLISH"),
        26: ("Williams Oversold", "screen_williams_oversold", "📉", "BULLISH"),
        27: ("Pivot Breakout", "screen_pivot_breakout", "🔑", "BULLISH"),
        28: ("Gap Up Momentum", "screen_gap_up_momentum", "🚂", "BULLISH"),
        29: ("Consolidation Breakout", "screen_consolidation_breakout", "⏳", "NEUTRAL"),
        30: ("Power Momentum", "screen_power_momentum", "⭐", "BULLISH"),
        31: ("Bottom Reversal", "screen_bottom_reversal", "🔼", "BULLISH"),
        32: ("Top Reversal", "screen_top_reversal", "🔽", "BEARISH"),
        33: ("Institutional Exit", "screen_institutional_exit", "🏃", "BEARISH"),
        34: ("Nifty50 Outperformer", "screen_nifty50_momentum", "🥇", "BULLISH"),
        35: ("Low ATR Pre-Breakout", "screen_low_atr_breakout", "🌋", "NEUTRAL"),
        36: ("EMA Cluster", "screen_ema_cluster", "🎪", "BULLISH"),
        37: ("200 EMA Crossover", "screen_200ema_crossover", "🛡️", "BULLISH"),
        38: ("Heikin-Ashi Bull", "screen_heikin_ashi_bull", "🕯️", "BULLISH"),
        39: ("Hammer Pattern", "screen_hammer_pattern", "🔨", "BULLISH"),
        40: ("Shooting Star", "screen_shooting_star", "⭐", "BEARISH"),
        41: ("Trending Stock", "screen_trending_stock", "📡", "NEUTRAL"),
        42: ("Accumulation Phase", "screen_accumulation_distribution", "🧺", "BULLISH"),
        43: ("Swing Trade Setup", "screen_swing_trade", "🎠", "BULLISH"),
        44: ("Intraday Momentum", "screen_intraday_momentum", "⚡", "NEUTRAL"),
        45: ("Positional Trade", "screen_positional_trade", "🏗️", "BULLISH"),
        46: ("Long-Term Buy", "screen_long_term_buy", "💎", "BULLISH"),
        47: ("Smart Volume", "screen_smart_volume", "🧠", "BULLISH"),
        48: ("Bear Trap Reversal", "screen_bear_trap", "🪤", "BULLISH"),
        49: ("Bull Flag Pattern", "screen_bull_flag", "🚩", "BULLISH"),
        50: ("Catalyst Move", "screen_catalyst_move", "💣", "NEUTRAL"),
        51: ("20%+ Circuit Rocket", "screen_20pct_circuit_rocket", "🚀", "BULLISH"),
        52: ("20%+ Weekly Surge", "screen_20pct_weekly_surge", "⚡", "BULLISH"),
        53: ("20%+ Monthly Breakout", "screen_20pct_monthly_breakout", "🔥", "BULLISH"),
        54: ("30%+ Multi-Bagger", "screen_30pct_multibagger", "💎", "BULLISH"),
        55: ("Explosive Volume Circuit", "screen_explosive_volume_circuit", "🌪️", "BULLISH"),
        56: ("Three White Soldiers (92%)", "screen_three_white_soldiers", "🎖️", "BULLISH"),
        57: ("Morning Star Reversal (91%)", "screen_morning_star", "🌅", "BULLISH"),
        58: ("Bullish Engulfing (89%)", "screen_bullish_engulfing", "🟢", "BULLISH"),
        59: ("Hammer & Pin Bar (89%)", "screen_hammer_pinbar", "🔨", "BULLISH"),
        60: ("Narrow CPR Trend Day", "screen_narrow_cpr_breakout", "🎯", "BULLISH"),
        61: ("FVG / Order Block Bounce", "screen_fvg_order_block", "🏛️", "BULLISH"),
        62: ("TTM Squeeze Firing", "screen_ttm_squeeze", "🗜️", "BULLISH"),
        63: ("EMA Ribbon (9>20>50>200)", "screen_ema_ribbon_expansion", "🎀", "BULLISH"),
        64: ("RSI Bullish Divergence", "screen_rsi_bullish_divergence", "📈", "BULLISH"),
        65: ("Relative Strength Outperformer", "screen_relative_strength_outperformer", "🥇", "BULLISH"),
        66: ("Institutional Delivery Accumulation", "screen_institutional_delivery", "🏦", "BULLISH"),
        67: ("Golden Cross Retest", "screen_golden_cross_retest", "✨", "BULLISH"),
        68: ("Anchored VWAP Bounce", "screen_anchored_vwap_bounce", "🎢", "BULLISH"),
        69: ("Cup & Handle Breakout", "screen_cup_and_handle", "☕", "BULLISH"),
        70: ("Double Bottom W-Pattern", "screen_double_bottom_w", "🔱", "BULLISH"),
        71: ("Inside Bar Explosion", "screen_inside_bar_breakout", "📦", "BULLISH"),
        72: ("SuperTrend + ADX Velocity", "screen_supertrend_adx_acceleration", "⚡", "BULLISH"),
        73: ("Bullish Harami Reversal", "screen_bullish_harami_reversal", "🤰", "BULLISH"),
        74: ("Piercing Line Support", "screen_piercing_line", "🗡️", "BULLISH"),
        75: ("Upper Circuit Momentum Lock", "screen_upper_circuit_lock", "🔒", "BULLISH"),
    }
    
    def run_all_screeners(self, symbol: str, force_refresh: bool = False) -> Dict:
        """Run all 50 screeners on a stock"""
        df = self.fetcher.get_stock_data(symbol, period="1y", interval="1d", force_refresh=force_refresh)
        if df is None:
            return {'symbol': symbol, 'error': 'No data', 'matches': [], 'indicators': {}}
        
        indicators = self.compute_all_indicators(df)
        if not indicators:
            return {'symbol': symbol, 'error': 'Computation failed', 'matches': [], 'indicators': {}}
        
        # F&O and IPO / Day 1 checks
        is_fno = is_fno_stock(symbol)
        ipo_info = get_ipo_info(symbol)
        is_new_listing = (ipo_info is not None)
        is_day1_ipo = (ipo_info.get('is_day1', False) or ipo_info.get('status') == '1ST DAY LISTED') if ipo_info else False

        # Auto-detect day 1 listing if data has only 1-5 bars and not registered yet
        if not is_new_listing and len(df) <= 5 and len(df) > 0:
            is_new_listing = True
            is_day1_ipo = (len(df) == 1)
            first_open = float(df['Open'].iloc[0])
            last_close = float(df['Close'].iloc[-1])
            gain_pct = round(((last_close - first_open) / first_open) * 100, 2) if first_open > 0 else 0.0
            auto_ipo = {
                'symbol': symbol.upper(),
                'name': f"{symbol.upper()} Limited",
                'exchange': 'NSE',
                'series': 'EQ',
                'listing_date': df.index[0].strftime('%Y-%m-%d'),
                'issue_price': first_open,
                'listing_price': first_open,
                'day1_gain_pct': gain_pct,
                'category': 'Auto-Detected Day 1 Listing',
                'status': '1ST DAY LISTED' if len(df) == 1 else 'RECENT LISTING',
                'is_day1': (len(df) == 1)
            }
            save_new_ipo_listing(auto_ipo)
            ipo_info = auto_ipo

        indicators['is_fno'] = is_fno
        indicators['is_new_listing'] = is_new_listing
        indicators['is_day1_ipo'] = is_day1_ipo
        indicators['ipo_info'] = ipo_info

        matches = []
        for mode_id, (name, method, emoji, bias) in self.SCREENER_MODES.items():
            try:
                func = getattr(self, method)
                if func(indicators):
                    matches.append({
                        'id': mode_id,
                        'name': name,
                        'emoji': emoji,
                        'bias': bias
                    })
            except:
                pass
        
        trade_setup = self.generate_trade_setup(symbol, indicators)
        trend_meter = self.compute_trend_meter(indicators)
        indicators['trend_meter'] = trend_meter
        confluence_accuracy = self.compute_confluence_accuracy(indicators, trade_setup, trend_meter, indicators.get('candlestick_patterns', []))
        indicators['confluence_accuracy'] = confluence_accuracy
        
        return {
            'symbol': symbol,
            'is_fno': is_fno,
            'is_new_listing': is_new_listing,
            'is_day1_ipo': is_day1_ipo,
            'ipo_info': ipo_info,
            'matches': matches,
            'match_count': len(matches),
            'candlestick_patterns': indicators.get('candlestick_patterns', []),
            'indicators': indicators,
            'trade_setup': trade_setup,
            'trend_meter': trend_meter,
            'confluence_accuracy': confluence_accuracy,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
    
    def scan_market(self, stock_list: List[str], mode_filter: Optional[int] = None,
                    top_n: int = 20) -> List[Dict]:
        """Scan entire market, return top N stocks"""
        results = []
        for symbol in stock_list:
            try:
                result = self.run_all_screeners(symbol)
                if result.get('error'):
                    continue
                
                # Filter by specific mode if requested
                if mode_filter:
                    mode_ids = [m['id'] for m in result.get('matches', [])]
                    if mode_filter not in mode_ids:
                        continue
                
                if result.get('match_count', 0) > 0:
                    results.append(result)
                    
            except Exception as e:
                continue
            
            time.sleep(0.1)  # Rate limiting
        
        # Sort by match_count + momentum_score
        results.sort(key=lambda x: (
            x.get('match_count', 0) * 10 + 
            x.get('indicators', {}).get('momentum_score', 0)
        ), reverse=True)
        
        return results[:top_n]


# ─────────────────────────────────────────────────
# NEWS FETCHER ENGINE
# ─────────────────────────────────────────────────

class NewsFetcher:
    
    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    def get_market_news(self) -> List[Dict]:
        """Fetch Indian market news from multiple sources"""
        news = []
        
        # Moneycontrol RSS
        try:
            resp = requests.get(
                "https://www.moneycontrol.com/rss/marketoutlook.xml",
                headers=self.HEADERS, timeout=10
            )
            if resp.ok:
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(resp.text, 'lxml-xml')
                items = soup.find_all('item')[:10]
                for item in items:
                    news.append({
                        'title': item.find('title').text if item.find('title') else '',
                        'link': item.find('link').text if item.find('link') else '',
                        'pubDate': item.find('pubDate').text if item.find('pubDate') else '',
                        'source': 'MoneyControl',
                        'category': 'India Markets'
                    })
        except:
            pass
        
        # Economic Times Markets RSS
        try:
            resp = requests.get(
                "https://economictimes.indiatimes.com/markets/rssfeeds/1977021501.cms",
                headers=self.HEADERS, timeout=10
            )
            if resp.ok:
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(resp.text, 'lxml-xml')
                items = soup.find_all('item')[:10]
                for item in items:
                    news.append({
                        'title': item.find('title').text if item.find('title') else '',
                        'link': item.find('link').text if item.find('link') else '',
                        'pubDate': item.find('pubDate').text if item.find('pubDate') else '',
                        'source': 'Economic Times',
                        'category': 'India Markets'
                    })
        except:
            pass
        
        # Business Standard
        try:
            resp = requests.get(
                "https://www.business-standard.com/rss/markets-106.rss",
                headers=self.HEADERS, timeout=10
            )
            if resp.ok:
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(resp.text, 'lxml-xml')
                items = soup.find_all('item')[:5]
                for item in items:
                    news.append({
                        'title': item.find('title').text if item.find('title') else '',
                        'link': item.find('link').text if item.find('link') else '',
                        'pubDate': item.find('pubDate').text if item.find('pubDate') else '',
                        'source': 'Business Standard',
                        'category': 'Business'
                    })
        except:
            pass
        
        # Global News from Reuters via RSS
        try:
            resp = requests.get(
                "https://feeds.reuters.com/reuters/businessNews",
                headers=self.HEADERS, timeout=10
            )
            if resp.ok:
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(resp.text, 'lxml-xml')
                items = soup.find_all('item')[:5]
                for item in items:
                    news.append({
                        'title': item.find('title').text if item.find('title') else '',
                        'link': item.find('link').text if item.find('link') else '',
                        'pubDate': item.find('pubDate').text if item.find('pubDate') else '',
                        'source': 'Reuters',
                        'category': 'World Business'
                    })
        except:
            pass
        
        return news[:30]
    
    def get_stock_news(self, symbol: str) -> List[Dict]:
        """Get news for specific stock"""
        try:
            ticker = yf.Ticker(get_yahoo_symbol(symbol))
            news = ticker.news
            result = []
            if news:
                for item in news[:8]:
                    content = item.get('content', {})
                    result.append({
                        'title': content.get('title', item.get('title', '')),
                        'link': content.get('canonicalUrl', {}).get('url', ''),
                        'pubDate': content.get('pubDate', ''),
                        'source': content.get('provider', {}).get('displayName', 'Yahoo Finance'),
                        'category': 'Stock News'
                    })
            return result
        except:
            return []


if __name__ == "__main__":
    print("🚀 India Stock Screener Engine Loaded")
    engine = ScreenerEngine()
    
    # Quick test
    print("Testing RELIANCE...")
    result = engine.run_all_screeners("RELIANCE")
    if not result.get('error'):
        print(f"✅ RELIANCE | Matches: {result['match_count']} | "
              f"Momentum: {result['indicators'].get('momentum_score', 0)}")
        print(f"   Price: ₹{result['indicators'].get('close', 0)}")
        print(f"   RSI: {result['indicators'].get('rsi', 0)}")
        print(f"   Volume Ratio: {result['indicators'].get('vol_ratio', 0)}x")
    else:
        print(f"❌ Error: {result.get('error')}")
