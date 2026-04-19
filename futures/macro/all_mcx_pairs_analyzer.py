"""
ALL MCX PAIR TRADES ANALYZER

Find ALL possible liquid pair trades in MCX, not just Gold/Silver!

MCX Liquid Instruments:
- Metals: Gold, Silver, Copper, Zinc, Lead, Aluminum, Nickel
- Energy: Crude Oil, Natural Gas
- Indices: Nifty, Bank Nifty, Fin Nifty

Possible Pairs (20+):
1. Gold/Silver (safe haven ratio)
2. Crude/Gold (risk-on vs risk-off)
3. Crude/Natural Gas (energy spread)
4. Copper/Gold (industrial vs safe haven)
5. Silver/Copper (industrial metals)
6. Nifty/Bank Nifty (sector rotation)
7. Gold/Copper (flight to safety indicator)
8. Base metals (Copper/Zinc, Aluminum/Copper, etc.)
9. Energy (Crude/Nat Gas calendar spreads)
10. And more...

Usage:
    python3 futures/macro/all_mcx_pairs_analyzer.py

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

# Import Hurst exponent for regime detection
from futures.indicators.hurst_exponent import HurstExponentCalculator, MarketRegime


@dataclass
class PairOpportunity:
    """Pair trade opportunity"""
    name: str
    leg1: str
    leg2: str
    category: str  # METALS, ENERGY, INDICES, CROSS-ASSET

    current_ratio: float
    mean_ratio: float
    z_score: float

    direction: str  # LONG ratio (leg1 up, leg2 down) or SHORT ratio
    trade_description: str

    entry: float
    target: float
    stop: float

    expected_return: float
    probability: float

    correlation: float
    liquidity_score: int  # 0-100
    rollover_compatible: bool

    reasoning: str
    score: int  # Overall 0-100

    # Hurst regime analysis
    leg1_hurst: float = 0.5
    leg2_hurst: float = 0.5
    leg1_regime: str = "UNKNOWN"
    leg2_regime: str = "UNKNOWN"
    hurst_signal: str = ""


class AllMCXPairsAnalyzer:
    """Find ALL liquid MCX pair opportunities"""

    def __init__(self):
        # Initialize Hurst calculator
        self.hurst_calc = HurstExponentCalculator()

        # MCX instruments with yfinance proxies
        self.instruments = {
            # Precious Metals
            'GOLD': 'GC=F',
            'SILVER': 'SI=F',

            # Energy
            'CRUDE': 'CL=F',
            'NATGAS': 'NG=F',

            # Base Metals
            'COPPER': 'HG=F',
            'ZINC': 'ZN=F',  # Using zinc futures proxy
            'ALUMINUM': 'ALI=F',  # Aluminum proxy

            # Indices
            'NIFTY': '^NSEI',
            'BANKNIFTY': '^NSEBANK',
        }

        # Define pair universe
        self.pair_definitions = [
            # SAFE HAVEN vs INDUSTRIAL
            {
                'name': 'Gold/Silver Ratio',
                'leg1': 'GOLD',
                'leg2': 'SILVER',
                'category': 'METALS',
                'description': 'Safe haven ratio - silver has industrial demand',
                'liquidity': 100
            },
            {
                'name': 'Gold/Copper Ratio',
                'leg1': 'GOLD',
                'leg2': 'COPPER',
                'category': 'CROSS-ASSET',
                'description': 'Flight to safety indicator - copper is pure industrial',
                'liquidity': 85
            },
            {
                'name': 'Silver/Copper Ratio',
                'leg1': 'SILVER',
                'leg2': 'COPPER',
                'category': 'METALS',
                'description': 'Industrial metals - both sensitive to economy',
                'liquidity': 80
            },

            # RISK-ON vs RISK-OFF
            {
                'name': 'Crude/Gold Ratio',
                'leg1': 'CRUDE',
                'leg2': 'GOLD',
                'category': 'CROSS-ASSET',
                'description': 'Risk-on (crude) vs Risk-off (gold) sentiment',
                'liquidity': 95
            },

            # ENERGY SPREADS
            {
                'name': 'Crude/NatGas Ratio',
                'leg1': 'CRUDE',
                'leg2': 'NATGAS',
                'category': 'ENERGY',
                'description': 'Energy spread - oil vs gas pricing arbitrage',
                'liquidity': 90
            },

            # INDICES (SECTOR ROTATION)
            {
                'name': 'Nifty/BankNifty Ratio',
                'leg1': 'NIFTY',
                'leg2': 'BANKNIFTY',
                'category': 'INDICES',
                'description': 'Broad market vs Banking sector rotation',
                'liquidity': 95
            },

            # BASE METALS (ECONOMIC INDICATORS)
            {
                'name': 'Copper/Zinc Ratio',
                'leg1': 'COPPER',
                'leg2': 'ZINC',
                'category': 'METALS',
                'description': 'Industrial metals spread - construction demand',
                'liquidity': 70
            },

            # MIXED (ENERGY vs METALS)
            {
                'name': 'Crude/Copper Ratio',
                'leg1': 'CRUDE',
                'leg2': 'COPPER',
                'category': 'CROSS-ASSET',
                'description': 'Energy vs Industrial - economy strength indicator',
                'liquidity': 75
            },
            {
                'name': 'Crude/Silver Ratio',
                'leg1': 'CRUDE',
                'leg2': 'SILVER',
                'category': 'CROSS-ASSET',
                'description': 'Energy vs dual-demand metal',
                'liquidity': 80
            },
        ]

    def fetch_data(self, ticker: str, years: int = 3) -> Optional[pd.DataFrame]:
        """Fetch data with error handling"""
        try:
            end = datetime.now()
            start = end - timedelta(days=years*365)
            data = yf.download(ticker, start=start, end=end, progress=False)

            if isinstance(data.columns, pd.MultiIndex):
                data.columns = data.columns.get_level_values(0)

            if len(data) < 100:
                return None

            return data
        except:
            return None

    def analyze_ratio(self, data1: pd.DataFrame, data2: pd.DataFrame) -> Optional[Dict]:
        """Calculate ratio statistics"""
        try:
            combined = pd.DataFrame({
                'price1': data1['Close'],
                'price2': data2['Close']
            }).dropna()

            if len(combined) < 100:
                return None

            combined['ratio'] = combined['price1'] / combined['price2']

            current = combined['ratio'].iloc[-1]
            mean = combined['ratio'].mean()
            std = combined['ratio'].std()
            z_score = (current - mean) / std if std > 0 else 0

            # Mean reversion analysis
            above_1sigma = combined[combined['ratio'] > mean + std]
            below_1sigma = combined[combined['ratio'] < mean - std]

            reversion_count = 0
            extreme_count = len(above_1sigma) + len(below_1sigma)

            for idx in above_1sigma.index:
                idx_pos = combined.index.get_loc(idx)
                if idx_pos + 60 < len(combined):
                    future = combined['ratio'].iloc[idx_pos:idx_pos+60]
                    if future.min() < mean:
                        reversion_count += 1

            for idx in below_1sigma.index:
                idx_pos = combined.index.get_loc(idx)
                if idx_pos + 60 < len(combined):
                    future = combined['ratio'].iloc[idx_pos:idx_pos+60]
                    if future.max() > mean:
                        reversion_count += 1

            reversion_prob = (reversion_count / extreme_count * 100) if extreme_count > 0 else 0

            correlation = combined['price1'].corr(combined['price2'])

            return {
                'current': current,
                'mean': mean,
                'std': std,
                'z_score': z_score,
                'high': combined['ratio'].max(),
                'low': combined['ratio'].min(),
                'reversion_probability': reversion_prob,
                'correlation': correlation
            }
        except:
            return None

    def calculate_hurst_regimes(self, data1: pd.DataFrame, data2: pd.DataFrame) -> Dict:
        """Calculate Hurst exponent for both legs"""
        try:
            # Calculate Hurst for leg 1
            hurst1_result = self.hurst_calc.calculate(data1['Close'], lookback=100)

            # Calculate Hurst for leg 2
            hurst2_result = self.hurst_calc.calculate(data2['Close'], lookback=100)

            # Generate signal based on Hurst regimes
            h1 = hurst1_result.hurst_exponent
            h2 = hurst2_result.hurst_exponent

            # Ideal scenarios for pair trades:
            # 1. Both mean-reverting (H<0.4) → ratio likely to mean revert
            # 2. One trending, one mean-reverting → directional edge
            # 3. Both trending in same direction → poor for pairs

            if h1 < 0.4 and h2 < 0.4:
                signal = "EXCELLENT - Both legs mean-reverting, ratio trade ideal"
                hurst_bonus = 15
            elif h1 < 0.45 or h2 < 0.45:
                signal = "GOOD - At least one leg mean-reverting"
                hurst_bonus = 10
            elif h1 > 0.6 and h2 > 0.6:
                signal = "CAUTION - Both trending, ratio may not revert"
                hurst_bonus = -10
            elif abs(h1 - h2) > 0.2:
                signal = "MIXED - Regime divergence, directional edge"
                hurst_bonus = 5
            else:
                signal = "NEUTRAL - Choppy regimes"
                hurst_bonus = 0

            return {
                'leg1_hurst': h1,
                'leg2_hurst': h2,
                'leg1_regime': hurst1_result.regime.value,
                'leg2_regime': hurst2_result.regime.value,
                'signal': signal,
                'bonus': hurst_bonus
            }
        except:
            # If Hurst fails, return neutral
            return {
                'leg1_hurst': 0.5,
                'leg2_hurst': 0.5,
                'leg1_regime': 'UNKNOWN',
                'leg2_regime': 'UNKNOWN',
                'signal': 'N/A',
                'bonus': 0
            }

    def calculate_opportunity_score(self, stats: Dict, liquidity: int, hurst_bonus: int = 0) -> int:
        """
        Score pair opportunity 0-100

        Factors:
        - Z-score magnitude (higher = better mean reversion opportunity)
        - Reversion probability
        - Correlation (lower = better for pair trading)
        - Liquidity
        - Hurst regime bonus/penalty
        """
        score = 0

        # Z-score component (0-40 pts)
        abs_z = abs(stats['z_score'])
        if abs_z > 2.5:
            score += 40
        elif abs_z > 2.0:
            score += 35
        elif abs_z > 1.5:
            score += 25
        elif abs_z > 1.0:
            score += 15
        else:
            score += 5

        # Reversion probability (0-30 pts)
        rev_prob = stats['reversion_probability']
        if rev_prob > 70:
            score += 30
        elif rev_prob > 50:
            score += 20
        elif rev_prob > 30:
            score += 10
        else:
            score += 5

        # Correlation (0-20 pts) - lower is better
        corr = stats['correlation']
        if corr < 0.5:
            score += 20  # Low correlation = good for pairs
        elif corr < 0.7:
            score += 15
        elif corr < 0.85:
            score += 10
        else:
            score += 5  # High correlation = not ideal

        # Liquidity (0-10 pts)
        score += int(liquidity / 10)

        # Hurst regime bonus (-10 to +15 pts)
        score += hurst_bonus

        return min(100, max(0, score))

    def analyze_pair(self, pair_def: Dict) -> Optional[PairOpportunity]:
        """Analyze single pair"""
        leg1_ticker = self.instruments.get(pair_def['leg1'])
        leg2_ticker = self.instruments.get(pair_def['leg2'])

        if not leg1_ticker or not leg2_ticker:
            return None

        # Fetch data
        data1 = self.fetch_data(leg1_ticker, years=3)
        data2 = self.fetch_data(leg2_ticker, years=3)

        if data1 is None or data2 is None:
            return None

        # Analyze ratio
        stats = self.analyze_ratio(data1, data2)
        if stats is None:
            return None

        # Calculate Hurst regimes
        hurst_info = self.calculate_hurst_regimes(data1, data2)

        # Determine direction
        z = stats['z_score']
        current = stats['current']
        mean = stats['mean']
        std = stats['std']

        if z > 1:  # Ratio high, bet on reversion down
            direction = "SHORT RATIO"
            trade_desc = f"Short {pair_def['leg1']}, Long {pair_def['leg2']}"
            entry = current
            target = mean
            stop = current + std
            expected_return = (entry - target) / entry * 100
        elif z < -1:  # Ratio low, bet on reversion up
            direction = "LONG RATIO"
            trade_desc = f"Long {pair_def['leg1']}, Short {pair_def['leg2']}"
            entry = current
            target = mean
            stop = current - std
            expected_return = (target - entry) / entry * 100
        else:  # Neutral, look for direction
            if z > 0:
                direction = "SHORT RATIO"
                trade_desc = f"Short {pair_def['leg1']}, Long {pair_def['leg2']}"
            else:
                direction = "LONG RATIO"
                trade_desc = f"Long {pair_def['leg1']}, Short {pair_def['leg2']}"
            entry = current
            target = mean
            stop = current + (std if z > 0 else -std)
            expected_return = abs(mean - current) / current * 100

        # Score (including Hurst bonus)
        score = self.calculate_opportunity_score(stats, pair_def['liquidity'], hurst_info['bonus'])

        # Reasoning
        if abs(z) > 2:
            reasoning = f"Ratio at {z:.2f}σ - EXTREME deviation, high mean reversion probability"
        elif abs(z) > 1.5:
            reasoning = f"Ratio at {z:.2f}σ - Significant deviation from mean"
        elif abs(z) > 1:
            reasoning = f"Ratio at {z:.2f}σ - Moderate deviation, watch for entry"
        else:
            reasoning = f"Ratio at {z:.2f}σ - Near mean, no clear edge"

        return PairOpportunity(
            name=pair_def['name'],
            leg1=pair_def['leg1'],
            leg2=pair_def['leg2'],
            category=pair_def['category'],
            current_ratio=current,
            mean_ratio=mean,
            z_score=z,
            direction=direction,
            trade_description=trade_desc,
            entry=entry,
            target=target,
            stop=stop,
            expected_return=expected_return,
            probability=stats['reversion_probability'],
            correlation=stats['correlation'],
            liquidity_score=pair_def['liquidity'],
            rollover_compatible=True,  # All MCX monthly
            reasoning=reasoning,
            score=score,
            leg1_hurst=hurst_info['leg1_hurst'],
            leg2_hurst=hurst_info['leg2_hurst'],
            leg1_regime=hurst_info['leg1_regime'],
            leg2_regime=hurst_info['leg2_regime'],
            hurst_signal=hurst_info['signal']
        )

    def scan_all_pairs(self) -> List[PairOpportunity]:
        """Scan all pairs"""
        opportunities = []

        print(f"\n{'='*100}")
        print(f"ALL MCX PAIR TRADES SCANNER")
        print(f"{'='*100}")
        print(f"Scanning {len(self.pair_definitions)} pair combinations...\n")

        for pair_def in self.pair_definitions:
            print(f"📊 Analyzing {pair_def['name']}...")

            opp = self.analyze_pair(pair_def)

            if opp:
                print(f"   ✅ Score: {opp.score}/100")
                print(f"   Z-score: {opp.z_score:.2f}σ")
                print(f"   Direction: {opp.direction}")
                print(f"   Expected: {opp.expected_return:+.1f}%")
                print()
                opportunities.append(opp)
            else:
                print(f"   ❌ Insufficient data\n")

        # Sort by score
        opportunities.sort(key=lambda x: x.score, reverse=True)

        return opportunities

    def display_results(self, opportunities: List[PairOpportunity]):
        """Display ranked results"""
        print(f"\n{'='*100}")
        print(f"RANKED PAIR TRADE OPPORTUNITIES")
        print(f"{'='*100}\n")

        for i, opp in enumerate(opportunities, 1):
            print(f"{i}. {opp.name} - Score: {opp.score}/100 [{opp.category}]")
            print(f"   {'='*95}")
            print(f"   Current Ratio: {opp.current_ratio:.3f}")
            print(f"   Mean: {opp.mean_ratio:.3f} | Z-Score: {opp.z_score:.2f}σ")
            print(f"\n   Trade: {opp.direction}")
            print(f"   → {opp.trade_description}")
            print(f"\n   Entry: {opp.entry:.3f}")
            print(f"   Target: {opp.target:.3f} ({opp.expected_return:+.1f}%)")
            print(f"   Stop: {opp.stop:.3f}")
            print(f"\n   Reversion Probability: {opp.probability:.0f}%")
            print(f"   Correlation: {opp.correlation:.2f}")
            print(f"   Liquidity: {opp.liquidity_score}/100")

            # Hurst regime analysis
            print(f"\n   📊 HURST REGIME ANALYSIS:")
            print(f"   {opp.leg1} Hurst: {opp.leg1_hurst:.3f} ({opp.leg1_regime})")
            print(f"   {opp.leg2} Hurst: {opp.leg2_hurst:.3f} ({opp.leg2_regime})")
            print(f"   Signal: {opp.hurst_signal}")

            print(f"\n   💡 {opp.reasoning}")
            print()

        # Summary by category
        print(f"{'='*100}")
        print(f"SUMMARY BY CATEGORY")
        print(f"{'='*100}\n")

        by_category = {}
        for opp in opportunities:
            if opp.category not in by_category:
                by_category[opp.category] = []
            by_category[opp.category].append(opp)

        for category, opps in by_category.items():
            avg_score = sum(o.score for o in opps) / len(opps)
            high_score = [o for o in opps if o.score >= 70]

            print(f"{category}:")
            print(f"   Total: {len(opps)} pairs")
            print(f"   Avg Score: {avg_score:.0f}/100")
            print(f"   High Conviction (70+): {len(high_score)}")
            print()


def main():
    analyzer = AllMCXPairsAnalyzer()
    opportunities = analyzer.scan_all_pairs()
    analyzer.display_results(opportunities)

    print(f"{'='*100}")
    print(f"Total liquid pair opportunities found: {len(opportunities)}")
    print(f"High conviction (70+): {len([o for o in opportunities if o.score >= 70])}")
    print(f"Moderate (50-69): {len([o for o in opportunities if 50 <= o.score < 70])}")
    print(f"{'='*100}\n")


if __name__ == "__main__":
    main()
