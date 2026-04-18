"""
WIDER TARGET SCANNER - For Mid-Uptrend Stocks

For stocks that have already moved (3-6% above 20 SMA):
- Can't use tight targets (6%) = bad R:R
- Solution: Use wider targets (8-12%)
- Longer hold time (2-3 weeks instead of 1-2 weeks)

This catches stocks in mid-uptrend that still have room to run.

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

    reasoning: str


class WiderTargetScanner:
    """Use wider targets (8-12%) for mid-uptrend stocks"""

    def __init__(self, capital: float = 10_00_000):
        self.capital = capital
        self.risk_per_trade = capital * 0.02

        self.symbols = self._get_symbols()

    def _get_symbols(self) -> List[str]:
        """Top 50 + your stocks"""
        symbols = [
            # Your specific stocks
            'SOBHA', 'INDUSINDBK', 'SBIN',

            # Large Cap
            'RELIANCE', 'TCS', 'HDFCBANK', 'INFY', 'ICICIBANK',
            'HINDUNILVR', 'ITC', 'BHARTIARTL', 'BAJFINANCE',
            'KOTAKBANK', 'LT', 'ASIANPAINT', 'AXISBANK', 'MARUTI',
            'TITAN', 'SUNPHARMA', 'ULTRACEMCO', 'NESTLEIND', 'WIPRO',

            # Mid Cap
            'HCLTECH', 'POWERGRID', 'NTPC', 'TATASTEEL', 'ADANIPORTS',
            'DIVISLAB', 'DRREDDY', 'GRASIM', 'HINDALCO',
            'JSWSTEEL', 'M&M', 'ONGC', 'TECHM', 'TATACONSUM',
            'CIPLA', 'EICHERMOT', 'GODREJCP', 'HEROMOTOCO', 'BAJAJFINSV',

            # Active
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
        """Find mid-uptrend setup with wider targets"""

        if len(data) < 20:
            return None

        try:
            current = data.iloc[-1]
            price = float(current['Close'])

            if price < 50:
                return None

            sma_20 = data['Close'].rolling(20).mean()
            sma_20_val = float(sma_20.iloc[-1])

            rsi = self.calculate_rsi(data['Close'])

            price_5d_ago = float(data['Close'].iloc[-5]) if len(data) >= 5 else price
            change_5d = ((price - price_5d_ago) / price_5d_ago) * 100

            dist_20_pct = ((price - sma_20_val) / sma_20_val) * 100

            name = symbol.replace('.NS', '')

            # MID-UPTREND SETUP
            # Criteria:
            # 1. Price > 20 SMA (uptrend)
            # 2. Price 2-8% above 20 SMA (mid-uptrend, not early)
            # 3. RSI not overbought
            # 4. Wider targets (8% and 12%)

            if price > sma_20_val and 2 <= dist_20_pct <= 8 and rsi < 75:
                # Entry: At market
                entry = price

                # Stop: Below 20 SMA
                stop = sma_20_val * 0.97

                # Targets: WIDER (8% and 12% instead of 6% and 10%)
                t1 = price * 1.08   # 8% gain
                t2 = price * 1.12   # 12% gain

                risk = entry - stop
                rr = (t1 - entry) / risk if risk > 0 else 0

                # Accept if:
                # - R:R >= 1.2
                # - Risk < 9%
                if rr >= 1.2 and risk / entry < 0.09:
                    shares = int(self.risk_per_trade / risk) if risk > 0 else 0
                    if shares > 0 and shares * entry < self.capital * 0.5:

                        momentum_str = f"+{change_5d:.1f}%" if change_5d > 0 else f"{change_5d:.1f}%"

                        return Trade(
                            rank=0, symbol=symbol, name=name, price=price,
                            setup='MID_UPTREND',
                            entry=entry, stop_loss=stop, target_1=t1, target_2=t2,
                            risk_per_share=risk, rr_ratio=rr,
                            shares=shares, position_value=shares * entry,
                            rsi=rsi,
                            price_vs_20sma_pct=dist_20_pct,
                            price_change_5d=change_5d,
                            reasoning=f'{dist_20_pct:+.1f}% above 20 SMA (mid-uptrend), {momentum_str} momentum, RSI {rsi:.0f}'
                        )

            return None

        except Exception as e:
            return None

    def scan_all(self, top_n: int = 15) -> List[Trade]:
        """Scan"""
        print(f"\n{'='*80}")
        print(f"WIDER TARGET SCANNER - MID-UPTREND TRADES")
        print(f"{'='*80}")
        print(f"For stocks 2-8% above 20 SMA (already moved)")
        print(f"Targets: 8% and 12% (wider than usual)")
        print(f"Hold time: 2-3 weeks")
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

        # Sort by R:R
        all_trades.sort(key=lambda t: t.rr_ratio, reverse=True)

        for i, trade in enumerate(all_trades[:top_n], 1):
            trade.rank = i

        return all_trades[:top_n]

    def display_trades(self, trades: List[Trade]):
        """Display"""
        if not trades:
            print("❌ No mid-uptrend trades found")
            return

        print(f"{'='*80}")
        print(f"🎯 TOP {len(trades)} MID-UPTREND TRADES (WIDER TARGETS)")
        print(f"{'='*80}\n")

        for t in trades:
            print(f"{t.rank}. {t.name} | ₹{t.price:.2f} | {t.setup}")
            print(f"   📍 Entry: ₹{t.entry:.2f}")
            print(f"   🛡️  Stop:  ₹{t.stop_loss:.2f} (₹{t.risk_per_share:.2f} risk, {(t.risk_per_share/t.entry)*100:.1f}%)")
            print(f"   🎯 Target 1: ₹{t.target_1:.2f} (+{((t.target_1/t.entry-1)*100):.1f}%)")
            print(f"   🎯 Target 2: ₹{t.target_2:.2f} (+{((t.target_2/t.entry-1)*100):.1f}%)")
            print(f"   📊 R:R: {t.rr_ratio:.2f}:1 | RSI: {t.rsi:.0f}")
            print(f"   💰 Position: {t.shares:,} shares = ₹{t.position_value:,.0f}")
            print(f"   💡 {t.reasoning}")
            print()

        total_allocation = sum(t.position_value for t in trades)
        print(f"{'='*80}")
        print(f"PORTFOLIO: ₹{total_allocation:,.0f} allocated ({total_allocation/self.capital*100:.1f}%)")
        print(f"Risk: ₹{len(trades) * self.risk_per_trade:,.0f} ({len(trades)*2:.0f}%)")
        print(f"Avg R:R: {np.mean([t.rr_ratio for t in trades]):.2f}:1")


def main():
    scanner = WiderTargetScanner(capital=10_00_000)
    trades = scanner.scan_all(top_n=15)
    scanner.display_trades(trades)

    if len(trades) > 0:
        print(f"\n💡 MID-UPTREND TRADES:")
        print(f"""
These stocks have already moved 3-6% above 20 SMA.
You're NOT catching the bottom, but joining mid-move.

PROS:
✅ Trend confirmed (less whipsaw)
✅ Momentum established
✅ 8-12% targets still achievable

CONS:
❌ Missed first 3-5% of move
❌ Need bigger move to hit targets (2-3 weeks)
❌ If reversal starts, you're late

WHEN TO USE:
- When early entries not available
- When you want confirmed trends
- When you're okay with partial gains
        """)


if __name__ == "__main__":
    main()
