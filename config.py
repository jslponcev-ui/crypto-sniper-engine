import os

# Lee las variables del sistema (las que pusimos en el Dashboard de Render)
# Si no encuentra alguna, usará el valor por defecto que pongas a la derecha
HELIUS_API_KEY = os.environ.get("HELIUS_API_KEY", "SIN_KEY")
HELIUS_RPC_URL = f"https://mainnet.helius-rpc.com/?api-key={HELIUS_API_KEY}"
TRADE_AMOUNT_USD = float(os.environ.get("TRADE_AMOUNT_USD", 500.0))
PROFIT_THRESHOLD_USD = float(os.environ.get("PROFIT_THRESHOLD_USD", 0.50))
ACTIVE_EXCHANGES = [ "okx"]

# Los tokens no son secretos, así que pueden ir aquí
WATCHED_TOKENS = {
    "SOL": {
        "mint": "So11111111111111111111111111111111111111112",
        "ws_symbol": "SOLUSDT",
        "decimals": 9
    },
    "JUP": {
        "mint": "JUPyiwrYJFskUPiHa7hkeR8VUtAeFoSYbKedZNsDvCN",
        "ws_symbol": "JUPUSDT",
        "decimals": 6
    },
    "BONK": {
        "mint": "DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263",
        "ws_symbol": "1000BONKUSDT",
        "decimals": 5
    },
    "WIF": {
        "mint": "EKpQGSJtjMFqKZ9KQanSqYXRcF8fBopzLHYxdM65zcjm",
        "ws_symbol": "WIFUSDT",
        "decimals": 6
    }
}