import csv
from pathlib import Path
from datetime import datetime
import pandas as pd

PORTFOLIO_FILE = Path("data/portfolio.csv")

def log_investment(price, shares, ticker, date_override=None):
    PORTFOLIO_FILE.parent.mkdir(exist_ok=True)
    with open(PORTFOLIO_FILE, "a", newline="") as f:
        writer = csv.writer(f)
        row_date = date_override if date_override else str(datetime.now().date())
        writer.writerow([row_date, price, shares, ticker])

def get_portfolio_df():
    if not PORTFOLIO_FILE.exists():
        return pd.DataFrame(columns=["Date", "Price", "Shares", "Ticker"])
    df = pd.read_csv(PORTFOLIO_FILE, header=None, names=["Date", "Price", "Shares", "Ticker"])
    return df

def already_invested_today():
    df = get_portfolio_df()
    today = str(datetime.now().date())
    return not df[df["Date"] == today].empty