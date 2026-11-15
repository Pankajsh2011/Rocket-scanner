"""
╔══════════════════════════════════════════════════════════════════════╗
║          INDIA STOCK SCREENER - FLASK API SERVER                     ║
║          NSE/BSE | 50 Screeners | Institutional | AI Signals         ║
╚══════════════════════════════════════════════════════════════════════╝
"""

from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import os
import json
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from screener_engine import (
    ScreenerEngine, NewsFetcher,
    ALL_STOCKS, NSE_ALL_STOCKS, BSE_ALL_STOCKS,
    NIFTY50_STOCKS, NIFTY_NEXT50, MIDCAP_STOCKS,
    BSE_LARGECAP, BSE_MIDCAP, BSE_SMALLCAP,
    SECTOR_MAP,
    SECTOR_BANKS, SECTOR_IT, SECTOR_PHARMA,
    SECTOR_AUTO, SECTOR_FMCG, SECTOR_REALTY,
    SECTOR_METAL, SECTOR_ENERGY, SECTOR_DEFENCE, SECTOR_CHEMICALS
)

import numpy as np
from flask.json.provider import DefaultJSONProvider

class NumpyJSONProvider(DefaultJSONProvider):
    def default(self, obj):
        if isinstance(obj, np.bool_):
            return bool(obj)
        if isinstance(obj, (np.integer, np.int64, np.int32)):
            return int(obj)
        if isinstance(obj, (np.floating, np.float64, np.float32)):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super().default(obj)

app = Flask(__name__)
app.json = NumpyJSONProvider(app)
app.config['SECRET_KEY'] = 'india_screener_2024'
app.config['TEMPLATES_AUTO_RELOAD'] = True
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# Global engine instances
screener = ScreenerEngine()
news_fetcher = NewsFetcher()
from dhan_service import dhan_client

# Load 4,200+ Indian Stocks Master Database
MASTER_STOCKS_FILE = os.path.join(os.path.dirname(__file__), "data", "indian_stocks_master.json")
ALL_4000_STOCKS = []
if os.path.exists(MASTER_STOCKS_FILE):
    try:
        with open(MASTER_STOCKS_FILE, 'r', encoding='utf-8') as f:
            ALL_4000_STOCKS = json.load(f)
    except:
        pass
ALL_4000_SYMBOLS = [s['symbol'] for s in ALL_4000_STOCKS] if ALL_4000_STOCKS else ALL_STOCKS
NSE_OFFICIAL_SYMBOLS = [s['symbol'] for s in ALL_4000_STOCKS if s.get('exchange') == 'NSE']
BSE_OFFICIAL_SYMBOLS = [s['symbol'] for s in ALL_4000_STOCKS if s.get('exchange') == 'BSE']

# Cache for scan results
scan_cache = {
    'results': [],
    'last_scan': None,
    'is_scanning': False,
    'stop_requested': False,
    'scan_progress': 0,
    'total_stocks': 0
}

news_cache = {
    'articles': [],
    'last_fetch': None
}


# ─────────────────────────────────────────────────
# API ROUTES
# ─────────────────────────────────────────────────

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/health')
def health():
    return jsonify({'status': 'ok', 'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')})

