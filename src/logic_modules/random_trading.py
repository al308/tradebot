# random_trading.py
import logging
import random

import gradio as gr

logger = logging.getLogger("tradebot")

# Configuration for random trading
config = {
    "buy_probability": 0.5,
    "sell_probability": 0.5,
    "min_quantity": 1,
    "max_quantity": 10,
}


def set_config(new_config):
    global config
    config.update(new_config)


def execute_random_trades(strategy, plan):
    try:
        if random.random() < config["buy_probability"]:
            symbol = random.choice(strategy.watchlist)
            quantity = random.randint(config["min_quantity"], config["max_quantity"])
            logger.info(f"Random buy: {symbol}, Quantity: {quantity}")
            plan[symbol] = ("buy", quantity)

        if random.random() < config["sell_probability"]:
            portfolio_symbols = [
                symbol
                for symbol in strategy.last_trades
                if strategy.last_trades[symbol] == "buy"
            ]
            if portfolio_symbols:
                symbol = random.choice(portfolio_symbols)
                quantity = random.randint(
                    config["min_quantity"], config["max_quantity"]
                )
                logger.info(f"Random sell: {symbol}, Quantity: {quantity}")
                plan[symbol] = ("sell", quantity)

    except Exception as e:
        logger.error(f"Error executing random trades: {e}")


def create_ui():
    with gr.Blocks() as ui:
        buy_probability = gr.Slider(
            minimum=0.0,
            maximum=1.0,
            value=config["buy_probability"],
            label="Buy Probability",
        )
        sell_probability = gr.Slider(
            minimum=0.0,
            maximum=1.0,
            value=config["sell_probability"],
            label="Sell Probability",
        )
        min_quantity = gr.Number(value=config["min_quantity"], label="Min Quantity")
        max_quantity = gr.Number(value=config["max_quantity"], label="Max Quantity")

        update_button = gr.Button("Update Random Trade Config")

        update_button.click(
            lambda bp, sp, min_q, max_q: set_config(
                {
                    "buy_probability": bp,
                    "sell_probability": sp,
                    "min_quantity": int(min_q),
                    "max_quantity": int(max_q),
                }
            ),
            inputs=[buy_probability, sell_probability, min_quantity, max_quantity],
            outputs=None,
        )
    return ui
