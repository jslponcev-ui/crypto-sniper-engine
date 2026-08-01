import logging
import sys
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID

logger = logging.getLogger("TelegramNotifier")


class TelegramNotifier:
    """
    Módulo de notificaciones y control remoto vía Telegram.
    """
    def __init__(self, circuit_breaker=None):
        self.token = TELEGRAM_BOT_TOKEN
        self.chat_id = TELEGRAM_CHAT_ID
        self.circuit_breaker = circuit_breaker
        self.app = None

        if self.token and self.token != "tu_token_de_telegram_aqui":
            self.app = ApplicationBuilder().token(self.token).build()
            self._setup_handlers()

    def _setup_handlers(self):
        """Registra los comandos del bot de Telegram."""
        if not self.app:
            return
        self.app.add_handler(CommandHandler("status", self._cmd_status))
        self.app.add_handler(CommandHandler("pause", self._cmd_pause))
        self.app.add_handler(CommandHandler("resume", self._cmd_resume))
        self.app.add_handler(CommandHandler("reset", self._cmd_reset))

    async def _cmd_status(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not self.circuit_breaker:
            await update.message.reply_text("ℹ️ Circuit Breaker no vinculado.")
            return

        status = "PAUSADO ⏸️" if self.circuit_breaker.is_paused else "EN VIVO 🟢"
        msg = (
            f"📊 *Estado del Crypto Sniper Engine*\n"
            f"• Estado: {status}\n"
            f"• Filtro: Ganancia Neta ≥ $1.00 USD\n"
            f"• Conexión: WebSockets Activos (Binance ↔ OKX)"
        )
        await update.message.reply_text(msg, parse_mode="Markdown")

    async def _cmd_pause(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if self.circuit_breaker:
            self.circuit_breaker.pause()
            await update.message.reply_text("⏸️ *Sniper Pausado.* El monitoreo se ha detenido de forma segura.", parse_mode="Markdown")

    async def _cmd_resume(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if self.circuit_breaker:
            self.circuit_breaker.resume()
            await update.message.reply_text("▶️ *Sniper Reanudado.* Monitoreando brechas en tiempo real...", parse_mode="Markdown")

    async def _cmd_reset(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("🔄 *Reiniciando proceso Python...*", parse_mode="Markdown")
        sys.exit(0)  # Cierra la instancia para que systemd o el launcher la reinicie limpia

    async def send_alert(self, text: str):
        """Envía un mensaje proactivo al chat configurado."""
        if not self.app or not self.chat_id:
            logger.warning(f"⚠️ Alerta Telegram omitida (no configurado): {text}")
            return

        try:
            await self.app.bot.send_message(chat_id=self.chat_id, text=text, parse_mode="Markdown")
        except Exception as e:
            logger.error(f"❌ Error al enviar notificación a Telegram: {e}")

    async def start_polling(self):
        """Inicia la escucha de comandos de Telegram en segundo plano."""
        if self.app:
            logger.info("🤖 Bot de Telegram inicializado y escuchando comandos...")
            await self.app.initialize()
            await self.app.start()
            await self.app.updater.start_polling()

    async def stop(self):
        """Detiene la conexión con Telegram de forma limpia."""
        if self.app:
            await self.app.updater.stop()
            await self.app.stop()
            await self.app.shutdown()