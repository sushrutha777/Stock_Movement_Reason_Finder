import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import requests

# This is your live Render API!
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
    with st.spinner("Fetching top movers from API..."):
        try:
            response = requests.get(f"{API_BASE_URL}/top-movers", params={"period": f"{days_range}d", "top_n": 5})
            response.raise_for_status()
            data = response.json()
            
            if analysis_type == "🚀 Top 5 Gainers":
                movers = data.get("top_gainers", [])
            else:
                movers = data.get("top_losers", [])
                
            if not movers:
                st.error("No stock data found.")
                st.session_state.top5_df = None
            else:
                df_changes = pd.DataFrame(movers)
                df_changes.rename(columns={"ticker": "Ticker", "change_percent": "Change%"}, inplace=True)
                st.session_state.top5_df = df_changes
        except Exception as e:
            st.error(f"Failed to fetch data from API: {e}")
            st.session_state.top5_df = None

# If top5 computed, always show table & selection
if st.session_state.top5_df is not None:
    st.subheader(analysis_type)
    top5_df = st.session_state.top5_df.copy()

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
            st.info("Select at least one stock.")
        else:
            for ticker in selected_tickers:
                row = top5_df[top5_df["Ticker"] == ticker].iloc[0]
                change = row["Change%"]
                sign = "+" if change > 0 else ""
                st.write(f"### {ticker} ({sign}{change:.2f}%)")

                # 2. Call the remote API for News, Reasoning AND Chart Data!
                with st.spinner(f"Fetching reasoning and chart for {ticker}..."):
                    try:
                        reason_resp = requests.get(f"{API_BASE_URL}/reason/{ticker}", params={"period": f"{days_range}d"})
                        reason_resp.raise_for_status()
                        reason_data = reason_resp.json()
                        
                        # Use the "history" data from the backend to draw the chart!
                        # No more local yfinance calls means no more rate limits on Streamlit Cloud
                        history = reason_data.get("history", [])
                        if history:
                            chart_df = pd.DataFrame(history)
                            chart_df["date"] = pd.to_datetime(chart_df["date"])
                            
                            fig = go.Figure()
                            fig.add_trace(go.Scatter(x=chart_df["date"], y=chart_df["close"],
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
                            st.warning("No chart data returned from backend.")

                        # News
                        headlines = reason_data.get("headlines", [])
                        if headlines:
                            st.subheader("📰 Latest News Headlines")
                            for h in headlines:
                                st.markdown(f"- [{h['title']}]({h['link']})", unsafe_allow_html=True)
                        
                        # Summary
                        st.subheader("Summary")
                        st.markdown(reason_data.get("reason", "No reasoning generated."), unsafe_allow_html=True)

                    except Exception as e:
                        st.error(f"Failed to fetch data from API: {e}")