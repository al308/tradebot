import logging

import gradio as gr

logger = logging.getLogger("tradebot")

# Default configuration
config = {"spread_limit": 0.02, "verbose": False}


def set_config(new_config):
    global config
    config.update(new_config)


def filter_transactions(portfolio, plan, spreads):
    try:
        for symbol, action in plan.items():
            spread = spreads.get(symbol, 0)
            if spread > config["spread_limit"]:
                logger.info(f"Spread too high for {symbol}. Rejecting {action} action.")
                del plan[symbol]

    except Exception as e:
        logger.error(f"Error filtering transactions: {e}")


def create_ui():
    with gr.Blocks() as ui:
        spread_limit = gr.Slider(minimum=0.01, maximum=0.1, label="Spread Limit")
        verbose = gr.Checkbox(label="Verbose Logging")

        update_button = gr.Button("Update Spread Config")

        update_button.click(
            lambda s, v: set_config({"spread_limit": s, "verbose": v}),
            inputs=[spread_limit, verbose],
            outputs=None,
        )
    return ui
