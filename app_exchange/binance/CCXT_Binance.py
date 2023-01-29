from datetime import datetime

import ccxt.async_support as ccxt
import pandas as pd

from app_exchange.utils import notify_send, ORDER_ENABLE, MIN_BALANCE

statcln = [
    "symbol",
    "entryPrice",
    "positionSide",
    "unrealizedProfit",
    "positionAmt",
    "initialMargin",
    "leverage",
]


def get_order_id() -> str:
    id = datetime.now().isoformat()
    return f"stupid_{id}"


async def connect() -> ccxt.binance:
    return ccxt.binance()


async def connect_loads() -> ccxt.binance:
    exchange = ccxt.binance()
    await exchange.load_markets(reload=True)
    return exchange


async def disconnect(exchange: ccxt.binance):
    return await exchange.close()


class PositionMode:
    def __init__(self):
        self.dualSidePosition: bool = False
        self.Sside: str = "BOTH"
        self.Lside: str = "BOTH"

    async def get_currentmode(self):
        exchange = await connect()
        try:
            currentMODE = await exchange.fapiPrivate_get_positionside_dual()
        except Exception:
            await disconnect(exchange)
            exchange = await connect()
            currentMODE = await exchange.fapiPrivate_get_positionside_dual()
        await disconnect(exchange)
        self.dualSidePosition = currentMODE["dualSidePosition"]
        if currentMode.dualSidePosition:
            self.Sside = "SHORT"
            self.Lside = "LONG"


class AccountBalance:
    """docstring for AccountBalance."""

    def __init__(self):
        self.balance = ""
        self.fiat_balance = ""

    async def update_balance(self):
        exchange = await connect()
        try:
            balance = await exchange.fetch_balance()
            await disconnect(exchange)
            self.balance = balance
            self.fiat_balance = {
                x: y for x, y in balance.items() if "USD" in x[-4:]
            }
        except Exception:
            await disconnect(exchange)
            exchange = await connect()
            balance = await exchange.fetch_balance()
            await disconnect(exchange)
            self.balance = balance
            self.fiat_balance = {
                x: y for x, y in balance.items() if "USD" in x[-4:]
            }


account_balance = AccountBalance()
currentMode = PositionMode()


async def get_bidask(
    symbol: str, exchange: ccxt.binance, bidask: str = "ask"
) -> float:
    try:
        info = (await exchange.fetch_bids_asks())[symbol][bidask]
    except Exception:
        info = (await exchange.fetch_bids_asks())[symbol[:-5]][bidask]
    return float(info)


# set leverage
async def setleverage(symbol: str, lev: int, exchange: ccxt.binance) -> int:
    try:
        await exchange.set_leverage(lev, symbol)
        return lev
    except Exception as e:
        print(e)
        lever = await exchange.fetch_positions_risk([symbol])
        for x in range(len(lever)):
            if (lever[x]["symbol"]) == symbol:
                lev = round(lever[x]["leverage"], 0)
                await exchange.set_leverage(int(lev), symbol)
                break
        return int(lev)


async def closeall_order(data, position_data, side):
    # position_size = abs(float(position_data["positionAmt"][data["symbol"]]))
    # position_entry = float(position_data["entryPrice"][data["symbol"]])
    # position_lev = int(position_data["leverage"][data["symbol"]])
    #
    # order = await exchange.create_order(
    #     symbol=data["symbol"],
    #     positionSide=side,
    #     side=data["order_side"],
    #     type="MARKET",
    #     quantity=position_size,
    # )
    # print(order)
    # margin = position_entry * position_size / position_lev
    # balance = check_balance("USDT")
    # profit_loss = float(position_data["unRealizedProfit"][data["symbol"]])
    #
    # message = (
    #     f"Binance Bot: {BOT_NAME}\n"
    #     + f"Coin       : {data['symbol']}\n"
    #     + "Order      : CloseAll\n"
    #     + f"Amount     : {position_size}\n"
    #     + f"Margin     : {round(margin, 2)}USDT\n"
    #     + f"P/L        : {round(profit_loss, 2)} USDT\n"
    #     + f"Leverage   : X{position_lev}\n"
    #     + f"Balance    : {round(balance, 2)} USDT"
    # )
    pass


