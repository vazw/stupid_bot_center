from line_notify import LineNotify

SECRET_KEY = "somekey"
ORDER_ENABLE = True
MIN_BALANCE = 50


def notify_send(
    msg: str, sticker: int = None, package: int = None, image_path: str = None
) -> None:
    notify = LineNotify("LINETOKEN")
    if image_path is not None:
        notify.send(msg, image_path=image_path)
    elif sticker is not None:
        notify.send(
            msg,
            sticker_id=sticker,
            package_id=package,
        )
    else:
        notify.send(msg)
