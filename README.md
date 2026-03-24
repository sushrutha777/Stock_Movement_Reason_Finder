# 📈 Stock Movement Reason Finder

A modern, **AI-augmented financial analysis tool** designed to explain NIFTY100 stock price movements using real-time news and Gemini 2.5 AI.

## 🏗️ Architecture: Client-Server Model
The project has been refactored into a decoupled, production-ready architecture:

1. **Backend (FastAPI):** Hosted on **Render**, handles heavy computation, Yahoo Finance data fetching, news aggregation, and Gemini AI reasoning.
2. **Frontend (Streamlit):** Hosted on **Streamlit Cloud**, providing a lightweight, interactive UI that communicates with the backend via RESTful API calls.

## 🚀 Live Links
- **🔥 Frontend App:** [stock-movement-reason-finder.streamlit.app](https://stock-movement-reason-finder.streamlit.app/)
- **⚙️ Backend API:** [stock-movement-reason-finder.onrender.com](https://stock-movement-reason-finder.onrender.com/docs)

## ✨ key Features
- **Top Movers Detection:** Automatically identifies the top 5 gainers and losers in the NIFTY100.
- **AI-Powered Reasoning:** Uses **Gemini 2.5 Flash** to analyze Google RSS news and provide concise, bulleted summaries for price spikes/drops.
- **Interactive Visualization:** Renders interactive stock charts using **Plotly**, with data served directly from the backend API.
- **Decoupled Security:** API keys are stored securely as Environment Variables on Render, preventing leaks and keeping the frontend lightweight.

## 📦 Project Structure
- `/app`: FastAPI application (Main entry: `app/main.py`)
- `/backend`: Core business logic (Spike detection, News, Reasoning)
- `/utils`: Helper modules (NIFTY100 ticker list)
- `app.py`: Streamlit frontend application

## 🛠️ Local Setup

1. **Clone & Install:**
   ```bash
   git clone https://github.com/sushrutha777/Stock_Movement_Reason_Finder.git
   cd Stock_Movement_Reason_Finder
   pip install -r requirements.txt
   ```

2. **Run Backend (Optional):**
   ```bash
   uvicorn app.main:app --reload
   ```

3. **Run Frontend:**
   ```bash
   streamlit run app.py
   ```

---
