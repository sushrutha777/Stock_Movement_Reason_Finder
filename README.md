# 📈 Stock Movement Reason Finder

This project is a **stock movement reason finder web app** built with **Streamlit**.  
It analyzes **NIFTY100 stocks**, identifies **top gainers and losers**, and provides **AI-powered reasoning** for major price movements using **Google RSS news** and **Gemini Pro API**.  

---

## 🚀 Features
- **Top 5 Gainers & Losers** detection based on stock price changes.
- **Google RSS news fetching** to gather relevant headlines for each stock.
- **AI-powered explanations** using Gemini Pro API for price spikes/drops.
- **Interactive Streamlit UI** to select day ranges and analysis type.
- **Modular backend** with separate scripts for news fetching, reasoning, spike detection, and top movers.
- Optimized with **`@st.cache_resource`** (or Streamlit caching) to reduce redundant API calls.

---

## Installation and Setup

1. Clone this repository:
   ```bash
   git clone https://github.com/sushrutha777/Stock_Movement_Reason_Finder.git
   cd Stock_Movement_Reason_Finder
2. Create Virtual Environment:
   ```bash
    python -m venv venv
   .\venv\Scripts\activate
3. Install the required dependencies:
   ```bash
    pip install -r requirements.txt
4. Create a .env file in the project root and add your Google Gemini API key:
   ```bash
    GOOGLE_API_KEY=your_api_key_here
5. Run the Streamlit app:
   ```bash
    streamlit run app.py
