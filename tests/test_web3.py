import sys
import os
# Agregar el directorio raíz del proyecto a sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import asyncio
import logging
from src.web3_streamer import JupiterStreamer

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("TestWeb3")


async def main():
    jupiter = JupiterStreamer(input_symbol="USDC", output_symbol="SOL", amount_usd=90.0)
    
    # Iniciar consulta periódica en fondo
    task = asyncio.create_task(jupiter.start_polling(interval_sec=1.0))
    logger.info("⏳ Consultando cotizaciones en tiempo real desde la red de Solana (Jupiter)...")
    
    for _ in range(5):
        await asyncio.sleep(2.0)
        if jupiter.quote_data:
            data = jupiter.quote_data
            logger.info(
                f"⚡ [SOLANA / JUPITER WEB3] "
                f"Precio Efectivo SOL: ${data['buy_price']:.2f} USD | "
                f"Recibirías: {data['out_amount_sol']:.4f} SOL | "
                f"Impacto de Precio: {data['price_impact_pct']:.3f}%"
            )

    await jupiter.stop()
    task.cancel()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass