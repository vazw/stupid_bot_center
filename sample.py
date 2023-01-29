import requests

msg = {
    "exchange": "BITKUB",  # any Binance, OKX, bybit : str
    "pair": "BTC/USDT",  # any : str
    "order": "OpenLong",  # "Open{Short, Long}", "Close{All, }{Short, Long}",
    # "TP{Short, Long}", "SL{Short,Long}",
    # "Tailing{Short, Long}" : str
    "amount": "@0.05",  # any @100, $100, %100 : str
    "leverage": 125,  # any  : int
    "callbackRate": 2.3,  # any if side == Tailing : float
    "activeatePrice": 25_100,  # any if side == Tailing : float
    "triggerPrice": 30_000,  # any if side == TP or SL : float
}

if Openlong:
    requests.post(
        "https://127.0.0.1:9999/order",  # ตัวอย่าง
        json=msg,
    )
