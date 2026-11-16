"""
╔══════════════════════════════════════════════════════════════════════════╗
║  QUANT SCREENERS - Minervini VCP + Stockbee Episodic Pivot (EP)         ║
║  Adapted for Indian NSE/BSE Market (yfinance data, no paid APIs)        ║
║  Mode 76: Minervini Stage-2 Uptrend (7-Point Trend Template)            ║
║  Mode 77: VCP Volatility Contraction Pattern (2+ contractions)          ║
║  Mode 78: Stockbee Episodic Pivot (Gap-up Day-1 Catalyst)              ║
╚══════════════════════════════════════════════════════════════════════════╝
"""

from typing import Dict, List, Optional, Tuple
import math


# ─────────────────────────────────────────────────────────────────────────────
# UTILITY FUNCTIONS
# ─────────────────────────────────────────────────────────────────────────────

def compute_sma(closes: List[float], period: int) -> Optional[float]:
    """Simple moving average over last `period` closes."""
    if len(closes) < period:
        return None
    return sum(closes[-period:]) / period


def compute_sma_n_bars_ago(closes: List[float], period: int, bars_ago: int) -> Optional[float]:
    """SMA computed on data ending `bars_ago` bars in the past."""
    end = len(closes) - bars_ago
    if end < period:
        return None
    return sum(closes[end - period:end]) / period


def _rolling_max(values: List[float], window: int) -> List[float]:
    """Rolling maximum for swing high detection."""
    result = []
    for i in range(len(values)):
        start = max(0, i - window)
        result.append(max(values[start:i + 1]))
    return result


def _rolling_min(values: List[float], window: int) -> List[float]:
    """Rolling minimum for swing low detection."""
    result = []
    for i in range(len(values)):
        start = max(0, i - window)
        result.append(min(values[start:i + 1]))
    return result


# ─────────────────────────────────────────────────────────────────────────────
# VCP: MINERVINI 7-POINT STAGE-2 TREND TEMPLATE  (Indian NSE/BSE Adaptation)
# ─────────────────────────────────────────────────────────────────────────────

def _compute_trend_template(df) -> Dict:
    """
    Minervini's 7-Point Trend Template adapted for Indian market.
    Need 5/7 criteria to pass (relaxed from strict 7/7 for emerging market volatility).

    Criteria:
      1. Price > SMA50 AND Price > SMA150 AND Price > SMA200 (if 200d available)
      2. SMA150 > SMA200
      3. SMA200 trending up (now vs 22 trading days ago)
      4. Price > SMA50
      5. Price >= 25% above 52-week low
      6. Price within 30% of 52-week high (relaxed from 25% for Indian markets)
      7. ret_3m >= 10% (relative strength proxy vs benchmark)
    """
    try:
        closes = list(df['Close'].dropna())
        if len(closes) < 50:
            return _empty_trend()

        price = closes[-1]
        high_52w = max(closes[-252:]) if len(closes) >= 252 else max(closes)
        low_52w = min(closes[-252:]) if len(closes) >= 252 else min(closes)

        sma50 = compute_sma(closes, 50)
        sma150 = compute_sma(closes, 150) if len(closes) >= 150 else None
        sma200 = compute_sma(closes, 200) if len(closes) >= 200 else None
        sma200_22d_ago = compute_sma_n_bars_ago(closes, 200, 22) if len(closes) >= 222 else None

        # 3-month return (63 trading days)
        price_63d_ago = closes[-64] if len(closes) >= 64 else closes[0]
        ret_3m = ((price - price_63d_ago) / price_63d_ago * 100) if price_63d_ago > 0 else 0.0

        criteria = {}
        score = 0

        # Criterion 1: Price above all major moving averages
        c1_conditions = [price > sma50] if sma50 else []
        if sma150:
            c1_conditions.append(price > sma150)
        if sma200:
            c1_conditions.append(price > sma200)
        c1 = len(c1_conditions) > 0 and all(c1_conditions)
        criteria['c1_price_above_smas'] = c1
        if c1: score += 1

        # Criterion 2: SMA150 > SMA200
        if sma150 and sma200:
            c2 = sma150 > sma200
        elif sma150:
            c2 = True  # Partial pass if no 200d
        else:
            c2 = False
        criteria['c2_sma150_above_sma200'] = c2
        if c2: score += 1

        # Criterion 3: SMA200 trending up
        if sma200 and sma200_22d_ago:
            c3 = sma200 > sma200_22d_ago
        else:
            c3 = True  # Partial pass if insufficient data
        criteria['c3_sma200_trending_up'] = c3
        if c3: score += 1

        # Criterion 4: Price > SMA50 (separately scored for emphasis)
        c4 = bool(sma50 and price > sma50)
        criteria['c4_price_above_sma50'] = c4
        if c4: score += 1

        # Criterion 5: Price >= 25% above 52-week low
        if low_52w > 0:
            pct_above_low = ((price - low_52w) / low_52w) * 100
            c5 = pct_above_low >= 25.0
        else:
            c5 = False
        criteria['c5_above_52w_low_25pct'] = c5
        if c5: score += 1

        # Criterion 6: Price within 30% of 52-week high (relaxed for Indian market)
        if high_52w > 0:
            pct_from_high = ((high_52w - price) / high_52w) * 100
            c6 = pct_from_high <= 30.0
        else:
            c6 = False
        criteria['c6_within_30pct_of_52w_high'] = c6
        if c6: score += 1

        # Criterion 7: Relative strength (3-month return >= 10%)
        c7 = ret_3m >= 10.0
        criteria['c7_rs_strength'] = c7
        if c7: score += 1

        trend_score = round((score / 7) * 100)
        passed = score >= 5  # 5 out of 7 for Indian market

        return {
            'vcp_trend_score': trend_score,
            'vcp_trend_passed': passed,
            'vcp_trend_criteria': score,
            'vcp_sma50': round(sma50, 2) if sma50 else None,
            'vcp_sma150': round(sma150, 2) if sma150 else None,
            'vcp_sma200': round(sma200, 2) if sma200 else None,
            **{f'vcp_{k}': v for k, v in criteria.items()},
        }
    except Exception as e:
        return _empty_trend()


