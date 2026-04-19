"""
MASTER TRADING DASHBOARD

Single command to see ALL opportunities across:
1. Futures macro trades (medium-term)
2. Futures intraday (Grade A signals)
3. Stocks swing trades (conservative)
4. Pair trades (risk reduction)

Output: Top 15 ranked opportunities with:
- Time horizon
- Entry/Stop/Target
- Risk %
- Favorability score
- Disruption factors
- Recommended allocation

Usage:
    python3 master_scanner.py

Author: Trading System
Date: 2026-04-19
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

import pandas as pd
import numpy as np
from datetime import datetime
from typing import List, Dict, Optional
from dataclasses import dataclass, field


@dataclass
class UnifiedOpportunity:
    """Unified opportunity across all strategies"""
    rank: int
    name: str
    category: str  # MACRO / INTRADAY / STOCK / PAIR
    instrument: str
    direction: str  # LONG/SHORT/SPREAD

    # Score
    favorability_score: int  # 0-100

    # Trade setup
    entry_price: float
    stop_loss: float
    target_1: float

    # Risk metrics
    risk_pct: float  # % of position
    rr_ratio: float
    recommended_allocation_pct: float  # % of total capital

    # Returns
    expected_return: float
    best_case: float
    worst_case: float

    # Timing
    time_horizon: str  # INTRADAY / DAYS / WEEKS / MONTHS
    entry_timing: str  # NOW / WAIT / SCALE

    # Optional fields with defaults
    target_2: Optional[float] = None
    disruption_factors: List[str] = field(default_factory=list)
    gap_risk: int = 0  # 0-100
    reasoning: str = ""
    confidence: int = 0  # For intraday signals


class MasterScanner:
    """Aggregate all trading opportunities"""

    def __init__(self, capital: float = 1200000):
        self.capital = capital
        self.opportunities = []

    def scan_macro_futures(self):
        """Scan macro opportunities"""
        print("📊 Scanning macro futures...")

        try:
            from futures.macro.favorability_scanner import FavorabilityScanner

            scanner = FavorabilityScanner(capital=self.capital)
            results = scanner.scan_all_opportunities()

            for result in results:
                if result.favorability_score >= 50:  # Only include 50+
                    self.opportunities.append(UnifiedOpportunity(
                        rank=0,  # Will assign later
                        name=f"{result.instrument} {result.direction}",
                        category="MACRO",
                        instrument=result.instrument,
                        direction=result.direction,
                        favorability_score=result.favorability_score,
                        entry_price=result.current_price,
                        stop_loss=result.current_price * (1 - result.max_risk_pct/100) if result.direction == 'LONG' else result.current_price * (1 + result.max_risk_pct/100),
                        target_1=result.current_price * (1 + result.avg_case_return/100) if result.direction == 'LONG' else result.current_price * (1 - result.avg_case_return/100),
                        target_2=result.current_price * (1 + result.best_case_return/100) if result.direction == 'LONG' else result.current_price * (1 - result.best_case_return/100),
                        risk_pct=result.max_risk_pct,
                        rr_ratio=(result.avg_case_return / result.max_risk_pct) if result.max_risk_pct > 0 else 0,
                        recommended_allocation_pct=result.position_size_recommended,
                        expected_return=result.avg_case_return,
                        best_case=result.best_case_return,
                        worst_case=result.worst_case_return,
                        time_horizon="WEEKS-MONTHS",
                        entry_timing="SCALE" if result.gap_risk_score > 70 else "NOW",
                        disruption_factors=["Check detailed analysis"],
                        gap_risk=result.gap_risk_score,
                        reasoning=result.reasoning
                    ))

            print(f"   Found {len([o for o in self.opportunities if o.category == 'MACRO'])} macro opportunities")

        except Exception as e:
            print(f"   ❌ Error scanning macro: {str(e)}")

    def scan_intraday_futures(self):
        """Scan intraday Grade A signals"""
        print("📊 Scanning intraday futures...")

        try:
            from futures.scanners.multi_instrument_scanner import MultiInstrumentScanner

            scanner = MultiInstrumentScanner()
            results = scanner.scan_all()

            for name, signal in results.items():
                if signal:  # Grade A signal found
                    self.opportunities.append(UnifiedOpportunity(
                        rank=0,
                        name=f"{name} {signal.signal_type} (Intraday)",
                        category="INTRADAY",
                        instrument=name,
                        direction=signal.signal_type,
                        favorability_score=signal.confidence,
                        entry_price=signal.entry_price,
                        stop_loss=signal.stop_loss,
                        target_1=signal.target,
                        risk_pct=signal.risk_pct,
                        rr_ratio=signal.rr_ratio,
                        recommended_allocation_pct=10,  # Fixed 10% for intraday
                        expected_return=signal.rr_ratio * signal.risk_pct,
                        best_case=signal.rr_ratio * signal.risk_pct * 1.5,
                        worst_case=-signal.risk_pct,
                        time_horizon="INTRADAY",
                        entry_timing="NOW (wait for candle close)",
                        disruption_factors=["Intraday volatility", "News events"],
                        gap_risk=0,  # Intraday, no overnight hold
                        reasoning=signal.reasoning,
                        confidence=signal.confidence
                    ))

            print(f"   Found {len([o for o in self.opportunities if o.category == 'INTRADAY'])} intraday signals")

        except Exception as e:
            print(f"   ❌ Error scanning intraday: {str(e)}")

    def scan_stocks(self):
        """Scan stock opportunities"""
        print("📊 Scanning stocks...")

        try:
            from stocks.scanners.conservative_scanner import ConservativeScanner

            scanner = ConservativeScanner()
            results = scanner.scan_all()

            count = 0
            for symbol, setup in results.items():
                if setup:  # Signal found
                    # Calculate metrics
                    risk = abs(setup['entry'] - setup['stop'])
                    reward = abs(setup['target_1'] - setup['entry'])
                    rr = reward / risk if risk > 0 else 0

                    self.opportunities.append(UnifiedOpportunity(
                        rank=0,
                        name=f"{symbol} LONG (Stock)",
                        category="STOCK",
                        instrument=symbol,
                        direction="LONG",
                        favorability_score=70,  # Conservative = moderate score
                        entry_price=setup['entry'],
                        stop_loss=setup['stop'],
                        target_1=setup['target_1'],
                        target_2=setup.get('target_2'),
                        risk_pct=(risk / setup['entry']) * 100,
                        rr_ratio=rr,
                        recommended_allocation_pct=5,  # 5% per stock
                        expected_return=(reward / setup['entry']) * 100 * 0.6,  # Assume 60% target hit
                        best_case=(reward / setup['entry']) * 100,
                        worst_case=-(risk / setup['entry']) * 100,
                        time_horizon="DAYS-WEEKS",
                        entry_timing="GTT (after market close)",
                        disruption_factors=["Market correction", "Sector weakness"],
                        gap_risk=50,  # Moderate for stocks
                        reasoning=setup.get('reasoning', 'Conservative swing setup')
                    ))

                    count += 1
                    if count >= 10:  # Max 10 stocks
                        break

            print(f"   Found {len([o for o in self.opportunities if o.category == 'STOCK'])} stock opportunities")

        except Exception as e:
            print(f"   ❌ Error scanning stocks: {str(e)}")

    def scan_pair_trades(self):
        """Scan pair trading opportunities"""
        print("📊 Scanning pair trades...")

        try:
            from futures.macro.pair_trade_analyzer import PairTradeAnalyzer

            analyzer = PairTradeAnalyzer()
            results = analyzer.scan_all_pairs()

            for pair in results:
                if pair.direction != "WAIT":
                    # Score based on z-score and reversion probability
                    score = min(100, int(50 + abs(pair.z_score) * 10 + pair.mean_reversion_probability / 2))

                    self.opportunities.append(UnifiedOpportunity(
                        rank=0,
                        name=f"{pair.name} ({pair.direction})",
                        category="PAIR",
                        instrument=pair.name,
                        direction=pair.direction,
                        favorability_score=score,
                        entry_price=pair.current_ratio,
                        stop_loss=pair.stop_ratio,
                        target_1=pair.target_ratio,
                        risk_pct=abs(pair.entry_ratio - pair.stop_ratio) / pair.entry_ratio * 100,
                        rr_ratio=abs(pair.target_ratio - pair.entry_ratio) / abs(pair.entry_ratio - pair.stop_ratio) if abs(pair.entry_ratio - pair.stop_ratio) > 0 else 0,
                        recommended_allocation_pct=20,  # 20% for pairs
                        expected_return=pair.expected_return,
                        best_case=pair.best_case,
                        worst_case=pair.worst_case,
                        time_horizon="WEEKS-MONTHS",
                        entry_timing="NOW",
                        disruption_factors=pair.disruption_factors,
                        gap_risk=30,  # Lower for pairs (market neutral)
                        reasoning=pair.reasoning
                    ))

            print(f"   Found {len([o for o in self.opportunities if o.category == 'PAIR'])} pair opportunities")

        except Exception as e:
            print(f"   ❌ Error scanning pairs: {str(e)}")

    def rank_opportunities(self):
        """Rank all opportunities by composite score"""

        for opp in self.opportunities:
            # Composite score = favorability * 0.6 + RR * 20 - gap_risk * 0.2
            composite = (
                opp.favorability_score * 0.6 +
                min(opp.rr_ratio * 20, 40) -  # Cap RR bonus at 40
                opp.gap_risk * 0.2
            )
            opp.rank = int(composite)

        # Sort by rank
        self.opportunities.sort(key=lambda x: x.rank, reverse=True)

        # Assign display rank
        for i, opp in enumerate(self.opportunities, 1):
            opp.rank = i

    def display_dashboard(self):
        """Display master dashboard"""

        print("\n" + "="*120)
        print("MASTER TRADING DASHBOARD - TOP OPPORTUNITIES")
        print("="*120)
        print(f"Scan Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Capital: ₹{self.capital:,.0f}")
        print(f"Total Opportunities: {len(self.opportunities)}")
        print()

        # Display top 15
        top_15 = self.opportunities[:15]

        for opp in top_15:
            print(f"\n{'='*120}")
            print(f"#{opp.rank}. {opp.name} - Score: {opp.favorability_score}/100 [{opp.category}]")
            print(f"{'='*120}")

            # Trade setup
            print(f"\n📍 TRADE SETUP:")
            print(f"   Direction: {opp.direction}")
            print(f"   Entry: ${opp.entry_price:.2f}")
            print(f"   Stop: ${opp.stop_loss:.2f}")
            print(f"   Target 1: ${opp.target_1:.2f}")
            if opp.target_2:
                print(f"   Target 2: ${opp.target_2:.2f}")

            # Risk/Reward
            print(f"\n💰 RISK/REWARD:")
            print(f"   Risk: {opp.risk_pct:.1f}%")
            print(f"   R:R Ratio: {opp.rr_ratio:.2f}:1")
            print(f"   Expected Return: {opp.expected_return:+.1f}%")
            print(f"   Best Case: {opp.best_case:+.1f}%")
            print(f"   Worst Case: {opp.worst_case:+.1f}%")

            # Position sizing
            allocation = self.capital * (opp.recommended_allocation_pct / 100)
            print(f"\n💼 POSITION SIZING:")
            print(f"   Recommended Allocation: {opp.recommended_allocation_pct:.0f}% = ₹{allocation:,.0f}")
            print(f"   Max Risk: ₹{allocation * opp.risk_pct / 100:,.0f}")

            # Timing
            print(f"\n⏰ TIMING:")
            print(f"   Time Horizon: {opp.time_horizon}")
            print(f"   Entry Timing: {opp.entry_timing}")
            print(f"   Gap Risk: {opp.gap_risk}/100")

            # Disruption factors
            if opp.disruption_factors:
                print(f"\n⚠️  DISRUPTION FACTORS:")
                for factor in opp.disruption_factors[:3]:  # Max 3
                    print(f"   • {factor}")

            # Reasoning
            if opp.reasoning:
                print(f"\n💡 REASONING:")
                print(f"   {opp.reasoning}")

        # Summary by category
        print("\n" + "="*120)
        print("SUMMARY BY CATEGORY")
        print("="*120)

        by_category = {}
        for opp in self.opportunities:
            if opp.category not in by_category:
                by_category[opp.category] = []
            by_category[opp.category].append(opp)

        for category, opps in by_category.items():
            count = len(opps)
            avg_score = sum(o.favorability_score for o in opps) / count if count > 0 else 0
            total_allocation = sum(o.recommended_allocation_pct for o in opps[:5])  # Top 5 per category

            print(f"\n{category}:")
            print(f"   Opportunities: {count}")
            print(f"   Avg Score: {avg_score:.0f}/100")
            print(f"   Total Allocation (top 5): {total_allocation:.0f}%")

        # Portfolio recommendation
        print("\n" + "="*120)
        print("RECOMMENDED PORTFOLIO")
        print("="*120)

        print("\nTop 5 Opportunities:")
        total_allocation = 0
        for i, opp in enumerate(self.opportunities[:5], 1):
            allocation = opp.recommended_allocation_pct
            total_allocation += allocation
            capital_amount = self.capital * (allocation / 100)

            print(f"\n{i}. {opp.name}")
            print(f"   Allocation: {allocation:.0f}% (₹{capital_amount:,.0f})")
            print(f"   Expected Return: {opp.expected_return:+.1f}%")
            print(f"   Time Horizon: {opp.time_horizon}")

        print(f"\nTotal Deployed: {total_allocation:.0f}%")
        print(f"Cash Reserve: {100 - total_allocation:.0f}%")

        expected_portfolio_return = sum(
            o.expected_return * o.recommended_allocation_pct / 100
            for o in self.opportunities[:5]
        )

        print(f"\nExpected Portfolio Return: {expected_portfolio_return:+.1f}%")
        print(f"Expected Profit: ₹{self.capital * expected_portfolio_return / 100:,.0f}")


def main():
    print("\n" + "="*120)
    print("MASTER SCANNER - AGGREGATING ALL OPPORTUNITIES")
    print("="*120)
    print()

    scanner = MasterScanner(capital=1200000)

    # Scan all sources
    scanner.scan_macro_futures()
    scanner.scan_intraday_futures()
    scanner.scan_stocks()
    scanner.scan_pair_trades()

    # Rank and display
    scanner.rank_opportunities()
    scanner.display_dashboard()

    print("\n" + "="*120)
    print("Scan complete! Run this anytime to see updated opportunities.")
    print("="*120)
    print()


if __name__ == "__main__":
    main()
