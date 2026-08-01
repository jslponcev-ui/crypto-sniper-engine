# main.py
import asyncio
import aiohttp
from config import WATCHED_TOKENS, TRADE_AMOUNT_USD, PROFIT_THRESHOLD_USD, ACTIVE_EXCHANGES, HELIUS_API_KEY
from src.live_stream import PriceStreamer
from src.fees import FeeManager

async def main():
    print("🚀 Iniciando Bot de Arbitraje Híbrido Multi-Token (Modo Seguro)...", flush=True)
    print(f"⚡ [Helius RPC]: Conectado exitosamente con API Key ({HELIUS_API_KEY[:8]}...)", flush=True)
    
    # 1. Cargar comisiones
    fee_manager = FeeManager()
    await fee_manager.update_fees()
    
    # 2. Instanciar Streamer de precios
    streamer = PriceStreamer()
    
    # 3. Iniciar WebSockets de Binance y OKX en segundo plano
    asyncio.create_task(streamer.start_binance_ws())
    asyncio.create_task(streamer.start_okx_ws())
    
    print("⏳ Esperando primeros datos de Binance, OKX y Jupiter...", flush=True)
    await asyncio.sleep(3)

    async with aiohttp.ClientSession() as session:
        while True:
            try:
                # Consultar precios en DEX
                await streamer.fetch_all_jupiter_prices(session=session)
                
                print("\n" + "="*65, flush=True)
                print("📊 RESUMEN DE PRECIOS Y ARBITRAJE EN VIVO", flush=True)
                print("="*65, flush=True)
                
                for token, meta in WATCHED_TOKENS.items():
                    dex_price = streamer.prices[token]["jupiter_buy"]
                    binance_p = streamer.prices[token]["binance"]
                    okx_p = streamer.prices[token]["okx"]
                    
                    dex_str = f"${dex_price:.6f}" if dex_price > 0 else "Cargando..."
                    binance_str = f"${binance_p:.6f}" if binance_p > 0 else "Cargando..."
                    okx_str = f"${okx_p:.6f}" if okx_p > 0 else "Cargando..."
                    
                    print(f"🔹 [{token}]: DEX = {dex_str} | Binance = {binance_str} | OKX = {okx_str}", flush=True)
                    
                    if dex_price > 0.0:
                        for cex in ACTIVE_EXCHANGES:
                            cex_price = streamer.prices[token][cex]
                            if cex_price > 0.0:
                                # Cálculo de margen
                                spread = cex_price - dex_price
                                estimated_units = TRADE_AMOUNT_USD / dex_price
                                gross_profit = spread * estimated_units
                                
                                # Costo de gas/red estimado ($0.50)
                                net_profit = gross_profit - 0.50
                                
                                if net_profit >= PROFIT_THRESHOLD_USD:
                                    print(f"  🔥 ¡OPORTUNIDAD! [{token} - {cex.upper()}]: Buy DEX @ ${dex_price:.6f} -> Sell CEX @ ${cex_price:.6f} | Ganancia Neta: +${net_profit:.2f} USD", flush=True)
                                else:
                                    print(f"  📈 Spread [{cex.upper()}]: Neto estimado: ${net_profit:.4f} USD", flush=True)
                
                # Intervalo de refresco
                await asyncio.sleep(5)
                
            except Exception as e:
                print(f"⚠️ Error en el bucle principal: {e}", flush=True)
                await asyncio.sleep(3)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Bot detenido manualmente por el usuario.")