def _empty_trend() -> Dict:
    return {
        'vcp_trend_score': 0, 'vcp_trend_passed': False, 'vcp_trend_criteria': 0,
        'vcp_sma50': None, 'vcp_sma150': None, 'vcp_sma200': None,
    }


# ─────────────────────────────────────────────────────────────────────────────
# VCP: VOLATILITY CONTRACTION PATTERN DETECTION
# ─────────────────────────────────────────────────────────────────────────────

def _find_swing_highs_lows(closes: List[float], highs: List[float], lows: List[float],
                             window: int = 5) -> Tuple[List[Tuple[int, float]], List[Tuple[int, float]]]:
    """
    Detect swing highs and lows using rolling window.
    Returns (swing_highs, swing_lows) as list of (index, price) tuples.
    """
    swing_highs = []
    swing_lows = []
    n = len(closes)

    for i in range(window, n - window):
        # Swing high: high[i] is maximum in window on both sides
        is_high = all(highs[i] >= highs[j] for j in range(i - window, i + window + 1) if j != i)
        if is_high:
            swing_highs.append((i, highs[i]))

        # Swing low: low[i] is minimum in window on both sides
        is_low = all(lows[i] <= lows[j] for j in range(i - window, i + window + 1) if j != i)
        if is_low:
            swing_lows.append((i, lows[i]))

    return swing_highs, swing_lows


