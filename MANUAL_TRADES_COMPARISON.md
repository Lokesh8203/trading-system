# Manual Trades Comparison Guide

**Purpose:** Compare your manual trades vs system signals  
**Date:** 2026-04-18

---

## 📊 TradingView Setup

### **Instruments to Check:**

#### **Gold:**
```
Symbol: COMEX:GC1!
(or MCX:GOLD1! if you have MCX data)

Settings:
- Timeframe: 15 minutes
- Date Range: April 15-17, 2026
- Focus Time: 05:00-09:00 UTC on April 17
  (Our system found 2 signals in this window)
```

#### **Silver:**
```
Symbol: COMEX:SI1!
(or MCX:SILVER1!)

Settings:
- Timeframe: 15 minutes
- Date Range: April 15-17, 2026
```

#### **For Reference - Other Instruments:**
```
Crude Oil: MCX:CRUDEOIL1! or NYMEX:CL1!
Nifty: NSE:NIFTY or Index Futures
Bank Nifty: NSE:BANKNIFTY or Index Futures
```

---

## 🎯 What System Found (April 17, 2026)

### **Trade #1:**
```
Time:   2026-04-17 05:15 UTC (10:45 AM IST)
Type:   SELL
Entry:  $4,824.80
Reason: Mean-reversion (Hurst 0.448)
Result: Target hit in 15 minutes
P&L:    +$0.54
```

### **Trade #2:**
```
Time:   2026-04-17 08:45 UTC (02:15 PM IST)
Type:   SELL
Entry:  $4,817.80
Reason: Mean-reversion (Hurst 0.449)
Result: Target hit in 15 minutes
P&L:    +$1.99
```

---

## 📝 Manual Trade Template

When you check TradingView, mark YOUR trades using this format:

```markdown
### My Trade #1:
- Time: [HH:MM UTC / IST]
- Type: BUY / SELL
- Entry: $X,XXX.XX
- Exit: $X,XXX.XX (or still open)
- Reason: [Why you took it - pattern, level, etc.]
- P&L: +/- $XX.XX
- Duration: [X minutes]

### My Trade #2:
[Same format]
```

---

## 🔍 Questions to Answer

### **1. Did you see the same signals?**
- [ ] Yes, I would have taken Trade #1 (05:15 UTC)
- [ ] Yes, I would have taken Trade #2 (08:45 UTC)
- [ ] No, I wouldn't have taken these

**If No, why not?**
- [ ] Didn't see the setup
- [ ] Saw it but different timing
- [ ] Saw it but different entry level
- [ ] Risk/reward wasn't attractive
- [ ] Other: ___________

### **2. What trades did system MISS?**

List any trades YOU would have taken that system didn't catch:

```
Trade A:
- Time: ___________
- Type: BUY/SELL
- Entry: ___________
- Pattern: ___________ (breakout, reversal, range, etc.)
- Why system missed it: ___________

Trade B:
[Same format]
```

### **3. Key Differences:**

**System strengths:**
- What did system catch that you might have missed?

**System weaknesses:**
- What did you see that system didn't?
- Were stop/targets reasonable?
- Was timing good?

---

## 💡 Data Format for Me

When you come back with data, paste it like this:

```
## GOLD - April 15-17, 2026

### My Manual Trades:
1. SELL @ $4,825 (05:20 UTC) → $4,820 (+$5) - 20 min
   Reason: Double top rejection at $4,830

2. BUY @ $4,810 (10:30 UTC) → $4,825 (+$15) - 45 min
   Reason: Bounce off support, volume spike

3. SELL @ $4,818 (08:45 UTC) → $4,812 (+$6) - 15 min
   Reason: Failed breakout above $4,820

### System Signals:
- Signal #1: SELL @ $4,824.80 (05:15) ✅ Match my trade #1
- Signal #2: SELL @ $4,817.80 (08:45) ✅ Match my trade #3

### System Missed:
- My trade #2 (BUY @ $4,810) - System was in mean-revert mode, only SELL signals

### Analysis:
- System caught 2 of my 3 trades (66% overlap)
- System missed the BUY because Hurst was <0.45 (mean-revert mode)
- My entries slightly different but same direction
- System stop/target calculation has bugs (stop was $5,324!)
```

---

## 🔧 Bug Status

### **Fixed:**
- ✅ Timeframe (changed from 1-hour → 15-min)
- ✅ Hurst lookback (adjusted for intraday)
- ✅ Data quality (verified as good)

