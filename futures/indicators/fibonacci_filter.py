"""
FIBONACCI RETRACEMENT FILTER

Detects resistance/support at key Fibonacci levels:
- 0.236 (23.6%)
- 0.382 (38.2%)
- 0.500 (50%)
- 0.618 (61.8%) ← Golden ratio, strongest resistance/support
- 0.786 (78.6%)

Prevents longing at resistance (0.618 retracement of recent fall)
Prevents shorting at support (0.618 retracement of recent rise)

Example: Nifty war fall from 25,000 → 23,000
- Current: 24,236 = 0.618 retracement
- This is RESISTANCE (likely rejection)
- System should NOT recommend LONG here

Author: Trading System
Date: 2026-04-20
Version: 1.0
"""

import pandas as pd
import numpy as np
from typing import Dict, Optional, Tuple
from dataclasses import dataclass


@dataclass
class FibonacciAnalysis:
    """Fibonacci retracement analysis"""
    is_safe_entry: bool
    score: int  # 0-100, higher = safer entry

    # Swing detection
    swing_high: float
    swing_low: float
    swing_direction: str  # UP/DOWN

    # Current position
    current_price: float
    retracement_level: float  # 0-1 (0.618 = 61.8% retracement)
    nearest_fib: str  # "0.618", "0.5", etc.

    # Resistance/Support
    at_resistance: bool
    at_support: bool

    warning: Optional[str]
    recommendation: str


class FibonacciFilter:
    """Filter trades at Fibonacci resistance/support"""

    # Fibonacci levels (strongest to weakest)
    FIB_LEVELS = {
        0.618: "GOLDEN",     # Strongest resistance/support
        0.5: "STRONG",       # Psychological level
        0.382: "MODERATE",
        0.786: "MODERATE",
        0.236: "WEAK"
    }

    # Danger zones (avoid entries within this range of Fib level)
    DANGER_ZONE_PCT = 3.0  # Within 3% of Fib level = danger (increased from 1%)

    def analyze(self, data: pd.DataFrame, lookback: int = 60) -> FibonacciAnalysis:
        """
        Analyze if current price is at Fibonacci resistance/support

        Args:
            data: OHLC dataframe
            lookback: Bars to find swing high/low (default 60 = ~3 months daily)

        Returns:
            FibonacciAnalysis with entry safety assessment
        """

        if len(data) < lookback:
            return FibonacciAnalysis(
                is_safe_entry=False,
                score=0,
                swing_high=0,
                swing_low=0,
                swing_direction="UNKNOWN",
                current_price=0,
                retracement_level=0,
                nearest_fib="NONE",
                at_resistance=False,
                at_support=False,
                warning="Insufficient data",
                recommendation="SKIP - Not enough history"
            )

        # Get swing high/low
        swing_high, swing_low = self._find_swing_points(data, lookback)

        # Current price
        current_price = float(data['Close'].iloc[-1])

        # Determine swing direction (most recent dominant move)
        swing_direction = self._determine_swing_direction(data, swing_high, swing_low)

        # Calculate retracement level
        if swing_direction == "DOWN":
            # After fall, how much has it retraced back up?
            retracement_level = (current_price - swing_low) / (swing_high - swing_low)
        elif swing_direction == "UP":
            # After rise, how much has it retraced back down?
            retracement_level = (swing_high - current_price) / (swing_high - swing_low)
        else:
            retracement_level = 0.5

        retracement_level = max(0, min(1, retracement_level))  # Clamp 0-1

        # Find nearest Fib level
        nearest_fib, distance = self._find_nearest_fib(retracement_level)

        # Check if at resistance/support
        at_resistance = False
        at_support = False

        # Check distance to ANY major Fib level (0.5, 0.618)
        dist_to_50 = abs(retracement_level - 0.5)
        dist_to_618 = abs(retracement_level - 0.618)

        if swing_direction == "DOWN":
            # Bouncing up from fall → Fib levels are RESISTANCE
            if distance < self.DANGER_ZONE_PCT / 100:
                at_resistance = True
            # Also check if near 50% or 61.8% specifically
            elif dist_to_50 < 0.03 or dist_to_618 < 0.03:  # Within 3%
                at_resistance = True
        elif swing_direction == "UP":
            # Pulling back from rise → Fib levels are SUPPORT
            if distance < self.DANGER_ZONE_PCT / 100:
                at_support = True
            elif dist_to_50 < 0.03 or dist_to_618 < 0.03:
                at_support = True
        else:
            # UNKNOWN direction, be conservative
            # If near major Fib, flag as potential resistance
            if dist_to_50 < 0.03 or dist_to_618 < 0.03:
                at_resistance = True  # Default to resistance for longs

        # Calculate score
        score = self._calculate_score(retracement_level, distance, swing_direction, at_resistance, at_support)

        # Is safe entry?
        is_safe_entry = score >= 60 and not (at_resistance or at_support)

        # Generate warning
        warning = None
        if at_resistance:
            fib_price = swing_low + (swing_high - swing_low) * retracement_level
            warning = f"⚠️ AT FIBONACCI RESISTANCE: {nearest_fib} retracement (${fib_price:.2f}) - Likely rejection"
        elif at_support:
            fib_price = swing_high - (swing_high - swing_low) * retracement_level
            warning = f"⚠️ AT FIBONACCI SUPPORT: {nearest_fib} retracement (${fib_price:.2f}) - Likely bounce"

        # Recommendation
        if score >= 80:
            recommendation = "✅ SAFE - Away from Fib levels"
        elif score >= 60:
            recommendation = "⚠️ ACCEPTABLE - Monitor Fib levels"
        elif at_resistance:
            recommendation = "❌ SKIP LONG - At resistance, wait for breakout OR pullback"
        elif at_support:
            recommendation = "❌ SKIP SHORT - At support, wait for breakdown OR bounce"
        else:
            recommendation = "⚠️ CAUTION - Near Fib level"

        return FibonacciAnalysis(
            is_safe_entry=is_safe_entry,
            score=score,
            swing_high=swing_high,
            swing_low=swing_low,
            swing_direction=swing_direction,
            current_price=current_price,
            retracement_level=retracement_level,
            nearest_fib=nearest_fib,
            at_resistance=at_resistance,
            at_support=at_support,
            warning=warning,
            recommendation=recommendation
        )

    def _find_swing_points(self, data: pd.DataFrame, lookback: int) -> Tuple[float, float]:
        """Find swing high and swing low in lookback period"""
        recent = data.tail(lookback)

        swing_high = float(recent['High'].max())
        swing_low = float(recent['Low'].min())

        return swing_high, swing_low

    def _determine_swing_direction(self, data: pd.DataFrame, swing_high: float, swing_low: float) -> str:
        """
        Determine if most recent swing was UP or DOWN

        Logic:
        - Find when swing high and swing low occurred
        - If high is more recent → was moving UP (now might be retracing down)
        - If low is more recent → was moving DOWN (now might be retracing up)
        """

        recent = data.tail(60)

        # Find index of swing high and swing low
        high_idx = None
        low_idx = None

        for i in range(len(recent)):
            if float(recent.iloc[i]['High']) == swing_high:
                high_idx = i
            if float(recent.iloc[i]['Low']) == swing_low:
                low_idx = i

        if high_idx is None or low_idx is None:
            return "UNKNOWN"

        # Which came later?
        if low_idx > high_idx:
            return "DOWN"  # Low is more recent (fell from high)
        else:
            return "UP"  # High is more recent (rose from low)

    def _find_nearest_fib(self, retracement_level: float) -> Tuple[str, float]:
        """
        Find nearest Fibonacci level

        Returns:
            (fib_level_name, distance_to_level)
        """

        min_distance = 1.0
        nearest = "NONE"

        for fib, strength in self.FIB_LEVELS.items():
            distance = abs(retracement_level - fib)
            if distance < min_distance:
                min_distance = distance
                nearest = f"{fib:.3f} ({strength})"

        return nearest, min_distance

    def _calculate_score(self, retracement_level: float, distance: float,
                        swing_direction: str, at_resistance: bool, at_support: bool) -> int:
        """
        Calculate safety score (0-100)

        Penalties:
        - At 0.618 resistance/support: -50 (dangerous)
        - At 0.5 resistance/support: -30
        - At other Fib levels: -20
        - Near Fib levels (within 2%): -10
        """

        score = 100

        # Heavy penalty for being AT Fib resistance/support
        if at_resistance or at_support:
            if distance < 0.01:  # Within 1%
                # Which Fib level?
                for fib, strength in self.FIB_LEVELS.items():
                    if abs(retracement_level - fib) < 0.02:
                        if strength == "GOLDEN":
                            score -= 50  # 0.618 is strongest
                        elif strength == "STRONG":
                            score -= 30
                        else:
                            score -= 20
                        break
        elif distance < 0.02:  # Near (within 2%)
            score -= 10

        score = max(0, min(100, score))

        return score

    def is_safe_long(self, data: pd.DataFrame, min_score: int = 60) -> bool:
        """
        Quick check if safe to LONG (not at resistance)

        Returns:
            True if safe, False if at resistance
        """
        analysis = self.analyze(data)
        return not analysis.at_resistance and analysis.score >= min_score

    def is_safe_short(self, data: pd.DataFrame, min_score: int = 60) -> bool:
        """
        Quick check if safe to SHORT (not at support)

        Returns:
            True if safe, False if at support
        """
        analysis = self.analyze(data)
        return not analysis.at_support and analysis.score >= min_score


