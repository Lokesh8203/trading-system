"""
PAIR TRADE ANALYZER

Reduce directional risk by trading spreads/ratios.

Pair trades:
1. Gold/Silver Ratio (currently low, mean reversion?)
2. Crude Oil vs Gold (risk-on vs risk-off)
3. Nifty vs Bank Nifty (sector rotation)
4. Gold vs Dollar Index (inverse correlation)

Benefits:
- Reduced directional risk (market neutral)
- Lower margin requirements
- Easier to predict (relative value vs absolute)
- Less affected by overall market moves

Usage:
    python3 futures/macro/pair_trade_analyzer.py

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
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from scipy import stats


@dataclass
class PairTrade:
    """Pair trade opportunity"""
    name: str
    leg1_instrument: str
    leg2_instrument: str

    direction: str  # LONG spread, SHORT spread

    # Ratio/Spread
    current_ratio: float
    mean_ratio: float
    std_ratio: float
    z_score: float

    # Historical stats
    ratio_high: float
    ratio_low: float
    mean_reversion_probability: float

    # Trade setup
    entry_ratio: float
    target_ratio: float
    stop_ratio: float

    # Returns
    expected_return: float
    best_case: float
    worst_case: float

    # Risk metrics
    correlation: float  # -1 to 1 (lower = better for pair)
    volatility_ratio: float

    # Execution
    leg1_size: int
    leg2_size: int
    hedge_ratio: float

    # Rollover
    leg1_expiry: str
    leg2_expiry: str
    rollover_compatible: bool

    reasoning: str
    disruption_factors: List[str]


class PairTradeAnalyzer:
    """Analyze pair trading opportunities"""

    def __init__(self):
        self.pairs = {
            'GOLD_SILVER': {
                'leg1': 'GC=F',
                'leg2': 'SI=F',
                'name': 'Gold/Silver Ratio',
                'description': 'Silver cheap vs Gold'
            },
            'CRUDE_GOLD': {
                'leg1': 'CL=F',
                'leg2': 'GC=F',
                'name': 'Crude/Gold Ratio',
                'description': 'Risk-on (crude) vs Risk-off (gold)'
            },
            'NIFTY_BANKNIFTY': {
                'leg1': '^NSEI',
                'leg2': '^NSEBANK',
                'name': 'Nifty/Bank Nifty Ratio',
                'description': 'Broad market vs Banking sector'
            }
        }

    def fetch_data(self, ticker: str, years: int = 5) -> pd.DataFrame:
        """Fetch data"""
        end = datetime.now()
        start = end - timedelta(days=years*365)
        data = yf.download(ticker, start=start, end=end, progress=False)

        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.get_level_values(0)

        return data

    def calculate_ratio_stats(self, data1: pd.DataFrame, data2: pd.DataFrame) -> Dict:
        """
        Calculate ratio statistics

        Args:
            data1: Numerator (leg 1)
            data2: Denominator (leg 2)
        """
        # Align data
        combined = pd.DataFrame({
            'price1': data1['Close'],
            'price2': data2['Close']
        }).dropna()

        # Calculate ratio
        combined['ratio'] = combined['price1'] / combined['price2']

        # Statistics
        current_ratio = combined['ratio'].iloc[-1]
        mean_ratio = combined['ratio'].mean()
        std_ratio = combined['ratio'].std()
        z_score = (current_ratio - mean_ratio) / std_ratio if std_ratio > 0 else 0

        # Extremes
        ratio_high = combined['ratio'].max()
        ratio_low = combined['ratio'].min()

        # Mean reversion probability
        # How often does ratio revert to mean after moving 1σ away?
        above_1sigma = combined[combined['ratio'] > mean_ratio + std_ratio].index
        reversion_count = 0

        for idx in above_1sigma:
            # Look ahead 60 days
            idx_pos = combined.index.get_loc(idx)
            if idx_pos + 60 < len(combined):
                future = combined['ratio'].iloc[idx_pos:idx_pos+60]
                if future.min() < mean_ratio:
                    reversion_count += 1

        reversion_prob = reversion_count / len(above_1sigma) * 100 if len(above_1sigma) > 0 else 0

        # Correlation (lower = better for pair trading)
        correlation = combined['price1'].corr(combined['price2'])

        return {
            'current': current_ratio,
            'mean': mean_ratio,
            'std': std_ratio,
            'z_score': z_score,
            'high': ratio_high,
            'low': ratio_low,
            'reversion_probability': reversion_prob,
            'correlation': correlation,
            'data': combined
        }

    def analyze_gold_silver_ratio(self) -> PairTrade:
        """
        Gold/Silver Ratio Analysis

        Historical context:
        - Normal range: 60-80
        - Silver bull markets: Ratio falls to 40-50 (silver outperforms)
        - Gold bull markets: Ratio rises to 90-100 (gold outperforms)
        - Current: ~60 (low, silver relatively expensive)

        Thesis 1: LONG ratio (short silver vs long gold) if ratio < 55
        Thesis 2: SHORT ratio (long silver vs short gold) if ratio > 75
        """
        print("\n" + "="*100)
        print("GOLD/SILVER RATIO ANALYSIS")
        print("="*100)

        gold_data = self.fetch_data('GC=F', years=10)
        silver_data = self.fetch_data('SI=F', years=10)

        stats = self.calculate_ratio_stats(gold_data, silver_data)

        current = stats['current']
        mean = stats['mean']
        z_score = stats['z_score']

        print(f"\n📊 Current Ratio: {current:.1f}")
        print(f"   Long-term Mean: {mean:.1f}")
        print(f"   Standard Deviation: {stats['std']:.1f}")
        print(f"   Z-Score: {z_score:.2f}σ")
        print(f"   Historical Range: {stats['low']:.1f} - {stats['high']:.1f}")

        print(f"\n📈 Historical Context:")
        print(f"   Normal Range: 60-80")
        print(f"   Silver Bull (ratio falls): 40-50")
        print(f"   Gold Bull (ratio rises): 90-100")
        print(f"   Current: {current:.1f}")

        # Determine trade direction
        if current < 55:
            direction = "LONG RATIO (Long Gold, Short Silver)"
            reasoning = f"Ratio at {current:.1f} is very low. Silver expensive vs gold. Expect mean reversion."
            entry = current
            target = mean
            stop = current - stats['std']
            expected_return = (target - entry) / entry * 100

        elif current > 75:
            direction = "SHORT RATIO (Short Gold, Long Silver)"
            reasoning = f"Ratio at {current:.1f} is high. Silver cheap vs gold. Expect mean reversion."
            entry = current
            target = mean
            stop = current + stats['std']
            expected_return = (entry - target) / entry * 100

        else:
            direction = "SHORT RATIO (Long Silver vs Gold)"
            reasoning = f"Ratio at {current:.1f} is low-to-mid range. Silver has industrial demand + safe haven. Gold only safe haven."
            entry = current
            target = current - 5  # Target 5 point drop
            stop = current + 5
            expected_return = (entry - target) / entry * 100

        print(f"\n💡 TRADE SETUP:")
        print(f"   Direction: {direction}")
        print(f"   Entry Ratio: {entry:.1f}")
        print(f"   Target Ratio: {target:.1f}")
        print(f"   Stop Ratio: {stop:.1f}")
        print(f"   Expected Return: {expected_return:+.1f}%")

        # Why silver outperforms
        print(f"\n🥈 Why Silver > Gold (Ratio Falls)?")
        print(f"   1. Industrial Demand: 50% of silver demand is industrial (solar, EVs, electronics)")
        print(f"      - Gold: <10% industrial")
        print(f"   2. Supply Deficit: Silver has structural supply deficit (more demand than production)")
        print(f"   3. Smaller Market: $1T silver vs $12T gold = easier to move")
        print(f"   4. Dual Demand: Silver gets BOTH safe haven + industrial demand")
        print(f"      - During recovery: Industrial demand boosts silver")
        print(f"      - During crisis: Safe haven demand boosts both, but silver catches up")
        print(f"   5. Mean Reversion: Ratio at {current:.1f} vs mean {mean:.1f}")

        # Historical performance
        print(f"\n📉 Historical Mean Reversion:")
        print(f"   Probability: {stats['reversion_probability']:.0f}%")
        print(f"   Correlation: {stats['correlation']:.2f} (1.0 = perfect, lower = better for pairs)")

        # Disruption factors
        disruptions = [
            "Gold spike on geopolitical crisis (flight to safety)",
            "Silver industrial demand collapse (recession)",
            "Gold central bank buying surge",
            "Silver mine supply increase"
        ]

        print(f"\n⚠️  Disruption Factors:")
        for d in disruptions:
            print(f"   - {d}")

        # Hedge ratio
        gold_price = gold_data['Close'].iloc[-1]
        silver_price = silver_data['Close'].iloc[-1]

        # For $10,000 position
        # If shorting ratio: Long silver, short gold
        # Want equal dollar exposure

        gold_contracts = 1  # 100 oz
        gold_value = gold_contracts * 100 * gold_price

        # Match with silver
        silver_contracts = gold_value / (5000 * silver_price)  # 5000 oz per contract

        print(f"\n💼 Hedge Ratio (Equal Dollar Exposure):")
        print(f"   Gold: {gold_contracts} contract (100 oz) = ${gold_value:,.0f}")
        print(f"   Silver: {silver_contracts:.1f} contracts (5000 oz each)")
        print(f"   Ratio: 1 Gold : {silver_contracts:.1f} Silver")

        return PairTrade(
            name="Gold/Silver Ratio",
            leg1_instrument="GOLD (GC=F)",
            leg2_instrument="SILVER (SI=F)",
            direction=direction,
            current_ratio=current,
            mean_ratio=mean,
            std_ratio=stats['std'],
            z_score=z_score,
            ratio_high=stats['high'],
            ratio_low=stats['low'],
            mean_reversion_probability=stats['reversion_probability'],
            entry_ratio=entry,
            target_ratio=target,
            stop_ratio=stop,
            expected_return=expected_return,
            best_case=expected_return * 1.5,
            worst_case=-abs(stop - entry) / entry * 100,
            correlation=stats['correlation'],
            volatility_ratio=1.0,  # Simplified
            leg1_size=gold_contracts,
            leg2_size=int(silver_contracts),
            hedge_ratio=silver_contracts,
            leg1_expiry="Monthly",
            leg2_expiry="Monthly",
            rollover_compatible=True,
            reasoning=reasoning,
            disruption_factors=disruptions
        )

    def analyze_crude_gold_ratio(self) -> PairTrade:
        """
        Crude Oil / Gold Ratio

        Interpretation:
        - High ratio: Risk-on (crude strong, gold weak) = Economic growth
        - Low ratio: Risk-off (crude weak, gold strong) = Economic fear

        Current thesis: War risk elevated but not extreme
        - If war escalates: Crude up, gold up (ratio stable)
        - If war ends: Crude down, gold stable (ratio down)
        - If recession: Crude down, gold up (ratio down sharply)
        """
        print("\n" + "="*100)
        print("CRUDE OIL / GOLD RATIO ANALYSIS")
        print("="*100)

        crude_data = self.fetch_data('CL=F', years=5)
        gold_data = self.fetch_data('GC=F', years=5)

        stats = self.calculate_ratio_stats(crude_data, gold_data)

        current = stats['current']
        mean = stats['mean']
        z_score = stats['z_score']

        print(f"\n📊 Current Ratio: {current:.3f}")
        print(f"   Long-term Mean: {mean:.3f}")
        print(f"   Z-Score: {z_score:.2f}σ")

        print(f"\n💡 Interpretation:")
        if z_score > 1:
            print(f"   RISK-ON: Crude strong vs Gold (ratio high)")
            print(f"   → Markets pricing growth, not fear")
            direction = "SHORT RATIO (Short Crude, Long Gold)"
            reasoning = "Ratio extended, mean reversion expected"
        elif z_score < -1:
            print(f"   RISK-OFF: Gold strong vs Crude (ratio low)")
            print(f"   → Markets pricing fear, not growth")
            direction = "LONG RATIO (Long Crude, Short Gold)"
            reasoning = "Ratio depressed, recovery expected"
        else:
            print(f"   NEUTRAL: Balanced risk sentiment")
            direction = "WAIT"
            reasoning = "No clear edge"

        return PairTrade(
            name="Crude/Gold Ratio",
            leg1_instrument="CRUDE (CL=F)",
            leg2_instrument="GOLD (GC=F)",
            direction=direction,
            current_ratio=current,
            mean_ratio=mean,
            std_ratio=stats['std'],
            z_score=z_score,
            ratio_high=stats['high'],
            ratio_low=stats['low'],
            mean_reversion_probability=stats['reversion_probability'],
            entry_ratio=current,
            target_ratio=mean,
            stop_ratio=current + stats['std'] if z_score > 0 else current - stats['std'],
            expected_return=(mean - current) / current * 100 if z_score > 0 else (current - mean) / current * 100,
            best_case=10,
            worst_case=-5,
            correlation=stats['correlation'],
            volatility_ratio=1.0,
            leg1_size=1,
            leg2_size=1,
            hedge_ratio=1.0,
            leg1_expiry="Monthly",
            leg2_expiry="Monthly",
            rollover_compatible=True,
            reasoning=reasoning,
            disruption_factors=[
                "War escalation (both up)",
                "Recession (crude down, gold up)",
                "Fed policy shift"
            ]
        )

    def scan_all_pairs(self) -> List[PairTrade]:
        """Scan all pair opportunities"""
        results = []

        results.append(self.analyze_gold_silver_ratio())
        results.append(self.analyze_crude_gold_ratio())

        return results


def main():
    analyzer = PairTradeAnalyzer()
    results = analyzer.scan_all_pairs()

    print("\n" + "="*100)
    print("PAIR TRADE SUMMARY")
    print("="*100)

    for pair in results:
        print(f"\n{pair.name}:")
        print(f"   Direction: {pair.direction}")
        print(f"   Current Ratio: {pair.current_ratio:.2f}")
        print(f"   Z-Score: {pair.z_score:.2f}σ")
        print(f"   Expected Return: {pair.expected_return:+.1f}%")
        print(f"   Mean Reversion Probability: {pair.mean_reversion_probability:.0f}%")
        print(f"   Correlation: {pair.correlation:.2f}")
        print(f"   Rollover Compatible: {'✅' if pair.rollover_compatible else '❌'}")


if __name__ == "__main__":
    main()
