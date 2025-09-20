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

st.title("📈 Stock Movement Reasoning ")
st.write("Analyze NIFTY100 stocks and explain major spikes using Google News + Gemini AI reasoning.")

# --- User Controls ---
days_range = st.slider("Select Day Range for Analysis", 1, 30, 7)
analysis_type = st.radio("Select Analysis Type:", ["🚀 Top 5 Gainers", "📉 Top 5 Losers"])

if st.button("🔍 Analyze"):
    results = []

    with st.spinner("Fetching stock data for NIFTY100..."):
        for ticker in NIFTY100:
            df = get_recent_data(ticker, period=f"{days_range}d")
            if df is not None and not df.empty:
                if "Close" in df.columns:
                    change = round(((df["Close"].iloc[-1] - df["Open"].iloc[0]) / df["Open"].iloc[0]) * 100, 2)
                    results.append((ticker, change, df))

    if not results:
        st.error("No stock data found")
    else:
        df_changes = pd.DataFrame(results, columns=["Ticker", "Change%", "Data"])
        df_changes.sort_values(by="Change%", ascending=False, inplace=True)

        # --- Gainers or Losers based on selection ---
        if analysis_type == "🚀 Top 5 Gainers":
            selected = df_changes.head(5)
        else:  # 📉 Top 5 Losers
            selected = df_changes.tail(5).iloc[::-1]

        st.subheader(analysis_type)
        st.dataframe(selected[["Ticker", "Change%"]].round(2))

        for _, row in selected.iterrows():
            ticker, change, df = row["Ticker"], row["Change%"], row["Data"]
            sign = "+" if change > 0 else ""
            st.write(f"### {ticker} ({sign}{change:.2f}%)")

            # Stock Chart
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=df.index, y=df["Close"], mode="lines+markers", name="Close Price"))
            fig.update_layout(title=f"{ticker} Closing Prices", xaxis_title="Date", yaxis_title="Price", template="plotly_white")
            st.plotly_chart(fig, use_container_width=True)

            # News
            headlines = fetch_news_rss(ticker, max_headlines=5)
            if headlines:
                st.subheader("📰 Latest News Headlines")
                for h in headlines:
                    st.markdown(f"- [{h['title']}]({h['link']})", unsafe_allow_html=True)

            # AI Reasoning
            movement = "gained" if change > 0 else "dropped"
            stock_info = f"{ticker} {movement} {abs(change):.2f}% in last {days_range} days."
            reasoning_text = generate_reasoning(stock_info, headlines, api_key=GEMINI_API_KEY)
            st.subheader("🤖 AI Summary")
            st.markdown(reasoning_text, unsafe_allow_html=True)
