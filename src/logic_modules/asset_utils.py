import logging
from datetime import datetime

import torch
from pandas import Timedelta

from logger_setup import setup_logger
from logic_modules.finbert_utils import estimate_sentiment

# Set up the logger
logger = setup_logger()


def get_dates(strategy_instance):
    """Get today's date and the date three days prior."""
    today = strategy_instance.get_datetime()
    three_days_prior = today - Timedelta(days=3)
    return today.strftime("%Y-%m-%d"), three_days_prior.strftime("%Y-%m-%d")


def position_sizing(strategy_instance, symbol, cash_at_risk):
    """Calculate position size based on cash at risk."""
    cash = strategy_instance.get_cash()
    last_price = strategy_instance.get_last_price(symbol)
    quantity = round(
        (cash * cash_at_risk / len(strategy_instance.symbols)) / last_price, 0
    )
    return cash, last_price, quantity


def get_sentiment(strategy_instance, symbol):
    """Estimate sentiment for a given symbol."""
    today, three_days_prior = get_dates(strategy_instance)
    try:
        news = strategy_instance.api.get_news(
            symbol=symbol, start=three_days_prior, end=today
        )
        headlines = [article.headline for article in news]
        if not headlines:
            logger.info(
                "No news available for %s between %s and %s.",
                symbol,
                three_days_prior,
                today,
            )
            return 0.0, "neutral"

        probability, sentiment = estimate_sentiment(headlines)

        # Convert tensor to float
        if isinstance(probability, torch.Tensor):
            probability = probability.item()  # Convert tensor to a Python float

        logger.info("Good news for %s probability: %f", symbol, probability)
        return probability, sentiment
    except Exception as e:
        logger.error("Error fetching news for %s: %s", symbol, e)
        return 0.0, "neutral"
