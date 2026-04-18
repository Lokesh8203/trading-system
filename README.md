# Trading System

Systematic signal generation for Indian markets (NSE stocks and MCX/COMEX futures)

**Status**: Production ready ✅  
**Last updated**: 2026-04-18

---

## Quick Start

### Futures (Gold/Silver) - Grade A Signals
```bash
python3 futures/scanners/gold_silver_15min_scanner.py
```
**Expected**: 2-3 high-quality signals per day

### Stocks (NSE) - Conservative Swing Trades
```bash
python3 stocks/scanners/conservative_scanner.py
```
**Expected**: 0-8 signals per day (market dependent)

---

## What This System Does

### ✅ Futures (15-min timeframe)
- **Instruments**: Gold (GC=F), Silver (SI=F)
- **Patterns**: Breakouts, breakdowns, SMA bounces
- **Quality**: Grade A only (Confidence 80%+, R:R 1.5:1+)
- **Frequency**: 2-3 signals/day
- **Entry**: Wait for 15-min candle close

**Works in ANY market condition** (up, down, sideways)

### ✅ Stocks (Daily timeframe)
- **Universe**: NSE top 60 liquid stocks
- **Patterns**: Early-to-mid uptrend entries
- **Quality**: Conservative (R:R 1.5:1+, Risk <6%)
- **Frequency**: 0-8 signals/day (bull market: 5-10)
- **Entry**: EOD scan, GTT orders for next day

**Best in bull markets**, correctly says "NO" during corrections

---

## Documentation

- **[futures/README.md](futures/README.md)** - Futures scanner guide
- **[stocks/README.md](stocks/README.md)** - Stock scanner guide  
- **[QUICK_START.md](QUICK_START.md)** - Setup instructions
- **[TRADING_KNOWLEDGE_BASE.md](TRADING_KNOWLEDGE_BASE.md)** - Market concepts

---

## Signal Quality (Grade A Standard)

| Metric | Futures | Stocks |
|--------|---------|--------|
| Confidence | 80%+ | 70%+ |
| R:R Ratio | 1.5:1+ | 1.5:1+ |
| Max Risk | <1.5% | <6% |
| Volume | 1.2x+ avg | Market dependent |

---

## Happy Trading! 🎯

See individual READMEs for detailed usage.
