import pandas as pd
from pypfopt.efficient_frontier import EfficientFrontier
from pypfopt.expected_returns import mean_historical_return
from pypfopt.risk_models import CovarianceShrinkage

def optimize_portfolio(historical_prices):
    """Optimize portfolio allocation using PyPortfolioOpt."""
    mu = mean_historical_return(historical_prices)
    S = CovarianceShrinkage(historical_prices).ledoit_wolf()
    ef = EfficientFrontier(mu, S)
    ef.max_sharpe()
    cleaned_weights = ef.clean_weights()
    return cleaned_weights
