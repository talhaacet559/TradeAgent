import logging
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
from .config import MONGO_SERV
from .metrics import exception_counter
from .schema import BtcPrice

agent = "reposervice"
logger = logging.getLogger("uvicorn")


def doc_to_model(doc):
    doc["id"] = doc.pop("_id")
    return doc


client = AsyncIOMotorClient(MONGO_SERV)
db = client.trading_db
btc_price_collection = db.get_collection("btc-prices")
trade_signal_collection = db.get_collection("tradesignal")


def klines_convert(listdata:list):
    try:
        btc = BtcPrice(
            opendate=datetime.fromtimestamp(listdata[0] / 1000),
            closedate=datetime.fromtimestamp(listdata[0] / 1000),
            open=listdata[1],
            high=listdata[2],
            low=listdata[3],
            close=listdata[4]
        )
        return btc.model_dump()
    except Exception as e:
        exception_counter.labels(type(e).__name__, agent)
        logger.error(f"{agent} - Error converting klines-Schema: {e}", exc_info=True)
        return None


