# Trading System - Complete Setup

Production-ready trading system for Indian markets (₹12L capital).

## 🚀 Quick Start - One Command

```bash
python3 master_scanner.py
```

**Shows top 15 opportunities across:**
- Macro futures (weeks-months)
- Intraday signals (Grade A, 15-min)  
- Stock swings (conservative)
- Pair trades (risk-neutral)

---

## 🎯 Current Recommendations (April 19, 2026)

### #1: SILVER - Score 80/100 ⭐

**Three ways to play:**

1. **Intraday:** $81.84 → $82.34 (+0.6%, hours)
2. **Macro:** $81.84 → $105.51 (+28.9%, weeks-months)
3. **Pair:** Gold/Silver ratio SHORT (+8.4%, market neutral)

**Why silver?**
- Gold/Silver ratio at -2.26σ (very rare!)
- Silver 26% CHEAPER vs gold than historical average
- Industrial demand 50% (solar, EVs) + safe haven
- R:R: 2.72:1, bounced off 20 SMA

### Portfolio Allocation:
- Silver intraday: 10% (₹1.2L)
- Silver macro: 40% (₹4.8L)
- Gold/Silver pair: 20% (₹2.4L)
- Cash reserve: 30% (₹3.6L)

**Expected return:** +12.3%

---

## 📊 All Scanners

### 1. Master Scanner ⭐ NEW
```bash
python3 master_scanner.py
```
**One command for everything.** Top 15 ranked opportunities across all strategies.

### 2. Macro Opportunities
```bash
python3 futures/macro/favorability_scanner.py
```
Medium-term trades (weeks-months). Works anytime (weekend/after-hours).

### 3. Pair Trades ⭐ NEW
```bash
python3 futures/macro/pair_trade_analyzer.py
```
Risk-neutral spreads. Current: Gold/Silver ratio at -2.26σ.

### 4. Intraday Grade A
```bash
python3 futures/scanners/multi_instrument_scanner.py
```
15-min futures signals. 80%+ confidence, 1.5:1+ R:R.

### 5. Stock Swings
```bash
python3 stocks/scanners/conservative_scanner.py
```
Conservative NSE trades. R:R 1.5:1+, Risk <6%.

---

## 💡 Key Insights

### Silver Dominates Rankings
- **Intraday:** 80/100 (Grade A signal)
- **Macro:** 80/100 (excellent positioning)
- **Pair:** 77/100 (ratio at -2.26σ)

**Not bullish "for no reason"** - it's statistical arbitrage + fundamentals.

### Crude Oil NOT Extended
**Myth:** "War premium peaked, ready to fall"  
**Reality:** Z-score 0.42σ (barely above mean)
- If war escalates: +40% upside to 3σ
- If war ends: -6.6% downside (not -10%)
- **Action:** WAIT for catalyst

### Gap Risk Quantified
- Indices (Nifty/Bank Nifty): 80/100 → Reduce allocation 25%
- Commodities: 40/100 → Full position OK
- Pairs: 30/100 → Market neutral

---

## 📋 Daily Routine

**Morning:**
```bash
python3 master_scanner.py
```

**Every 15 min (market hours):**
```bash
python3 futures/scanners/multi_instrument_scanner.py
```

**After close:**
```bash
python3 stocks/scanners/conservative_scanner.py
```

**Weekly:**
```bash
python3 futures/macro/pair_trade_analyzer.py
```

---

## 📚 Full Documentation

- **MASTER_SCANNER_GUIDE.md** - Complete dashboard guide
- **FAVORABILITY_SCANNER_GUIDE.md** - Macro opportunities
- **MACRO_TRADING_STRATEGY.md** - Strategy framework
- **QUICK_COMMANDS.md** - Quick reference

---

**Status:** Production Ready ✅  
**Last Updated:** April 19, 2026  
**GitHub:** https://github.com/Lokesh8203/trading-system

Run `python3 master_scanner.py` to see current opportunities!
