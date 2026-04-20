"""
FINAL TRADE CHECK - Multi-Timeframe Verification

Correct approach:
- Higher TF (Weekly/Daily) → Trade quality & ranking
- Lower TF (Hourly/15-min) → Entry timing

Output:
- Trade Quality: Determines if trade is valid (rank in scanner)
- Entry Status: When to enter (now, wait, or skip)

Usage:
    python3 final_trade_check.py SI=F LONG
    python3 final_trade_check.py SI=F LONG FUTURE
    python3 final_trade_check.py RELIANCE.NS LONG STOCK

Author: Trading System
Date: 2026-04-20
Version: 2.0 (Redesigned based on actual trading process)
"""

import sys
import warnings
warnings.filterwarnings('ignore')

sys.path.insert(0, '.')
from futures.indicators.multi_timeframe_scorer import MultiTimeframeScorer


def main():
    if len(sys.argv) < 3:
        print("Usage: python3 final_trade_check.py <SYMBOL> <DIRECTION> [ASSET_TYPE]")
        print()
        print("Examples:")
        print("  python3 final_trade_check.py SI=F LONG FUTURE")
        print("  python3 final_trade_check.py ^NSEI LONG FUTURE")
        print("  python3 final_trade_check.py RELIANCE.NS LONG STOCK")
        print()
        print("Asset types: STOCK or FUTURE (default: FUTURE)")
        print()
        print("Common symbols:")
        print("  Futures: SI=F (Silver), GC=F (Gold), CL=F (Crude)")
        print("  Indices: ^NSEI (Nifty), ^NSEBANK (BankNifty)")
        print("  Stocks: Add .NS suffix (RELIANCE.NS, TCS.NS)")
        return

    symbol = sys.argv[1]
    direction = sys.argv[2].upper()
    asset_type = sys.argv[3].upper() if len(sys.argv) > 3 else "FUTURE"

    if direction not in ['LONG', 'SHORT']:
        print(f"Error: Direction must be LONG or SHORT, got '{direction}'")
        return

    if asset_type not in ['STOCK', 'FUTURE']:
        print(f"Error: Asset type must be STOCK or FUTURE, got '{asset_type}'")
        return

    print("\n" + "="*70)
    print(f"FINAL TRADE CHECK: {symbol} {direction} ({asset_type})")
    print("="*70)
    print()
    print("Analyzing timeframes...")
    print("This takes 1-2 minutes, please wait...")
    print()

    scorer = MultiTimeframeScorer()
    result = scorer.score_trade(symbol, direction, asset_type)

    print("\n" + "="*70)
    print("VERDICT")
    print("="*70)
    print()
    print(f"TRADE QUALITY (Higher TF): {result.trade_quality_score}/100")
    print(f"  Weekly: {result.weekly_score}/100")
    print(f"  Daily:  {result.daily_score}/100")
    print()
    print(f"ENTRY TIMING (Lower TF):   {result.entry_timing_score}/100")
    print(f"  Hourly: {result.hourly_score}/100")
    if result.m15_score is not None:
        print(f"  15-min: {result.m15_score}/100")
    print()
    print(f"Entry Status: {result.entry_status}")
    print(f"Suggestion:   {result.entry_suggestion}")

    print()
    print("="*70)

    # Interpretation
    if result.entry_status.startswith("✅"):
        print("✅ PROCEED - Both trade quality and entry timing good")
    elif result.entry_status.startswith("⏸️"):
        print("⏸️ VALID TRADE - But wait for better entry timing")
        print()
        print(f"   Trade still ranks #{result.rank_score} in scanner")
        print(f"   Action: {result.entry_suggestion}")
    elif result.entry_status.startswith("⚠️"):
        print("⚠️ CAUTION - Trade quality moderate, entry ready")
        print()
        print("   Consider: Reduce position size or wait for higher TF to strengthen")
    else:
        print("❌ SKIP - Trade quality poor on higher timeframes")
        print()
        print("   Higher timeframes (weekly/daily) show unfavorable setup")

    print("="*70)
    print()


if __name__ == "__main__":
    main()
