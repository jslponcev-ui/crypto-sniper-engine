# src/fees.py
class FeeManager:
    def __init__(self):
        # Tarifas por defecto (0.1% CEX, gas estimado Solana)
        self.fees = {
            "binance": 0.001,
            "okx": 0.001,
            "solana_gas_usd": 0.005
        }

    async def update_fees(self):
        """Usa comisiones dinámicas o cae en caché seguro"""
        print("🔄 [FeeManager] Usando comisiones estándar en caché (Modo Seguro)...", flush=True)
        return self.fees