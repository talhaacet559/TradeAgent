from contextlib import asynccontextmanager
import logging.config
from starlette.responses import Response
from .config import LOGGING_CONFIG
from .kafkacons import consume
import logging
import asyncio
from .klines import get_klines
from .reposervice import doc_to_model, btc_price_collection, trade_signal_collection
from .schema import BtcPrice, TradeSignal, BtcPriceResponse, TradeSignalResponse
from pymongo import DESCENDING
from fastapi import FastAPI, Query
from .kafkaprod import send_btc_prices, start_kafka_producer
from .metrics import update_system_metrics, RequestCounterMiddleware
from prometheus_client import generate_latest

logger = logging.getLogger("uvicorn.asgi")
logging.config.dictConfig(LOGGING_CONFIG)

consumer_task: asyncio.Task | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global consumer_task
    await start_kafka_producer()
    consumer_task = asyncio.create_task(consume())
    klines_task = asyncio.create_task(get_klines())
    btc_prices_task = asyncio.create_task(send_btc_prices())
    yield
    consumer_task.cancel()
    klines_task.cancel()
    btc_prices_task.cancel()
    try:
        await consumer_task
    except asyncio.CancelledError:
        logger.info("Consumer task fully cleaned up after cancel.")


app = FastAPI(lifespan=lifespan)
app.add_middleware(RequestCounterMiddleware)


@app.get("/metrics")
async def metrics():
    await update_system_metrics()
    return Response(generate_latest(), media_type="text/plain")


@app.get("/")
async def main():
    from .config import APP, VERSION, AUTHOR
    return {
        "app": APP,
        "version": VERSION,
        "author": AUTHOR
    }


@app.get("/btc-price/", response_model=BtcPriceResponse)
async def get_btc_prices(skip: int = Query(0, ge=0), limit: int = Query(200, ge=1, le=200)):
    cursor = (
        btc_price_collection
        .find()
        .sort("opendate", DESCENDING)
        .skip(skip)
        .limit(limit)
    )
    docs = await cursor.to_list(length=limit)
    return {
        "range": f"{skip + 1} - {skip + len(docs)}",
        "prices": [BtcPrice(**doc_to_model(doc)) for doc in docs]
    }


@app.get("/trade-signal/", response_model=TradeSignalResponse)
async def get_trade_signals(skip: int = Query(0, ge=0), limit: int = Query(50, ge=1, le=100)):
    cursor = (trade_signal_collection
              .find()
              .sort("tm", DESCENDING)
              .skip(skip)
              .limit(limit))
    docs = await cursor.to_list(length=limit)
    if len(docs) == 0:
        return []
    return {
        "range": f"{skip + 1} - {limit}",
        "signals": [TradeSignal(**doc_to_model(doc)) for doc in docs]
    }


@app.get("/liveness")
async def liveness_probe():
    return {"status": "alive"}


@app.get("/klines-debug")
async def klines():
    asyncio.create_task(get_klines())
