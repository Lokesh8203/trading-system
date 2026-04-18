# Professional Stock Signal Generation Framework
## Multi-Faceted Weighted Scoring System

**Goal:** Generate high-quality buy signals for stocks that filter out noise, avoid illiquid stocks, and identify moves with defined risk BEFORE they're played out.

**Philosophy:** Signal generation only (no trade execution) - focused on finding the RIGHT stocks at the RIGHT time with proper RISK defined.

---

## 🎯 The Problem with Existing Screeners

### **ChartInk Screeners Analysis (By Name):**

1. **Mark Minervini Momentum - Stage 2** 
   - ✅ Good: Stage 2 focus (trending stocks)
   - ❌ Problem: Often catches late moves, no liquidity filter

2. **Stage 1 to Stage 2 Scanner**
   - ✅ Good: Early entry (transition point)
   - ❌ Problem: False breakouts common, no volume confirmation

3. **Trend Template for Momentum Stocks**
   - ✅ Good: Momentum confirmation
   - ❌ Problem: Generic, catches both early and late moves

4. **Weekly Bottomed Out - Trend Turning**
   - ✅ Good: Reversal at support
   - ❌ Problem: Knife-catching risk, weak stocks included

5. **Ankur's Volume Scan**
   - ✅ Good: Volume focus (institutional activity)
   - ❌ Problem: Volume spikes alone insufficient

