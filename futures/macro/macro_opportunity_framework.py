"""
MACRO OPPORTUNITY FRAMEWORK

For high-conviction, medium-term futures plays based on macro events.

Use cases:
1. War ending → Crude oil down 10%+
2. Index bottoms → Nifty/Bank Nifty up 15%+
3. Fed pivot → Dollar down, Gold up
4. Recession fears → Safe haven plays

NOT for:
- Daily trading (use intraday scanners for that)
- Low conviction trades
- "Hoping" plays without analysis

Framework:
1. Thesis validation (with historical data)
2. Scenario analysis (bull/base/bear cases)
3. Position sizing (20-40% max, NOT all-in)
4. Stop loss levels (even on conviction trades)
5. Pyramid entry (scale in over time)
6. Exit strategy (take profits in stages)

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


@dataclass
class MacroOpportunity:
    """High-conviction macro trade"""
    name: str
    thesis: str
    instrument: str
    direction: str  # LONG/SHORT

    # Price levels
    current_price: float
    entry_zone_low: float
    entry_zone_high: float
    stop_loss: float
    target_1: float
    target_2: float
    target_3: float

    # Risk/Reward
    max_risk_pct: float
    expected_return_pct: float

    # Probability analysis
    historical_probability: float
    scenarios: Dict[str, float]  # bull/base/bear outcomes

    # Position sizing
    recommended_allocation_pct: float
    max_leverage: float

    # Timeframe
    expected_duration_days: int
    catalyst_date: Optional[str]

    # Supporting data
    supporting_factors: List[str]
    risk_factors: List[str]


class MacroAnalyzer:
    """Analyze macro opportunities with historical data"""

    def __init__(self, capital: float = 1200000):
        """
        Initialize with your capital

        Args:
            capital: Total capital in INR (default ₹12L)
        """
        self.capital = capital

    def fetch_historical_data(self, ticker: str, years: int = 5) -> pd.DataFrame:
        """Fetch historical data for analysis"""
        end = datetime.now()
        start = end - timedelta(days=years*365)
        data = yf.download(ticker, start=start, end=end, progress=False)

        # Flatten MultiIndex if present
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.get_level_values(0)

        return data

    def analyze_support_resistance(self, data: pd.DataFrame, lookback: int = 252) -> Dict:
        """
        Find key support/resistance levels

        Returns recent highs/lows that acted as S/R
        """
        recent = data.tail(lookback)

        # Find swing highs and lows
        highs = []
        lows = []

        for i in range(10, len(recent)-10):
            window_before = recent['High'].iloc[i-10:i]
            window_after = recent['High'].iloc[i+1:i+11]

            if recent['High'].iloc[i] > window_before.max() and recent['High'].iloc[i] > window_after.max():
                highs.append(recent['High'].iloc[i])

            window_before_low = recent['Low'].iloc[i-10:i]
            window_after_low = recent['Low'].iloc[i+1:i+11]

            if recent['Low'].iloc[i] < window_before_low.min() and recent['Low'].iloc[i] < window_after_low.min():
                lows.append(recent['Low'].iloc[i])

        current_price = data['Close'].iloc[-1]

        # Find nearest support/resistance
        supports = [l for l in lows if l < current_price]
        resistances = [h for h in highs if h > current_price]

        return {
            'current_price': current_price,
            'nearest_support': max(supports) if supports else None,
            'strong_support': sorted(supports, reverse=True)[:3] if supports else [],
            'nearest_resistance': min(resistances) if resistances else None,
            'strong_resistance': sorted(resistances)[:3] if resistances else [],
            'all_supports': sorted(supports, reverse=True),
            'all_resistances': sorted(resistances)
        }

    def analyze_volatility_regime(self, data: pd.DataFrame, window: int = 20) -> Dict:
        """
        Analyze current volatility vs historical

        High volatility = bigger moves possible (both ways)
        """
        data = data.copy()
        data['Returns'] = data['Close'].pct_change()
        data['Volatility'] = data['Returns'].rolling(window).std() * np.sqrt(252) * 100

        current_vol = data['Volatility'].iloc[-1]
        avg_vol = data['Volatility'].mean()
        percentile = (data['Volatility'] < current_vol).sum() / len(data['Volatility']) * 100

        return {
            'current_volatility': current_vol,
            'average_volatility': avg_vol,
            'percentile': percentile,
            'regime': 'HIGH' if percentile > 75 else 'NORMAL' if percentile > 25 else 'LOW'
        }

    def backtest_drawdown_recovery(self, data: pd.DataFrame) -> Dict:
        """
        Analyze historical drawdowns and recovery times

        Key question: After X% drawdown, how often did it recover? How long?
        """
        data = data.copy()
        data['Cummax'] = data['Close'].cummax()
        data['Drawdown'] = (data['Close'] - data['Cummax']) / data['Cummax'] * 100

        # Find all drawdowns > 5%
        drawdowns = []
        in_drawdown = False
        dd_start = None
        dd_max = 0

        for i in range(len(data)):
            dd = data['Drawdown'].iloc[i]

            if dd < -5 and not in_drawdown:
                in_drawdown = True
                dd_start = i
                dd_max = dd

            if in_drawdown:
                dd_max = min(dd_max, dd)

                # Recovery: back above -1%
                if dd > -1:
                    recovery_days = i - dd_start
                    drawdowns.append({
                        'start_idx': dd_start,
                        'max_drawdown': dd_max,
                        'recovery_days': recovery_days,
                        'recovered': True
                    })
                    in_drawdown = False

        if in_drawdown:
            # Still in drawdown
            drawdowns.append({
                'start_idx': dd_start,
                'max_drawdown': dd_max,
                'recovery_days': len(data) - dd_start,
                'recovered': False
            })

        # Statistics
        recovered = [d for d in drawdowns if d['recovered']]

        if len(recovered) > 0:
            avg_recovery = np.mean([d['recovery_days'] for d in recovered])
            median_recovery = np.median([d['recovery_days'] for d in recovered])
        else:
            avg_recovery = None
            median_recovery = None

        return {
            'total_drawdowns': len(drawdowns),
            'recovered_count': len(recovered),
            'recovery_rate': len(recovered) / len(drawdowns) * 100 if drawdowns else 0,
            'average_recovery_days': avg_recovery,
            'median_recovery_days': median_recovery,
            'max_drawdown_ever': data['Drawdown'].min(),
            'current_drawdown': data['Drawdown'].iloc[-1],
            'all_drawdowns': drawdowns
        }

    def calculate_position_sizing(self,
                                   entry_price: float,
                                   stop_loss: float,
                                   allocation_pct: float,
                                   leverage: float,
                                   lot_size: int,
                                   tick_value: float) -> Dict:
        """
        Calculate position size for macro trade

        Args:
            entry_price: Entry price
            stop_loss: Stop loss price
            allocation_pct: % of capital to allocate (20-40%)
            leverage: Effective leverage (2-5x)
            lot_size: Contract lot size
            tick_value: Rupee value per tick

        Returns position sizing details
        """
        # Capital to deploy
        allocated_capital = self.capital * (allocation_pct / 100)
        leveraged_capital = allocated_capital * leverage

        # Risk per contract
        risk_per_point = abs(entry_price - stop_loss)
        risk_per_lot = risk_per_point * lot_size * tick_value

        # Max lots based on capital
        max_lots = int(leveraged_capital / (entry_price * lot_size * tick_value))

        # Risk-adjusted lots (max 50% loss on stop)
        risk_adjusted_lots = int(allocated_capital * 0.5 / risk_per_lot)

        # Recommended: smaller of the two
        recommended_lots = min(max_lots, risk_adjusted_lots)

        # Final metrics
        total_value = entry_price * recommended_lots * lot_size * tick_value
        total_risk = risk_per_lot * recommended_lots
        total_margin = total_value / leverage

        return {
            'allocated_capital': allocated_capital,
            'leveraged_exposure': leveraged_capital,
            'recommended_lots': recommended_lots,
            'max_lots_possible': max_lots,
            'risk_adjusted_lots': risk_adjusted_lots,
            'total_position_value': total_value,
            'total_risk_amount': total_risk,
            'margin_required': total_margin,
            'risk_pct_of_capital': (total_risk / self.capital) * 100,
            'exposure_pct_of_capital': (total_value / self.capital) * 100
        }

    def scenario_analysis(self,
                         entry_price: float,
                         targets: List[float],
                         stop_loss: float,
                         lots: int,
                         lot_size: int,
                         tick_value: float,
                         probabilities: List[float]) -> Dict:
        """
        Calculate expected value across scenarios

        Args:
            entry_price: Entry price
            targets: [target1, target2, target3]
            stop_loss: Stop loss
            lots: Number of lots
            lot_size: Contract lot size
            tick_value: Rupee per tick
            probabilities: [p_target1, p_target2, p_target3, p_stop]

        Returns expected value analysis
        """
        # Normalize probabilities
        prob_sum = sum(probabilities)
        probs = [p / prob_sum for p in probabilities]

        # Calculate outcomes
        outcomes = []

        for i, target in enumerate(targets):
            pnl = (target - entry_price) * lots * lot_size * tick_value
            outcomes.append({
                'scenario': f'Target {i+1}',
                'price': target,
                'pnl': pnl,
                'return_pct': (pnl / self.capital) * 100,
                'probability': probs[i] * 100
            })

        # Stop loss outcome
        stop_pnl = (stop_loss - entry_price) * lots * lot_size * tick_value
        outcomes.append({
            'scenario': 'Stop Loss',
            'price': stop_loss,
            'pnl': stop_pnl,
            'return_pct': (stop_pnl / self.capital) * 100,
            'probability': probs[-1] * 100
        })

        # Expected value
        expected_pnl = sum(o['pnl'] * (o['probability']/100) for o in outcomes)
        expected_return = (expected_pnl / self.capital) * 100

        return {
            'outcomes': outcomes,
            'expected_pnl': expected_pnl,
            'expected_return_pct': expected_return,
            'risk_reward_ratio': abs(targets[0] - entry_price) / abs(entry_price - stop_loss)
        }


def example_crude_oil_analysis():
    """
    Example: Crude oil short thesis

    Thesis: War ends by June → Oil down 10%
    """
    print("\n" + "="*80)
    print("MACRO OPPORTUNITY ANALYSIS: CRUDE OIL SHORT")
    print("="*80)

    analyzer = MacroAnalyzer(capital=1200000)

    # Fetch data
    print("\n📊 Fetching historical data...")
    data = analyzer.fetch_historical_data('CL=F', years=5)

    # Current market
    current_price = data['Close'].iloc[-1]
    print(f"\n💰 Current Price: ${current_price:.2f}")

    # Support/Resistance
    print("\n🎯 Support/Resistance Analysis:")
    sr = analyzer.analyze_support_resistance(data)
    print(f"   Nearest Support: ${sr['nearest_support']:.2f}")
    print(f"   Strong Supports: {[f'${s:.2f}' for s in sr['strong_support'][:3]]}")
    print(f"   Nearest Resistance: ${sr['nearest_resistance']:.2f}")

    # Volatility
    print("\n📈 Volatility Analysis:")
    vol = analyzer.analyze_volatility_regime(data)
    print(f"   Current Vol: {vol['current_volatility']:.1f}%")
    print(f"   Average Vol: {vol['average_volatility']:.1f}%")
    print(f"   Regime: {vol['regime']} (percentile: {vol['percentile']:.0f})")

    # Drawdown recovery
    print("\n📉 Historical Drawdown Recovery:")
    dd = analyzer.backtest_drawdown_recovery(data)
    print(f"   Recovery Rate: {dd['recovery_rate']:.0f}% ({dd['recovered_count']}/{dd['total_drawdowns']} times)")
    print(f"   Avg Recovery: {dd['average_recovery_days']:.0f} days")
    print(f"   Current Drawdown: {dd['current_drawdown']:.1f}%")

    # THESIS SETUP
    print("\n" + "="*80)
    print("TRADE SETUP")
    print("="*80)

    thesis = """
    Thesis: War ends by June 2026 → Crude oil down 10%

    Supporting factors:
    - June futures trading at discount (contango)
    - Geopolitical de-escalation signs
    - US strategic reserves refilling at lower prices
    - China demand slower than expected

    Risk factors:
    - War escalates further
    - OPEC+ surprise production cuts
    - US sanctions on major producer
    - Unexpected demand spike
    """
    print(thesis)

    # Trade parameters
    entry = current_price
    stop = entry * 1.08  # 8% stop (war escalates)
    target1 = entry * 0.95  # 5% down
    target2 = entry * 0.90  # 10% down
    target3 = entry * 0.85  # 15% down

    print(f"\n📍 Price Levels:")
    print(f"   Entry: ${entry:.2f}")
    print(f"   Stop: ${stop:.2f} (+8%)")
    print(f"   Target 1: ${target1:.2f} (-5%)")
    print(f"   Target 2: ${target2:.2f} (-10%)")
    print(f"   Target 3: ${target3:.2f} (-15%)")

    # Position sizing
    print("\n💼 Position Sizing (30% allocation, 3x leverage):")
    sizing = analyzer.calculate_position_sizing(
        entry_price=entry,
        stop_loss=stop,
        allocation_pct=30,  # 30% of capital
        leverage=3,         # 3x leverage
        lot_size=1000,      # Crude oil = 1000 barrels
        tick_value=1        # $1 per barrel
    )

    print(f"   Allocated: ₹{sizing['allocated_capital']:,.0f} (30% of ₹12L)")
    print(f"   Leveraged Exposure: ₹{sizing['leveraged_exposure']:,.0f}")
    print(f"   Recommended Lots: {sizing['recommended_lots']}")
    print(f"   Total Position Value: ₹{sizing['total_position_value']:,.0f}")
    print(f"   Total Risk: ₹{sizing['total_risk_amount']:,.0f} ({sizing['risk_pct_of_capital']:.1f}% of capital)")
    print(f"   Margin Required: ₹{sizing['margin_required']:,.0f}")

    # Scenario analysis
    print("\n🎲 Scenario Analysis:")
    scenarios = analyzer.scenario_analysis(
        entry_price=entry,
        targets=[target1, target2, target3],
        stop_loss=stop,
        lots=sizing['recommended_lots'],
        lot_size=1000,
        tick_value=1,
        probabilities=[0.3, 0.4, 0.2, 0.1]  # 30% T1, 40% T2, 20% T3, 10% stop
    )

    for outcome in scenarios['outcomes']:
        print(f"\n   {outcome['scenario']}:")
        print(f"      Price: ${outcome['price']:.2f}")
        print(f"      P&L: ₹{outcome['pnl']:,.0f} ({outcome['return_pct']:+.1f}%)")
        print(f"      Probability: {outcome['probability']:.0f}%")

    print(f"\n   Expected Return: {scenarios['expected_return_pct']:+.1f}%")
    print(f"   Risk/Reward: {scenarios['risk_reward_ratio']:.2f}:1")

    print("\n" + "="*80)
    print("RECOMMENDATION")
    print("="*80)

    if scenarios['expected_return_pct'] > 5:
        print("✅ FAVORABLE - Expected value positive")
        print(f"   Position: SHORT {sizing['recommended_lots']} lots at ${entry:.2f}")
        print(f"   Risk: ₹{sizing['total_risk_amount']:,.0f} ({sizing['risk_pct_of_capital']:.1f}%)")
        print(f"   Reward: Up to ₹{scenarios['outcomes'][2]['pnl']:,.0f} (best case)")
    else:
        print("⚠️  UNFAVORABLE - Risk/reward not attractive")
        print("   Consider reducing position or waiting")

    print("\n⏰ Timeline: Hold until June 2026 or stop hit")
    print("📊 Monitor: Geopolitical news, OPEC meetings, demand data")
    print()


def example_bank_nifty_analysis():
    """
    Example: Bank Nifty long thesis

    Thesis: 50k is bottom, current 56k, target 65k
    """
    print("\n" + "="*80)
    print("MACRO OPPORTUNITY ANALYSIS: BANK NIFTY LONG")
    print("="*80)

    analyzer = MacroAnalyzer(capital=1200000)

    # Fetch data
    print("\n📊 Fetching historical data...")
    data = analyzer.fetch_historical_data('^NSEBANK', years=3)

    # Current market
    current_price = data['Close'].iloc[-1]
    print(f"\n💰 Current Price: ₹{current_price:.2f}")

    # Support/Resistance
    print("\n🎯 Support/Resistance Analysis:")
    sr = analyzer.analyze_support_resistance(data)
    print(f"   Nearest Support: ₹{sr['nearest_support']:.2f}")
    print(f"   Strong Supports: {[f'₹{s:.2f}' for s in sr['strong_support'][:3]]}")
    print(f"   Nearest Resistance: ₹{sr['nearest_resistance']:.2f}")

    # Check if 50k is in support list
    supports_near_50k = [s for s in sr['all_supports'] if 48000 < s < 52000]
    if supports_near_50k:
        print(f"   ✅ 50k zone tested: {[f'₹{s:.0f}' for s in supports_near_50k]}")
    else:
        print(f"   ⚠️  50k NOT tested in recent history")

    # Drawdown recovery
    print("\n📉 Historical Drawdown Recovery:")
    dd = analyzer.backtest_drawdown_recovery(data)
    print(f"   Recovery Rate: {dd['recovery_rate']:.0f}% ({dd['recovered_count']}/{dd['total_drawdowns']} times)")
    print(f"   Avg Recovery: {dd['average_recovery_days']:.0f} days")
    print(f"   Current Position: {dd['current_drawdown']:.1f}% from ATH")

    # THESIS
    print("\n" + "="*80)
    print("TRADE SETUP")
    print("="*80)

    thesis = """
    Thesis: Bank Nifty bottomed at 50k, target 65k (15% up)

    Supporting factors:
    - RBI rate cut cycle starting
    - Credit growth improving
    - NPA cycle bottoming
    - FII flows returning

    Risk factors:
    - Global recession fears
    - Regulatory tightening
    - Fresh NPA concerns
    - Break below 50k = invalidates thesis
    """
    print(thesis)

    # Trade parameters
    entry = current_price
    stop = 49500  # Below 50k = thesis wrong
    target1 = 60000  # 6% up
    target2 = 63000  # 12% up
    target3 = 66000  # 17% up

    print(f"\n📍 Price Levels:")
    print(f"   Entry: ₹{entry:.2f}")
    print(f"   Stop: ₹{stop:.2f} ({(stop/entry-1)*100:+.1f}%)")
    print(f"   Target 1: ₹{target1:.2f} ({(target1/entry-1)*100:+.1f}%)")
    print(f"   Target 2: ₹{target2:.2f} ({(target2/entry-1)*100:+.1f}%)")
    print(f"   Target 3: ₹{target3:.2f} ({(target3/entry-1)*100:+.1f}%)")

    # Position sizing
    print("\n💼 Position Sizing (40% allocation, 4x leverage):")
    sizing = analyzer.calculate_position_sizing(
        entry_price=entry,
        stop_loss=stop,
        allocation_pct=40,  # 40% of capital
        leverage=4,         # 4x leverage
        lot_size=15,        # Bank Nifty lot = 15
        tick_value=1        # ₹1 per point
    )

    print(f"   Allocated: ₹{sizing['allocated_capital']:,.0f} (40% of ₹12L)")
    print(f"   Leveraged Exposure: ₹{sizing['leveraged_exposure']:,.0f}")
    print(f"   Recommended Lots: {sizing['recommended_lots']}")
    print(f"   Total Position Value: ₹{sizing['total_position_value']:,.0f}")
    print(f"   Total Risk: ₹{sizing['total_risk_amount']:,.0f} ({sizing['risk_pct_of_capital']:.1f}% of capital)")
    print(f"   Margin Required: ₹{sizing['margin_required']:,.0f}")

    # Scenario analysis
    print("\n🎲 Scenario Analysis:")
    scenarios = analyzer.scenario_analysis(
        entry_price=entry,
        targets=[target1, target2, target3],
        stop_loss=stop,
        lots=sizing['recommended_lots'],
        lot_size=15,
        tick_value=1,
        probabilities=[0.3, 0.4, 0.2, 0.1]
    )

    for outcome in scenarios['outcomes']:
        print(f"\n   {outcome['scenario']}:")
        print(f"      Price: ₹{outcome['price']:.2f}")
        print(f"      P&L: ₹{outcome['pnl']:,.0f} ({outcome['return_pct']:+.1f}%)")
        print(f"      Probability: {outcome['probability']:.0f}%")

    print(f"\n   Expected Return: {scenarios['expected_return_pct']:+.1f}%")
    print(f"   Risk/Reward: {scenarios['risk_reward_ratio']:.2f}:1")

    print("\n" + "="*80)
    print("RECOMMENDATION")
    print("="*80)

    if scenarios['expected_return_pct'] > 8:
        print("✅ FAVORABLE - Expected value positive")
        print(f"   Position: LONG {sizing['recommended_lots']} lots at ₹{entry:.2f}")
        print(f"   Risk: ₹{sizing['total_risk_amount']:,.0f} ({sizing['risk_pct_of_capital']:.1f}%)")
        print(f"   Reward: Up to ₹{scenarios['outcomes'][2]['pnl']:,.0f} (best case)")
        print("\n   Entry Strategy:")
        print(f"      - 1/3 position now at ₹{entry:.0f}")
        print(f"      - 1/3 if pullback to ₹{entry*0.97:.0f}")
        print(f"      - 1/3 on breakout above ₹{entry*1.03:.0f}")
    else:
        print("⚠️  UNFAVORABLE - Risk/reward not attractive")
        print("   Wait for better entry or clearer confirmation")

    print("\n⏰ Timeline: 2-3 months")
    print("📊 Monitor: RBI policy, credit data, global risk sentiment")
    print()


if __name__ == "__main__":
    # Run both examples
    example_crude_oil_analysis()
    example_bank_nifty_analysis()
