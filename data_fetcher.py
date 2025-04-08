import yfinance as yf

def fetch_price_and_trend(ticker):
    ticker_data = yf.Ticker(ticker)
    live_price = ticker_data.info.get("regularMarketPrice", None)
    hist = ticker_data.history(period="7d")
    if hist.empty or len(hist) < 2:
        return None, None, None
    hist = hist[hist['Close'].notnull()]
    moving_avg = hist['Close'].mean()

    return float(live_price), float(moving_avg), hist