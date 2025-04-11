import datetime
import logging
from .schema import BtcPrice
from typing import List
from .schema import Sma, SmaMsg
agent = "algo"
logger = logging.getLogger("uvicorn")


def handle_price_msg(msg: List[BtcPrice]):
    # Filter and compute the mid-point price (average of high and low) for valid dates
    long = [
        (a.high + a.low) / 2  # Access properties directly instead of a["high"]
        for a in msg
        if a.opendate.date() < datetime.datetime.now().date()  # Access opendate as a property
    ]

    # Use the 51st value (index 50) as short SMA basis, if it exists
    short = long[50]

    return SmaMsg(
        time=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        sma=Sma(
            short=short,
            long=sum(long) / len(long)
        )
    )