async def tailing_stop_order(
    symbol: str,
    exchange: ccxt.binance,
    side: str,
    amount: float,
    triggerPrice: float,
    callbackrate: float,
    currentMode: dict,
    hedge_side: str,
) -> None:
    orderid = get_order_id()
    if currentMode["dualSidePosition"]:
        ordertailingSL = await exchange.create_order(
            symbol,
            "TRAILING_STOP_MARKET",
            side,
            amount,
            params={
                "activationPrice": triggerPrice,
                "callbackRate": callbackrate,
                "positionSide": hedge_side,
                "newClientOrderId": orderid,
            },
        )
    else:
        ordertailingSL = await exchange.create_order(
            symbol,
            "TRAILING_STOP_MARKET",
            side,
            amount,
            params={
                "activationPrice": triggerPrice,
                "callbackRate": callbackrate,
                "reduceOnly": True,
                "positionSide": hedge_side,
                "newClientOrderId": orderid,
            },
        )
    print(ordertailingSL)
    msg2 = (
        "BINANCE:"
        + f"\nCoin        : {symbol}"
        + "\nStatus      : Tailing-StopLoss"
        + f"\nAmount      : {amount}"
        + f"\nCallbackRate: {callbackrate}%"
        + f"\ntriggerPrice: {triggerPrice}"
    )
    notify_send(msg2)


async def order_sl(
    symbol: str,
    exchange: ccxt.binance,
    amount: float,
    stop: float,
    side: str,
    currentMode: dict,
    hedge_side: str,
) -> None:
    orderid = get_order_id()
    if currentMode["dualSidePosition"]:
        orderSL = await exchange.create_order(
            symbol,
            "stop",
            side,
            amount,
            stop,
            params={
                "stopPrice": stop,
                "triggerPrice": stop,
                "positionSide": hedge_side,
                "newClientOrderId": orderid,
            },
        )
    else:
        orderSL = await exchange.create_order(
            symbol,
            "stop",
            side,
            amount,
            stop,
            params={
                "stopPrice": stop,
                "triggerPrice": stop,
                "reduceOnly": True,
                "positionSide": hedge_side,
                "newClientOrderId": orderid,
            },
        )
    print(orderSL)
    msg = (
        "BINANCE:"
        + f"\nCoin        : {symbol}"
        + "\nStatus      : StopLoss"
        + f"\nAmount      : {amount}"
        + f"\nStop Price  : {stop}"
    )
    notify_send(msg)


async def order_tp(
    symbol: str,
    stop_price: float,
    exchange: ccxt.binance,
    amount: float,
    side: str,
    currentMode: dict,
    hedge_side: str,
) -> None:
    orderid = get_order_id()
    if currentMode["dualSidePosition"]:
        orderTP = await exchange.create_order(
            symbol,
            "TAKE_PROFIT_MARKET",
            side,
            amount,
            stop_price,
            params={
                "stopPrice": stop_price,
                "triggerPrice": stop_price,
                "positionSide": hedge_side,
                "newClientOrderId": orderid,
            },
        )
    else:
        orderTP = await exchange.create_order(
            symbol,
            "TAKE_PROFIT_MARKET",
            side,
            amount,
            stop_price,
            params={
                "stopPrice": stop_price,
                "triggerPrice": stop_price,
                "reduceOnly": True,
                "positionSide": hedge_side,
                "newClientOrderId": orderid,
            },
        )
    print(orderTP)
    msg = (
        "BINANCE:"
        + f"\nCoin        : {symbol}"
        + "\nStatus      : StopLoss"
        + f"\nAmount      : {amount}"
        + f"\ntriggerPrice: {stop_price}"
    )
    notify_send(msg)


# OpenLong=Buy
async def OpenLong():
    pass


# OpenShort=Sell
async def OpenShort():
    pass


