import logging  # Add this line
from pandas import Timedelta
from datetime import datetime
from finbert_utils import estimate_sentiment
import torch

def get_dates(strategy_instance):
    today = strategy_instance.get_datetime()
    three_days_prior = today - Timedelta(days=3)
    return today.strftime('%Y-%m-%d'), three_days_prior.strftime('%Y-%m-%d')

def position_sizing(strategy_instance, symbol, cash_at_risk):
    cash = strategy_instance.get_cash()
    last_price = strategy_instance.get_last_price(symbol)
    quantity = round((cash * cash_at_risk / len(strategy_instance.symbols)) / last_price, 0)
    return cash, last_price, quantity

def get_sentiment(strategy_instance, symbol):
    today, three_days_prior = get_dates(strategy_instance)
    try:
        news = strategy_instance.api.get_news(
            symbol=symbol,
            start=three_days_prior,
            end=today
        )
        headlines = [article.headline for article in news]
        if not headlines:
            logging.info(f"No news available for {symbol} between {three_days_prior} and {today}.")
            return 0.0, "neutral"
        
        probability, sentiment = estimate_sentiment(headlines)
        
        # Convert tensor to float
        if isinstance(probability, torch.Tensor):
            probability = probability.item()  # Convert tensor to a Python float
        
        print("Good news for", symbol, "probability:", probability)
        return probability, sentiment
    except Exception as e:
        logging.error(f"Error fetching news for {symbol}: {e}")
        return 0.0, "neutral"

