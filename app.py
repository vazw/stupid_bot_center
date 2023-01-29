import uvicorn
from fastapi import FastAPI, Request
from app_exchange import *
from app_exchange.utils import SECRET_KEY


async def get_balance(exchange):
    if exchange == "Binance":
        await Binance.account_balance.update_balance()
        return Binance.account_balance.balance
    elif exchange == "Bitkub":
        pass
    else:
        return 404


async def make_order(order_info):
    if exchange == "Binance":
        await Binance.account_balance.update_balance()
        return await Binance.signal_handle(order_info)
    elif exchange == "Bitkub":
        pass
    else:
        return 404


app = FastAPI()


@app.get("/")
async def read_root():
    return {"Hello": "World"}


@app.post("/order")
async def order(info: Request):
    """
    msg = {
    "passphrase": "abcd1234", # any : str
    "exchange": "BITKUB",  # any Binance, OKX, bybit : str
    "symbol": "BTC/USDT",  # any : str
    "order": "OpenLong",  # "Open{Short, Long}", "Close{All, }{Short, Long}",
                         # "TP{Short, Long}", "SL{Short,Long}",
                         # "Tailing{Short, Long}" : str
    "amount": 0.05,  # any : float
    "leverage": 125,  # any  : int
    "callbackRate": 2.3,  # any if side == Tailing : float
    "activeatePrice": 25_100,  # any if side == Tailing : float
    "triggerPrice": 30_000,  # any if side == TP or SL : float
    }
    """
    order_info = await info.json()
    if order_info["passphrase"] != SECRET_KEY:
        return {"status": "fail", "data": "Invalid"}

    try:
        order = await make_order(order_info)
        return {"status": "SUCCESS", "data": order}
    except Exception:
        return {"status": "fail", "data": 404}


@app.post("/balance")
async def balance(info: Request):
    """
    payload : {"passphrase": "abcd1234" ,"exchange": "Binance"} # OKX Bitkub ..any
    """
    req_info = await info.json()
    exchange_info = req_info["exchange"]
    if req_info["passphrase"] != SECRET_KEY:
        return {"status": "fail", "data": "Invalid"}
    try:
        balance = await get_balance(exchange_info)
        print(balance)
        return {"status": "SUCCESS", "data": balance}
    except Exception:
        return {"status": "Fail", "data": 404}


if __name__ == "__main__":
    uvicorn.run(app, port=8888)
