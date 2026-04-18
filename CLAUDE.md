# Trading System - Claude Code Instructions

## Project Overview
A systematic trading signal generation system focused on producing high-quality buy/sell signals through quantitative analysis and backtesting.

**Current Phase:** Signal generation (not automated execution)

## Development Principles

### Code Quality
- Write vectorized pandas/numpy operations (avoid loops)
- Include docstrings for all signal generation functions
- Add type hints for function parameters and returns
- Handle missing data and edge cases gracefully
- Log all important decisions and errors

### Signal Development
- Every signal must be backtestable
- Calculate key metrics: Sharpe ratio, max drawdown, win rate
- Validate signals on out-of-sample data
- Document the logic and assumptions behind each signal
- Include parameter sensitivity analysis

### Data Handling
- Cache downloaded market data to avoid redundant API calls
- Always check for data quality issues (gaps, outliers)
- Use timezone-aware datetime handling
- Resample data carefully (forward-fill for prices, not for signals)

### Security
- Never commit API keys or secrets to git
- Store sensitive config in .env files or config/secrets.json
- Use environment variables for credentials

### Testing
- Write unit tests for signal logic
- Test edge cases: missing data, single data point, all NaN
- Validate that signals don't leak future information

## Project Structure
```
trading-system/
├── data/              # Market data (gitignored except samples)
├── signals/           # Signal generation modules
├── backtesting/       # Backtesting framework
├── analysis/          # Performance analysis tools
├── config/            # Config files (secrets gitignored)
├── notebooks/         # Exploration and analysis
└── tests/             # Unit tests
```

## Workflow Preferences
- Commit after completing each logical feature
- Use descriptive commit messages
- Push to personal GitHub (Lokesh8203/trading-system)
- Run tests before committing signal logic changes

## Tech Stack
- Python 3.9+
- pandas, numpy for data processing
- pandas-ta, ta-lib for technical indicators
- yfinance for data fetching
- matplotlib/plotly for visualization
- pytest for testing

## Git Configuration
- Local git user: Lokesh Surana <lokesh8203@gmail.com>
- Remote: Personal GitHub account (not Salesforce)
- Credentials: Use stored PAT for authentication
