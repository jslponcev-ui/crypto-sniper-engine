# src/live_stream.py
import asyncio
import json
import websockets
import aiohttp
from config import WATCHED_TOKENS, TRADE_AMOUNT_USD, HELIUS_RPC_URL

# Mint de USDC en Solana
USDC_MINT = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"

class PriceStreamer:
    def __init__(self):
        self.prices = {token: {"binance": 0.0, "okx": 0.0, "jupiter_buy": 0.0} for token in WATCHED_TOKENS}
        self.rpc_url = HELIUS_RPC_URL

    async def start_binance_ws(self):
        streams = "/".join([f"{data['ws_symbol'].lower()}@bookTicker" for data in WATCHED_TOKENS.values()])
        url = f"wss://stream.binance.com:9443/stream?streams={streams}"
        while True:
            try:
                async with websockets.connect(url) as ws:
                    print("🟢 [WebSocket] Conectado a Binance Multi-Token", flush=True)
                    while True:
                        msg = await ws.recv()
                        data = json.loads(msg)
                        if "data" in data:
                            raw = data["data"]
                            symbol_raw = raw['s'].upper()
                            for token, meta in WATCHED_TOKENS.items():
                                if meta["ws_symbol"].upper() == symbol_raw:
                                    price = float(raw['a'])
                                    if token == "BONK":
                                        price = price / 1000.0
                                    self.prices[token]["binance"] = price
                                    break
            except Exception as e:
                print(f"⚠️ [Binance WS Error]: {e}", flush=True)
                await asyncio.sleep(3)

    async def start_okx_ws(self):
        url = "wss://ws.okx.com:8443/ws/v5/public"
        while True:
            try:
                async with websockets.connect(url) as ws:
                    args = []
                    for token in WATCHED_TOKENS.keys():
                        inst = "1000BONK-USDT" if token == "BONK" else f"{token}-USDT"
                        args.append({"channel": "tickers", "instId": inst})
                    sub_msg = {"op": "subscribe", "args": args}
                    await ws.send(json.dumps(sub_msg))
                    print("🟢 [WebSocket] Conectado a OKX Multi-Token", flush=True)
                    while True:
                        msg = await ws.recv()
                        data = json.loads(msg)
                        if "data" in data and len(data["data"]) > 0:
                            inst_id = data["data"][0]["instId"]
                            for token in WATCHED_TOKENS.keys():
                                expected_inst = "1000BONK-USDT" if token == "BONK" else f"{token}-USDT"
                                if inst_id == expected_inst:
                                    price = float(data["data"][0]["askPx"])
                                    if token == "BONK":
                                        price = price / 1000.0
                                    self.prices[token]["okx"] = price
                                    break
            except Exception as e:
                print(f"⚠️ [OKX WS Error]: {e}", flush=True)
                await asyncio.sleep(3)

    async def fetch_token_jupiter(self, session: aiohttp.ClientSession, token: str, meta: dict):
        amount_in_atoms = int(TRADE_AMOUNT_USD * 1_000_000)
        mint = meta["mint"]
        decimals = meta["decimals"]
        url = f"https://quote-api.jup.ag/v6/quote?inputMint={USDC_MINT}&outputMint={mint}&amount={amount_in_atoms}&slippageBps=50"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "application/json"
        }
        try:
            async with session.get(url, headers=headers, timeout=aiohttp.ClientTimeout(total=8.0)) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    out_amount_atoms = float(data.get("outAmount", 0))
                    if out_amount_atoms > 0:
                        tokens_received = out_amount_atoms / (10 ** decimals)
                        price_per_token = TRADE_AMOUNT_USD / tokens_received
                        self.prices[token]["jupiter_buy"] = price_per_token
                else:
                    print(f"⚠️ [Jupiter Debug] Error HTTP {resp.status} para {token}", flush=True)
        except Exception as e:
            print(f"⚠️ [Jupiter Debug] Error de conexión para {token}: {str(e)}", flush=True)

    async def fetch_all_jupiter_prices(self, session: aiohttp.ClientSession):
        tasks = [
            self.fetch_token_jupiter(session, token, meta)
            for token, meta in WATCHED_TOKENS.items()
        ]
        await asyncio.gather(*tasks, return_exceptions=True)