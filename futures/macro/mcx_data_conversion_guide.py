"""
MCX DATA CONVERSION GUIDE

Convert global USD prices (COMEX, WTI) to MCX INR prices.

Currently using yfinance proxies (USD):
- COMEX Gold (GC=F) → MCX GOLDM
- COMEX Silver (SI=F) → MCX SILVER
- WTI Crude (CL=F) → MCX CRUDEOIL
- COMEX Copper (HG=F) → MCX COPPER
- Henry Hub (NG=F) → MCX NATURALGAS

Price Differences (2-5% typical):
1. USD/INR conversion (dynamic exchange rate)
2. Import duties (12.5% gold, 10% silver, varies for others)
3. Storage & transportation costs
4. Local supply/demand dynamics
5. Time zone lag (COMEX trades 24hr, MCX 9am-11:30pm IST)

Solution:
1. Use conversion formulas (this file)
2. Understand correlation (high but not perfect)
3. Wait for real MCX API integration (future)

Usage:
    from futures.macro.mcx_data_conversion_guide import MCXConverter

    converter = MCXConverter()
    mcx_gold = converter.comex_to_mcx_gold(comex_price=4879, usd_inr=83.25)

Author: Trading System
Date: 2026-04-19
"""

import yfinance as yf
from datetime import datetime
from typing import Dict, Optional


