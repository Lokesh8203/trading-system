# Futures Signal Generation Framework
## For Index Futures & Commodity Futures (Gold, Silver, Crude, Nifty, Bank Nifty)

**Source:** Extracted from Sierra Chart Hurst Exponent studies + Professional trading principles

**Philosophy:** Pure price action + volume + regime detection for swift scalping trades

---

## 🎯 Key Concepts from ACS_Source

### **What We Found:**

Your Sierra Chart studies implement:

1. **Hurst Exponent** - Market regime detection
   - Thresholds: 
     - < 0.40: Mean-reverting (DOWN_THRESHOLD)
     - > 0.60: Trending (UP_THRESHOLD)
     - 0.40-0.60: Random/choppy

2. **Volume Profile Analysis**
   - HVN (High Volume Nodes) - Strong support/resistance
   - LVN (Low Volume Nodes) - Fast movement zones
   - POC (Point of Control) - Fair value
   - VAH/VAL (Value Area High/Low)

3. **Multi-Timeframe Analysis**
   - 0.75× series
   - 1× series
   - 3× series
   - Volume bars (900 volume chart referenced)

4. **FragmentBlock System**
   - Zones classification (HVN vs LVN)
   - Volume accumulation per price level
   - Max/min volume tracking

---

## 🔥 Extracted Logic for Python Implementation

### **1. Hurst Exponent Calculation**

**Purpose:** Determine if market is trending or mean-reverting

```python
def calculate_hurst_exponent(prices, lookback=100):
    """
    Calculate Hurst Exponent using R/S analysis
    
    H > 0.6: Trending (persistent) - Trade breakouts, follow trends
    H < 0.4: Mean-reverting (anti-persistent) - Fade extremes, range trade
    H ≈ 0.5: Random walk - Avoid trading, low edge
    
    Args:
        prices: pd.Series of closing prices
        lookback: Number of bars to analyze
    
    Returns:
        float: Hurst exponent value (0-1)
    """
    import numpy as np
    
    if len(prices) < lookback:
        return 0.5  # Neutral if insufficient data
    
    prices = prices[-lookback:].values
    
    # Calculate log returns
    log_returns = np.log(prices[1:] / prices[:-1])
    
    # Calculate mean
    mean_return = np.mean(log_returns)
    
    # Calculate cumulative deviation from mean
    cumulative_deviation = np.cumsum(log_returns - mean_return)
    
    # Calculate range (R)
    R = np.max(cumulative_deviation) - np.min(cumulative_deviation)
    
    # Calculate standard deviation (S)
    S = np.std(log_returns)
    
    if S == 0:
        return 0.5
    
    # R/S ratio
    rs_ratio = R / S
    
    # Hurst exponent
    H = np.log(rs_ratio) / np.log(lookback)
    
    # Clamp between 0 and 1
    H = max(0.0, min(1.0, H))
    
    return H
```

**Usage in Trading:**
```python
hurst = calculate_hurst_exponent(gold_prices, lookback=100)

if hurst > 0.6:
    regime = "TRENDING"
    strategy = "Breakout, trend continuation"
    
elif hurst < 0.4:
    regime = "MEAN_REVERTING"
    strategy = "Fade extremes, range trading"
    
else:
    regime = "CHOPPY"
    strategy = "Avoid or reduce size"
```

---

### **2. Volume Profile (HVN/LVN/POC)**

**Purpose:** Identify key price levels based on volume

