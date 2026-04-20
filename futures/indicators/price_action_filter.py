"""
PRICE ACTION CONSOLIDATION FILTER

Catches technically bad entries:
- Multiple inside bars (consolidation)
- Small body candles (indecision)
- Failed breakouts (no follow-through)
- Stuck price action

Integrates into scanners to prevent recommending:
- Silver at $80 with bearish inside bars
- Any instrument consolidating after breakout

Author: Trading System
Date: 2026-04-20
Version: 1.0
"""

import pandas as pd
import numpy as np
from typing import Dict, Optional
from dataclasses import dataclass


@dataclass
class PriceActionAnalysis:
    """Price action quality assessment"""
    is_clean: bool
    score: int  # 0-100, higher = cleaner price action

    # Flags
    has_consolidation: bool
    has_inside_bars: bool
    has_indecision: bool
    has_failed_breakout: bool

    # Details
    inside_bar_count: int
    small_body_count: int
    trend_strength: str  # STRONG/MODERATE/WEAK/CHOPPY

    warning: Optional[str]
    recommendation: str


class PriceActionFilter:
    """Filter out consolidating/indecisive price action"""

    # Thresholds
    MAX_INSIDE_BARS = 2  # More than 2 inside bars in last 5 = consolidation
    MAX_SMALL_BODIES = 3  # More than 3 small bodies in last 5 = indecision
    SMALL_BODY_PCT = 0.3  # Body < 0.3% of price = small
    MIN_TREND_STRENGTH = 0.5  # For trending price action

    def analyze(self, data: pd.DataFrame, lookback: int = 10) -> PriceActionAnalysis:
        """
        Analyze recent price action quality

        Args:
            data: OHLC dataframe (must have Open, High, Low, Close)
            lookback: Bars to analyze (default 10)

        Returns:
            PriceActionAnalysis with flags and recommendation
        """

        if len(data) < lookback:
            return PriceActionAnalysis(
                is_clean=False,
                score=0,
                has_consolidation=True,
                has_inside_bars=False,
                has_indecision=True,
                has_failed_breakout=False,
                inside_bar_count=0,
                small_body_count=0,
                trend_strength="UNKNOWN",
                warning="Insufficient data",
                recommendation="SKIP - Not enough bars"
            )

        # Get recent bars
        recent = data.tail(lookback)

        # Count inside bars
        inside_bar_count = self._count_inside_bars(recent)

        # Count small body candles
        small_body_count = self._count_small_bodies(recent)

        # Check for failed breakout
        failed_breakout = self._detect_failed_breakout(recent)

        # Measure trend strength
        trend_strength = self._measure_trend_strength(recent)

        # Determine flags
        has_consolidation = inside_bar_count > self.MAX_INSIDE_BARS
        has_inside_bars = inside_bar_count >= 2
        has_indecision = small_body_count > self.MAX_SMALL_BODIES
        has_failed_breakout = failed_breakout

        # Calculate score (0-100)
        score = 100

        # Penalties
        score -= inside_bar_count * 15  # -15 per inside bar
        score -= small_body_count * 10  # -10 per small body
        if failed_breakout:
            score -= 30

        # Trend strength bonus/penalty
        if trend_strength == "STRONG":
            score += 10
        elif trend_strength == "CHOPPY":
            score -= 20

        score = max(0, min(100, score))

        # Is clean? (no major issues)
        is_clean = score >= 60 and not has_consolidation

        # Generate warning
        warning = None
        if has_consolidation:
            warning = f"⚠️ CONSOLIDATION: {inside_bar_count} inside bars in last {lookback} bars"
        elif has_indecision:
            warning = f"⚠️ INDECISION: {small_body_count} small-body candles"
        elif failed_breakout:
            warning = "⚠️ FAILED BREAKOUT: No follow-through after recent high/low"
        elif trend_strength == "CHOPPY":
            warning = "⚠️ CHOPPY: No clear direction"

        # Recommendation
        if score >= 70:
            recommendation = "✅ CLEAN - Good price action"
        elif score >= 50:
            recommendation = "⚠️ ACCEPTABLE - Monitor closely"
        else:
            recommendation = "❌ SKIP - Poor price action, wait for clarity"

        return PriceActionAnalysis(
            is_clean=is_clean,
            score=score,
            has_consolidation=has_consolidation,
            has_inside_bars=has_inside_bars,
            has_indecision=has_indecision,
            has_failed_breakout=failed_breakout,
            inside_bar_count=inside_bar_count,
            small_body_count=small_body_count,
            trend_strength=trend_strength,
            warning=warning,
            recommendation=recommendation
        )

    def _count_inside_bars(self, data: pd.DataFrame) -> int:
        """Count inside bars (high < prev high AND low > prev low)"""
        count = 0

        for i in range(1, len(data)):
            curr = data.iloc[i]
            prev = data.iloc[i-1]

            curr_high = float(curr['High'])
            curr_low = float(curr['Low'])
            prev_high = float(prev['High'])
            prev_low = float(prev['Low'])

            if curr_high < prev_high and curr_low > prev_low:
                count += 1

        return count

    def _count_small_bodies(self, data: pd.DataFrame) -> int:
        """Count small-body candles (body < 0.3% of price)"""
        count = 0

        for i in range(len(data)):
            row = data.iloc[i]

            open_p = float(row['Open'])
            close = float(row['Close'])

            body = abs(close - open_p)
            body_pct = (body / open_p) * 100

            if body_pct < self.SMALL_BODY_PCT:
                count += 1

        return count

    def _detect_failed_breakout(self, data: pd.DataFrame) -> bool:
        """
        Detect failed breakout:
        - Made new high in last 5 bars
        - But closed below that level for 3+ bars
        """

        if len(data) < 5:
            return False

        recent_5 = data.tail(5)
        high_5 = float(recent_5['High'].max())

        # Find when high was made
        high_idx = None
        for i in range(len(recent_5)):
            if float(recent_5.iloc[i]['High']) == high_5:
                high_idx = i
                break

        if high_idx is None or high_idx >= len(recent_5) - 1:
            return False  # High is too recent to judge

        # Check if subsequent bars failed to hold
        bars_after = recent_5.iloc[high_idx+1:]
        closes_below = 0

        for i in range(len(bars_after)):
            close = float(bars_after.iloc[i]['Close'])
            if close < high_5 * 0.995:  # More than 0.5% below high
                closes_below += 1

        # Failed if 2+ bars closed significantly below
        return closes_below >= 2

    def _measure_trend_strength(self, data: pd.DataFrame) -> str:
        """
        Measure trend strength:
        STRONG: Clear directional movement
        MODERATE: Some direction
        WEAK: Little movement
        CHOPPY: No clear direction
        """

        if len(data) < 5:
            return "UNKNOWN"

        # Calculate directional movement
        closes = data['Close'].values

        # Count consecutive moves in same direction
        up_moves = 0
        down_moves = 0

        for i in range(1, len(closes)):
            if closes[i] > closes[i-1]:
                up_moves += 1
            elif closes[i] < closes[i-1]:
                down_moves += 1

        total_moves = len(closes) - 1

        # Dominant direction
        if up_moves > total_moves * 0.7:
            return "STRONG"  # 70%+ up
        elif down_moves > total_moves * 0.7:
            return "STRONG"  # 70%+ down
        elif max(up_moves, down_moves) > total_moves * 0.6:
            return "MODERATE"  # 60%+ in one direction
        elif abs(up_moves - down_moves) <= 2:
            return "CHOPPY"  # Roughly equal up/down
        else:
            return "WEAK"

    def is_good_entry(self, data: pd.DataFrame, min_score: int = 60) -> bool:
        """
        Quick check if price action is good for entry

        Args:
            data: OHLC dataframe
            min_score: Minimum score to consider (default 60)

        Returns:
            True if clean price action, False if consolidating
        """
        analysis = self.analyze(data)
        return analysis.score >= min_score and analysis.is_clean


