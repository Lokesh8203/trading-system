"""
Index Data Collector for NSE Indices

Collects data for:
- Standard NSE indices
- Sectoral indices
- Custom-built indices (calculated from constituents)

Provides:
- Historical index data
- Real-time index values
- Constituent-based index calculation
- Relative strength analysis across indices
- Sectoral rotation detection
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
import logging
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from collectors.free_data import FreeDataCollector
from indices.nse_indices_config import (
    ALL_INDICES, CUSTOM_INDICES, get_index_config,
    get_custom_indices, get_index_group, WATCHLIST_PRESETS
)

logger = logging.getLogger(__name__)


class IndexCollector:
    """
    Collects and calculates index data for NSE indices.

    Features:
    - Fetch standard index data
    - Calculate custom indices from constituents
    - Relative strength analysis
    - Sectoral strength comparison
    - Index health metrics
    """

    def __init__(self, data_collector: FreeDataCollector = None):
        """
        Initialize IndexCollector.

        Args:
            data_collector: Optional FreeDataCollector instance
        """
        self.data_collector = data_collector or FreeDataCollector()
        logger.info("IndexCollector initialized")

    def get_index_data(
        self,
        index_symbol: str,
        start_date: datetime,
        end_date: datetime,
        interval: str = '1d'
    ) -> pd.DataFrame:
        """
        Get historical data for an index.

        For custom indices, calculates from constituents.
        For standard indices, fetches from data source.

        Args:
            index_symbol: Index symbol (e.g., 'NIFTY50', 'NIFTY_CHEMICALS_CUSTOM')
            start_date: Start date
            end_date: End date
            interval: Data interval

        Returns:
            DataFrame with OHLCV data
        """
        config = get_index_config(index_symbol)

        if not config:
            logger.error(f"Index {index_symbol} not found in configuration")
            return pd.DataFrame()

        if config.is_custom and config.constituents:
            # Calculate custom index from constituents
            return self._calculate_custom_index(
                config.constituents,
                start_date,
                end_date,
                interval
            )
        else:
            # Fetch standard index data
            if config.yahoo_symbol:
                return self.data_collector.get_historical_data(
                    config.yahoo_symbol,
                    start_date,
                    end_date,
                    interval
                )
            else:
                logger.warning(f"No Yahoo symbol for {index_symbol}, cannot fetch data")
                return pd.DataFrame()

    def _calculate_custom_index(
        self,
        constituents: List[str],
        start_date: datetime,
        end_date: datetime,
        interval: str
    ) -> pd.DataFrame:
        """
        Calculate custom index from constituent stocks.

        Uses equal-weighted methodology:
        - Each stock has equal weight
        - Index value = average of all constituent returns
        - Base value = 1000

        Args:
            constituents: List of stock symbols
            start_date: Start date
            end_date: End date
            interval: Data interval

        Returns:
            DataFrame with calculated index values
        """
        try:
            logger.info(f"Calculating custom index from {len(constituents)} constituents")

            # Fetch data for all constituents
            constituent_data = {}
            for symbol in constituents:
                df = self.data_collector.get_historical_data(
                    symbol,
                    start_date,
                    end_date,
                    interval
                )
                if not df.empty:
                    constituent_data[symbol] = df['Close']

            if not constituent_data:
                logger.warning("No constituent data available")
                return pd.DataFrame()

            # Create DataFrame of all closes
            closes = pd.DataFrame(constituent_data)

            # Calculate equal-weighted returns
            returns = closes.pct_change()
            avg_returns = returns.mean(axis=1)

            # Calculate index values (base = 1000)
            base_value = 1000
            index_values = base_value * (1 + avg_returns).cumprod()

            # Create OHLCV approximation
            # For custom indices, we'll just use Close
            # Open = previous close, High/Low = Close (approximation)
            result = pd.DataFrame({
                'Date': closes.index,
                'Open': index_values.shift(1).fillna(base_value),
                'High': index_values,  # Approximation
                'Low': index_values,   # Approximation
                'Close': index_values,
                'Volume': closes.count(axis=1)  # Number of constituents with data
            })

            result = result.dropna()
            logger.info(f"Calculated custom index: {len(result)} rows")

            return result

        except Exception as e:
            logger.error(f"Error calculating custom index: {e}")
            return pd.DataFrame()

    def get_multiple_indices(
        self,
        index_symbols: List[str],
        start_date: datetime,
        end_date: datetime,
        interval: str = '1d'
    ) -> Dict[str, pd.DataFrame]:
        """
        Fetch data for multiple indices.

        Args:
            index_symbols: List of index symbols
            start_date: Start date
            end_date: End date
            interval: Data interval

        Returns:
            Dictionary mapping index symbol to DataFrame
        """
        results = {}

        for symbol in index_symbols:
            logger.info(f"Fetching {symbol}...")
            df = self.get_index_data(symbol, start_date, end_date, interval)
            if not df.empty:
                results[symbol] = df

        return results

    def calculate_relative_strength(
        self,
        index_symbol: str,
        benchmark_symbol: str,
        start_date: datetime,
        end_date: datetime,
        lookback_period: int = 20
    ) -> pd.DataFrame:
        """
        Calculate relative strength of an index vs. benchmark.

        RS = (Index / Benchmark) * 100
        RS > 100: Outperforming benchmark
        RS < 100: Underperforming benchmark

        Args:
            index_symbol: Index to analyze
            benchmark_symbol: Benchmark index (typically NIFTY50)
            start_date: Start date
            end_date: End date
            lookback_period: Period for RS calculations

        Returns:
            DataFrame with RS metrics
        """
        # Fetch data
        index_data = self.get_index_data(index_symbol, start_date, end_date)
        benchmark_data = self.get_index_data(benchmark_symbol, start_date, end_date)

        if index_data.empty or benchmark_data.empty:
            logger.warning(f"Insufficient data for RS calculation")
            return pd.DataFrame()

        # Align dates
        merged = pd.merge(
            index_data[['Date', 'Close']],
            benchmark_data[['Date', 'Close']],
            on='Date',
            suffixes=('_index', '_benchmark')
        )

        # Calculate RS
        merged['RS'] = (merged['Close_index'] / merged['Close_benchmark']) * 100

        # Calculate RS moving average
        merged[f'RS_MA{lookback_period}'] = merged['RS'].rolling(
            window=lookback_period
        ).mean()

        # Calculate RS Rate of Change
        merged['RS_ROC'] = merged['RS'].pct_change(lookback_period) * 100

        # Outperformance flag
        merged['Outperforming'] = merged['RS'] > 100

        # Momentum
        merged['RS_Momentum'] = merged['RS'] > merged[f'RS_MA{lookback_period}']

        return merged

    def scan_sectoral_strength(
        self,
        sectors: List[str] = None,
        lookback_days: int = 30,
        benchmark: str = 'NIFTY50'
    ) -> pd.DataFrame:
        """
        Scan relative strength of all sectors.

        Args:
            sectors: List of sectoral index symbols (None = all)
            lookback_days: Analysis period
            benchmark: Benchmark index

        Returns:
            DataFrame ranked by relative strength
        """
        if sectors is None:
            sectors = get_index_group('core_sectors')

        end_date = datetime.now()
        start_date = end_date - timedelta(days=lookback_days)

        results = []

        for sector in sectors:
            try:
                # Get performance
                sector_data = self.get_index_data(sector, start_date, end_date)

                if sector_data.empty or len(sector_data) < 2:
                    continue

                # Calculate returns
                first_close = sector_data.iloc[0]['Close']
                last_close = sector_data.iloc[-1]['Close']
                returns = ((last_close - first_close) / first_close) * 100

                # Calculate RS
                rs_df = self.calculate_relative_strength(
                    sector, benchmark, start_date, end_date
                )

                if not rs_df.empty:
                    latest_rs = rs_df.iloc[-1]['RS']
                    rs_momentum = rs_df.iloc[-1]['RS_Momentum']
                else:
                    latest_rs = 0
                    rs_momentum = False

                config = get_index_config(sector)

                results.append({
                    'Index': sector,
                    'Sector': config.sector if config else 'Unknown',
                    'Returns_%': round(returns, 2),
                    'RS': round(latest_rs, 2),
                    'RS_Momentum': rs_momentum,
                    'Outperforming': latest_rs > 100,
                    'Strength': 'Strong' if (returns > 0 and latest_rs > 100) else
                               'Moderate' if returns > 0 else 'Weak'
                })

            except Exception as e:
                logger.error(f"Error scanning {sector}: {e}")
                continue

        # Create DataFrame and sort by returns
        df = pd.DataFrame(results)
        df = df.sort_values('Returns_%', ascending=False)

        return df

    def find_rotation_opportunities(
        self,
        lookback_days: int = 30
    ) -> Dict[str, List[str]]:
        """
        Identify sectoral rotation opportunities.

        Categorizes sectors into:
        - Leaders: Outperforming and accelerating
        - Laggards: Underperforming but improving
        - Weakening: Was strong, now declining
        - Avoid: Underperforming and declining

        Args:
            lookback_days: Analysis period

        Returns:
            Dictionary categorizing sectors
        """
        # Scan all core sectors
        sectors = get_index_group('core_sectors')
        strength_df = self.scan_sectoral_strength(sectors, lookback_days)

        if strength_df.empty:
            return {}

        # Categorize
        leaders = strength_df[
            (strength_df['Returns_%'] > 0) &
            (strength_df['RS_Momentum'] == True) &
            (strength_df['Outperforming'] == True)
        ]['Index'].tolist()

        laggards = strength_df[
            (strength_df['Returns_%'] > 0) &
            (strength_df['Outperforming'] == False)
        ]['Index'].tolist()

        weakening = strength_df[
            (strength_df['Returns_%'] > 0) &
            (strength_df['RS_Momentum'] == False)
        ]['Index'].tolist()

        avoid = strength_df[
            (strength_df['Returns_%'] < 0)
        ]['Index'].tolist()

        return {
            'leaders': leaders,
            'laggards_improving': laggards,
            'weakening': weakening,
            'avoid': avoid
        }

    def get_watchlist_data(
        self,
        watchlist_name: str,
        days: int = 30
    ) -> Dict[str, pd.DataFrame]:
        """
        Get data for a predefined watchlist.

        Args:
            watchlist_name: Name from WATCHLIST_PRESETS
            days: Number of days of historical data

        Returns:
            Dictionary of index data
        """
        indices = WATCHLIST_PRESETS.get(watchlist_name, [])

        if not indices:
            logger.warning(f"Watchlist '{watchlist_name}' not found")
            return {}

        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        return self.get_multiple_indices(indices, start_date, end_date)

    def calculate_breadth(
        self,
        index_symbol: str,
        start_date: datetime,
        end_date: datetime
    ) -> pd.DataFrame:
        """
        Calculate market breadth for custom indices.

        Breadth = % of constituents above their moving average

        Args:
            index_symbol: Custom index symbol
            start_date: Start date
            end_date: End date

        Returns:
            DataFrame with breadth metrics
        """
        config = get_index_config(index_symbol)

        if not config or not config.is_custom or not config.constituents:
            logger.error(f"{index_symbol} is not a custom index with constituents")
            return pd.DataFrame()

        try:
            # Fetch constituent data
            constituent_data = {}
            for symbol in config.constituents:
                df = self.data_collector.get_historical_data(
                    symbol, start_date, end_date
                )
                if not df.empty:
                    constituent_data[symbol] = df.set_index('Date')['Close']

            if not constituent_data:
                return pd.DataFrame()

            # Create DataFrame
            closes = pd.DataFrame(constituent_data)

            # Calculate 50-day MA for each constituent
            mas = closes.rolling(window=50).mean()

            # Calculate breadth (% above MA)
            above_ma = closes > mas
            breadth = (above_ma.sum(axis=1) / len(config.constituents)) * 100

            # Create result DataFrame
            result = pd.DataFrame({
                'Date': closes.index,
                'Breadth_%': breadth,
                'Constituents_Above_MA': above_ma.sum(axis=1),
                'Total_Constituents': len(config.constituents)
            })

            # Add breadth interpretation
            result['Breadth_Signal'] = result['Breadth_%'].apply(
                lambda x: 'Strong' if x > 70 else
                         'Moderate' if x > 50 else
                         'Weak' if x > 30 else 'Very Weak'
            )

            return result

        except Exception as e:
            logger.error(f"Error calculating breadth: {e}")
            return pd.DataFrame()


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

def quick_sector_scan(days: int = 30) -> pd.DataFrame:
    """
    Quick scan of all sectors.

    Args:
        days: Lookback period

    Returns:
        DataFrame with sector performance
    """
    collector = IndexCollector()
    return collector.scan_sectoral_strength(lookback_days=days)


def find_strongest_sectors(top_n: int = 5, days: int = 30) -> List[str]:
    """
    Find top N strongest sectors.

    Args:
        top_n: Number of top sectors to return
        days: Lookback period

    Returns:
        List of strongest sector index symbols
    """
    scan = quick_sector_scan(days)
    if scan.empty:
        return []
    return scan.head(top_n)['Index'].tolist()


def get_rotation_report(days: int = 30) -> Dict:
    """
    Get comprehensive rotation report.

    Args:
        days: Lookback period

    Returns:
        Dictionary with rotation analysis
    """
    collector = IndexCollector()
    return collector.find_rotation_opportunities(days)


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)

    print("\n" + "="*70)
    print("INDEX COLLECTOR DEMO")
    print("="*70)

    collector = IndexCollector()

    # 1. Sector Strength Scan
    print("\n📊 SECTOR STRENGTH SCAN (Last 30 Days)")
    print("-"*70)
    scan = collector.scan_sectoral_strength(lookback_days=30)
    print(scan.to_string(index=False))

    # 2. Rotation Opportunities
    print("\n\n🔄 SECTORAL ROTATION OPPORTUNITIES")
    print("-"*70)
    rotation = collector.find_rotation_opportunities(lookback_days=30)

    print("\n✅ LEADERS (Buy/Hold):")
    for idx in rotation.get('leaders', []):
        config = get_index_config(idx)
        print(f"  - {config.name if config else idx}")

    print("\n⚠️  WEAKENING (Consider Profit Booking):")
    for idx in rotation.get('weakening', []):
        config = get_index_config(idx)
        print(f"  - {config.name if config else idx}")

    print("\n❌ AVOID (Underperforming):")
    for idx in rotation.get('avoid', []):
        config = get_index_config(idx)
        print(f"  - {config.name if config else idx}")

    # 3. Custom Index Example
    print("\n\n🧪 CUSTOM INDEX: Chemicals Sector")
    print("-"*70)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)

    chem_data = collector.get_index_data(
        'NIFTY_CHEMICALS_CUSTOM',
        start_date,
        end_date
    )

    if not chem_data.empty:
        first_close = chem_data.iloc[0]['Close']
        last_close = chem_data.iloc[-1]['Close']
        returns = ((last_close - first_close) / first_close) * 100

        print(f"Starting Value: {first_close:.2f}")
        print(f"Current Value: {last_close:.2f}")
        print(f"Returns: {returns:.2f}%")

    # 4. Relative Strength Example
    print("\n\n📈 RELATIVE STRENGTH: IT vs Nifty50")
    print("-"*70)
    rs_data = collector.calculate_relative_strength(
        'NIFTY_IT',
        'NIFTY50',
        start_date,
        end_date
    )

    if not rs_data.empty:
        latest = rs_data.iloc[-1]
        print(f"Current RS: {latest['RS']:.2f}")
        print(f"Outperforming Nifty50: {latest['Outperforming']}")
        print(f"RS Momentum: {latest['RS_Momentum']}")

    print("\n" + "="*70)
    print("✓ Demo Complete!")
    print("="*70)
