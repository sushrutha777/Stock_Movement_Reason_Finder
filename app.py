from numpy import unique_all
import streamlit as st
import os
from dotenv import load_dotenv
import plotly.graph_objects as go
import pandas as pd
from backend.spike_detector import SpikeDetector
from backend.news_fetcher import NewsFetcher
from backend.reasoning import ReasoningGenerator
from utils.nifty100 import NIFTY100

# Load env
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

st.set_page_config(page_title="Stock Movement Reason Finder", layout="wide")

st.title("📈 Stock Movement Reasoning ")
st.write("Analyze NIFTY100 stocks and explain major spikes using Google News + Gemini AI reasoning.")

# User Controls 
days_range = st.slider("Select Day Range for Analysis", 1, 30, 7)
analysis_type = st.radio("Select Analysis Type:", ["🚀 Top 5 Gainers", "📉 Top 5 Losers"])

if "top5_df" not in st.session_state:
    st.session_state.top5_df = None

# Create class instances once
spike = SpikeDetector(period="7d", interval="1d")  
reasoner = ReasoningGenerator(api_key=GEMINI_API_KEY)

if st.button("🔍 Analyze"):
    results = []

    with st.spinner("Fetching stock data for NIFTY100..."):
        for ticker in NIFTY100:
            # OOP CALL
            spike.period = f"{days_range}d"  
            df = spike.get_recent_data(ticker)

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

        # Gainers or Losers based on selection 
        if analysis_type == "🚀 Top 5 Gainers":
            top5 = df_changes.head(5).copy()
        else:  # 📉 Top 5 Losers
            top5 = df_changes.tail(5).iloc[::-1].copy()

        st.session_state.top5_df = top5

# If top5 computed, always show table & selection
if st.session_state.top5_df is not None:
    st.subheader(analysis_type)
    top5_df = st.session_state.top5_df.copy()

    # display table
    display = top5_df[["Ticker", "Change%"]].reset_index(drop=True)
    display.index = display.index + 1
    display.index.name = ""
    display["Change%"] = display["Change%"].apply(lambda x: f"{x:+.2f}%")
    st.dataframe(display, use_container_width=True)

    st.markdown("---")
    st.subheader("Choose stocks from the Top 5 to analyze")
    tickers_list = top5_df["Ticker"].tolist()

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

                # Chart
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=df.index, y=df["Close"],
                                         mode="lines+markers", name="Close Price"))
                fig.update_layout(
                    title=f"{ticker} Closing Prices",
                    xaxis_title="Date",
                    yaxis_title="Price",
                    template="plotly_white",
                    height=380,
                )
                st.plotly_chart(fig, use_container_width=True)

                # News
                news = NewsFetcher(query=ticker, max_headlines=5)
                headlines = news.fetch()

                if headlines:
                    st.subheader("📰 Latest News Headlines")
                    for h in headlines:
                        st.markdown(f"- [{h['title']}]({h['link']})", unsafe_allow_html=True)
                else:
                    st.info("No recent headlines found for this ticker.")

                # Reasoning
                movement = "gained" if change > 0 else "dropped"
                stock_info = f"{ticker} {movement} {abs(change):.2f}% in last {days_range} days."

                reasoning_text = reasoner.generate_reasoning(stock_info, headlines)
                st.subheader("Summary")
                st.markdown(reasoning_text, unsafe_allow_html=True)