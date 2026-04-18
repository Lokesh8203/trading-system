"""
Data collection modules for Indian markets.

Supports multiple data sources:
- Free: yfinance, nselib (for development/backtesting)
- Paid: Zerodha KiteConnect (for live trading)
- Indices: NSE sectoral and custom indices
"""

from .free_data import FreeDataCollector
from .kite_data import KiteDataCollector
from .index_collector import IndexCollector

__all__ = ['FreeDataCollector', 'KiteDataCollector', 'IndexCollector']
