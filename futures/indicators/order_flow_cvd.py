"""
ORDER FLOW & CUMULATIVE VOLUME DELTA (CVD) ANALYZER

Concepts from ACS_Resources and institutional trading:

Cumulative Volume Delta (CVD):
- Buy Volume - Sell Volume accumulated over time
- Shows institutional flow (where smart money is positioned)
- Divergence with price = potential reversal

Order Flow Imbalance:
- Heavy buying at resistance = absorption (likely breakdown)
- Heavy selling at support = absorption (likely bounce)
- Cluster of orders at level = strong S/R

Volume Profile:
- Volume at each price level
- Point of Control (POC) = highest volume level
- Value Area (VA) = 70% of volume

Applications:
1. Confirm breakouts (high CVD + price break = strong)
2. Spot reversals (CVD divergence with price)
3. Identify S/R (volume clusters)
4. Detect accumulation/distribution

Limitations with yfinance:
- Only OHLCV data (no bid/ask, no tick data)
- Approximate buy/sell using uptick/downtick
- Not true order flow (need Level 2 data)

Usage:
    from futures.indicators.order_flow_cvd import OrderFlowAnalyzer

    analyzer = OrderFlowAnalyzer()
    result = analyzer.analyze(data)
    print(result.cvd_signal)  # BULLISH/BEARISH/NEUTRAL

Author: Trading System
Date: 2026-04-19
"""

import pandas as pd
import numpy as np
from typing import Dict, Optional
from dataclasses import dataclass
from enum import Enum


class CVDSignal(Enum):
    """CVD signal classification"""
    STRONG_BULLISH = "STRONG_BULLISH"      # CVD rising + price rising
    BULLISH = "BULLISH"                     # CVD rising
    NEUTRAL = "NEUTRAL"                     # No clear trend
    BEARISH = "BEARISH"                     # CVD falling
    STRONG_BEARISH = "STRONG_BEARISH"      # CVD falling + price falling


class DivergenceType(Enum):
    """Price-CVD divergence types"""
    BULLISH_DIV = "BULLISH_DIVERGENCE"     # Price lower low, CVD higher low (buy)
    BEARISH_DIV = "BEARISH_DIVERGENCE"     # Price higher high, CVD lower high (sell)
    HIDDEN_BULL = "HIDDEN_BULLISH"         # Price higher low, CVD lower low (continuation)
    HIDDEN_BEAR = "HIDDEN_BEARISH"         # Price lower high, CVD higher high (continuation)
    NONE = "NO_DIVERGENCE"


@dataclass
class OrderFlowResult:
    """Order flow analysis result"""
    # CVD metrics
    current_cvd: float
    cvd_trend: str  # UP/DOWN/FLAT
    cvd_signal: CVDSignal
    cvd_strength: int  # 0-100

    # Divergence
    divergence: DivergenceType
    divergence_strength: int  # 0-100

    # Volume profile
    poc_price: float  # Point of Control
    value_area_high: float
    value_area_low: float
    price_vs_poc: str  # ABOVE/BELOW/AT

    # Order flow imbalance
    recent_buy_volume: float
    recent_sell_volume: float
    buy_sell_ratio: float
    imbalance_signal: str  # BUYING/SELLING/BALANCED

    # Overall signal
    overall_signal: str  # BUY/SELL/NEUTRAL
    confidence: int  # 0-100
    reasoning: str