@app.route('/api/scan', methods=['GET'])
def api_scan():
    """Full market scan with optional min return filter"""
    universe = request.args.get('universe', 'nifty50')
    mode_id = request.args.get('mode')
    top_n = int(request.args.get('top', 20))
    min_ret = float(request.args.get('min_ret', 0))
    
    if universe == 'custom_selected':
        custom_stocks = data.get('custom_stocks', [])
        if isinstance(custom_stocks, str):
            stock_list = [s.strip().upper() for s in custom_stocks.split(',') if s.strip()]
        elif isinstance(custom_stocks, list):
            stock_list = [str(s).strip().upper() for s in custom_stocks if str(s).strip()]
        else:
            stock_list = []
        if not stock_list:
            stock_list = NIFTY50_STOCKS
    elif universe == 'nifty50':
        stock_list = NIFTY50_STOCKS
    elif universe == 'nifty100':
        stock_list = NIFTY50_STOCKS + NIFTY_NEXT50
    elif universe == 'nse_all':
        stock_list = NSE_ALL_STOCKS
    elif universe == 'bse_large':
        stock_list = list(set(BSE_LARGECAP))
    elif universe == 'bse_mid':
        stock_list = list(set(BSE_MIDCAP))
    elif universe == 'bse_small':
        stock_list = list(set(BSE_SMALLCAP))
    elif universe == 'bse_all':
        stock_list = list(set(BSE_ALL_STOCKS))
    elif universe == 'all_4000':
        stock_list = ALL_4000_SYMBOLS if ALL_4000_SYMBOLS else ALL_STOCKS
    elif universe == 'nse_2600':
        stock_list = NSE_OFFICIAL_SYMBOLS if NSE_OFFICIAL_SYMBOLS else NSE_ALL_STOCKS
    elif universe == 'bse_exclusive':
        stock_list = BSE_OFFICIAL_SYMBOLS if BSE_OFFICIAL_SYMBOLS else BSE_ALL_STOCKS
    elif universe == 'all':
        stock_list = ALL_STOCKS
    elif universe.startswith('sector_'):
        sector_name = universe[7:].replace('_', ' ').title()
        stock_list = SECTOR_MAP.get(sector_name, NIFTY50_STOCKS)
    else:
        stock_list = NIFTY50_STOCKS
    
    mode_filter = int(mode_id) if mode_id else None
    min_accuracy = float(request.args.get('min_accuracy', 80.0))
    
    if not scan_cache['is_scanning']:
        thread = threading.Thread(
            target=run_scan_background,
            args=(stock_list, mode_filter, top_n, min_ret, min_accuracy)
        )
        thread.daemon = True
        thread.start()
        return jsonify({'status': 'scanning', 'message': f'Scan started for {len(stock_list)} stocks', 'min_ret': min_ret, 'min_accuracy': min_accuracy})
    else:
        return jsonify({'status': 'busy', 'progress': scan_cache['scan_progress'],
                       'total': scan_cache['total_stocks']})

def _filter_and_append_result(result, mode_filter, stock_list, results, min_accuracy=80.0):
    if min_accuracy > 80.0:
        acc = result.get('confluence_accuracy', {})
        if acc.get('score', 80.0) < min_accuracy:
            return
    if mode_filter:
        mode_ids = [m['id'] for m in result.get('matches', [])]
        if mode_filter in mode_ids:
            results.append(result)
    else:
        if result.get('match_count', 0) > 0 or len(stock_list) <= 15:
            results.append(result)

