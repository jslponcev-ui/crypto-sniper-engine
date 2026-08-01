import sys
import logging
import asyncio

logger = logging.getLogger("CircuitBreaker")

class CircuitBreaker:
    """
    Guardián de seguridad: Pausa o detiene el proceso al PRIMER error grave.
    """
    def __init__(self, telegram_notifier=None):
        self.is_paused = False
        self.telegram = telegram_notifier

    async def trigger_emergency_stop(self, error_msg: str):
        """Dispara el freno de mano al primer error irrecuperable."""
        self.is_paused = True
        critical_log = f"🚨 [CRITICAL STOP] El bot se ha detenido por seguridad: {error_msg}"
        logger.critical(critical_log)

        if self.telegram:
            await self.telegram.send_alert(critical_log)

        await asyncio.sleep(1)
        sys.exit(1)

    def pause(self):
        self.is_paused = True
        logger.warning("⏸️ Sistema pausado manualmente por el usuario.")

    def resume(self):
        self.is_paused = False
        logger.info("▶️ Sistema reanudado.")