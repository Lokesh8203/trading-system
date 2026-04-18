

# NSE Sectoral & Custom Indices Guide

## Overview

This module provides comprehensive index tracking for NSE markets to identify sector-specific trading opportunities. Beyond standard indices like Nifty 50 and Bank Nifty, we track:

- **40+ Sectoral Indices** (Auto, Pharma, IT, Metal, etc.)
- **10+ Custom Indices** (Chemicals, Defense, Renewables, Digital Economy, etc.)
- **Thematic Indices** (Quality, Alpha, Low Volatility, Dividend)
- **Relative Strength Analysis** (Sector rotation detection)
- **Breadth Metrics** (Market health indicators)

---

## Why Track Sectoral Indices?

### 1. **Sector Rotation Opportunities**
Markets don't move uniformly. Different sectors lead at different times:
- **Bull Market Early**: Cyclicals lead (Auto, Real Estate, Capital Goods)
- **Bull Market Late**: Defensives lead (FMCG, Pharma, IT)
- **Bear Market**: Quality, Low Volatility outperform

### 2. **Better Stock Selection**
- Trade stocks in **leading sectors** (tailwind)
- Avoid stocks in **lagging sectors** (headwind)
- Even mediocre stock in strong sector > great stock in weak sector

### 3. **Risk Management**
- Diversification across uncorrelated sectors
- Hedge positions (long IT, short Metal if inverse correlation)
- Reduce portfolio volatility

### 4. **Early Trend Detection**
- Sector indices turn before individual stocks
- Identify rotation before it's obvious
- Position ahead of the crowd

---

## Available Indices

### Standard NSE Indices (18)

| Category | Indices |
|----------|---------|
| **Broad Market** | Nifty 50, Nifty 100, Nifty 200, Nifty 500, Nifty Next 50 |
| **Market Cap** | Nifty Midcap 50/100, Nifty Smallcap 100 |
| **Banking** | Bank Nifty, Nifty PSU Bank, Nifty Pvt Bank |
| **Financial** | Nifty Financial Services |

### Official Sectoral Indices (15)

| Sector | Index |
|--------|-------|
| Auto | Nifty Auto |
| Pharma | Nifty Pharma |
| IT | Nifty IT |
| FMCG | Nifty FMCG |
| Metal | Nifty Metal |
| Realty | Nifty Realty |
| Energy | Nifty Energy |
| Media | Nifty Media |
| Infrastructure | Nifty Infrastructure |
| Commodities | Nifty Commodities |
| Consumption | Nifty India Consumption |
| Oil & Gas | Nifty Oil & Gas |
| Healthcare | Nifty Healthcare |

### Custom Indices (10+)

We've built custom indices for sectors not covered by NSE:

| Index | Sector | Why Important |
|-------|--------|---------------|
| **Nifty Chemicals (Custom)** | Chemicals | Specialty chemicals booming, China+1 theme |
| **Nifty Defense (Custom)** | Defense | Government focus on Make in India defense |
| **Nifty Renewables (Custom)** | Green Energy | Renewable energy transition theme |
| **Nifty Digital (Custom)** | Digital Economy | E-commerce, fintech, digital services growth |
| **Nifty Logistics (Custom)** | Logistics | E-commerce driving logistics boom |
| **Nifty Textiles (Custom)** | Textiles | Export opportunity, PLI schemes |
| **Nifty Retail (Custom)** | Organized Retail | Shift from unorganized to organized retail |
| **Nifty Capital Goods (Custom)** | Engineering | Infrastructure spending, capex cycle |
| **Nifty PSU (Custom)** | PSU (non-bank) | Government disinvestment, value unlocking |
| **Nifty Tourism (Custom)** | Hotels/Travel | Post-pandemic recovery theme |

### Thematic Indices (5)

| Index | Theme |
|-------|-------|
| Nifty Alpha 50 | High risk-adjusted returns |
| Nifty Quality 30 | High ROE, low debt companies |
| Nifty Low Volatility 50 | Stable, low-volatility stocks |
| Nifty Dividend Opportunities | High dividend yield |
| Nifty Growth Sectors 15 | High-growth potential sectors |

---

## How to Use

### 1. Quick Sector Scan

```python
from data.collectors import IndexCollector

collector = IndexCollector()

# Scan all core sectors (last 30 days)
scan = collector.scan_sectoral_strength(lookback_days=30)
print(scan)
```

**Output:**
```
Index                    Sector            Returns_%    RS    RS_Momentum  Strength
NIFTY_IT                IT                8.5          105.2  True         Strong
NIFTY_AUTO              Auto              6.2          102.1  True         Strong
NIFTY_PHARMA            Pharma            3.1          98.5   False        Moderate
NIFTY_METAL             Metal             -2.3         94.2   False        Weak
```

