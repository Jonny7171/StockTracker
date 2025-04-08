import streamlit as st
from config import load_user_settings, save_user_settings
from data_fetcher import fetch_price_and_trend
from strategy import calculate_investment_percentage
from portfolio import log_investment, get_portfolio_df, already_invested_today
from datetime import datetime
import pandas as pd
import altair as alt
import yfinance as yf

st.set_page_config(layout="wide")
st.title("Smart Investment Tracker")

settings = load_user_settings()
if "settings_loaded" not in st.session_state:
    for key, val in settings.items():
        st.session_state[key] = val
    st.session_state.settings_loaded = True

st.sidebar.header("User Settings")
ticker_input = st.sidebar.text_input("Enter ETF Ticker (e.g. VSP.TO)", key="ticker")
monthly_budget_input = st.sidebar.number_input("Monthly Budget (CAD)", min_value=0, key="monthly_budget", step=100)
min_trade_input = st.sidebar.number_input("Minimum Trade Amount (CAD)", min_value=0, key="min_trade_amount", step=10)
frequency_input = st.sidebar.selectbox("Recommendation Frequency", ["daily", "weekly", "monthly"], key="recommendation_frequency")

if st.sidebar.button("Save Settings"):
    updated_settings = {
        "ticker": st.session_state["ticker"],
        "monthly_budget": st.session_state["monthly_budget"],
        "min_trade_amount": st.session_state["min_trade_amount"],
        "recommendation_frequency": st.session_state["recommendation_frequency"]
    }
    save_user_settings(updated_settings)
    st.session_state.update(updated_settings)
    st.sidebar.success("Settings saved!")

st.sidebar.header("Add Existing Position")
existing_ticker = st.sidebar.text_input("Ticker (e.g. VSP.TO)", key="existing_ticker")
existing_date = st.sidebar.date_input("Purchase Date", datetime.now().date())
existing_price = st.sidebar.number_input("Purchase Price (CAD)", min_value=0.0, step=1.0, format="%.2f", key="existing_price")
existing_shares = st.sidebar.number_input("Number of Stocks Purchased", min_value=1, step=1, key="existing_shares")

if st.sidebar.button("Add Existing Position"):
    if not existing_ticker.strip():
        st.sidebar.error("Please enter a valid ticker for the existing position.")
    elif existing_price <= 0 or existing_shares <= 0:
        st.sidebar.error("Price and number of stocks must be greater than zero.")
    else:
        log_investment(existing_price, existing_shares, existing_ticker, date_override=str(existing_date))
        st.sidebar.success(f"Added {existing_shares} share(s) of {existing_ticker} on {existing_date} at ${existing_price:.2f} each.")

if not st.session_state["ticker"].strip():
    st.error("No ETF ticker selected. Please enter a valid ticker (e.g. VSP.TO).")
    st.stop()
if st.session_state["monthly_budget"] <= 0:
    st.error("Monthly budget must be greater than zero.")
    st.stop()

try:
    latest, moving_avg, history = fetch_price_and_trend(st.session_state["ticker"])
except Exception as e:
    st.error(f"Error fetching data for ticker {st.session_state['ticker']}: {e}")
    st.stop()
if latest is None:
    st.error("Failed to fetch ETF data. The ticker may be invalid.")
    st.stop()

