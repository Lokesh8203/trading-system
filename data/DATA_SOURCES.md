# Data Sources for Indian Markets

## Summary of Findings

### Your Existing Repos
1. **kite-scanner** - Abandoned/early stage, no usable code
2. **nselib** - Functional NSE data scraper (free, no API key needed)
3. **pykiteconnect** - Fork of official library, use official version instead

### Recommended Data Strategy

## 1. Real-Time Tick Data (Zerodha KiteConnect)

**What:** WebSocket streaming for live market data
**Cost:** Requires Zerodha trading account (₹2000 monthly Kite Connect API subscription)
**Instruments:** NSE, MCX (Gold, Silver, Crude), NFO
**Limitations:** 
- Need active API subscription
- Rate limits apply (not documented publicly)
- GIFT Nifty not directly available

**Use For:** Real-time signal generation and alert triggers

## 2. Historical Data - FREE Sources

### A. NSE Stocks (NSE500)
**Source:** nselib (your fork or original)
- Free, no API key needed
- Scrapes NSE website
- Capital market + derivatives data
- **Limitation:** May break if NSE changes website structure

### B. Global Commodities & Indices
**Source:** yfinance (Yahoo Finance)
```python
# International commodities tradable in India
WTI Crude: "CL=F"
Brent Crude: "BZ=F"  
Gold: "GC=F"
Silver: "SI=F"
Nifty 50: "^NSEI"
```
**Limitation:** Not tick-by-tick, 1-min minimum granularity

### C. MCX Commodities (Gold, Silver, Crude)
**Source:** Option 1 - Zerodha Historical API (requires subscription)
**Source:** Option 2 - NSE/MCX Website scraping (free but unreliable)

## 3. GIFT Nifty
**Challenge:** Not available on standard free APIs
**Options:**
- Scrape from NSE/SGX websites (unreliable)
- Use Nifty 50 as proxy for strategy development
- Wait for Zerodha API subscription

## Recommended Approach

### Phase 1: Development & Backtesting (FREE)
1. Use **nselib** for NSE500 stocks historical data
2. Use **yfinance** for commodities proxies (GC=F for gold, etc.)
3. Build and test signal logic without real-time data
4. Calculate support/resistance on historical data

### Phase 2: Live Trading (Paid - Zerodha Required)
1. Subscribe to Zerodha Kite Connect API (₹2000/month)
2. Use **KiteTicker WebSocket** for real-time ticks
3. Trigger signal calculations on-demand
4. Set alerts via Zerodha GTT (Good Till Triggered) orders
5. Receive notifications and trade manually

## Data Collection Architecture

```
┌─────────────────────────────────────────┐
│         Historical Backtesting          │
│  (nselib + yfinance) - FREE             │
└─────────────────┬───────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────┐
│    Signal Logic Development             │
│    Support/Resistance Calculation       │
└─────────────────┬───────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────┐
│   Live Data Collection                  │
│   (KiteTicker WebSocket) - PAID         │
│   - On-demand trigger                   │
│   - Key level monitoring                │
└─────────────────┬───────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────┐
│   Alert System (Zerodha GTT)            │
│   - Broker handles notifications        │
│   - Manual trade execution              │
└─────────────────────────────────────────┘
```

## Cost Analysis

**Option 1: FREE (Development Only)**
- Historical data: FREE
- Strategy development: FREE
- Cannot trade live or get real-time alerts

**Option 2: Zerodha API (Live Trading)**
- API subscription: ₹2000/month
- Real-time data: Included
- GTT orders: FREE (built into broker)
- Historical data: Included

**Recommendation:** Start with Option 1, switch to Option 2 when strategy is proven.
