# MCX CONTRACT QUICK REFERENCE
## For ₹12 Lakh Capital Trading

**Last Updated:** April 19, 2026  
**⚠️ VERIFY ALL SPECS WITH ZERODHA BEFORE TRADING**

---

## CONTRACTS SUITABLE FOR ₹12L CAPITAL

### ✅ TIER 1: BEST FOR RETAIL (Liquid + Right Size)

| Contract | Lot Size | Contract Value | Margin (NRML) | Margin (MIS) | Liquidity | Use Case |
|----------|----------|----------------|---------------|--------------|-----------|----------|
| **GOLDM** | 100g | ₹72,000 | ₹4,500 | ₹2,250 | GOOD | Gold pairs - can trade 10-50 lots |
| **SILVERM** | 5kg | ₹6,10,000 | ₹38,000 | ₹19,000 | GOOD | Silver pairs - can trade 3-7 lots |
| **CRUDEOIL** | 100bbl | ₹7,00,000 | ₹45,000 | ₹22,500 | EXCELLENT | Crude pairs - can trade 4-10 lots |
| **CRUDEOILM** | 10bbl | ₹70,000 | ₹4,500 | ₹2,250 | FAIR | Fine-tuning - can trade 20-50 lots |

### ⚠️ TIER 2: USABLE WITH CAUTION

| Contract | Lot Size | Contract Value | Margin (NRML) | Margin (MIS) | Liquidity | Issue |
|----------|----------|----------------|---------------|--------------|-----------|-------|
| **COPPER** | 1 MT | ₹8,45,000 | ₹50,000 | ₹25,000 | GOOD | Large lot = 1-3 lots max |
| **ZINC** | 5 MT | ₹13,25,000 | ₹80,000 | ₹40,000 | FAIR | Very large = 1-2 lots max |
| **NATURALGAS** | 1250 mmBtu | ₹2,96,000 | ₹18,000 | ₹9,000 | GOOD | High volatility, overnight gaps |

### ❌ TIER 3: AVOID

| Contract | Lot Size | Why Avoid |
|----------|----------|-----------|
| **GOLD** (regular) | 1kg | ₹7.2L contract = too large, use GOLDM instead |
| **SILVER** (regular) | 30kg | ₹36.6L contract = too large, use SILVERM instead |
| **GOLDGUINEA** | 8g | ₹5,760 contract = poor liquidity, wide spreads |
| **SILVERMICRO** | 1kg | Unverified availability, likely illiquid |

---

## POSITION SIZING EXAMPLES

### Example 1: Crude/Gold Pair (25% allocation = ₹3L)

**Leg 1: LONG 4 lots CRUDEOIL**
- Margin: 4 × ₹45,000 = ₹1,80,000
- Exposure: 4 × ₹7,00,000 = ₹28,00,000

**Leg 2: SHORT 40 lots GOLDM**
- Margin: 40 × ₹4,500 = ₹1,80,000
- Exposure: 40 × ₹72,000 = ₹28,80,000

**Total margin:** ₹3,60,000 (leaves ₹8.4L for other trades/buffer)  
**Risk (15% stop):** ₹4.2L loss = 3.5% of capital ✅

---

### Example 2: Silver/Copper Pair (20% allocation = ₹2.4L)

**Leg 1: SHORT 3 lots SILVERM**
- Margin: 3 × ₹38,000 = ₹1,14,000
- Exposure: 3 × ₹6,10,000 = ₹18,30,000

**Leg 2: LONG 2 lots COPPER**
- Margin: 2 × ₹50,000 = ₹1,00,000
- Exposure: 2 × ₹8,45,000 = ₹16,90,000

**Total margin:** ₹2,14,000  
**Risk (20% stop):** ₹7L loss = 5.8% of capital ✅

---

## LIQUIDITY CHECK (Before Trading)

**EXCELLENT Liquidity (Trade Anytime):**
- CRUDEOIL: 50,000+ lots/day
- GOLD: 100,000+ lots/day
- GOLDM: 30,000+ lots/day
- SILVER: 40,000+ lots/day

**GOOD Liquidity (Trade During Peak Hours):**
- SILVERM: 10,000+ lots/day
- COPPER: 15,000+ lots/day
- NATURALGAS: 20,000+ lots/day

**FAIR Liquidity (Check Spreads First):**
- ZINC: 5,000+ lots/day
- CRUDEOILM: 3,000+ lots/day

**POOR Liquidity (Avoid):**
- GOLDGUINEA: <1,000 lots/day
- Any micro contracts: <500 lots/day

---

## MARGIN REQUIREMENTS

**NRML (Normal - Overnight Holding):**
- Typically 5-7% of contract value
- Use for multi-day/week positions
- No intraday benefit

**MIS (Margin Intraday Square-off):**
- Typically 3-3.5% of contract value (half of NRML)
- Must close by 11:15 PM same day
- Better for day trades or active management

**⚠️ Margins change based on volatility!**
- During high volatility: can go up to 10-15%
- Check current margins on Zerodha before trading
- Keep 40% extra buffer for adverse moves

---

## OPTIMAL TRADING HOURS (MCX)

**Market Hours:** 9:00 AM - 11:30 PM IST (most contracts)

**❌ AVOID:**
- 9:00-9:15 AM (opening volatility)
- 11:15-11:30 PM (closing volatility)
- During major news events (RBI, US Fed, inventory reports)

**✅ BEST TIMES:**
1. **2:00-4:00 PM IST** (London open, HIGH priority)
2. **7:00-10:00 PM IST** (US open, HIGHEST priority)
3. **9:30-11:30 AM IST** (Post-opening settle, MEDIUM priority)

---

## KEY RATIOS TO WATCH

