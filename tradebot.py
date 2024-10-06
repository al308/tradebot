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
from logic_modules.asset_utils import position_sizing, get_sentiment
from logic_modules.portfolio_utils import optimize_portfolio

from logger_setup import setup_logger

# Set up the logger
logger = setup_logger()

# Load environment variables from .env file
load_dotenv()

# Credentials
ALPACA_CREDS = {
    "API_KEY": os.getenv('ALPACA_API_KEY'),
    "API_SECRET": os.getenv('ALPACA_API_SECRET'),
    "PAPER": os.getenv('ALPACA_PAPER') != 'False',
    "BASE_URL": os.getenv('ALPACA_BASE_URL')
}

# Define the strategy
class PortfolioTrader(Strategy):
    def initialize(self, symbols: list = None, cash_at_risk: float = 0.5, timeframe='day', bars_length=150):
        # Initialize the API
        self.api = REST(ALPACA_CREDS["API_KEY"], ALPACA_CREDS["API_SECRET"], base_url=ALPACA_CREDS["BASE_URL"])
        
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
        self.timeframe = timeframe
        self.bars_length = bars_length  # Number of historical bars to fetch
        self.last_trades = {symbol: None for symbol in self.symbols}

    def position_sizing(self, symbol):
        return position_sizing(self, symbol, self.cash_at_risk)

    def fetch_historical_prices(self):
        logging.info(f"Fetching historical prices for {', '.join(self.symbols)}")

        try:
            # Ensure no 'quote' parameter is passed
            bars = self.api.get_bars(
                self.symbols,
                TimeFrame.Day,
                limit=30  # Adjust this as needed
            )

            price_data = {}
            for symbol in self.symbols:
                df = bars.df[bars.df['symbol'] == symbol]
                if df.empty:
                    logging.warning(f"No data for {symbol}")
                else:
                    price_data[symbol] = df['close'].values

            price_df = pd.DataFrame(price_data)
            logging.info(f"Retrieved historical prices: {price_df.head()}")
            return price_df

        except Exception as e:
            logging.error(f"Error fetching historical prices: {e}")
            raise


    def on_trading_iteration(self):
        try:
            historical_prices = self.fetch_historical_prices()
            
            # Check if historical prices are valid
            if historical_prices.empty:
                logger.error("No historical prices available.")
                return

            portfolio_weights = optimize_portfolio(historical_prices)
            logger.info(f"Portfolio Weights: {portfolio_weights}")

            for symbol in self.symbols:
                cash, last_price, quantity = self.position_sizing(symbol)

                if cash is None or last_price is None or quantity is None:
                    logger.warning(f"Skipping {symbol} due to error in position sizing.")
                    continue

                logger.info(f"Checking trading conditions for {symbol} - Cash: {cash}, Last Price: {last_price}, Quantity: {quantity}")
                logger.info(f"Position sizing for {symbol} - Quantity: {quantity}, Portfolio Weight: {portfolio_weights.get(symbol, 0)}")

                # Check if cash is available for the trade
                if cash > last_price:
                    probability, sentiment = get_sentiment(self, symbol)
                    logger.info(f"Sentiment for {symbol}: Probability={probability}, Sentiment={sentiment}")

                    # Positive sentiment - Buy
                    if sentiment == "positive" and probability > 0.80:
                        logger.info(f"Buying {symbol} with quantity {quantity}")

                        if self.last_trades[symbol] == "sell":
                            self.sell_all(symbol)

                        adjusted_quantity = round(quantity * portfolio_weights.get(symbol, 0))
                        if adjusted_quantity > 0:
                            logger.info(f"Placing buy order for {symbol} - Adjusted Quantity: {adjusted_quantity}")
                            order = self.create_order(
                                symbol,
                                adjusted_quantity,
                                "buy",
                                type="market",
                                time_in_force="day"
                            )
                            self.submit_order(order)
                            self.last_trades[symbol] = "buy"
                        else:
                            logger.warning(f"Adjusted quantity for {symbol} is zero. No buy order placed.")

                    # Negative sentiment - Sell
                    elif sentiment == "negative" and probability > 0.80:
                        logger.info(f"Selling {symbol}")

                        if self.last_trades[symbol] == "buy":
                            self.sell_all(symbol)

                        adjusted_quantity = round(quantity * portfolio_weights.get(symbol, 0))
                        if adjusted_quantity > 0:
                            logger.info(f"Placing sell order for {symbol} - Adjusted Quantity: {adjusted_quantity}")
                            order = self.create_order(
                                symbol,
                                adjusted_quantity,
                                "sell",
                                type="market",
                                time_in_force="day"
                            )
                            self.submit_order(order)
                            self.last_trades[symbol] = "sell"
                        else:
                            logger.warning(f"Adjusted quantity for {symbol} is zero. No sell order placed.")

        except Exception as e:
            logger.error(f"Error during trading iteration: {e}")


    def sell_all(self, symbol):
        """Sell all shares of a specific symbol."""
        try:
            position = self.get_position(symbol)
            if position and position.quantity > 0:
                order = self.create_order(
                    symbol,
                    position.quantity,
                    "sell",
                    type="market",
                    time_in_force="day"
                )
                self.submit_order(order)
        except Exception as e:
            logger.error(f"Error selling all for {symbol}: {e}")

if __name__ == "__main__":
    start_date = datetime(2023, 11, 15)
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
        logfile="my_log.log",
        parameters={}
    )