```python
def calculate_volume_profile(df, num_bins=50):
    """
    Calculate volume profile for a given period
    
    Returns HVN zones (strong S/R), LVN zones (fast movement), POC (fair value)
    
    Args:
        df: DataFrame with columns ['High', 'Low', 'Close', 'Volume']
        num_bins: Number of price bins to divide range into
    
    Returns:
        dict: {
            'poc': Point of Control price,
            'vah': Value Area High,
            'val': Value Area Low,
            'hvn_zones': List of high volume node price ranges,
            'lvn_zones': List of low volume node price ranges,
            'profile': Full volume profile data
        }
    """
    import pandas as pd
    import numpy as np
    
    # Determine price range
    high = df['High'].max()
    low = df['Low'].min()
    price_range = high - low
    
    if price_range == 0:
        return None
    
    # Create price bins
    bin_size = price_range / num_bins
    bins = np.linspace(low, high, num_bins + 1)
    
    # Initialize volume accumulator
    volume_at_price = np.zeros(num_bins)
    
    # Accumulate volume at each price level
    for idx, row in df.iterrows():
        # For each bar, distribute volume across price levels it touched
        bar_low = row['Low']
        bar_high = row['High']
        bar_volume = row['Volume']
        
        # Find bins this bar touches
        low_bin = int((bar_low - low) / bin_size)
        high_bin = int((bar_high - low) / bin_size)
        
        # Clamp to valid range
        low_bin = max(0, min(low_bin, num_bins - 1))
        high_bin = max(0, min(high_bin, num_bins - 1))
        
        # Distribute volume evenly across touched bins
        bins_touched = high_bin - low_bin + 1
        volume_per_bin = bar_volume / bins_touched
        
        for bin_idx in range(low_bin, high_bin + 1):
            volume_at_price[bin_idx] += volume_per_bin
    
    # Find POC (Point of Control) - highest volume bin
    poc_bin = np.argmax(volume_at_price)
    poc_price = low + (poc_bin + 0.5) * bin_size
    poc_volume = volume_at_price[poc_bin]
    
    # Calculate Value Area (70% of volume)
    total_volume = np.sum(volume_at_price)
    target_volume = total_volume * 0.70
    
    # Start from POC and expand outward
    accumulated_volume = volume_at_price[poc_bin]
    val_bin = poc_bin
    vah_bin = poc_bin
    
    while accumulated_volume < target_volume:
        # Check which direction has more volume
        lower_volume = volume_at_price[val_bin - 1] if val_bin > 0 else 0
        upper_volume = volume_at_price[vah_bin + 1] if vah_bin < num_bins - 1 else 0
        
        if lower_volume > upper_volume and val_bin > 0:
            val_bin -= 1
            accumulated_volume += volume_at_price[val_bin]
        elif vah_bin < num_bins - 1:
            vah_bin += 1
            accumulated_volume += volume_at_price[vah_bin]
        else:
            break
    
    vah_price = low + (vah_bin + 0.5) * bin_size
    val_price = low + (val_bin + 0.5) * bin_size
    
    # Identify HVN zones (high volume nodes)
    # HVN = bins with volume > 150% of average
    avg_volume = total_volume / num_bins
    hvn_threshold = avg_volume * 1.5
    
    hvn_zones = []
    for i in range(num_bins):
        if volume_at_price[i] > hvn_threshold:
            price = low + (i + 0.5) * bin_size
            hvn_zones.append({
                'price': price,
                'volume': volume_at_price[i],
                'strength': volume_at_price[i] / poc_volume  # Relative to POC
            })
    
    # Identify LVN zones (low volume nodes)
    # LVN = bins with volume < 50% of average
    lvn_threshold = avg_volume * 0.5
    
    lvn_zones = []
    for i in range(num_bins):
        if volume_at_price[i] < lvn_threshold:
            price = low + (i + 0.5) * bin_size
            lvn_zones.append({
                'price': price,
                'volume': volume_at_price[i]
            })
    
    return {
        'poc': poc_price,
        'poc_volume': poc_volume,
        'vah': vah_price,
        'val': val_price,
        'hvn_zones': hvn_zones,
        'lvn_zones': lvn_zones,
        'volume_profile': volume_at_price,
        'price_bins': bins
    }
```

**Usage in Trading:**
```python
# Calculate volume profile for last 100 bars
vp = calculate_volume_profile(gold_data[-100:])

# Trading logic
current_price = gold_data.iloc[-1]['Close']

# Check proximity to key levels
for hvn in vp['hvn_zones']:
    if abs(current_price - hvn['price']) < 10:  # Within 10 points
        print(f"At HVN zone {hvn['price']} - Strong S/R")
        # Expect bounce or rejection

# Check if in LVN
in_lvn = any(abs(current_price - lvn['price']) < 10 for lvn in vp['lvn_zones'])
if in_lvn:
    print("In LVN zone - Expect fast move")
    # Price should move quickly through
```

---

### **3. Combined Regime + Volume Profile Trading**

**The Power Combo:**