### 2. Find Rotation Opportunities

```python
# Identify which sectors to trade
rotation = collector.find_rotation_opportunities(lookback_days=30)

# Leaders: Buy/hold these sectors
print("Leaders:", rotation['leaders'])

# Weakening: Consider booking profits
print("Weakening:", rotation['weakening'])

# Avoid: Stay away
print("Avoid:", rotation['avoid'])
```

### 3. Relative Strength Analysis

```python
# Compare IT sector vs Nifty 50
rs_data = collector.calculate_relative_strength(
    index_symbol='NIFTY_IT',
    benchmark_symbol='NIFTY50',
    start_date=datetime.now() - timedelta(days=90),
    end_date=datetime.now()
)

# RS > 100: Outperforming
# RS < 100: Underperforming
latest_rs = rs_data.iloc[-1]['RS']
print(f"IT Relative Strength: {latest_rs}")
```

### 4. Custom Index Data

```python
# Get data for custom chemicals index
chem_data = collector.get_index_data(
    'NIFTY_CHEMICALS_CUSTOM',
    start_date=datetime.now() - timedelta(days=30),
    end_date=datetime.now()
)

# Calculate returns
returns = ((chem_data.iloc[-1]['Close'] - chem_data.iloc[0]['Close']) / 
           chem_data.iloc[0]['Close']) * 100

print(f"Chemicals Sector Returns: {returns:.2f}%")
```

### 5. Use Watchlists

Predefined watchlists for common analysis:

```python
# Primary watchlist (main indices)
data = collector.get_watchlist_data('primary', days=30)

# Sectoral rotation (all core sectors)
data = collector.get_watchlist_data('sectoral_rotation', days=30)

# Emerging themes (new opportunity sectors)
data = collector.get_watchlist_data('emerging_themes', days=30)
```

**Available Watchlists:**
- `primary`: Nifty 50, Bank Nifty, IT, Auto, Pharma, Metal
- `sectoral_rotation`: All 8 core sectors
- `emerging_themes`: Chemicals, Defense, Renewables, Digital, Logistics
- `volatility_play`: Large cap, Mid cap, Small cap, Low Vol
- `quality_focus`: Quality 30, Alpha 50, Dividend
- `all_sectoral`: All NSE sectoral indices
- `all_custom`: All custom indices

---

## Trading Strategies Using Indices

### Strategy 1: Sector Rotation

**Concept:** Trade stocks in leading sectors, avoid lagging sectors

**Steps:**
1. Run weekly sector scan
2. Identify top 3 strongest sectors (RS > 100, positive momentum)
3. Select 2-3 best stocks from each strong sector
4. Enter long positions
5. Exit when sector moves to "weakening" category

**Entry Rules:**
- Sector RS > 102 (clear outperformance)
- Sector returns > Nifty 50 returns
- RS momentum positive (RS > RS MA)
- Pick stocks outperforming sector index

**Exit Rules:**
- Sector RS falls below 98
- Sector returns turn negative
- RS momentum turns negative

### Strategy 2: Pair Trading (Long/Short)

**Concept:** Long strong sector, short weak sector

**Steps:**
1. Find highest RS sector (Leader)
2. Find lowest RS sector (Laggard)
3. Long stocks in leader sector
4. Short stocks in laggard sector
5. Close when RS differential narrows

**Example:**
- Long: NIFTY_IT (RS = 108, strong momentum)
- Short: NIFTY_METAL (RS = 92, weak momentum)
- Close when RS gap < 10 points

### Strategy 3: Mean Reversion (Laggard Recovery)

**Concept:** Buy underperforming sectors showing early recovery signs

**Entry:**
- Sector RS < 95 (underperforming)
- But recent RS momentum turning positive
- Volume increasing on up days
- Support holding
- = Laggard starting to recover

**Target:** RS reaches 100 (catches up to market)

### Strategy 4: Breadth Divergence

**Concept:** Use custom index breadth to detect sector tops/bottoms

**For Custom Indices:**
```python
breadth = collector.calculate_breadth(
    'NIFTY_CHEMICALS_CUSTOM',
    start_date, end_date
)

# Bullish: Breadth > 70% (most stocks above 50 MA)
# Bearish: Breadth < 30% (most stocks below 50 MA)
```

**Trading:**
- **Breadth > 70% + Sector strong**: Continue holding
- **Breadth < 30% + Sector weak**: Avoid or short
- **Breadth improving from < 30%**: Early accumulation signal
- **Breadth declining from > 70%**: Distribution warning

### Strategy 5: Multi-Sector Confirmation

**Concept:** Trade Nifty 50 only when sectors agree

