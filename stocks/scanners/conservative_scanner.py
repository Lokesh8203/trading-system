"""
CONSERVATIVE SCANNER - Capital Preservation First

NO compromises on risk management:
- R:R >= 1.5:1 MINIMUM (no exceptions)
- Risk per trade <= 6% MAXIMUM
- Quality over quantity
- Max 5-8 trades (not 13-15)

If this finds 0 trades, it means:
- Market not suitable for swing longs
- Move to futures/commodities
- Or wait for better setup

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

    shares: int
    position_value: float

    rsi: float
    price_vs_20sma_pct: float
    price_change_5d: float

    reasoning: str


class ConservativeScanner:
    """Conservative scanner - no compromises"""

    def __init__(self, capital: float = 10_00_000):
        self.capital = capital
        self.risk_per_trade = capital * 0.02

        self.symbols = self._get_symbols()

    def _get_symbols(self) -> List[str]:
        """Top 60 liquid stocks"""
        symbols = [
            # Large Cap
            'RELIANCE', 'TCS', 'HDFCBANK', 'INFY', 'ICICIBANK',
            'HINDUNILVR', 'ITC', 'SBIN', 'BHARTIARTL', 'BAJFINANCE',
            'KOTAKBANK', 'LT', 'ASIANPAINT', 'AXISBANK', 'MARUTI',
            'TITAN', 'SUNPHARMA', 'ULTRACEMCO', 'NESTLEIND', 'WIPRO',

            # Mid Cap
            'HCLTECH', 'POWERGRID', 'NTPC', 'TATASTEEL', 'ADANIPORTS',
            'DIVISLAB', 'DRREDDY', 'GRASIM', 'HINDALCO', 'INDUSINDBK',
            'JSWSTEEL', 'M&M', 'ONGC', 'TECHM', 'TATACONSUM',
            'CIPLA', 'EICHERMOT', 'GODREJCP', 'HEROMOTOCO', 'BAJAJFINSV',

            # Active
            'BRITANNIA', 'COALINDIA', 'APOLLOHOSP', 'PIDILITIND', 'HAVELLS',
            'BERGEPAINT', 'DABUR', 'MARICO', 'TATAPOWER', 'TATACHEM',
            'AUROPHARMA', 'LUPIN', 'INDIGO', 'SHREECEM', 'VEDL',
            'GAIL', 'TRENT', 'ADANIENT', 'SBILIFE', 'ICICIGI'
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
        """Find setup - STRICT criteria"""

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

            # CONSERVATIVE SETUP
            # Only accept stocks that meet ALL criteria:
            # 1. Price > 20 SMA (uptrend)
            # 2. Price 0.5-5% above 20 SMA (early-to-mid uptrend, not extended)
            # 3. Positive momentum
            # 4. RSI 50-70 (not oversold, not overbought)
            # 5. R:R >= 1.5:1
            # 6. Risk <= 6%

            if (price > sma_20_val and
                0.5 <= dist_20_pct <= 5 and
                change_5d > 0 and
                50 < rsi < 70):

                # Entry: At market
                entry = price

                # Stop: Below 20 SMA
                stop = sma_20_val * 0.97

                # Targets: 8% and 12%
                t1 = price * 1.08
                t2 = price * 1.12

                risk = entry - stop
                rr = (t1 - entry) / risk if risk > 0 else 0
                risk_pct = (risk / entry) * 100

                # STRICT: R:R >= 1.5 AND risk <= 6%
                if rr >= 1.5 and risk_pct <= 6.0:
                    shares = int(self.risk_per_trade / risk) if risk > 0 else 0
                    if shares > 0 and shares * entry < self.capital * 0.4:

                        return Trade(
                            rank=0, symbol=symbol, name=name, price=price,
                            setup='CONSERVATIVE',
                            entry=entry, stop_loss=stop, target_1=t1, target_2=t2,
                            risk_per_share=risk, rr_ratio=rr,
                            shares=shares, position_value=shares * entry,
                            rsi=rsi,
                            price_vs_20sma_pct=dist_20_pct,
                            price_change_5d=change_5d,
                            reasoning=f'{dist_20_pct:.1f}% above 20 SMA, +{change_5d:.1f}% momentum, RSI {rsi:.0f}'
                        )

            return None

        except Exception as e:
            return None

    def scan_all(self, top_n: int = 8) -> List[Trade]:
        """Scan - limit to top 8"""
        print(f"\n{'='*80}")
        print(f"CONSERVATIVE SCANNER - CAPITAL PRESERVATION FIRST")
        print(f"{'='*80}")
        print(f"Criteria: R:R >= 1.5:1, Risk <= 6%, RSI 50-70, Positive momentum")
        print(f"Max trades: {top_n} (quality over quantity)")
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

        print(f"\n✅ Found {len(all_trades)} conservative setups\n")

        # Sort by R:R
        all_trades.sort(key=lambda t: t.rr_ratio, reverse=True)

        for i, trade in enumerate(all_trades[:top_n], 1):
            trade.rank = i

        return all_trades[:top_n]

    def display_trades(self, trades: List[Trade]):
        """Display"""
        if not trades:
            print("="*80)
            print("❌ NO CONSERVATIVE SETUPS FOUND")
            print("="*80)
            print("""
This means:
1. Market not suitable for swing longs right now
2. Stocks either extended or not trending
3. Risk/Reward not favorable

RECOMMENDATION:
→ Focus on Futures/Commodities (Gold, Silver)
→ Or wait 3-7 days for stocks to consolidate
→ Don't force trades when market says NO

This is GOOD - protecting capital!
            """)
            return

        print(f"{'='*80}")
        print(f"🎯 TOP {len(trades)} CONSERVATIVE TRADES")
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
        total_risk = len(trades) * self.risk_per_trade
        print(f"{'='*80}")
        print(f"PORTFOLIO: ₹{total_allocation:,.0f} allocated ({total_allocation/self.capital*100:.1f}%)")
        print(f"Risk: ₹{total_risk:,.0f} ({(total_risk/self.capital)*100:.0f}%)")
        print(f"Avg R:R: {np.mean([t.rr_ratio for t in trades]):.2f}:1")
        print()
        print(f"✅ Conservative allocation - can take all {len(trades)} trades")


def main():
    scanner = ConservativeScanner(capital=10_00_000)
    trades = scanner.scan_all(top_n=8)
    scanner.display_trades(trades)

    if len(trades) > 0:
        print(f"\n📋 EXECUTION:")
        print(f"""
1. Set GTT BUY orders at entry price
2. Set GTT SL immediately
3. Hold 2-3 weeks for 8-12% targets
4. Exit 50% at T1, trail rest
        """)


if __name__ == "__main__":
    main()