def main():
    """Test with sample data"""
    import yfinance as yf

    print("\n" + "="*80)
    print("PRICE ACTION FILTER - TEST")
    print("="*80)

    # Test with Silver (should catch consolidation)
    print("\n1. Testing SILVER (should flag consolidation):")
    silver = yf.download('SI=F', period='1mo', interval='1d', progress=False)

    filter_obj = PriceActionFilter()
    analysis = filter_obj.analyze(silver, lookback=10)

    print(f"   Score: {analysis.score}/100")
    print(f"   Is Clean: {analysis.is_clean}")
    print(f"   Inside Bars: {analysis.inside_bar_count}")
    print(f"   Small Bodies: {analysis.small_body_count}")
    print(f"   Trend: {analysis.trend_strength}")
    print(f"   Warning: {analysis.warning}")
    print(f"   Recommendation: {analysis.recommendation}")

    # Test with clean trending instrument
    print("\n2. Testing SPY (should be cleaner):")
    spy = yf.download('SPY', period='1mo', interval='1d', progress=False)
    analysis_spy = filter_obj.analyze(spy, lookback=10)

    print(f"   Score: {analysis_spy.score}/100")
    print(f"   Is Clean: {analysis_spy.is_clean}")
    print(f"   Inside Bars: {analysis_spy.inside_bar_count}")
    print(f"   Small Bodies: {analysis_spy.small_body_count}")
    print(f"   Trend: {analysis_spy.trend_strength}")
    print(f"   Recommendation: {analysis_spy.recommendation}")

    print("\n" + "="*80)
    print("Integration: Use analysis.score >= 60 and analysis.is_clean for filter")


if __name__ == "__main__":
    main()