# CloseLong=Sell
async def CloseLong():
    pass


# CloseShort=Buy
async def CloseShort():
    pass


def check_amount(actions, position_data) -> float:
    if (
        actions == "CloseLong"
        or actions == "OpenLong"
        or actions == "CloseAllLong"
        or actions == "TPLong"
        or actions == "SLLong"
        or actions == "TailingLong"
    ):
        return position_data["amount_long"]
    elif (
        actions == "CloseShort"
        or actions == "OpenShort"
        or actions == "CloseAllShort"
        or actions == "TPShort"
        or actions == "SLShort"
        or actions == "TailingShort"
    ):
        return position_data["amount_short"]
    elif actions == "test":
        return 0.0
    else:
        return 0.0


def check_actions(actions) -> str:
    if (
        actions == "CloseLong"
        or actions == "OpenShort"
        or actions == "CloseAllLong"
        or actions == "TPLong"
        or actions == "SLLong"
        or actions == "TailingLong"
    ):
        return "sell"
    elif (
        actions == "CloseShort"
        or actions == "OpenLong"
        or actions == "CloseAllShort"
        or actions == "TPShort"
        or actions == "SLShort"
        or actions == "TailingShort"
    ):
        return "buy"
    elif actions == "test":
        return "test"
    else:
        return "test"


async def get_current_position(symbol) -> pd.DataFrame:
    balance = account_balance.balance
    positions = balance["info"]["positions"]
    status = pd.DataFrame(
        [
            position
            for position in positions
            if float(position["positionAmt"]) != 0
        ],
        columns=statcln,
    )
    posim = symbol  # "BTCUSDT"
    if status is None:
        return
    status = status[status["symbol"] == posim]

    if status.empty:
        amt_short = 0.0
        amt_long = 0.0
        upnl_short = 0.0
        upnl_long = 0.0

    elif len(status.index) > 1:
        amt_long = float(
            (
                status["positionAmt"][i]
                for i in status.index
                if status["symbol"][i] == posim
                and status["positionSide"][i] == "LONG"
            ).__next__()
        )
        amt_short = float(
            (
                status["positionAmt"][i]
                for i in status.index
                if status["symbol"][i] == posim
                and status["positionSide"][i] == "SHORT"
            ).__next__()
        )
        upnl_long = float(
            (
                status["unrealizedProfit"][i]
                for i in status.index
                if status["symbol"][i] == posim
                and status["positionSide"][i] == "LONG"
            ).__next__()
        )
        upnl_short = float(
            (
                status["unrealizedProfit"][i]
                for i in status.index
                if status["symbol"][i] == posim
                and status["positionSide"][i] == "SHORT"
            ).__next__()
        )

    else:
        amt = float(
            (
                status["positionAmt"][i]
                for i in status.index
                if status["symbol"][i] == posim
            ).__next__()
        )
        amt_long = amt if amt > 0 else 0.0
        amt_short = amt if amt < 0 else 0.0
        upnl = float(
            (
                status["unrealizedProfit"][i]
                for i in status.index
                if status["symbol"][i] == posim
            ).__next__()
        )
        upnl_long = upnl if amt != 0 else 0.0
        upnl_short = upnl if amt != 0 else 0.0

    is_in_Long = True if amt_long != 0 else False
    is_in_Short = True if amt_short != 0 else False

    return {
        "is_in_long": is_in_Long,
        "amount_long": amt_long,
        "pnl_long": upnl_long,
        "is_in_short": is_in_Short,
        "amount_short": amt_short,
        "pnl_short": upnl_short,
    }


async def amount_precision(
    symbol, exchange, order_amount, position_amount, action
) -> float:
    m = len(order_amount)
    bidask = await get_bidask(
        symbol, exchange, "bid" if action == "SELL" else "ask"
    )
    if order_amount[0] == "%":
        percent = float(order_amount[1:m])
        amount = percent / 100 * position_amount
        return exchange.amount_to_precision(symbol, amount)
    elif order_amount[0] == "@":
        fiat = float(order_amount[1:m])
        return exchange.amount_to_precision(symbol, fiat)
    elif order_amount[0] == "$":
        usd = float(order_amount[1:m])
        return exchange.amount_to_precision(symbol, usd / bidask)
    else:
        return 0


