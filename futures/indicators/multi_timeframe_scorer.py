"""
MULTI-TIMEFRAME SCORER (Correct Approach)

Based on actual trading methodology:
- Higher timeframes (Weekly/Daily) → TRADE QUALITY & RANKING
- Lower timeframes (Hourly/15-min) → ENTRY TIMING only

Key principle: Lower TF choppiness ≠ bad trade, just bad ENTRY TIMING

Workflow:
1. Score trade based on Weekly + Daily (determines rank in scanner)
2. Check Hourly/15-min for ENTRY STATUS:
   - Clean → "✅ ENTER NOW"
   - Choppy → "⏸️ WAIT - Watch for [specific trigger]"
   - Never → "❌ SKIP" (only if higher TF broken)

Author: Trading System
Date: 2026-04-20
Version: 2.0 (Redesigned based on actual trading process)
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

import pandas as pd
import yfinance as yf
from typing import Dict, Optional
from dataclasses import dataclass

from futures.indicators.price_action_filter import PriceActionFilter
from futures.indicators.fibonacci_filter import FibonacciFilter


@dataclass
class TradeScore:
    """Trade scoring result"""
    symbol: str
    direction: str
    asset_type: str  # STOCK or FUTURE

    # TRADE QUALITY (Higher TF) - Used for ranking
    weekly_score: int
    daily_score: int
    trade_quality_score: int  # Weighted average of weekly + daily

    # ENTRY TIMING (Lower TF) - Used for timing
    hourly_score: int
    m15_score: Optional[int]  # For futures
    entry_timing_score: int

    # Overall
    rank_score: int  # What rank to give in scanner (based on higher TF only)
    entry_status: str  # ENTER_NOW / WAIT / CAUTION

    # Detailed info
    weekly_analysis: str
    daily_analysis: str
    entry_suggestion: str  # What to wait for if not ready


class MultiTimeframeScorer:
    """Score trades correctly: Higher TF = quality, Lower TF = timing"""

    def __init__(self):
        self.pa_filter = PriceActionFilter()
        self.fib_filter = FibonacciFilter()

    def score_trade(self, symbol: str, direction: str = "LONG",
                   asset_type: str = "STOCK") -> TradeScore:
        """
        Score trade properly

        Args:
            symbol: Ticker
            direction: LONG/SHORT
            asset_type: STOCK or FUTURE (determines TF weights)

        Returns:
            TradeScore with quality (for ranking) and timing (for entry)
        """

        print(f"\n{'='*70}")
        print(f"SCORING: {symbol} {direction} ({asset_type})")
        print(f"{'='*70}")

        # Fetch data for each timeframe
        weekly_data = self._fetch_data(symbol, '1wk', 52)  # 1 year
        daily_data = self._fetch_data(symbol, '1d', 120)  # 6 months
        hourly_data = self._fetch_data(symbol, '1h', 100)  # ~2 weeks

        m15_data = None
        if asset_type == "FUTURE":
            m15_data = self._fetch_data(symbol, '15m', 100)  # For futures only

        # Score each timeframe
        print("\n1. HIGHER TIMEFRAMES (Trade Quality):")
        print("   " + "-"*50)

        weekly_score = self._score_timeframe(
            weekly_data, direction, "WEEKLY"
        ) if weekly_data is not None else 0

        daily_score = self._score_timeframe(
            daily_data, direction, "DAILY"
        ) if daily_data is not None else 0

        # Calculate trade quality (for ranking)
        # ALL instruments: Weekly = Daily (finding S/R levels over time)
        # Longer timeframe = more respected levels
        trade_quality = int(weekly_score * 0.5 + daily_score * 0.5)

        print(f"\n   → Trade Quality Score: {trade_quality}/100")
        print(f"      (This determines ranking in scanner)")

        # Score lower timeframes (entry timing)
        print("\n2. LOWER TIMEFRAMES (Entry Timing):")
        print("   " + "-"*50)

        hourly_score = self._score_timeframe(
            hourly_data, direction, "HOURLY"
        ) if hourly_data is not None else 0

        m15_score = None
        if m15_data is not None:
            m15_score = self._score_timeframe(
                m15_data, direction, "15-MIN"
            )

        # Calculate entry timing
        if asset_type == "STOCK":
            # Stocks: Hourly/2-hourly (but less critical - no leverage)
            entry_timing = hourly_score
        else:
            # Futures/Index: 15-min is CRITICAL for SL (leverage!)
            # 15-min 70% + Hourly 30% (15-min dominant)
            if m15_score is not None:
                entry_timing = int(m15_score * 0.7 + hourly_score * 0.3)
            else:
                entry_timing = hourly_score

        print(f"\n   → Entry Timing Score: {entry_timing}/100")
        print(f"      (This determines when to enter)")

        # Determine entry status
        entry_status, entry_suggestion = self._determine_entry_status(
            trade_quality, entry_timing, hourly_score, m15_score, asset_type
        )

        # Analysis summaries
        weekly_analysis = self._get_analysis_summary(weekly_data, direction, "WEEKLY")
        daily_analysis = self._get_analysis_summary(daily_data, direction, "DAILY")

        print(f"\n{'='*70}")
        print(f"RESULT:")
        print(f"{'='*70}")
        print(f"Trade Quality: {trade_quality}/100 (rank in scanner)")
        print(f"Entry Status: {entry_status}")
        print(f"Suggestion: {entry_suggestion}")
        print()

        return TradeScore(
            symbol=symbol,
            direction=direction,
            asset_type=asset_type,
            weekly_score=weekly_score,
            daily_score=daily_score,
            trade_quality_score=trade_quality,
            hourly_score=hourly_score,
            m15_score=m15_score,
            entry_timing_score=entry_timing,
            rank_score=trade_quality,  # Rank based on higher TF only!
            entry_status=entry_status,
            weekly_analysis=weekly_analysis,
            daily_analysis=daily_analysis,
            entry_suggestion=entry_suggestion
        )

    def _fetch_data(self, symbol: str, interval: str, lookback: int) -> Optional[pd.DataFrame]:
        """Fetch data for timeframe"""
        try:
            if interval == '1wk':
                data = yf.download(symbol, period='1y', interval=interval, progress=False)
            elif interval == '1d':
                data = yf.download(symbol, period='6mo', interval=interval, progress=False)
            elif interval == '1h':
                data = yf.download(symbol, period='1mo', interval=interval, progress=False)
            elif interval == '15m':
                data = yf.download(symbol, period='7d', interval=interval, progress=False)
            else:
                return None

            return data if len(data) >= lookback // 2 else None
        except:
            return None

    def _score_timeframe(self, data: pd.DataFrame, direction: str, tf_name: str) -> int:
        """Score a single timeframe"""

        if data is None or len(data) < 10:
            return 0

        try:
            # Price action
            pa_lookback = min(15, len(data) // 2)
            pa_analysis = self.pa_filter.analyze(data, lookback=pa_lookback)

            # Fibonacci
            fib_lookback = min(60, len(data))
            fib_analysis = self.fib_filter.analyze(data, lookback=fib_lookback)

            # Combine (weighted)
            # Price action 40%, Fibonacci 60%
            score = int(pa_analysis.score * 0.4 + fib_analysis.score * 0.6)

            # Heavy penalty if at resistance/support in wrong direction
            if direction == "LONG" and fib_analysis.at_resistance:
                score = min(score, 30)
            elif direction == "SHORT" and fib_analysis.at_support:
                score = min(score, 30)

            status = "✅" if score >= 70 else "⚠️" if score >= 50 else "❌"
            print(f"   {tf_name:8s}: {score:3d}/100 {status}")

            return score

        except:
            return 0

    def _determine_entry_status(self, trade_quality: int, entry_timing: int,
                                hourly: int, m15: Optional[int], asset_type: str) -> tuple:
        """
        Determine entry status and suggestion

        Key difference:
        - Stocks: Entry timing less critical (no leverage, can be relaxed)
        - Futures: Entry timing CRITICAL (leverage = need precise SL on 15-min)

        Returns: (status, suggestion)
        """

        # If trade quality itself is bad (higher TF broken), don't enter
        if trade_quality < 40:
            return ("❌ SKIP", "Higher timeframe setup broken - skip this trade entirely")

        # If trade quality moderate (40-59)
        if trade_quality < 60:
            if entry_timing >= 70:
                return ("⚠️ ENTER WITH CAUTION", "Trade quality moderate, but entry clean - reduce size")
            else:
                if asset_type == "STOCK":
                    # Stocks: Can still enter if not too choppy (no leverage)
                    if entry_timing >= 40:
                        return ("⚠️ ENTER WITH CAUTION", "Trade quality moderate, entry acceptable - reduce size")
                    else:
                        return ("⏸️ WAIT", "Both trade quality and entry timing weak - wait for one to improve")
                else:
                    # Futures: Need both to be decent (leverage risk)
                    return ("⏸️ WAIT", "Trade quality moderate + entry not ready - wait for both to align")

        # Trade quality is good (60+), now check entry timing
        if entry_timing >= 70:
            return ("✅ ENTER NOW", "Both trade quality and entry timing are good")

        elif entry_timing >= 50:
            # Entry timing acceptable
            if asset_type == "STOCK":
                # Stocks: Can enter even with OK timing (no leverage)
                return ("✅ ENTER NOW (or wait)", f"Trade quality good, entry acceptable - can enter or wait for stronger hourly")
            else:
                # Futures: Prefer cleaner entry (leverage)
                return ("⏸️ WAIT PREFERRED", f"Trade quality good but 15-min not ideal ({m15}/100) - wait for cleaner entry")

        else:
            # Entry timing poor (<50)
            if asset_type == "STOCK":
                # Stocks: Entry timing matters less
                if entry_timing >= 30:
                    return ("⚠️ ENTER CAUTIOUSLY", f"Trade quality good, entry choppy - acceptable for stocks (no leverage)")
                else:
                    return ("⏸️ WAIT", f"Entry very choppy (hourly {hourly}/100) - wait for consolidation to break")
            else:
                # Futures: Entry timing CRITICAL
                if m15 is not None and m15 < 50:
                    return ("⏸️ MUST WAIT", f"15-min choppy ({m15}/100) - leverage requires precise entry, watch for breakout")
                elif hourly < 50:
                    return ("⏸️ MUST WAIT", f"Hourly choppy ({hourly}/100) - wait for clearer direction")
                else:
                    return ("⏸️ WAIT", "Entry timing not aligned with higher timeframe trend")

    def _get_analysis_summary(self, data: Optional[pd.DataFrame], direction: str, tf_name: str) -> str:
        """Get brief analysis summary"""

        if data is None or len(data) < 10:
            return f"{tf_name}: No data"

        try:
            fib_analysis = self.fib_filter.analyze(data, lookback=min(60, len(data)))

            if fib_analysis.at_resistance and direction == "LONG":
                return f"{tf_name}: At resistance"
            elif fib_analysis.at_support and direction == "SHORT":
                return f"{tf_name}: At support"
            else:
                return f"{tf_name}: Clean"
        except:
            return f"{tf_name}: Unknown"


def main():
    """Test scorer"""

    scorer = MultiTimeframeScorer()

    print("\n" + "="*70)
    print("MULTI-TIMEFRAME SCORER - TEST")
    print("="*70)

    # Test 1: Silver (should have good daily but choppy hourly)
    print("\n1. SILVER (FUTURE):")
    silver = scorer.score_trade('SI=F', 'LONG', 'FUTURE')
    print(f"\n   Rank in scanner: {silver.rank_score}/100")
    print(f"   Entry status: {silver.entry_status}")

    # Test 2: Nifty
    print("\n2. NIFTY (FUTURE):")
    nifty = scorer.score_trade('^NSEI', 'LONG', 'FUTURE')
    print(f"\n   Rank in scanner: {nifty.rank_score}/100")
    print(f"   Entry status: {nifty.entry_status}")


if __name__ == "__main__":
    main()
