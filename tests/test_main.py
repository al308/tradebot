# tests/test_main.py
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

from main import PortfolioTrader


@patch("main.fetch_historical_prices")
@patch("main.optimize_portfolio")
@patch("main.revise_plan")
def test_on_trading_iteration(
    mock_revise_plan, mock_optimize_portfolio, mock_fetch_historical_prices
):
    # Create a DataFrame to mock historical prices
    mock_fetch_historical_prices.return_value = pd.DataFrame({"AAPL": [150, 155]})
    mock_optimize_portfolio.return_value = {"AAPL": 1.0}
    mock_revise_plan.return_value = {"AAPL": ("buy", 10)}  # Mock a valid revised plan

    strategy = PortfolioTrader()
    strategy.api = MagicMock()
    strategy.create_order = MagicMock()
    strategy.submit_order = MagicMock()
    strategy.get_position = MagicMock(return_value=MagicMock(quantity=10))
    strategy.logger = MagicMock()

    # Call initialize to set up symbols and other attributes
    strategy.initialize()

    strategy.on_trading_iteration()

    strategy.submit_order.assert_called()
