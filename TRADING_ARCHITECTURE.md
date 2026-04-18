# Trading System Architecture

## Two Distinct Trading Systems

This trading system is divided into two independent subsystems with different philosophies, timeframes, and methodologies:

---

## 🏗️ **System Architecture**

```
trading-system/
│
├── 1. STOCK INVESTING SYSTEM (System 1)
│   ├── Stage Analysis Framework
│   ├── Base Breakout Detection
│   ├── Financial Screening (Statements + Cash Flows)
│   ├── Technical Setups (200 EMA, Narrow Ranges)
│   └── Position Sizing (Lower leverage, longer holds)
│
├── 2. FUTURES SCALPING SYSTEM (System 2)
│   ├── Pure Price Action (No fundamentals)
│   ├── Breakout/Breakdown Detection (Hourly)
│   ├── Pair Trading Logic
│   ├── Rapid Entry/Exit
│   └── Tight Stop Loss Management
│
└── SHARED INFRASTRUCTURE
    ├── Data Collection (Both use same data feeds)
    ├── Sectoral Analysis (System 1 uses more)
    ├── Knowledge Base (Both reference)
    └── Risk Management (Different rules per system)
```

---

## 📊 **System 1: Stock Investing**

### **Philosophy**
- **"Right stock, right time, right stage"**
- Quality companies in momentum phase
- Fundamental validation required
- Ride trends until stage changes

### **Universe**
- NSE 200/500 stocks
- Focus on liquid names (avg daily volume > 1 million)
- Market cap > ₹5000 Cr (preference)

### **Entry Criteria (ALL must be met)**

#### 1. **Stage Analysis** (Mark Minervini / Stan Weinstein)
- **Stage 2 only** (Advancing phase)
- Stock above 200 EMA (rising)
- Higher highs, higher lows
- Volume confirming

#### 2. **Technical Setup** (Your Favorites)
- **Narrow Range Consolidation** (7-10 days tight)
  - Low volatility compression
  - Volume declining
  - Ready to expand
  
- **200 EMA Rides**
  - Price pulling back to 200 EMA
  - Holding support
  - Bounce with volume
  
- **Base Breakout**
  - Cup & Handle, Flat Base, VCP
  - 4+ weeks consolidation minimum
  - Breakout on increasing volume

#### 3. **Fundamental Validation** (Quick Screen)
- **Sales Growth:** YoY > 15% (last 2 quarters)
- **Profit Growth:** YoY > 20% (last 2 quarters)
- **Cash Flow:** Operating CF positive and growing
- **Debt/Equity:** < 1 (or improving trend)
- **ROE:** > 15%
- **Promoter Holding:** > 40%, not declining

#### 4. **Sectoral Strength**
- Sector RS > 100 (outperforming Nifty 50)
- Sector in top 5 performers
- Stock outperforming sector

### **Position Sizing**
- **Risk per trade:** 1% of capital
- **Position size:** Based on stop loss distance
- **Max positions:** 5-8 stocks
- **Max sector exposure:** 30% in one sector

### **Stop Loss**
- **Swing low below entry** or **8-10% max**
- Trail to breakeven at +10%
- Trail with 50 EMA after +20%

### **Targets**
- **T1:** 20% (book 33%)
- **T2:** 40% (book 33%)
- **T3:** Let it run, trail with 50 EMA (33%)

### **Exit Rules**
1. **Stop hit**
2. **Stage changes** (breaks 200 EMA, distribution signs)
3. **Fundamentals deteriorate** (earnings miss, cash flow negative)
4. **Sector weakens** (RS < 95)
5. **Time stop** (No progress in 8 weeks)

### **Review Frequency**
- **Weekly:** Portfolio review, sector rotation check
- **Quarterly:** Fundamental re-screening (earnings, statements)

---

## ⚡ **System 2: Futures Scalping**

### **Philosophy**
- **"In and out, swift wins"**
- Pure price action, no story
- Strict discipline, tight stops
- High win rate over big targets

