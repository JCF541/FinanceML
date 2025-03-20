import pandas as pd

class TradingStrategy:
    """Defines the buy/sell decision-making process using sentiment analysis."""

    def __init__(self, bullish_ma_window=10):
        self.bullish_ma_window = bullish_ma_window

    def should_buy(self, df, current_date):
        """Buy when sentiment is bullish and price is above moving average."""
        if current_date not in df.index:
            return False
        row = df.loc[current_date]

        if df.index.get_loc(current_date) < self.bullish_ma_window:
            return False  # not enough data for moving average yet

        moving_average = df["close"].rolling(self.bullish_ma_window).mean().loc[current_date]
        return row["bullish_signal"] and row["close"] > moving_average

    def should_sell(self, df, current_date):
        """Sell when sentiment is bearish."""
        row = df.loc[current_date]
        return row["bearish_signal"]
