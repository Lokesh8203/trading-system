"""
Test Scanner Frequency - How many signals in 30 days?

Run practical scanner on every 15-min bar for last 30 days
to see REAL signal frequency

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


def fetch_gold_data(days: int = 30):
    """Fetch Gold 15-min data"""
    end = datetime.now()
    start = end - timedelta(days=days)
    data = yf.download('GC=F', start=start, end=end, interval='15m', progress=False)
    return data


def add_indicators(data: pd.DataFrame) -> pd.DataFrame:
    """Add indicators"""
    df = data.copy()
    df['SMA_20'] = df['Close'].rolling(20).mean()
    df['SMA_50'] = df['Close'].rolling(50).mean()
    df['EMA_9'] = df['Close'].ewm(span=9, adjust=False).mean()

    df['HL'] = df['High'] - df['Low']
    df['HC'] = abs(df['High'] - df['Close'].shift(1))
    df['LC'] = abs(df['Low'] - df['Close'].shift(1))
    df['TR'] = df[['HL', 'HC', 'LC']].max(axis=1)
    df['ATR'] = df['TR'].rolling(14).mean()

    df['Vol_SMA'] = df['Volume'].rolling(20).mean()
    df['Range_Pct'] = ((df['High'] - df['Low']) / df['Close']) * 100

    return df


def check_signals(data: pd.DataFrame, bar_idx: int) -> list:
    """Check signals at this bar (returns list of patterns found)"""

    if bar_idx < 100:
        return []

    signals = []

    bar = data.iloc[bar_idx]
    prev_bars = data.iloc[bar_idx-20:bar_idx]

    price = float(bar['Close'])
    high = float(bar['High'])
    low = float(bar['Low'])
    open_price = float(bar['Open'])

    sma_20 = float(bar['SMA_20'])
    ema_9 = float(bar['EMA_9'])
    atr = float(bar['ATR'])

    volume = float(bar['Volume'])
    avg_vol = float(bar['Vol_SMA'])

    # PATTERN 1: Breakout
    high_20 = float(prev_bars['High'].max())
    if high > high_20 and volume > avg_vol * 1.2:
        signals.append('BREAKOUT_HIGH')

    # PATTERN 2: Breakdown
    low_20 = float(prev_bars['Low'].min())
    if low < low_20 and volume > avg_vol * 1.2:
        signals.append('BREAKDOWN_LOW')

    # PATTERN 3: SMA Bounce
    prev_3 = data.iloc[bar_idx-3:bar_idx]
    touched_sma = any(float(b['Low']) <= float(b['SMA_20']) * 1.005 for idx, b in prev_3.iterrows())
    if touched_sma and price > sma_20 and price > ema_9:
        signals.append('SMA_BOUNCE')

    # PATTERN 4: EMA Cross
    if bar_idx >= 1:
        prev = data.iloc[bar_idx-1]
        prev_ema = float(prev['EMA_9'])
        prev_sma20 = float(prev['SMA_20'])

        if prev_ema < prev_sma20 and ema_9 > sma_20:
            signals.append('EMA_CROSS_UP')
        if prev_ema > prev_sma20 and ema_9 < sma_20:
            signals.append('EMA_CROSS_DOWN')

    # PATTERN 5: Momentum Bar
    bar_range_pct = float(bar['Range_Pct'])
    avg_range = float(prev_bars['Range_Pct'].mean())

    if bar_range_pct > avg_range * 2 and volume > avg_vol * 1.5:
        if price > open_price:
            signals.append('MOMENTUM_BULL')
        elif price < open_price:
            signals.append('MOMENTUM_BEAR')

    return signals


def main():
    """Test scanner frequency"""
    print(f"\n{'='*80}")
    print(f"SCANNER FREQUENCY TEST - LAST 30 DAYS")
    print(f"{'='*80}\n")

    print("📥 Fetching Gold 15-min data...")
    data = fetch_gold_data(30)
    print(f"✅ Fetched {len(data)} bars")
    print(f"Period: {data.index[0]} to {data.index[-1]}\n")

    print("📊 Adding indicators...")
    data = add_indicators(data)

    print("🔍 Scanning every bar...\n")

    all_signals = []
    pattern_counts = {}

    for i in range(100, len(data)):
        signals = check_signals(data, i)

        if signals:
            timestamp = data.index[i]
            price = float(data.iloc[i]['Close'])

            # Take first signal only (avoid duplicates on same bar)
            primary_signal = signals[0]

            all_signals.append({
                'timestamp': timestamp,
                'price': price,
                'pattern': primary_signal,
                'all_patterns': signals
            })

            for pattern in signals:
                pattern_counts[pattern] = pattern_counts.get(pattern, 0) + 1

    print(f"{'='*80}")
    print(f"RESULTS")
    print(f"{'='*80}\n")

    print(f"Total bars scanned: {len(data) - 100}")
    print(f"Total signals found: {len(all_signals)}")
    print(f"Signal frequency: {len(all_signals) / (len(data) - 100) * 100:.1f}% of bars")
    print(f"Signals per day: {len(all_signals) / 30:.1f}")
    print(f"Signals per month (30 days): {len(all_signals)}")

    print(f"\n📊 BY PATTERN:")
    for pattern, count in sorted(pattern_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"  {pattern:20s}: {count:4d} times")

    print(f"\n📅 FIRST 10 SIGNALS:")
    for i, sig in enumerate(all_signals[:10], 1):
        print(f"{i:2d}. {sig['timestamp'].strftime('%m-%d %H:%M')} | ${sig['price']:>8.2f} | {sig['pattern']}")

    print(f"\n{'='*80}")
    print(f"CONCLUSION")
    print(f"{'='*80}")
    print(f"""
✅ Found {len(all_signals)} signals in 30 days
✅ That's {len(all_signals) / 30:.1f} signals per day
✅ Or ~{len(all_signals)} signals per month

This is with ONE instrument (Gold) only.
With Gold + Silver = ~{len(all_signals) * 2} signals/month

This is REALISTIC frequency for automated scanner.
    """)


if __name__ == "__main__":
    main()
