import aiohttp
import asyncio
import logging
from datetime import datetime

logger = logging.getLogger("Web3Streamer")

SOLANA_MINTS = {
    "USDC": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
    "SOL": "So11111111111111111111111111111111111111112",
    "USDT": "Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB"
}


class JupiterStreamer:
    """
    Streamer/Poll optimizado para consultar cotizaciones en Solana (DEX) vía Jupiter.
    """
    def __init__(self, input_symbol: str = "USDC", output_symbol: str = "SOL", amount_usd: float = 90.0):
        self.input_symbol = input_symbol
        self.output_symbol = output_symbol
        self.amount_usd = amount_usd
        
        self.input_mint = SOLANA_MINTS.get(input_symbol)
        self.output_mint = SOLANA_MINTS.get(output_symbol)
        
        self.quote_data = None
        self.last_update = None
        self.is_running = False

        # Endpoints con fallback para evitar Rate Limit (429)
        self.endpoints = [
            "https://quote-api.jup.ag/v6/quote",
            "https://api.jup.ag/swap/v1/quote"
        ]

    async def fetch_quote(self, session: aiohttp.ClientSession, input_mint: str, output_mint: str, amount_atoms: int):
        params = {
            "inputMint": input_mint,
            "outputMint": output_mint,
            "amount": str(amount_atoms),
            "slippageBps": 50
        }
        headers = {"User-Agent": "Mozilla/5.0"}

        for url in self.endpoints:
            try:
                async with session.get(url, params=params, headers=headers, timeout=4.0) as resp:
                    if resp.status == 200:
                        return await resp.json()
                    elif resp.status == 429:
                        await asyncio.sleep(0.5)  # Breve pausa si hay rate limit
                        continue
            except Exception:
                continue
        return None

    async def start_polling(self, interval_sec: float = 2.5):
        """Bucle asíncrono optimizado a 2.5s para respetar rate limits de RPCs libres."""
        self.is_running = True
        logger.info(f"⚡ Streamer Web3 activo en Solana para {self.output_symbol}/{self.input_symbol}...")

        amount_atoms = int(self.amount_usd * 1_000_000)

        async with aiohttp.ClientSession() as session:
            while self.is_running:
                buy_quote = await self.fetch_quote(session, self.input_mint, self.output_mint, amount_atoms)
                
                if buy_quote and "outAmount" in buy_quote:
                    out_amount_sol = int(buy_quote["outAmount"]) / 1_000_000_000
                    if out_amount_sol > 0:
                        effective_buy_price = self.amount_usd / out_amount_sol

                        self.quote_data = {
                            "buy_price": effective_buy_price,
                            "out_amount_sol": out_amount_sol,
                            "price_impact_pct": float(buy_quote.get("priceImpactPct", 0)) * 100,
                            "raw_quote": buy_quote
                        }
                        self.last_update = datetime.now()

                await asyncio.sleep(interval_sec)

    async def stop(self):
        self.is_running = False
        logger.info("🛑 Deteniendo Web3 Streamer...")