async def ordering(order_data, position_data, exchange):
    """{
        "is_in_long": is_in_Long,
        "amount_long": amt_long,
        "pnl_long": upnl_long,
        "is_in_short": is_in_Short,
        "amount_short": amt_short,
        "pnl_short": upnl_short,
    }"""
    if order_data["action"] == "CloseLong":
        if position_data["is_in_long"]:
            CloseLong(order_data, position_data)
            return "Order Done"
        else:
            return "No Position : Do Nothing"
    elif order_data["action"] == "CloseShort":
        if position_data["is_in_short"]:
            CloseShort(order_data, position_data)
            return "Order Done"
        else:
            return "No Position : Do Nothing"
    elif order_data["action"] == "OpenLong":
        if not order_data["mode"] and position_data["is_in_short"]:
            CloseAllShort(order_data, position_data)
            OpenLong(order_data)
            return "Order Done"
        elif position_data["is_in_long"]:
            return "Already in position : Do Nothing"
        else:
            OpenLong(order_data)
            return "Order Done"
    elif order_data["action"] == "OpenShort":
        if not order_data["mode"] and position_data["is_in_long"]:
            CloseAllLong(order_data, position_data)
            OpenShort(order_data)
            return "Order Done"
        elif position_data["is_in_short"]:
            return "Already in position : Do Nothing"
        else:
            OpenShort(order_data)
            return "Order Done"
    elif order_data["action"] == "test":
        return "test"
    else:
        return "Nothin to do"


async def signal_handle(data) -> str:
    """
    msg = {
    "passphrase": "abcd1234", # any : str
    "exchange": "BITKUB",  # any Binance, OKX, bybit : str
    "symbol": "BTC/USDT",  # any : str
    "order": "OpenLong",  # "Open{Short, Long}", "Close{All, }{Short, Long}",
                         # "TP{Short, Long}", "SL{Short,Long}",
                         # "Tailing{Short, Long}" : str
    "amount": "@0.05",  # any @100, $100, %100 : str
    "leverage": 125,  # any  : int
    "callbackRate": 2.3,  # any if side == Tailing : float
    "activatePrice": 25_100,  # any if side == Tailing : float
    "triggerPrice": 30_000,  # any if side == TP or SL : float
    }
    """
    symbol = data["symbol"]
    if (symbol[len(symbol) - 4 : len(symbol)]) == "PERP":
        symbol = symbol[0 : len(symbol) - 4]
    quote = "BUSD" if symbol.endswith("BUSD") else "USDT"

    await account_balance.update_balance()
    balance = account_balance.fiat_balance
    if float(balance[quote]["free"]) < MIN_BALANCE:
        notify_send("ยอดเงินไม่พอ")
        return "ยอดเงินไม่พอ"

    await currentMode.get_currentmode()
    is_in_hedge_mode = currentMode.dualSidePosition
    position_data = await get_current_position(symbol)
    exchange = await connect_loads()
    actions = check_actions((data["order"] if ORDER_ENABLE else "test"))
    position_amount = check_amount(
        (data["order"] if ORDER_ENABLE else "test"), position_data
    )
    amount = await amount_precision(
        symbol, exchange, data["amount"], position_amount, actions
    )

    order_data = {
        "amount_type": data["amount"][0],
        "amount": amount,
        "symbol": symbol,
        "leverage": int(data["leverage"]),
        "action": (data["order"] if ORDER_ENABLE else "test"),
        "order_side": actions,  # buy or sell
        "mode": is_in_hedge_mode,  # boolean
        "LongSide": "LONG" if is_in_hedge_mode else "BOTH",
        "ShortSide": "SHORT" if is_in_hedge_mode else "BOTH",
        "balance": balance,
    }
    message = await ordering(order_data, position_data, exchange)
    return message
