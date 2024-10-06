# price_utils.py
import logging

import pandas as pd
from alpaca_trade_api import REST, TimeFrame

logger = logging.getLogger("tradebot")


def fetch_historical_prices(api, symbols):
    logger.info(f"Fetching historical prices for {', '.join(symbols)}")

    try:
        bars = api.get_bars(
            symbols, TimeFrame.Day, limit=30
        ).df  # Ensure this returns a DataFrame

        price_data = {}
        for symbol in symbols:
            df = bars[bars["symbol"] == symbol]  # Ensure 'symbol' column exists
            if df.empty:
                logger.warning(f"No data for {symbol}")
            else:
                price_data[symbol] = df["close"].values

        price_df = pd.DataFrame(price_data)
        logger.info(f"Retrieved historical prices: {price_df.head()}")
        return price_df

    except Exception as e:
        logger.error(f"Error fetching historical prices: {e}")
        raise
