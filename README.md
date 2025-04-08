# Smart Investment Tracker

A personal finance tool that helps you make smarter, rule-based investments into ETFs or stocks — built with Python and Streamlit.

This tracker:
- Recommends how much to invest based on short-term price deviation.
- Simulates and logs daily investments using a fixed monthly budget.
- Displays a live dashboard of your current portfolio value.
- Supports tracking **multiple stocks**.
- Lets you log past stock purchases manually (no fractional shares).
- Supports multiple investing strategies
- Supports multiple investing frequencies

---

## Features

### Automated Recommendations
- Calculates recommended daily investment based on deviation from 7-day moving average.
- Ensures purchases follow minimum trade limits and only full shares are bought.

### Real-Time Dashboard
- Live price, moving average, and daily deviation metrics.
- Chart of recent price history with daily recommendation.
- Portfolio history and **daily value tracking**.

### Portfolio Tracker
- Tracks total shares, cost basis, current value per stock.
- Graphs total portfolio value and individual tickers over time.

### Manual Entry Support
- Add past transactions (price, date, ticker, # of shares).
- All transactions are integrated with performance charts and totals.

---

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/Jonny7171/StockTracker.git
cd StockTracker
```
### 2. Install Dependencies

```bash
pip install streamlit yfinance pandas altair
```

### 2. Run the App
```bash
streamlit run app.py
```

## Notes
- Portfolio data is saved locally to data/portfolio.csv.
- Prices are pulled via the yfinance API.
- Supports only full share purchases, no fractional trades.
- Time series tracking is based on purchase history and historical close prices.