**Rules:**
```python
sectors = ['NIFTY_AUTO', 'NIFTY_IT', 'NIFTY_PHARMA', 'NIFTY_METAL']

# Count sectors with RS > 100
strong_sectors = sum(1 for s in sectors if get_rs(s) > 100)

if strong_sectors >= 3:
    # Broad-based rally, safe to trade Nifty long
elif strong_sectors <= 1:
    # Narrow rally, stay cautious or short
```

---

## Sector Characteristics

### Cyclical Sectors (Economy-Sensitive)

**High Beta, Lead in Bull Markets:**
- **Auto**: Consumer spending indicator
- **Real Estate**: Credit cycle, interest rates
- **Metal**: Global commodity demand
- **Capital Goods**: Capex cycle
- **Infrastructure**: Government spending

**Trade:** Buy early in economic recovery, sell before peak

### Defensive Sectors (Recession-Resistant)

**Low Beta, Outperform in Bear Markets:**
- **FMCG**: Essential goods, stable demand
- **Pharma**: Healthcare spending continues
- **Utilities**: Power, essential services

**Trade:** Rotate into during market uncertainty

### Growth Sectors

**Secular Growth, Less Cyclical:**
- **IT**: Continuous digital transformation
- **Digital Economy**: Structural shift to online
- **Healthcare**: Aging population, rising incomes

**Trade:** Long-term holds with occasional profit-booking

### Emerging Themes (High Growth Potential)

**New Opportunities:**
- **Defense**: Make in India, geopolitics
- **Renewables**: Energy transition
- **Chemicals**: China+1, specialty chemicals boom
- **Logistics**: E-commerce infrastructure

**Trade:** Early positioning, ride the theme

---

## Index Groups for Analysis

Pre-configured groups for specific analysis:

```python
from data.indices.nse_indices_config import get_index_group

# Broad market indices
broad = get_index_group('broad_market')

# Market cap segments
midcaps = get_index_group('market_cap')

# Core sectors
core = get_index_group('core_sectors')

# Banking/Financial
banking = get_index_group('banking_financial')

# Emerging sectors
emerging = get_index_group('emerging_sectors')

# Cyclical sectors
cyclical = get_index_group('cyclical')

# Defensive sectors
defensive = get_index_group('defensive')

# All custom indices
custom = get_index_group('custom_all')
```

---

## Sector Correlation Matrix

Understanding sector relationships:

| Sector 1 | Sector 2 | Correlation | Implication |
|----------|----------|-------------|-------------|
| Auto | Metal | +0.7 | Positive (auto uses metal) |
| IT | INR/USD | -0.6 | Negative (strong rupee hurts IT exports) |
| Pharma | Market | +0.3 | Low (relatively independent) |
| Banking | Interest Rates | +0.5 | Positive (higher rates help banks initially) |
| FMCG | Rural Demand | +0.6 | Positive (rural consumption driver) |
| Real Estate | Interest Rates | -0.7 | Negative (high rates hurt demand) |

**Hedging Examples:**
- Long Auto + Short Metal = Reduce correlation
- Long IT + Short Bank Nifty = Currency hedge
- Long Pharma + Long FMCG = Defensive basket

---

## Best Practices

### 1. **Weekly Sector Review**
- Every Sunday, scan all sectors
- Note top 3 and bottom 3
- Track rotation over 4-8 weeks
- Position accordingly

### 2. **Combine with Stock Selection**
- First: Identify strong sector (index level)
- Then: Pick strong stocks within sector
- = Confluence of sector + stock strength

### 3. **Use Multiple Timeframes**
- **Daily**: Intraday sector moves
- **Weekly**: Swing trading sectors
- **Monthly**: Long-term sector trends

### 4. **Don't Fight Sector Trend**
- Even great stock in weak sector struggles
- Average stock in strong sector can outperform
- **Sector momentum > Stock fundamentals (short-term)**

### 5. **Watch for Divergences**
- Sector making new highs, but breadth declining = Warning
- Sector bottoming, but breadth improving = Accumulation
- Price divergence from RS = Reversal signal

### 6. **Monitor Emerging Custom Indices**
- Chemicals, Defense, Renewables = Structural themes
- Can provide 2-5 year trends
- Early positioning = maximum returns

---

## Quick Reference: Index Symbols

### Most Watched

```python
# Primary
'NIFTY50', 'BANKNIFTY'

# Core Sectors
'NIFTY_IT', 'NIFTY_AUTO', 'NIFTY_PHARMA', 
'NIFTY_METAL', 'NIFTY_FMCG', 'NIFTY_ENERGY'

# Emerging Custom
'NIFTY_CHEMICALS_CUSTOM', 'NIFTY_DEFENSE_CUSTOM',
'NIFTY_RENEWABLES_CUSTOM', 'NIFTY_DIGITAL_CUSTOM'

# Thematic
'NIFTY_ALPHA50', 'NIFTY_QUALITY30', 'NIFTY_LOW_VOL50'
```

