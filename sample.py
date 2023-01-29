import requests

msg = {
    "exchange": "BITKUB",  # any Binance, OKX, bybit : str
    "pair": "BTC/USDT",  # any : str
    "side": "OpenLong",  # "OpenShort", "CloseLong", "CloseShort", "TP", "SL", "Tailing" : str
    "amount": 0.05,  # any : float
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
