# config.py

# Credenciales de Helius RPC
HELIUS_API_KEY = "712d85cd-9f99-4a5b-9a77-b24a396bb6f4"
HELIUS_RPC_URL = f"https://mainnet.helius-rpc.com/?api-key={HELIUS_API_KEY}"

# Parámetros de Trading
TRADE_AMOUNT_USD = 500.0
PROFIT_THRESHOLD_USD = 0.50
ACTIVE_EXCHANGES = ["binance", "okx"]

# Mapeo de Tokens y Decimales Oficiales en Solana
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