import streamlit as st
import os
from dotenv import load_dotenv
import plotly.graph_objects as go
import pandas as pd

from backend.spike_detector import get_recent_data
from backend.news_fetcher import fetch_news_rss
from backend.reasoning import generate_reasoning
from utils.nifty100 import NIFTY100

# Load env
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

st.set_page_config(page_title="Stock Movement Reason Finder", layout="wide")

st.title("📈 Stock jai Movement Reasoning ")
st.write("Analyze NIFTY100 stocks and explain major spikes using Google News + Gemini AI reasoning.")

# --- User Controls ---
days_range = st.slider("Select Day Range for Analysis", 1, 30, 7)
analysis_type = st.radio("Select Analysis Type:", ["🚀 Top 5 Gainers", "📉 Top 5 Losers"])

# persist top5 results so user can pick after computing
if "top5_df" not in st.session_state:
    st.session_state.top5_df = None

if st.button("🔍 Analyze"):
    results = []

    with st.spinner("Fetching stock data for NIFTY100..."):
        for ticker in NIFTY100:
            df = get_recent_data(ticker, period=f"{days_range}d")
            if df is not None and not df.empty:
                if "Close" in df.columns and "Open" in df.columns:
                    try:
                        change = round(((df["Close"].iloc[-1] - df["Open"].iloc[0]) / df["Open"].iloc[0]) * 100, 2)
                        results.append((ticker, change, df))
                    except Exception:
                        continue

    if not results:
        st.error("No stock data found")
        st.session_state.top5_df = None
    else:
        df_changes = pd.DataFrame(results, columns=["Ticker", "Change%", "Data"])
        df_changes.sort_values(by="Change%", ascending=False, inplace=True)

        # --- Gainers or Losers based on selection ---
        if analysis_type == "🚀 Top 5 Gainers":
            top5 = df_changes.head(5).copy()
        else:  # 📉 Top 5 Losers
            top5 = df_changes.tail(5).iloc[::-1].copy()

        # store for later inspection
        st.session_state.top5_df = top5

# If top5 computed, always show the table (so it doesn't disappear) and let user select which to analyze
if st.session_state.top5_df is not None:
    st.subheader(analysis_type)
    top5_df = st.session_state.top5_df.copy()

    # prepare display table with Rank 1-5 and formatted Change%
    display = top5_df[["Ticker", "Change%"]].reset_index(drop=True)
    display.insert(0, "Rank", range(1, len(display) + 1))
    display["Change%"] = display["Change%"].apply(lambda x: f"{x:+.2f}%")

    st.dataframe(display, use_container_width=True)

    st.markdown("---")
    st.subheader("🎯 Select stock(s) from Top-5 to inspect")
    tickers_list = top5_df["Ticker"].tolist()

    # choose single or multiple - using multiselect to allow multiple
    selected_tickers = st.multiselect("Pick stock(s) for detailed analysis", options=tickers_list)

    if st.button("🔎 Analyze Selected"):
        if not selected_tickers:
            st.info("Select at least one stock from the Top-5 to analyze.")
        else:
            for ticker in selected_tickers:
                row = top5_df[top5_df["Ticker"] == ticker].iloc[0]
                change = row["Change%"]
                df = row["Data"]
                sign = "+" if change > 0 else ""
                st.write(f"### {ticker} ({sign}{change:.2f}%)")

                # Stock Chart
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=df.index, y=df["Close"], mode="lines+markers", name="Close Price"))
                fig.update_layout(
                    title=f"{ticker} Closing Prices",
                    xaxis_title="Date",
                    yaxis_title="Price",
                    template="plotly_white",
                    height=380,
                )
                st.plotly_chart(fig, use_container_width=True)

                # News
                headlines = fetch_news_rss(ticker, max_headlines=5)
                if headlines:
                    st.subheader("📰 Latest News Headlines")
                    for h in headlines:
                        st.markdown(f"- [{h['title']}]({h['link']})", unsafe_allow_html=True)
                else:
                    st.info("No recent headlines found for this ticker.")

                # AI Reasoning
                movement = "gained" if change > 0 else "dropped"
                stock_info = f"{ticker} {movement} {abs(change):.2f}% in last {days_range} days."
                reasoning_text = generate_reasoning(stock_info, headlines, api_key=GEMINI_API_KEY)
                st.subheader("Summary")
                st.markdown(reasoning_text, unsafe_allow_html=True)
else:
    st.info("Click '🔍 Analyze' to compute Top-5 gainers/losers, then pick which stock(s) to inspect.")
