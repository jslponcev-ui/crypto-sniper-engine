import pytest
from src.evaluator import SniperEvaluator


def test_no_opportunity_when_prices_are_equal():
    evaluator = SniperEvaluator(min_profit_usd=1.00)
    
    # Precios idénticos en ambos lados
    buy_book = {"asks": [[60000.0, 2.0]], "bids": [[59990.0, 2.0]]}
    sell_book = {"asks": [[60005.0, 2.0]], "bids": [[60000.0, 2.0]]}

    res = evaluator.evaluate_opportunity(buy_book, sell_book, amount_usd=100.0)
    assert res["is_valid"] is False
    assert res["reason"] == "No spread"


def test_profit_below_threshold_is_rejected():
    evaluator = SniperEvaluator(min_profit_usd=1.00)
    
    # Brecha de precio muy pequeña ($0.10 USD de beneficio)
    buy_book = {"asks": [[60000.0, 5.0]]}
    sell_book = {"bids": [[60010.0, 5.0]]}

    res = evaluator.evaluate_opportunity(buy_book, sell_book, amount_usd=90.0)
    assert res["is_valid"] is False
    assert "below threshold" in res["reason"]


def test_valid_sniper_opportunity_approved():
    evaluator = SniperEvaluator(min_profit_usd=1.00, fee_rate=0.001)
    
    # Brecha de precio amplia suficiente para cubrir fees y dejar > $1.00 USD
    buy_book = {"asks": [[50000.0, 10.0]]}   # Comprar BTC a $50,000
    sell_book = {"bids": [[52000.0, 10.0]]}  # Vender BTC a $52,000

    res = evaluator.evaluate_opportunity(buy_book, sell_book, amount_usd=100.0)
    
    assert res["is_valid"] is True
    assert res["net_profit"] > 1.00
    assert res["buy_price"] == 50000.0
    assert res["sell_price"] == 52000.0