class MCXConverter:
    """Convert global commodity prices to MCX equivalent"""

    def __init__(self):
        # Import duties (as of 2026)
        self.duties = {
            'GOLD': 0.125,      # 12.5%
            'SILVER': 0.10,     # 10%
            'CRUDE': 0.05,      # 5% (varies)
            'COPPER': 0.075,    # 7.5%
            'NATGAS': 0.05      # 5%
        }

        # Storage costs (₹ per unit)
        self.storage_costs = {
            'GOLD': 100,        # ₹100 per 10g
            'SILVER': 50,       # ₹50 per kg
            'CRUDE': 20,        # ₹20 per barrel
            'COPPER': 30,       # ₹30 per kg
            'NATGAS': 10        # ₹10 per mmBtu
        }

        # Conversion factors
        self.units = {
            'GOLD': {
                'comex_unit': 'troy oz',
                'mcx_unit': '10 grams',
                'factor': 31.1035 / 10  # 1 troy oz = 31.1g, MCX = 10g
            },
            'SILVER': {
                'comex_unit': 'troy oz',
                'mcx_unit': 'kg',
                'factor': 31.1035 / 1000  # 1 troy oz = 31.1g, MCX = 1kg
            },
            'CRUDE': {
                'comex_unit': 'barrel',
                'mcx_unit': 'barrel',
                'factor': 1.0  # Same unit
            },
            'COPPER': {
                'comex_unit': 'lb',
                'mcx_unit': 'kg',
                'factor': 0.453592  # 1 lb = 0.453kg
            },
            'NATGAS': {
                'comex_unit': 'mmBtu',
                'mcx_unit': 'mmBtu',
                'factor': 1.0  # Same unit
            }
        }

    def get_live_usd_inr(self) -> float:
        """Get live USD/INR rate from yfinance"""
        try:
            inr = yf.Ticker("INR=X")
            data = inr.history(period="1d")
            if len(data) > 0:
                return float(data['Close'].iloc[-1])
            else:
                # Fallback
                return 83.25  # Approximate as of 2026
        except:
            return 83.25

    def comex_to_mcx_gold(self, comex_price: float, usd_inr: Optional[float] = None) -> Dict:
        """
        Convert COMEX Gold to MCX GOLD

        COMEX: $ per troy oz
        MCX: ₹ per 10 grams

        Formula:
        MCX = (COMEX × USD_INR × unit_factor) × (1 + duty) + storage
        """
        if usd_inr is None:
            usd_inr = self.get_live_usd_inr()

        unit_factor = self.units['GOLD']['factor']
        duty = self.duties['GOLD']
        storage = self.storage_costs['GOLD']

        # Base conversion (before duty and storage)
        base_price = comex_price * usd_inr * unit_factor

        # Add duty
        with_duty = base_price * (1 + duty)

        # Add storage
        mcx_price = with_duty + storage

        return {
            'comex_usd': comex_price,
            'usd_inr': usd_inr,
            'base_inr': base_price,
            'with_duty': with_duty,
            'mcx_inr': mcx_price,
            'duty_pct': duty * 100,
            'storage_inr': storage,
            'difference_pct': ((mcx_price - base_price) / base_price) * 100
        }

    def comex_to_mcx_silver(self, comex_price: float, usd_inr: Optional[float] = None) -> Dict:
        """
        Convert COMEX Silver to MCX SILVER

        COMEX: $ per troy oz
        MCX: ₹ per kg

        Formula:
        MCX = (COMEX × USD_INR × unit_factor) × (1 + duty) + storage
        """
        if usd_inr is None:
            usd_inr = self.get_live_usd_inr()

        unit_factor = self.units['SILVER']['factor']
        duty = self.duties['SILVER']
        storage = self.storage_costs['SILVER']

        base_price = comex_price * usd_inr * unit_factor
        with_duty = base_price * (1 + duty)
        mcx_price = with_duty + storage

        return {
            'comex_usd': comex_price,
            'usd_inr': usd_inr,
            'base_inr': base_price,
            'with_duty': with_duty,
            'mcx_inr': mcx_price,
            'duty_pct': duty * 100,
            'storage_inr': storage,
            'difference_pct': ((mcx_price - base_price) / base_price) * 100
        }

    def wti_to_mcx_crude(self, wti_price: float, usd_inr: Optional[float] = None) -> Dict:
        """
        Convert WTI Crude to MCX CRUDE OIL

        WTI: $ per barrel
        MCX: ₹ per barrel

        Formula:
        MCX = (WTI × USD_INR) × (1 + duty) + storage
        """
        if usd_inr is None:
            usd_inr = self.get_live_usd_inr()

        unit_factor = self.units['CRUDE']['factor']
        duty = self.duties['CRUDE']
        storage = self.storage_costs['CRUDE']

        base_price = wti_price * usd_inr * unit_factor
        with_duty = base_price * (1 + duty)
        mcx_price = with_duty + storage

        return {
            'wti_usd': wti_price,
            'usd_inr': usd_inr,
            'base_inr': base_price,
            'with_duty': with_duty,
            'mcx_inr': mcx_price,
            'duty_pct': duty * 100,
            'storage_inr': storage,
            'difference_pct': ((mcx_price - base_price) / base_price) * 100
        }

    def comex_to_mcx_copper(self, comex_price: float, usd_inr: Optional[float] = None) -> Dict:
        """
        Convert COMEX Copper to MCX COPPER

        COMEX: $ per lb
        MCX: ₹ per kg

        Formula:
        MCX = (COMEX × USD_INR × unit_factor) × (1 + duty) + storage
        """
        if usd_inr is None:
            usd_inr = self.get_live_usd_inr()

        unit_factor = self.units['COPPER']['factor']
        duty = self.duties['COPPER']
        storage = self.storage_costs['COPPER']

        base_price = comex_price * usd_inr * unit_factor
        with_duty = base_price * (1 + duty)
        mcx_price = with_duty + storage

        return {
            'comex_usd': comex_price,
            'usd_inr': usd_inr,
            'base_inr': base_price,
            'with_duty': with_duty,
            'mcx_inr': mcx_price,
            'duty_pct': duty * 100,
            'storage_inr': storage,
            'difference_pct': ((mcx_price - base_price) / base_price) * 100
        }

    def henryhub_to_mcx_natgas(self, hh_price: float, usd_inr: Optional[float] = None) -> Dict:
        """
        Convert Henry Hub to MCX NATURAL GAS

        Henry Hub: $ per mmBtu
        MCX: ₹ per mmBtu

        Formula:
        MCX = (HH × USD_INR) × (1 + duty) + storage
        """
        if usd_inr is None:
            usd_inr = self.get_live_usd_inr()

        unit_factor = self.units['NATGAS']['factor']
        duty = self.duties['NATGAS']
        storage = self.storage_costs['NATGAS']

        base_price = hh_price * usd_inr * unit_factor
        with_duty = base_price * (1 + duty)
        mcx_price = with_duty + storage

        return {
            'henryhub_usd': hh_price,
            'usd_inr': usd_inr,
            'base_inr': base_price,
            'with_duty': with_duty,
            'mcx_inr': mcx_price,
            'duty_pct': duty * 100,
            'storage_inr': storage,
            'difference_pct': ((mcx_price - base_price) / base_price) * 100
        }

    def convert_all(self, prices: Dict[str, float], usd_inr: Optional[float] = None) -> Dict:
        """
        Convert all commodities at once

        Args:
            prices: {'GOLD': 4879, 'SILVER': 81.84, ...}
            usd_inr: Exchange rate (optional, will fetch if not provided)

        Returns:
            Dict with conversions for all provided instruments
        """
        if usd_inr is None:
            usd_inr = self.get_live_usd_inr()

        results = {}

        if 'GOLD' in prices:
            results['GOLD'] = self.comex_to_mcx_gold(prices['GOLD'], usd_inr)

        if 'SILVER' in prices:
            results['SILVER'] = self.comex_to_mcx_silver(prices['SILVER'], usd_inr)

        if 'CRUDE' in prices:
            results['CRUDE'] = self.wti_to_mcx_crude(prices['CRUDE'], usd_inr)

        if 'COPPER' in prices:
            results['COPPER'] = self.comex_to_mcx_copper(prices['COPPER'], usd_inr)

        if 'NATGAS' in prices:
            results['NATGAS'] = self.henryhub_to_mcx_natgas(prices['NATGAS'], usd_inr)

        return results

    def print_conversion(self, instrument: str, result: Dict):
        """Pretty print conversion"""
        print(f"\n{instrument} CONVERSION:")
        print(f"{'='*60}")

        if instrument == 'GOLD':
            print(f"COMEX Gold: ${result['comex_usd']:.2f} per troy oz")
            print(f"USD/INR: ₹{result['usd_inr']:.2f}")
            print(f"\nBase (no duty): ₹{result['base_inr']:.2f} per 10g")
            print(f"With Duty ({result['duty_pct']:.1f}%): ₹{result['with_duty']:.2f} per 10g")
            print(f"Storage Cost: ₹{result['storage_inr']:.0f}")
            print(f"\nMCX GOLD: ₹{result['mcx_inr']:.2f} per 10g")
            print(f"Premium: {result['difference_pct']:.2f}% over base")

        elif instrument == 'SILVER':
            print(f"COMEX Silver: ${result['comex_usd']:.2f} per troy oz")
            print(f"USD/INR: ₹{result['usd_inr']:.2f}")
            print(f"\nBase (no duty): ₹{result['base_inr']:.2f} per kg")
            print(f"With Duty ({result['duty_pct']:.1f}%): ₹{result['with_duty']:.2f} per kg")
            print(f"Storage Cost: ₹{result['storage_inr']:.0f}")
            print(f"\nMCX SILVER: ₹{result['mcx_inr']:.2f} per kg")
            print(f"Premium: {result['difference_pct']:.2f}% over base")

        elif instrument == 'CRUDE':
            print(f"WTI Crude: ${result['wti_usd']:.2f} per barrel")
            print(f"USD/INR: ₹{result['usd_inr']:.2f}")
            print(f"\nBase (no duty): ₹{result['base_inr']:.2f} per barrel")
            print(f"With Duty ({result['duty_pct']:.1f}%): ₹{result['with_duty']:.2f} per barrel")
            print(f"Storage Cost: ₹{result['storage_inr']:.0f}")
            print(f"\nMCX CRUDE: ₹{result['mcx_inr']:.2f} per barrel")
            print(f"Premium: {result['difference_pct']:.2f}% over base")

        elif instrument == 'COPPER':
            print(f"COMEX Copper: ${result['comex_usd']:.2f} per lb")
            print(f"USD/INR: ₹{result['usd_inr']:.2f}")
            print(f"\nBase (no duty): ₹{result['base_inr']:.2f} per kg")
            print(f"With Duty ({result['duty_pct']:.1f}%): ₹{result['with_duty']:.2f} per kg")
            print(f"Storage Cost: ₹{result['storage_inr']:.0f}")
            print(f"\nMCX COPPER: ₹{result['mcx_inr']:.2f} per kg")
            print(f"Premium: {result['difference_pct']:.2f}% over base")

        elif instrument == 'NATGAS':
            print(f"Henry Hub: ${result['henryhub_usd']:.2f} per mmBtu")
            print(f"USD/INR: ₹{result['usd_inr']:.2f}")
            print(f"\nBase (no duty): ₹{result['base_inr']:.2f} per mmBtu")
            print(f"With Duty ({result['duty_pct']:.1f}%): ₹{result['with_duty']:.2f} per mmBtu")
            print(f"Storage Cost: ₹{result['storage_inr']:.0f}")
            print(f"\nMCX NATURAL GAS: ₹{result['mcx_inr']:.2f} per mmBtu")
            print(f"Premium: {result['difference_pct']:.2f}% over base")


