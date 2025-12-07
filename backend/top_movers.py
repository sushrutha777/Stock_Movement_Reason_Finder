import yfinance as yf
import pandas as pd
from typing import List, Dict, Any


class TopMovers:
    """
    Compute top N gainers and losers among a set of tickers
    based on first Open vs last Close.
    """

    def __init__(self, tickers: List[str], days: int = 30, top_n: int = 5, debug: bool = False):
        """
        Args:
            tickers (List[str]): List of ticker symbols.
            days (int): Lookback period in days. Default 30.
            top_n (int): Number of top gainers/losers to return. Default 5.
            debug (bool): If True, prints debug info.
        """
        self.tickers = tickers
        self.days = days
        self.top_n = top_n
        self.debug = debug

    def _fetch_data(self) -> pd.DataFrame:
        """Fetch OHLC data for all tickers."""
        period = f"{self.days}d"
        data = yf.download(self.tickers, period=period, interval="1d")

        # Remove timezone & sort
        data.index = data.index.tz_localize(None)
        data = data.sort_index()

        # Keep only date (optional)
        data.index = pd.to_datetime(data.index.date)

        return data

    def _log_debug(self, open_first: pd.Series, close_last: pd.Series) -> None:
        """Print debug information if enabled."""
        if not self.debug:
            return

        print("\n=== Debug: First Open vs Last Close ===")
        for t in self.tickers:
            try:
                print(f"{t}: Open={open_first[t]:.2f}, Close={close_last[t]:.2f}")
            except KeyError:
                print(f"{t}: Missing data")

    def get_top_movers(self) -> Dict[str, Any]:
        """
        Calculate top gainers and losers.

        Returns:
            dict: { "gainers": {ticker: pct}, "losers": {ticker: pct} }
                  or { "error": "message" }
        """
        try:
            data = self._fetch_data()

            if data.empty or "Open" not in data.columns or "Close" not in data.columns:
                return {"error": "No data found."}

            open_first = data["Open"].iloc[0]
            close_last = data["Close"].iloc[-1]

            self._log_debug(open_first, close_last)

            movement = ((close_last - open_first) / open_first) * 100
            movement = movement.sort_values(ascending=False)

            gainers = movement.head(self.top_n).to_dict()
            losers = movement.tail(self.top_n).to_dict()

            return {"gainers": gainers, "losers": losers}

        except Exception as e:
            return {"error": str(e)}
