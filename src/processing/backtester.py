import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import logging
from src.scraping.scrape_data import fetch_binance_historical_data
from src.data.models.agent import BullishAgent, BearishAgent

# Configure logging if not already configured elsewhere.
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class Backtester:
    def __init__(self, trading_strategy, start_date, end_date, initial_balance=10000, trading_fee=0.001):
        self.strategy = trading_strategy
        self.start_date = start_date
        self.end_date = end_date
        self.initial_balance = initial_balance
        self.trading_fee = trading_fee
        self.df = None
        self.trades = []

    def load_data(self, symbol="BTCUSDT", interval="1d"):
        try:
            self.df = fetch_binance_historical_data(symbol=symbol, interval=interval, lookback="365 days ago UTC")
            self.df.set_index("date", inplace=True)
            logger.info("Binance market data loaded successfully.")
        except Exception as e:
            logger.error(f"Error loading market data: {e}")
            raise

    def apply_sentiment_analysis(self, articles):
        # Instantiate analysis agents for the provided articles.
        bullish_agent = BullishAgent(articles)
        bearish_agent = BearishAgent(articles)

        # Run analysis. For empty article list, these agents should return empty DataFrames.
        bull_df = bullish_agent.analyze()
        bear_df = bearish_agent.analyze()

        # Debug prints for verification.
        logger.info("Bullish analysis result:")
        logger.info(bull_df.head())
        logger.info("Bearish analysis result:")
        logger.info(bear_df.head())

        # If bull_df is empty or does not contain expected columns, assign default signals.
        if bull_df.empty or "date_parsed" not in bull_df.columns or "bullish_signal" not in bull_df.columns:
            logger.info("No bullish analysis data available; assigning default False to bullish_signal.")
            self.df["bullish_signal"] = False
        else:
            self.df["bullish_signal"] = self.df.index.map(
                lambda d: bull_df.loc[bull_df["date_parsed"] == d, "bullish_signal"].any()
                if d in bull_df["date_parsed"].values else False
            )

        # Similarly, if bear_df is empty or missing expected columns, assign default signals.
        if bear_df.empty or "date_parsed" not in bear_df.columns or "bearish_signal" not in bear_df.columns:
            logger.info("No bearish analysis data available; assigning default False to bearish_signal.")
            self.df["bearish_signal"] = False
        else:
            self.df["bearish_signal"] = self.df.index.map(
                lambda d: bear_df.loc[bear_df["date_parsed"] == d, "bearish_signal"].any()
                if d in bear_df["date_parsed"].values else False
            )

    def execute_strategy(self):
        balance = self.initial_balance
        position = 0  # BTC holdings

        for i in range(1, len(self.df)):
            current_price = self.df.iloc[i]["close"]
            date = self.df.index[i]

            try:
                if self.df.iloc[i]["bullish_signal"] and balance > 0:
                    amount = (balance * (1 - self.trading_fee)) / current_price
                    position += amount
                    balance = 0
                    self.trades.append({
                        "date": date, "action": "BUY", "price": current_price, "amount": amount
                    })
                    logger.info(f"Executed BUY on {date} for {amount:.4f} BTC")
                elif self.df.iloc[i]["bearish_signal"] and position > 0:
                    balance += position * current_price * (1 - self.trading_fee)
                    self.trades.append({
                        "date": date, "action": "SELL", "price": current_price, "amount": position
                    })
                    logger.info(f"Executed SELL on {date} for {position:.4f} BTC")
                    position = 0
            except Exception as e:
                logger.error(f"Error during strategy execution on {date}: {e}")

        final_value = balance + (position * self.df.iloc[-1]["close"])
        logger.info(f"Final portfolio value: ${final_value:.2f}")
        return final_value

    def plot_results(self):
        buy_signals = [trade for trade in self.trades if trade["action"] == "BUY"]
        sell_signals = [trade for trade in self.trades if trade["action"] == "SELL"]

        plt.figure(figsize=(12, 6))
        plt.plot(self.df.index, self.df["close"], label="BTC Price", linewidth=1, alpha=0.7)

        if buy_signals:
            plt.scatter(
                [trade["date"] for trade in buy_signals],
                [trade["price"] for trade in buy_signals],
                marker="^", color="g", label="Buy", alpha=0.8
            )
        if sell_signals:
            plt.scatter(
                [trade["date"] for trade in sell_signals],
                [trade["price"] for trade in sell_signals],
                marker="v", color="r", label="Sell", alpha=0.8
            )

        plt.title("Backtesting Results")
        plt.xlabel("Date")
        plt.ylabel("Price (USDT)")
        plt.legend()
        plt.grid()
        plt.show()
