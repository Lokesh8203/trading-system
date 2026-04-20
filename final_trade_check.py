"""
FINAL TRADE CHECK - Multi-Timeframe Verification

Run THIS before entering any trade from master scanner.

Why separate from master scanner?
- Master scanner needs to be FAST (under 30 seconds)
- Multi-timeframe analysis takes 2-3 minutes
- Only check trades you're actually planning to take

Usage:
    python3 final_trade_check.py SILVER LONG
    python3 final_trade_check.py ^NSEI LONG
    python3 final_trade_check.py RELIANCE.NS SHORT

Author: Trading System
Date: 2026-04-20
Version: 1.0
"""

import sys
import warnings
warnings.filterwarnings('ignore')

from futures.indicators.multi_timeframe_analyzer import MultiTimeframeAnalyzer


def main():
    if len(sys.argv) < 3:
        print("Usage: python3 final_trade_check.py <SYMBOL> <DIRECTION>")
        print()
        print("Examples:")
        print("  python3 final_trade_check.py SI=F LONG")
        print("  python3 final_trade_check.py ^NSEI LONG")
        print("  python3 final_trade_check.py RELIANCE.NS SHORT")
        print()
        print("Common symbols:")
        print("  Futures: SI=F (Silver), GC=F (Gold), CL=F (Crude)")
        print("  Indices: ^NSEI (Nifty), ^NSEBANK (BankNifty)")
        print("  Stocks: Add .NS suffix (RELIANCE.NS, TCS.NS)")
        return

    symbol = sys.argv[1]
    direction = sys.argv[2].upper()

    if direction not in ['LONG', 'SHORT']:
        print(f"Error: Direction must be LONG or SHORT, got '{direction}'")
        return

    print("\n" + "="*70)
    print(f"FINAL TRADE CHECK: {symbol} {direction}")
    print("="*70)
    print()
    print("Analyzing across multiple timeframes...")
    print("This takes 1-2 minutes, please wait...")
    print()

    analyzer = MultiTimeframeAnalyzer()
    result = analyzer.analyze(symbol, direction, include_15min=False)

    print("\n" + "="*70)
    print("VERDICT")
    print("="*70)
    print()
    print(f"Consensus Score: {result.consensus_score}/100")
    print(f"Clean Timeframes: {result.timeframes_clean}/{result.timeframes_total}")
    print(f"Safe to Trade: {'✅ YES' if result.is_safe_entry else '❌ NO'}")
    print()
    print(f"Recommendation: {result.recommendation}")

    if result.warnings:
        print()
        print("WARNINGS:")
        for warning in result.warnings:
            print(f"  • {warning}")

    print()
    print("="*70)

    if result.is_safe_entry:
        print("✅ PROCEED - Multi-timeframe analysis passed")
    else:
        print("❌ SKIP THIS TRADE - Multi-timeframe issues detected")
        print()
        print("Action: Wait for better setup or skip entirely")

    print("="*70)
    print()


if __name__ == "__main__":
    main()
