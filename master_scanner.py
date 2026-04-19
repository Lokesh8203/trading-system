"""
MASTER TRADING DASHBOARD

Single command to see ALL opportunities across:
1. Futures macro trades (medium-term)
2. Futures intraday (Grade A signals)
3. Stocks swing trades (conservative)
4. Pair trades (risk reduction)

Quality Thresholds (v2.1):
- MACRO: ≥70 (GRADE A), 50-69 (GRADE B - shown with warning if no Grade A)
- PAIRS: ≥60 (GRADE A), 40-59 (GRADE B - shown with warning if no Grade A)
- INTRADAY: Grade A only (strict filtering already applied)
- STOCKS: Conservative only (strict filtering already applied)

Philosophy: Quality > Quantity. If no Grade A trades, system shows warning.

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
Version: 2.1 (Quality-first)
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

import warnings
warnings.filterwarnings('ignore', category=FutureWarning)
warnings.filterwarnings('ignore', message='.*urllib3.*')

import pandas as pd
import numpy as np
from datetime import datetime
from typing import List, Dict, Optional
from dataclasses import dataclass, field

# Import MCX timing schedule and fundamental filter
from futures.macro.mcx_trading_timing_guide import MCXTradingSchedule
from futures.macro.fundamental_filter import FundamentalFilter


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

    # Quality (with default - must come after non-defaults)
    quality_grade: str = "A"  # A (primary) or B (fallback)

    # Optional fields with defaults
    target_2: Optional[float] = None
    disruption_factors: List[str] = field(default_factory=list)
    gap_risk: int = 0  # 0-100
    reasoning: str = ""
    confidence: int = 0  # For intraday signals

    # MCX timing
    can_trade_now: bool = True
    trading_status: str = ""
    optimal_window: str = ""
    wait_until: Optional[str] = None


class MasterScanner:
    """Aggregate all trading opportunities"""

    def __init__(self, capital: float = 1200000):
        self.capital = capital
        self.opportunities = []
        self.mcx_schedule = MCXTradingSchedule()
        self.fundamental_filter = FundamentalFilter()

    def scan_macro_futures(self):
        """Scan macro opportunities"""
        print("📊 Scanning macro futures...")

        try:
            from futures.macro.favorability_scanner import FavorabilityScanner

            scanner = FavorabilityScanner(capital=self.capital)
            results = scanner.scan_all_opportunities()

            for result in results:
                if result.favorability_score >= 50:  # Include 50+ for now, will grade later
                    # Determine quality grade
                    grade = "A" if result.favorability_score >= 70 else "B"

                    self.opportunities.append(UnifiedOpportunity(
                        rank=0,  # Will assign later
                        name=f"{result.instrument} {result.direction}",
                        category="MACRO",
                        instrument=result.instrument,
                        direction=result.direction,
                        favorability_score=result.favorability_score,
                        quality_grade=grade,
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
                if signal:  # Grade A signal found (already filtered)
                    self.opportunities.append(UnifiedOpportunity(
                        rank=0,
                        name=f"{name} {signal.signal_type} (Intraday)",
                        category="INTRADAY",
                        instrument=name,
                        direction=signal.signal_type,
                        favorability_score=signal.confidence,
                        quality_grade="A",  # Intraday is always Grade A
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

    def scan_intraday_stocks(self):
        """Scan stock intraday Grade A signals"""
        print("📊 Scanning stock intraday...")

        try:
            from stocks.scanners.intraday_scanner import StockIntradayScanner

            scanner = StockIntradayScanner()
            results = scanner.scan_all()

            for name, signal in results.items():
                if signal:  # Grade A signal found
                    self.opportunities.append(UnifiedOpportunity(
                        rank=0,
                        name=f"{name} {signal.signal_type} (Stock Intraday)",
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
                        entry_timing="NOW (5-min candle close)",
                        quality_grade="A",  # Stock intraday is always Grade A
                        disruption_factors=["Intraday volatility", "News events"],
                        gap_risk=0,  # Intraday, no overnight hold
                        reasoning=signal.reasoning,
                        confidence=signal.confidence
                    ))

            print(f"   Found {len([o for o in self.opportunities if o.category == 'INTRADAY' and 'Stock' in o.name])} stock intraday signals")

        except Exception as e:
            print(f"   ❌ Error scanning stock intraday: {str(e)}")

    def scan_stocks(self):
        """Scan stock swing opportunities"""
        print("📊 Scanning stock swings...")

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
                        quality_grade="A",  # Stocks are always Grade A (strict filters)
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
        """Scan ALL pair trading opportunities with fundamental filter"""
        print("📊 Scanning all MCX pair trades...")

        try:
            from futures.macro.all_mcx_pairs_analyzer import AllMCXPairsAnalyzer

            analyzer = AllMCXPairsAnalyzer()
            results = analyzer.scan_all_pairs()

            for pair in results:
                # Apply fundamental filter
                filter_result = self.fundamental_filter.filter_opportunity(
                    pair_name=pair.name,
                    original_score=pair.score,
                    original_allocation=15,  # Default pair allocation
                    expected_return=pair.expected_return
                )

                # Only show if fundamentals support it (keep 40+ for now, will grade later)
                if filter_result['should_show'] and filter_result['adjusted_score'] >= 40:
                    # Add warning to disruption factors if fundamentals weak
                    disruption_list = [pair.reasoning]
                    if filter_result['warning']:
                        disruption_list.insert(0, filter_result['warning'])

                    # Determine quality grade
                    grade = "A" if filter_result['adjusted_score'] >= 60 else "B"

                    self.opportunities.append(UnifiedOpportunity(
                        rank=0,
                        name=f"{pair.name} ({pair.direction})",
                        category="PAIR",
                        instrument=pair.name,
                        direction=pair.direction,
                        favorability_score=filter_result['adjusted_score'],  # Use adjusted score
                        quality_grade=grade,
                        entry_price=pair.entry,
                        stop_loss=pair.stop,
                        target_1=pair.target,
                        risk_pct=abs(pair.entry - pair.stop) / pair.entry * 100 if pair.entry > 0 else 0,
                        rr_ratio=abs(pair.target - pair.entry) / abs(pair.entry - pair.stop) if abs(pair.entry - pair.stop) > 0 else 0,
                        recommended_allocation_pct=filter_result['adjusted_allocation'],  # Use filtered allocation
                        expected_return=filter_result['adjusted_return'],  # Use adjusted return
                        best_case=pair.expected_return * 1.5,
                        worst_case=-abs(pair.stop - pair.entry) / pair.entry * 100 if pair.entry > 0 else 0,
                        time_horizon="WEEKS-MONTHS",
                        entry_timing="NOW",
                        disruption_factors=disruption_list,
                        gap_risk=30,  # Lower for pairs (market neutral)
                        reasoning=f"{pair.trade_description} | Z-score: {pair.z_score:.2f}σ | Reversion prob: {pair.probability:.0f}%"
                    ))

            print(f"   Found {len([o for o in self.opportunities if o.category == 'PAIR'])} pair opportunities (50+ score)")

        except Exception as e:
            print(f"   ❌ Error scanning pairs: {str(e)}")

    def check_mcx_timing(self):
        """Check MCX timing for all opportunities"""
        mcx_instruments = ['GOLD', 'SILVER', 'CRUDE', 'COPPER', 'NATGAS']

        for opp in self.opportunities:
            # Check if MCX instrument
            is_mcx = any(instr in opp.instrument.upper() for instr in mcx_instruments)

            if is_mcx:
                # Get instrument name (e.g., GOLD from GOLD LONG)
                instrument = None
                for instr in mcx_instruments:
                    if instr in opp.instrument.upper():
                        instrument = instr
                        break

                if instrument:
                    status = self.mcx_schedule.can_trade_now(instrument)
                    opp.can_trade_now = status['can_trade']
                    opp.trading_status = status.get('reason', 'Market open') if not status['can_trade'] else 'CAN TRADE'

                    if status['can_trade']:
                        opp.optimal_window = status.get('window', 'Open')
                        opp.wait_until = None
                    else:
                        opp.optimal_window = "N/A"
                        if 'wait_until' in status:
                            opp.wait_until = status['wait_until'].strftime('%I:%M %p')
                        elif 'next_open' in status:
                            opp.wait_until = status['next_open'].strftime('%I:%M %p')
                        else:
                            opp.wait_until = "Tomorrow"
            else:
                # Not MCX, always tradeable (stocks/indices via GTT)
                opp.can_trade_now = True
                opp.trading_status = "GTT/Market Order"
                opp.optimal_window = "N/A"
                opp.wait_until = None

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
        """Display master dashboard with quality tiering"""

        # Count by quality grade
        grade_a = [o for o in self.opportunities if o.quality_grade == "A"]
        grade_b = [o for o in self.opportunities if o.quality_grade == "B"]

        print("\n" + "="*120)
        print("MASTER TRADING DASHBOARD - TOP OPPORTUNITIES")
        print("="*120)
        print(f"Scan Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Capital: ₹{self.capital:,.0f}")
        print(f"Total Opportunities: {len(self.opportunities)}")
        print(f"  ✅ GRADE A (Primary): {len(grade_a)} trades")
        print(f"  ⚠️  GRADE B (Fallback): {len(grade_b)} trades")
        print()

        # Quality warning if no Grade A
        if len(grade_a) == 0:
            print("="*120)
            print("⚠️  WARNING: NO GRADE A TRADES FOUND")
            print("="*120)
            print("Market conditions not ideal. Consider:")
            print("  1. Wait for better setup (recommended)")
            print("  2. Trade Grade B signals with caution (reduced size)")
            print("  3. Focus on cash preservation")
            print()

        # Determine what to show
        if len(grade_a) >= 10:
            # Plenty of Grade A, show only those
            to_display = grade_a[:15]
            print("📊 Showing: GRADE A trades only (sufficient quality available)")
        elif len(grade_a) > 0:
            # Some Grade A, fill rest with Grade B
            to_display = grade_a + grade_b[:max(0, 15 - len(grade_a))]
            print(f"📊 Showing: {len(grade_a)} GRADE A + {min(len(grade_b), 15-len(grade_a))} GRADE B trades")
        else:
            # No Grade A, show top Grade B with warning
            to_display = grade_b[:15]
            print("📊 Showing: GRADE B trades only (NO GRADE A AVAILABLE - CAUTION!)")

        print()

        for opp in to_display:
            # Quality indicator
            quality_indicator = "✅ GRADE A" if opp.quality_grade == "A" else "⚠️  GRADE B - CAUTION"

            print(f"\n{'='*120}")
            print(f"#{opp.rank}. {opp.name} - Score: {opp.favorability_score}/100 [{opp.category}] {quality_indicator}")
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

            # MCX timing status
            if opp.can_trade_now:
                print(f"\n✅ TRADING STATUS: {opp.trading_status}")
                if opp.optimal_window and opp.optimal_window != "N/A":
                    print(f"   Current Window: {opp.optimal_window}")
            else:
                print(f"\n❌ TRADING STATUS: {opp.trading_status}")
                if opp.wait_until:
                    print(f"   Wait Until: {opp.wait_until}")
                print(f"   ⚠️  AVOID first 15 min (9:00-9:15) and last 15 min (11:15-11:30)")

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
    scanner.scan_intraday_stocks()  # NEW: Stock intraday Grade A signals
    scanner.scan_stocks()
    scanner.scan_pair_trades()

    # Check MCX timing
    scanner.check_mcx_timing()

    # Rank and display
    scanner.rank_opportunities()
    scanner.display_dashboard()

    # Display next scanner run time
    next_scan = scanner.mcx_schedule.next_scanner_run()
    print("\n" + "="*120)
    print("📊 NEXT SCANNER RUN:")
    print(f"   Time: {next_scan['time'].strftime('%I:%M %p IST')}")
    print(f"   Session: {next_scan['session']}")
    print(f"   Action: {next_scan['action']}")

    print("\n" + "="*120)
    print("Scan complete! Run this anytime to see updated opportunities.")
    print("Optimal MCX windows: 9:30-11:30 AM | 2:00-4:00 PM (HIGH) | 7:00-10:00 PM (HIGHEST)")
    print("="*120)
    print()


if __name__ == "__main__":
    main()