def _detect_vcp_contractions(swing_highs: List[Tuple[int, float]],
                               swing_lows: List[Tuple[int, float]]) -> Dict:
    """
    Detect VCP contractions: successive corrections that get shallower (tighter).
    Each correction depth should be <= 75% of the previous one.
    Initial correction (T1): 8% to 45% for Indian market.
    """
    if len(swing_highs) < 2 or len(swing_lows) < 1:
        return {'vcp_num_contractions': 0, 'vcp_pattern_valid': False, 'vcp_pivot_price': None,
                'vcp_pattern_score': 0}

    contractions = []
    pivot_price = None

    # Find correction cycles: swing_high → swing_low → swing_high (recovery)
    all_points = sorted(
        [(idx, price, 'H') for idx, price in swing_highs] +
        [(idx, price, 'L') for idx, price in swing_lows],
        key=lambda x: x[0]
    )

    i = 0
    while i < len(all_points) - 1:
        if all_points[i][2] == 'H':
            # Find the next low after this high
            j = i + 1
            while j < len(all_points) and all_points[j][2] != 'L':
                j += 1
            if j < len(all_points):
                high_price = all_points[i][1]
                low_price = all_points[j][1]
                depth_pct = ((high_price - low_price) / high_price) * 100 if high_price > 0 else 0
                if 8.0 <= depth_pct <= 45.0:  # Valid contraction range for Indian market
                    contractions.append({
                        'high_idx': all_points[i][0],
                        'low_idx': all_points[j][0],
                        'high': high_price,
                        'low': low_price,
                        'depth_pct': round(depth_pct, 2)
                    })
                i = j
            else:
                i += 1
        else:
            i += 1

    if not contractions:
        return {'vcp_num_contractions': 0, 'vcp_pattern_valid': False, 'vcp_pivot_price': None,
                'vcp_pattern_score': 0}

    # Count valid successive contractions (each getting tighter)
    valid_contractions = 0
    for k in range(1, len(contractions)):
        prev_depth = contractions[k - 1]['depth_pct']
        curr_depth = contractions[k]['depth_pct']
        if curr_depth <= prev_depth * 0.75:  # At least 25% tighter
            valid_contractions += 1

    num_contractions = min(len(contractions), valid_contractions + 1) if valid_contractions > 0 else len(contractions)

    # Pivot price: last swing high (potential breakout level)
    if contractions:
        pivot_price = round(contractions[-1]['high'], 2)

    pattern_valid = num_contractions >= 2
    pattern_score = min(100, num_contractions * 25 + (10 if pattern_valid else 0))

    return {
        'vcp_num_contractions': num_contractions,
        'vcp_pattern_valid': pattern_valid,
        'vcp_pivot_price': pivot_price,
        'vcp_pattern_score': pattern_score,
    }


def _detect_volume_dry_up(volumes: List[float]) -> Dict:
    """
    Volume dry-up: average volume of last 10 bars < 70% of 50-bar average.
    Indicates institutional selling has stopped — coiling for breakout.
    """
    if len(volumes) < 50:
        return {'vcp_volume_dry_up': False, 'vcp_vol_dry_ratio': None}

    avg_vol_10 = sum(volumes[-10:]) / 10
    avg_vol_50 = sum(volumes[-50:]) / 50

    ratio = avg_vol_10 / avg_vol_50 if avg_vol_50 > 0 else 1.0
    dry_up = ratio < 0.70

    return {
        'vcp_volume_dry_up': dry_up,
        'vcp_vol_dry_ratio': round(ratio, 3),
    }


def compute_vcp_indicators(df) -> Dict:
    """
    Main VCP computation: Trend Template + Pattern Detection + Volume Analysis.
    Returns dict with all vcp_* indicators.
    """
    try:
        result = {}

        # 1. Trend Template
        trend_data = _compute_trend_template(df)
        result.update(trend_data)

        # 2. VCP Pattern Detection (use last 60 bars)
        lookback = 60
        df_vcp = df.tail(lookback)
        closes = list(df_vcp['Close'].dropna())
        highs = list(df_vcp['High'].dropna())
        lows = list(df_vcp['Low'].dropna())
        volumes = list(df['Volume'].dropna())

        min_len = min(len(closes), len(highs), len(lows))
        closes = closes[:min_len]
        highs = highs[:min_len]
        lows = lows[:min_len]

        swing_highs, swing_lows = _find_swing_highs_lows(closes, highs, lows, window=5)
        pattern_data = _detect_vcp_contractions(swing_highs, swing_lows)
        result.update(pattern_data)

        # 3. Volume Dry-up
        vol_data = _detect_volume_dry_up(volumes)
        result.update(vol_data)

        # 4. Composite VCP Score (Trend 50% + Pattern 30% + Volume 20%)
        trend_score = result.get('vcp_trend_score', 0)
        pattern_score = result.get('vcp_pattern_score', 0)
        vol_bonus = 20 if result.get('vcp_volume_dry_up', False) else 0
        composite = round((trend_score * 0.5) + (pattern_score * 0.3) + vol_bonus)
        result['vcp_composite_score'] = min(100, composite)

        return result

    except Exception as e:
        return {
            'vcp_trend_score': 0, 'vcp_trend_passed': False, 'vcp_trend_criteria': 0,
            'vcp_sma50': None, 'vcp_sma150': None, 'vcp_sma200': None,
            'vcp_num_contractions': 0, 'vcp_pattern_valid': False,
            'vcp_pivot_price': None, 'vcp_pattern_score': 0,
            'vcp_volume_dry_up': False, 'vcp_vol_dry_ratio': None,
            'vcp_composite_score': 0,
        }


# ─────────────────────────────────────────────────────────────────────────────
# EPISODIC PIVOT (EP): STOCKBEE METHODOLOGY — Day-1 Catalyst Gap-Up
# ─────────────────────────────────────────────────────────────────────────────

