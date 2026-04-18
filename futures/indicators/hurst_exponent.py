"""
Hurst Exponent Calculator for Market Regime Detection
Ported from Sierra Chart ACS_Source hurst_exponent_signal_latest.cpp

The Hurst Exponent (H) measures market memory and trend persistence:
- H > 0.6: Strong trending market (breakouts likely to continue)
- H = 0.5: Random walk (no memory, unpredictable)
- H < 0.4: Mean-reverting market (extremes likely to reverse)

Author: Trading System
Date: 2026-04-18
"""

import numpy as np
import pandas as pd
from typing import Tuple, Dict, Optional
from dataclasses import dataclass
from enum import Enum


class MarketRegime(Enum):
    """Market regime classification based on Hurst Exponent"""
    STRONG_TREND = "STRONG_TREND"        # H > 0.60
    TRENDING = "TRENDING"                 # 0.55 < H <= 0.60
    CHOPPY = "CHOPPY"                     # 0.45 <= H <= 0.55
    MEAN_REVERTING = "MEAN_REVERTING"     # 0.40 <= H < 0.45
    STRONG_MEAN_REVERT = "STRONG_MEAN_REVERT"  # H < 0.40


@dataclass
class HurstResult:
    """Result container for Hurst Exponent calculation"""
    hurst_exponent: float
    regime: MarketRegime
    confidence: float  # 0-1, based on sample size and stability
    lookback_periods: int
    interpretation: str
    trading_advice: str