### **Universe**
- **Commodities:** Gold (MCX), Silver (MCX), Crude Oil (MCX)
- **Indices:** Nifty 50 Futures, Bank Nifty Futures
- **Forex:** USD/INR (if available)

### **Timeframe**
- **Primary:** 1-Hour candles
- **Entry:** 15-min or 5-min (precision)
- **Context:** 4-Hour or Daily (trend bias)

### **Entry Setups**

#### 1. **Breakout Trading**
- **Pattern:** Consolidation range (hourly)
- **Trigger:** Break above/below range on volume
- **Confirmation:** Close beyond range
- **Entry:** On retest or immediately
- **Stop:** Other side of range + buffer (20-30 points)
- **Target:** 1× to 2× range height

**Example (Nifty):**
```
Range: 21,500 - 21,600 (100 points)
Breakout: Above 21,600
Entry: 21,610 (on close above or retest)
Stop: 21,570 (below range)
Target 1: 21,700 (1× range = 100 points)
Target 2: 21,800 (2× range = 200 points)
```

#### 2. **Breakdown Trading**
- **Pattern:** Support breakdown
- **Trigger:** Break below key level on volume
- **Entry:** On retest failure or immediately
- **Stop:** Above breakdown level + buffer
- **Target:** 1-1.5× risk distance

#### 3. **Trend Continuation**
- **Setup:** Pullback in strong trend (hourly)
- **Trigger:** Bounce off 20 EMA or 50 EMA
- **Confirmation:** Bullish engulfing or hammer
- **Entry:** Above confirmation candle
- **Stop:** Below EMA or swing low
- **Target:** Previous high + 50%

#### 4. **Pair Trading**
- **Gold vs Silver**
  - When ratio extremes
  - Long underperformer, short outperformer
  
- **Nifty vs Bank Nifty**
  - Divergence trading
  - Long leader, short laggard (or vice versa)
  
- **Crude vs INR**
  - Correlation play

### **Pair Trade Example**

**Gold/Silver Ratio Trading:**
```
Normal Ratio: 80-85
Current: 90 (Gold expensive vs Silver)

Trade:
- Short Gold Futures
- Long Silver Futures (proportional)

Exit:
- Ratio returns to 85
- Or stop at ratio 92 (loss)
- Or profit at ratio 82 (gain)
```

**Nifty/Bank Nifty Divergence:**
```
Scenario: Nifty breaking highs, Bank Nifty lagging

Trade:
- Long Nifty Futures
- Short Bank Nifty Futures (beta-adjusted)

Exit:
- Both converge (Bank Nifty catches up)
- Stop if Nifty reverses below recent low
```

### **Position Sizing**
- **Risk per trade:** 0.5% of capital (tighter for scalping)
- **Max positions:** 1-2 at a time (focus)
- **Leverage:** Max 3-5× (futures inherent leverage)

### **Stop Loss (NON-NEGOTIABLE)**
- **Nifty/Bank Nifty:** 30-50 points from entry
- **Gold:** ₹100-200 per 100g
- **Silver:** ₹200-400 per kg
- **Crude:** $0.50-1.00 per barrel
- **ALWAYS place stop immediately after entry**

### **Targets (SHORT targets, quick wins)**
- **Primary:** 1× risk (1:1 R:R minimum)
- **Extended:** 1.5-2× risk (if momentum strong)
- **Scale out:** 50% at T1, 50% at T2
- **Max hold:** 1-2 hours (unless strong trend)

