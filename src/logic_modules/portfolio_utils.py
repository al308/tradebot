import pandas as pd
from pypfopt.efficient_frontier import EfficientFrontier
from pypfopt.expected_returns import mean_historical_return
from pypfopt.risk_models import CovarianceShrinkage


def optimize_portfolio(historical_prices):
    """Optimize portfolio allocation using PyPortfolioOpt."""
    try:
        # Check for empty or NaN values
        if historical_prices.empty or historical_prices.isnull().values.any():
            raise ValueError("Historical prices data is empty or contains NaN values.")

        # Ensure there are enough data points
        if len(historical_prices) < 2:
            raise ValueError("Not enough data points for optimization.")

        mu = mean_historical_return(historical_prices)
        S = CovarianceShrinkage(historical_prices).ledoit_wolf()
        ef = EfficientFrontier(mu, S)
        ef.max_sharpe()
        cleaned_weights = ef.clean_weights()

        print("Optimized Weights:", cleaned_weights)

        return cleaned_weights
    except Exception as e:
        print(f"Error optimizing portfolio: {e}")
        return {}
