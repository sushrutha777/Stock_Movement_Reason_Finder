"""
API routes for the Stock Movement Reason Finder.

All business logic is delegated to the existing backend/ and utils/ modules.
"""

import os
from typing import Optional

from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException, Query

from backend.spike_detector import SpikeDetector
from backend.news_fetcher import NewsFetcher
from backend.reasoning import ReasoningGenerator
from utils.nifty100 import NIFTY100
from app.schemas.stock_schema import (
    ReasonResponse,
    SpikeResponse,
    TopMoversResponse,
    StockMover,
    Headline,
)

load_dotenv()

router = APIRouter()

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

# Pre-build a set of valid base names (without ".NS") for user-friendly lookup
_VALID_TICKERS = {t.replace(".NS", "").upper(): t for t in NIFTY100}


def _resolve_ticker(stock: str) -> str:
    """
    Resolve a user-supplied stock name to a full Yahoo Finance ticker.

    Raises HTTPException 404 if the stock is not in the NIFTY100 list.
    """
    key = stock.strip().upper()

    # Accept with or without the ".NS" suffix
    if key in _VALID_TICKERS:
        return _VALID_TICKERS[key]
    if key in {t.upper() for t in NIFTY100}:
        return key

    raise HTTPException(
        status_code=404,
        detail=f"Stock '{stock}' not found in NIFTY100 list. "
        f"Use the /top-movers endpoint to see valid tickers.",
    )


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@router.get(
    "/spike/{stock}",
    response_model=SpikeResponse,
    summary="Detect price spike for a stock",
)
def get_spike(
    stock: str,
    period: str = Query("7d", description="Lookback period, e.g. 7d, 14d, 30d"),
    threshold: float = Query(3.0, description="Spike threshold in percent"),
):
    """
    Check whether a NIFTY100 stock has experienced a significant price spike.

    Returns spike status and the latest percentage change.
    """
    try:
        ticker = _resolve_ticker(stock)

        detector = SpikeDetector(period=period, interval="1d")
        df = detector.get_recent_data(ticker)

        if df is None or df.empty:
            raise HTTPException(
                status_code=404,
                detail=f"No market data available for '{stock}'. The market may be closed.",
            )

        is_spike, pct_change = detector.detect_spike(df, threshold)

        return SpikeResponse(
            stock=ticker,
            is_spike=is_spike,
            change_percent=round(pct_change, 2) if pct_change is not None else None,
            threshold=threshold,
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/reason/{stock}",
    response_model=ReasonResponse,
    summary="Get AI reasoning for stock movement",
)
def get_reason(
    stock: str,
    period: str = Query("7d", description="Lookback period, e.g. 7d, 14d, 30d"),
    max_headlines: int = Query(5, description="Maximum number of news headlines"),
):
    """
    Fetch recent market data and news for a NIFTY100 stock, then generate
    an AI-powered explanation of the price movement using Gemini.
    """
    try:
        ticker = _resolve_ticker(stock)

        # 1. Get price data
        detector = SpikeDetector(period=period, interval="1d")
        df = detector.get_recent_data(ticker)

        if df is None or df.empty:
            raise HTTPException(
                status_code=404,
                detail=f"No market data available for '{stock}'. The market may be closed.",
            )

        # Calculate overall % change
        change = None
        try:
            change = round(
                ((df["Close"].iloc[-1] - df["Open"].iloc[0]) / df["Open"].iloc[0]) * 100, 2
            )
        except Exception:
            pass

        # 2. Fetch news
        fetcher = NewsFetcher(query=ticker, max_headlines=max_headlines)
        headlines = fetcher.fetch()

        # 3. Generate reasoning
        movement = "gained" if (change and change > 0) else "dropped"
        abs_change = abs(change) if change is not None else 0
        stock_info = f"{ticker} {movement} {abs_change:.2f}% in the recent period."

        api_key = os.getenv("GEMINI_API_KEY")
        reasoner = ReasoningGenerator(api_key=api_key)
        reasoning_text = reasoner.generate_reasoning(stock_info, headlines)

        return ReasonResponse(
            stock=ticker,
            change_percent=change,
            reason=reasoning_text,
            headlines=[Headline(**h) for h in headlines],
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/top-movers",
    response_model=TopMoversResponse,
    summary="Get top gaining and losing NIFTY100 stocks",
)
def get_top_movers(
    period: str = Query("7d", description="Lookback period, e.g. 7d, 14d, 30d"),
    top_n: int = Query(5, description="Number of top gainers/losers to return"),
):
    """
    Scan all NIFTY100 stocks, compute percentage change over the given period,
    and return the top gainers and top losers.
    """
    try:
        detector = SpikeDetector(period=period, interval="1d")
        results: list[tuple[str, float]] = []

        for ticker in NIFTY100:
            df = detector.get_recent_data(ticker)
            if df is not None and not df.empty:
                if "Close" in df.columns and "Open" in df.columns:
                    try:
                        change = round(
                            ((df["Close"].iloc[-1] - df["Open"].iloc[0])
                             / df["Open"].iloc[0])
                            * 100,
                            2,
                        )
                        results.append((ticker, change))
                    except Exception:
                        continue

        if not results:
            raise HTTPException(
                status_code=503,
                detail="Unable to fetch stock data. Markets may be closed or data unavailable.",
            )

        # Sort descending by change
        results.sort(key=lambda x: x[1], reverse=True)

        gainers = [StockMover(ticker=t, change_percent=c) for t, c in results[:top_n]]
        losers = [StockMover(ticker=t, change_percent=c) for t, c in results[-top_n:][::-1]]

        # Extract numeric days from period string (e.g. "7d" -> 7)
        try:
            period_days = int(period.replace("d", ""))
        except ValueError:
            period_days = 7

        return TopMoversResponse(
            period_days=period_days,
            top_gainers=gainers,
            top_losers=losers,
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
