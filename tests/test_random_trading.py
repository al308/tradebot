# tests/test_random_trading.py
from unittest.mock import MagicMock

import pytest

from logic_modules.random_trading import execute_random_trades, set_config


def test_execute_random_trades_buy():
    strategy = MagicMock()
    strategy.watchlist = ["AAPL", "GOOG"]
    strategy.last_trades = {}

    plan = {}
    set_config({"buy_probability": 1.0, "sell_probability": 0.0})  # Force buy

    execute_random_trades(strategy, plan)

    assert len(plan) == 1
    assert list(plan.values())[0][0] == "buy"


def test_execute_random_trades_sell():
    strategy = MagicMock()
    strategy.watchlist = ["AAPL", "GOOG"]
    strategy.last_trades = {"AAPL": "buy"}

    plan = {}
    set_config({"buy_probability": 0.0, "sell_probability": 1.0})  # Force sell

    execute_random_trades(strategy, plan)

    assert len(plan) == 1
    assert list(plan.values())[0][0] == "sell"