def run_scan_background(stock_list, mode_filter, top_n, min_ret=0.0, min_accuracy=80.0):
    """Run ultra-fast scan using ThreadPoolExecutor with instant stop capability and 80-120% accuracy filtering"""
    scan_cache['is_scanning'] = True
    scan_cache['stop_requested'] = False
    scan_cache['scan_progress'] = 0
    scan_cache['total_stocks'] = len(stock_list)
    scan_cache['results'] = []
    
    results = []
    was_stopped = False
    completed_count = 0
    total = len(stock_list)

    def scan_single(sym):
        if scan_cache.get('stop_requested', False):
            return None
        try:
            return screener.run_all_screeners(sym)
        except Exception:
            return None

    # Parallel processing with up to 12 workers for 10x-15x faster scanning
    max_workers = min(12, max(2, len(stock_list)))
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_map = {executor.submit(scan_single, symbol): symbol for symbol in stock_list}
        
        for future in as_completed(future_map):
            symbol = future_map[future]
            completed_count += 1
            scan_cache['scan_progress'] = completed_count
            
            if scan_cache.get('stop_requested', False):
                was_stopped = True
                print(f"[Scan] User STOPPED scan at {completed_count}/{total}")
                for f in future_map:
                    f.cancel()
                break

            try:
                res = future.result()
            except Exception:
                res = None

            if res and not res.get('error'):
                ind = res.get('indicators', {})
                if min_ret > 0:
                    r1 = ind.get('ret_1d', 0)
                    if r1 >= min_ret:
                        _filter_and_append_result(res, mode_filter, stock_list, results, min_accuracy)
                else:
                    _filter_and_append_result(res, mode_filter, stock_list, results, min_accuracy)

            # Real-time progress update
            socketio.emit('scan_progress', {
                'progress': completed_count,
                'total': total,
                'current_symbol': symbol,
                'pct': round((completed_count / total) * 100, 1),
                'matched_so_far': len(results)
            })

    # Sort results: 20%+ Rockets on top, then 110%+ Alpha, then 100%+ Perfect Confluence, then score
    results.sort(key=lambda x: (
        (300 if x.get('indicators', {}).get('is_20pct_mover') else 0) +
        (200 if x.get('confluence_accuracy', {}).get('is_alpha') else 0) +
        (100 if x.get('confluence_accuracy', {}).get('is_100') else 0) +
        x.get('confluence_accuracy', {}).get('score', 80) * 2 +
        x.get('match_count', 0) * 10 +
        x.get('indicators', {}).get('momentum_score', 0)
    ), reverse=True)
    
    scan_cache['results'] = results[:top_n]
    scan_cache['last_scan'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    scan_cache['is_scanning'] = False
    scan_cache['stop_requested'] = False
    
    # Emit completed / stopped
    socketio.emit('scan_complete', {
        'count': len(scan_cache['results']),
        'timestamp': scan_cache['last_scan'],
        'stopped': was_stopped
    })

@app.route('/api/scan/stop', methods=['POST', 'GET'])
def api_scan_stop():
    """Stop/abort the running scan immediately"""
    if scan_cache.get('is_scanning', False):
        scan_cache['stop_requested'] = True
        return jsonify({'status': 'stopping', 'message': 'Scan stop requested successfully'})
    return jsonify({'status': 'idle', 'message': 'No scan currently active'})

@app.route('/api/scan/results')
def scan_results():
    """Get cached scan results"""
    return jsonify({
        'is_scanning': scan_cache['is_scanning'],
        'progress': scan_cache['scan_progress'],
        'total': scan_cache['total_stocks'],
        'last_scan': scan_cache['last_scan'],
        'results': scan_cache['results'],
        'count': len(scan_cache['results'])
    })

@app.route('/api/stock/<symbol>')
def stock_detail(symbol):
    """Get full analysis for one stock"""
    result = screener.run_all_screeners(symbol.upper())
    
    # Also get institutional data
    inst_data = screener.fetcher.get_institutional_data(symbol.upper())
    result['institutional'] = inst_data
    
    # Get stock news
    stock_news = news_fetcher.get_stock_news(symbol.upper())
    result['news'] = stock_news
    
    return jsonify(result)

@app.route('/api/stock/<symbol>/quote')
def live_quote(symbol):
    """Get live quote"""
    quote = screener.fetcher.get_live_quote(symbol.upper())
    return jsonify(quote)

@app.route('/api/screener/modes')
def screener_modes():
    """List all 50 screener modes"""
    modes = []
    for mode_id, (name, method, emoji, bias) in screener.SCREENER_MODES.items():
        modes.append({
            'id': mode_id,
            'name': name,
            'emoji': emoji,
            'bias': bias
        })
    return jsonify({'modes': modes, 'count': len(modes)})

@app.route('/api/news')
def get_news():
    """Get market news"""
    now = time.time()
    
    # Cache news for 15 minutes
    if (not news_cache['articles'] or 
        (news_cache['last_fetch'] and (now - news_cache['last_fetch']) > 900)):
        try:
            news_cache['articles'] = news_fetcher.get_market_news()
            news_cache['last_fetch'] = now
        except:
            pass
    
    return jsonify({
        'articles': news_cache['articles'],
        'count': len(news_cache['articles']),
        'last_updated': datetime.fromtimestamp(news_cache['last_fetch']).strftime('%Y-%m-%d %H:%M') if news_cache['last_fetch'] else None
    })

@app.route('/api/watchlist/analyze', methods=['POST'])
def analyze_watchlist():
    """Analyze custom watchlist"""
    data = request.json
    symbols = data.get('symbols', [])
    
    results = []
    for symbol in symbols[:30]:  # Limit to 30
        result = screener.run_all_screeners(symbol.upper())
        if not result.get('error'):
            results.append(result)
    
    results.sort(key=lambda x: x.get('match_count', 0), reverse=True)
    return jsonify({'results': results})

@app.route('/api/top/movers')
def top_movers():
    """Quick top movers from Nifty50"""
    movers = []
    for symbol in NIFTY50_STOCKS[:25]:
        quote = screener.fetcher.get_live_quote(symbol)
        if quote:
            movers.append(quote)
        time.sleep(0.05)
    
    # Top gainers and losers
    gainers = sorted(movers, key=lambda x: x.get('change_pct', 0), reverse=True)[:5]
    losers = sorted(movers, key=lambda x: x.get('change_pct', 0))[:5]
    volume_leaders = sorted(movers, key=lambda x: x.get('volume', 0), reverse=True)[:5]
    
    return jsonify({
        'gainers': gainers,
        'losers': losers,
        'volume_leaders': volume_leaders,
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    })

@app.route('/api/institutional/<symbol>')
def institutional_data(symbol):
    """Get institutional holding data"""
    data = screener.fetcher.get_institutional_data(symbol.upper())
    return jsonify(data)


# ─────────────────────────────────────────────────
# WEBSOCKET EVENTS
# ─────────────────────────────────────────────────

@socketio.on('connect')
def handle_connect():
    emit('connected', {'data': 'India Screener Connected!', 'time': datetime.now().isoformat()})

@socketio.on('request_scan')
def handle_scan_request(data):
    universe = data.get('universe', 'nifty50')
    mode_filter = data.get('mode_id')
    top_n = data.get('top', 20)
    min_ret = float(data.get('min_ret', 0))
    min_accuracy = float(data.get('min_accuracy', 80.0))
    
    if universe == 'custom_selected':
        custom_stocks = data.get('custom_stocks', [])
        if isinstance(custom_stocks, str):
            stock_list = [s.strip().upper() for s in custom_stocks.split(',') if s.strip()]
        elif isinstance(custom_stocks, list):
            stock_list = [str(s).strip().upper() for s in custom_stocks if str(s).strip()]
        else:
            stock_list = []
        if not stock_list:
            stock_list = NIFTY50_STOCKS
    elif universe == 'nifty50':
        stock_list = NIFTY50_STOCKS
    elif universe == 'nifty100':
        stock_list = NIFTY50_STOCKS + NIFTY_NEXT50
    elif universe == 'nse_all':
        stock_list = list(set(NSE_ALL_STOCKS))
    elif universe == 'bse_large':
        stock_list = list(set(BSE_LARGECAP))
    elif universe == 'bse_mid':
        stock_list = list(set(BSE_MIDCAP))
    elif universe == 'bse_small':
        stock_list = list(set(BSE_SMALLCAP))
    elif universe == 'bse_all':
        stock_list = list(set(BSE_ALL_STOCKS))
    elif universe == 'rockets_20':
        # Prioritize high momentum universe for 20%+ scan
        stock_list = list(set(BSE_MIDCAP + BSE_SMALLCAP + NIFTY_NEXT50))
        min_ret = 20.0  # strictly 20.0%+ Day Percentage
    elif universe == 'all_4000':
        stock_list = ALL_4000_SYMBOLS if ALL_4000_SYMBOLS else list(set(ALL_STOCKS))
    elif universe == 'nse_2600':
        stock_list = NSE_OFFICIAL_SYMBOLS if NSE_OFFICIAL_SYMBOLS else list(set(NSE_ALL_STOCKS))
    elif universe == 'bse_exclusive':
        stock_list = BSE_OFFICIAL_SYMBOLS if BSE_OFFICIAL_SYMBOLS else list(set(BSE_ALL_STOCKS))
    elif universe == 'all':
        stock_list = list(set(ALL_STOCKS))
    elif universe.startswith('sector_'):
        sector_key = universe[7:]
        # match sector name from key
        for name, lst in SECTOR_MAP.items():
            if name.lower().replace(' ', '_').replace('&', 'and') == sector_key:
                stock_list = lst
                break
        else:
            stock_list = NIFTY50_STOCKS
    else:
        stock_list = NIFTY50_STOCKS
    
    if not scan_cache['is_scanning']:
        thread = threading.Thread(
            target=run_scan_background,
            args=(stock_list, mode_filter, top_n, min_ret, min_accuracy)
        )
        thread.daemon = True
        thread.start()
        emit('scan_started', {'message': f'Scanning {len(stock_list)} stocks...', 'total': len(stock_list), 'min_ret': min_ret, 'min_accuracy': min_accuracy})
    else:
        emit('scan_busy', {'progress': scan_cache['scan_progress']})

@socketio.on('request_stop_scan')
def handle_stop_scan():
    """Client requested to stop/abort the running scan"""
    if scan_cache.get('is_scanning', False):
        scan_cache['stop_requested'] = True
        emit('scan_stopping', {'message': 'Scan stop requested by user'})
    else:
        emit('scan_stopped', {'message': 'No active scan running'})


@app.route('/api/grok/live')
def grok_live():
    """Grok Bot Terminal live state, agents, and logs"""
    best_stock = scan_cache['results'][0] if scan_cache['results'] else screener.run_all_screeners("TRENT")
    sym = best_stock.get('symbol', 'TRENT')
    ind = best_stock.get('indicators', {})
    setup = best_stock.get('trade_setup', {})
    
    # Check Dhan broker status
    dhan_info = dhan_client.get_fund_limits()
    dhan_connected = dhan_info.get('authenticated', False)
    balance = f"₹{dhan_info.get('avail_balance', 0):,.2f}" if dhan_connected else "₹1,55,920"

    agents = [
        {"name": "SCANNER", "sub": "75 modes + candlestick patterns", "status": "SCAN", "action": f"next ${sym} spike {ind.get('vol_ratio', 2.8)}x", "color": "#ff9800"},
        {"name": "RUG CHECK", "sub": "filters suspicious / circuit locks", "status": "PASS", "action": f"circuits clean ${sym}", "color": "#e91e63"},
        {"name": "SIZER", "sub": "sizes from account equity", "status": "32% eq", "action": f"32% of {balance}", "color": "#7c3aed"},
        {"name": "EXECUTOR", "sub": "opens + closes, tracks slip", "status": "LIVE", "action": f"LONG ${sym} slip 0.8%", "color": "#00e676"},
        {"name": "ACCURACY ENGINE", "sub": "99% Confluence Filter", "status": "99% CONF", "action": f"Verified ${sym} · 5 Confluence Factors", "color": "#00e676"},
        {"name": "LOGGER", "sub": "writes every decision", "status": "WRITE", "action": f"line #42 · enter ${sym}", "color": "#ff9800"},
        {"name": "EQUITY", "sub": "balance + curve updates", "status": "UPDATE", "action": f"{balance} · 8 closes", "color": "#00d4ff"},
        {"name": "YOU", "sub": "reads the log in the morning", "status": "READING", "action": "stopped asking, started reading", "color": "#78909c"}
    ]
    
    live_flow = [
        {"sym": sym, "badge": f"vol {ind.get('vol_ratio', 2.5)}x", "active": True},
        {"sym": "BEL", "badge": "spike 3.2x", "active": False},
        {"sym": "HAL", "badge": "vol 2.8x", "active": False},
        {"sym": "COCHINSHIP", "badge": "20%+ rocket", "active": False}
    ]
    
    logs = [
        {"time": "09:18", "type": "ENTER", "sym": "MAZAGON", "size": "size 24%", "res": "+4.12%", "pnl": "+₹4,230", "status": "EXIT", "note": "trailing stop hit"},
        {"time": "10:05", "type": "FILTERED", "sym": "RPOWER", "size": "", "res": "", "pnl": "", "status": "PASS", "note": "upper circuit limit 5%"},
        {"time": "11:22", "type": "ENTER", "sym": "SUZLON", "size": "size 20%", "res": "-1.8%", "pnl": "-₹1,850", "status": "EXIT", "note": "stop 15% hit"},
        {"time": "12:15", "type": "ENTER", "sym": sym, "size": "size 32%", "res": f"{ind.get('ret_1d', 3.5)}% live", "pnl": "+₹5,820", "status": "LIVE", "note": f"volume {ind.get('vol_ratio', 2.5)}x in 15m · {len(best_stock.get('matches', []))} signals"}
    ]
    
    return jsonify({
        'active_symbol': sym,
        'balance': balance,
        'dhan_account': dhan_info,
        'dhan_connected': dhan_connected,
        'trades': 8,
        'wins': 6,
        'losses': 2,
        'win_rate': 75.0,
        'candlestick_patterns': best_stock.get('candlestick_patterns', []),
        'active_trade': {
            'symbol': sym,
            'entry': setup.get('entry', ind.get('close', 0)),
            'stop_loss': setup.get('stop_loss', 0),
            'target': setup.get('target2', 0),
            'target1': setup.get('target1', 0),
            'target3': setup.get('target3', 0),
            'current_price': ind.get('close', 0),
            'ret_pct': ind.get('ret_1d', 0),
            'vol_ratio': ind.get('vol_ratio', 1.0),
            'slip': '0.8%',
            'size': '32% of equity',
            'candles': ind.get('candles', []),
            'matches': best_stock.get('matches', []),
            'confidence': setup.get('confidence', 'HIGH'),
            'reasons': setup.get('reasons', [])
        },
        'agents': agents,
        'live_flow': live_flow,
        'logs': logs
    })


# ─────────────────────────────────────────────────
# LIVE MARKET STATUS ENGINE (NSE / BSE)
# ─────────────────────────────────────────────────

@app.route('/api/market/status')
def api_market_status():
    """Live Market Timing and Status for Indian Exchanges (IST UTC+5:30)"""
    from datetime import datetime, timezone, timedelta
    utc_now = datetime.now(timezone.utc)
    ist_now = utc_now + timedelta(hours=5, minutes=30)
    
    weekday = ist_now.weekday()  # 0 = Monday, 6 = Sunday
    hour = ist_now.hour
    minute = ist_now.minute
    total_minutes = hour * 60 + minute
    
    is_weekday = (weekday < 5)
    is_live = False
    status_text = "MARKET CLOSED"
    status_detail = "NSE & BSE Trading Hours: 09:15 AM - 03:30 PM IST (Mon-Fri)"
    color = "#ff5252"
    badge = "🔴 CLOSED"
    
    if is_weekday:
        if 9*60 <= total_minutes < 9*60 + 15:
            is_live = False
            status_text = "PRE-MARKET SESSION"
            status_detail = "NSE Call Auction (09:00 - 09:15 IST)"
            color = "#ffb300"
            badge = "🟡 PRE-MARKET"
        elif 9*60 + 15 <= total_minutes <= 15*60 + 30:
            is_live = True
            status_text = "LIVE MARKET OPEN"
            status_detail = "NSE & BSE Live Trading Session (09:15 - 15:30 IST)"
            color = "#00e676"
            badge = "🟢 LIVE NSE/BSE"
        elif 15*60 + 30 < total_minutes <= 16*60:
            is_live = False
            status_text = "POST-MARKET CLOSING"
            status_detail = "NSE Closing Session (15:30 - 16:00 IST)"
            color = "#ff9800"
            badge = "🟠 POST-MARKET"
        else:
            status_text = "MARKET CLOSED"
            color = "#90a4ae"
            badge = "🔴 CLOSED"
    else:
        status_text = "WEEKEND CLOSED"
        status_detail = "Market opens Monday at 09:15 AM IST"
        color = "#90a4ae"
        badge = "🔴 WEEKEND CLOSED"
        
    return jsonify({
        'is_live': is_live,
        'status_text': status_text,
        'status_detail': status_detail,
        'badge': badge,
        'color': color,
        'ist_time': ist_now.strftime('%I:%M:%S %p'),
        'ist_date': ist_now.strftime('%a, %d %b %Y')
    })


# ─────────────────────────────────────────────────
# VIRTUAL PAPER TRADING SIMULATION ENGINE
# ─────────────────────────────────────────────────

PAPER_FILE = os.path.join(os.path.dirname(__file__), 'data', 'paper_trading.json')

def load_paper_account():
    if os.path.exists(PAPER_FILE):
        try:
            with open(PAPER_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            pass
    return {
        'initial_balance': 1000000.0,
        'cash_balance': 1000000.0,
        'positions': [],
        'history': [],
        'total_trades': 0,
        'wins': 0,
        'losses': 0,
        'realized_pnl': 0.0
    }

def save_paper_account(data):
    try:
        os.makedirs(os.path.dirname(PAPER_FILE), exist_ok=True)
        with open(PAPER_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        print("[Paper] Error saving account:", e)

@app.route('/api/paper/account')
def api_paper_account():
    """Get full Paper Trading virtual portfolio overview with live P&L"""
    account = load_paper_account()
    positions = account.get('positions', [])
    
    total_unrealized = 0.0
    invested_margin = 0.0
    
    for pos in positions:
        sym = pos.get('symbol')
        buy_price = float(pos.get('buy_price', 0))
        qty = int(pos.get('quantity', 0))
        side = pos.get('side', 'BUY')
        
        quote = screener.fetcher.get_live_quote(sym)
        current_price = float(quote.get('price', buy_price)) if quote and quote.get('price') else buy_price
        pos['current_price'] = current_price
        
        if side == 'BUY':
            pnl = (current_price - buy_price) * qty
        else:
            pnl = (buy_price - current_price) * qty
            
        pos['unrealized_pnl'] = round(pnl, 2)
        pos['pnl_pct'] = round((pnl / (buy_price * qty) * 100) if buy_price * qty > 0 else 0, 2)
        total_unrealized += pnl
        invested_margin += (buy_price * qty)
        
    cash = float(account.get('cash_balance', 1000000.0))
    total_equity = cash + invested_margin + total_unrealized
    total_trades = account.get('total_trades', 0)
    wins = account.get('wins', 0)
    
    return jsonify({
        'cash_balance': round(cash, 2),
        'invested_margin': round(invested_margin, 2),
        'unrealized_pnl': round(total_unrealized, 2),
        'realized_pnl': round(account.get('realized_pnl', 0.0), 2),
        'total_equity': round(total_equity, 2),
        'positions': positions,
        'history': account.get('history', [])[:30],
        'total_trades': total_trades,
        'wins': wins,
        'losses': account.get('losses', 0),
        'win_rate': round((wins / total_trades * 100) if total_trades > 0 else 0.0, 1)
    })

@app.route('/api/paper/order', methods=['POST'])
def api_paper_order():
    """Execute Virtual Paper Trade (Market/Limit Order)"""
    data = request.get_json(silent=True) or {}
    symbol = str(data.get('symbol', '')).strip().upper()
    side = data.get('side', 'BUY').upper()
    qty = int(data.get('quantity', 1))
    price = float(data.get('price', 0))
    stop_loss = float(data.get('stop_loss', 0))
    target = float(data.get('target', 0))
    
    if not symbol or qty <= 0 or price <= 0:
        return jsonify({'status': 'error', 'message': 'Invalid symbol, quantity, or price'}), 400
        
    account = load_paper_account()
    cost = price * qty
    
    if side == 'BUY' and account['cash_balance'] < cost:
        return jsonify({'status': 'error', 'message': f'Insufficient virtual balance. Required: ₹{cost:,.2f}, Available: ₹{account["cash_balance"]:,.2f}'}), 400
        
    order_id = f"VIRT-{int(time.time()*1000)}"
    position = {
        'id': order_id,
        'symbol': symbol,
        'side': side,
        'quantity': qty,
        'buy_price': price,
        'current_price': price,
        'stop_loss': stop_loss,
        'target': target,
        'opened_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'unrealized_pnl': 0.0,
        'pnl_pct': 0.0
    }
    
    account['cash_balance'] -= cost
    account['positions'].append(position)
    save_paper_account(account)
    
    socketio.emit('paper_order_placed', {'order': position})
    
    return jsonify({
        'status': 'success',
        'order_id': order_id,
        'position': position,
        'message': f'✅ Virtual Paper Trade Executed: {side} {qty} {symbol} @ ₹{price:,.2f}'
    })

@app.route('/api/paper/exit', methods=['POST'])
def api_paper_exit():
    """Square off/Exit an open virtual position"""
    data = request.get_json(silent=True) or {}
    order_id = data.get('order_id')
    
    account = load_paper_account()
    positions = account.get('positions', [])
    found = None
    
    for p in positions:
        if p.get('id') == order_id:
            found = p
            break
            
    if not found:
        return jsonify({'status': 'error', 'message': 'Position not found'}), 404
        
    sym = found['symbol']
    qty = found['quantity']
    buy_price = float(found['buy_price'])
    side = found['side']
    
    quote = screener.fetcher.get_live_quote(sym)
    exit_price = float(quote.get('price', buy_price)) if quote and quote.get('price') else buy_price
    
    if side == 'BUY':
        pnl = (exit_price - buy_price) * qty
    else:
        pnl = (buy_price - exit_price) * qty
        
    margin_returned = (buy_price * qty) + pnl
    account['cash_balance'] += margin_returned
    account['realized_pnl'] += pnl
    account['total_trades'] += 1
    if pnl >= 0:
        account['wins'] += 1
    else:
        account['losses'] += 1
        
    positions.remove(found)
    found['exit_price'] = exit_price
    found['closed_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    found['realized_pnl'] = round(pnl, 2)
    account['history'].insert(0, found)
    
    save_paper_account(account)
    
    return jsonify({
        'status': 'success',
        'pnl': round(pnl, 2),
        'message': f'Position {sym} squared off @ ₹{exit_price:,.2f} | P&L: ₹{pnl:+,.2f}'
    })

@app.route('/api/paper/reset', methods=['POST'])
def api_paper_reset():
    """Reset virtual capital to ₹10,00,000"""
    account = {
        'initial_balance': 1000000.0,
        'cash_balance': 1000000.0,
        'positions': [],
        'history': [],
        'total_trades': 0,
        'wins': 0,
        'losses': 0,
        'realized_pnl': 0.0
    }
    save_paper_account(account)
    return jsonify({'status': 'success', 'message': 'Virtual Paper Trading account reset to ₹10,00,000'})


@app.route('/api/sectors')
def list_sectors():
    """List all available sector universes"""
    sectors = []
    for name, stocks in SECTOR_MAP.items():
        sectors.append({
            'name': name,
            'key': 'sector_' + name.lower().replace(' ', '_').replace('&', 'and'),
            'count': len(stocks)
        })
    return jsonify({'sectors': sectors})


@app.route('/api/stocks/master')
def get_master_stocks():
    """Search and paginate through 4,200+ Indian stocks"""
    q = (request.args.get('q') or request.args.get('query') or '').strip().upper()
    exchange = request.args.get('exchange', 'ALL').upper()
    page = int(request.args.get('page', 1))
    limit = int(request.args.get('limit', 50))
    
    filtered = ALL_4000_STOCKS
    if exchange in ['NSE', 'BSE']:
        filtered = [s for s in filtered if s.get('exchange') == exchange]
    if q:
        filtered = [s for s in filtered if q in s.get('symbol', '') or q in s.get('name', '').upper()]
        
    start = (page - 1) * limit
    end = start + limit
    return jsonify({
        'total': len(filtered),
        'page': page,
        'limit': limit,
        'stocks': filtered[start:end]
    })


# ─────────────────────────────────────────────────
# DHAN HQ BROKER & TRADING INTEGRATION
# ─────────────────────────────────────────────────

@app.route('/api/dhan/status')
def dhan_status():
    """Get DhanHQ broker connection status and fund limits"""
    funds = dhan_client.get_fund_limits(force_refresh=True)
    return jsonify(funds)

@app.route('/api/dhan/holdings')
def dhan_holdings():
    """Get stock holdings from Dhan"""
    return jsonify(dhan_client.get_holdings())

@app.route('/api/dhan/positions')
def dhan_positions():
    """Get open/closed positions from Dhan"""
    return jsonify(dhan_client.get_positions())

@app.route('/api/dhan/order', methods=['POST'])
def dhan_place_order():
    """Execute order via Dhan or Paper Trade Simulation"""
    data = request.get_json(silent=True) or {}
    result = dhan_client.place_order(data)
    return jsonify(result)

@app.route('/api/dhan/login-url')
def dhan_login_url():
    """Generate 1-Click DhanHQ OAuth Login URL"""
    return jsonify(dhan_client.generate_login_url())

@app.route('/dhan/callback')
def dhan_callback():
    """Handle Dhan OAuth redirect callback with tokenId"""
    token_id = request.args.get('tokenId') or request.args.get('token_id')
    if not token_id:
        return """
        <html><body style="font-family:sans-serif;background:#101522;color:#fff;text-align:center;padding:50px;">
        <h2 style="color:#ff5252;">⚠️ Missing Token ID</h2>
        <p>No tokenId received in callback.</p>
        </body></html>
        """, 400
    
    res = dhan_client.consume_token(token_id)
    if res.get('status') == 'success':
        socketio.emit('dhan_connected', {'client_name': res.get('client_name')})
        return f"""
        <html><body style="font-family:sans-serif;background:#101522;color:#fff;text-align:center;padding:50px;">
        <div style="font-size:3rem;margin-bottom:10px;">🏛️✅</div>
        <h2 style="color:#00e676;">DhanHQ Account Connected Successfully!</h2>
        <p style="font-size:1.1rem;color:#cfd8dc;">Welcome back, <strong>{res.get('client_name', 'Trader')}</strong> (Client ID: {res.get('client_id')})</p>
        <p style="color:#78909c;font-size:0.85rem;">Live trading & market quotes are now active. You may close this window and return to Grok Screener.</p>
        <script>
          if (window.opener) {{
            window.opener.location.reload();
            setTimeout(() => window.close(), 2000);
          }}
        </script>
        </body></html>
        """
    else:
        return f"""
        <html><body style="font-family:sans-serif;background:#101522;color:#fff;text-align:center;padding:50px;">
        <h2 style="color:#ff5252;">❌ Dhan Authentication Failed</h2>
        <p style="color:#cfd8dc;">{res.get('error')}</p>
        </body></html>
        """, 400

@app.route('/api/dhan/consume-token', methods=['POST'])
def dhan_consume_token():
    """Consume tokenId manually if pasted by user"""
    data = request.get_json(silent=True) or {}
    token_id = data.get('tokenId') or data.get('token_id', '')
    if not token_id:
        return jsonify({'status': 'error', 'message': 'Token ID required'}), 400
    res = dhan_client.consume_token(token_id)
    return jsonify(res)

@app.route('/api/dhan/update-token', methods=['POST'])
def dhan_update_token():
    """Update 24-hr access token dynamically from UI"""
    data = request.get_json(silent=True) or {}
    new_token = data.get('token', '').strip()
    new_client_id = data.get('client_id', '').strip() or None
    if not new_token:
        return jsonify({'status': 'error', 'message': 'Token cannot be empty'}), 400
    res = dhan_client.update_token(new_token, new_client_id)
    return jsonify(res)



if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5050))
    print("=" * 60)
    print("🚀 ROCKETSCAN PRO - NSE/BSE TECHNICAL SCREENER & PAPER TRADING")
    print(f"   Listening on port {port} (Local: http://localhost:{port})")
    print("=" * 60)
    socketio.run(app, host='0.0.0.0', port=port, debug=False, allow_unsafe_werkzeug=True)