```python
def generate_futures_signal(df, instrument='GOLD'):
    """
    Generate futures trading signal using Hurst + Volume Profile
    
    Returns signal with regime context and volume-based levels
    """
    
    # Calculate Hurst Exponent
    hurst = calculate_hurst_exponent(df['Close'], lookback=100)
    
    # Calculate Volume Profile (last 100 bars)
    vp = calculate_volume_profile(df[-100:])
    
    # Current price and context
    current_price = df.iloc[-1]['Close']
    current_high = df.iloc[-1]['High']
    current_low = df.iloc[-1]['Low']
    
    # Determine regime
    if hurst > 0.6:
        regime = "TRENDING"
        regime_score = 10
    elif hurst < 0.4:
        regime = "MEAN_REVERTING"
        regime_score = 10
    else:
        regime = "CHOPPY"
        regime_score = 0  # Avoid trading
    
    # Check position relative to volume profile
    near_poc = abs(current_price - vp['poc']) < (instrument_tick_size * 20)
    near_hvn = any(abs(current_price - hvn['price']) < 10 for hvn in vp['hvn_zones'])
    in_lvn = any(abs(current_price - lvn['price']) < 10 for lvn in vp['lvn_zones'])
    
    # Generate signal based on regime + volume structure
    signal = None
    
    # TRENDING REGIME - Trade breakouts and continuation
    if regime == "TRENDING":
        # Breakout above POC with trend
        if current_price > vp['poc'] and not near_hvn:
            signal = {
                'type': 'LONG_BREAKOUT',
                'entry': current_price + 5,  # Above current
                'stop': vp['poc'] - 10,      # Below POC
                'target1': next_hvn_above(current_price, vp),
                'confidence': 'HIGH',
                'reason': 'Trending market breaking above POC'
            }
        
        # Pullback to HVN in uptrend
        elif near_hvn and current_price > vp['poc']:
            signal = {
                'type': 'LONG_PULLBACK',
                'entry': nearest_hvn_price(current_price, vp),
                'stop': nearest_hvn_price(current_price, vp) - 15,
                'target1': vp['vah'],
                'confidence': 'MEDIUM',
                'reason': 'Pullback to HVN support in uptrend'
            }
    
    # MEAN-REVERTING REGIME - Fade extremes, trade to POC
    elif regime == "MEAN_REVERTING":
        # Price far above POC - fade
        if current_price > vp['vah'] + 20:
            signal = {
                'type': 'SHORT_FADE',
                'entry': current_price,
                'stop': current_price + 20,  # Tight stop
                'target1': vp['poc'],        # Back to fair value
                'confidence': 'MEDIUM',
                'reason': 'Overbought in mean-reverting regime'
            }
        
        # Price far below POC - fade
        elif current_price < vp['val'] - 20:
            signal = {
                'type': 'LONG_FADE',
                'entry': current_price,
                'stop': current_price - 20,  # Tight stop
                'target1': vp['poc'],        # Back to fair value
                'confidence': 'MEDIUM',
                'reason': 'Oversold in mean-reverting regime'
            }
    
    # CHOPPY REGIME - Avoid or very selective
    else:
        signal = {
            'type': 'NO_TRADE',
            'reason': 'Choppy market, low edge'
        }
    
    # Add regime and volume context
    if signal:
        signal['hurst'] = hurst
        signal['regime'] = regime
        signal['poc'] = vp['poc']
        signal['vah'] = vp['vah']
        signal['val'] = vp['val']
        signal['near_hvn'] = near_hvn
        signal['in_lvn'] = in_lvn
    
    return signal
```

---

## 📊 Futures Signal Scoring System

Unlike stocks (5 pillars), futures use **4 pillars** (no fundamentals):

```
┌────────────────────────────────────────────┐
│   FUTURES SIGNAL SCORE (0-100)             │
├────────────────────────────────────────────┤
│ 1. REGIME (HURST)      40 pts ████████████ │
│    • Trending vs mean-reverting            │
│    • Choppy = avoid                        │
│                                            │
│ 2. PRICE ACTION        35 pts ████████████ │
│    • Breakout/breakdown                    │
│    • HVN bounce                            │
│    • LVN acceleration                      │
│    • Volume confirmation                   │
│                                            │
│ 3. VOLUME PROFILE      15 pts ████         │
│    • Position vs POC/VAH/VAL               │
│    • Near HVN (support/resistance)         │
│    • In LVN (fast move zone)               │
│                                            │
│ 4. MOMENTUM            10 pts ███          │
│    • RSI divergence                        │
│    • MACD alignment                        │
│    • Trend strength                        │
└────────────────────────────────────────────┘
```

---

## 🎯 Complete Futures Signal Generator

### **Implementation Structure:**

```python
futures/signal_generation/
├── regime_detector.py         # Hurst Exponent calculation
├── volume_profiler.py         # VP calculation (HVN/LVN/POC)
├── price_action_scorer.py     # Breakout/breakdown/pullback detection
├── momentum_scorer.py          # RSI, MACD scoring
├── signal_generator.py         # Composite scoring
└── config/
    ├── thresholds.py           # Hurst thresholds, HVN/LVN criteria
    └── instruments.py          # Gold, Silver, Crude, Nifty, Bank Nifty specs
```

