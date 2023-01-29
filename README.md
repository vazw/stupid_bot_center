# stupid_bot_center
Multi-exchange center module from Stupid Bot community group

## sample payload
```python
msg = {
    "exchange": "BITKUB",  # any Binance, OKX, bybit : str
    "symbol": "BTC/USDT",  # any : str
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
```
## params ของ order ที่จะรับได้
- exchange
> Binance <br/>
> comming...soon<br/>
- symbol
> ใช้รูปแบบตาม exchange นั้น ๆ (แนะนำแบบ settle ของ ท่าน @app)
- order
> OpenLong > เปิด Long Position โดยราคา market<br/>
> CloseLong > ปิด Long Position โดยราคา market<br/>
> TPLong<br/>
> SLLong<br/>
> TailingLong<br/>
> CloseAllLong<br/>
> OpenShort<br/>
> CloseShort<br/>
> TPShort<br/>
> SLShort<br/>
> TailingShort<br/>
> CloseAllShort<br/>
- amount
> @ = จำนวนเหรียญ/หุ้น<br/>
> $ = จำนวนเงิน fiat<br/>
> % = %ของ Position นั้น ๆ (สำหรับ order close หรือ tp เท่านั้น sl ให้ใช้ %100)<br/>
- leverage 
> ใช้ตามความเหมาะสม interger (1-125)
- callbackRate และ activatePrice
> สำหรับส่งพร้อม TailingOrder
- triggerPrice
> ส่งพร้อม TP หรือ SL เท่านัั้น
