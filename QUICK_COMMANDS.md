# Quick Commands - Trading System

## Daily Scanners

### Futures (Run every 15 min)
```bash
python3 futures/scanners/gold_silver_15min_scanner.py
```
Expected: 2-3 Grade A signals per day

### Stocks (Run after market close)
```bash
python3 stocks/scanners/conservative_scanner.py
```
Expected: 0-8 signals per day

---

## Current Status Check

```bash
# Check futures signals RIGHT NOW
python3 futures/scanners/gold_silver_15min_scanner.py

# Check stock signals (EOD)
python3 stocks/scanners/conservative_scanner.py
```

---

## What You'll See

### Grade A Signal Found
```
✅ SIGNAL: BUY | SMA_BOUNCE
Entry: $81.84
Stop: $81.64
Target: $82.34
Risk: $0.20 (0.25%)
R:R: 2.49:1
Confidence: 80% | Grade: A
```

**Action**: Place bracket order immediately

### No Signal
```
⏸️ No Grade A signal (price: $4879.60)
```

**Action**: Check back in 15 minutes (futures) or tomorrow (stocks)

---

## Position Sizing Quick Reference

**Capital**: ₹10L | **Risk**: 2% = ₹20K per trade

### Futures
- Gold Mini: 1-2 contracts max
- Silver: 2 contracts max

### Stocks
- Shares = ₹20,000 / (Entry - Stop)
- Max position: 40% of capital

---

## Entry Rules

### Futures (15-min)
1. Wait for candle to close (15:00, 15:15, 15:30, etc.)
2. Check if signal appears at close
3. Enter at next candle open (15:01, 15:16, 15:31, etc.)

### Stocks (Daily)
1. Scan after market close (3:30 PM)
2. Review signals
3. Set GTT orders for next day

---

## Bracket Order Setup

```
1. Entry: BUY at signal price
2. Stop Loss: SELL at stop price (OCO with target)
3. Target: SELL at target price (OCO with stop)
```

First to hit wins, other cancels automatically.

---

## Documentation

- **Detailed guide**: `futures/README.md`, `stocks/README.md`
- **Today's summary**: `SESSION_SUMMARY_APRIL_18_2026.md`
- **Quick start**: This file

---

## Git Commands

```bash
# Check status
git status

# Pull latest
git pull origin main

# Push changes
git add .
git commit -m "Your message"
git push origin main
```

---

**That's it! Keep it simple.** 🎯
