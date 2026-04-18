# Quick Start Guide - Data Collection

## 🎯 Goal
Get tick-by-tick data for trading signals on:
- **NSE**: NSE500 stocks
- **MCX**: Gold, Silver, Crude Oil
- **Global**: WTI Crude, Gold, Silver (via international futures)
- **GIFT Nifty**: (via Nifty 50 proxy for now)

## 📊 Two-Phase Approach

### Phase 1: FREE - Development & Testing (START HERE)
**Cost:** $0  
**Purpose:** Build and validate strategy without spending money

```bash
# Install dependencies
pip install yfinance pandas numpy matplotlib

# Run the demo
python examples/data_collection_demo.py
```

**What you get:**
- Historical data for backtesting
- Daily OHLC data (can go down to 1-minute)
- Commodities: Gold, Silver, Crude Oil
- Indices: Nifty 50, Bank Nifty
- NSE Stocks: Any stock with .NS suffix

**Limitations:**
- 15-20 min delay (not true real-time)
- No tick-by-tick data
- Cannot set broker alerts

---

### Phase 2: PAID - Live Trading (After Strategy is Proven)
**Cost:** ₹2000/month (Zerodha Kite Connect subscription)  
**Purpose:** Real-time tick data and broker integration

**Prerequisites:**
1. Active Zerodha trading account
2. Subscribe to Kite Connect API at https://kite.trade/
3. Get API credentials (key, secret)

**Setup:**
```bash
# Install Zerodha library
pip install kiteconnect

# Create .env file
echo "KITE_API_KEY=your_key_here" >> .env
echo "KITE_API_SECRET=your_secret_here" >> .env
echo "KITE_ACCESS_TOKEN=your_token_here" >> .env
```

**What you get:**
- True tick-by-tick data (WebSocket streaming)
- All NSE, MCX instruments
- Historical data API
- Integration with Zerodha GTT (Good Till Triggered) orders
- Set alerts at support/resistance levels
- Broker sends notifications

---

## 🚀 Getting Started (FREE - No API Keys Needed)

### Step 1: Install Dependencies
```bash
cd /Users/lsurana/trading-system
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Step 2: Test Data Collection
```python
from data.collectors import FreeDataCollector
from datetime import datetime, timedelta

# Initialize collector
collector = FreeDataCollector()

# Get last 30 days of Gold data
data = collector.get_historical_data(
    symbol='GOLD',
    start_date=datetime.now() - timedelta(days=30),
    end_date=datetime.now(),
    interval='1d'
)

print(data.tail())
```

### Step 3: Fetch Multiple Instruments
```python
# Get data for multiple instruments
instruments = ['GOLD', 'SILVER', 'CRUDE_WTI', 'NIFTY50']
data = collector.get_multiple_symbols(
    symbols=instruments,
    start_date=datetime.now() - timedelta(days=30),
    end_date=datetime.now()
)

for symbol, df in data.items():
    print(f"{symbol}: {len(df)} rows")
```

### Step 4: Get NSE Stocks
```python
# NSE stocks (add .NS suffix)
nse_stocks = ['RELIANCE', 'TCS', 'INFY', 'HDFCBANK']
nse_data = collector.get_nse_stocks(
    symbols=nse_stocks,
    start_date=datetime.now() - timedelta(days=7),
    end_date=datetime.now()
)
```

---

## 📝 Symbol Reference

### Commodities (via yfinance)
| Instrument | Symbol Code | Yahoo Symbol |
|------------|-------------|--------------|
| Gold Futures | `GOLD` | `GC=F` |
| Silver Futures | `SILVER` | `SI=F` |
| WTI Crude Oil | `CRUDE_WTI` | `CL=F` |
| Brent Crude Oil | `CRUDE_BRENT` | `BZ=F` |

### Indices
| Instrument | Symbol Code | Yahoo Symbol |
|------------|-------------|--------------|
| Nifty 50 | `NIFTY50` | `^NSEI` |
| Bank Nifty | `BANKNIFTY` | `^NSEBANK` |
| Sensex | `SENSEX` | `^BSESN` |

### NSE Stocks
Add `.NS` suffix to stock symbol:
- `RELIANCE.NS` - Reliance Industries
- `TCS.NS` - Tata Consultancy Services
- `INFY.NS` - Infosys
- `HDFCBANK.NS` - HDFC Bank

---

## 🎪 Live Demo

Run the complete demo:
```bash
cd /Users/lsurana/trading-system
python examples/data_collection_demo.py
```

This will:
1. Fetch 30 days of commodity and index data
2. Display latest prices
3. Show NSE stock data
4. Explain Kite API setup

---

## 🔄 When to Upgrade to Zerodha API?

Upgrade when:
1. ✅ Your strategy shows consistent profitability in backtests
2. ✅ You've validated signals on at least 3-6 months of historical data
3. ✅ You understand the risk management
4. ✅ You're ready to trade with real money

**Don't upgrade if:**
- ❌ Still developing/testing strategy
- ❌ Haven't validated signals
- ❌ Not trading yet

---

## 📖 Next Steps

1. **Test data collection** - Run the demo script
2. **Build signal logic** - Create support/resistance detection
3. **Backtest signals** - Validate on historical data
4. **Calculate metrics** - Sharpe ratio, win rate, drawdown
5. **When ready** - Subscribe to Kite API and go live

---

## 🆘 Common Issues

### Issue: "No module named 'yfinance'"
```bash
pip install yfinance
```

### Issue: "No data available for symbol"
- Check symbol format (use `.NS` for NSE stocks)
- Try different date range
- Check if market was open on those dates

### Issue: "Want tick-by-tick data NOW"
- Free sources don't offer true tick data
- Minimum granularity: 1 minute
- For tick data, need Zerodha subscription

---

## 💡 Pro Tips

1. **Cache data locally** - Don't fetch same data repeatedly
2. **Respect rate limits** - yfinance has limits, add delays between requests
3. **Use appropriate intervals** - Daily for long-term, 1-min for intraday
4. **Start simple** - Test with 1-2 instruments first
5. **Validate data quality** - Check for gaps, outliers

---

## 📞 Resources

- **yfinance docs**: https://pypi.org/project/yfinance/
- **Kite Connect docs**: https://kite.trade/docs/pykiteconnect/v4/
- **Zerodha API pricing**: https://kite.trade/pricing
- **Data sources comparison**: See `data/DATA_SOURCES.md`
