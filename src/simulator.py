import logging
from datetime import datetime

logger = logging.getLogger("PaperTrader")


class PaperTrader:
    """
    Simulador en memoria para registrar ejecuciones teóricas
    y evaluar el rendimiento del bot sin arriesgar capital real.
    """
    def __init__(self):
        self.trades = []
        self.total_simulated_profit_usd = 0.0

    def record_trade(self, opportunity: dict, direction: str):
        """Registra una operación simulada con timestamp y ganancia neta."""
        trade_entry = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3],
            "direction": direction,
            "buy_price": opportunity["buy_price"],
            "sell_price": opportunity["sell_price"],
            "net_profit": opportunity["net_profit"],
            "amount_usd": opportunity["amount_usd"]
        }
        
        self.trades.append(trade_entry)
        self.total_simulated_profit_usd += opportunity["net_profit"]

        logger.info(
            f"📝 [PAPER TRADE SIMULADO #{len(self.trades)}] "
            f"Dirección: {direction} | "
            f"Ganancia Neta: +${opportunity['net_profit']:.2f} USD | "
            f"Acumulado: +${self.total_simulated_profit_usd:.2f} USD"
        )
        return trade_entry