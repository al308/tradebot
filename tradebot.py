import os
from dotenv import load_dotenv
import pandas as pd
import logging
from datetime import datetime
from pandas import Timedelta
from lumibot.brokers.alpaca import Alpaca
from lumibot.strategies.strategy import Strategy
from lumibot.backtesting import YahooDataBacktesting
from alpaca_trade_api import REST, TimeFrame

# Import utility functions
from asset_utils import position_sizing, get_sentiment
from portfolio_utils import optimize_portfolio

# Load environment variables from .env file
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)

# Credentials
ALPACA_CREDS = {
    "API_KEY": os.getenv('ALPACA_API_KEY'),
    "API_SECRET": os.getenv('ALPACA_API_SECRET'),
    "PAPER": os.getenv('ALPACA_PAPER') != 'False',
    "BASE_URL": os.getenv('ALPACA_BASE_URL')
}

# Define the strategy
class PortfolioTrader(Strategy):
    def initialize(self, symbols: list = None, cash_at_risk: float = 0.5):
        # Default to 25 diverse symbols if none are provided
        if symbols is None:
            self.symbols = [
                "AAPL", "MSFT", "GOOG", "AMZN", "TSLA",   # Tech
                "JPM", "BAC", "HSBC", "GS", "V",          # Finance
                "PFE", "JNJ", "MRK", "GSK", "AZN",        # Healthcare
                "XOM", "CVX", "BP", "SHEL", "TTE",        # Energy
                "PG", "KO", "UL",                         # Consumer Goods
                "BA", "GE"                                # Industrials
            ]
        else:
            self.symbols = symbols  # Custom list if provided

        self.sleeptime = "24H"
        self.cash_at_risk = cash_at_risk
        self.last_trades = {symbol: None for symbol in self.symbols}
        self.api = REST(
            ALPACA_CREDS["API_KEY"],
            ALPACA_CREDS["API_SECRET"],
            base_url=ALPACA_CREDS["BASE_URL"]
        )
        self.price_cache = {}

    def position_sizing(self, symbol):
        return position_sizing(self, symbol, self.cash_at_risk)

    def get_sentiment(self, symbol):
        return get_sentiment(self, symbol)

    def get_historical_prices(self, symbols):
        current_date_dt = self.get_datetime()
        current_date = current_date_dt.strftime('%Y-%m-%d')

        if current_date in self.price_cache:
            return self.price_cache[current_date]

        start_date_dt = current_date_dt - Timedelta(days=100)
        start_date = start_date_dt.strftime('%Y-%m-%d')

        price_data = {}

        for symbol in symbols:
            try:
                bars = self.api.get_bars(
                    symbol,
                    TimeFrame.Day,
                    start=start_date_dt.isoformat(),
                    end=current_date_dt.isoformat(),
                    limit=100
                ).df

                if bars.empty:
                    logging.warning(f"No data for {symbol} between {start_date} and {current_date}.")
                    continue

                logging.info(f"Fetched {len(bars)} bars for {symbol}")
                bars = bars.sort_values('timestamp')
                price_data[symbol] = bars['close'].values
            except Exception as e:
                logging.error(f"Error fetching prices for {symbol}: {e}")
                continue

        if not price_data:
            raise ValueError(f"No historical data available for symbols between {start_date} and {current_date}.")

        price_df = pd.DataFrame(price_data)
        self.price_cache[current_date] = price_df
        return price_df


    def on_trading_iteration(self):
        try:
            historical_prices = self.get_historical_prices(self.symbols)
            portfolio_weights = optimize_portfolio(historical_prices)

            for symbol in self.symbols:
                cash, last_price, quantity = self.position_sizing(symbol)

                if cash is None or last_price is None or quantity is None:
                    logging.warning(f"Skipping {symbol} due to error in position sizing.")
                    continue

                logging.info(f"Checking trading conditions for {symbol} - Cash: {cash}, Last Price: {last_price}, Quantity: {quantity}")
                logging.info(f"Position sizing for {symbol} - Quantity: {quantity}, Portfolio Weight: {portfolio_weights.get(symbol, 0)}")

                # Check if cash is available for the trade
                if cash > last_price:
                    probability, sentiment = self.get_sentiment(symbol)
                    logging.info(f"Sentiment for {symbol}: Probability={probability}, Sentiment={sentiment}")

                    # Positive sentiment - Buy
                    if sentiment == "positive" and probability > 0.80:
                        logging.info(f"Buying {symbol} with quantity {quantity}")

                        # Only sell previous positions if they exist
                        if self.last_trades[symbol] == "sell":
                            self.sell_all(symbol)

                        adjusted_quantity = round(quantity * portfolio_weights.get(symbol, 0))
                        if adjusted_quantity > 0:
                            logging.info(f"Placing buy order for {symbol} - Adjusted Quantity: {adjusted_quantity}")
                            order = self.create_order(
                                symbol,
                                adjusted_quantity,
                                "buy",
                                order_type="market",
                                time_in_force="day"
                            )
                            self.submit_order(order)
                            self.last_trades[symbol] = "buy"
                        else:
                            logging.warning(f"Adjusted quantity for {symbol} is zero. No buy order placed.")

                    # Negative sentiment - Sell
                    elif sentiment == "negative" and probability > 0.80:
                        logging.info(f"Selling {symbol}")

                        # Only sell if there's a previous buy trade
                        if self.last_trades[symbol] == "buy":
                            self.sell_all(symbol)

                        adjusted_quantity = round(quantity * portfolio_weights.get(symbol, 0))
                        if adjusted_quantity > 0:
                            logging.info(f"Placing sell order for {symbol} - Adjusted Quantity: {adjusted_quantity}")
                            order = self.create_order(
                                symbol,
                                adjusted_quantity,
                                "sell",
                                order_type="market",
                                time_in_force="day"
                            )
                            self.submit_order(order)
                            self.last_trades[symbol] = "sell"
                        else:
                            logging.warning(f"Adjusted quantity for {symbol} is zero. No sell order placed.")

        except Exception as e:
            logging.error(f"Error during trading iteration: {e}")


    def sell_all(self, symbol):
        """Sell all shares of a specific symbol."""
        try:
            position = self.get_position(symbol)
            if position and position.quantity > 0:
                order = self.create_order(
                    symbol,
                    position.quantity,
                    "sell",
                    order_type="market",
                    time_in_force="day"
                )
                self.submit_order(order)
        except Exception as e:
            logging.error(f"Error selling all for {symbol}: {e}")

if __name__ == "__main__":
    start_date = datetime(2023, 12, 15)
    end_date = datetime(2023, 12, 31)

    broker = Alpaca(ALPACA_CREDS)
    strategy = PortfolioTrader(
        name="PortfolioTrader",
        broker=broker,
        parameters={
            "symbols": None,  # Use default list
            "cash_at_risk": 0.5
        }
    )

    strategy.backtest(
        YahooDataBacktesting,
        start_date,
        end_date,
        parameters={}
    )