deviation = (latest - moving_avg) / moving_avg
percent = calculate_investment_percentage(latest, moving_avg)
daily_budget = st.session_state["monthly_budget"] / 30
raw_recommended_amount = daily_budget * percent
recommended_shares = int(raw_recommended_amount // latest) if latest > 0 else 0
recommended_investment = recommended_shares * latest if recommended_shares >= 1 else 0

col1, col2 = st.columns([1, 2])
with col1:
    st.metric("Live Price", f"${latest:.2f}")
    st.metric("7-day Moving Avg", f"${moving_avg:.2f}")
    st.metric("Deviation", f"{deviation * 100:.2f}%")
    st.metric("Recommended Shares", f"{recommended_shares}")
    st.metric("Recommended Investment", f"${recommended_investment:.2f}")
    if recommended_investment >= st.session_state["min_trade_amount"] and recommended_shares >= 1:
        if already_invested_today():
            st.info("You've already invested today.")
        elif st.button("Simulate Investment"):
            log_investment(latest, recommended_shares, st.session_state["ticker"])
            st.success(f"Simulated purchase: {recommended_shares} share(s) of {st.session_state['ticker']} at ${latest:.2f} each, total ${recommended_investment:.2f}")
    else:
        st.info("Below minimum trade amount or insufficient funds to purchase a full share. Skipping today.")
with col2:
    st.subheader(f"{st.session_state['ticker']} Price Over Last 7 Days")
    chart_df = history[['Close']].copy()
    chart_df['7-Day Average'] = moving_avg
    chart_df = chart_df.reset_index()
    chart = (alt.Chart(chart_df)
             .transform_fold(['Close', '7-Day Average'], as_=['Metric', 'Value'])
             .mark_line(point=True)
             .encode(x=alt.X('Date:T', axis=alt.Axis(format='%b %d', title='Date')),
                     y=alt.Y('Value:Q', scale=alt.Scale(domain=[chart_df['Close'].min()*0.98, chart_df['Close'].max()*1.02]), title='Price (CAD)'),
                     color='Metric:N')
             .properties(width=600, height=300))
    st.altair_chart(chart, use_container_width=True)

st.subheader("Purchase History")
df = get_portfolio_df()
if not df.empty:
    df["# Stocks"] = df["Shares"]  # 'Shares' column now holds the number purchased
    st.dataframe(df[["Date", "Price", "# Stocks", "Ticker"]])
else:
    st.info("No investments logged yet.")

st.subheader("Active Portfolio")
df = get_portfolio_df()
if "Ticker" not in df.columns:
    st.error("Ticker column not found in portfolio data. Please ensure transactions are logged with a ticker.")
    st.stop()
if not df.empty:
    grouped = df.groupby("Ticker", as_index=False).agg({
        "Shares": "sum",
        "Price": "mean"  # Average purchase price (weighted average would be better; this is a simple version)
    })
    grouped["Total Cost"] = grouped["Shares"] * grouped["Price"]
    current_prices = {}
    for ticker in grouped["Ticker"].unique():
        try:
            t_latest, _, _ = fetch_price_and_trend(ticker)
            current_prices[ticker] = t_latest if t_latest else 0.0
        except Exception as e:
            current_prices[ticker] = 0.0
    grouped["Current Price"] = grouped["Ticker"].apply(lambda t: current_prices[t])
    grouped["Current Value"] = grouped["Shares"] * grouped["Current Price"]
    grouped.rename(columns={"Shares": "Total Stocks"}, inplace=True)
    st.dataframe(grouped[["Ticker", "Total Stocks", "Price", "Total Cost", "Current Price", "Current Value"]])
else:
    st.write("No active portfolio to show (no transactions).")

st.subheader("Portfolio Value Over Time")
df = get_portfolio_df()
if not df.empty:
    df["Date"] = pd.to_datetime(df["Date"]).dt.normalize()
    tickers = df["Ticker"].unique()
    start_date = df["Date"].min()
    end_date = pd.Timestamp.today().normalize()
    all_dates = pd.date_range(start=start_date, end=end_date, freq='D')
    timeline = pd.DataFrame({"Date": all_dates})
    for ticker in tickers:
        sub = df[df["Ticker"] == ticker].copy()
        sub["Date"] = pd.to_datetime(sub["Date"]).dt.normalize()
        sub = sub.sort_values("Date")
        sub["Cumulative Stocks"] = sub["Shares"].cumsum()
        sub = sub.set_index("Date")["Cumulative Stocks"]
        sub = sub.reindex(all_dates).fillna(method="ffill").fillna(0)
        sub = sub.reset_index()
        sub.columns = ["Date", f"{ticker}_Stocks"]
        timeline = timeline.merge(sub, on="Date", how="left")
    timeline.fillna(0, inplace=True)
    value_df = timeline.copy()
    for ticker in tickers:
        try:
            t_hist = yf.Ticker(ticker).history(start=start_date.strftime("%Y-%m-%d"),
                                               end=end_date.strftime("%Y-%m-%d"),
                                               interval="1d")
            if not t_hist.empty:
                t_hist = t_hist.copy()
                t_hist.index = t_hist.index.tz_localize(None)
                t_hist["Close"] = t_hist["Close"].ffill()
                t_hist = t_hist.reset_index()
                t_hist["Date"] = pd.to_datetime(t_hist["Date"]).dt.normalize()
                t_hist.rename(columns={"Close": f"{ticker}_Close"}, inplace=True)
                value_df["Date"] = pd.to_datetime(value_df["Date"]).dt.normalize()
                value_df = value_df.merge(t_hist[["Date", f"{ticker}_Close"]], on="Date", how="left")
        except Exception as e:
            st.error(f"Error fetching history for {ticker}: {e}")
    for ticker in tickers:
        close_col = f"{ticker}_Close"
        stock_col = f"{ticker}_Stocks"
        value_col = f"{ticker}_Value"
        if close_col in value_df.columns and stock_col in value_df.columns:
            value_df[close_col] = value_df[close_col].ffill().fillna(0)
            value_df[value_col] = value_df[stock_col] * value_df[close_col]
        else:
            value_df[value_col] = 0
    value_cols = [f"{ticker}_Value" for ticker in tickers]
    value_df["Total"] = value_df[value_cols].sum(axis=1)
    melt_cols = value_cols + ["Total"]
    plot_df = value_df.melt(id_vars="Date", value_vars=melt_cols, var_name="Ticker", value_name="Value")
    chart = (alt.Chart(plot_df)
             .mark_line(point=True)
             .encode(x=alt.X("Date:T", title="Date"),
                     y=alt.Y("Value:Q", title="Portfolio Value (CAD)"),
                     color=alt.Color("Ticker:N", title="Ticker"))
             .properties(width=800, height=400))
    st.altair_chart(chart, use_container_width=True)
else:
    st.write("No portfolio data available for time series.")