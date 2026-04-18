"""
Volume Profile Calculator for Futures Trading
Ported from Sierra Chart ACS_Source hurst_exponent_signal_latest.cpp

Volume Profile shows where trading activity occurred at different price levels:
- POC (Point of Control): Price level with highest volume
- HVN (High Volume Nodes): Strong support/resistance zones
- LVN (Low Volume Nodes): Areas of fast price movement
- VAH/VAL (Value Area High/Low): 70% of volume range

Author: Trading System
Date: 2026-04-18
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class VolumeNode:
    """Represents a price level with volume"""
    price: float
    volume: float
    volume_pct: float  # Percentage of total volume


@dataclass
class VolumeProfile:
    """Complete volume profile analysis result"""
    poc: float  # Point of Control (highest volume price)
    vah: float  # Value Area High (top of 70% volume)
    val: float  # Value Area Low (bottom of 70% volume)
    hvn_zones: List[Tuple[float, float]]  # High Volume Node ranges
    lvn_zones: List[Tuple[float, float]]  # Low Volume Node ranges
    total_volume: float
    price_levels: pd.DataFrame  # Price -> Volume mapping

    def is_near_hvn(self, price: float, tolerance: float = 0.005) -> bool:
        """Check if price is near a High Volume Node"""
        for hvn_low, hvn_high in self.hvn_zones:
            if hvn_low * (1 - tolerance) <= price <= hvn_high * (1 + tolerance):
                return True
        return False

    def is_in_lvn(self, price: float) -> bool:
        """Check if price is in a Low Volume Node (fast move zone)"""
        for lvn_low, lvn_high in self.lvn_zones:
            if lvn_low <= price <= lvn_high:
                return True
        return False

    def distance_to_poc(self, price: float) -> float:
        """Calculate distance from current price to POC (in %)"""
        return (price - self.poc) / self.poc * 100

    def get_nearest_hvn(self, price: float, direction: str = 'below') -> Optional[float]:
        """Find nearest HVN level above or below current price"""
        if direction == 'below':
            hvn_levels = [hvn[0] for hvn in self.hvn_zones if hvn[0] < price]
            return max(hvn_levels) if hvn_levels else None
        else:  # above
            hvn_levels = [hvn[1] for hvn in self.hvn_zones if hvn[1] > price]
            return min(hvn_levels) if hvn_levels else None


class VolumeProfileCalculator:
    """
    Calculate Volume Profile using tick-based or price-based binning

    Based on Market Profile methodology (J. Peter Steidlmayer, 1985)
    and Volume Profile extensions in Sierra Chart
    """

    def __init__(self, num_bins: int = 50, value_area_pct: float = 0.70):
        """
        Initialize Volume Profile calculator

        Args:
            num_bins: Number of price levels to analyze (default 50)
            value_area_pct: Percentage for Value Area (default 0.70 = 70%)
        """
        self.num_bins = num_bins
        self.value_area_pct = value_area_pct

        # HVN/LVN detection thresholds (from Sierra Chart)
        self.hvn_threshold = 1.5  # Volume > 1.5x average = HVN
        self.lvn_threshold = 0.5  # Volume < 0.5x average = LVN

    def calculate(
        self,
        data: pd.DataFrame,
        price_col: str = 'Close',
        volume_col: str = 'Volume',
        tick_size: Optional[float] = None
    ) -> VolumeProfile:
        """
        Calculate Volume Profile for given data

        Args:
            data: DataFrame with price and volume columns
            price_col: Name of price column (default 'Close')
            volume_col: Name of volume column (default 'Volume')
            tick_size: Optional tick size for binning (if None, auto-calculate)

        Returns:
            VolumeProfile with POC, VAH, VAL, HVN/LVN zones
        """
        if len(data) == 0:
            raise ValueError("Empty data provided")

        prices = data[price_col].values
        volumes = data[volume_col].values

        # Determine price range
        price_min = prices.min()
        price_max = prices.max()

        # Calculate tick size if not provided
        if tick_size is None:
            tick_size = (price_max - price_min) / self.num_bins

        # Create price bins
        bins = np.arange(price_min, price_max + tick_size, tick_size)

        # Digitize prices into bins
        price_indices = np.digitize(prices, bins) - 1

        # Aggregate volume at each price level
        volume_at_price = np.zeros(len(bins) - 1)
        for idx, vol in zip(price_indices, volumes):
            if 0 <= idx < len(volume_at_price):
                volume_at_price[idx] += vol

        # Create DataFrame of price levels
        bin_centers = (bins[:-1] + bins[1:]) / 2
        total_volume = volume_at_price.sum()

        price_levels = pd.DataFrame({
            'price': bin_centers,
            'volume': volume_at_price,
            'volume_pct': volume_at_price / total_volume * 100
        })

        # Sort by volume (descending)
        price_levels_sorted = price_levels.sort_values('volume', ascending=False)

        # Calculate POC (Point of Control) - highest volume price
        poc_idx = price_levels_sorted.index[0]
        poc = price_levels.loc[poc_idx, 'price']

        # Calculate Value Area (70% of volume)
        vah, val = self._calculate_value_area(price_levels_sorted, total_volume)

        # Identify HVN and LVN zones
        hvn_zones = self._identify_hvn_zones(price_levels)
        lvn_zones = self._identify_lvn_zones(price_levels)

        return VolumeProfile(
            poc=poc,
            vah=vah,
            val=val,
            hvn_zones=hvn_zones,
            lvn_zones=lvn_zones,
            total_volume=total_volume,
            price_levels=price_levels
        )

    def _calculate_value_area(
        self,
        price_levels_sorted: pd.DataFrame,
        total_volume: float
    ) -> Tuple[float, float]:
        """
        Calculate Value Area High and Low (70% of volume)

        Starts from POC and expands up/down until 70% volume captured
        """
        target_volume = total_volume * self.value_area_pct

        # Start from POC (highest volume)
        current_volume = price_levels_sorted.iloc[0]['volume']
        included_prices = [price_levels_sorted.iloc[0]['price']]

        remaining_indices = list(price_levels_sorted.index[1:])

        # Expand value area until we hit 70% volume
        while current_volume < target_volume and remaining_indices:
            # Get next highest volume level
            next_idx = remaining_indices.pop(0)
            next_price = price_levels_sorted.loc[next_idx, 'price']
            next_volume = price_levels_sorted.loc[next_idx, 'volume']

            included_prices.append(next_price)
            current_volume += next_volume

        # VAH = max price in value area, VAL = min price
        vah = max(included_prices)
        val = min(included_prices)

        return vah, val

    def _identify_hvn_zones(self, price_levels: pd.DataFrame) -> List[Tuple[float, float]]:
        """
        Identify High Volume Nodes (strong support/resistance)

        HVN = contiguous price levels with volume > 1.5x average
        """
        avg_volume = price_levels['volume'].mean()
        threshold = avg_volume * self.hvn_threshold

        hvn_mask = price_levels['volume'] >= threshold
        hvn_zones = []

        # Find contiguous HVN regions
        in_hvn = False
        hvn_start = None

        for idx, row in price_levels.iterrows():
            if row['volume'] >= threshold:
                if not in_hvn:
                    hvn_start = row['price']
                    in_hvn = True
            else:
                if in_hvn:
                    hvn_end = price_levels.loc[idx - 1, 'price']
                    hvn_zones.append((hvn_start, hvn_end))
                    in_hvn = False

        # Close final HVN if needed
        if in_hvn:
            hvn_end = price_levels.iloc[-1]['price']
            hvn_zones.append((hvn_start, hvn_end))

        return hvn_zones

    def _identify_lvn_zones(self, price_levels: pd.DataFrame) -> List[Tuple[float, float]]:
        """
        Identify Low Volume Nodes (fast move zones)

        LVN = contiguous price levels with volume < 0.5x average
        """
        avg_volume = price_levels['volume'].mean()
        threshold = avg_volume * self.lvn_threshold

        lvn_zones = []

        # Find contiguous LVN regions
        in_lvn = False
        lvn_start = None

        for idx, row in price_levels.iterrows():
            if row['volume'] <= threshold and row['volume'] > 0:
                if not in_lvn:
                    lvn_start = row['price']
                    in_lvn = True
            else:
                if in_lvn:
                    lvn_end = price_levels.loc[idx - 1, 'price']
                    # Only include significant LVN zones (> 0.5% of price range)
                    if (lvn_end - lvn_start) / lvn_start > 0.005:
                        lvn_zones.append((lvn_start, lvn_end))
                    in_lvn = False

        # Close final LVN if needed
        if in_lvn:
            lvn_end = price_levels.iloc[-1]['price']
            if (lvn_end - lvn_start) / lvn_start > 0.005:
                lvn_zones.append((lvn_start, lvn_end))

        return lvn_zones

    def calculate_rolling(
        self,
        data: pd.DataFrame,
        window: int = 20,
        step: int = 5,
        price_col: str = 'Close',
        volume_col: str = 'Volume'
    ) -> pd.DataFrame:
        """
        Calculate rolling Volume Profile over time

        Args:
            data: DataFrame with price and volume
            window: Rolling window size (days)
            step: Step size between calculations
            price_col: Price column name
            volume_col: Volume column name

        Returns:
            DataFrame with rolling POC, VAH, VAL
        """
        results = []

        for i in range(window, len(data), step):
            window_data = data.iloc[i-window:i]

            try:
                vp = self.calculate(window_data, price_col, volume_col)

                results.append({
                    'timestamp': data.index[i-1],
                    'poc': vp.poc,
                    'vah': vp.vah,
                    'val': vp.val,
                    'num_hvn': len(vp.hvn_zones),
                    'num_lvn': len(vp.lvn_zones)
                })
            except Exception:
                continue

        return pd.DataFrame(results).set_index('timestamp')


def analyze_gold_volume_profile(data: pd.DataFrame, lookback: int = 20) -> VolumeProfile:
    """
    Quick helper to analyze Gold futures volume profile

    Args:
        data: DataFrame with Close and Volume columns
        lookback: Days to analyze (default 20)

    Returns:
        VolumeProfile with POC, VAH, VAL, HVN/LVN zones
    """
    calculator = VolumeProfileCalculator()
    recent_data = data.iloc[-lookback:]
    return calculator.calculate(recent_data)


if __name__ == "__main__":
    print("Volume Profile Calculator")
    print("=" * 50)
    print("\nUsage:")
    print("  from futures.indicators.volume_profile import analyze_gold_volume_profile")
    print("  vp = analyze_gold_volume_profile(gold_data)")
    print("  print(f'POC: {vp.poc}')")
    print("  print(f'VAH: {vp.vah}, VAL: {vp.val}')")
    print("  print(f'HVN Zones: {vp.hvn_zones}')")