---

## 🔥 Key Trading Rules from Sierra Chart Logic

### **1. Hurst-Based Regime Switching**

```python
# From your code: DOWN_THRESHOLD = 0.40, UP_THRESHOLD = 0.60

if hurst <= 0.40:
    # Mean-reverting market
    strategy = "FADE_EXTREMES"
    - Short overbought (price > VAH + 2 std dev)
    - Long oversold (price < VAL - 2 std dev)
    - Target POC
    - Tight stops (20-30 points)
    
elif hurst >= 0.60:
    # Trending market
    strategy = "FOLLOW_TREND"
    - Buy pullbacks to HVN
    - Short rallies to HVN (if downtrend)
    - Breakout trades
    - Wider stops (allow trend to breathe)
    
else:
    # Choppy market
    strategy = "AVOID"
    - Reduce size or skip
    - Only trade at extreme HVN levels
```

### **2. Volume Profile Integration**

```python
# HVN zones (from FragmentBlock logic)
- HVN = Strong support/resistance
- Price bounces at HVN in trending markets
- Price gets rejected at HVN in mean-reverting markets

# LVN zones
- Price moves FAST through LVN (no volume = no resistance)
- Don't expect support/resistance
- Target next HVN

# POC (Point of Control)
- Fair value
- Price gravitates toward POC
- Mean-reversion target
- Balance point
```

### **3. Multi-Timeframe Confirmation**

```python
# Your code uses 0.75x, 1x, 3x series
# Translation to timeframes:

if hurst_15min > 0.6 and hurst_1hour > 0.6:
    # Strong trend across timeframes
    confidence = "VERY_HIGH"
    
elif hurst_15min > 0.6 and hurst_1hour < 0.5:
    # Short-term trend, longer-term choppy
    confidence = "MEDIUM"
    # Be quick, don't overstay

elif hurst_15min < 0.4 and hurst_1hour > 0.6:
    # Short-term mean-reversion, longer-term trend
    # BEST for pullback trades
    confidence = "HIGH"
```

---

## 🛠️ Instrument-Specific Configuration

### **Gold (MCX)**

```python
GOLD_CONFIG = {
    'tick_size': 1.0,            # ₹1 per 10g
    'stop_loss_ticks': 100,      # ₹100 stop
    'target_ticks': 200,         # ₹200 target (1:2 R:R)
    'hvn_threshold': 50,         # Consider HVN if within ₹50
    'lvn_threshold': 20,         # Consider in LVN if within ₹20
    'hurst_lookback': 100,       # 100 bars for Hurst
    'vp_lookback': 100,          # 100 bars for VP
    'peak_hours': [(9, 30), (14, 30)]  # Morning & afternoon
}
```

### **Silver (MCX)**

```python
SILVER_CONFIG = {
    'tick_size': 1.0,            # ₹1 per kg
    'stop_loss_ticks': 200,      # ₹200 stop
    'target_ticks': 400,         # ₹400 target
    'hvn_threshold': 100,
    'lvn_threshold': 50,
    'hurst_lookback': 100,
    'vp_lookback': 100,
    'peak_hours': [(9, 30), (14, 30)]
}
```

### **Crude Oil (MCX)**

```python
CRUDE_CONFIG = {
    'tick_size': 1.0,            # ₹1 per barrel
    'stop_loss_ticks': 50,       # $0.50 stop (₹50)
    'target_ticks': 100,         # $1.00 target
    'hvn_threshold': 25,
    'lvn_threshold': 10,
    'hurst_lookback': 50,        # More reactive for crude
    'vp_lookback': 50,
    'peak_hours': [(9, 15), (14, 0), (17, 30)]  # Follows US hours
}
```

### **Nifty 50 Futures**

```python
NIFTY_CONFIG = {
    'tick_size': 0.05,           # 0.05 points
    'stop_loss_ticks': 30,       # 30 points stop
    'target_ticks': 60,          # 60 points target
    'hvn_threshold': 20,
    'lvn_threshold': 10,
    'hurst_lookback': 75,
    'vp_lookback': 75,
    'peak_hours': [(9, 30), (14, 30)]
}
```

### **Bank Nifty Futures**

```python
BANKNIFTY_CONFIG = {
    'tick_size': 0.05,
    'stop_loss_ticks': 50,       # 50 points stop (more volatile)
    'target_ticks': 100,         # 100 points target
    'hvn_threshold': 30,
    'lvn_threshold': 15,
    'hurst_lookback': 75,
    'vp_lookback': 75,
    'peak_hours': [(9, 30), (14, 30)]
}
```

