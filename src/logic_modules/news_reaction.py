import logging

import gradio as gr

from logic_modules.finbert_utils import estimate_sentiment

logger = logging.getLogger("tradebot")

# Default configuration
config = {"positive_threshold": 0.80, "negative_threshold": 0.80, "verbose": False}


def set_config(new_config):
    global config
    config.update(new_config)


def react_to_news(portfolio, plan, news_data):
    try:
        for symbol, news in news_data.items():
            probability, sentiment = estimate_sentiment(news)

            if config["verbose"]:
                logger.info(f"News for {symbol}: {news}")
                logger.info(
                    f"Sentiment for {symbol}: Probability={probability}, Sentiment={sentiment}"
                )

            if sentiment == "positive" and probability > config["positive_threshold"]:
                plan[symbol] = "buy"

            elif sentiment == "negative" and probability > config["negative_threshold"]:
                plan[symbol] = "sell"

    except Exception as e:
        logger.error(f"Error reacting to news: {e}")


def create_ui():
    with gr.Blocks() as ui:
        positive_threshold = gr.Slider(
            minimum=0.5, maximum=1.0, label="Positive Sentiment Threshold"
        )
        negative_threshold = gr.Slider(
            minimum=0.5, maximum=1.0, label="Negative Sentiment Threshold"
        )
        verbose = gr.Checkbox(label="Verbose Logging")

        update_button = gr.Button("Update News Config")

        update_button.click(
            lambda p, n, v: set_config(
                {"positive_threshold": p, "negative_threshold": n, "verbose": v}
            ),
            inputs=[positive_threshold, negative_threshold, verbose],
            outputs=None,
        )
    return ui
