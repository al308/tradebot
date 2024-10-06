import logging

import gradio as gr

logger = logging.getLogger("tradebot")

# Default configuration
config = {"momentum_threshold": 0.05, "verbose": False}


def set_config(new_config):
    global config
    config.update(new_config)


def execute_momentum_trades(strategy, plan, historical_prices):
    try:
        # Example logic (replace with actual logic)
        for symbol in strategy.watchlist:
            # Check if historical prices are available
            if symbol not in historical_prices:
                strategy.logger.warning(f"No historical prices for {symbol}")
                continue

            # Example momentum logic
            prices = historical_prices[symbol]
            if len(prices) < 2:
                strategy.logger.warning(f"Not enough data for {symbol}")
                continue

            # Calculate momentum (example)
            momentum = prices[-1] - prices[-2]
            strategy.logger.info(f"Momentum for {symbol}: {momentum}")

            # Decide action based on momentum
            if momentum > 0:
                plan[symbol] = "buy"
            elif momentum < 0:
                plan[symbol] = "sell"

    except Exception as e:
        strategy.logger.error(f"Error executing momentum trades: {e}")


def create_ui():
    with gr.Blocks() as ui:
        momentum_threshold = gr.Slider(
            minimum=0.01, maximum=0.1, label="Momentum Threshold"
        )
        verbose = gr.Checkbox(label="Verbose Logging")

        update_button = gr.Button("Update Momentum Config")

        update_button.click(
            lambda m, v: set_config({"momentum_threshold": m, "verbose": v}),
            inputs=[momentum_threshold, verbose],
            outputs=None,
        )
    return ui
