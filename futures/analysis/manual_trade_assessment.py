"""
Manual Trade Assessment - Last 30 Days

Look at Gold 15-min chart and identify:
- Where would a REAL trader have entered?
- What signals were visible?
- Breakouts, support/resistance, patterns

Goal: Find 10+ tradeable opportunities per month

Author: Trading System
Date: 2026-04-18
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, timedelta
from typing import List, Dict


def fetch_gold_data(days: int = 30):
    """Fetch Gold 15-min data"""
    end = datetime.now()
    start = end - timedelta(days=days)
    data = yf.download('GC=F', start=start, end=end, interval='15m', progress=False)
    return data


def identify_manual_trades(data: pd.DataFrame) -> List[Dict]:
    """
    Identify trades a MANUAL trader would have taken

    Looking for:
    1. Breakouts above resistance
    2. Breakdowns below support
    3. Bounce off support
    4. Rejection at resistance
    5. Moving average crosses
    6. Strong momentum bars
    7. Consolidation breakouts
    """

    trades = []

    # Calculate indicators
    data['SMA_20'] = data['Close'].rolling(20).mean()
    data['SMA_50'] = data['Close'].rolling(50).mean()
    data['EMA_9'] = data['Close'].ewm(span=9, adjust=False).mean()

    # Calculate ATR for volatility
    data['HL'] = data['High'] - data['Low']
    data['HC'] = abs(data['High'] - data['Close'].shift(1))
    data['LC'] = abs(data['Low'] - data['Close'].shift(1))
    data['TR'] = data[['HL', 'HC', 'LC']].max(axis=1)
    data['ATR'] = data['TR'].rolling(14).mean()

    # Volume
    data['Vol_SMA'] = data['Volume'].rolling(20).mean()

    # Range
    data['Range'] = data['High'] - data['Low']
    data['Range_Pct'] = ((data['High'] - data['Low']) / data['Close']) * 100

    print(f"\n{'='*80}")
    print(f"MANUAL TRADE IDENTIFICATION - LAST 30 DAYS")
    print(f"{'='*80}\n")
    print(f"Period: {data.index[0]} to {data.index[-1]}")
    print(f"Total 15-min bars: {len(data)}")
    print(f"\nAnalyzing for manual trading opportunities...\n")

    # Scan each bar for opportunities
    for i in range(100, len(data)):  # Start after 100 bars for indicators

        bar = data.iloc[i]
        prev_bars = data.iloc[i-20:i]

        price = float(bar['Close'])
        high = float(bar['High'])
        low = float(bar['Low'])
        open_price = float(bar['Open'])

        sma_20 = float(bar['SMA_20'])
        sma_50 = float(bar['SMA_50'])
        ema_9 = float(bar['EMA_9'])
        atr = float(bar['ATR'])

        volume = float(bar['Volume'])
        avg_vol = float(bar['Vol_SMA'])

        timestamp = bar.name

        # PATTERN 1: Breakout above 20-bar high (classic breakout)
        high_20 = float(prev_bars['High'].max())
        if high > high_20 and volume > avg_vol * 1.2:
            trades.append({
                'timestamp': timestamp,
                'type': 'BUY',
                'pattern': 'BREAKOUT_HIGH',
                'entry': price,
                'stop': high_20 - atr,
                'target': price + 2 * atr,
                'reason': f'Broke above 20-bar high ${high_20:.2f} with volume'
            })

        # PATTERN 2: Breakdown below 20-bar low
        low_20 = float(prev_bars['Low'].min())
        if low < low_20 and volume > avg_vol * 1.2:
            trades.append({
                'timestamp': timestamp,
                'type': 'SELL',
                'pattern': 'BREAKDOWN_LOW',
                'entry': price,
                'stop': low_20 + atr,
                'target': price - 2 * atr,
                'reason': f'Broke below 20-bar low ${low_20:.2f} with volume'
            })

        # PATTERN 3: Bounce off SMA 20 (pullback trade)
        if i >= 3:
            prev_3_lows = [float(data.iloc[i-j]['Low']) for j in range(1, 4)]
            touched_sma = any(low_val <= sma_20 * 1.005 for low_val in prev_3_lows)

            if touched_sma and price > sma_20 and price > ema_9:
                trades.append({
                    'timestamp': timestamp,
                    'type': 'BUY',
                    'pattern': 'SMA_BOUNCE',
                    'entry': price,
                    'stop': sma_20 - atr * 0.5,
                    'target': price + 1.5 * atr,
                    'reason': f'Bounced off 20 SMA ${sma_20:.2f}, resuming uptrend'
                })

        # PATTERN 4: EMA 9 cross above SMA 20 (momentum shift)
        if i >= 1:
            prev_ema = float(data.iloc[i-1]['EMA_9'])
            prev_sma20 = float(data.iloc[i-1]['SMA_20'])

            if prev_ema < prev_sma20 and ema_9 > sma_20:
                trades.append({
                    'timestamp': timestamp,
                    'type': 'BUY',
                    'pattern': 'EMA_CROSS_UP',
                    'entry': price,
                    'stop': sma_20 - atr * 0.8,
                    'target': price + 2 * atr,
                    'reason': f'EMA 9 crossed above SMA 20, momentum shift'
                })

            # EMA cross down
            if prev_ema > prev_sma20 and ema_9 < sma_20:
                trades.append({
                    'timestamp': timestamp,
                    'type': 'SELL',
                    'pattern': 'EMA_CROSS_DOWN',
                    'entry': price,
                    'stop': sma_20 + atr * 0.8,
                    'target': price - 2 * atr,
                    'reason': f'EMA 9 crossed below SMA 20, momentum shift'
                })

        # PATTERN 5: Strong momentum bar (big move with volume)
        bar_range_pct = float(bar['Range_Pct'])
        avg_range = float(prev_bars['Range_Pct'].mean())

        if bar_range_pct > avg_range * 2 and volume > avg_vol * 1.5:
            if price > open_price:  # Bullish bar
                trades.append({
                    'timestamp': timestamp,
                    'type': 'BUY',
                    'pattern': 'MOMENTUM_BAR',
                    'entry': price,
                    'stop': low,
                    'target': price + (price - low),
                    'reason': f'Strong bullish bar, {bar_range_pct:.2f}% range with high volume'
                })
            elif price < open_price:  # Bearish bar
                trades.append({
                    'timestamp': timestamp,
                    'type': 'SELL',
                    'pattern': 'MOMENTUM_BAR',
                    'entry': price,
                    'stop': high,
                    'target': price - (high - price),
                    'reason': f'Strong bearish bar, {bar_range_pct:.2f}% range with high volume'
                })

        # PATTERN 6: Consolidation breakout (tight range then expansion)
        if i >= 10:
            last_10_ranges = data.iloc[i-10:i]['Range_Pct']
            avg_range_10 = float(last_10_ranges.mean())

            if avg_range_10 < 0.3 and bar_range_pct > 0.5:  # Tight then expansion
                if price > float(prev_bars['High'].max()):
                    trades.append({
                        'timestamp': timestamp,
                        'type': 'BUY',
                        'pattern': 'CONSOLIDATION_BREAK',
                        'entry': price,
                        'stop': float(prev_bars['Low'].min()),
                        'target': price + atr * 2,
                        'reason': f'Broke out of tight consolidation (avg {avg_range_10:.2f}%)'
                    })

    return trades


def analyze_trades(trades: List[Dict], data: pd.DataFrame):
    """Analyze identified trades and their outcomes"""

    print(f"\n{'='*80}")
    print(f"IDENTIFIED MANUAL TRADES")
    print(f"{'='*80}\n")

    if not trades:
        print("❌ No manual trades identified")
        return

    print(f"Found {len(trades)} potential manual trades\n")

    # Group by pattern
    patterns = {}
    for t in trades:
        pattern = t['pattern']
        if pattern not in patterns:
            patterns[pattern] = []
        patterns[pattern].append(t)

    print(f"BY PATTERN:")
    for pattern, pattern_trades in sorted(patterns.items(), key=lambda x: len(x[1]), reverse=True):
        print(f"  {pattern:25s}: {len(pattern_trades):3d} trades")

    # Show first 15 trades
    print(f"\n{'='*80}")
    print(f"FIRST 15 IDENTIFIED TRADES (Sample)")
    print(f"{'='*80}\n")

    for i, t in enumerate(trades[:15], 1):
        risk = abs(t['entry'] - t['stop'])
        reward = abs(t['target'] - t['entry'])
        rr = reward / risk if risk > 0 else 0

        print(f"{i}. {t['timestamp'].strftime('%m-%d %H:%M')} | {t['type']:4s} | {t['pattern']}")
        print(f"   Entry: ${t['entry']:.2f} | Stop: ${t['stop']:.2f} | Target: ${t['target']:.2f}")
        print(f"   Risk: ${risk:.2f} | R:R: {rr:.2f}:1")
        print(f"   💡 {t['reason']}")
        print()

    # Stats
    avg_risk = np.mean([abs(t['entry'] - t['stop']) for t in trades])
    avg_rr = np.mean([abs(t['target'] - t['entry']) / abs(t['entry'] - t['stop'])
                      for t in trades if abs(t['entry'] - t['stop']) > 0])

    trades_per_day = len(trades) / 30

    print(f"\n{'='*80}")
    print(f"STATISTICS")
    print(f"{'='*80}")
    print(f"Total trades found: {len(trades)}")
    print(f"Trades per day: {trades_per_day:.1f}")
    print(f"Trades per month (30 days): {len(trades)}")
    print(f"Average risk per trade: ${avg_risk:.2f}")
    print(f"Average R:R: {avg_rr:.2f}:1")

    print(f"\n{'='*80}")
    print(f"CONCLUSION")
    print(f"{'='*80}")

    if len(trades) >= 10:
        print(f"✅ Found {len(trades)} manual trades in 30 days")
        print(f"✅ This meets the 10+ trades/month target")
        print(f"\nNext step: Build scanner with these patterns:")
        print(f"  1. Breakout above 20-bar high")
        print(f"  2. Breakdown below 20-bar low")
        print(f"  3. Bounce off SMA 20 in uptrend")
        print(f"  4. EMA 9 crosses SMA 20")
        print(f"  5. Strong momentum bars with volume")
        print(f"  6. Consolidation breakouts")
        print(f"\nThese are REAL patterns manual traders use.")
        print(f"Forget Hurst - focus on price action!")
    else:
        print(f"⚠️  Only {len(trades)} trades found")
        print(f"Need to lower thresholds or add more patterns")


def main():
    """Run manual trade assessment"""

    # Fetch data
    print("📥 Fetching Gold 15-min data (last 30 days)...")
    data = fetch_gold_data(30)
    print(f"✅ Fetched {len(data)} bars")

    # Identify trades
    trades = identify_manual_trades(data)

    # Analyze
    analyze_trades(trades, data)

    print(f"\n{'='*80}")
    print(f"READY TO BUILD PRACTICAL SCANNER")
    print(f"{'='*80}")
    print(f"""
These patterns are what REAL traders see on charts.
They don't wait for Hurst > 0.6 or < 0.4.
They trade breakouts, bounces, crosses, momentum.

Next: Build scanner that generates these signals in real-time.
    """)


if __name__ == "__main__":
    main()
