"""
FUNDAMENTAL FILTER FOR PAIR TRADES

Filters out pair trades where structural shifts invalidate historical means.

Based on research from COMMODITY_FUNDAMENTALS_RESEARCH_2024_2026.md

Update frequency: Monthly (structural shifts are slow-moving)
Last Updated: 2026-04-19

Author: Trading System
"""

from dataclasses import dataclass
from enum import Enum


class FundamentalStrength(Enum):
    """Fundamental support for mean reversion"""
    STRONG = "STRONG"          # No structural shift, full mean reversion expected
    MODERATE = "MODERATE"      # Partial shift, reduced mean reversion
    WEAK = "WEAK"             # Strong structural shift, minimal reversion
    AVOID = "AVOID"           # Structural shift invalidates historical mean


@dataclass
class FundamentalAssessment:
    """Fundamental analysis result"""
    pair_name: str
    strength: FundamentalStrength
    mean_valid: bool
    expected_reversion_pct: int  # 0-100, % of historical mean reversion
    allocation_multiplier: float  # 0-1, reduce allocation if structural shift
    reasoning: str
    last_updated: str


class FundamentalFilter:
    """Filter pair trades by fundamental validity"""

    def __init__(self):
        """Initialize with April 2026 fundamental research"""

        # Fundamental assessments (updated monthly)
        self.assessments = {
            # STRONG: No structural shift
            'Crude/Gold': FundamentalAssessment(
                pair_name='Crude/Gold',
                strength=FundamentalStrength.STRONG,
                mean_valid=True,
                expected_reversion_pct=100,
                allocation_multiplier=1.0,
                reasoning='No structural shift in oil demand. Current deviation driven by geopolitics (temporary). Historical mean valid.',
                last_updated='2026-04-19'
            ),
            'Crude/Silver': FundamentalAssessment(
                pair_name='Crude/Silver',
                strength=FundamentalStrength.STRONG,
                mean_valid=True,
                expected_reversion_pct=100,
                allocation_multiplier=1.0,
                reasoning='Oil demand unchanged. Silver shift affects silver/gold more than crude/silver.',
                last_updated='2026-04-19'
            ),

            # MODERATE: Partial structural shift
            'Silver/Copper': FundamentalAssessment(
                pair_name='Silver/Copper',
                strength=FundamentalStrength.MODERATE,
                mean_valid=False,
                expected_reversion_pct=60,
                allocation_multiplier=0.75,
                reasoning='Silver shifted to industrial (60% from 30%). Supply squeeze real. New mean likely 9-10 vs historical 7.85.',
                last_updated='2026-04-19'
            ),
            'Gold/Silver': FundamentalAssessment(
                pair_name='Gold/Silver',
                strength=FundamentalStrength.MODERATE,
                mean_valid=False,
                expected_reversion_pct=50,
                allocation_multiplier=0.6,
                reasoning='Silver role fundamentally changed (safe haven → industrial). New mean likely 65-70 vs historical 80.9.',
                last_updated='2026-04-19'
            ),

            # WEAK/AVOID: Strong structural shift
            'Copper/Zinc': FundamentalAssessment(
                pair_name='Copper/Zinc',
                strength=FundamentalStrength.AVOID,
                mean_valid=False,
                expected_reversion_pct=20,
                allocation_multiplier=0.25,
                reasoning='Strong structural shift: Electrification (EVs, AI) favors copper. Supply deficit structural (10yr+ fix). New mean likely 0.048-0.050 vs historical 0.040.',
                last_updated='2026-04-19'
            ),

            # Default for pairs not researched yet
            'Crude/NatGas': FundamentalAssessment(
                pair_name='Crude/NatGas',
                strength=FundamentalStrength.MODERATE,
                mean_valid=True,
                expected_reversion_pct=70,
                allocation_multiplier=0.8,
                reasoning='Energy spread. Some shift to renewables but natural gas still needed. Research needed.',
                last_updated='2026-04-19'
            ),
            'Crude/Copper': FundamentalAssessment(
                pair_name='Crude/Copper',
                strength=FundamentalStrength.MODERATE,
                mean_valid=True,
                expected_reversion_pct=60,
                allocation_multiplier=0.7,
                reasoning='Copper shift to electrification, but crude stable. Mixed dynamics. Research needed.',
                last_updated='2026-04-19'
            ),
            'Nifty/BankNifty': FundamentalAssessment(
                pair_name='Nifty/BankNifty',
                strength=FundamentalStrength.MODERATE,
                mean_valid=True,
                expected_reversion_pct=70,
                allocation_multiplier=0.8,
                reasoning='Sector rotation. No major structural shift. Research needed.',
                last_updated='2026-04-19'
            ),
            'Gold/Copper': FundamentalAssessment(
                pair_name='Gold/Copper',
                strength=FundamentalStrength.MODERATE,
                mean_valid=False,
                expected_reversion_pct=60,
                allocation_multiplier=0.7,
                reasoning='Copper shift to electrification. Gold stable. Research needed.',
                last_updated='2026-04-19'
            ),
        }

    def get_assessment(self, pair_name: str) -> FundamentalAssessment:
        """Get fundamental assessment for a pair"""
        # Normalize pair name (handle different formats)
        normalized = self._normalize_pair_name(pair_name)

        # Return assessment if exists
        if normalized in self.assessments:
            return self.assessments[normalized]

        # Default for unknown pairs (conservative)
        return FundamentalAssessment(
            pair_name=pair_name,
            strength=FundamentalStrength.MODERATE,
            mean_valid=False,
            expected_reversion_pct=50,
            allocation_multiplier=0.5,
            reasoning='No fundamental research available. Trade with caution.',
            last_updated='2026-04-19'
        )

    def _normalize_pair_name(self, pair_name: str) -> str:
        """Normalize pair name to match assessments dict"""
        # Handle different naming formats
        name = pair_name.replace('Ratio', '').replace('ratio', '').strip()

        # Common variations
        variations = {
            'Gold/Silver Ratio': 'Gold/Silver',
            'Copper/Zinc Ratio': 'Copper/Zinc',
            'Silver/Copper Ratio': 'Silver/Copper',
            'Crude/Gold Ratio': 'Crude/Gold',
            'Crude Oil/Gold': 'Crude/Gold',
            'CRUDE/GOLD': 'Crude/Gold',
            # Add more as needed
        }

        return variations.get(name, name)

    def filter_opportunity(self, pair_name: str, original_score: int,
                          original_allocation: float, expected_return: float) -> dict:
        """
        Filter a pair opportunity by fundamentals

        Returns adjusted values:
        - adjusted_score: Original score * strength factor
        - adjusted_allocation: Original allocation * multiplier
        - adjusted_return: Expected return * reversion_pct
        - should_show: Whether to show in scanner
        - warning: User warning if fundamentals weak
        """
        assessment = self.get_assessment(pair_name)

        # Strength factor (for scoring)
        strength_factors = {
            FundamentalStrength.STRONG: 1.0,
            FundamentalStrength.MODERATE: 0.75,
            FundamentalStrength.WEAK: 0.5,
            FundamentalStrength.AVOID: 0.25
        }
        strength_factor = strength_factors[assessment.strength]

        # Adjusted values
        adjusted_score = int(original_score * strength_factor)
        adjusted_allocation = original_allocation * assessment.allocation_multiplier
        adjusted_return = expected_return * (assessment.expected_reversion_pct / 100)

        # Should show in scanner? (only if score >40 after adjustment)
        should_show = adjusted_score >= 40

        # Warning message
        if assessment.strength == FundamentalStrength.AVOID:
            warning = f"⚠️ AVOID: {assessment.reasoning}"
        elif assessment.strength == FundamentalStrength.WEAK:
            warning = f"⚠️ WEAK: {assessment.reasoning}"
        elif assessment.strength == FundamentalStrength.MODERATE:
            warning = f"⚠️ CAUTION: {assessment.reasoning}"
        else:
            warning = None

        return {
            'adjusted_score': adjusted_score,
            'adjusted_allocation': adjusted_allocation,
            'adjusted_return': adjusted_return,
            'should_show': should_show,
            'warning': warning,
            'assessment': assessment
        }

    def needs_update(self) -> bool:
        """Check if fundamental research needs updating"""
        from datetime import datetime, timedelta

        # Get oldest assessment date
        oldest_date = min(
            datetime.strptime(a.last_updated, '%Y-%m-%d')
            for a in self.assessments.values()
        )

        # Update if older than 30 days
        days_old = (datetime.now() - oldest_date).days
        return days_old > 30

    def get_update_status(self) -> dict:
        """Get status of fundamental research"""
        from datetime import datetime

        assessments_by_date = {}
        for a in self.assessments.values():
            date = a.last_updated
            if date not in assessments_by_date:
                assessments_by_date[date] = []
            assessments_by_date[date].append(a.pair_name)

        oldest_date = min(assessments_by_date.keys())
        days_old = (datetime.now() - datetime.strptime(oldest_date, '%Y-%m-%d')).days

        return {
            'oldest_research_date': oldest_date,
            'days_old': days_old,
            'needs_update': days_old > 30,
            'assessments_by_date': assessments_by_date,
            'recommendation': 'Update research' if days_old > 30 else 'Research current'
        }


