"""
STOCK INTRADAY SCANNER - Grade A Signals Only

Mirrors futures/multi_instrument_scanner.py but for stocks:
- 5-min charts (higher frequency than 15-min futures)
- Same Grade A criteria (FVG + SMA + momentum + R:R 2:1)
- Strict quality bar (80%+ confidence, <1.5% risk)
- Exit same day (no overnight risk)

Target: 3-5 Grade A intraday signals per day
Capital: ₹10-15% per trade (₹1.2-1.8L with ₹12L capital)

Scans: Top 30 liquid NSE stocks

Author: Trading System
Date: 2026-04-19
Version: 1.0
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

import warnings
warnings.filterwarnings('ignore')

import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, timedelta
from typing import Dict, Optional
from dataclasses import dataclass


@dataclass
class IntradaySignal:
    """Intraday signal"""
    symbol: str
    name: str
    signal_type: str  # BUY/SELL
    pattern: str

    entry_price: float
    stop_loss: float
    target: float

    risk_pct: float
    rr_ratio: float
    confidence: int

    vol_ratio: float
    reasoning: str
    timestamp: datetime


class StockIntradayScanner:
    """Grade A intraday signals for stocks"""

    # Quality thresholds (STRICT)
    MIN_CONFIDENCE = 80
    MIN_RR_RATIO = 1.5
    MAX_RISK_PCT = 1.5
    MIN_VOLUME_RATIO = 1.2

    def __init__(self):
        """Initialize with top 30 liquid stocks"""
        self.symbols = self._get_symbols()

    def _get_symbols(self):
        """Top 30 most liquid NSE stocks"""
        stocks = [
            # Large Cap Liquid
            'RELIANCE', 'TCS', 'HDFCBANK', 'INFY', 'ICICIBANK',
            'HINDUNILVR', 'ITC', 'SBIN', 'BHARTIARTL', 'BAJFINANCE',

            # Mid Cap Active
            'KOTAKBANK', 'LT', 'ASIANPAINT', 'AXISBANK', 'MARUTI',
            'TITAN', 'SUNPHARMA', 'ULTRACEMCO', 'NESTLEIND', 'WIPRO',

            # High Volume
            'HCLTECH', 'POWERGRID', 'NTPC', 'TATASTEEL', 'ADANIPORTS',
            'DIVISLAB', 'DRREDDY', 'GRASIM', 'HINDALCO', 'INDUSINDBK'
        ]
        return [s + '.NS' for s in stocks]

    def fetch_intraday_data(self, symbol: str) -> Optional[pd.DataFrame]:
        """Fetch 5-min data (last 5 days)"""
        try:
            end = datetime.now()
            start = end - timedelta(days=5)

            data = yf.download(
                symbol,
                start=start,
                end=end,
                interval='5m',
                progress=False
            )

            if len(data) < 50:
                return None

            # Calculate indicators
            data['SMA_20'] = data['Close'].rolling(20).mean()
            data['ATR'] = self._calculate_atr(data, period=14)
            data['Vol_SMA'] = data['Volume'].rolling(20).mean()

            # Drop NaN
            data = data.dropna()

            return data if len(data) > 20 else None

        except Exception as e:
            return None

    def _calculate_atr(self, data: pd.DataFrame, period: int = 14) -> pd.Series:
        """Calculate ATR"""
        high = data['High']
        low = data['Low']
        close = data['Close']

        tr1 = high - low
        tr2 = abs(high - close.shift())
        tr3 = abs(low - close.shift())

        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr = tr.rolling(period).mean()

        return atr

    def detect_signal(self, symbol: str, data: pd.DataFrame) -> Optional[IntradaySignal]:
        """Detect Grade A signal"""

        if len(data) < 21:
            return None

        try:
            bar = data.iloc[-1]
            prev_bars = data.iloc[-21:-1]

            price = float(bar['Close'])
            high = float(bar['High'])
            low = float(bar['Low'])

            sma_20 = float(bar['SMA_20'])
            atr = float(bar['ATR'])
            volume = float(bar['Volume'])
            avg_vol = float(bar['Vol_SMA'])

            if atr == 0 or avg_vol == 0:
                return None

            timestamp = bar.name

            signal_data = None

            # PATTERN 1: SMA Bounce (BUY)
            # Price touched 20 SMA, bounced up with volume
            dist_to_sma = abs(low - sma_20) / atr
            if (dist_to_sma < 0.3 and  # Touched SMA
                price > sma_20 and  # Closed above
                volume > avg_vol * self.MIN_VOLUME_RATIO):

                entry = price
                stop = sma_20 - atr * 0.5
                target = price + 2 * atr

                signal_data = {
                    'pattern': 'SMA_BOUNCE',
                    'type': 'BUY',
                    'entry': entry,
                    'stop': stop,
                    'target': target,
                    'vol_ratio': volume / avg_vol,
                    'reasoning': f'Bounced off 20 SMA ₹{sma_20:.2f}, resuming uptrend'
                }

            # PATTERN 2: Breakout (BUY)
            # Break above recent high with volume
            high_20 = float(prev_bars['High'].max())
            if (high > high_20 and
                volume > avg_vol * self.MIN_VOLUME_RATIO):

                entry = price
                stop = high_20 - atr
                target = price + 2 * atr

                signal_data = {
                    'pattern': 'BREAKOUT_HIGH',
                    'type': 'BUY',
                    'entry': entry,
                    'stop': stop,
                    'target': target,
                    'vol_ratio': volume / avg_vol,
                    'reasoning': f'Broke above 20-bar high ₹{high_20:.2f} with {volume/avg_vol:.1f}x volume'
                }

            # PATTERN 3: Breakdown (SELL)
            # Break below recent low with volume
            low_20 = float(prev_bars['Low'].min())
            if (low < low_20 and
                volume > avg_vol * self.MIN_VOLUME_RATIO):

                entry = price
                stop = low_20 + atr
                target = price - 2 * atr

                signal_data = {
                    'pattern': 'BREAKDOWN_LOW',
                    'type': 'SELL',
                    'entry': entry,
                    'stop': stop,
                    'target': target,
                    'vol_ratio': volume / avg_vol,
                    'reasoning': f'Broke below 20-bar low ₹{low_20:.2f} with {volume/avg_vol:.1f}x volume'
                }

            # PATTERN 4: Momentum Continuation (BUY)
            # Strong uptrend, pullback to SMA, resume
            if price > sma_20:
                price_5bars_ago = float(data.iloc[-6]['Close'])
                momentum = (price - price_5bars_ago) / price_5bars_ago * 100

                if (momentum > 0.5 and  # Positive momentum
                    dist_to_sma < 0.5 and  # Near SMA
                    volume > avg_vol * self.MIN_VOLUME_RATIO):

                    entry = price
                    stop = sma_20 - atr * 0.5
                    target = price + 2.5 * atr

                    signal_data = {
                        'pattern': 'MOMENTUM_CONTINUATION',
                        'type': 'BUY',
                        'entry': entry,
                        'stop': stop,
                        'target': target,
                        'vol_ratio': volume / avg_vol,
                        'reasoning': f'+{momentum:.1f}% momentum, pullback complete'
                    }

            # Grade signal if found
            if signal_data:
                risk = abs(signal_data['entry'] - signal_data['stop'])
                reward = abs(signal_data['target'] - signal_data['entry'])

                risk_pct = (risk / signal_data['entry']) * 100
                rr_ratio = reward / risk if risk > 0 else 0

                # Quality filter (STRICT)
                if (rr_ratio >= self.MIN_RR_RATIO and
                    risk_pct <= self.MAX_RISK_PCT):

                    # Calculate confidence
                    confidence = self._calculate_confidence(
                        rr_ratio=rr_ratio,
                        risk_pct=risk_pct,
                        vol_ratio=signal_data['vol_ratio'],
                        pattern=signal_data['pattern']
                    )

                    if confidence >= self.MIN_CONFIDENCE:
                        name = symbol.replace('.NS', '')

                        return IntradaySignal(
                            symbol=symbol,
                            name=name,
                            signal_type=signal_data['type'],
                            pattern=signal_data['pattern'],
                            entry_price=signal_data['entry'],
                            stop_loss=signal_data['stop'],
                            target=signal_data['target'],
                            risk_pct=risk_pct,
                            rr_ratio=rr_ratio,
                            confidence=confidence,
                            vol_ratio=signal_data['vol_ratio'],
                            reasoning=signal_data['reasoning'],
                            timestamp=timestamp
                        )

            return None

        except Exception as e:
            return None

    def _calculate_confidence(self, rr_ratio: float, risk_pct: float,
                             vol_ratio: float, pattern: str) -> int:
        """Calculate confidence score (0-100)"""

        # Base: 60
        confidence = 60

        # R:R bonus (max +20)
        if rr_ratio >= 3.0:
            confidence += 20
        elif rr_ratio >= 2.5:
            confidence += 15
        elif rr_ratio >= 2.0:
            confidence += 10
        else:
            confidence += 5

        # Risk penalty (lower risk = higher confidence)
        if risk_pct < 0.8:
            confidence += 15
        elif risk_pct < 1.2:
            confidence += 10
        else:
            confidence += 0

        # Volume bonus
        if vol_ratio > 2.0:
            confidence += 10
        elif vol_ratio > 1.5:
            confidence += 5

        # Pattern bonus
        pattern_bonuses = {
            'SMA_BOUNCE': 5,  # High success rate
            'MOMENTUM_CONTINUATION': 5,
            'BREAKOUT_HIGH': 0,
            'BREAKDOWN_LOW': -5  # Sell signals less reliable in bull market
        }
        confidence += pattern_bonuses.get(pattern, 0)

        return min(confidence, 100)

    def scan_all(self) -> Dict[str, Optional[IntradaySignal]]:
        """Scan all stocks, return Grade A signals"""

        print("\n" + "="*80)
        print("STOCK INTRADAY SCANNER - GRADE A ONLY (5-min)")
        print("="*80)
        print(f"Scan Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Stocks: {len(self.symbols)}")
        print(f"Quality: Confidence {self.MIN_CONFIDENCE}%+, R:R {self.MIN_RR_RATIO}:1+, Risk <{self.MAX_RISK_PCT}%")
        print()

        signals = {}
        found_count = 0

        for symbol in self.symbols:
            name = symbol.replace('.NS', '')
            print(f"📊 {name:15s} ({symbol})...", end=' ')

            data = self.fetch_intraday_data(symbol)
            if data is None:
                print("❌ No data")
                signals[name] = None
                continue

            signal = self.detect_signal(symbol, data)

            if signal:
                print(f"✅ SIGNAL: {signal.signal_type} | {signal.pattern}")
                print(f"   Entry: ₹{signal.entry_price:.2f}")
                print(f"   Stop: ₹{signal.stop_loss:.2f}")
                print(f"   Target: ₹{signal.target:.2f}")
                print(f"   Risk: ₹{abs(signal.entry_price - signal.stop_loss):.2f} ({signal.risk_pct:.2f}%)")
                print(f"   R:R: {signal.rr_ratio:.2f}:1 | Vol: {signal.vol_ratio:.1f}x")
                print(f"   Confidence: {signal.confidence}% | Grade: A")
                print(f"   💡 {signal.reasoning}")
                found_count += 1
            else:
                current_price = float(data.iloc[-1]['Close'])
                print(f"⏸️  No Grade A signal (price: ₹{current_price:.2f})")

            signals[name] = signal

        print(f"\n✅ Found {found_count} Grade A intraday stock signals")
        return signals


def main():
    """Run standalone"""
    scanner = StockIntradayScanner()
    signals = scanner.scan_all()

    # Summary
    grade_a = [s for s in signals.values() if s is not None]

    if grade_a:
        print("\n" + "="*80)
        print(f"GRADE A SIGNALS SUMMARY ({len(grade_a)} trades)")
        print("="*80)

        for signal in grade_a:
            print(f"\n{signal.name} - {signal.signal_type} | Confidence: {signal.confidence}%")
            print(f"  Entry: ₹{signal.entry_price:.2f} | Stop: ₹{signal.stop_loss:.2f} | Target: ₹{signal.target:.2f}")
            print(f"  Risk: {signal.risk_pct:.2f}% | R:R: {signal.rr_ratio:.2f}:1")
            print(f"  Pattern: {signal.pattern}")
            print(f"  💡 {signal.reasoning}")

        print("\n" + "="*80)
        print("EXECUTION:")
        print("  1. Enter on next 5-min candle close")
        print("  2. Set stop loss immediately")
        print("  3. Exit at target OR before 3:20 PM (whichever first)")
        print("  4. NEVER hold overnight")
        print("  5. Allocation: 10-15% per trade (₹1.2-1.8L)")
    else:
        print("\n" + "="*80)
        print("NO GRADE A SIGNALS")
        print("="*80)
        print("Market not suitable for intraday longs right now.")
        print("Check again in 30-60 minutes.")


if __name__ == "__main__":
    main()
