"""
Data collection modules for Indian markets.

Supports multiple data sources:
- Free: yfinance, nselib (for development/backtesting)
- Paid: Zerodha KiteConnect (for live trading)
"""

from .free_data import FreeDataCollector
from .kite_data import KiteDataCollector

__all__ = ['FreeDataCollector', 'KiteDataCollector']
