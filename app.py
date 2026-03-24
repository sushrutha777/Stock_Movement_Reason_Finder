import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import requests
import yfinance as yf

# This is your live Render API! Streamlit will now act purely as the Frontend
API_BASE_URL = "https://stock-movement-reason-finder.onrender.com"

st.set_page_config(page_title="Stock Movement Reason Finder", layout="wide")

st.title("📈 Stock Movement Reasoning ")
st.write("Analyze NIFTY100 stocks and explain major spikes using Google News + Gemini AI reasoning.")

# User Controls 
days_range = st.slider("Select Day Range for Analysis", 1, 30, 7)
analysis_type = st.radio("Select Analysis Type:", ["🚀 Top 5 Gainers", "📉 Top 5 Losers"])

if "top5_df" not in st.session_state:
    st.session_state.top5_df = None

if st.button("🔍 Analyze"):
    with st.spinner("Fetching top movers from API... this might take a moment."):
        # 1. Call the remote API instead of running all the math locally!
        try:
            response = requests.get(f"{API_BASE_URL}/top-movers", params={"period": f"{days_range}d", "top_n": 5})
            response.raise_for_status()
            data = response.json()
            
            # Extract gainers or losers based on user selection
            if analysis_type == "🚀 Top 5 Gainers":
                movers = data.get("top_gainers", [])
            else:
                movers = data.get("top_losers", [])
                
            if not movers:
                st.error("No stock data found.")
                st.session_state.top5_df = None
            else:
                df_changes = pd.DataFrame(movers)
                # DataFrame has columns: ['ticker', 'change_percent']
                df_changes.rename(columns={"ticker": "Ticker", "change_percent": "Change%"}, inplace=True)
                st.session_state.top5_df = df_changes
        except Exception as e:
            st.error(f"Failed to fetch data from API. Ensure your Render server is live! Error: {e}")
            st.session_state.top5_df = None

# If top5 computed, always show table & selection
if st.session_state.top5_df is not None:
    st.subheader(analysis_type)
    top5_df = st.session_state.top5_df.copy()

    # display table
    display = top5_df.copy()
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
                sign = "+" if change > 0 else ""
                st.write(f"### {ticker} ({sign}{change:.2f}%)")

                # Fetch data just for drawing the Chart (Streamlit UI feature)
                with st.spinner(f"Loading chart for {ticker}..."):
                    t = yf.Ticker(ticker)
                    df = t.history(period=f"{days_range}d", interval="1d")
                    
                    if not df.empty:
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
                    else:
                        st.warning("Could not load chart data.")

                # 2. Call the remote API for News & AI Reasoning! 
                with st.spinner(f"Requesting AI reasoning from Render API for {ticker}..."):
                    try:
                        reason_resp = requests.get(f"{API_BASE_URL}/reason/{ticker}", params={"period": f"{days_range}d"})
                        reason_resp.raise_for_status()
                        reason_data = reason_resp.json()
                        
                        headlines = reason_data.get("headlines", [])
                        if headlines:
                            st.subheader("📰 Latest News Headlines")
                            for h in headlines:
                                st.markdown(f"- [{h['title']}]({h['link']})", unsafe_allow_html=True)
                        else:
                            st.info("No recent headlines found for this ticker.")
                        
                        st.subheader("Summary")
                        st.markdown(reason_data.get("reason", "No reasoning generated."), unsafe_allow_html=True)

                    except Exception as e:
                        st.error(f"Failed to fetch AI reasoning from API: {e}")