# src/evaluator.py

def evaluate_cex_web3_opportunity(
    trade_amount_usd: float,
    cex_name: str,
    cex_sell_price: float,
    web3_buy_price: float,
    dynamic_fees: dict,
    solana_gas_usd: float = 0.002
) -> dict:
    """
    Calcula el rendimiento neto real usando las comisiones actualizadas dinámicamente.
    """
    # 1. Obtener comisión Taker real del CEX (fallback a 0.10% si no existe)
    cex_fee_pct = dynamic_fees.get(cex_name.lower(), 0.0010)
    
    # Comisión estimada de AMM en Jupiter/Solana (~0.08%)
    web3_swap_fee_pct = 0.0008

    # 2. Capital efectivo en DEX descontando tarifa de gas de la red Solana
    effective_capital_usd = trade_amount_usd - solana_gas_usd
    if effective_capital_usd <= 0:
        return {"net_profit_usd": -999.0, "is_viable": False}

    # 3. Compra en DEX (Jupiter)
    tokens_bought = (effective_capital_usd * (1.0 - web3_swap_fee_pct)) / web3_buy_price

    # 4. Venta en CEX descontando la comisión Taker real
    gross_revenue = tokens_bought * cex_sell_price
    net_revenue = gross_revenue * (1.0 - cex_fee_pct)

    # 5. Ganancia neta y margen porcentual
    net_profit_usd = net_revenue - trade_amount_usd
    profit_margin_pct = (net_profit_usd / trade_amount_usd) * 100

    return {
        "net_profit_usd": round(net_profit_usd, 4),
        "profit_margin_pct": round(profit_margin_pct, 3),
        "cex_fee_pct": cex_fee_pct,
        "solana_gas_usd": solana_gas_usd,
        "is_viable": net_profit_usd > 0
    }