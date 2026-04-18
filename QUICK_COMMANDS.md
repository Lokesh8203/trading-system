# Quick Commands Reference

## Daily Scanning

### Multi-Instrument Scanner (All commodities + indices)
```bash
python3 futures/scanners/multi_instrument_scanner.py
```
**Scans**: Gold, Silver, Crude, Nifty, Bank Nifty  
**Expected**: 2-3 Grade A signals/day across all instruments  
**Run**: Every 15 minutes during market hours

### Gold/Silver Scanner (Commodities only)
```bash
python3 futures/scanners/gold_silver_15min_scanner.py
```
**Scans**: Gold, Silver (COMEX)  
**Expected**: 2-3 Grade A signals/day  
**Run**: Every 15 minutes

### Stock Scanner (NSE)
```bash
python3 stocks/scanners/conservative_scanner.py
```
**Scans**: NSE top 60 liquid stocks  
**Expected**: 0-8 signals/day (market dependent)  
**Run**: After market close (3:30 PM IST)

---

## What to Expect

### Futures (15-min timeframe)
- **Trending days**: 5-8 signals
- **Choppy days**: 0-1 signals
- **Average**: 2-3 signals/day per instrument
- **Entry**: Wait for 15-min candle close, then enter

### Stocks (Daily timeframe)
- **Bull market**: 5-10 signals/day
- **Consolidation**: 0-3 signals/day
- **Bear market**: 0 signals/day
- **Entry**: Set GTT orders after EOD scan

---

## Position Sizing

### Futures (₹10L capital, 2% risk = ₹20K)
**Silver example**:
```
Signal: BUY @ $81.84
Stop: $81.64 (20 cents = 20 points)
Risk: 20 × $50 = $1,000 per contract
Contracts: ₹20K / ₹1K = 2 contracts max
```

**Gold mini**:
```
Signal: BUY @ $2,500
Stop: $2,480 (20 points)
Risk: 20 × $10 = $200 per contract
Contracts: ₹20K / ₹200 = 10 contracts max
```

### Stocks (₹10L capital, 2% risk = ₹20K)
**Example**:
```
Signal: BUY @ ₹1,000
Stop: ₹970 (₹30 risk/share)
Shares: ₹20K / ₹30 = 666 shares
Position: 666 × ₹1,000 = ₹6.66L (66% of capital)
```

---

## Entry Rules

### Futures
1. Wait for 15-min candle to close (e.g., 15:15:00)
2. Check scanner output immediately after close
3. If Grade A signal appears, enter at next candle open
4. Place bracket order (Entry + Stop + Target)

### Stocks
1. Run scanner after market close (3:30 PM)
2. Review signals, select best 3-5 setups
3. Set GTT orders for next day
4. Orders execute at market open if conditions met

---

## Grade A Standards

### Futures
- ✅ Confidence: 80%+
- ✅ R:R Ratio: 1.5:1+
- ✅ Risk: <1.5% per trade
- ✅ Volume: 1.2x+ average

### Stocks (Conservative)
- ✅ R:R Ratio: 1.5:1+
- ✅ Risk: <6% per trade
- ✅ RSI: 50-70
- ✅ Momentum: Positive 5-day change
- ✅ Position: 0.5-5% above 20 SMA

---

## Data Sources

### Available Sources
```bash
# Default: yfinance (COMEX proxies)
python3 futures/scanners/multi_instrument_scanner.py

# TradingView symbols
python3 futures/scanners/multi_instrument_scanner.py --source tradingview

# MCX symbols (currently using proxies, needs real MCX feed)
python3 futures/scanners/multi_instrument_scanner.py --source mcx
```

---

## When 0 Signals Found

**For futures**: Market in consolidation, check back in 15 minutes

**For stocks**: Market not cooperating, scanner correctly protecting capital
- Focus on futures instead
- Wait 3-7 days for market stabilization
- Don't force trades

---

## Automation Setup (Future)

### Cron job for continuous scanning
```bash
# Every 15 minutes, 9 AM - 5 PM, Mon-Fri
*/15 9-17 * * 1-5 python3 futures/scanners/multi_instrument_scanner.py >> logs/scanner.log 2>&1
```

---

## Quick Reference

| Scanner | Instruments | Frequency | Timeframe | Expected Signals |
|---------|-------------|-----------|-----------|------------------|
| Multi-instrument | Gold, Silver, Crude, Nifty, Bank Nifty | Every 15 min | 15-min | 2-3/day |
| Gold/Silver | Gold, Silver | Every 15 min | 15-min | 2-3/day |
| Conservative | NSE top 60 | EOD | Daily | 0-8/day |

---

**Last updated**: 2026-04-18