def main():
    """Test with real data"""
    import yfinance as yf

    print("\n" + "="*80)
    print("FIBONACCI FILTER - TEST")
    print("="*80)

    # Test with Nifty (should catch 0.618 resistance)
    print("\n1. Testing NIFTY (should flag 0.618 resistance):")
    nifty = yf.download('^NSEI', period='3mo', interval='1d', progress=False)

    filter_obj = FibonacciFilter()
    analysis = filter_obj.analyze(nifty, lookback=60)

    print(f"   Current: ${analysis.current_price:.2f}")
    print(f"   Swing High: ${analysis.swing_high:.2f}")
    print(f"   Swing Low: ${analysis.swing_low:.2f}")
    print(f"   Direction: {analysis.swing_direction}")
    print(f"   Retracement: {analysis.retracement_level:.1%}")
    print(f"   Nearest Fib: {analysis.nearest_fib}")
    print(f"   At Resistance: {analysis.at_resistance}")
    print(f"   Score: {analysis.score}/100")
    print(f"   Warning: {analysis.warning}")
    print(f"   Recommendation: {analysis.recommendation}")

    # Test with another instrument
    print("\n2. Testing GOLD:")
    gold = yf.download('GC=F', period='3mo', interval='1d', progress=False)
    analysis_gold = filter_obj.analyze(gold, lookback=60)

    print(f"   Current: ${analysis_gold.current_price:.2f}")
    print(f"   Swing: ${analysis_gold.swing_high:.2f} → ${analysis_gold.swing_low:.2f}")
    print(f"   Retracement: {analysis_gold.retracement_level:.1%}")
    print(f"   Nearest Fib: {analysis_gold.nearest_fib}")
    print(f"   Score: {analysis_gold.score}/100")
    print(f"   Safe to Long: {filter_obj.is_safe_long(gold)}")

    print("\n" + "="*80)
    print("Integration: Use is_safe_long() or is_safe_short() before entry")


if __name__ == "__main__":
    main()
