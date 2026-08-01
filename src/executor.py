import asyncio
import logging
import ccxt.pro as ccxtpro
from config import (
    BINANCE_API_KEY, BINANCE_SECRET,
    OKX_API_KEY, OKX_SECRET, OKX_PASSPHRASE
)

logger = logging.getLogger("TradeExecutor")


class TradeExecutor:
    """
    Ejecutor de órdenes Spot en paralelo para garantizar latencia mínima
    y minimizar el riesgo de deslizamiento (Slippage).
    """
    def __init__(self, circuit_breaker=None):
        self.circuit_breaker = circuit_breaker
        
        # Inicializar clientes asíncronos
        self.binance = ccxtpro.binance({
            'apiKey': BINANCE_API_KEY,
            'secret': BINANCE_SECRET,
            'enableRateLimit': True,
        })
        
        self.okx = ccxtpro.okx({
            'apiKey': OKX_API_KEY,
            'secret': OKX_SECRET,
            'password': OKX_PASSPHRASE,
            'enableRateLimit': True,
        })

    async def execute_order(self, exchange, symbol: str, order_type: str, side: str, amount: float, price: float = None):
        """Envía una orden individual a un exchange específico."""
        try:
            logger.info(f"⚡ Enviando orden {side.upper()} en {exchange.id} por {amount} {symbol}...")
            # En producción se usan órdenes 'limit' al precio detectado o 'market' según estrategia
            order = await exchange.create_order(
                symbol=symbol,
                type=order_type,
                side=side,
                amount=amount,
                price=price
            )
            logger.info(f"✅ Orden completada en {exchange.id}: ID {order.get('id')}")
            return order
        except Exception as e:
            error_msg = f"❌ Fallo crítico enviando orden en {exchange.id}: {e}"
            logger.error(error_msg)
            if self.circuit_breaker:
                await self.circuit_breaker.trigger_emergency_stop(error_msg)
            raise e

    async def execute_atomic_arbitrage(self, buy_exchange_id: str, sell_exchange_id: str, symbol: str, amount: float, buy_price: float, sell_price: float):
        """
        Lanza ambas órdenes de compra y venta EN PARALELO.
        Ambas peticiones salen en el mismo tick de CPU.
        """
        exchanges = {
            "binance": self.binance,
            "okx": self.okx
        }
        
        buy_ex = exchanges.get(buy_exchange_id)
        sell_ex = exchanges.get(sell_exchange_id)

        if not buy_ex or not sell_ex:
            logger.error("Exchanges no válidos para la ejecución.")
            return

        logger.info(f"🚀 [DISPARANDO SNIPER ATÓMICO] Comprando en {buy_exchange_id} ➔ Vendiendo en {sell_exchange_id}")

        # Disparo en paralelo vía asyncio.gather
        try:
            results = await asyncio.gather(
                self.execute_order(buy_ex, symbol, 'limit', 'buy', amount, buy_price),
                self.execute_order(sell_ex, symbol, 'limit', 'sell', amount, sell_price),
                return_exceptions=True
            )
            return results
        finally:
            # Asegurar cierre de conexiones de red
            await buy_ex.close()
            await sell_ex.close()