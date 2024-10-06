import os
import sys

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from unittest.mock import MagicMock

import pytest

from logic_modules.momentum_trading import execute_momentum_trades


def test_execute_momentum_trades():
    strategy = MagicMock()
    strategy.watchlist = ["AAPL", "GOOG"]
    strategy.logger = MagicMock()

    historical_prices = {"AAPL": [150, 155], "GOOG": [1000, 995]}

    plan = {}
    execute_momentum_trades(strategy, plan, historical_prices)

    assert plan["AAPL"] == "buy"
    assert plan["GOOG"] == "sell"