def main():
    """Print fundamental filter status"""
    filter_obj = FundamentalFilter()

    print("\n" + "="*80)
    print("FUNDAMENTAL FILTER - PAIR TRADE VALIDITY")
    print("="*80)

    status = filter_obj.get_update_status()
    print(f"\nResearch Status:")
    print(f"  Last Updated: {status['oldest_research_date']}")
    print(f"  Age: {status['days_old']} days")
    print(f"  Status: {status['recommendation']}")

    print("\n" + "="*80)
    print("FUNDAMENTAL ASSESSMENTS")
    print("="*80)

    # Group by strength
    by_strength = {
        FundamentalStrength.STRONG: [],
        FundamentalStrength.MODERATE: [],
        FundamentalStrength.WEAK: [],
        FundamentalStrength.AVOID: []
    }

    for assessment in filter_obj.assessments.values():
        by_strength[assessment.strength].append(assessment)

    # Print each group
    for strength in [FundamentalStrength.STRONG, FundamentalStrength.MODERATE,
                     FundamentalStrength.WEAK, FundamentalStrength.AVOID]:
        pairs = by_strength[strength]
        if pairs:
            print(f"\n{'='*80}")
            print(f"{strength.value} FUNDAMENTAL SUPPORT")
            print(f"{'='*80}")

            for a in pairs:
                print(f"\n{a.pair_name}:")
                print(f"  Mean Valid: {'Yes' if a.mean_valid else 'No (obsolete)'}")
                print(f"  Expected Reversion: {a.expected_reversion_pct}% of historical")
                print(f"  Allocation Multiplier: {a.allocation_multiplier:.0%}")
                print(f"  Reasoning: {a.reasoning}")

    print("\n" + "="*80)
    print("MONTHLY UPDATE RECOMMENDATION")
    print("="*80)
    print("\nFundamental shifts are SLOW (months/years), not daily.")
    print("Update frequency: MONTHLY")
    print("\nWhat to check monthly:")
    print("  1. Major policy changes (EV mandates, carbon taxes)")
    print("  2. Supply shocks (mine closures, OPEC cuts)")
    print("  3. Demand shifts (recession, tech adoption)")
    print("  4. Correlation changes (industrial vs safe haven)")
    print("\nCurrent recommendation: Research is FRESH (updated Apr 19, 2026)")
    print("Next review: May 19, 2026")
    print()


if __name__ == "__main__":
    main()
