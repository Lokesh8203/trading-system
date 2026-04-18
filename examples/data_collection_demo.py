"""
Demo script showing how to collect data using both free and paid sources.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime, timedelta
from data.collectors import FreeDataCollector
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def demo_free_data_collection():
    """
    Demonstrate free data collection for development/backtesting.
    Works without any API keys or subscriptions.
    """
    print("\n" + "=" * 70)
    print("FREE DATA COLLECTION DEMO")
    print("=" * 70)

    collector = FreeDataCollector()

    # Define instruments to track
    instruments = ['GOLD', 'SILVER', 'CRUDE_WTI', 'NIFTY50']

    # Get last 30 days of data
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)

    print(f"\nFetching {len(instruments)} instruments from {start_date.date()} to {end_date.date()}")
    print("-" * 70)

    # Fetch data
    data = collector.get_multiple_symbols(
        symbols=instruments,
        start_date=start_date,
        end_date=end_date,
        interval='1d'
    )

    # Display results
    for symbol, df in data.items():
        if df.empty:
            print(f"\n❌ {symbol}: No data available")
            continue

        latest = df.iloc[-1]
        print(f"\n✓ {symbol}:")
        print(f"  Rows fetched: {len(df)}")
        print(f"  Latest close: ${latest['Close']:.2f}")
        print(f"  Date: {latest['Date']}")
        print(f"  Volume: {latest['Volume']:,.0f}")

    print("\n" + "-" * 70)

    # Get latest prices
    print("\nLATEST PRICES (Live):")
    print("-" * 70)

    for symbol in instruments:
        price = collector.get_latest_price(symbol)
        if price:
            print(f"  {symbol:15s}: ${price:,.2f}")
        else:
            print(f"  {symbol:15s}: ❌ Unavailable")

    # Demo: NSE stocks
    print("\n" + "-" * 70)
    print("NSE STOCKS DEMO:")
    print("-" * 70)

    nse_stocks = ['RELIANCE', 'TCS', 'INFY', 'HDFCBANK']
    print(f"\nFetching {len(nse_stocks)} NSE stocks (last 7 days)...")

    nse_data = collector.get_nse_stocks(
        symbols=nse_stocks,
        start_date=datetime.now() - timedelta(days=7),
        end_date=datetime.now(),
        interval='1d'
    )

    for symbol, df in nse_data.items():
        if not df.empty:
            latest_price = df.iloc[-1]['Close']
            print(f"  {symbol:15s}: ₹{latest_price:,.2f}")


def demo_kite_data_collection():
    """
    Demonstrate Zerodha KiteConnect data collection.
    Requires API subscription and credentials.
    """
    print("\n" + "=" * 70)
    print("KITE DATA COLLECTION DEMO")
    print("=" * 70)
    print("\n⚠️  This requires:")
    print("  1. Active Zerodha trading account")
    print("  2. Kite Connect API subscription (₹2000/month)")
    print("  3. API credentials (key, secret, access token)")
    print("\nSetup instructions:")
    print("  1. Visit https://kite.trade/")
    print("  2. Create an app and get API credentials")
    print("  3. Store in .env file:")
    print("     KITE_API_KEY=your_key")
    print("     KITE_API_SECRET=your_secret")
    print("     KITE_ACCESS_TOKEN=your_token")
    print("\nExample code:")
    print("-" * 70)

    example_code = """
from data.collectors import KiteDataCollector
from datetime import datetime, timedelta
import os

# Initialize
collector = KiteDataCollector(
    api_key=os.getenv('KITE_API_KEY'),
    access_token=os.getenv('KITE_ACCESS_TOKEN')
)

# Search for instruments
gold_instruments = collector.search_instrument('GOLD', exchange='MCX')
print(gold_instruments[['tradingsymbol', 'instrument_token', 'exchange']])

# Get historical data
instrument_token = gold_instruments.iloc[0]['instrument_token']
df = collector.get_historical_data(
    instrument_token=instrument_token,
    from_date=datetime.now() - timedelta(days=30),
    to_date=datetime.now(),
    interval='day'
)

# Real-time streaming
def on_ticks(ws, ticks):
    for tick in ticks:
        print(f"Symbol: {tick['instrument_token']}, "
              f"Price: {tick['last_price']}, "
              f"Volume: {tick['volume']}")

collector.start_ticker(
    instrument_tokens=[instrument_token],
    on_tick_callback=on_ticks
)
"""

    print(example_code)
    print("-" * 70)


def main():
    """Run all demos."""

    print("\n")
    print("╔" + "═" * 68 + "╗")
    print("║" + " " * 15 + "TRADING SYSTEM - DATA COLLECTION DEMO" + " " * 15 + "║")
    print("╚" + "═" * 68 + "╝")

    # Demo 1: Free data (always works)
    try:
        demo_free_data_collection()
    except Exception as e:
        logger.error(f"Free data demo failed: {e}")

    # Demo 2: Kite data (info only)
    demo_kite_data_collection()

    print("\n" + "=" * 70)
    print("RECOMMENDATIONS:")
    print("=" * 70)
    print("""
1. START WITH FREE DATA:
   - Develop and test your strategy using free sources
   - Use yfinance for commodities and indices
   - No cost, immediate access

2. VALIDATE YOUR STRATEGY:
   - Backtest on historical data
   - Calculate performance metrics
   - Ensure strategy is profitable before going live

3. UPGRADE TO KITE API:
   - Once strategy is proven, subscribe to Kite Connect
   - Get real-time tick data
   - Set up alerts using Zerodha GTT orders
   - Trade manually based on alerts (Phase 1)

4. DATA COLLECTION BEST PRACTICES:
   - Cache historical data locally (avoid redundant API calls)
   - Use on-demand fetching (don't pull continuously)
   - Set up alerts at key levels (support/resistance)
   - Let broker handle notifications
    """)

    print("=" * 70)
    print("\n✓ Demo complete! Check the code in examples/ and data/collectors/")
    print()


if __name__ == '__main__':
    main()
