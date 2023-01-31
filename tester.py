import requests

msg1 = {
    "passphrase": "somekey",
    "exchange": "BITKUB",
    "symbol": "BTC/USDT",
    "order": "OpenLong",
    "amount": "@0.05",
    "closePercent": 0,
    "stopLossRate": 5.98,
    "maxLossRate": 1,
}

msg2 = {
    "passphrase": "somekey",
    "exchange": "Binance",
}


requests.post(
    "http://127.0.0.1:8888/balance",
    json=msg2,
)
