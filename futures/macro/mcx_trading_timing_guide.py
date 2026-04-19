"""
MCX TRADING TIMING & EXECUTION GUIDE

Critical timing rules for MCX:
1. MCX sessions: 9:00 AM - 11:30 PM / 11:55 PM (depending on instrument)
2. AVOID first 15 minutes (9:00-9:15 AM) - opening volatility
3. AVOID last 15 minutes (11:15-11:30 PM) - closing volatility
4. BEST times: 10:00 AM - 11:00 AM, 2:00 PM - 4:00 PM, 7:00 PM - 10:00 PM

Global vs MCX correlation:
- COMEX Gold (GC=F) → MCX GOLD correlation: 0.95+
- But prices differ due to:
  - USD/INR conversion
  - Import duty (12.5% for gold, 10% for silver)
  - Storage costs
  - Local demand/supply
  - Time zone lag

When to run scanner:
- Morning: 9:30 AM (after opening settle)
- Afternoon: 2:00 PM (London open overlap)
- Evening: 7:00 PM (US market open)

When to enter trades:
- WAIT 15 minutes after any major market open
- AVOID last 15 minutes before close
- Use limit orders during volatile periods
- Use market orders only during stable periods

Author: Trading System
Date: 2026-04-19
"""

from datetime import datetime, time

class MCXTradingSchedule:
    """MCX trading schedule and optimal entry times"""

    def __init__(self):
        # MCX sessions (IST)
        self.sessions = {
            'GOLD': {
                'open': time(9, 0),
                'close': time(23, 30),
                'avoid_first': time(9, 15),  # Avoid 9:00-9:15
                'avoid_last': time(23, 15)   # Avoid 23:15-23:30
            },
            'SILVER': {
                'open': time(9, 0),
                'close': time(23, 30),
                'avoid_first': time(9, 15),
                'avoid_last': time(23, 15)
            },
            'CRUDE': {
                'open': time(9, 0),
                'close': time(23, 30),
                'avoid_first': time(9, 15),
                'avoid_last': time(23, 15)
            },
            'COPPER': {
                'open': time(9, 0),
                'close': time(23, 30),
                'avoid_first': time(9, 15),
                'avoid_last': time(23, 15)
            },
            'NATGAS': {
                'open': time(9, 0),
                'close': time(23, 30),
                'avoid_first': time(9, 15),
                'avoid_last': time(23, 15)
            }
        }

        # Optimal entry windows (IST)
        self.optimal_windows = [
            {
                'name': 'Morning Session',
                'start': time(9, 30),
                'end': time(11, 30),
                'description': 'After opening settle, Indian participation high',
                'priority': 'MEDIUM'
            },
            {
                'name': 'Afternoon Session',
                'start': time(14, 0),
                'end': time(16, 0),
                'description': 'London open overlap, good liquidity',
                'priority': 'HIGH'
            },
            {
                'name': 'Evening Session',
                'start': time(19, 0),
                'end': time(22, 0),
                'description': 'US market open, highest global liquidity',
                'priority': 'HIGHEST'
            }
        ]

        # Scanner run times
        self.scanner_schedule = [
            {
                'time': time(9, 30),
                'session': 'Morning',
                'action': 'Run scanner after opening settle'
            },
            {
                'time': time(14, 0),
                'session': 'Afternoon',
                'action': 'Run scanner for London open'
            },
            {
                'time': time(19, 0),
                'session': 'Evening',
                'action': 'Run scanner for US open'
            }
        ]

    def can_trade_now(self, instrument: str) -> dict:
        """Check if current time is good for trading"""
        now = datetime.now().time()

        if instrument not in self.sessions:
            return {'can_trade': False, 'reason': 'Unknown instrument'}

        sess = self.sessions[instrument]

        # Check if market open
        if now < sess['open'] or now > sess['close']:
            return {
                'can_trade': False,
                'reason': 'Market closed',
                'next_open': sess['open']
            }

        # Check if in avoid zone
        if sess['open'] <= now <= sess['avoid_first']:
            return {
                'can_trade': False,
                'reason': 'Opening volatility (avoid first 15 min)',
                'wait_until': sess['avoid_first']
            }

        if sess['avoid_last'] <= now <= sess['close']:
            return {
                'can_trade': False,
                'reason': 'Closing volatility (avoid last 15 min)',
                'next_session': 'Tomorrow'
            }

        # Find current optimal window
        current_window = None
        for window in self.optimal_windows:
            if window['start'] <= now <= window['end']:
                current_window = window
                break

        if current_window:
            return {
                'can_trade': True,
                'window': current_window['name'],
                'priority': current_window['priority'],
                'description': current_window['description']
            }
        else:
            return {
                'can_trade': True,
                'window': 'Off-peak',
                'priority': 'LOW',
                'description': 'Outside optimal windows, lower liquidity'
            }

    def next_scanner_run(self) -> dict:
        """When should you run the scanner next?"""
        now = datetime.now().time()

        for schedule in self.scanner_schedule:
            if now < schedule['time']:
                return {
                    'time': schedule['time'],
                    'session': schedule['session'],
                    'action': schedule['action']
                }

        # If past all times, next is tomorrow morning
        return {
            'time': self.scanner_schedule[0]['time'],
            'session': 'Tomorrow Morning',
            'action': 'Run scanner after opening settle'
        }


