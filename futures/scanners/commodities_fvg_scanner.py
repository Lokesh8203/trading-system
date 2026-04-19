"""
COMMODITIES FAIR VALUE GAP (FVG) SCANNER

Extends price action analysis to MCX commodities:
- Gold, Silver, Crude Oil, Copper, Natural Gas

Fair Value Gap (FVG): 3-candle imbalance where price "gaps" leaving unfilled zone
- Bullish FVG: candle[i-2].high < candle[i].low → expect price to fill gap (retest support)
- Bearish FVG: candle[i-2].low > candle[i].high → expect price to fill gap (retest resistance)

Use FVG zones as:
1. Entry zones (buy at bullish FVG, sell at bearish FVG)
2. Target zones (take profit when gap filled)
3. Invalidation (if gap doesn't hold, setup invalid)

Integrated with MCX timing: Only signals during optimal windows.

Usage:
    python3 futures/scanners/commodities_fvg_scanner.py

Author: Trading System
Date: 2026-04-19
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Tuple
from dataclasses import dataclass

# Import MCX timing
from futures.macro.mcx_trading_timing_guide import MCXTradingSchedule


@dataclass
class FVGSignal:
    """Fair Value Gap signal"""
    timestamp: datetime
    instrument: str
    signal_type: str  # BUY/SELL
    pattern: str  # FVG, ORDER_BLOCK, STRUCTURE_BREAK

    entry_price: float
    stop_loss: float
    target: float

    # FVG-specific
    fvg_low: float
    fvg_high: float
    fvg_size: float
    fvg_atr_ratio: float  # Gap size / ATR

    risk_dollars: float
    reward_dollars: float
    rr_ratio: float
    risk_pct: float

    confidence: int
    grade: str

    # MCX timing
    can_trade_now: bool
    trading_window: str
    window_priority: str

    reasoning: str


class CommoditiesFVGScanner:
    """Find Fair Value Gaps and price action setups in commodities"""

    # Grade A thresholds
    MIN_CONFIDENCE = 75
    MIN_RR_RATIO = 1.5
    MAX_RISK_PCT = 2.0  # Commodities more volatile than indices

    def __init__(self):
        # MCX instruments with yfinance proxies
        self.instruments = {
            'GOLD': 'GC=F',
            'SILVER': 'SI=F',
            'CRUDE': 'CL=F',
            'COPPER': 'HG=F',
            'NATGAS': 'NG=F'
        }

        # MCX timing
        self.mcx_schedule = MCXTradingSchedule()

    def fetch_data(self, ticker: str, bars: int = 400) -> Optional[pd.DataFrame]:
        """Fetch 15-min data"""
        try:
            end = datetime.now()
            start = end - timedelta(days=10)
            data = yf.download(ticker, start=start, end=end, interval='15m', progress=False)

            if len(data) < 100:
                return None

            # Flatten MultiIndex columns if present
            if isinstance(data.columns, pd.MultiIndex):
                data.columns = data.columns.get_level_values(0)

            return data.iloc[-bars:]
        except Exception as e:
            return None

    def add_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """Add price-based indicators"""
        df = data.copy()

        # Moving averages
        df['SMA_20'] = df['Close'].rolling(20).mean()
        df['SMA_50'] = df['Close'].rolling(50).mean()
        df['EMA_9'] = df['Close'].ewm(span=9, adjust=False).mean()

        # ATR for stops/targets
        df['HL'] = df['High'] - df['Low']
        df['HC'] = abs(df['High'] - df['Close'].shift(1))
        df['LC'] = abs(df['Low'] - df['Close'].shift(1))
        df['TR'] = df[['HL', 'HC', 'LC']].max(axis=1)
        df['ATR'] = df['TR'].rolling(14).mean()

        # Candle body and wicks
        df['Body'] = abs(df['Close'] - df['Open'])
        df['High_OC'] = df[['Open', 'Close']].max(axis=1)
        df['Low_OC'] = df[['Open', 'Close']].min(axis=1)
        df['Upper_Wick'] = df['High'] - df['High_OC']
        df['Lower_Wick'] = df['Low_OC'] - df['Low']
        df['Range'] = df['High'] - df['Low']

        # Volume (if available)
        if 'Volume' in df.columns:
            df['Vol_SMA'] = df['Volume'].rolling(20).mean()
            df['Vol_Ratio'] = df['Volume'] / df['Vol_SMA']
        else:
            df['Vol_Ratio'] = 1.0

        return df

    def find_fair_value_gap(self, data: pd.DataFrame, idx: int) -> Optional[Dict]:
        """
        Fair Value Gap: 3-candle imbalance

        Bullish FVG: candle[i-2].high < candle[i].low (gap up)
        Bearish FVG: candle[i-2].low > candle[i].high (gap down)

        Returns: dict with FVG details
        """
        if idx < 2:
            return None

        candle_old = data.iloc[idx - 2]
        candle_mid = data.iloc[idx - 1]
        candle_new = data.iloc[idx]

        # Bullish FVG: gap between old high and new low
        if candle_old['High'] < candle_new['Low']:
            gap_low = candle_old['High']
            gap_high = candle_new['Low']
            gap_size = gap_high - gap_low
            gap_atr_ratio = gap_size / candle_new['ATR'] if candle_new['ATR'] > 0 else 0

            # Significant gap (>30% ATR)
            if gap_atr_ratio > 0.3:
                return {
                    'direction': 'BUY',
                    'gap_low': gap_low,
                    'gap_high': gap_high,
                    'gap_size': gap_size,
                    'gap_atr_ratio': gap_atr_ratio,
                    'candle_mid_close': candle_mid['Close']
                }

        # Bearish FVG: gap between old low and new high
        if candle_old['Low'] > candle_new['High']:
            gap_low = candle_new['High']
            gap_high = candle_old['Low']
            gap_size = gap_high - gap_low
            gap_atr_ratio = gap_size / candle_new['ATR'] if candle_new['ATR'] > 0 else 0

            if gap_atr_ratio > 0.3:
                return {
                    'direction': 'SELL',
                    'gap_low': gap_low,
                    'gap_high': gap_high,
                    'gap_size': gap_size,
                    'gap_atr_ratio': gap_atr_ratio,
                    'candle_mid_close': candle_mid['Close']
                }

        return None

    def find_order_block(self, data: pd.DataFrame, idx: int) -> Optional[Dict]:
        """
        Order Block: Strong rejection candle followed by move

        Bullish OB: Strong buying candle with long lower wick, price rallies after
        Bearish OB: Strong selling candle with long upper wick, price drops after
        """
        if idx < 5:
            return None

        candle = data.iloc[idx - 1]  # Previous candle
        current = data.iloc[idx]

        range_val = candle['Range']

        if range_val == 0:
            return None

        # Bullish OB: long lower wick (>40% of range), closes near high
        lower_wick_pct = candle['Lower_Wick'] / range_val
        if (lower_wick_pct > 0.4 and
            candle['Close'] > candle['Open'] and
            current['Close'] > candle['High']):
            return {
                'direction': 'BUY',
                'ob_low': candle['Low'],
                'ob_high': candle['Close'],
                'wick_pct': lower_wick_pct
            }

        # Bearish OB: long upper wick (>40% of range), closes near low
        upper_wick_pct = candle['Upper_Wick'] / range_val
        if (upper_wick_pct > 0.4 and
            candle['Close'] < candle['Open'] and
            current['Close'] < candle['Low']):
            return {
                'direction': 'SELL',
                'ob_low': candle['Close'],
                'ob_high': candle['High'],
                'wick_pct': upper_wick_pct
            }

        return None

    def find_structure_break(self, data: pd.DataFrame, idx: int) -> Optional[Dict]:
        """
        Break of Structure: Price breaks recent swing high/low
        """
        if idx < 20:
            return None

        recent = data.iloc[idx-20:idx]
        current = data.iloc[idx]

        # Bullish: break above recent swing high
        swing_high = recent['High'].max()
        if current['Close'] > swing_high and current['Close'] > current['Open']:
            return {
                'direction': 'BUY',
                'level': swing_high
            }

        # Bearish: break below recent swing low
        swing_low = recent['Low'].min()
        if current['Close'] < swing_low and current['Close'] < current['Open']:
            return {
                'direction': 'SELL',
                'level': swing_low
            }

        return None

    def calculate_confidence(self, signal_data: dict) -> int:
        """Calculate confidence"""
        confidence = 50

        # R:R bonus
        rr = signal_data['rr']
        if rr >= 3.0:
            confidence += 25
        elif rr >= 2.0:
            confidence += 20
        elif rr >= 1.5:
            confidence += 15

        # Risk size
        risk_pct = signal_data['risk_pct']
        if risk_pct < 1.0:
            confidence += 15
        elif risk_pct < 1.5:
            confidence += 10
        elif risk_pct > 2.0:
            confidence -= 10

        # Pattern quality
        pattern = signal_data['pattern']
        if pattern == 'FVG':
            # FVG quality based on size
            fvg_atr_ratio = signal_data.get('fvg_atr_ratio', 0)
            if fvg_atr_ratio > 0.8:
                confidence += 20  # Large gap = strong signal
            elif fvg_atr_ratio > 0.5:
                confidence += 15
            else:
                confidence += 10
        elif pattern == 'ORDER_BLOCK':
            confidence += 15
        elif pattern == 'STRUCTURE_BREAK':
            confidence += 10

        # Trend alignment
        if signal_data.get('trend_aligned', False):
            confidence += 10

        # Volume confirmation (if available)
        vol_ratio = signal_data.get('vol_ratio', 1.0)
        if vol_ratio > 1.5:
            confidence += 10

        return min(100, max(0, confidence))

    def find_signals(self, data: pd.DataFrame, instrument: str) -> Optional[FVGSignal]:
        """Find Grade A signals using price action"""

        if len(data) < 100:
            return None

        idx = len(data) - 1
        bar = data.iloc[idx]

        price = bar['Close']
        atr = bar['ATR']
        sma_20 = bar['SMA_20']
        vol_ratio = bar.get('Vol_Ratio', 1.0)
        timestamp = bar.name

        signal_data = None

        # PATTERN 1: Fair Value Gap (PRIORITY)
        fvg = self.find_fair_value_gap(data, idx)
        if fvg:
            direction = fvg['direction']
            gap_low = fvg['gap_low']
            gap_high = fvg['gap_high']
            gap_size = fvg['gap_size']
            gap_atr_ratio = fvg['gap_atr_ratio']

            if direction == 'BUY':
                entry = price
                stop = gap_low - atr * 0.5
                target = price + 2 * atr

                signal_data = {
                    'pattern': 'FVG',
                    'type': 'BUY',
                    'entry': entry,
                    'stop': stop,
                    'target': target,
                    'fvg_low': gap_low,
                    'fvg_high': gap_high,
                    'fvg_size': gap_size,
                    'fvg_atr_ratio': gap_atr_ratio,
                    'trend_aligned': price > sma_20,
                    'vol_ratio': vol_ratio,
                    'reasoning': f'Bullish FVG ${gap_low:.2f}-${gap_high:.2f} ({gap_atr_ratio:.1f}× ATR), price retesting support'
                }

            elif direction == 'SELL':
                entry = price
                stop = gap_high + atr * 0.5
                target = price - 2 * atr

                signal_data = {
                    'pattern': 'FVG',
                    'type': 'SELL',
                    'entry': entry,
                    'stop': stop,
                    'target': target,
                    'fvg_low': gap_low,
                    'fvg_high': gap_high,
                    'fvg_size': gap_size,
                    'fvg_atr_ratio': gap_atr_ratio,
                    'trend_aligned': price < sma_20,
                    'vol_ratio': vol_ratio,
                    'reasoning': f'Bearish FVG ${gap_low:.2f}-${gap_high:.2f} ({gap_atr_ratio:.1f}× ATR), price retesting resistance'
                }

        # PATTERN 2: Order Block
        if not signal_data:
            ob = self.find_order_block(data, idx)
            if ob:
                direction = ob['direction']
                ob_low = ob['ob_low']
                ob_high = ob['ob_high']

                if direction == 'BUY':
                    entry = price
                    stop = ob_low - atr * 0.5
                    target = price + 2 * atr

                    signal_data = {
                        'pattern': 'ORDER_BLOCK',
                        'type': 'BUY',
                        'entry': entry,
                        'stop': stop,
                        'target': target,
                        'fvg_low': ob_low,
                        'fvg_high': ob_high,
                        'fvg_size': ob_high - ob_low,
                        'fvg_atr_ratio': (ob_high - ob_low) / atr,
                        'trend_aligned': price > sma_20,
                        'vol_ratio': vol_ratio,
                        'reasoning': f'Bullish Order Block ${ob_low:.2f}-${ob_high:.2f}, continuation expected'
                    }

                elif direction == 'SELL':
                    entry = price
                    stop = ob_high + atr * 0.5
                    target = price - 2 * atr

                    signal_data = {
                        'pattern': 'ORDER_BLOCK',
                        'type': 'SELL',
                        'entry': entry,
                        'stop': stop,
                        'target': target,
                        'fvg_low': ob_low,
                        'fvg_high': ob_high,
                        'fvg_size': ob_high - ob_low,
                        'fvg_atr_ratio': (ob_high - ob_low) / atr,
                        'trend_aligned': price < sma_20,
                        'vol_ratio': vol_ratio,
                        'reasoning': f'Bearish Order Block ${ob_low:.2f}-${ob_high:.2f}, continuation expected'
                    }

        # PATTERN 3: Structure Break
        if not signal_data:
            structure = self.find_structure_break(data, idx)
            if structure:
                direction = structure['direction']
                level = structure['level']

                if direction == 'BUY':
                    entry = price
                    stop = level - atr * 0.5
                    target = price + 1.5 * atr

                    signal_data = {
                        'pattern': 'STRUCTURE_BREAK',
                        'type': 'BUY',
                        'entry': entry,
                        'stop': stop,
                        'target': target,
                        'fvg_low': level,
                        'fvg_high': level,
                        'fvg_size': 0,
                        'fvg_atr_ratio': 0,
                        'trend_aligned': price > sma_20,
                        'vol_ratio': vol_ratio,
                        'reasoning': f'Broke above structure ${level:.2f}, bullish momentum'
                    }

                elif direction == 'SELL':
                    entry = price
                    stop = level + atr * 0.5
                    target = price - 1.5 * atr

                    signal_data = {
                        'pattern': 'STRUCTURE_BREAK',
                        'type': 'SELL',
                        'entry': entry,
                        'stop': stop,
                        'target': target,
                        'fvg_low': level,
                        'fvg_high': level,
                        'fvg_size': 0,
                        'fvg_atr_ratio': 0,
                        'trend_aligned': price < sma_20,
                        'vol_ratio': vol_ratio,
                        'reasoning': f'Broke below structure ${level:.2f}, bearish momentum'
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

        # Check MCX timing
        timing_status = self.mcx_schedule.can_trade_now(instrument)
        can_trade = timing_status['can_trade']
        trading_window = timing_status.get('window', 'N/A') if can_trade else 'WAIT'
        window_priority = timing_status.get('priority', 'N/A') if can_trade else 'N/A'

        # Create signal
        return FVGSignal(
            timestamp=timestamp,
            instrument=instrument,
            signal_type=signal_data['type'],
            pattern=signal_data['pattern'],
            entry_price=signal_data['entry'],
            stop_loss=signal_data['stop'],
            target=signal_data['target'],
            fvg_low=signal_data['fvg_low'],
            fvg_high=signal_data['fvg_high'],
            fvg_size=signal_data['fvg_size'],
            fvg_atr_ratio=signal_data['fvg_atr_ratio'],
            risk_dollars=risk,
            reward_dollars=reward,
            rr_ratio=rr,
            risk_pct=risk_pct,
            confidence=confidence,
            grade='A',
            can_trade_now=can_trade,
            trading_window=trading_window,
            window_priority=window_priority,
            reasoning=signal_data['reasoning']
        )

    def scan_all(self) -> Dict[str, Optional[FVGSignal]]:
        """Scan all commodities"""
        print(f"\n{'='*100}")
        print(f"COMMODITIES FAIR VALUE GAP (FVG) SCANNER")
        print(f"{'='*100}")
        print(f"Scan Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Instruments: Gold, Silver, Crude, Copper, NatGas")
        print(f"Patterns: FVG (priority), Order Blocks, Structure Breaks")
        print(f"Quality: Confidence 75%+, R:R 1.5:1+, Risk <2%")
        print(f"MCX Timing: Integrated (shows CAN TRADE / WAIT)\n")

        results = {}

        for name, ticker in self.instruments.items():
            print(f"📊 {name:15s} ({ticker})...")

            try:
                data = self.fetch_data(ticker, bars=400)

                if data is None or len(data) < 100:
                    print(f"   ❌ Insufficient data\n")
                    results[name] = None
                    continue

                data = self.add_indicators(data)
                signal = self.find_signals(data, name)

                if signal:
                    status_icon = "✅" if signal.can_trade_now else "❌"
                    print(f"   {status_icon} SIGNAL: {signal.signal_type} | {signal.pattern}")
                    print(f"   Entry: ${signal.entry_price:.2f}")
                    print(f"   Stop: ${signal.stop_loss:.2f}")
                    print(f"   Target: ${signal.target:.2f}")
                    if signal.pattern == 'FVG':
                        print(f"   FVG Zone: ${signal.fvg_low:.2f}-${signal.fvg_high:.2f} ({signal.fvg_atr_ratio:.1f}× ATR)")
                    print(f"   Risk: ${signal.risk_dollars:.2f} ({signal.risk_pct:.2f}%)")
                    print(f"   R:R: {signal.rr_ratio:.2f}:1")
                    print(f"   Confidence: {signal.confidence}% | Grade: {signal.grade}")

                    if signal.can_trade_now:
                        print(f"   ⏰ TIMING: {signal.trading_window} ({signal.window_priority} priority)")
                    else:
                        print(f"   ⏰ TIMING: {signal.trading_window} - WAIT for optimal window")

                    print(f"   💡 {signal.reasoning}\n")
                else:
                    current_price = data['Close'].iloc[-1]
                    print(f"   ⏸️  No Grade A signal (price: ${current_price:.2f})\n")

                results[name] = signal

            except Exception as e:
                print(f"   ❌ Error: {str(e)}\n")
                results[name] = None

        return results

    def display_summary(self, results: Dict[str, Optional[FVGSignal]]):
        """Display summary"""
        signals = [s for s in results.values() if s is not None]

        print(f"{'='*100}")
        print(f"SUMMARY")
        print(f"{'='*100}")
        print(f"Commodities scanned: {len(results)}")
        print(f"Grade A signals found: {len(signals)}")

        if signals:
            print(f"\n🎯 ACTIONABLE SIGNALS (GRADE A):")
            for sig in signals:
                status = "✅ CAN TRADE" if sig.can_trade_now else "❌ WAIT"
                window = f"({sig.trading_window})" if sig.can_trade_now else f"(until optimal window)"

                print(f"\n   {sig.instrument}:")
                print(f"      {sig.signal_type} @ ${sig.entry_price:.2f}")
                print(f"      Stop: ${sig.stop_loss:.2f} | Target: ${sig.target:.2f}")
                print(f"      Pattern: {sig.pattern} | Conf: {sig.confidence}%")
                print(f"      Timing: {status} {window}")
        else:
            print(f"\n⏸️  No Grade A signals right now")
            print(f"   Wait for clear price action setups")

        print(f"\n💡 FAIR VALUE GAP STRATEGY:")
        print(f"   1. Identify 3-candle imbalances (FVG zones)")
        print(f"   2. Price retests gap = entry opportunity")
        print(f"   3. Stop below/above gap boundary")
        print(f"   4. Target: 2× ATR or next structure level")
        print(f"   5. Best during HIGH/HIGHEST MCX windows")

        print(f"\n⏰ OPTIMAL MCX WINDOWS:")
        print(f"   Morning: 9:30-11:30 AM (MEDIUM)")
        print(f"   Afternoon: 2:00-4:00 PM (HIGH) ← Best")
        print(f"   Evening: 7:00-10:00 PM (HIGHEST) ← Best")

        # Next scanner run
        next_scan = self.mcx_schedule.next_scanner_run()
        print(f"\n📊 NEXT SCANNER RUN:")
        print(f"   Time: {next_scan['time'].strftime('%I:%M %p IST')}")
        print(f"   Session: {next_scan['session']}")
        print(f"   Action: {next_scan['action']}")

        print(f"\n📊 Expected frequency: 1-2 FVG signals/day per commodity")
        print(f"⏰ Run every 15 minutes or at optimal times (9:30 AM, 2 PM, 7 PM)\n")


def main():
    """Run scanner"""
    scanner = CommoditiesFVGScanner()
    results = scanner.scan_all()
    scanner.display_summary(results)


if __name__ == "__main__":
    main()