class OrderFlowAnalyzer:
    """Analyze order flow using OHLCV data (approximation)"""

    def __init__(self, lookback: int = 100):
        """
        Initialize order flow analyzer

        Args:
            lookback: Periods to analyze (default 100)
        """
        self.lookback = lookback

    def calculate_buy_sell_volume(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Approximate buy/sell volume using uptick/downtick

        Real order flow needs tick data (bid/ask).
        This approximation:
        - If close > open: classify volume as BUY
        - If close < open: classify volume as SELL
        - If close == open: split 50/50

        Better approximation:
        - Use close-to-close change
        - Weight by price change magnitude
        """
        df = data.copy()

        # Method 1: Simple (close vs open)
        df['Price_Change'] = df['Close'] - df['Open']

        # Buy volume (bullish candles)
        df['Buy_Volume'] = np.where(df['Price_Change'] > 0, df['Volume'], 0)

        # Sell volume (bearish candles)
        df['Sell_Volume'] = np.where(df['Price_Change'] < 0, df['Volume'], 0)

        # Neutral volume (doji)
        neutral = np.where(df['Price_Change'] == 0, df['Volume'], 0)
        df['Buy_Volume'] += neutral / 2
        df['Sell_Volume'] += neutral / 2

        # Method 2: Weighted by magnitude (better)
        # Larger moves = more conviction
        df['Abs_Change'] = abs(df['Price_Change'])
        df['Total_Change'] = df['Abs_Change'].rolling(window=5).sum()

        # Weight factor (0-1)
        df['Weight'] = np.where(
            df['Total_Change'] > 0,
            df['Abs_Change'] / df['Total_Change'],
            0.5
        )

        # Weighted buy/sell
        df['Buy_Volume_Weighted'] = np.where(
            df['Price_Change'] > 0,
            df['Volume'] * df['Weight'],
            df['Volume'] * (1 - df['Weight']) * 0.2  # Small portion to buy even on down candle
        )

        df['Sell_Volume_Weighted'] = np.where(
            df['Price_Change'] < 0,
            df['Volume'] * df['Weight'],
            df['Volume'] * (1 - df['Weight']) * 0.2
        )

        return df

    def calculate_cvd(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate Cumulative Volume Delta (CVD)

        CVD = Cumulative sum of (Buy Volume - Sell Volume)
        """
        df = data.copy()

        # Volume delta
        df['Volume_Delta'] = df['Buy_Volume_Weighted'] - df['Sell_Volume_Weighted']

        # Cumulative sum
        df['CVD'] = df['Volume_Delta'].cumsum()

        # Normalize CVD (for comparison across instruments)
        cvd_mean = df['CVD'].mean()
        cvd_std = df['CVD'].std()
        df['CVD_Normalized'] = (df['CVD'] - cvd_mean) / cvd_std if cvd_std > 0 else 0

        return df

    def calculate_volume_profile(self, data: pd.DataFrame, bins: int = 50) -> Dict:
        """
        Calculate Volume Profile (volume at each price level)

        Returns:
            - Point of Control (POC): Price with highest volume
            - Value Area High/Low (VAH/VAL): 70% of volume range
        """
        # Create price bins
        price_min = data['Low'].min()
        price_max = data['High'].max()
        price_range = price_max - price_min

        if price_range == 0:
            return {
                'poc': data['Close'].iloc[-1],
                'vah': data['Close'].iloc[-1],
                'val': data['Close'].iloc[-1]
            }

        bin_size = price_range / bins
        bins_array = np.arange(price_min, price_max + bin_size, bin_size)

        # Allocate volume to bins
        volume_profile = np.zeros(len(bins_array) - 1)

        for idx, row in data.iterrows():
            # Each candle's volume distributed across its range
            candle_min = row['Low']
            candle_max = row['High']
            candle_vol = row['Volume']

            # Find bins that overlap with this candle
            for i in range(len(bins_array) - 1):
                bin_low = bins_array[i]
                bin_high = bins_array[i + 1]

                # Overlap calculation
                overlap_low = max(bin_low, candle_min)
                overlap_high = min(bin_high, candle_max)

                if overlap_high > overlap_low:
                    # Proportion of candle in this bin
                    overlap_pct = (overlap_high - overlap_low) / (candle_max - candle_min) if (candle_max - candle_min) > 0 else 1
                    volume_profile[i] += candle_vol * overlap_pct

        # Find POC (highest volume bin)
        poc_idx = np.argmax(volume_profile)
        poc_price = (bins_array[poc_idx] + bins_array[poc_idx + 1]) / 2

        # Find Value Area (70% of volume)
        total_volume = volume_profile.sum()
        target_volume = total_volume * 0.70

        # Start from POC and expand outward
        va_volume = volume_profile[poc_idx]
        va_low_idx = poc_idx
        va_high_idx = poc_idx

        while va_volume < target_volume and (va_low_idx > 0 or va_high_idx < len(volume_profile) - 1):
            # Check which direction has more volume
            vol_below = volume_profile[va_low_idx - 1] if va_low_idx > 0 else 0
            vol_above = volume_profile[va_high_idx + 1] if va_high_idx < len(volume_profile) - 1 else 0

            if vol_above > vol_below:
                va_high_idx += 1
                va_volume += vol_above
            else:
                va_low_idx -= 1
                va_volume += vol_below

        vah = (bins_array[va_high_idx] + bins_array[va_high_idx + 1]) / 2
        val = (bins_array[va_low_idx] + bins_array[va_low_idx + 1]) / 2

        return {
            'poc': poc_price,
            'vah': vah,
            'val': val
        }

    def detect_divergence(self, data: pd.DataFrame, lookback: int = 20) -> DivergenceType:
        """
        Detect price-CVD divergence

        Bullish Divergence: Price makes lower low, CVD makes higher low
        Bearish Divergence: Price makes higher high, CVD makes lower high
        """
        if len(data) < lookback:
            return DivergenceType.NONE

        recent = data.iloc[-lookback:]

        # Find price swings
        price_highs = recent['High']
        price_lows = recent['Low']
        cvd = recent['CVD']

        # Current extremes
        current_price_high = price_highs.iloc[-5:].max()
        current_price_low = price_lows.iloc[-5:].min()
        current_cvd = cvd.iloc[-1]

        # Previous extremes
        prev_price_high = price_highs.iloc[:-5].max()
        prev_price_low = price_lows.iloc[:-5].min()

        # Find CVD at those price levels
        prev_high_idx = price_highs.iloc[:-5].idxmax()
        prev_low_idx = price_lows.iloc[:-5].idxmin()

        prev_cvd_at_high = cvd.loc[prev_high_idx]
        prev_cvd_at_low = cvd.loc[prev_low_idx]

        # Regular Bullish Divergence
        if current_price_low < prev_price_low and current_cvd > prev_cvd_at_low:
            return DivergenceType.BULLISH_DIV

        # Regular Bearish Divergence
        if current_price_high > prev_price_high and current_cvd < prev_cvd_at_high:
            return DivergenceType.BEARISH_DIV

        # Hidden Bullish (continuation)
        if current_price_low > prev_price_low and current_cvd < prev_cvd_at_low:
            return DivergenceType.HIDDEN_BULL

        # Hidden Bearish (continuation)
        if current_price_high < prev_price_high and current_cvd > prev_cvd_at_high:
            return DivergenceType.HIDDEN_BEAR

        return DivergenceType.NONE

    def analyze(self, data: pd.DataFrame) -> OrderFlowResult:
        """
        Complete order flow analysis

        Args:
            data: OHLCV DataFrame

        Returns:
            OrderFlowResult with signals
        """
        if len(data) < self.lookback:
            raise ValueError(f"Need at least {self.lookback} bars, got {len(data)}")

        # Use recent data
        recent_data = data.iloc[-self.lookback:].copy()

        # Step 1: Calculate buy/sell volume
        df = self.calculate_buy_sell_volume(recent_data)

        # Step 2: Calculate CVD
        df = self.calculate_cvd(df)

        # Step 3: Volume profile
        volume_profile = self.calculate_volume_profile(df)

        # Step 4: Detect divergence
        divergence = self.detect_divergence(df)

        # Current values
        current_price = df['Close'].iloc[-1]
        current_cvd = df['CVD'].iloc[-1]
        current_cvd_norm = df['CVD_Normalized'].iloc[-1]

        # CVD trend
        cvd_slope = (df['CVD'].iloc[-1] - df['CVD'].iloc[-20]) if len(df) >= 20 else 0
        if cvd_slope > 0:
            cvd_trend = "UP"
            cvd_signal = CVDSignal.BULLISH
        elif cvd_slope < 0:
            cvd_trend = "DOWN"
            cvd_signal = CVDSignal.BEARISH
        else:
            cvd_trend = "FLAT"
            cvd_signal = CVDSignal.NEUTRAL

        # Price trend
        price_slope = (df['Close'].iloc[-1] - df['Close'].iloc[-20]) if len(df) >= 20 else 0

        # Confirm with price
        if cvd_slope > 0 and price_slope > 0:
            cvd_signal = CVDSignal.STRONG_BULLISH
        elif cvd_slope < 0 and price_slope < 0:
            cvd_signal = CVDSignal.STRONG_BEARISH

        # CVD strength (0-100)
        cvd_strength = min(100, int(abs(current_cvd_norm) * 50))

        # Recent buy/sell pressure (last 10 bars)
        recent_buy = df['Buy_Volume_Weighted'].iloc[-10:].sum()
        recent_sell = df['Sell_Volume_Weighted'].iloc[-10:].sum()
        buy_sell_ratio = recent_buy / recent_sell if recent_sell > 0 else 1.0

        if buy_sell_ratio > 1.5:
            imbalance = "STRONG_BUYING"
        elif buy_sell_ratio > 1.1:
            imbalance = "BUYING"
        elif buy_sell_ratio < 0.7:
            imbalance = "STRONG_SELLING"
        elif buy_sell_ratio < 0.9:
            imbalance = "SELLING"
        else:
            imbalance = "BALANCED"

        # Price vs POC
        poc = volume_profile['poc']
        if current_price > poc * 1.01:
            price_vs_poc = "ABOVE"
        elif current_price < poc * 0.99:
            price_vs_poc = "BELOW"
        else:
            price_vs_poc = "AT"

        # Divergence strength
        if divergence in [DivergenceType.BULLISH_DIV, DivergenceType.BEARISH_DIV]:
            div_strength = 80  # Regular divergence strong
        elif divergence in [DivergenceType.HIDDEN_BULL, DivergenceType.HIDDEN_BEAR]:
            div_strength = 60  # Hidden divergence moderate
        else:
            div_strength = 0

        # Overall signal
        score = 0

        # CVD component
        if cvd_signal == CVDSignal.STRONG_BULLISH:
            score += 40
        elif cvd_signal == CVDSignal.BULLISH:
            score += 20
        elif cvd_signal == CVDSignal.BEARISH:
            score -= 20
        elif cvd_signal == CVDSignal.STRONG_BEARISH:
            score -= 40

        # Imbalance component
        if "BUYING" in imbalance:
            score += 20
        elif "SELLING" in imbalance:
            score -= 20

        # Divergence component
        if divergence == DivergenceType.BULLISH_DIV:
            score += 30
        elif divergence == DivergenceType.BEARISH_DIV:
            score -= 30
        elif divergence == DivergenceType.HIDDEN_BULL:
            score += 15
        elif divergence == DivergenceType.HIDDEN_BEAR:
            score -= 15

        # Position vs POC
        if price_vs_poc == "BELOW" and cvd_trend == "UP":
            score += 10  # Accumulation below POC
        elif price_vs_poc == "ABOVE" and cvd_trend == "DOWN":
            score -= 10  # Distribution above POC

        # Final signal
        if score > 40:
            overall = "STRONG_BUY"
        elif score > 20:
            overall = "BUY"
        elif score < -40:
            overall = "STRONG_SELL"
        elif score < -20:
            overall = "SELL"
        else:
            overall = "NEUTRAL"

        confidence = min(100, abs(score))

        # Reasoning
        reasons = []
        if cvd_signal in [CVDSignal.STRONG_BULLISH, CVDSignal.BULLISH]:
            reasons.append(f"CVD trending {cvd_trend}")
        if imbalance != "BALANCED":
            reasons.append(f"Order flow: {imbalance}")
        if divergence != DivergenceType.NONE:
            reasons.append(f"{divergence.value}")
        if price_vs_poc != "AT":
            reasons.append(f"Price {price_vs_poc} POC (${poc:.2f})")

        reasoning = " | ".join(reasons) if reasons else "No clear order flow signal"

        return OrderFlowResult(
            current_cvd=current_cvd,
            cvd_trend=cvd_trend,
            cvd_signal=cvd_signal,
            cvd_strength=cvd_strength,
            divergence=divergence,
            divergence_strength=div_strength,
            poc_price=poc,
            value_area_high=volume_profile['vah'],
            value_area_low=volume_profile['val'],
            price_vs_poc=price_vs_poc,
            recent_buy_volume=recent_buy,
            recent_sell_volume=recent_sell,
            buy_sell_ratio=buy_sell_ratio,
            imbalance_signal=imbalance,
            overall_signal=overall,
            confidence=confidence,
            reasoning=reasoning
        )


def analyze_instrument_order_flow(data: pd.DataFrame) -> OrderFlowResult:
    """
    Quick helper to analyze order flow

    Args:
        data: OHLCV DataFrame

    Returns:
        OrderFlowResult
    """
    analyzer = OrderFlowAnalyzer(lookback=100)
    return analyzer.analyze(data)


if __name__ == "__main__":
    print("Order Flow & CVD Analyzer")
    print("=" * 60)
    print("\nThis module analyzes:")
    print("1. Cumulative Volume Delta (CVD) - buy/sell pressure")
    print("2. Price-CVD divergences - reversal signals")
    print("3. Volume Profile - POC, Value Area")
    print("4. Order flow imbalance - recent buying/selling")
    print("\nUsage:")
    print("  from futures.indicators.order_flow_cvd import analyze_instrument_order_flow")
    print("  result = analyze_instrument_order_flow(data)")
    print("  print(result.overall_signal)  # BUY/SELL/NEUTRAL")
    print("  print(result.reasoning)")
    print("\nLimitations:")
    print("  - Uses OHLCV approximation (not true tick data)")
    print("  - No bid/ask spread info")
    print("  - No Level 2 order book")
    print("  - Best used as confirmation, not primary signal")