### For Rotation Analysis

```python
rotation_set = [
    'NIFTY_AUTO',       # Cyclical
    'NIFTY_METAL',      # Cyclical
    'NIFTY_REALTY',     # Cyclical
    'NIFTY_CAPGOODS_CUSTOM',  # Cyclical
    
    'NIFTY_IT',         # Growth
    'NIFTY_PHARMA',     # Defensive
    'NIFTY_FMCG',       # Defensive
    
    'NIFTY_CHEMICALS_CUSTOM',  # Emerging
    'NIFTY_DEFENSE_CUSTOM',    # Emerging
]
```

---

## Example: Complete Workflow

```python
from data.collectors import IndexCollector
from datetime import datetime, timedelta

# Initialize
collector = IndexCollector()

# Step 1: Sector Strength Scan
print("="*70)
print("WEEKLY SECTOR SCAN")
print("="*70)
scan = collector.scan_sectoral_strength(lookback_days=30)
print(scan)

# Step 2: Identify Rotation
rotation = collector.find_rotation_opportunities(lookback_days=30)

print("\n🟢 LEADERS (Trade these):")
for idx in rotation['leaders']:
    print(f"  - {idx}")

print("\n🔴 AVOID (Skip these):")
for idx in rotation['avoid']:
    print(f"  - {idx}")

# Step 3: Deep Dive into Leader
leader = rotation['leaders'][0]  # Top leader
print(f"\n📊 ANALYZING: {leader}")

# Get RS
rs_data = collector.calculate_relative_strength(
    leader, 'NIFTY50',
    datetime.now() - timedelta(days=60),
    datetime.now()
)

print(f"  Current RS: {rs_data.iloc[-1]['RS']:.2f}")
print(f"  RS Momentum: {rs_data.iloc[-1]['RS_Momentum']}")

# Get constituent stocks (if custom index)
config = get_index_config(leader)
if config.is_custom and config.constituents:
    print(f"\n  Top Stocks in {leader}:")
    for stock in config.constituents[:5]:
        print(f"    - {stock}")

# Step 4: Set Alerts
print("\n🔔 ALERTS TO SET:")
print(f"  - Alert if {leader} RS falls below 100")
print(f"  - Alert if {leader} returns turn negative")
print(f"  - Alert if breadth falls below 50%")

print("\n✅ Analysis Complete!")
```

---

## Advanced: Building Your Own Custom Index

To add a new custom index:

1. **Open:** `data/indices/nse_indices_config.py`

2. **Add to CUSTOM_INDICES:**

```python
'YOUR_INDEX_NAME': IndexConfig(
    name='Display Name',
    symbol='YOUR_INDEX_NAME',
    sector='Your Sector',
    description='Description of index',
    is_custom=True,
    constituents=[
        'STOCK1.NS',
        'STOCK2.NS',
        'STOCK3.NS',
        # ... more stocks
    ]
),
```

3. **Use immediately:**

```python
data = collector.get_index_data('YOUR_INDEX_NAME', start, end)
```

**Example Custom Indices You Can Build:**
- EV/Battery sector
- Semiconductor/Electronics
- Fintech companies
- Wealth management/Brokers
- Agri-commodities
- Export-oriented companies

---

## Troubleshooting

### Issue: Custom index shows no data
**Solution:** Check if constituent stock symbols are correct (should end with `.NS`)

### Issue: RS calculation returns empty
**Solution:** Ensure both index and benchmark have data for the date range

### Issue: Yahoo symbol not found for standard index
**Solution:** Some NSE indices may not be on Yahoo Finance. Custom calculation may be needed.

### Issue: Constituent stocks not updating
**Solution:** Stock may have been delisted or symbol changed. Update constituents list.

---

## Resources

- **NSE Indices:** https://www.niftyindices.com/
- **Index Methodology:** Check NSE website for constituent methodology
- **Rebalancing:** NSE indices rebalance semi-annually (check official dates)
- **Thematic Reports:** NSE publishes thematic index reports

---

## Summary

✅ Track 40+ indices (standard + custom)  
✅ Identify sector rotation opportunities  
✅ Calculate relative strength vs benchmarks  
✅ Use breadth metrics for timing  
✅ Pre-built watchlists for quick analysis  
✅ Trade with sector tailwinds  

**Next Steps:**
1. Run weekly sector scan
2. Identify 2-3 strongest sectors
3. Select best stocks from those sectors
4. Monitor rotation continuously
5. Adjust portfolio as sectors rotate

---

**Happy Trading! 🚀**