| Ratio | Current | Mean | Z-Score | Signal | Recommended Allocation |
|-------|---------|------|---------|--------|----------------------|
| **Crude/Gold** | 0.017 | 0.028 | -1.14σ | BUY ratio | 20-25% ✅ |
| **Crude/Silver** | 1.009 | 2.352 | -1.55σ | BUY ratio | 20-25% ✅ |
| **Silver/Copper** | 13.38 | 7.85 | +2.24σ | SELL ratio | 15-20% ⚠️ |
| **Gold/Silver** | 59.6 | 82.9 | -2.38σ | BUY ratio | 10-15% ⚠️ |
| **Copper/Zinc** | 0.055 | 0.040 | +2.50σ | AVOID | Max 10% ❌ |

**Legend:**
- ✅ = Strong fundamental support for mean reversion
- ⚠️ = Partial structural shift, trade smaller
- ❌ = Structural shift, high risk

---

## CRITICAL CHECKLIST BEFORE TRADING

### Pre-Trade:
- [ ] Verified contract specs with Zerodha
- [ ] Checked current open interest (>1000 contracts)
- [ ] Checked bid-ask spread (<0.1%)
- [ ] Confirmed margin availability (70% of allocation)
- [ ] Set stop loss levels (15-20% of position)
- [ ] Trading during optimal hours (2-4 PM or 7-10 PM)
- [ ] Reserved 40% capital as buffer

### During Trade:
- [ ] Using LIMIT orders (not market)
- [ ] Stop loss orders placed immediately after entry
- [ ] Position sizing correct (not over-leveraged)
- [ ] Monitoring both legs of pair trade
- [ ] Avoiding adding to losing positions

### Post-Trade:
- [ ] Reviewing daily P&L
- [ ] Checking if fundamental thesis intact
- [ ] Adjusting stops to breakeven if 10% profit
- [ ] Planning rollover (if holding past expiry)
- [ ] Keeping trade journal updated

---

## RISK MANAGEMENT RULES

**Position Limits:**
1. Max 40% allocation per pair trade
2. Max 70% total margin utilization
3. Keep 30-40% cash reserve always

**Stop Loss Rules:**
1. Set stop = 15-20% of position value
2. NEVER remove stop loss to "avoid getting stopped out"
3. Use OCO orders if available
4. If stopped out, wait 1 day before re-entering

**Time Stops:**
1. Review fundamentals monthly
2. Exit after 6 months if no progress (even without stop hit)
3. Don't hold through multiple contract rollovers (costs add up)

**Margin Management:**
1. Keep ₹5L separate emergency fund for margin calls
2. If margin call received, reduce position (don't add money)
3. If volatility increases, reduce position size proportionally

---

## COMMON MISTAKES TO AVOID

1. ❌ **Trading GOLDGUINEA for "small size"**
   - Illiquid, wide spreads, poor fills
   - Use GOLDM instead (10x bigger but much better liquidity)

2. ❌ **Using all margin buying power**
   - Leaves no room for adverse moves
   - Overnight gaps can wipe you out
   - Always keep 40% buffer

3. ❌ **Ignoring rollover costs**
   - MCX futures expire monthly
   - Rollover = exit old contract + enter new = 2 trades
   - Costs 0.5-1% per leg = 1-2% total
   - Factor this into targets

4. ❌ **Chasing with market orders**
   - MCX spreads can be 0.1-0.2%
   - Market orders in illiquid contracts = bad fills
   - Always use limit orders, be patient

5. ❌ **Holding through major events**
   - US Fed, RBI, weekly oil inventory, OPEC meetings
   - Volatility spikes = margin calls
   - Reduce position before events, re-enter after

6. ❌ **Treating pair trade as two separate trades**
   - Both legs must be sized proportionally
   - If one leg stopped out, close other leg too
   - Don't let pair become directional bet

---

## IMPORTANT DISCLAIMERS

**⚠️ Contract Specifications:**
- Based on April 2026 industry standards
- Margins change daily with volatility
- Mini contract availability varies
- **MUST verify with Zerodha before trading**

**⚠️ Liquidity:**
- Can deteriorate during high volatility
- Check current open interest/volume
- May vary by contract month (trade near month)

**⚠️ Prices:**
- Using USD global prices converted to INR
- Actual MCX prices differ by 2-5% (import duty, storage)
- Correlations high (0.88-0.95) but not perfect

**⚠️ Fundamental Research:**
- Based on April 19, 2026 web research
- Market conditions change rapidly
- Review fundamentals monthly
- Don't blindly trade historical ratios

---

## QUICK DECISION TREE

```
Do you have ₹12L capital?
│
├─ NO → Don't trade MCX futures (too risky)
│
└─ YES → Continue
    │
    ├─ Is ratio at >1.5σ deviation?
    │   ├─ NO → Wait for better setup
    │   └─ YES → Continue
    │
    ├─ Is there fundamental support for mean reversion?
    │   ├─ NO (structural shift) → Reduce size by 50% or AVOID
    │   └─ YES → Continue
    │
    ├─ Are contracts liquid? (Check open interest, spreads)
    │   ├─ NO → Use more liquid alternative (GOLDM vs GOLD)
    │   └─ YES → Continue
    │
    ├─ Can you afford 15-20% stop loss? (Check margin)
    │   ├─ NO → Reduce position size
    │   └─ YES → Continue
    │
    ├─ Is it optimal trading hours? (2-4 PM or 7-10 PM)
    │   ├─ NO → Wait for better timing
    │   └─ YES → ENTER TRADE
    │
    └─ Place stop loss IMMEDIATELY after entry
```

---

**Remember: The goal is NOT to maximize returns, but to maximize risk-adjusted returns while preserving capital.**

*For detailed fundamental analysis, see: COMMODITY_FUNDAMENTALS_RESEARCH_2024_2026.md*
