"""
TIGHT STOP SCANNER - Accept Tight Stops for V-Recovery Setups

For stocks in V-shaped recovery:
- Sharp drop then fast bounce
- Now above 20 SMA
- 10-day low is far away
- Use 20 SMA as stop (TIGHT)

Trade-off:
- Better R:R (1.5:1+)
- Lower risk per trade (3-6%)
- BUT higher stop-out rate (40-50% instead of 30%)

When to use:
- When you see good setups but scanner rejects them
- When you're okay with frequent small losses
- When you want to catch V-recoveries

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
from typing import List, Dict, Optional
from dataclasses import dataclass


@dataclass
class Trade:
    """Trade setup"""
    rank: int
    symbol: str
    name: str
    price: float
    setup: str

    entry: float
    stop_loss: float
    target_1: float
    target_2: float

    risk_per_share: float
    rr_ratio: float

    # For ₹10L capital, 2% risk
    shares: int
    position_value: float

    # Indicators
    rsi: float
    price_vs_20sma_pct: float
    price_change_5d: float
    distance_from_high: float

    reasoning: str


class TightStopScanner:
    """Use tight stops (20 SMA only) for aggressive entries"""

    def __init__(self, capital: float = 10_00_000):
        self.capital = capital
        self.risk_per_trade = capital * 0.02

        # Include the stocks you mentioned + top 50
        self.symbols = self._get_symbols()

    def _get_symbols(self) -> List[str]:
        """Top 50 + specific stocks"""
        symbols = [
            # Your specific stocks
            'SOBHA', 'INDUSINDBK', 'SBIN',

            # Large Cap Liquids
            'RELIANCE', 'TCS', 'HDFCBANK', 'INFY', 'ICICIBANK',
            'HINDUNILVR', 'ITC', 'BHARTIARTL', 'BAJFINANCE',
            'KOTAKBANK', 'LT', 'ASIANPAINT', 'AXISBANK', 'MARUTI',
            'TITAN', 'SUNPHARMA', 'ULTRACEMCO', 'NESTLEIND', 'WIPRO',

            # Mid Cap Momentum
            'HCLTECH', 'POWERGRID', 'NTPC', 'TATASTEEL', 'ADANIPORTS',
            'DIVISLAB', 'DRREDDY', 'GRASIM', 'HINDALCO',
            'JSWSTEEL', 'M&M', 'ONGC', 'TECHM', 'TATACONSUM',
            'CIPLA', 'EICHERMOT', 'GODREJCP', 'HEROMOTOCO', 'BAJAJFINSV',

            # Active Traders
            'BRITANNIA', 'COALINDIA', 'APOLLOHOSP', 'PIDILITIND', 'HAVELLS',
            'BERGEPAINT', 'DABUR', 'MARICO', 'TATAPOWER', 'TATACHEM'
        ]
        return [s + '.NS' for s in symbols]

    def fetch_data(self, symbol: str) -> Optional[pd.DataFrame]:
        """Fetch data"""
        try:
            end = datetime.now()
            start = end - timedelta(days=60)
            data = yf.download(symbol, start=start, end=end, progress=False)
            return data if len(data) > 20 else None
        except:
            return None

    def calculate_rsi(self, prices: pd.Series, period: int = 14) -> float:
        """Calculate RSI"""
        try:
            delta = prices.diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            return float(rsi.iloc[-1])
        except:
            return 50

    def find_setup(self, data: pd.DataFrame, symbol: str) -> Optional[Trade]:
        """Find setup with TIGHT stop (20 SMA only)"""

        if len(data) < 20:
            return None

        try:
            # Current state
            current = data.iloc[-1]
            price = float(current['Close'])

            if price < 50:  # Skip only penny stocks
                return None

            # Basic indicators
            sma_20 = data['Close'].rolling(20).mean()
            sma_20_val = float(sma_20.iloc[-1])

            # Metrics
            rsi = self.calculate_rsi(data['Close'])

            price_5d_ago = float(data['Close'].iloc[-5]) if len(data) >= 5 else price
            change_5d = ((price - price_5d_ago) / price_5d_ago) * 100

            # Distance from 20 SMA
            dist_20_pct = ((price - sma_20_val) / sma_20_val) * 100

            # Distance from high
            high_52w = float(data['High'].rolling(min(252, len(data))).max().iloc[-1])
            dist_from_high = ((high_52w - price) / high_52w) * 100

            name = symbol.replace('.NS', '')

            # TIGHT STOP SETUP
            # Criteria:
            # 1. Price > 20 SMA (uptrend)
            # 2. Any momentum
            # 3. RSI not overbought
            # 4. Use ONLY 20 SMA as stop (tight)

            if price > sma_20_val and change_5d > -2 and rsi < 75:
                # Entry: At market
                entry = price

                # Stop: ONLY below 20 SMA (TIGHT)
                stop = sma_20_val * 0.97

                # Targets: 6% and 10%
                t1 = price * 1.06
                t2 = price * 1.10

                risk = entry - stop
                rr = (t1 - entry) / risk if risk > 0 else 0

                # Accept if:
                # - R:R >= 1.3 (slightly higher because tighter stop = more stop-outs)
                # - Risk per share < 8%
                if rr >= 1.3 and risk / entry < 0.08:
                    shares = int(self.risk_per_trade / risk) if risk > 0 else 0
                    if shares > 0 and shares * entry < self.capital * 0.5:

                        # Reasoning
                        momentum_str = f"+{change_5d:.1f}%" if change_5d > 0 else f"{change_5d:.1f}%"

                        return Trade(
                            rank=0, symbol=symbol, name=name, price=price,
                            setup='TIGHT_STOP',
                            entry=entry, stop_loss=stop, target_1=t1, target_2=t2,
                            risk_per_share=risk, rr_ratio=rr,
                            shares=shares, position_value=shares * entry,
                            rsi=rsi,
                            price_vs_20sma_pct=dist_20_pct,
                            price_change_5d=change_5d,
                            distance_from_high=dist_from_high,
                            reasoning=f'{dist_20_pct:+.1f}% above 20 SMA, {momentum_str} momentum, RSI {rsi:.0f}'
                        )

            return None

        except Exception as e:
            return None

    def scan_all(self, top_n: int = 15) -> List[Trade]:
        """Scan and find TOP trades"""
        print(f"\n{'='*80}")
        print(f"TIGHT STOP SCANNER - V-RECOVERY SETUPS")
        print(f"{'='*80}")
        print(f"Stop: Below 20 SMA ONLY (ignoring 10d low)")
        print(f"Risk: 3-6% per trade (tight)")
        print(f"R:R: 1.3:1+ required")
        print(f"Scanning {len(self.symbols)} stocks...\n")

        all_trades = []
        scanned = 0

        for symbol in self.symbols:
            scanned += 1
            if scanned % 10 == 0:
                print(f"  Progress: {scanned}/{len(self.symbols)}...")

            data = self.fetch_data(symbol)
            if data is None:
                continue

            trade = self.find_setup(data, symbol)
            if trade:
                all_trades.append(trade)

        print(f"\n✅ Found {len(all_trades)} setups\n")

        # Sort by R:R ratio
        all_trades.sort(key=lambda t: t.rr_ratio, reverse=True)

        # Assign ranks
        for i, trade in enumerate(all_trades[:top_n], 1):
            trade.rank = i

        return all_trades[:top_n]

    def display_trades(self, trades: List[Trade]):
        """Display trades"""
        if not trades:
            print("❌ No trades with tight stops either")
            print("   Market likely in downtrend")
            return

        print(f"{'='*80}")
        print(f"🎯 TOP {len(trades)} TIGHT STOP TRADES")
        print(f"{'='*80}\n")

        for t in trades:
            print(f"{t.rank}. {t.name} | ₹{t.price:.2f} | {t.setup}")
            print(f"   📍 Entry: ₹{t.entry:.2f} (AT MARKET)")
            print(f"   🛡️  Stop:  ₹{t.stop_loss:.2f} (₹{t.risk_per_share:.2f} risk, {(t.risk_per_share/t.entry)*100:.1f}%)")
            print(f"   🎯 Target 1: ₹{t.target_1:.2f} (+{((t.target_1/t.entry-1)*100):.1f}%)")
            print(f"   🎯 Target 2: ₹{t.target_2:.2f} (+{((t.target_2/t.entry-1)*100):.1f}%)")
            print(f"   📊 R:R: {t.rr_ratio:.2f}:1 | RSI: {t.rsi:.0f}")
            print(f"   💰 Position: {t.shares:,} shares = ₹{t.position_value:,.0f}")
            print(f"   💡 {t.reasoning} | {t.distance_from_high:.1f}% from high")
            print()

        # Summary
        total_allocation = sum(t.position_value for t in trades)
        print(f"{'='*80}")
        print(f"PORTFOLIO: ₹{total_allocation:,.0f} allocated ({total_allocation/self.capital*100:.1f}%)")
        print(f"Risk: ₹{len(trades) * self.risk_per_trade:,.0f} ({len(trades)*2:.0f}%)")
        print(f"Avg R:R: {np.mean([t.rr_ratio for t in trades]):.2f}:1")

        print(f"\n⚠️  TIGHT STOP WARNING:")
        print(f"""
Tight stops (below 20 SMA) have trade-offs:

PROS:
✅ Better R:R ratios (1.5-2:1)
✅ Lower risk per trade (3-6%)
✅ Can catch V-shaped recoveries early

CONS:
❌ Higher stop-out rate (~40-50%)
❌ Normal pullbacks will stop you out
❌ Need higher win rate to be profitable

USE WHEN:
- You see clear uptrend (price well above 20 SMA)
- Strong momentum (RSI 60-70)
- You're okay with frequent small losses
- You want aggressive entries

AVOID WHEN:
- Choppy/sideways market
- Price barely above 20 SMA
- Low momentum
        """)


def main():
    scanner = TightStopScanner(capital=10_00_000)
    trades = scanner.scan_all(top_n=15)
    scanner.display_trades(trades)

    if len(trades) > 0:
        print(f"\n📋 HOW TO EXECUTE:")
        print(f"""
1. Enter at market (don't wait)
2. Set GTT SL immediately at stop level
3. Watch first 2-3 days closely
4. If pullback to 20 SMA, may get stopped (accept it)
5. If moves up, trail stop to entry +2% after 3 days
6. Exit 50% at T1, trail rest
        """)


if __name__ == "__main__":
    main()
