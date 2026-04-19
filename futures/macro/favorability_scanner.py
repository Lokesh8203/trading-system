"""
MACRO TRADE FAVORABILITY SCANNER

Real-time favorability index (0-100) for macro opportunities.
Works anytime - weekend, weeknight, market closed.

Score based on:
1. Historical position (support/resistance proximity)
2. Volatility regime
3. Technical setup (trend, momentum)
4. Fundamental catalyst strength
5. Risk/reward at current levels

Usage:
    python3 futures/macro/favorability_scanner.py

Output:
    - Favorability score (0-100) for each opportunity
    - Best/Average/Worst case returns
    - Recommended action (BUY/SELL/WAIT)
    - Gap risk assessment
    - Position sizing

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
class FavorabilityScore:
    """Trade favorability assessment"""
    instrument: str
    direction: str  # LONG/SHORT

    # Overall score
    favorability_score: int  # 0-100
    recommendation: str  # BUY/SELL/WAIT

    # Current market state
    current_price: float
    global_instrument: str  # For commodities
    mcx_equivalent: str  # MCX contract
    conversion_factor: float  # Global to MCX

    # Historical positioning
    percentile_52w: float  # Where are we in 52-week range?
    distance_from_support: float
    distance_from_resistance: float

    # Volatility
    current_volatility: float
    avg_volatility: float
    volatility_regime: str

    # Returns projection
    best_case_return: float
    avg_case_return: float
    worst_case_return: float
    probability_profitable: float

    # Risk assessment
    gap_risk_score: int  # 0-100 (100 = very high gap risk)
    position_size_recommended: float  # % of capital
    max_risk_pct: float

    # Breakdown
    score_breakdown: Dict[str, int]
    reasoning: str


class FavorabilityScanner:
    """Score macro opportunities in real-time"""

    def __init__(self, capital: float = 1200000):
        self.capital = capital

        # Global to MCX mapping
        self.instrument_map = {
            'GOLD': {
                'global': 'GC=F',  # COMEX Gold
                'mcx': 'GOLDM',  # Gold Mini MCX (100g)
                'conversion': 321.5,  # Approx oz to 10g (1 oz = 31.1g)
                'lot_size': 100,  # 100g per lot
                'tick_value': 1  # ₹1 per gram
            },
            'SILVER': {
                'global': 'SI=F',  # COMEX Silver
                'mcx': 'SILVER',  # Silver MCX
                'conversion': 31.1,  # Oz to kg (1 oz = 31.1g, 1000g/kg)
                'lot_size': 30,  # 30kg per lot
                'tick_value': 1  # ₹1 per kg
            },
            'CRUDE': {
                'global': 'CL=F',  # WTI Crude
                'mcx': 'CRUDEOIL',
                'conversion': 1,  # Both in barrels
                'lot_size': 100,  # 100 barrels
                'tick_value': 1  # ₹1 per barrel
            },
            'NIFTY': {
                'global': '^NSEI',  # Nifty Index
                'mcx': 'NIFTY_FUT',
                'conversion': 1,
                'lot_size': 50,  # 50 units
                'tick_value': 1
            },
            'BANKNIFTY': {
                'global': '^NSEBANK',
                'mcx': 'BANKNIFTY_FUT',
                'conversion': 1,
                'lot_size': 15,  # 15 units
                'tick_value': 1
            }
        }

    def fetch_data(self, ticker: str, years: int = 3) -> pd.DataFrame:
        """Fetch data with MultiIndex handling"""
        end = datetime.now()
        start = end - timedelta(days=years*365)
        data = yf.download(ticker, start=start, end=end, progress=False)

        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.get_level_values(0)

        return data

    def calculate_percentile_position(self, data: pd.DataFrame, window: int = 252) -> Dict:
        """Where is current price in historical range?"""
        recent = data.tail(window)
        current = data['Close'].iloc[-1]

        low_52w = recent['Low'].min()
        high_52w = recent['High'].max()

        percentile = (current - low_52w) / (high_52w - low_52w) * 100 if high_52w > low_52w else 50

        return {
            'current': current,
            'low_52w': low_52w,
            'high_52w': high_52w,
            'percentile': percentile,
            'range': high_52w - low_52w
        }

    def find_key_levels(self, data: pd.DataFrame) -> Dict:
        """Find support/resistance levels"""
        # Simple approach: recent swing highs/lows
        window = 252
        recent = data.tail(window)

        # Find local maxima/minima
        highs = []
        lows = []

        for i in range(20, len(recent)-20):
            if recent['High'].iloc[i] == recent['High'].iloc[i-20:i+20].max():
                highs.append(recent['High'].iloc[i])
            if recent['Low'].iloc[i] == recent['Low'].iloc[i-20:i+20].min():
                lows.append(recent['Low'].iloc[i])

        current = data['Close'].iloc[-1]

        # Nearest levels
        supports = [l for l in lows if l < current]
        resistances = [h for h in highs if h > current]

        nearest_support = max(supports) if supports else current * 0.9
        nearest_resistance = min(resistances) if resistances else current * 1.1

        return {
            'nearest_support': nearest_support,
            'nearest_resistance': nearest_resistance,
            'support_distance': (current - nearest_support) / current * 100,
            'resistance_distance': (nearest_resistance - current) / current * 100
        }

    def analyze_volatility(self, data: pd.DataFrame) -> Dict:
        """Current vs average volatility"""
        data = data.copy()
        data['Returns'] = data['Close'].pct_change()
        data['Volatility'] = data['Returns'].rolling(20).std() * np.sqrt(252) * 100

        current_vol = data['Volatility'].iloc[-1]
        avg_vol = data['Volatility'].mean()
        std_vol = data['Volatility'].std()

        # Z-score
        z_score = (current_vol - avg_vol) / std_vol if std_vol > 0 else 0

        if z_score > 2:
            regime = 'EXTREME_HIGH'
        elif z_score > 1:
            regime = 'HIGH'
        elif z_score < -1:
            regime = 'LOW'
        else:
            regime = 'NORMAL'

        return {
            'current': current_vol,
            'average': avg_vol,
            'z_score': z_score,
            'regime': regime,
            'percentile': stats.percentileofscore(data['Volatility'].dropna(), current_vol)
        }

    def analyze_war_premium_crude(self, data: pd.DataFrame) -> Dict:
        """
        Special analysis for crude oil during war scenarios

        Questions:
        1. Where are we historically during wars?
        2. Have we hit 3 sigma spike?
        3. Is there more upside or mean reversion coming?
        """
        data = data.copy()

        # Calculate z-score from long-term mean
        mean_price = data['Close'].mean()
        std_price = data['Close'].std()
        current_price = data['Close'].iloc[-1]

        z_score = (current_price - mean_price) / std_price

        # Find historical war spikes (>2 sigma events)
        data['Z_Score'] = (data['Close'] - mean_price) / std_price
        war_spikes = data[data['Z_Score'] > 2].copy()

        # How many times did we go above 3 sigma?
        extreme_spikes = len(data[data['Z_Score'] > 3])
        total_days = len(data)
        extreme_spike_probability = extreme_spikes / total_days * 100

        # Current position
        if z_score > 3:
            war_phase = 'EXTREME (>3σ) - Peak likely near'
        elif z_score > 2:
            war_phase = 'HIGH (2-3σ) - Can spike more to 3σ'
        elif z_score > 1:
            war_phase = 'ELEVATED (1-2σ) - Room to spike'
        else:
            war_phase = 'NORMAL (<1σ) - No war premium priced in'

        # Historical spikes: how long did they last?
        if len(war_spikes) > 0:
            # Group consecutive spike days
            war_spikes['Group'] = (war_spikes.index.to_series().diff() > pd.Timedelta(days=7)).cumsum()
            spike_durations = war_spikes.groupby('Group').size()
            avg_spike_duration = spike_durations.mean()
            max_spike_duration = spike_durations.max()
        else:
            avg_spike_duration = 0
            max_spike_duration = 0

        # Mean reversion: after >2σ, how often did price fall 10% within 60 days?
        reversion_count = 0
        if len(war_spikes) > 0:
            for idx in war_spikes.index:
                spike_price = data.loc[idx, 'Close']
                # Look ahead 60 days
                future_idx = data.index.get_indexer([idx], method='nearest')[0]
                if future_idx + 60 < len(data):
                    future_prices = data['Close'].iloc[future_idx:future_idx+60]
                    if future_prices.min() < spike_price * 0.9:
                        reversion_count += 1

        reversion_rate = reversion_count / len(war_spikes) * 100 if len(war_spikes) > 0 else 0

        return {
            'current_price': current_price,
            'mean_price': mean_price,
            'std_price': std_price,
            'z_score': z_score,
            'war_phase': war_phase,
            'historical_2sigma_events': len(war_spikes),
            'historical_3sigma_events': extreme_spikes,
            'probability_3sigma': extreme_spike_probability,
            'avg_spike_duration_days': avg_spike_duration,
            'max_spike_duration_days': max_spike_duration,
            'reversion_rate_60days': reversion_rate,
            'upside_to_3sigma': (mean_price + 3*std_price - current_price) / current_price * 100,
            'downside_to_mean': (mean_price - current_price) / current_price * 100
        }

    def calculate_gap_risk(self, instrument: str, data: pd.DataFrame) -> Dict:
        """
        Assess overnight/weekend gap risk

        For Nifty/Bank Nifty especially critical
        """
        data = data.copy()

        # Calculate gaps
        data['Gap'] = (data['Open'] - data['Close'].shift(1)) / data['Close'].shift(1) * 100

        # Statistics
        gaps = data['Gap'].dropna()
        avg_gap = gaps.mean()
        std_gap = gaps.std()
        max_gap_up = gaps.max()
        max_gap_down = gaps.min()

        # Count significant gaps (>1%)
        large_gaps = gaps[abs(gaps) > 1]
        gap_frequency = len(large_gaps) / len(gaps) * 100

        # For indices: check if GIFT Nifty correlation helps
        if instrument in ['NIFTY', 'BANKNIFTY']:
            gap_risk_score = 80  # High for indices (no 24hr market)
            mitigation = "Use GIFT Nifty for pre-market indication"
        else:
            gap_risk_score = 40  # Lower for commodities (24hr markets)
            mitigation = "Track global markets during Asian/European sessions"

        return {
            'avg_gap': avg_gap,
            'std_gap': std_gap,
            'max_gap_up': max_gap_up,
            'max_gap_down': max_gap_down,
            'gap_frequency': gap_frequency,
            'gap_risk_score': gap_risk_score,
            'mitigation': mitigation
        }

    def calculate_favorability_score(self,
                                     instrument: str,
                                     direction: str,
                                     data: pd.DataFrame,
                                     catalyst: str = "") -> FavorabilityScore:
        """
        Calculate overall favorability score (0-100)

        Scoring components:
        - Historical position (30 pts): Better if near support for longs, resistance for shorts
        - Volatility regime (20 pts): High vol = more opportunity
        - Technical setup (20 pts): Trend, momentum
        - Risk/reward (20 pts): Attractive R:R at current levels
        - Catalyst strength (10 pts): Is there a clear catalyst?
        """

        # Get instrument config
        config = self.instrument_map[instrument]

        # Analyses
        position = self.calculate_percentile_position(data)
        levels = self.find_key_levels(data)
        vol = self.analyze_volatility(data)
        gap = self.calculate_gap_risk(instrument, data)

        # Special: War premium for crude
        if instrument == 'CRUDE':
            war = self.analyze_war_premium_crude(data)
        else:
            war = None

        # SCORING
        scores = {}

        # 1. Historical Position (30 pts)
        percentile = position['percentile']
        if direction == 'LONG':
            # Want to be low (near support)
            if percentile < 20:
                scores['position'] = 30  # Excellent
            elif percentile < 40:
                scores['position'] = 20  # Good
            elif percentile < 60:
                scores['position'] = 10  # Neutral
            else:
                scores['position'] = 0  # Poor (too extended)
        else:  # SHORT
            # Want to be high (near resistance)
            if percentile > 80:
                scores['position'] = 30
            elif percentile > 60:
                scores['position'] = 20
            elif percentile > 40:
                scores['position'] = 10
            else:
                scores['position'] = 0

        # 2. Volatility Regime (20 pts)
        # High vol = more opportunity (if you can handle it)
        vol_percentile = vol['percentile']
        if vol_percentile > 80:
            scores['volatility'] = 20  # High vol = big moves possible
        elif vol_percentile > 60:
            scores['volatility'] = 15
        elif vol_percentile > 40:
            scores['volatility'] = 10
        else:
            scores['volatility'] = 5  # Low vol = small moves

        # 3. Technical Setup (20 pts)
        # Trend alignment
        sma_50 = data['Close'].rolling(50).mean().iloc[-1]
        current = position['current']

        if direction == 'LONG':
            if current > sma_50:
                scores['technical'] = 15  # With trend
            else:
                scores['technical'] = 5  # Against trend
        else:
            if current < sma_50:
                scores['technical'] = 15
            else:
                scores['technical'] = 5

        # Add momentum component
        roc_20 = (current - data['Close'].iloc[-20]) / data['Close'].iloc[-20] * 100
        if direction == 'LONG' and roc_20 > 0:
            scores['technical'] += 5  # Positive momentum for long
        elif direction == 'SHORT' and roc_20 < 0:
            scores['technical'] += 5  # Negative momentum for short

        # 4. Risk/Reward (20 pts)
        if direction == 'LONG':
            entry = current
            stop = levels['nearest_support'] * 0.98  # Just below support
            target = levels['nearest_resistance']
        else:
            entry = current
            stop = levels['nearest_resistance'] * 1.02  # Just above resistance
            target = levels['nearest_support']

        risk = abs(entry - stop) / entry * 100
        reward = abs(target - entry) / entry * 100
        rr_ratio = reward / risk if risk > 0 else 0

        if rr_ratio >= 2.0:
            scores['risk_reward'] = 20
        elif rr_ratio >= 1.5:
            scores['risk_reward'] = 15
        elif rr_ratio >= 1.0:
            scores['risk_reward'] = 10
        else:
            scores['risk_reward'] = 0

        # 5. Catalyst Strength (10 pts)
        if catalyst:
            scores['catalyst'] = 10  # User provided catalyst
        else:
            scores['catalyst'] = 5  # No specific catalyst

        # TOTAL SCORE
        total_score = sum(scores.values())

        # RECOMMENDATION
        if total_score >= 75:
            recommendation = f"{direction} - HIGH CONVICTION"
        elif total_score >= 60:
            recommendation = f"{direction} - MODERATE"
        elif total_score >= 45:
            recommendation = f"{direction} - LOW CONVICTION"
        else:
            recommendation = "WAIT - Unfavorable"

        # RETURNS PROJECTION
        # Best case: Hit target
        # Avg case: Hit midpoint
        # Worst case: Hit stop

        best_return = reward
        avg_return = reward * 0.6  # Assume partial profit
        worst_return = -risk

        # Probability profitable based on score
        prob_profitable = min(90, total_score * 0.8)  # Max 90%

        # POSITION SIZING
        # Higher score = more allocation (but capped at 40%)
        if total_score >= 75:
            allocation = 40
        elif total_score >= 60:
            allocation = 30
        elif total_score >= 45:
            allocation = 20
        else:
            allocation = 10

        # GAP RISK adjustment
        # If high gap risk (indices), reduce allocation
        if gap['gap_risk_score'] > 70:
            allocation = allocation * 0.75  # Reduce by 25%

        # Build reasoning
        reasoning_parts = []
        reasoning_parts.append(f"Position: {percentile:.0f}th percentile (52-week)")
        reasoning_parts.append(f"Volatility: {vol['regime']} ({vol['percentile']:.0f}th percentile)")
        reasoning_parts.append(f"R:R: {rr_ratio:.2f}:1")

        if war:
            reasoning_parts.append(f"War Premium: {war['war_phase']}")
            reasoning_parts.append(f"Z-score: {war['z_score']:.2f}σ")

        reasoning = " | ".join(reasoning_parts)

        return FavorabilityScore(
            instrument=instrument,
            direction=direction,
            favorability_score=int(total_score),
            recommendation=recommendation,
            current_price=current,
            global_instrument=config['global'],
            mcx_equivalent=config['mcx'],
            conversion_factor=config['conversion'],
            percentile_52w=percentile,
            distance_from_support=levels['support_distance'],
            distance_from_resistance=levels['resistance_distance'],
            current_volatility=vol['current'],
            avg_volatility=vol['average'],
            volatility_regime=vol['regime'],
            best_case_return=best_return,
            avg_case_return=avg_return,
            worst_case_return=worst_return,
            probability_profitable=prob_profitable,
            gap_risk_score=gap['gap_risk_score'],
            position_size_recommended=allocation,
            max_risk_pct=risk,
            score_breakdown=scores,
            reasoning=reasoning
        )

    def scan_all_opportunities(self) -> List[FavorabilityScore]:
        """Scan all opportunities and rank by favorability"""

        opportunities = [
            ('CRUDE', 'SHORT', 'War ending by June'),
            ('CRUDE', 'LONG', 'Supply disruption continues'),
            ('GOLD', 'LONG', 'Safe haven demand'),
            ('SILVER', 'LONG', 'Industrial + safe haven'),
            ('NIFTY', 'LONG', '50k bottom holding'),
            ('BANKNIFTY', 'LONG', '50k bottom + RBI cuts'),
        ]

        results = []

        print("\n" + "="*100)
        print("MACRO OPPORTUNITY FAVORABILITY SCANNER")
        print("="*100)
        print(f"Scan Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Capital: ₹{self.capital:,.0f}")
        print("\nScanning opportunities...\n")

        for instrument, direction, catalyst in opportunities:
            print(f"📊 Analyzing {instrument} {direction}...")

            try:
                config = self.instrument_map[instrument]
                data = self.fetch_data(config['global'], years=3)

                if len(data) < 100:
                    print(f"   ❌ Insufficient data\n")
                    continue

                score = self.calculate_favorability_score(
                    instrument=instrument,
                    direction=direction,
                    data=data,
                    catalyst=catalyst
                )

                results.append(score)

                # Display
                print(f"   Score: {score.favorability_score}/100")
                print(f"   Recommendation: {score.recommendation}")
                print(f"   {score.reasoning}")
                print()

            except Exception as e:
                print(f"   ❌ Error: {str(e)}\n")

        # Sort by score
        results.sort(key=lambda x: x.favorability_score, reverse=True)

        return results

    def display_detailed_report(self, results: List[FavorabilityScore]):
        """Display full report with rankings"""

        print("\n" + "="*100)
        print("FAVORABILITY RANKINGS")
        print("="*100)

        for i, score in enumerate(results, 1):
            print(f"\n{i}. {score.instrument} {score.direction} - Score: {score.favorability_score}/100")
            print(f"   {'='*90}")

            # Current state
            print(f"   Current Price: ${score.current_price:.2f} ({score.global_instrument})")
            print(f"   MCX Equivalent: {score.mcx_equivalent}")
            print(f"   Position: {score.percentile_52w:.0f}th percentile (52-week)")
            print(f"   Volatility: {score.volatility_regime} ({score.current_volatility:.1f}% vs {score.avg_volatility:.1f}% avg)")

            # Distance from levels
            print(f"\n   Support: {score.distance_from_support:.1f}% below")
            print(f"   Resistance: {score.distance_from_resistance:.1f}% above")

            # Returns projection
            print(f"\n   Returns Projection:")
            print(f"      Best Case:  {score.best_case_return:+.1f}%")
            print(f"      Avg Case:   {score.avg_case_return:+.1f}%")
            print(f"      Worst Case: {score.worst_case_return:+.1f}%")
            print(f"      Probability Profitable: {score.probability_profitable:.0f}%")

            # Risk
            print(f"\n   Risk Assessment:")
            print(f"      Max Risk: {score.max_risk_pct:.1f}%")
            print(f"      Gap Risk: {score.gap_risk_score}/100")
            print(f"      Recommended Allocation: {score.position_size_recommended:.0f}% of capital")

            # Score breakdown
            print(f"\n   Score Breakdown:")
            for component, points in score.score_breakdown.items():
                print(f"      {component.replace('_', ' ').title()}: {points}")

            # Recommendation
            print(f"\n   💡 {score.recommendation}")

        # Summary
        print("\n" + "="*100)
        print("RECOMMENDED ACTIONS")
        print("="*100)

        high_conv = [s for s in results if s.favorability_score >= 75]
        moderate = [s for s in results if 60 <= s.favorability_score < 75]

        if high_conv:
            print("\n✅ HIGH CONVICTION (Score 75+):")
            for s in high_conv:
                capital_allocation = self.capital * (s.position_size_recommended / 100)
                print(f"   • {s.instrument} {s.direction}: Allocate ₹{capital_allocation:,.0f} ({s.position_size_recommended:.0f}%)")
                print(f"     Expected: {s.avg_case_return:+.1f}% avg, {s.best_case_return:+.1f}% best")

        if moderate:
            print("\n⚠️  MODERATE CONVICTION (Score 60-74):")
            for s in moderate:
                capital_allocation = self.capital * (s.position_size_recommended / 100)
                print(f"   • {s.instrument} {s.direction}: Allocate ₹{capital_allocation:,.0f} ({s.position_size_recommended:.0f}%)")

        wait = [s for s in results if s.favorability_score < 60]
        if wait:
            print("\n⏸️  WAIT (Score <60):")
            for s in wait:
                print(f"   • {s.instrument} {s.direction}: Not favorable at current levels")

        print("\n" + "="*100)


def analyze_crude_war_premium():
    """Special deep-dive on crude oil war premium"""

    print("\n" + "="*100)
    print("CRUDE OIL WAR PREMIUM ANALYSIS")
    print("="*100)

    scanner = FavorabilityScanner()
    data = scanner.fetch_data('CL=F', years=5)

    war = scanner.analyze_war_premium_crude(data)

    print(f"\n📊 Current Market:")
    print(f"   Price: ${war['current_price']:.2f}")
    print(f"   Long-term Mean: ${war['mean_price']:.2f}")
    print(f"   Standard Deviation: ${war['std_price']:.2f}")

    print(f"\n🎯 War Premium Assessment:")
    print(f"   Z-Score: {war['z_score']:.2f}σ")
    print(f"   Phase: {war['war_phase']}")

    print(f"\n📈 Historical War Spikes (>2σ):")
    print(f"   Total Events: {war['historical_2sigma_events']}")
    print(f"   Extreme Events (>3σ): {war['historical_3sigma_events']}")
    print(f"   Probability of 3σ: {war['probability_3sigma']:.1f}%")
    print(f"   Avg Spike Duration: {war['avg_spike_duration_days']:.0f} days")
    print(f"   Max Spike Duration: {war['max_spike_duration_days']:.0f} days")

    print(f"\n📉 Mean Reversion:")
    print(f"   Reversion Rate (60 days): {war['reversion_rate_60days']:.0f}%")
    print(f"   Downside to Mean: {war['downside_to_mean']:.1f}%")

    print(f"\n🚀 Upside Potential:")
    print(f"   To 3σ Level: {war['upside_to_3sigma']:.1f}%")

    print(f"\n💡 INTERPRETATION:")
    if war['z_score'] > 2.5:
        print("   ⚠️  EXTREME spike - very close to historical max")
        print("   → Mean reversion likely within 60 days")
        print("   → SHORT opportunity if war de-escalates")
    elif war['z_score'] > 2.0:
        print("   🔶 HIGH spike - but room to 3σ")
        print(f"   → Can spike another {war['upside_to_3sigma']:.0f}% if war escalates")
        print("   → WAIT for clearer direction")
    elif war['z_score'] > 1.0:
        print("   📈 ELEVATED - moderate war premium")
        print("   → Still room to spike if war worsens")
        print("   → Or fall if war ends")
    else:
        print("   ✅ NORMAL - no war premium priced in")
        print("   → LONG opportunity if war risk emerges")

    print("\n" + "="*100)


if __name__ == "__main__":
    # Run full scan
    scanner = FavorabilityScanner(capital=1200000)
    results = scanner.scan_all_opportunities()
    scanner.display_detailed_report(results)

    # Special crude analysis
    analyze_crude_war_premium()