### **Still Broken:**
- ❌ Stop/Target calculation
  - Signal #1 had stop at $5,324 (should be ~$4,875)
  - Logic for HVN-based stops is buggy
  - Need to fall back to fixed points

### **In Progress:**
- ⏳ Fixing stop/target logic (added sanity checks)
- ⏳ Testing with assertions to catch bad levels

---

## 💰 Live Scanner Cost

### **Cost per Scan (2 instruments):**
```
Data fetching:     ~500 tokens
Hurst calculation: ~1,000 tokens
Volume Profile:    ~500 tokens
Signal generation: ~500 tokens
------------------------
TOTAL:            ~2,500 tokens
```

### **Running Continuously:**

**24/7 Operation (every 15 min):**
```
4 scans/hour × 24 hours = 96 scans/day
96 scans × 2,500 tokens = 240,000 tokens/day

Cost: ~$0.72/day = ~$22/month
```

**Optimized (Trading Hours Only):**
```
9 AM - 5 PM IST (8 hours/day)
4 scans/hour × 8 hours = 32 scans/day
32 scans × 2,500 tokens = 80,000 tokens/day

Cost: ~$0.24/day = ~$7/month
```

**Ultra Optimized:**
```
Every 30 minutes (not 15)
Gold only (not Silver)

Cost: ~$3-4/month
```

### **Verdict:** 
✅ **Very affordable!** Cheaper than most data feeds ($50-200/month)

---

## 🚀 How to Run Live Scanner

### **Test Once:**
```bash
cd /Users/lsurana/trading-system
python3 futures/live_scanner/scanner_15min.py --mode once
```

### **Run Continuously (every 15 min):**
```bash
python3 futures/live_scanner/scanner_15min.py --mode continuous
```

### **Custom Interval:**
```bash
# Scan every 30 minutes
python3 futures/live_scanner/scanner_15min.py --mode continuous --interval 30
```

### **Stop Scanner:**
Press `Ctrl+C`

---

## 📊 What Scanner Shows

```
================================================================================
SCAN #1 - 2026-04-18 15:10:58
================================================================================

📊 Gold MCX
   Price: $4879.60
   🎯 SIGNAL: SELL
   Confidence: 68/100
   Entry: $4,879.60
   Stop: $4,929.60
   Target: $4,779.60
   Hurst: 0.4480 (MEAN_REVERTING)
   🔔 HIGH CONFIDENCE ALERT!

📊 Silver MCX
   Price: $81.84
   No signal (Hurst: 0.523)

📈 SESSION STATS:
   Scans completed: 1
   Signals found: 1
   API calls: 2
```

---

## 🎯 Next Steps

### **1. Check TradingView (You Do This):**
- Open COMEX:GC1! on 15-min chart
- Date: April 15-17, 2026
- Mark YOUR trades
- Note what you would have done

### **2. Come Back With Data:**
- Paste your trades in format above
- I'll compare vs system
- We'll identify gaps

### **3. Fix Bugs (I Do This):**
- Fix stop/target calculation
- Add your feedback to improve system
- Retest and validate

### **4. Decide on Scanner:**
- Run live for 1-2 weeks?
- Compare system vs your manual eye?
- See if it catches what you see?

---

## 📌 Key Questions

Before we continue, I need to know:

1. **Which TradingView data do you have?**
   - [ ] COMEX (US futures)
   - [ ] MCX (Indian)
   - [ ] Both

2. **What timezone do you trade in?**
   - [ ] IST (India)
   - [ ] UTC
   - [ ] Other: _______

3. **When do you want scanner to run?**
   - [ ] 24/7 (most expensive, ~$22/month)
   - [ ] Trading hours only (9am-5pm IST, ~$7/month)
   - [ ] Custom hours: _______
   - [ ] Manual (I'll run it when I want)

4. **Should I fix bugs first or wait for your manual trade data?**
   - [ ] Fix bugs now, I'll check TradingView later
   - [ ] Wait, I'll give you manual trades first
   - [ ] Do both in parallel

---

**Files Created:**
- `futures/live_scanner/scanner_15min.py` - Live scanner
- `futures/BACKTEST_15MIN_RESULTS.md` - Detailed backtest analysis
- `MANUAL_TRADES_COMPARISON.md` - This guide

**Status:**
- ✅ Backtest found 2 trades (both winners)
- ✅ Live scanner working (low cost)
- ❌ Stop/target calculation buggy
- ⏳ Need your manual trade data to compare
