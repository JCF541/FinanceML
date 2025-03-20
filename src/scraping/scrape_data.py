from binance.client import Client
import pandas as pd
import yaml
import os
import time

def get_config():
    current_dir = os.path.dirname(__file__)
    config_path = os.path.abspath(os.path.join(current_dir, '../config/config.yml'))

    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    return config
# Securely load Binance API credentials from config
config = get_config()
api_key = config["binance"]["api_key"]
api_secret = config["binance"]["api_secret"]

# Binance client initialization
client = Client(api_key, api_secret)

def fetch_binance_historical_data(symbol="BTCUSDT", interval=Client.KLINE_INTERVAL_1DAY, lookback="365 days ago UTC"):
    """
    Fetches historical BTC trading data from Binance.

    Args:
        symbol (str): Trading symbol pair.
        interval (str): Candlestick interval.
        lookback (str): Period to look back from current time.

    Returns:
        pd.DataFrame: DataFrame with open, high, low, close, volume, and timestamps.
    """
    klines = client.get_historical_klines(symbol, interval, lookback)

    # Convert to pandas DataFrame
    data = pd.DataFrame(klines, columns=[
        "open_time", "open", "high", "low", "close", "volume",
        "close_time", "quote_asset_volume", "number_of_trades",
        "taker_buy_volume", "taker_buy_quote_volume", "ignore"
    ])

    # Convert timestamps to readable dates
    data["date"] = pd.to_datetime(data["open_time"], unit="ms")
    data["open_time"] = pd.to_datetime(data["open_time"], unit="ms")
    data["close_time"] = pd.to_datetime(data["close_time"], unit="ms")

    # Convert numeric columns
    numeric_cols = [
        "open", "high", "low", "close", "volume",
        "quote_asset_volume", "taker_buy_volume", "taker_buy_quote_volume"
    ]
    data[numeric_cols] = data[numeric_cols].apply(pd.to_numeric, axis=1)

    # Drop unnecessary column
    data.drop(columns=["ignore"], inplace=True)

    return data

if __name__ == "__main__":
    print("Fetching historical BTC data from Binance...")
    df_btc = fetch_binance_historical_data(symbol="BTCUSDT")

    # Save to CSV with timestamp
    filename = f"binance_btc_historical_{int(time.time())}.csv"
    df_btc.to_csv(filename, index=False)
    print(f"Historical BTC data successfully saved to {filename}")
