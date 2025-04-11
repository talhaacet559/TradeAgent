import logging
from pydantic import BaseModel, field_validator
import datetime
from enum import Enum
from typing import List

from .metrics import exception_counter

logger = logging.getLogger("uvicorn")
agent = "schema"


class TradeType(Enum):
    BUY = "BUY"
    SELL = "SELL"


class BtcPrice(BaseModel):
    opendate: datetime.datetime
    closedate: datetime.datetime
    open: float
    high: float
    low: float
    close: float


class TradeSignal(BaseModel):
    uuid: str
    type: str  # Use the TradeType Enum here
    price: float
    ts: float
    tr: float
    tm: float

    # Validate that the type is either BUY or SELL
    @field_validator('type')
    def validate_type(cls, v):
        if v not in TradeType:
            raise ValueError('Invalid trade type. Must be BUY or SELL.')
        return v


class BtcPriceResponse(BaseModel):
    range: str
    signals: List[BtcPrice]


class Sma(BaseModel):
    short: float
    long: float


class SmaMsg(BaseModel):
    time: str
    sma: Sma


def convert_sma(btcmsg: dict[str, str | dict[float]]) -> SmaMsg | None:
    try:
        return SmaMsg(
            time=btcmsg["time"],
            sma=Sma(**btcmsg["sma"])
        )
    except Exception as e:
        exception_counter.labels(type(e).__name__, agent).inc()
        logger.critical(f"{agent}- Error while converting Sma message. {e.args}")
        return None
