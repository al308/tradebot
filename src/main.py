import concurrent.futures
import logging
import os
from datetime import datetime, timedelta

import gradio as gr
from alpaca_trade_api import REST, TimeFrame
from dotenv import load_dotenv
from lumibot.backtesting import YahooDataBacktesting
from lumibot.brokers.alpaca import Alpaca
from lumibot.strategies.strategy import Strategy

from logger_setup import setup_logger
from logic_modules.ai_revisor import revise_plan

# Import utility functions and logic modules
from logic_modules.asset_utils import get_sentiment, position_sizing
from logic_modules.momentum_trading import create_ui as create_momentum_ui
from logic_modules.momentum_trading import execute_momentum_trades
from logic_modules.news_reaction import create_ui as create_news_ui
from logic_modules.news_reaction import react_to_news
from logic_modules.portfolio_utils import optimize_portfolio
from logic_modules.price_utils import (
    fetch_historical_prices,
)  # Import the new utility function
from logic_modules.random_trading import create_ui as create_random_ui
from logic_modules.random_trading import execute_random_trades
from logic_modules.transaction_filter import create_ui as create_spread_ui
from logic_modules.transaction_filter import filter_transactions

# Set up the logger
logger = setup_logger()

# Load environment variables from .env file
load_dotenv()

# Credentials
ALPACA_CREDS = {
    "API_KEY": os.getenv("ALPACA_API_KEY"),
    "API_SECRET": os.getenv("ALPACA_API_SECRET"),
    "PAPER": os.getenv("ALPACA_PAPER") != "False",
    "BASE_URL": os.getenv("ALPACA_BASE_URL"),
}


class PortfolioTrader(Strategy):
    def initialize(
        self, symbols=None, cash_at_risk=0.5, timeframe="day", bars_length=150
    ):
        self.api = REST(
            ALPACA_CREDS["API_KEY"],
            ALPACA_CREDS["API_SECRET"],
            base_url=ALPACA_CREDS["BASE_URL"],
        )

        if symbols is None:
            self.symbols = [
                "AAPL",
                "MSFT",
                "GOOG",
                "AMZN",
                "TSLA",
                "JPM",
                "BAC",
                "HSBC",
                "GS",
                "V",
                "PFE",
                "JNJ",
                "MRK",
                "GSK",
                "AZN",
                "XOM",
                "CVX",
                "BP",
                "SHEL",
                "TTE",
                "PG",
                "KO",
                "UL",
                "BA",
                "GE",
            ]
        else:
            self.symbols = symbols

        self.watchlist = self.symbols  # Add this line
        self.sleeptime = "24H"
        self.cash_at_risk = cash_at_risk
        self.timeframe = timeframe
        self.bars_length = bars_length
        self.last_trades = {symbol: None for symbol in self.symbols}

    def position_sizing(self, symbol):
        return position_sizing(self, symbol, self.cash_at_risk)

    def on_trading_iteration(self):
        try:
            historical_prices = fetch_historical_prices(self.api, self.symbols)

            if historical_prices.empty:
                logger.error("No historical prices available.")
                return

            portfolio_weights = optimize_portfolio(historical_prices)
            logger.info(f"Portfolio Weights: {portfolio_weights}")

            plan = {}
            news_data = {}  # Fetch or simulate news data
            spreads = {}  # Fetch or simulate spread data

            react_to_news(self, plan, news_data)
            execute_momentum_trades(self, plan, historical_prices)
            filter_transactions(self, plan, spreads)
            execute_random_trades(self, plan)

            # Revise the plan using AI
            revised_plan = revise_plan(plan)
            logger.info(f"Revised Plan: {revised_plan}")

            for symbol, (action, quantity) in revised_plan.items():
                if action == "buy":
                    logger.info(
                        f"Placing buy order for {symbol} - Quantity: {quantity}"
                    )
                    order = self.create_order(
                        symbol, quantity, "buy", type="market", time_in_force="day"
                    )
                    self.submit_order(order)
                    self.last_trades[symbol] = "buy"

                elif action == "sell":
                    self.sell_all(symbol)

        except Exception as e:
            logger.error(f"Error during trading iteration: {e}")

    def sell_all(self, symbol):
        try:
            position = self.get_position(symbol)
            if position and position.quantity > 0:
                order = self.create_order(
                    symbol,
                    position.quantity,
                    "sell",
                    type="market",
                    time_in_force="day",
                )
                self.submit_order(order)
        except Exception as e:
            logger.error(f"Error selling all for {symbol}: {e}")


def backtest(start_date, end_date):
    broker = Alpaca(ALPACA_CREDS)
    strategy = PortfolioTrader(
        name="PortfolioTrader",
        broker=broker,
        parameters={"symbols": None, "cash_at_risk": 0.5},
    )

    # Ensure the logs directory exists
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)

    # Define the log file path
    log_file_path = os.path.join(log_dir, "my_log.log")

    strategy.backtest(
        YahooDataBacktesting, start_date, end_date, logfile=log_file_path, parameters={}
    )
    logger.info("Backtesting completed.")
    return "Backtesting completed."


def run_backtesting(start_date, end_date):
    logger.info("Starting backtesting...")

    # Convert input strings to datetime objects
    start_date = datetime.strptime(start_date, "%Y-%m-%d")
    end_date = datetime.strptime(end_date, "%Y-%m-%d")

    with concurrent.futures.ProcessPoolExecutor() as executor:
        future = executor.submit(backtest, start_date, end_date)
        return future.result()


def read_log_file():
    with open("my_log.log", "r") as file:
        return file.read()


def create_ui():
    default_start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
    default_end_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

    with gr.Blocks() as demo:
        with gr.Row():
            with gr.Column():
                with gr.Accordion("News Reaction Settings", open=False):
                    create_news_ui()
                with gr.Accordion("Momentum Trading Settings", open=False):
                    create_momentum_ui()
                with gr.Accordion("Transaction Filter Settings", open=False):
                    create_spread_ui()
                with gr.Accordion("Random Trading Settings", open=False):
                    create_random_ui()

                start_date = gr.Textbox(label="Start Date", value=default_start_date)
                end_date = gr.Textbox(label="End Date", value=default_end_date)
                start_button = gr.Button("Start Backtesting")

            with gr.Column():
                log_view = gr.Textbox(label="Log Output", lines=20, interactive=False)
                refresh_button = gr.Button("Refresh Log")

        start_button.click(
            run_backtesting, inputs=[start_date, end_date], outputs=log_view
        )

        refresh_button.click(read_log_file, inputs=[], outputs=log_view)

    return demo


if __name__ == "__main__":
    ui = create_ui()
    ui.launch()