### **Common Issues:**
- ❌ No liquidity filtering (penny stocks included)
- ❌ No fundamental quality checks
- ❌ Catching moves too late (already extended)
- ❌ No risk definition (where's the stop?)
- ❌ No sectoral context (sector weak = stock struggles)
- ❌ Equal weight to all signals (no scoring)

---

## ✅ Our Solution: Multi-Faceted Weighted Scoring System

### **Concept:**
Each stock gets a **composite score (0-100)** based on multiple factors with different weights. Only stocks scoring **70+** generate signals.

### **Five Pillars:**

```
┌─────────────────────────────────────────────────────┐
│           STOCK SIGNAL SCORE (0-100)                │
├─────────────────────────────────────────────────────┤
│ 1. STAGE ANALYSIS        (30 points) - Trend phase  │
│ 2. TECHNICAL SETUP       (25 points) - Entry timing │
│ 3. FUNDAMENTAL QUALITY   (20 points) - Company     │
│ 4. LIQUIDITY & TRADE     (15 points) - Tradability  │
│ 5. SECTORAL STRENGTH     (10 points) - Tailwind     │
└─────────────────────────────────────────────────────┘
```

---

## 📊 PILLAR 1: Stage Analysis (30 points)

**Purpose:** Identify stocks in the right trend phase (Stage 2 early)

### **Scoring:**

#### **Stage 2 Confirmation (15 points max)**
```python
# All must be TRUE for full points
conditions = {
    'price_above_200ma': 5 points,      # Uptrend confirmed
    '200ma_rising': 5 points,            # MA slope positive
    'higher_highs_lows': 5 points        # Trend structure intact
}

# Deductions:
if price < 150ma: -3 points  # Too close to breakdown
if 200ma flat: -3 points     # Weak trend
```

#### **Stage Position (10 points max)**
```python
# Where in Stage 2 are we?
percent_above_200ma = (price - ma_200) / ma_200 * 100

if percent_above_200ma < 5%:
    stage_position_score = 10  # BEST - Just entered Stage 2
elif percent_above_200ma < 15%:
    stage_position_score = 8   # GOOD - Early Stage 2
elif percent_above_200ma < 30%:
    stage_position_score = 5   # OK - Mid Stage 2
elif percent_above_200ma < 50%:
    stage_position_score = 2   # LATE - Extended
else:
    stage_position_score = 0   # TOO LATE - Avoid
```

#### **Distance from Recent Base (5 points max)**
```python
# How far from breakout?
bars_since_breakout = count_bars_since_base_breakout()

if bars_since_breakout < 10:
    base_score = 5   # BEST - Fresh breakout
elif bars_since_breakout < 30:
    base_score = 3   # OK - Some momentum left
else:
    base_score = 0   # TOO LATE - Already extended
```

**Total Stage Score:** 0-30 points

---

## 📊 PILLAR 2: Technical Setup (25 points)

**Purpose:** Identify specific entry patterns with defined risk

### **Scoring:**

#### **Primary Setup Present (15 points max)**

Choose ONE of your favorite setups:

**A. Narrow Range Consolidation (NR7/NR4)**
```python
# 7-day consolidation with tight range
if has_nr7_pattern():
    setup_score = 15
    risk_defined = True
    stop_loss = low_of_consolidation - (0.02 * price)
    
elif has_nr4_pattern():
    setup_score = 12
    risk_defined = True
    stop_loss = low_of_consolidation - (0.02 * price)
else:
    setup_score = 0
```

**B. 200 EMA Pullback**
```python
# Price pulled back to 200 EMA and holding
if price_near_200ema(tolerance=2%) and price > 200ema:
    if bullish_reversal_candle():
        setup_score = 15
        risk_defined = True
        stop_loss = 200ema - (ATR * 1.5)
    else:
        setup_score = 10  # Setup forming, wait for confirmation
else:
    setup_score = 0
```

**C. Base Breakout (Cup, VCP, Flat)**
```python
# Clean base with breakout on volume
if base_breakout_detected():
    base_depth = (base_high - base_low) / base_high
    base_length = days_in_base()
    
    if base_length >= 30 and base_depth < 0.25 and volume > avg_volume * 1.5:
        setup_score = 15
        risk_defined = True
        stop_loss = base_breakout_level * 0.92  # 8% below breakout
    else:
        setup_score = 8  # Weak base
else:
    setup_score = 0
```

#### **Volume Confirmation (5 points max)**
```python
# Volume must support the move
recent_volume = avg_volume_last_5_days()
avg_volume_50 = avg_volume_last_50_days()

volume_ratio = recent_volume / avg_volume_50

if volume_ratio > 1.5:
    volume_score = 5   # Strong institutional interest
elif volume_ratio > 1.2:
    volume_score = 3   # Moderate interest
else:
    volume_score = 0   # Weak volume - skip
```

#### **Relative Strength (5 points max)**
```python
# Stock vs Nifty 50 performance
rs_3month = (stock_return_3m - nifty_return_3m)

if rs_3month > 15%:
    rs_score = 5   # Strong outperformance
elif rs_3month > 5%:
    rs_score = 3   # Moderate outperformance
elif rs_3month > 0%:
    rs_score = 1   # Slight outperformance
else:
    rs_score = 0   # Underperforming - avoid
```

**Total Technical Score:** 0-25 points

---

## 📊 PILLAR 3: Fundamental Quality (20 points)

**Purpose:** Filter out weak companies, focus on quality

### **Scoring:**

#### **Growth (8 points max)**
```python
# Sales and Profit Growth (YoY last 2 quarters avg)
sales_growth_yoy = avg_sales_growth_last_2q()
profit_growth_yoy = avg_profit_growth_last_2q()

# Sales Growth
if sales_growth_yoy > 20%:
    sales_score = 4
elif sales_growth_yoy > 10%:
    sales_score = 3
elif sales_growth_yoy > 0%:
    sales_score = 1
else:
    sales_score = 0  # Declining sales - avoid

# Profit Growth
if profit_growth_yoy > 25%:
    profit_score = 4
elif profit_growth_yoy > 15%:
    profit_score = 3
elif profit_growth_yoy > 0%:
    profit_score = 1
else:
    profit_score = 0  # Declining profits - avoid

growth_score = sales_score + profit_score  # 0-8 points
```

#### **Profitability (6 points max)**
```python
# ROE and Operating Margins
roe = return_on_equity()
operating_margin = operating_profit / revenue

# ROE
if roe > 20%:
    roe_score = 3
elif roe > 15%:
    roe_score = 2
elif roe > 10%:
    roe_score = 1
else:
    roe_score = 0

# Operating Margin
if operating_margin > 0.20:
    margin_score = 3
elif operating_margin > 0.12:
    margin_score = 2
elif operating_margin > 0.08:
    margin_score = 1
else:
    margin_score = 0

profitability_score = roe_score + margin_score  # 0-6 points
```

#### **Financial Health (6 points max)**
```python
# Debt and Cash Flow
debt_to_equity = total_debt / total_equity
operating_cf = operating_cash_flow_ttm()

# Debt
if debt_to_equity < 0.5:
    debt_score = 3  # Low debt
elif debt_to_equity < 1.0:
    debt_score = 2  # Moderate debt
elif debt_to_equity < 2.0:
    debt_score = 1  # High debt
else:
    debt_score = 0  # Very high debt - risky

# Cash Flow
if operating_cf > 0 and operating_cf_growing():
    cf_score = 3  # Strong and growing
elif operating_cf > 0:
    cf_score = 2  # Positive but flat
else:
    cf_score = 0  # Negative - avoid

financial_health_score = debt_score + cf_score  # 0-6 points
```

**Total Fundamental Score:** 0-20 points

---

## 📊 PILLAR 4: Liquidity & Tradeability (15 points)

**Purpose:** Filter out illiquid, penny stocks and already-extended moves

### **Scoring:**

#### **Liquidity (8 points max)**
```python
# Average Daily Volume and Value
avg_daily_volume = avg_volume_last_30_days()
avg_daily_value = avg_daily_volume * current_price

# Volume
if avg_daily_volume > 1_000_000:
    volume_liquidity_score = 4  # Highly liquid
elif avg_daily_volume > 500_000:
    volume_liquidity_score = 3  # Adequate
elif avg_daily_volume > 100_000:
    volume_liquidity_score = 1  # Low liquidity
else:
    volume_liquidity_score = 0  # Illiquid - avoid

# Value traded
if avg_daily_value > 50_000_000:  # ₹5 Cr
    value_liquidity_score = 4  # Institutional grade
elif avg_daily_value > 10_000_000:  # ₹1 Cr
    value_liquidity_score = 3  # Adequate
elif avg_daily_value > 5_000_000:   # ₹50 L
    value_liquidity_score = 1  # Low
else:
    value_liquidity_score = 0  # Too illiquid

liquidity_score = volume_liquidity_score + value_liquidity_score  # 0-8
```

#### **Price Level (3 points max)**
```python
# Avoid penny stocks
if price > 500:
    price_score = 3  # Blue chip range
elif price > 100:
    price_score = 2  # Mid cap range
elif price > 50:
    price_score = 1  # Small cap acceptable
else:
    price_score = 0  # Penny stock - avoid
```

#### **Market Cap (4 points max)**
```python
market_cap = shares_outstanding * current_price

if market_cap > 50_000_00_00_000:  # ₹50,000 Cr (Large cap)
    mcap_score = 4
elif market_cap > 10_000_00_00_000:  # ₹10,000 Cr (Mid cap)
    mcap_score = 3
elif market_cap > 5_000_00_00_000:   # ₹5,000 Cr (Small cap)
    mcap_score = 2
else:
    mcap_score = 0  # Micro cap - too risky
```

**Total Liquidity Score:** 0-15 points

---

## 📊 PILLAR 5: Sectoral Strength (10 points)

**Purpose:** Trade stocks in strong sectors (tailwind)

### **Scoring:**

```python
# Using your sectoral index tracking system
sector = get_stock_sector(stock_symbol)
sector_rs = get_sector_relative_strength(sector, benchmark='NIFTY50')
sector_momentum = sector_rs > sector_rs_ma_20

# Sector RS
if sector_rs > 105:
    sector_rs_score = 5  # Strong sector
elif sector_rs > 100:
    sector_rs_score = 4  # Outperforming
elif sector_rs > 95:
    sector_rs_score = 2  # Neutral
else:
    sector_rs_score = 0  # Weak sector - avoid

# Sector Momentum
if sector_momentum:
    momentum_score = 3  # Sector accelerating
else:
    momentum_score = 0  # Sector weakening

# Stock vs Sector
stock_vs_sector = stock_return_3m - sector_return_3m
if stock_vs_sector > 5%:
    relative_score = 2  # Stock leading sector
elif stock_vs_sector > 0%:
    relative_score = 1  # In line with sector
else:
    relative_score = 0  # Lagging sector

sectoral_score = sector_rs_score + momentum_score + relative_score  # 0-10
```

**Total Sectoral Score:** 0-10 points

---

## 🎯 COMPOSITE SIGNAL GENERATION

### **Final Score Calculation:**

```python
total_score = (
    stage_score +           # 0-30 points
    technical_score +       # 0-25 points
    fundamental_score +     # 0-20 points
    liquidity_score +       # 0-15 points
    sectoral_score          # 0-10 points
)

# Maximum possible: 100 points
```

### **Signal Strength:**

```python
if total_score >= 85:
    signal = "STRONG BUY"      # 🟢 Best setups, take immediately
    confidence = "Very High"
    
elif total_score >= 70:
    signal = "BUY"             # 🟢 Good setups, monitor closely
    confidence = "High"
    
elif total_score >= 60:
    signal = "WATCH"           # 🟡 Potential, needs improvement
    confidence = "Medium"
    
else:
    signal = "SKIP"            # 🔴 Insufficient quality
    confidence = "Low"
```

### **Signal Output:**

```python
{
    "symbol": "RELIANCE.NS",
    "signal": "STRONG BUY",
    "total_score": 87,
    "breakdown": {
        "stage_analysis": 28,      # /30
        "technical_setup": 23,     # /25
        "fundamental_quality": 18, # /20
        "liquidity": 13,           # /15
        "sectoral_strength": 5     # /10
    },
    "setup_type": "Narrow Range Breakout",
    "entry_price": 2450,
    "stop_loss": 2280,           # Defined risk
    "target_1": 2940,            # 20% (1:3 R:R)
    "target_2": 3430,            # 40%
    "risk_reward": "1:3.5",
    "sector": "Energy",
    "sector_rs": 108,            # Strong sector
    "timestamp": "2026-04-18 14:30:00"
}
```

---

## 🎛️ Weight Assignments (Expert-Based)

### **Why These Weights?**

**1. Stage Analysis (30%) - Highest Weight**
- **Reason:** Trend is king. Wrong stage = losing trade 80% of the time
- **Minervini's data:** 90% of big winners in Stage 2
- **Our focus:** Catch early Stage 2, avoid late

**2. Technical Setup (25%) - Second Highest**
- **Reason:** Entry timing critical. Best stock, wrong setup = mediocre returns
- **Your insight:** "Narrow ranges, 200 EMA rides most winning"
- **Our focus:** Specific patterns with defined risk

**3. Fundamental Quality (20%) - Quality Filter**
- **Reason:** Separates leaders from laggards
- **Data:** Growth stocks outperform value in Stage 2
- **Our focus:** Sales/profit growth, ROE, cash flow

**4. Liquidity & Tradeability (15%) - Noise Filter**
- **Reason:** Illiquid stocks = slippage, manipulation
- **Your complaint:** "Illiquid stocks, noise"
- **Our focus:** Min ₹1 Cr daily volume, avoid penny stocks

**5. Sectoral Strength (10%) - Tailwind**
- **Reason:** Even average stock in strong sector beats great stock in weak sector (short-term)
- **Data:** Sector accounts for 30-50% of stock movement
- **Our focus:** Sector RS > 100

---

## 🔍 Filtering Logic

### **Mandatory Requirements (Must Pass ALL):**

```python
# HARD FILTERS (Any failure = Auto-reject)

# 1. Liquidity Minimum
avg_daily_volume >= 100,000 shares
avg_daily_value >= ₹50 lakhs

# 2. Price Minimum
price >= ₹50  # No penny stocks

# 3. Market Cap Minimum
market_cap >= ₹5,000 Cr  # No micro caps

# 4. Stage Requirement
price > 200_day_ma  # Must be in uptrend

# 5. Fundamental Minimum
sales_growth_yoy > 0%  # Growing revenue
operating_cf > 0       # Positive cash flow

# 6. Risk Defined
stop_loss_defined = True  # Must have clear stop
risk_percent < 12%        # Max 12% risk from entry
```

### **Only stocks passing ALL hard filters proceed to scoring.**

---

## 📈 Signal Types & Categories

### **Category A: Early Stage 2 (Preferred)**
- Just entered Stage 2 (< 5% above 200 MA)
- Base breakout < 10 days old
- Fresh momentum
- **Best Risk:Reward**

### **Category B: Stage 2 Pullback (Your Specialty)**
- Established Stage 2 (5-15% above 200 MA)
- Pullback to 200 EMA or narrow range
- Support holding
- **Lower Risk, Proven Trend**

### **Category C: Stage 1 to 2 Transition (Advanced)**
- Bottoming process complete
- Just breaking above 200 MA
- Early accumulation signs
- **Highest Risk, Earliest Entry**

---

## 🛠️ Implementation Architecture

```
stocks/signal_generation/
│
├── scanner.py                    # Main scanning engine
├── scorers/
│   ├── stage_analyzer.py         # Pillar 1: Stage scoring
│   ├── technical_scorer.py       # Pillar 2: Setup detection
│   ├── fundamental_scorer.py     # Pillar 3: Quality metrics
│   ├── liquidity_scorer.py       # Pillar 4: Tradability
│   └── sectoral_scorer.py        # Pillar 5: Sector strength
│
├── filters/
│   ├── hard_filters.py           # Mandatory requirements
│   ├── liquidity_filter.py       # Volume, value, price filters
│   └── quality_filter.py         # Fundamental minimums
│
├── signal_generator.py           # Composite scoring & signal output
├── risk_calculator.py            # Stop loss & target calculation
└── config/
    ├── weights.py                # Weight configuration
    └── thresholds.py             # Threshold values
```

---

## 🎯 Usage Workflow

### **Daily/Weekly Scan:**

```python
from stocks.signal_generation import SignalGenerator

# Initialize
sg = SignalGenerator(
    universe='NSE500',
    min_score=70,
    max_signals=20
)

# Run scan
signals = sg.scan()

# Output
for signal in signals:
    print(f"""
    Symbol: {signal['symbol']}
    Signal: {signal['signal']}
    Score: {signal['total_score']}/100
    
    Setup: {signal['setup_type']}
    Entry: ₹{signal['entry_price']}
    Stop: ₹{signal['stop_loss']} ({signal['risk_pct']}%)
    Target 1: ₹{signal['target_1']} (R:R = 1:{signal['rr_ratio']})
    
    Why: 
    - Stage {signal['stage_position']} ({signal['pct_above_200ma']}% above 200 MA)
    - {signal['setup_description']}
    - Sector: {signal['sector']} (RS = {signal['sector_rs']})
    - Fundamentals: Sales ↑{signal['sales_growth']}%, Profit ↑{signal['profit_growth']}%
    
    Action: {signal['action_plan']}
    """)
```

### **Example Output:**

```
Symbol: RELIANCE.NS
Signal: STRONG BUY
Score: 87/100

Setup: Narrow Range Consolidation (NR7)
Entry: ₹2,450
Stop: ₹2,280 (6.9% risk)
Target 1: ₹2,940 (20% gain, R:R = 1:2.9)

Why:
- Stage 2 Early (8% above 200 MA) ✅
- 7-day tight consolidation breaking out ✅
- Sector: Energy (RS = 108) - Strong ✅
- Fundamentals: Sales ↑18%, Profit ↑24%, ROE 16% ✅
- Liquidity: ₹180 Cr daily volume ✅

Action: Set alert at ₹2,460 (breakout confirmation)
```

---

## 🔥 Advanced Features

### **1. Noise Reduction**

**Problem:** Too many signals = analysis paralysis

**Solution:**
```python
# Rank signals by score
# Show top 10-20 only
# Daily digest email with best setups
```

### **2. Already Extended Filter**

**Problem:** "Move already played out"

**Solution:**
```python
# Check distance from base breakout
if bars_since_breakout > 30:
    score -= 10  # Penalize late entries
    
# Check extension from 200 MA
if pct_above_200ma > 30%:
    score -= 15  # Too extended
```

### **3. False Breakout Prevention**

**Problem:** Stage 1-2 transitions fail often

**Solution:**
```python
# Require:
1. Volume confirmation (1.5× avg)
2. Multiple closes above 200 MA (not just 1)
3. 200 MA slope positive
4. Sector also strong
```

### **4. Risk-First Approach**

**Problem:** No defined risk = gambling

**Solution:**
```python
# Every signal MUST include:
- Stop loss price
- Risk percentage
- Risk:Reward ratio
- Max position size based on 1% risk rule
```

---

## 📊 Comparison: ChartInk vs Our System

| Aspect | ChartInk Screeners | Our System |
|--------|-------------------|------------|
| **Liquidity Filter** | ❌ No | ✅ Yes (mandatory) |
| **Fundamental Screen** | ❌ No | ✅ Yes (20% weight) |
| **Sectoral Context** | ❌ No | ✅ Yes (10% weight) |
| **Risk Definition** | ❌ No | ✅ Yes (every signal) |
| **Extension Filter** | ❌ No | ✅ Yes (penalize late) |
| **Composite Scoring** | ❌ Binary (pass/fail) | ✅ Weighted (0-100) |
| **Signal Ranking** | ❌ No priority | ✅ Best to worst |
| **False Breakout Filter** | ❌ Weak | ✅ Multi-factor |
| **Category Classification** | ❌ No | ✅ Yes (A/B/C) |
| **Noise Reduction** | ❌ 100+ results | ✅ Top 10-20 only |

---

## 🎓 Extensibility: Stocks → Futures/Commodities

### **Applicable to Both:**
- ✅ Stage Analysis (trend phase)
- ✅ Technical Setups (breakouts, pullbacks)
- ✅ Volume Confirmation
- ✅ Liquidity (futures always liquid)
- ✅ Risk Definition (stop loss)

### **Not Applicable to Futures:**
- ❌ Fundamentals (commodities have no earnings)
- ❌ Sectoral Strength (futures are standalone)

### **Futures Adaptation:**

```python
# For Gold, Silver, Crude, Nifty Futures

total_score = (
    trend_score +          # 40 points (higher weight, no fundamentals)
    technical_score +      # 35 points (setup + volume)
    momentum_score +       # 15 points (RSI, MACD)
    regime_score           # 10 points (Hurst Exponent - trending vs ranging)
)

# Futures-specific additions:
- Hurst Exponent (from your Sierra Chart code)
- Volume Profile (HVN/LVN/POC)
- Pair trading opportunities
```

---

## 🚀 Next Steps

**I recommend:**

1. **Build the stock scanner first** (this document)
   - Implement 5 pillars
   - Test on NSE500
   - Refine weights

2. **Then extend to futures** 
   - Adapt scoring (remove fundamentals)
   - Add regime detection (Hurst)
   - Add volume profile

---

## ✅ Key Takeaways

**Our system is superior because:**

1. ✅ **Multi-faceted:** 5 pillars, not just price action
2. ✅ **Weighted:** Important factors matter more
3. ✅ **Noise-filtered:** Liquidity, quality, extension checks
4. ✅ **Risk-defined:** Every signal has stop loss
5. ✅ **Ranked:** Best signals float to top
6. ✅ **Context-aware:** Sector strength included
7. ✅ **Prevents late entries:** Extension penalties
8. ✅ **Quality over quantity:** Top 10-20 only

**Your complaint solved:**
- ❌ "Illiquid stocks" → Mandatory ₹50L+ daily volume
- ❌ "Noise" → Hard filters + scoring threshold
- ❌ "Move already played out" → Extension penalties
- ❌ "Manually screen hard" → Automated composite scoring

---

**Ready to build this?** Let's start coding! 🎯
