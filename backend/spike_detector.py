import yfinance as yf
import pandas as pd
from typing import Optional, Tuple


class SpikeDetector:
    """
    Detect significant price spikes for any stock using Yahoo Finance data.
    """

    def __init__(self, period: str = "7d", interval: str = "1d"):
        """
        Initialize the data-fetcher settings.

        Args:
            period (str): How many days of data to fetch. Default "7d".
            interval (str): Interval between candles. Default "1d".
        """
        self.period = period
        self.interval = interval

    def get_recent_data(self, ticker: str) -> Optional[pd.DataFrame]:
        """
        Fetch recent stock data and calculate percent change.

        Args:
            ticker (str): Stock symbol.

        Returns:
            DataFrame or None
        """
        try:
            t = yf.Ticker(ticker)
            df = t.history(period=self.period, interval=self.interval)

            if df.empty:
                return None

            df["PctChange"] = df["Close"].pct_change() * 100
            return df

        except Exception:
            return None

    def detect_spike(self, df: pd.DataFrame, threshold: float) -> Tuple[bool, Optional[float]]:
        """
        Detect whether the most recent percentage change exceeds a given threshold.

        Args:
            df (pd.DataFrame): Data returned from get_recent_data().
            threshold (float): Spike threshold % (e.g., 3.0 => ±3%).

        Returns:
            (is_spike: bool, pct_change: float or None)
        """
        if df is None or df.empty or "PctChange" not in df.columns:
            return False, None

        last_change = df["PctChange"].iloc[-1]
        is_spike = abs(last_change) >= threshold

        return is_spike, last_change