def print_trading_schedule():
    """Print complete trading schedule"""
    schedule = MCXTradingSchedule()

    print("\n" + "="*100)
    print("MCX TRADING SCHEDULE & TIMING GUIDE")
    print("="*100)

    print("\n📅 MCX Market Hours (IST):")
    print("   All instruments: 9:00 AM - 11:30 PM")
    print("   Extended (select): Until 11:55 PM")

    print("\n❌ AVOID THESE TIMES:")
    print("   • 9:00 AM - 9:15 AM (Opening volatility)")
    print("   • 11:15 PM - 11:30 PM (Closing volatility)")
    print("   • During major news (RBI, US Fed, inventory data)")

    print("\n✅ OPTIMAL ENTRY WINDOWS:")
    for window in schedule.optimal_windows:
        print(f"\n   {window['name']} [{window['priority']}]")
        print(f"   Time: {window['start'].strftime('%I:%M %p')} - {window['end'].strftime('%I:%M %p')}")
        print(f"   Why: {window['description']}")

    print("\n⏰ SCANNER RUN SCHEDULE:")
    for sched in schedule.scanner_schedule:
        print(f"\n   {sched['time'].strftime('%I:%M %p')} - {sched['session']}")
        print(f"   → {sched['action']}")

    print("\n🎯 EXECUTION PROTOCOL:")
    print("   1. Run scanner at scheduled time")
    print("   2. Review signals, select best opportunity")
    print("   3. Check if in optimal window (priority HIGH or HIGHEST)")
    print("   4. If not, set price alert and wait for optimal window")
    print("   5. Use LIMIT orders (not market) during first hour")
    print("   6. Use MARKET orders only during stable mid-session")

    print("\n💡 CURRENT STATUS:")
    now = datetime.now()
    print(f"   Current Time: {now.strftime('%I:%M %p IST')}")

    for instrument in ['GOLD', 'SILVER', 'CRUDE']:
        status = schedule.can_trade_now(instrument)
        print(f"\n   {instrument}:")
        if status['can_trade']:
            print(f"      ✅ CAN TRADE")
            print(f"      Window: {status['window']}")
            print(f"      Priority: {status['priority']}")
            print(f"      {status['description']}")
        else:
            print(f"      ❌ WAIT")
            print(f"      Reason: {status['reason']}")
            if 'wait_until' in status:
                print(f"      Resume at: {status['wait_until'].strftime('%I:%M %p')}")

    next_scan = schedule.next_scanner_run()
    print(f"\n📊 NEXT SCANNER RUN:")
    print(f"   Time: {next_scan['time'].strftime('%I:%M %p')}")
    print(f"   Session: {next_scan['session']}")
    print(f"   Action: {next_scan['action']}")

    print("\n" + "="*100)


if __name__ == "__main__":
    print_trading_schedule()
