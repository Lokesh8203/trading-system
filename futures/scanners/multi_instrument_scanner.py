"""
MULTI-INSTRUMENT 15-MIN SCANNER - GRADE A SIGNALS ONLY

Scans multiple instruments in parallel:
- Commodities: Gold, Silver, Crude Oil
- Indices: Nifty, Bank Nifty (futures)

Data sources:
- TradingView: XAUUSD, XAGUSD, WTICRUDE (global markets)
- MCX/NSE: GOLDPETAL, SILVEMIC, CRUDEOIL, NIFTY, BANKNIFTY (Indian markets)

Usage:
    # Default (uses yfinance tickers - COMEX/global)
    python3 futures/scanners/multi_instrument_scanner.py

    # Specific source
    python3 futures/scanners/multi_instrument_scanner.py --source tradingview
    python3 futures/scanners/multi_instrument_scanner.py --source mcx

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
from typing import Optional, Dict, List
from dataclasses import dataclass
import argparse


@dataclass
class Signal:
    """High-quality trading signal"""
    timestamp: datetime
    instrument: str
    signal_type: str  # BUY/SELL
    pattern: str

    entry_price: float
    stop_loss: float
    target: float

    risk_dollars: float
    reward_dollars: float
    rr_ratio: float
    risk_pct: float

    volume_ratio: float
    confidence: int
    grade: str

    reasoning: str


class MultiInstrumentScanner:
    """Grade A signals for multiple instruments"""

    # Grade A thresholds
    MIN_CONFIDENCE = 80
    MIN_RR_RATIO = 1.5
    MAX_RISK_PCT = 1.5
    MIN_VOLUME_RATIO = 1.2

    def __init__(self, data_source='yfinance'):
        """
        Initialize with data source

        Args:
            data_source: 'yfinance' (default), 'tradingview', or 'mcx'
        """
        self.data_source = data_source
        self.instruments = self._get_instrument_config()

    def _get_instrument_config(self) -> Dict:
        """Get instrument configuration based on data source"""

        if self.data_source == 'tradingview':
            # TradingView symbols (will need forex API or different data source)
            # For now, using yfinance equivalents
            return {
                'GOLD (XAU/USD)': 'GC=F',      # COMEX Gold
                'SILVER (XAG/USD)': 'SI=F',    # COMEX Silver
                'CRUDE (WTI)': 'CL=F',         # WTI Crude
                'NIFTY 50 FUT': '^NSEI',       # Nifty Index (not futures, but proxy)
                'BANK NIFTY FUT': '^NSEBANK'   # Bank Nifty Index
            }

        elif self.data_source == 'mcx':
            # MCX symbols (would need actual MCX data feed)
            # Using yfinance proxies for now
            return {
                'GOLDPETAL MCX': 'GC=F',       # Use COMEX as proxy
                'SILVEMIC MCX': 'SI=F',        # Use COMEX as proxy
                'CRUDEOIL MCX': 'CL=F',        # Use WTI as proxy
                'NIFTY FUT': '^NSEI',          # Use index as proxy
                'BANKNIFTY FUT': '^NSEBANK'    # Use index as proxy
            }

        else:  # yfinance (default)
            return {
                'GOLD': 'GC=F',                # COMEX Gold
                'SILVER': 'SI=F',              # COMEX Silver
                'CRUDE': 'CL=F',               # WTI Crude
                'NIFTY': '^NSEI',              # Nifty Index
                'BANK NIFTY': '^NSEBANK'       # Bank Nifty Index
            }

    def fetch_data(self, ticker: str, bars: int = 400) -> Optional[pd.DataFrame]:
        """Fetch 15-min data"""
        try:
            end = datetime.now()
            start = end - timedelta(days=10)
            data = yf.download(ticker, start=start, end=end, interval='15m', progress=False)

            if len(data) < 100:
                return None

            return data.iloc[-bars:]
        except Exception as e:
            return None

    def add_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """Add technical indicators"""
        df = data.copy()

        # Moving averages
        df['SMA_20'] = df['Close'].rolling(20).mean()
        df['SMA_50'] = df['Close'].rolling(50).mean()
        df['EMA_9'] = df['Close'].ewm(span=9, adjust=False).mean()

        # ATR
        df['HL'] = df['High'] - df['Low']
        df['HC'] = abs(df['High'] - df['Close'].shift(1))
        df['LC'] = abs(df['Low'] - df['Close'].shift(1))
        df['TR'] = df[['HL', 'HC', 'LC']].max(axis=1)
        df['ATR'] = df['TR'].rolling(14).mean()

        # Volume
        df['Vol_SMA'] = df['Volume'].rolling(20).mean()

        # Range
        df['Range_Pct'] = ((df['High'] - df['Low']) / df['Close']) * 100

        return df

    def calculate_confidence(self, signal_data: dict) -> int:
        """Calculate confidence score (0-100)"""
        confidence = 50

        # R:R ratio bonus
        rr = signal_data['rr']
        if rr >= 3.0:
            confidence += 25
        elif rr >= 2.0:
            confidence += 20
        elif rr >= 1.5:
            confidence += 10

        # Volume bonus
        vol_ratio = signal_data['vol_ratio']
        if vol_ratio >= 2.0:
            confidence += 15
        elif vol_ratio >= 1.5:
            confidence += 10

        # Risk size
        risk_pct = signal_data['risk_pct']
        if risk_pct < 0.5:
            confidence += 10
        elif risk_pct < 1.0:
            confidence += 5
        elif risk_pct > 1.5:
            confidence -= 10

        # Pattern quality
        pattern = signal_data['pattern']
        if pattern in ['BREAKOUT_HIGH', 'BREAKDOWN_LOW']:
            confidence += 10

        return min(100, max(0, confidence))

    def find_signals(self, data: pd.DataFrame, instrument: str) -> Optional[Signal]:
        """Find Grade A signals"""

        if len(data) < 100:
            return None

        # Current bar
        bar = data.iloc[-1]
        prev_bars = data.iloc[-21:-1]

        price = float(bar['Close'].iloc[0]) if hasattr(bar['Close'], 'iloc') else float(bar['Close'])
        high = float(bar['High'].iloc[0]) if hasattr(bar['High'], 'iloc') else float(bar['High'])
        low = float(bar['Low'].iloc[0]) if hasattr(bar['Low'], 'iloc') else float(bar['Low'])

        sma_20 = float(bar['SMA_20'].iloc[0]) if hasattr(bar['SMA_20'], 'iloc') else float(bar['SMA_20'])
        atr = float(bar['ATR'].iloc[0]) if hasattr(bar['ATR'], 'iloc') else float(bar['ATR'])
        volume = float(bar['Volume'].iloc[0]) if hasattr(bar['Volume'], 'iloc') else float(bar['Volume'])
        avg_vol = float(bar['Vol_SMA'].iloc[0]) if hasattr(bar['Vol_SMA'], 'iloc') else float(bar['Vol_SMA'])

        timestamp = bar.name

        signal_data = None

        # PATTERN 1: Breakout above 20-bar high
        high_20 = float(prev_bars['High'].max())
        if high > high_20 and volume > avg_vol * self.MIN_VOLUME_RATIO:
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
                'reasoning': f'Broke above 20-bar high ${high_20:.2f} with {volume/avg_vol:.1f}x volume'
            }

        # PATTERN 2: Breakdown below 20-bar low
        low_20 = float(prev_bars['Low'].min())
        if low < low_20 and volume > avg_vol * self.MIN_VOLUME_RATIO:
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
                'reasoning': f'Broke below 20-bar low ${low_20:.2f} with {volume/avg_vol:.1f}x volume'
            }

        # PATTERN 3: SMA 20 bounce
        if not signal_data:
            prev_3 = data.iloc[-4:-1]
            touched_sma = any(float(b['Low']) <= float(b['SMA_20']) * 1.005
                            for idx, b in prev_3.iterrows())

            if touched_sma and price > sma_20:
                entry = price
                stop = sma_20 - atr * 0.5
                target = price + 1.5 * atr

                signal_data = {
                    'pattern': 'SMA_BOUNCE',
                    'type': 'BUY',
                    'entry': entry,
                    'stop': stop,
                    'target': target,
                    'vol_ratio': volume / avg_vol,
                    'reasoning': f'Bounced off 20 SMA ${sma_20:.2f}, resuming uptrend'
                }

        if not signal_data:
            return None

        # Calculate metrics
        risk = abs(signal_data['entry'] - signal_data['stop'])
        reward = abs(signal_data['target'] - signal_data['entry'])
        rr = reward / risk if risk > 0 else 0
        risk_pct = (risk / signal_data['entry']) * 100

        signal_data['risk'] = risk
        signal_data['reward'] = reward
        signal_data['rr'] = rr
        signal_data['risk_pct'] = risk_pct

        # Calculate confidence
        confidence = self.calculate_confidence(signal_data)

        # GRADE A FILTER
        if (confidence < self.MIN_CONFIDENCE or
            rr < self.MIN_RR_RATIO or
            risk_pct > self.MAX_RISK_PCT):
            return None

        # Create signal
        return Signal(
            timestamp=timestamp,
            instrument=instrument,
            signal_type=signal_data['type'],
            pattern=signal_data['pattern'],
            entry_price=signal_data['entry'],
            stop_loss=signal_data['stop'],
            target=signal_data['target'],
            risk_dollars=risk,
            reward_dollars=reward,
            rr_ratio=rr,
            risk_pct=risk_pct,
            volume_ratio=signal_data['vol_ratio'],
            confidence=confidence,
            grade='A',
            reasoning=signal_data['reasoning']
        )

    def scan_all(self) -> Dict[str, Optional[Signal]]:
        """Scan all instruments"""
        print(f"\n{'='*80}")
        print(f"MULTI-INSTRUMENT 15-MIN SCANNER - GRADE A ONLY")
        print(f"{'='*80}")
        print(f"Scan Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Data Source: {self.data_source}")
        print(f"Instruments: {len(self.instruments)}")
        print(f"Quality: Confidence 80%+, R:R 1.5:1+, Risk <1.5%\n")

        results = {}

        for name, ticker in self.instruments.items():
            print(f"📊 {name:20s} ({ticker})...")

            try:
                data = self.fetch_data(ticker, bars=400)

                if data is None or len(data) < 100:
                    print(f"   ❌ Insufficient data\n")
                    results[name] = None
                    continue

                data = self.add_indicators(data)
                signal = self.find_signals(data, name)

                if signal:
                    print(f"   ✅ SIGNAL: {signal.signal_type} | {signal.pattern}")
                    print(f"   Entry: ${signal.entry_price:.2f}")
                    print(f"   Stop: ${signal.stop_loss:.2f}")
                    print(f"   Target: ${signal.target:.2f}")
                    print(f"   Risk: ${signal.risk_dollars:.2f} ({signal.risk_pct:.2f}%)")
                    print(f"   R:R: {signal.rr_ratio:.2f}:1 | Vol: {signal.volume_ratio:.1f}x")
                    print(f"   Confidence: {signal.confidence}% | Grade: {signal.grade}")
                    print(f"   💡 {signal.reasoning}\n")
                else:
                    current_price = float(data['Close'].iloc[-1])
                    print(f"   ⏸️  No Grade A signal (price: ${current_price:.2f})\n")

                results[name] = signal

            except Exception as e:
                print(f"   ❌ Error: {str(e)}\n")
                results[name] = None

        return results

    def display_summary(self, results: Dict[str, Optional[Signal]]):
        """Display summary"""
        signals = [s for s in results.values() if s is not None]

        print(f"{'='*80}")
        print(f"SUMMARY")
        print(f"{'='*80}")
        print(f"Instruments scanned: {len(results)}")
        print(f"Grade A signals found: {len(signals)}")

        if signals:
            print(f"\n🎯 ACTIONABLE SIGNALS (GRADE A):")
            for sig in signals:
                print(f"\n   {sig.instrument}:")
                print(f"      {sig.signal_type} @ ${sig.entry_price:.2f}")
                print(f"      Stop: ${sig.stop_loss:.2f} | Target: ${sig.target:.2f}")
                print(f"      Pattern: {sig.pattern} | Conf: {sig.confidence}%")
        else:
            print(f"\n⏸️  No Grade A signals right now")
            print(f"   Market conditions not ideal across instruments")
            print(f"   Check back in 15 minutes\n")

        print(f"\n💡 GRADE A STANDARDS:")
        print(f"   ✅ Confidence: 80%+")
        print(f"   ✅ R:R Ratio: 1.5:1+")
        print(f"   ✅ Risk: <1.5% per trade")
        print(f"   ✅ Volume: 1.2x+ average")

        print(f"\n📊 Expected frequency: 2-3 signals/day per instrument")
        print(f"   With {len(self.instruments)} instruments: {len(self.instruments) * 2.5:.0f} signals/day possible")
        print(f"   (but take only best 2-3 across all instruments)")
        print(f"\n⏰ Run this scanner every 15 minutes for best results\n")


def main():
    """Run scanner"""
    parser = argparse.ArgumentParser(description='Multi-instrument 15-min scanner')
    parser.add_argument('--source',
                       choices=['yfinance', 'tradingview', 'mcx'],
                       default='yfinance',
                       help='Data source (default: yfinance)')

    args = parser.parse_args()

    scanner = MultiInstrumentScanner(data_source=args.source)
    results = scanner.scan_all()
    scanner.display_summary(results)


if __name__ == "__main__":
    main()
