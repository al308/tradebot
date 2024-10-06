# tests/test_transaction_filter.py
import pytest

from logic_modules.transaction_filter import filter_transactions, set_config


def test_filter_transactions():
    plan = {"AAPL": "buy", "GOOG": "sell"}
    spreads = {"AAPL": 0.03, "GOOG": 0.01}

    set_config({"spread_limit": 0.02})

    filter_transactions(None, plan, spreads)

    assert "AAPL" not in plan
    assert "GOOG" in plan
