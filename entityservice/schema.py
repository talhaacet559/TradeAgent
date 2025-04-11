import datetime
from typing import List

from pydantic import BaseModel, Field, field_validator
from enum import Enum


class TradeType(Enum):
    BUY = "BUY"
    SELL = "SELL"


class BtcPrice(BaseModel):
    opendate:datetime.datetime
    closedate:datetime.datetime
    open:float
    high:float
    low:float
    close:float


class TradeSignal(BaseModel):
    uuid: str
    type: str
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
    prices: List[BtcPrice]


class TradeSignalResponse(BaseModel):
    range: str
    signals:List[TradeSignal]


class Sma(BaseModel):
    short: float
    long: float


class SmaMsg(BaseModel):
    time: str
    sma: Sma