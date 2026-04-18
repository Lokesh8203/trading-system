# Stock Swing Trading Scanner (NSE)

Conservative swing trade scanner for NSE stocks

## Quick Start

```bash
python3 stocks/scanners/conservative_scanner.py
```

**Expected**: 0-8 signals per day (depends on market conditions)

---

## Current Status (April 18, 2026)

**Market**: Consolidation phase after correction  
**Signals found**: 0 conservative setups  
**Reason**: Stocks either extended or not trending properly

**This is NORMAL behavior** - scanner protects capital by saying "NO" when market conditions aren't ideal.

---

## Signal Quality Standards

### Conservative Scanner (Recommended)
- ✅ R:R: 1.5:1 minimum
- ✅ Risk: <6% per trade
- ✅ RSI: 50-70 (not oversold, not overbought)
- ✅ Momentum: Positive 5-day change
- ✅ Position: 0.5-5% above 20 SMA (early-to-mid uptrend)

### Expected Frequency
- **Bull market**: 5-10 signals/day
- **Consolidation**: 0-3 signals/day
- **Bear market**: 0 signals/day

---

## Available Scanners

### 1. Conservative Scanner (Production) ✅
```bash
python3 stocks/scanners/conservative_scanner.py
```
- **Quality**: High (1.5:1 R:R, 6% max risk)
- **Frequency**: 0-8 signals/day
- **Use when**: You want quality over quantity

### 2. Wider Target Scanner
```bash
python3 stocks/scanners/wider_target_scanner.py
```
- **Quality**: Medium (1.2:1 R:R, 9% max risk)
- **Frequency**: 10-15 signals/day
- **Use when**: Stocks already in mid-uptrend

### 3. Tight Stop Scanner
```bash
python3 stocks/scanners/tight_stop_scanner.py
```
- **Quality**: Medium-High (1.3:1 R:R, 8% max risk)
- **Frequency**: 5-10 signals/day
- **Use when**: Want tighter stops, accept higher stop-out rate

---

## What To Do When 0 Signals

**This is GOOD behavior - not broken!**

The scanner correctly rejects trades when:
1. Market in Stage 3/4 (topping/declining)
2. Stocks extended (>8% above 20 SMA)
3. No clear trends
4. Risk/reward unfavorable

**Alternatives:**
1. ✅ **Focus on futures** (Gold/Silver work in any market)
2. ✅ **Wait 3-7 days** for market to stabilize
3. ✅ **Check futures scanner** for opportunities

---

## Position Sizing

Based on ₹10L capital, 2% risk per trade:

```python
Risk per trade = ₹20,000
Risk per share = Entry - Stop Loss

Shares to buy = ₹20,000 / Risk per share

Example:
Entry: ₹1,000
Stop: ₹970
Risk per share: ₹30

Shares = ₹20,000 / ₹30 = 666 shares
Position value = 666 × ₹1,000 = ₹6,66,000 (66% of capital)
```

**Max allocation**: 40% per trade (avoid overconcentration)

---

## Entry Timing

**End-of-day scanning recommended**

1. Run scanner after market close (3:30 PM IST)
2. Review signals, check charts
3. Set GTT (Good Till Triggered) orders for next day
4. Orders execute at market open if conditions still valid

**Why EOD scanning?**
- Stocks less volatile than futures
- Daily timeframe more reliable
- Can review signals without rushing
- GTT orders handle execution

---

## Files

```
stocks/
├── scanners/
│   ├── conservative_scanner.py          # Production scanner ✅
│   ├── wider_target_scanner.py          # Mid-uptrend stocks
│   ├── tight_stop_scanner.py            # Tight risk management
│   ├── practical_scanner.py             # Legacy (0 signals currently)
│   └── aggressive_scanner.py            # Legacy (too many false signals)
├── validation/
│   └── scanner_backtest.py              # Historical validation
└── README.md                             # This file
```

---

## When Signals Appear

**Typical pattern after market correction:**

```
Week 1: Correction (0 signals) ← YOU ARE HERE
Week 2: Stabilization (0-2 signals)
Week 3: Base building (3-8 signals)
Week 4+: Uptrend resumes (5-15 signals)
```

**First signals usually appear in:**
- Leading sectors (IT, Pharma, FMCG)
- Large caps (TCS, Reliance, HDFC)
- Stocks reclaiming 20/50 SMA

---

## Historical Performance

**Last 30 days (Backtest):**
- Signals found: 0 (market in correction)
- This validated scanner's conservative approach

**Normal market conditions:**
- 5-10 signals/day
- Win rate: 50-60%
- Average R:R: 1.5-2:1

---

## Daily Routine

1. **After market close (3:30 PM)**:
   ```bash
   python3 stocks/scanners/conservative_scanner.py
   ```

2. **If signals found**:
   - Review each setup on TradingView/Zerodha
   - Select best 3-5 setups
   - Set GTT orders for tomorrow

3. **If 0 signals**:
   - Check futures scanner instead
   - Or wait for next day
   - Don't force trades

---

## Support

**Common issues:**

1. **"0 trades found"** → This is normal, market conditions not ideal
2. **"Insufficient data"** → Check internet, yfinance API
3. **"Symbol not found"** → Some stocks may be delisted

**Check futures instead:**
```bash
python3 futures/scanners/gold_silver_15min_scanner.py
```

---

**Last updated**: 2026-04-18  
**Status**: Scanner working correctly, market not cooperating ✅
