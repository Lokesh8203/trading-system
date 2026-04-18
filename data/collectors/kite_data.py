"""
Zerodha KiteConnect data collector for real-time and historical data.
Requires active Kite Connect API subscription.
"""

import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Callable
import logging

try:
    from kiteconnect import KiteConnect, KiteTicker
    KITE_AVAILABLE = True
except ImportError:
    KITE_AVAILABLE = False
    logging.warning("kiteconnect not installed. Install with: pip install kiteconnect")

logger = logging.getLogger(__name__)


class KiteDataCollector:
    """
    Real-time and historical data collector using Zerodha KiteConnect API.

    Features:
    - WebSocket tick-by-tick streaming
    - Historical OHLC data
    - Instrument master (all tradable symbols)
    - MCX commodities (Gold, Silver, Crude)
    - NSE equities and derivatives

    Requirements:
    - Active Zerodha trading account
    - Kite Connect API subscription (₹2000/month)
    - API key and access token
    """

    # Common instrument tokens (update these from actual instrument list)
    INSTRUMENTS = {
        # MCX Commodities (example tokens - update with actual)
        'MCX_GOLD': None,      # Gold futures (current month)
        'MCX_SILVER': None,    # Silver futures
        'MCX_CRUDEOIL': None,  # Crude oil futures

        # NSE Indices
        'NIFTY50': 256265,     # Nifty 50 index
        'BANKNIFTY': 260105,   # Bank Nifty index
    }

    def __init__(self, api_key: str, access_token: str = None):
        """
        Initialize KiteConnect client.

        Args:
            api_key: Kite Connect API key
            access_token: Pre-generated access token (optional)
        """
        if not KITE_AVAILABLE:
            raise ImportError(
                "kiteconnect library not installed. "
                "Install with: pip install kiteconnect"
            )

        self.api_key = api_key
        self.access_token = access_token
        self.kite = KiteConnect(api_key=api_key)

        if access_token:
            self.kite.set_access_token(access_token)
            logger.info("KiteConnect initialized with access token")
        else:
            logger.info("KiteConnect initialized. Call login() to authenticate.")

        self.ticker = None
        self.instruments_df = None

    def login(self, request_token: str) -> str:
        """
        Complete login and generate access token.

        Steps:
        1. User visits login URL
        2. After login, Zerodha redirects with request_token
        3. Pass request_token here to get access_token

        Args:
            request_token: Token from redirect URL after login

        Returns:
            access_token: Save this for future sessions
        """
        data = self.kite.generate_session(
            request_token,
            api_secret=input("Enter API Secret: ")
        )
        self.access_token = data["access_token"]
        self.kite.set_access_token(self.access_token)

        logger.info("Login successful. Access token generated.")
        return self.access_token

    def get_login_url(self) -> str:
        """Get the login URL for authentication."""
        return self.kite.login_url()

    def fetch_instruments(self, exchange: str = None) -> pd.DataFrame:
        """
        Fetch list of all tradable instruments.

        Args:
            exchange: Filter by exchange - 'NSE', 'MCX', 'NFO', etc.

        Returns:
            DataFrame with instrument details
        """
        instruments = self.kite.instruments(exchange)
        self.instruments_df = pd.DataFrame(instruments)

        logger.info(f"Fetched {len(self.instruments_df)} instruments")
        return self.instruments_df

    def search_instrument(self, symbol: str, exchange: str = None) -> pd.DataFrame:
        """
        Search for instrument by symbol name.

        Args:
            symbol: Partial or full symbol name
            exchange: Filter by exchange

        Returns:
            DataFrame with matching instruments
        """
        if self.instruments_df is None:
            self.fetch_instruments()

        df = self.instruments_df

        if exchange:
            df = df[df['exchange'] == exchange]

        mask = df['tradingsymbol'].str.contains(symbol, case=False, na=False) | \
               df['name'].str.contains(symbol, case=False, na=False)

        results = df[mask]
        logger.info(f"Found {len(results)} instruments matching '{symbol}'")

        return results

    def get_historical_data(
        self,
        instrument_token: int,
        from_date: datetime,
        to_date: datetime,
        interval: str = 'day'
    ) -> pd.DataFrame:
        """
        Fetch historical OHLC data.

        Args:
            instrument_token: Unique instrument identifier
            from_date: Start date
            to_date: End date
            interval: 'minute', '3minute', '5minute', '15minute',
                     '30minute', '60minute', 'day'

        Returns:
            DataFrame with OHLC data
        """
        records = self.kite.historical_data(
            instrument_token,
            from_date,
            to_date,
            interval
        )

        df = pd.DataFrame(records)

        if not df.empty:
            df.columns = [col.title() for col in df.columns]
            logger.info(f"Fetched {len(df)} historical records")

        return df

    def start_ticker(
        self,
        instrument_tokens: List[int],
        on_tick_callback: Callable,
        on_connect_callback: Callable = None,
        on_close_callback: Callable = None
    ):
        """
        Start WebSocket ticker for real-time data streaming.

        Args:
            instrument_tokens: List of instrument tokens to subscribe
            on_tick_callback: Function to handle incoming ticks
                             Signature: def on_ticks(ws, ticks)
            on_connect_callback: Function called on connection
                                Signature: def on_connect(ws, response)
            on_close_callback: Function called on disconnection
                              Signature: def on_close(ws, code, reason)
        """
        self.ticker = KiteTicker(self.api_key, self.access_token)

        def _on_connect(ws, response):
            logger.info("WebSocket connected")
            ws.subscribe(instrument_tokens)
            ws.set_mode(ws.MODE_FULL, instrument_tokens)

            if on_connect_callback:
                on_connect_callback(ws, response)

        def _on_close(ws, code, reason):
            logger.info(f"WebSocket closed: {code} - {reason}")
            if on_close_callback:
                on_close_callback(ws, code, reason)

        self.ticker.on_connect = _on_connect
        self.ticker.on_ticks = on_tick_callback
        self.ticker.on_close = _on_close

        logger.info(f"Starting ticker for {len(instrument_tokens)} instruments")
        self.ticker.connect(threaded=True)

    def stop_ticker(self):
        """Stop the WebSocket ticker."""
        if self.ticker:
            self.ticker.close()
            logger.info("Ticker stopped")

    def get_quote(self, instruments: List[str]) -> Dict:
        """
        Get real-time quote for instruments.

        Args:
            instruments: List of instrument identifiers (exchange:symbol format)
                        e.g., ['NSE:RELIANCE', 'MCX:GOLDM23SEPFUT']

        Returns:
            Dictionary with quote data
        """
        quotes = self.kite.quote(instruments)
        return quotes


# Example usage
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)

    print("KiteConnect Data Collector Example")
    print("=" * 50)
    print("\nTo use this module:")
    print("1. Get API key from https://kite.trade/")
    print("2. Generate access token using login flow")
    print("3. Store credentials in .env file")
    print("\nExample:")
    print("  from data.collectors import KiteDataCollector")
    print("  collector = KiteDataCollector(api_key='your_key', access_token='your_token')")
    print("  df = collector.get_historical_data(...)")
    print("\nFor WebSocket streaming:")
    print("  def on_ticks(ws, ticks):")
    print("      for tick in ticks:")
    print("          print(f\"Price: {tick['last_price']}\")")
    print("  collector.start_ticker(instrument_tokens=[...], on_tick_callback=on_ticks)")