---

## 🎯 Example Signals

### **Example 1: Gold Trending (Hurst = 0.72)**

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🟢 LONG SIGNAL: GOLD MCX
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Regime: TRENDING (Hurst = 0.72)
Setup: Pullback to HVN in uptrend

Entry: ₹62,450 (at HVN support)
Stop:  ₹62,350 (₹100 below, 0.16% risk)
Target 1: ₹62,650 (₹200, R:R = 1:2)
Target 2: ₹62,850 (₹400, R:R = 1:4)

Volume Profile Context:
  POC: ₹62,300 (below current - bullish)
  VAH: ₹62,700 (target)
  VAL: ₹62,100
  At HVN: Yes (₹62,450 is strong support)

Why:
  • Trending market (Hurst > 0.6)
  • Price pulled back to HVN
  • HVN holding as support
  • Target is next HVN at ₹62,650

Action: Buy at ₹62,450, stop ₹62,350
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### **Example 2: Nifty Mean-Reverting (Hurst = 0.35)**

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔴 SHORT SIGNAL: NIFTY 50 FUTURES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Regime: MEAN-REVERTING (Hurst = 0.35)
Setup: Fade overbought extreme

Entry: 21,650 (extended above VAH)
Stop:  21,680 (30 points above, tight)
Target: 21,600 (POC - fair value)

Volume Profile Context:
  POC: 21,600 (target - fair value)
  VAH: 21,630 (below current - extended)
  VAL: 21,550
  In LVN: No (near VAH, should reverse fast)

Why:
  • Mean-reverting market (Hurst < 0.4)
  • Price 20 points above VAH (overbought)
  • Fade back to POC (fair value)
  • Tight stop (mean-reversion = quick moves)

Action: Short at 21,650, stop 21,680, target 21,600
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### **Example 3: Choppy Market - No Trade**

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚠️  NO SIGNAL: SILVER MCX
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Regime: CHOPPY (Hurst = 0.48)
Setup: None - avoid trading

Hurst: 0.48 (random walk zone)
POC: ₹76,500
Price: ₹76,520 (near POC - no edge)

Why Avoid:
  • Hurst near 0.5 = random walk
  • Price near POC (no directional bias)
  • No clear regime = low probability
  • Better to wait for regime clarity

Action: SKIP - Wait for Hurst > 0.6 or < 0.4
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## 🚀 Implementation Priority

### **Phase 1: Core Logic (Week 1)**
1. ✅ Hurst Exponent calculator
2. ✅ Volume Profile calculator (HVN/LVN/POC)
3. ✅ Regime detector (trending/mean-reverting/choppy)

### **Phase 2: Signal Generation (Week 2)**
4. Price action scorer (breakouts, pullbacks)
5. Momentum scorer (RSI, MACD)
6. Composite signal generator

### **Phase 3: Real-time Integration (Week 3)**
7. Hourly data fetcher (Zerodha or free sources)
8. Real-time Hurst + VP calculation
9. Alert system (Telegram/WhatsApp)

### **Phase 4: Testing & Refinement (Week 4)**
10. Backtest on historical data
11. Paper trade for 100 signals
12. Refine thresholds

---

## ✅ Summary: What We Extracted

From your **ACS_Source Sierra Chart studies**, we identified:

1. **Hurst Exponent**
   - Thresholds: 0.40 (mean-reverting) and 0.60 (trending)
   - Multi-timeframe analysis (0.75x, 1x, 3x series)
   - **Application:** Market regime detection before every trade

2. **Volume Profile**
   - FragmentBlock system for zone identification
   - HVN (high volume nodes) = strong S/R
   - LVN (low volume nodes) = fast movement
   - POC (point of control) = fair value
   - **Application:** Precise entry/exit levels

3. **Combined Logic**
   - Trade breakouts in trending regimes (Hurst > 0.6)
   - Fade extremes in mean-reverting regimes (Hurst < 0.4)
   - Use HVN as support/resistance
   - Target POC in mean-reversion
   - Target next HVN in trends

**This is PERFECT for your System 2 (Futures Scalping)!**

---

## 🎯 Next Step

**Want me to code this in Python now?**

I'll build:
- `futures/indicators/hurst_exponent.py`
- `futures/indicators/volume_profile.py`
- `futures/signal_generation/regime_detector.py`
- `futures/signal_generation/signal_generator.py`

**Ready to implement?** 🚀
