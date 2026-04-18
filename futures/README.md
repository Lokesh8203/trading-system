# Futures Trading System

Grade A signal generation for Gold and Silver futures (MCX/COMEX)

## Quick Start

**Run the scanner:**
```bash
python3 futures/scanners/gold_silver_15min_scanner.py
```

**Expected output:** 2-3 Grade A signals per day (both instruments combined)

---

## What You Get

### Signal Quality (Grade A Only)
- ✅ **Confidence**: 80%+
- ✅ **R:R Ratio**: 1.5:1 minimum
- ✅ **Risk**: <1.5% per trade
- ✅ **Volume**: 1.2x+ average confirmation

### Signal Patterns
1. **Breakout High** - Price breaks above 20-bar high with volume
2. **Breakdown Low** - Price breaks below 20-bar low with volume
3. **SMA Bounce** - Pullback to 20 SMA in uptrend

### Signal Frequency
- **Choppy days**: 0-1 signals
- **Trending days**: 5-8 signals
- **Average**: 2-3 signals per day

---

## Entry Timing

**WAIT FOR CANDLE CLOSE**

Example:
```
15:00:00 - 15-min candle opens
15:14:59 - Candle still in progress
15:15:00 - Candle CLOSES ← Check conditions HERE
15:15:01 - Enter if signal appears
```

**Why wait for close?**
- Reduces false signals (price can reverse mid-candle)
- Confirms the pattern is real
- Standard practice for timeframe-based systems

---

## Position Sizing

Based on ₹10L capital, 2% risk per trade:

### Gold (GC=F)
- Full contract: 100 oz × $1 = $100/point
- Mini contract: 10 oz × $1 = $10/point
- **Recommendation**: Trade mini contracts

### Silver (SI=F)
- Full contract: 5,000 oz × $0.01 = $50/point
- **Recommendation**: 1-2 contracts max

### Example Trade
```
Signal: Silver BUY @ $81.84
Stop: $81.64 (20 cents = 20 points)
Target: $82.34 (50 cents = 50 points)

Risk per contract: 20 points × $50 = $1,000
For ₹20K risk: Trade 2 contracts max
```

---

## Bracket Orders (Recommended)

Place all three orders simultaneously:

1. **Entry order**: Buy/Sell at signal price
2. **Stop loss**: Exit at stop level (OCO with target)
3. **Target**: Exit at target level (OCO with stop)

Whichever hits first, other cancels automatically.

---

## Files Structure

```
futures/
├── scanners/
│   └── gold_silver_15min_scanner.py    # Main production scanner
├── indicators/
│   ├── hurst_exponent.py               # Market regime detection
│   └── volume_profile.py               # Volume-based levels
├── analysis/
│   ├── manual_trade_assessment.py      # Pattern identification
│   └── quality_filtered_signals.py     # Signal quality analysis
├── backtesting/
│   └── intraday_15min_backtest.py      # Historical validation
└── README.md                            # This file
```

---

## How It Works

### 1. Pattern Detection (Price Action)
- Scans 15-min bars for breakouts, breakdowns, bounces
- NO complex indicators (no Hurst required for real-time)
- Just moving averages, volume, ATR

### 2. Quality Filter (Grade A)
Confidence score based on:
- R:R ratio (higher = better)
- Volume confirmation (1.2x+ average)
- Risk percentage (<1.5%)
- Pattern type (breakouts score higher)

Only signals with 80%+ confidence are shown.

### 3. Signal Generation
Each signal includes:
- Entry price (current close)
- Stop loss (ATR-based)
- Target (2x ATR for breakouts, 1.5x for bounces)
- Risk/reward metrics
- Reasoning/pattern name

---

## Historical Performance

**Last 30 days (Gold only):**
- Total signals: 934
- Grade A signals: 82 (8.8%)
- Frequency: 2.7 Grade A signals/day

**Grade A quality breakdown:**
- Average R:R: 2.5:1
- Average risk: 0.8% per trade
- Average volume: 1.8x

---

## Usage Patterns

### Real-Time Scanning (Recommended)
```bash
# Run every 15 minutes manually
python3 futures/scanners/gold_silver_15min_scanner.py

# Or add to cron (every 15 min, 9 AM - 5 PM Mon-Fri)
*/15 9-17 * * 1-5 cd /Users/lsurana/trading-system && python3 futures/scanners/gold_silver_15min_scanner.py >> logs/scanner.log 2>&1
```

### Batch Scanning
Run at key times:
- 9:00 AM (market open)
- 12:00 PM (mid-day)
- 3:00 PM (afternoon)
- 5:00 PM (close)

---

## Next Steps

1. **Test the scanner**: Run it now to see live signals
2. **Paper trade**: Track signals for 1 week before real money
3. **Set up alerts**: Configure desktop/mobile notifications
4. **Automate**: Add to cron for continuous scanning

---

## Important Notes

- **Data source**: Uses yfinance (free, 15-min delayed)
- **Instruments**: COMEX Gold/Silver (GC=F, SI=F) as proxy for MCX
- **For MCX**: Replace tickers with actual MCX data feed
- **Timezone**: All times in market timezone (EST for COMEX)

---

## Support

Issues? Check:
1. Internet connection (for data fetch)
2. yfinance version (`pip3 install --upgrade yfinance`)
3. Sufficient historical data (needs 400+ bars)

---

**Last updated**: 2026-04-18  
**Status**: Production ready ✅
