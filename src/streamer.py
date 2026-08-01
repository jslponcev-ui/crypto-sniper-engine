import asyncio
import time
import logging
import ccxt.pro as ccxtpro
from config import STALE_DATA_MAX_MS

logger = logging.getLogger("WebSocketStreamer")

class OrderBookStreamer:
    def __init__(self, exchange_id: str, symbol: str):
        self.exchange_id = exchange_id
        self.symbol = symbol
        self.orderbook = None
        self.last_update_ms = 0
        self.is_running = False
        
        # Instanciar el cliente WebSocket de CCXT Pro
        exchange_class = getattr(ccxtpro, exchange_id)
        self.exchange = exchange_class({'enableRateLimit': True})

    async def start_stream(self):
        """Escucha el flujo de eventos del OrderBook sin consumir límites de API REST."""
        self.is_running = True
        logger.info(f"🔌 Conectando a WebSocket de {self.exchange_id} para {self.symbol}...")
        
        try:
            while self.is_running:
                # CCXT Pro gestiona el socket asíncrono en tiempo real
                self.orderbook = await self.exchange.watch_order_book(self.symbol)
                self.last_update_ms = int(time.time() * 1000)
        except Exception as e:
            logger.error(f"❌ Error en stream de {self.exchange_id}: {e}")
            raise e
        finally:
            await self.exchange.close()

    def is_data_fresh(self) -> bool:
        """Valida que los datos tengan menos de 500ms de antigüedad."""
        if not self.last_update_ms:
            return False
        current_time_ms = int(time.time() * 1000)
        age = current_time_ms - self.last_update_ms
        return age <= STALE_DATA_MAX_MS

    async def stop(self):
        self.is_running = False
        await self.exchange.close()
        logger.info(f"🛑 WebSocket de {self.exchange_id} cerrado.")