def compute_ep_indicators(df) -> Dict:
    """
    Stockbee Episodic Pivot: Day-1 gap-up on massive volume (catalyst event).
    Indian market adaptation:
      - Gap-up >= 4% on open (Indian circuit filter allows 10-20% gaps)
      - Day-1 total return >= 8% (Indian EP threshold)
      - Volume shock >= 2.5x 20-day average
      - Closed in upper 60% of day's range (strength confirmation)
      - Within 20% of 52-week high (not in deep downtrend)
    """
    try:
        closes = list(df['Close'].dropna())
        opens = list(df['Open'].dropna())
        highs = list(df['High'].dropna())
        lows = list(df['Low'].dropna())
        volumes = list(df['Volume'].dropna())

        min_len = min(len(closes), len(opens), len(highs), len(lows), len(volumes))
        if min_len < 22:
            return _empty_ep()

        closes = closes[:min_len]
        opens = opens[:min_len]
        highs = highs[:min_len]
        lows = lows[:min_len]
        volumes = volumes[:min_len]

        # Today's data
        close_today = closes[-1]
        open_today = opens[-1]
        high_today = highs[-1]
        low_today = lows[-1]
        vol_today = volumes[-1]
        close_yesterday = closes[-2]

        # EP metrics
        ep_gap_pct = ((open_today - close_yesterday) / close_yesterday * 100) if close_yesterday > 0 else 0.0
        ep_day_gain = ((close_today - close_yesterday) / close_yesterday * 100) if close_yesterday > 0 else 0.0

        # Volume shock: today's volume vs 20-day average
        avg_vol_20 = sum(volumes[-21:-1]) / 20 if len(volumes) >= 21 else sum(volumes[:-1]) / max(len(volumes) - 1, 1)
        ep_volume_shock = (vol_today / avg_vol_20) if avg_vol_20 > 0 else 0.0

        # Close location: where did price close within day's range?
        day_range = high_today - low_today
        ep_close_location = ((close_today - low_today) / day_range) if day_range > 0 else 0.5

        # 52-week metrics
        high_52w = max(closes[-252:]) if len(closes) >= 252 else max(closes)
        pct_from_52w_high = ((high_52w - close_today) / high_52w * 100) if high_52w > 0 else 100.0

        # EP Validity Check
        ep_valid = (
            ep_gap_pct >= 4.0 and           # Gap-up on open (catalyst)
            ep_day_gain >= 8.0 and           # Strong Day-1 close (Indian threshold)
            ep_volume_shock >= 2.5 and       # Volume shock 2.5x+ (institutional participation)
            ep_close_location >= 0.60 and    # Closed in upper 60% of range
            pct_from_52w_high <= 20.0        # Not in deep downtrend
        )

        # EP Score (0-100)
        ep_score = 0
        if ep_gap_pct >= 4.0:
            ep_score += min(25, int(ep_gap_pct * 2))
        if ep_day_gain >= 8.0:
            ep_score += min(25, int(ep_day_gain * 1.5))
        if ep_volume_shock >= 2.5:
            ep_score += min(30, int(ep_volume_shock * 5))
        if ep_close_location >= 0.6:
            ep_score += int(ep_close_location * 20)

        return {
            'ep_gap_pct': round(ep_gap_pct, 2),
            'ep_day_gain': round(ep_day_gain, 2),
            'ep_volume_shock': round(ep_volume_shock, 2),
            'ep_close_location': round(ep_close_location, 3),
            'ep_pct_from_52w_high': round(pct_from_52w_high, 2),
            'ep_valid': ep_valid,
            'ep_score': min(100, ep_score),
        }

    except Exception as e:
        return _empty_ep()


def _empty_ep() -> Dict:
    return {
        'ep_gap_pct': 0.0, 'ep_day_gain': 0.0, 'ep_volume_shock': 0.0,
        'ep_close_location': 0.0, 'ep_pct_from_52w_high': 100.0,
        'ep_valid': False, 'ep_score': 0,
    }


# ─────────────────────────────────────────────────────────────────────────────
# QUICK SELF-TEST
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == '__main__':
    print("quant_screeners.py - Self Test")
    print("compute_sma([10,20,30,40,50], 3) =", compute_sma([10, 20, 30, 40, 50], 3))  # Expected: 40.0
    print("Module OK - VCP + EP indicators ready for Indian NSE/BSE")
