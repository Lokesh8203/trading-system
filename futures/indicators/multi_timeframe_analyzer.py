"""
MULTI-TIMEFRAME ANALYZER

Holistic view across timeframes instead of single-timeframe analysis.

Problem: Daily looks good but hourly shows consolidation → Bad trade
Solution: Analyze ALL timeframes, require alignment

Timeframes analyzed:
- Daily (swing structure)
- 4-hour (intermediate trend)
- 1-hour (short-term action)
- 15-min (entry timing) - optional for intraday

Filters applied per timeframe:
- Price action (inside bars, consolidation)
- Fibonacci (resistance/support)

Result: Trade only if MOST timeframes agree

Author: Trading System
Date: 2026-04-20
Version: 1.0
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass

from futures.indicators.price_action_filter import PriceActionFilter, PriceActionAnalysis
from futures.indicators.fibonacci_filter import FibonacciFilter, FibonacciAnalysis


@dataclass
class TimeframeAnalysis:
    """Analysis for a single timeframe"""
    timeframe: str
    price_action: PriceActionAnalysis
    fibonacci: FibonacciAnalysis

    is_clean: bool
    score: int  # Combined score
    recommendation: str


@dataclass
class MultiTimeframeAnalysis:
    """Multi-timeframe consensus"""
    symbol: str
    direction: str  # LONG/SHORT

    # Individual timeframe results
    daily: Optional[TimeframeAnalysis]
    h4: Optional[TimeframeAnalysis]
    h1: Optional[TimeframeAnalysis]
    m15: Optional[TimeframeAnalysis]

    # Consensus
    timeframes_clean: int  # How many timeframes are clean
    timeframes_total: int
    consensus_score: int  # 0-100, weighted average

    is_safe_entry: bool
    recommendation: str
    warnings: List[str]


class MultiTimeframeAnalyzer:
    """Analyze instrument across multiple timeframes"""

    def __init__(self):
        self.pa_filter = PriceActionFilter()
        self.fib_filter = FibonacciFilter()

    def analyze(self, symbol: str, direction: str = "LONG",
                include_15min: bool = False) -> MultiTimeframeAnalysis:
        """
        Analyze instrument across timeframes

        Args:
            symbol: Ticker (e.g., 'SI=F', 'RELIANCE.NS')
            direction: LONG or SHORT
            include_15min: Include 15-min analysis (for intraday)

        Returns:
            MultiTimeframeAnalysis with consensus
        """

        print(f"\n{'='*70}")
        print(f"MULTI-TIMEFRAME ANALYSIS: {symbol} ({direction})")
        print(f"{'='*70}")

        # Fetch data for each timeframe
        timeframes = {
            'daily': ('1d', 60),    # 60 days
            'h4': ('1h', 120),      # 120 4-hour bars = 20 days
            'h1': ('1h', 60),       # 60 hours
        }

        if include_15min:
            timeframes['m15'] = ('15m', 100)  # 100 15-min bars

        analyses = {}

        for tf_name, (interval, lookback) in timeframes.items():
            analysis = self._analyze_timeframe(
                symbol, direction, tf_name, interval, lookback
            )
            analyses[tf_name] = analysis

        # Calculate consensus
        consensus = self._calculate_consensus(symbol, direction, analyses)

        return consensus

    def _analyze_timeframe(self, symbol: str, direction: str,
                          tf_name: str, interval: str, lookback: int) -> Optional[TimeframeAnalysis]:
        """Analyze single timeframe"""

        print(f"\n  Analyzing {tf_name.upper()}...")

        try:
            # Fetch data
            if tf_name == 'daily':
                data = yf.download(symbol, period='3mo', interval=interval, progress=False)
            elif tf_name == 'h4':
                # 4-hour bars from 1-hour data
                data = yf.download(symbol, period='1mo', interval='1h', progress=False)
                if len(data) > 0:
                    # Resample to 4-hour
                    data = data.resample('4H').agg({
                        'Open': 'first',
                        'High': 'max',
                        'Low': 'min',
                        'Close': 'last',
                        'Volume': 'sum'
                    }).dropna()
            else:
                data = yf.download(symbol, period='7d', interval=interval, progress=False)

            if len(data) < lookback // 2:
                print(f"    ⚠️  Insufficient data ({len(data)} bars)")
                return None

            # Price action analysis
            pa_lookback = min(15, len(data) // 2)
            pa_analysis = self.pa_filter.analyze(data, lookback=pa_lookback)

            # Fibonacci analysis
            fib_lookback = min(60, len(data))
            fib_analysis = self.fib_filter.analyze(data, lookback=fib_lookback)

            # Combined score
            score = self._combine_scores(pa_analysis, fib_analysis, direction)

            is_clean = pa_analysis.is_clean and score >= 60

            # Recommendation
            if score >= 70:
                recommendation = f"✅ {tf_name.upper()}: Clean"
            elif score >= 50:
                recommendation = f"⚠️  {tf_name.upper()}: Acceptable"
            else:
                recommendation = f"❌ {tf_name.upper()}: Skip"

            print(f"    Price Action: {pa_analysis.score}/100 ({pa_analysis.recommendation.split('-')[0]})")
            print(f"    Fibonacci: {fib_analysis.score}/100")
            print(f"    Combined: {score}/100 - {recommendation}")

            return TimeframeAnalysis(
                timeframe=tf_name,
                price_action=pa_analysis,
                fibonacci=fib_analysis,
                is_clean=is_clean,
                score=score,
                recommendation=recommendation
            )

        except Exception as e:
            print(f"    ❌ Error: {str(e)}")
            return None

    def _combine_scores(self, pa: PriceActionAnalysis, fib: FibonacciAnalysis,
                       direction: str) -> int:
        """
        Combine price action + Fibonacci into single score

        Weights:
        - Price action: 40%
        - Fibonacci: 60% (more important for entries)
        """

        combined = int(pa.score * 0.4 + fib.score * 0.6)

        # Heavy penalty if at resistance/support in wrong direction
        if direction == "LONG" and fib.at_resistance:
            combined = min(combined, 30)  # Cap at 30
        elif direction == "SHORT" and fib.at_support:
            combined = min(combined, 30)

        # Heavy penalty for bad price action
        if not pa.is_clean:
            combined = max(0, combined - 30)

        return combined

    def _calculate_consensus(self, symbol: str, direction: str,
                            analyses: Dict[str, Optional[TimeframeAnalysis]]) -> MultiTimeframeAnalysis:
        """Calculate multi-timeframe consensus"""

        print(f"\n  {'='*68}")
        print(f"  CONSENSUS:")
        print(f"  {'='*68}")

        # Count clean timeframes
        timeframes_total = len([a for a in analyses.values() if a is not None])
        timeframes_clean = len([a for a in analyses.values()
                               if a is not None and a.is_clean])

        # Weighted average score
        # Daily = 40%, H4 = 30%, H1 = 20%, M15 = 10%
        weights = {'daily': 0.4, 'h4': 0.3, 'h1': 0.2, 'm15': 0.1}

        total_weight = 0
        weighted_score = 0

        for tf_name, analysis in analyses.items():
            if analysis:
                weight = weights.get(tf_name, 0)
                weighted_score += analysis.score * weight
                total_weight += weight

        consensus_score = int(weighted_score / total_weight) if total_weight > 0 else 0

        # Collect warnings
        warnings = []
        for tf_name, analysis in analyses.items():
            if analysis:
                if analysis.price_action.warning:
                    warnings.append(f"{tf_name.upper()}: {analysis.price_action.warning}")
                if analysis.fibonacci.warning:
                    warnings.append(f"{tf_name.upper()}: {analysis.fibonacci.warning}")

        # Is safe entry?
        # Require: At least 2/3 timeframes clean AND consensus >= 60
        is_safe_entry = (
            timeframes_clean >= max(2, timeframes_total * 0.67) and
            consensus_score >= 60
        )

        # Recommendation
        if is_safe_entry and consensus_score >= 75:
            recommendation = f"✅ SAFE - {timeframes_clean}/{timeframes_total} timeframes clean"
        elif is_safe_entry:
            recommendation = f"⚠️  ACCEPTABLE - {timeframes_clean}/{timeframes_total} timeframes clean"
        else:
            recommendation = f"❌ SKIP - Only {timeframes_clean}/{timeframes_total} timeframes clean"

        print(f"  Clean timeframes: {timeframes_clean}/{timeframes_total}")
        print(f"  Consensus score: {consensus_score}/100")
        print(f"  Recommendation: {recommendation}")

        if warnings:
            print(f"\n  WARNINGS:")
            for warning in warnings:
                print(f"    • {warning}")

        return MultiTimeframeAnalysis(
            symbol=symbol,
            direction=direction,
            daily=analyses.get('daily'),
            h4=analyses.get('h4'),
            h1=analyses.get('h1'),
            m15=analyses.get('m15'),
            timeframes_clean=timeframes_clean,
            timeframes_total=timeframes_total,
            consensus_score=consensus_score,
            is_safe_entry=is_safe_entry,
            recommendation=recommendation,
            warnings=warnings
        )

    def quick_check(self, symbol: str, direction: str = "LONG") -> bool:
        """
        Quick check: Is this a safe entry across timeframes?

        Returns:
            True if safe, False if not
        """
        analysis = self.analyze(symbol, direction, include_15min=False)
        return analysis.is_safe_entry


def main():
    """Test multi-timeframe analyzer"""

    analyzer = MultiTimeframeAnalyzer()

    print("\n" + "="*70)
    print("MULTI-TIMEFRAME ANALYZER - TEST")
    print("="*70)

    # Test 1: Silver (should show hourly issues)
    print("\n1. SILVER (should show hourly consolidation):")
    silver_analysis = analyzer.analyze('SI=F', direction='LONG', include_15min=False)

    print(f"\n   Final: {silver_analysis.recommendation}")
    print(f"   Safe to trade: {silver_analysis.is_safe_entry}")

    # Test 2: Nifty (should show Fib resistance)
    print("\n2. NIFTY (should show Fibonacci resistance):")
    nifty_analysis = analyzer.analyze('^NSEI', direction='LONG', include_15min=False)

    print(f"\n   Final: {nifty_analysis.recommendation}")
    print(f"   Safe to trade: {nifty_analysis.is_safe_entry}")

    # Test 3: Quick check
    print("\n3. QUICK CHECK:")
    print(f"   Silver safe: {analyzer.quick_check('SI=F', 'LONG')}")
    print(f"   Nifty safe: {analyzer.quick_check('^NSEI', 'LONG')}")


if __name__ == "__main__":
    main()