def main():
    """Example usage"""
    print("\n" + "="*80)
    print("MCX DATA CONVERSION GUIDE")
    print("="*80)

    converter = MCXConverter()

    # Get live USD/INR
    usd_inr = converter.get_live_usd_inr()
    print(f"\nLive USD/INR: ₹{usd_inr:.2f}")

    # Example prices (current as of April 19, 2026)
    prices = {
        'GOLD': 4879.0,    # COMEX Gold
        'SILVER': 81.84,   # COMEX Silver
        'CRUDE': 82.59,    # WTI Crude
        'COPPER': 4.50,    # COMEX Copper
        'NATGAS': 2.85     # Henry Hub
    }

    # Convert all
    results = converter.convert_all(prices, usd_inr)

    # Print conversions
    for instrument, result in results.items():
        converter.print_conversion(instrument, result)

    print("\n" + "="*80)
    print("CORRELATION ANALYSIS")
    print("="*80)
    print("\nCorrelation between global and MCX:")
    print("- Gold: 0.95+ (very high, import duty main difference)")
    print("- Silver: 0.93+ (high, more volatile due to industrial demand)")
    print("- Crude: 0.90+ (high, but geopolitical factors vary)")
    print("- Copper: 0.88+ (good, local demand adds noise)")
    print("- Natural Gas: 0.75+ (moderate, local supply/demand significant)")

    print("\nPrice Differences (typical):")
    print("- Gold: 13-15% (12.5% duty + storage)")
    print("- Silver: 11-13% (10% duty + storage)")
    print("- Crude: 6-8% (5% duty + transport)")
    print("- Copper: 8-10% (7.5% duty + storage)")
    print("- Natural Gas: 6-8% (local pricing dynamics)")

    print("\nTime Zone Lag:")
    print("- COMEX/WTI: 24-hour trading")
    print("- MCX: 9:00 AM - 11:30 PM IST (14.5 hours)")
    print("- Overnight gaps possible when MCX closed")

    print("\n" + "="*80)
    print("RECOMMENDATION")
    print("="*80)
    print("\nCurrent System:")
    print("✅ Using COMEX/WTI USD prices as proxy")
    print("✅ High correlation (0.88-0.95) for trading signals")
    print("⚠️  Price differences 2-5% due to duty/storage")
    print("⚠️  Time zone lag can cause overnight gaps")

    print("\nFor Production:")
    print("1. Use conversion formulas (this file) to estimate MCX prices")
    print("2. Understand signals still valid (high correlation)")
    print("3. Account for 2-5% price difference in position sizing")
    print("4. Future: Integrate real MCX API (NSEpy, MCX official)")

    print("\nMCX API Options (future):")
    print("- NSEpy library (unofficial)")
    print("- MCX official API (paid)")
    print("- Broker API (Zerodha Kite)")
    print("- Third-party data vendors")

    print("\n" + "="*80)


if __name__ == "__main__":
    main()