### **Exit Rules**
1. **Stop hit** (no exceptions, no averaging down)
2. **Target hit** (book profit, don't get greedy)
3. **Time stop** (30-60 min no movement = exit breakeven)
4. **Reversal signal** (opposite setup forming)
5. **Market close approaching** (don't hold overnight unless planned)

### **Trade Frequency**
- **2-5 trades per day** (quality over quantity)
- **Peak hours:** 9:30-11:30 AM, 2:00-3:15 PM
- **Avoid:** 12:00-2:00 PM (lunch lull)

### **Review Frequency**
- **Daily:** End-of-day trade log, P&L, mistakes
- **Weekly:** Pattern recognition, what worked/didn't

---

## 🔄 **System Comparison**

| Aspect | System 1 (Stocks) | System 2 (Futures) |
|--------|-------------------|-------------------|
| **Timeframe** | Days to Months | Minutes to Hours |
| **Analysis** | Stage + Fundamentals + Technical | Pure Price Action |
| **Instruments** | NSE Stocks | Futures (Commodities, Indices) |
| **Entry Criteria** | 3-4 filters, confluence | 1-2 setups, clean trigger |
| **Stop Loss** | 8-10%, wider | 30-50 points, tight |
| **Target** | 20-40%+ | 1-2× risk |
| **Win Rate Target** | 50-60% (smaller edge, bigger wins) | 60-70% (tighter, consistent) |
| **Risk per Trade** | 1% | 0.5% |
| **Max Positions** | 5-8 | 1-2 |
| **Review** | Weekly/Quarterly | Daily |
| **Mental State** | Patient, research-driven | Alert, reactive |
| **Capital Allocation** | 70-80% | 20-30% |

---

## 📂 **File Organization**

```
trading-system/
│
├── stocks/                          # System 1: Stock Investing
│   ├── stage_analysis/
│   │   ├── stage_detector.py        # Identifies stock stage
│   │   ├── stage_scanner.py         # Scans NSE500 for Stage 2
│   │   └── README_STAGES.md         # Stage analysis guide
│   │
│   ├── fundamentals/
│   │   ├── financial_screener.py    # Sales, profit, CF screening
│   │   ├── data_fetcher.py          # Fetch statements (Screener.in, etc.)
│   │   └── README_FUNDAMENTALS.md   # How to screen
│   │
│   ├── technical_setups/
│   │   ├── narrow_range.py          # NR7, NR4 detection
│   │   ├── ema_200_rides.py         # 200 EMA pullback scanner
│   │   ├── base_breakout.py         # Cup, Handle, VCP patterns
│   │   └── README_SETUPS.md         # Technical setup guide
│   │
│   └── portfolio/
│       ├── position_sizer.py        # Calculate position size
│       ├── portfolio_manager.py     # Track open positions
│       └── watchlist.py             # Curated watchlist
│
├── futures/                         # System 2: Futures Scalping
│   ├── price_action/
│   │   ├── breakout_detector.py     # Hourly breakout/breakdown
│   │   ├── range_identifier.py      # Find consolidation ranges
│   │   ├── trend_continuation.py    # EMA pullback setups
│   │   └── README_PRICE_ACTION.md   # Price action guide
│   │
│   ├── pair_trading/
│   │   ├── ratio_calculator.py      # Gold/Silver ratio, etc.
│   │   ├── divergence_scanner.py    # Nifty vs Bank Nifty
│   │   ├── pair_trader.py           # Pair trade execution logic
│   │   └── README_PAIRS.md          # Pair trading strategies
│   │
│   ├── entry_exit/
│   │   ├── entry_manager.py         # Entry logic, confirmations
│   │   ├── stop_loss.py             # Tight SL management
│   │   ├── target_calculator.py     # Quick target calculation
│   │   └── README_EXECUTION.md      # Entry/exit discipline
│   │
│   └── monitoring/
│       ├── live_scanner.py          # Real-time hourly scanner
│       ├── alert_system.py          # Breakout/breakdown alerts
│       └── trade_log.py             # Daily trade journal
│
├── shared/                          # Shared Infrastructure
│   ├── data/                        # (Already exists)
│   ├── knowledge/                   # (Already exists)
│   └── risk_management/
│       ├── position_sizing.py       # General position size calculator
│       ├── portfolio_heat.py        # Max risk across all positions
│       └── README_RISK.md           # Risk management rules
│
└── config/
    ├── stock_config.py              # System 1 parameters
    ├── futures_config.py            # System 2 parameters
    └── general_config.py            # Shared settings
```

---

## 🎯 **Capital Allocation Strategy**

### **Total Capital: ₹10,00,000 (example)**

**System 1 (Stocks): ₹7,00,000 (70%)**
- More stable, longer holds
- Lower leverage (cash or margin)
- 5-8 positions × ₹87,500 avg each
- Risk per trade: ₹10,000 (1% of ₹10L total)

**System 2 (Futures): ₹2,00,000 (20%)**
- Higher volatility
- Futures inherent leverage
- 1-2 positions at a time
- Risk per trade: ₹5,000 (0.5% of ₹10L total)

**Reserve: ₹1,00,000 (10%)**
- Emergency fund
- Opportunity capital
- Drawdown buffer

---

## ⚙️ **Implementation Roadmap**

### **Phase 1: System 1 - Stock Investing (Weeks 1-4)**

**Week 1: Stage Analysis Framework**
- [ ] Build stage detection algorithm
- [ ] Create Stage 2 scanner for NSE500
- [ ] Identify current Stage 2 stocks
- [ ] Document stage characteristics

**Week 2: Financial Screening**
- [ ] Build financial data fetcher (Screener.in API or scraping)
- [ ] Create screening module (sales, profit, CF, ROE)
- [ ] Filter Stage 2 stocks by fundamentals
- [ ] Build watchlist generator

**Week 3: Technical Setups**
- [ ] Build narrow range detector (NR7, NR4)
- [ ] Create 200 EMA pullback scanner
- [ ] Add base breakout patterns (Cup, VCP)
- [ ] Combine technical + fundamental + stage filters

**Week 4: Portfolio Management**
- [ ] Build position sizer (based on stop loss)
- [ ] Create portfolio tracker
- [ ] Implement alert system for entries
- [ ] Backtest on 2 years data

### **Phase 2: System 2 - Futures Scalping (Weeks 5-8)**

**Week 5: Price Action Framework**
- [ ] Build hourly range identifier
- [ ] Create breakout/breakdown detector
- [ ] Implement EMA pullback scanner
- [ ] Test on Gold, Silver, Crude, Nifty, Bank Nifty

**Week 6: Pair Trading**
- [ ] Calculate Gold/Silver ratio
- [ ] Build Nifty vs Bank Nifty divergence scanner
- [ ] Create pair trade signal generator
- [ ] Backtest pair trades

**Week 7: Entry/Exit System**
- [ ] Implement precise entry logic (15m confirmation)
- [ ] Build automatic stop loss calculator
- [ ] Create quick target calculator (1-2× risk)
- [ ] Add time-based exit (no movement = exit)

**Week 8: Real-time Monitoring**
- [ ] Build live hourly scanner
- [ ] Create alert system (Telegram/WhatsApp)
- [ ] Daily trade logger
- [ ] Performance dashboard

### **Phase 3: Integration & Testing (Weeks 9-12)**

**Week 9: Both Systems Live (Paper Trading)**
- [ ] Run System 1 on 5 stocks (paper)
- [ ] Run System 2 on 3-5 futures trades daily (paper)
- [ ] Track performance separately
- [ ] Refine parameters

**Week 10: Risk Management Integration**
- [ ] Implement portfolio heat monitoring (max 6% total)
- [ ] Add drawdown protocols
- [ ] Create daily/weekly P&L reports
- [ ] Set up alerts for risk breaches

**Week 11: Optimization**
- [ ] Analyze System 1 performance (win rate, avg hold time)
- [ ] Analyze System 2 performance (win rate, R:R)
- [ ] Adjust parameters based on results
- [ ] Fix any issues

**Week 12: Go Live (Real Money, Small Size)**
- [ ] Start System 1 with 2-3 positions (50% size)
- [ ] Start System 2 with 1 future (50% size)
- [ ] Track everything meticulously
- [ ] Scale up after consistent results

---

## 🧠 **Trading Psychology by System**

### **System 1 Mindset (Investor)**
- **Patient:** Wait for all criteria to align
- **Researcher:** Read financials, understand business
- **Trend follower:** Ride Stage 2, exit Stage 3/4
- **Portfolio thinker:** Diversified across sectors
- **Less stressful:** Weekly checks sufficient

### **System 2 Mindset (Scalper)**
- **Alert:** Watch price action closely
- **Disciplined:** Stop loss non-negotiable
- **Quick:** In and out, no attachment
- **Focused:** 1-2 positions max
- **Reactive:** Price tells you, you don't predict
- **More intense:** Requires active monitoring

---

## 🎯 **Daily Workflow**

### **Morning Routine (30 min)**

**For System 1 (Stocks):**
- Check overnight news for portfolio stocks
- Review sector strength dashboard
- Check if any watchlist stocks triggered (breakout alerts)
- Update stop losses if needed (trail)

**For System 2 (Futures):**
- Check overnight global markets (Gold, Crude)
- Identify support/resistance on hourly charts
- Note key breakout/breakdown levels
- Prepare for 9:15 AM market open

### **Trading Hours (9:15 AM - 3:30 PM)**

**System 1:**
- Execute any pending stock entries (if triggered)
- Monitor portfolio (but don't obsess)
- Update trade log if any trades taken

**System 2:**
- **9:30-11:30 AM:** Active scalping window
  - Watch for breakouts/breakdowns
  - Take 1-2 high-probability setups
  - Book profits quickly (targets hit fast in morning)

- **12:00-2:00 PM:** Lunch break (avoid trading)

- **2:00-3:15 PM:** Second active window
  - Watch for late-day breakouts
  - Close all positions by 3:15 PM (if intraday)
  - Or carry overnight only if strong trend + planned

### **Evening Routine (30 min)**

**For System 1:**
- Run Stage 2 scanner (weekly, not daily)
- Check if any new stocks meet criteria
- Review fundamental news (quarterly earnings season)
- Update watchlist

**For System 2:**
- **Mandatory:** Log all trades (entry, exit, P&L, mistakes)
- Review what worked, what didn't
- Calculate daily P&L, win rate
- Prepare next day's levels (support/resistance)

---

## 📊 **Performance Metrics**

### **System 1 (Stocks) - Target Metrics**
- **Win Rate:** 50-60%
- **Avg Win:** 25%
- **Avg Loss:** 8%
- **Risk:Reward:** 1:3
- **Holding Period:** 30-90 days
- **Annual Return Target:** 30-40%
- **Max Drawdown:** 15%

### **System 2 (Futures) - Target Metrics**
- **Win Rate:** 60-70%
- **Avg Win:** 1.5× risk
- **Avg Loss:** 1× risk
- **Risk:Reward:** 1:1.5
- **Holding Period:** 30 min - 4 hours
- **Daily Return Target:** 0.5-1% (on futures capital)
- **Max Daily Drawdown:** 2%

---

## 🚨 **Risk Management Rules (CRITICAL)**

### **System 1 (Stocks)**
1. **Max risk per trade:** 1% of total capital
2. **Max open positions:** 8 stocks
3. **Max sector exposure:** 30% in one sector
4. **Stop loss mandatory:** 8-10% or technical level
5. **Portfolio heat limit:** 6% max across all positions
6. **Monthly stop:** -10% (pause trading, review)

### **System 2 (Futures)**
1. **Max risk per trade:** 0.5% of total capital
2. **Max positions:** 2 futures at once
3. **Stop loss mandatory:** Placed immediately (30-50 pts)
4. **No averaging down:** One entry only
5. **Daily stop:** -2% (stop trading for the day)
6. **Weekly stop:** -5% (stop trading for week, review)

### **Combined Portfolio**
- **Max portfolio risk at any time:** 6%
- **If total drawdown reaches 15%:** Pause all trading, review system
- **Monthly performance review:** Adjust if needed

---

## 🎓 **Learning Path for Each System**

### **For System 1 (Stocks)**

**Study:**
1. Mark Minervini's "Think & Trade Like a Champion" (Stage Analysis)
2. Stan Weinstein's "Secrets for Profiting in Bull and Bear Markets" (Stage Analysis)
3. William O'Neil's "How to Make Money in Stocks" (CAN SLIM)
4. Your financial statement analysis (balance sheet, cash flow, P&L)

**Practice:**
1. Paper trade 20 Stage 2 stocks
2. Track 3 months of results
3. Refine criteria based on results

### **For System 2 (Futures)**

**Study:**
1. Al Brooks' "Price Action Trading" (Price action mastery)
2. Your existing knowledge base (breakouts, breakdowns)
3. Pair trading literature (correlation, mean reversion)

**Practice:**
1. Paper trade 100 futures scalps
2. Track win rate, R:R
3. Find your edge (which setups work best for you)

---

## ✅ **Quick Decision Checklist**

### **System 1: Should I Buy This Stock?**
```
□ Stock in Stage 2 (above 200 EMA, rising, HH+HL)
□ One of my favorite setups present:
  □ Narrow range consolidation (NR7/NR4)
  □ 200 EMA pullback holding
  □ Base breakout (Cup, Handle, VCP)
□ Fundamentals pass:
  □ Sales growth > 15% YoY
  □ Profit growth > 20% YoY
  □ Operating cash flow positive
  □ ROE > 15%
□ Sector strong (RS > 100)
□ Stock outperforming sector
□ Volume confirming breakout
□ Risk 1% of capital
□ Stop loss defined (8-10% or technical)

If 9+/10 checkmarks: BUY
If 7-8/10: Consider
If <7: SKIP
```

### **System 2: Should I Take This Futures Trade?**
```
□ Clear setup visible:
  □ Breakout above range
  □ Breakdown below support
  □ Trend continuation pullback
  □ Pair trade opportunity
□ Hourly chart confirmation
□ Entry precise (15m or 5m)
□ Stop loss clear (30-50 points)
□ Target defined (1-2× risk)
□ Risk 0.5% of capital
□ Not emotional/revenge trade
□ Peak trading hours (9:30-11:30 or 2-3:15)
□ No other open futures position (or max 2)

If 9+/10 checkmarks: TAKE TRADE
If 7-8/10: Consider
If <7: SKIP (wait for better setup)
```

---

## 🎯 **Success Criteria**

### **After 3 Months:**

**System 1:**
- [ ] Built and running Stage 2 scanner
- [ ] Financial screening automated
- [ ] Taken 10+ stock positions (paper or real)
- [ ] Win rate 50%+
- [ ] Portfolio up 10%+ (if live)

**System 2:**
- [ ] Taken 100+ futures trades (paper or real)
- [ ] Win rate 60%+
- [ ] Avg R:R 1:1.5+
- [ ] Daily P&L positive 60% of days
- [ ] Consistent, not erratic

**Overall:**
- [ ] Clear separation maintained
- [ ] Risk management never breached
- [ ] Enjoying the process
- [ ] Learning from every trade

---

## 🚀 **Let's Get Started**

**Your request was:** "Divide this in two parts... what should be our plan?"

**The plan:**

1. **System 1 (Stocks):** 
   - Build Stage Analysis scanner
   - Add fundamental screening
   - Implement narrow range + 200 EMA setups
   - Portfolio management

2. **System 2 (Futures):**
   - Build hourly breakout/breakdown detector
   - Add pair trading logic
   - Implement tight stop/target management
   - Daily scalping system

**Both systems share:**
- Data collection infrastructure (already built)
- Knowledge base (already built)
- Sectoral analysis (more for System 1)

---

**Next Step:** 
Which system do you want to build first?

**Option A:** Start with System 1 (Stocks) - Stage Analysis
**Option B:** Start with System 2 (Futures) - Price Action Scalping
**Option C:** Build both in parallel (slower but comprehensive)

What's your preference?
