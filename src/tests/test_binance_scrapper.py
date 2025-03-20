import pytest
from scraping.scrape_data import fetch_binance_historical_data
import pandas as pd

def test_binance_historical_data():
    """Test that Binance historical data is retrieved and formatted correctly."""
    
    df = fetch_binance_historical_data(symbol="BTCUSDT", interval="1d", lookback="3 days ago UTC")

    # Ensure data is returned
    assert isinstance(df, pd.DataFrame)
    assert not df.empty

    expected_columns = [
        "open_time", "open", "high", "low", "close", "volume",
        "close_time", "quote_asset_volume", "number_of_trades",
        "taker_buy_volume", "taker_buy_quote_volume", "date"
    ]

    assert list(df.columns) == expected_columns

    # Ensure numeric fields are parsed correctly
    assert df["open"].dtype == "float64"
    assert df["high"].dtype == "float64"
    assert df["low"].dtype == "float64"
    assert df["close"].dtype == "float64"
    assert df["volume"].dtype == "float64"

    print("✅ Binance historical data test passed!")

