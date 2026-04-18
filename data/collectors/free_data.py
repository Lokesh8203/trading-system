"""
Free data collector using yfinance and nselib.
For development and backtesting without Zerodha API subscription.
"""

import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class FreeDataCollector:
    """
    Collects historical market data from free sources.

    Data Sources:
    - yfinance: Global commodities (Gold, Silver, Crude), Nifty
    - nselib: NSE stocks (when implemented)

    Limitations:
    - Not real-time (15-20 min delay)
    - Limited to 1-minute granularity minimum
    - No tick-by-tick data
    - Rate limits apply
    """

    # Symbol mappings for Indian-tradable instruments
    SYMBOL_MAP = {
        # Commodities (Yahoo Finance symbols)
        'GOLD': 'GC=F',          # Gold Futures
        'SILVER': 'SI=F',        # Silver Futures
        'CRUDE_WTI': 'CL=F',     # WTI Crude Oil
        'CRUDE_BRENT': 'BZ=F',   # Brent Crude Oil

        # Indices
        'NIFTY50': '^NSEI',      # Nifty 50
        'BANKNIFTY': '^NSEBANK', # Bank Nifty
        'SENSEX': '^BSESN',      # BSE Sensex

        # Currency (useful for commodity pricing)
        'USDINR': 'USDINR=X',    # USD/INR
    }

    def __init__(self, cache_dir: str = 'data/cache'):
        """
        Initialize the free data collector.

        Args:
            cache_dir: Directory to cache downloaded data
        """
        self.cache_dir = cache_dir
        logger.info("FreeDataCollector initialized")

    def get_historical_data(
        self,
        symbol: str,
        start_date: datetime,
        end_date: datetime,
        interval: str = '1d'
    ) -> pd.DataFrame:
        """
        Fetch historical OHLCV data for a symbol.

        Args:
            symbol: Symbol key (e.g., 'GOLD', 'NIFTY50') or direct Yahoo symbol
            start_date: Start date for data
            end_date: End date for data
            interval: Data interval - '1m', '5m', '15m', '1h', '1d', '1wk', '1mo'

        Returns:
            DataFrame with columns: Open, High, Low, Close, Volume, Date
        """
        try:
            # Map symbol if it's a predefined key
            yahoo_symbol = self.SYMBOL_MAP.get(symbol, symbol)

            logger.info(f"Fetching {yahoo_symbol} data from {start_date} to {end_date}")

            # Download data
            ticker = yf.Ticker(yahoo_symbol)
            df = ticker.history(
                start=start_date,
                end=end_date,
                interval=interval
            )

            if df.empty:
                logger.warning(f"No data returned for {yahoo_symbol}")
                return pd.DataFrame()

            # Clean and standardize
            df = df.reset_index()
            df.columns = [col.title() for col in df.columns]

            logger.info(f"Fetched {len(df)} rows for {yahoo_symbol}")
            return df

        except Exception as e:
            logger.error(f"Error fetching data for {symbol}: {e}")
            return pd.DataFrame()

    def get_multiple_symbols(
        self,
        symbols: List[str],
        start_date: datetime,
        end_date: datetime,
        interval: str = '1d'
    ) -> Dict[str, pd.DataFrame]:
        """
        Fetch data for multiple symbols.

        Args:
            symbols: List of symbol keys or Yahoo symbols
            start_date: Start date
            end_date: End date
            interval: Data interval

        Returns:
            Dictionary mapping symbol to DataFrame
        """
        results = {}

        for symbol in symbols:
            df = self.get_historical_data(symbol, start_date, end_date, interval)
            if not df.empty:
                results[symbol] = df

        return results

    def get_latest_price(self, symbol: str) -> Optional[float]:
        """
        Get the latest available price for a symbol.

        Args:
            symbol: Symbol key or Yahoo symbol

        Returns:
            Latest close price or None if unavailable
        """
        try:
            yahoo_symbol = self.SYMBOL_MAP.get(symbol, symbol)
            ticker = yf.Ticker(yahoo_symbol)

            # Get last 2 days to ensure we have data
            df = ticker.history(period='2d')

            if df.empty:
                return None

            return float(df['Close'].iloc[-1])

        except Exception as e:
            logger.error(f"Error fetching latest price for {symbol}: {e}")
            return None

    def get_nse_stocks(self, symbols: List[str], **kwargs) -> Dict[str, pd.DataFrame]:
        """
        Placeholder for NSE stock data collection.

        This will use nselib when implemented or direct NSE symbols via yfinance.

        Args:
            symbols: List of NSE stock symbols (e.g., ['RELIANCE.NS', 'TCS.NS'])
            **kwargs: Additional arguments for data fetching

        Returns:
            Dictionary mapping symbol to DataFrame
        """
        # Add .NS suffix if not present
        nse_symbols = [
            f"{sym}.NS" if not sym.endswith('.NS') else sym
            for sym in symbols
        ]

        return self.get_multiple_symbols(nse_symbols, **kwargs)


# Example usage
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)

    collector = FreeDataCollector()

    # Test: Get last 30 days of gold and crude data
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)

    print("Fetching commodity data...")
    data = collector.get_multiple_symbols(
        symbols=['GOLD', 'SILVER', 'CRUDE_WTI', 'NIFTY50'],
        start_date=start_date,
        end_date=end_date,
        interval='1d'
    )

    for symbol, df in data.items():
        print(f"\n{symbol}: {len(df)} rows")
        print(df.tail(3))

    # Test: Get latest prices
    print("\n\nLatest Prices:")
    for symbol in ['GOLD', 'SILVER', 'CRUDE_WTI', 'NIFTY50']:
        price = collector.get_latest_price(symbol)
        print(f"{symbol}: {price}")