class HurstExponentCalculator:
    """
    Calculate Hurst Exponent using R/S (Rescaled Range) Analysis

    Based on:
    - Original Hurst (1951) research on Nile river flows
    - Mandelbrot & Wallis (1969) fractal market hypothesis
    - Peters (1994) "Fractal Market Analysis"
    """

    # Thresholds from Sierra Chart study
    DOWN_THRESHOLD = 0.40  # Below = strong mean reversion
    UP_THRESHOLD = 0.60    # Above = strong trending

    def __init__(self, min_lookback: int = 50, max_lookback: int = 200):
        """
        Initialize Hurst calculator

        Args:
            min_lookback: Minimum periods for calculation (default 50)
            max_lookback: Maximum periods for calculation (default 200)
        """
        self.min_lookback = min_lookback
        self.max_lookback = max_lookback

    def calculate(
        self,
        prices: pd.Series,
        lookback: int = 100,
        method: str = 'rs'
    ) -> HurstResult:
        """
        Calculate Hurst Exponent for given price series

        Args:
            prices: Price series (close prices typically)
            lookback: Number of periods to analyze
            method: 'rs' for Rescaled Range (default), 'var' for Variance method

        Returns:
            HurstResult with exponent, regime, and trading advice
        """
        if len(prices) < self.min_lookback:
            raise ValueError(f"Need at least {self.min_lookback} periods, got {len(prices)}")

        # Use most recent data
        lookback = min(lookback, len(prices), self.max_lookback)
        recent_prices = prices.iloc[-lookback:].values

        if method == 'rs':
            hurst = self._rescaled_range_method(recent_prices)
        elif method == 'var':
            hurst = self._variance_method(recent_prices)
        else:
            raise ValueError(f"Unknown method: {method}")

        # Classify regime
        regime = self._classify_regime(hurst)

        # Calculate confidence based on sample size and stability
        confidence = self._calculate_confidence(recent_prices, hurst)

        # Generate interpretation and advice
        interpretation = self._interpret_hurst(hurst, regime)
        trading_advice = self._generate_trading_advice(hurst, regime)

        return HurstResult(
            hurst_exponent=hurst,
            regime=regime,
            confidence=confidence,
            lookback_periods=lookback,
            interpretation=interpretation,
            trading_advice=trading_advice
        )

    def _rescaled_range_method(self, prices: np.ndarray) -> float:
        """
        Calculate Hurst using Rescaled Range (R/S) Analysis

        This is the classic Hurst method:
        1. Calculate log returns
        2. Compute mean-adjusted cumulative deviation
        3. Find range R = max(cumdev) - min(cumdev)
        4. Calculate standard deviation S
        5. H = log(R/S) / log(n)
        """
        n = len(prices)

        # Step 1: Log returns
        log_returns = np.log(prices[1:] / prices[:-1])

        # Step 2: Mean return
        mean_return = np.mean(log_returns)

        # Step 3: Cumulative deviation from mean
        cumulative_deviation = np.cumsum(log_returns - mean_return)

        # Step 4: Range (R)
        R = np.max(cumulative_deviation) - np.min(cumulative_deviation)

        # Step 5: Standard deviation (S)
        S = np.std(log_returns, ddof=1)

        # Avoid division by zero
        if S == 0 or R == 0:
            return 0.5  # Random walk default

        # Step 6: Calculate Hurst
        # H = log(R/S) / log(n)
        hurst = np.log(R / S) / np.log(n)

        # Clamp to valid range [0, 1]
        hurst = np.clip(hurst, 0.0, 1.0)

        return hurst

    def _variance_method(self, prices: np.ndarray) -> float:
        """
        Calculate Hurst using Variance method

        Alternative method based on variance scaling:
        Var(X(t+tau) - X(t)) ~ tau^(2H)
        """
        n = len(prices)
        lags = range(2, min(20, n // 5))

        tau = []
        variances = []

        for lag in lags:
            # Calculate variance at this lag
            differences = prices[lag:] - prices[:-lag]
            var = np.var(differences)

            if var > 0:
                tau.append(lag)
                variances.append(var)

        if len(tau) < 3:
            # Fall back to R/S method
            return self._rescaled_range_method(prices)

        # Fit log(var) = 2H * log(tau) + C
        log_tau = np.log(tau)
        log_var = np.log(variances)

        # Linear regression
        coeffs = np.polyfit(log_tau, log_var, 1)
        hurst = coeffs[0] / 2.0  # slope / 2 = H

        # Clamp to valid range
        hurst = np.clip(hurst, 0.0, 1.0)

        return hurst

    def _classify_regime(self, hurst: float) -> MarketRegime:
        """Classify market regime based on Hurst value"""
        if hurst > self.UP_THRESHOLD:
            return MarketRegime.STRONG_TREND
        elif hurst > 0.55:
            return MarketRegime.TRENDING
        elif hurst >= 0.45:
            return MarketRegime.CHOPPY
        elif hurst >= self.DOWN_THRESHOLD:
            return MarketRegime.MEAN_REVERTING
        else:
            return MarketRegime.STRONG_MEAN_REVERT

    def _calculate_confidence(self, prices: np.ndarray, hurst: float) -> float:
        """
        Calculate confidence in Hurst estimate

        Higher confidence when:
        - Larger sample size
        - Hurst far from 0.5 (clear regime)
        - Stable over recent periods
        """
        n = len(prices)

        # Sample size factor (0.5 to 1.0)
        size_factor = min(1.0, n / self.max_lookback)

        # Distance from random walk (0.0 to 1.0)
        distance_factor = abs(hurst - 0.5) * 2

        # Overall confidence
        confidence = (size_factor + distance_factor) / 2

        return confidence

    def _interpret_hurst(self, hurst: float, regime: MarketRegime) -> str:
        """Generate human-readable interpretation"""
        interpretations = {
            MarketRegime.STRONG_TREND: (
                f"H={hurst:.3f}: Strong trending behavior. "
                "Price has persistent memory - moves tend to continue in same direction. "
                "Breakouts likely to follow through."
            ),
            MarketRegime.TRENDING: (
                f"H={hurst:.3f}: Moderate trending behavior. "
                "Some persistence in price movement. "
                "Trend-following strategies may work."
            ),
            MarketRegime.CHOPPY: (
                f"H={hurst:.3f}: Random walk behavior. "
                "Price has no memory - moves are unpredictable. "
                "No clear edge for trending or mean-reversion."
            ),
            MarketRegime.MEAN_REVERTING: (
                f"H={hurst:.3f}: Moderate mean-reverting behavior. "
                "Price tends to reverse after extremes. "
                "Fading strategies may work."
            ),
            MarketRegime.STRONG_MEAN_REVERT: (
                f"H={hurst:.3f}: Strong mean-reverting behavior. "
                "Price has anti-persistence - extremes typically reverse. "
                "Range-bound trading, fade breakouts."
            )
        }
        return interpretations[regime]

    def _generate_trading_advice(self, hurst: float, regime: MarketRegime) -> str:
        """Generate actionable trading advice"""
        advice = {
            MarketRegime.STRONG_TREND: (
                "✅ BREAKOUT MODE\n"
                "- Trade breakouts aggressively\n"
                "- Let winners run, use trailing stops\n"
                "- Add to winning positions\n"
                "- Avoid fading moves or calling tops/bottoms"
            ),
            MarketRegime.TRENDING: (
                "✅ TREND MODE\n"
                "- Trade with the trend\n"
                "- Buy pullbacks in uptrend\n"
                "- Sell bounces in downtrend\n"
                "- Use wider stops"
            ),
            MarketRegime.CHOPPY: (
                "⚠️ CAUTION MODE\n"
                "- Reduce position size\n"
                "- Take quick profits\n"
                "- Use tight stops\n"
                "- Avoid new positions if possible"
            ),
            MarketRegime.MEAN_REVERTING: (
                "↔️ RANGE MODE\n"
                "- Fade extremes\n"
                "- Sell rallies, buy dips\n"
                "- Target back to range middle\n"
                "- Use tight stops"
            ),
            MarketRegime.STRONG_MEAN_REVERT: (
                "↔️ STRONG RANGE MODE\n"
                "- Aggressively fade breakouts\n"
                "- Counter-trend trades\n"
                "- Book profits quickly\n"
                "- Avoid holding through range extremes"
            )
        }
        return advice[regime]

    def calculate_rolling(
        self,
        prices: pd.Series,
        window: int = 100,
        step: int = 1
    ) -> pd.DataFrame:
        """
        Calculate rolling Hurst Exponent over time

        Args:
            prices: Price series
            window: Rolling window size
            step: Step size between calculations (1 = every bar)

        Returns:
            DataFrame with columns: [hurst, regime, confidence]
        """
        results = []

        for i in range(window, len(prices), step):
            window_prices = prices.iloc[i-window:i]
            result = self.calculate(window_prices, lookback=window)

            results.append({
                'timestamp': prices.index[i-1],
                'hurst': result.hurst_exponent,
                'regime': result.regime.value,
                'confidence': result.confidence
            })

        return pd.DataFrame(results).set_index('timestamp')


def analyze_gold_regime(prices: pd.Series, lookback: int = 100) -> HurstResult:
    """
    Quick helper function to analyze Gold futures regime

    Args:
        prices: Gold close prices (pd.Series)
        lookback: Periods to analyze

    Returns:
        HurstResult with trading advice
    """
    calculator = HurstExponentCalculator()
    return calculator.calculate(prices, lookback=lookback)


if __name__ == "__main__":
    # Example usage
    print("Hurst Exponent Calculator")
    print("=" * 50)
    print("\nExample: Analyzing Gold MCX Futures")
    print("\nUsage:")
    print("  from futures.indicators.hurst_exponent import analyze_gold_regime")
    print("  result = analyze_gold_regime(gold_prices)")
    print("  print(result.interpretation)")
    print("  print(result.trading_advice)")
