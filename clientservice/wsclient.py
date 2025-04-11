import asyncio
import datetime
import json
import socket
import time
import uuid
import websockets

from .metrics import exception_counter
from .schema import TradeSignal, TradeType
from .kafkaprod import send_message
from .config import WS_URI, RETRY_CONN, RETRY_SLEEP_SEC, SND_TIMEOUT, RCV_TIMEOUT, TOPIC1, SMA_REDIS_KEY
import logging
from .redisclient import get_redis

logger = logging.getLogger('uvicorn')
logger_err = logging.getLogger('uvicorn.error')
agent = "wsclient"

mssg = {
    "method": "SUBSCRIBE",
    "params":
        [
            "btcusdt@aggTrade",
        ],
    "id": 1
}


async def connect(msg, shutdown_event: asyncio.Event):
    uri = f'{WS_URI}'
    count = 0
    redis_client = await get_redis()
    while count < RETRY_CONN and not shutdown_event.is_set():
        try:
            async with websockets.connect(uri) as websocket:
                logger.info(f"{agent}-Connected to server")
                await asyncio.wait_for(websocket.send(json.dumps(msg)), timeout=SND_TIMEOUT)
                count = 0
                while not shutdown_event.is_set():
                    sma_get = await redis_client.get(SMA_REDIS_KEY)
                    if sma_get:
                        sma = json.loads(sma_get.replace("'", '"')).get("sma")
                        try:
                            ts = time.perf_counter_ns()
                            response = await asyncio.wait_for(websocket.recv(), timeout=RCV_TIMEOUT)
                            response_dict = json.loads(response)
                            if "p" in response_dict.keys():
                                price = float(response_dict["p"])
                                decider = (price + float(sma["short"]) / 51) > (price + float(sma["long"]) / 201)
                                tr = time.perf_counter_ns()
                                message = TradeSignal(
                                    uuid=str(uuid.uuid1()),
                                    type=TradeType.BUY.value if decider else TradeType.SELL.value,
                                    price=price,
                                    ts=ts,
                                    tr=tr,
                                    tm=time.perf_counter_ns()
                                )
                                await send_message(TOPIC1, message=str(message.model_dump_json()))
                        except websockets.exceptions.ConnectionClosedError as e:
                            exception_counter.labels(type(e).__name__, agent).inc()
                            logger_err.critical(f"{agent}-Connection closed unexpectedly.")
                            count += 1
                            break
                else:
                    logger.warning(f"{agent}- Waiting for SMA input.")
                    await asyncio.sleep(5)
        except (
            websockets.exceptions.InvalidURI,
            websockets.exceptions.InvalidHandshake,
            socket.gaierror,
            TimeoutError,
            ConnectionRefusedError,
            OSError
        ) as e:
            exception_counter.labels(type(e).__name__, agent).inc()
            count += 1
            logger_err.exception(f"{agent}-Failed to connect to server.")

        if count < RETRY_CONN and not shutdown_event.is_set():
            await asyncio.sleep(RETRY_SLEEP_SEC)
            logger_err.critical(f"{agent}-Retrying after sleep...")
        else:
            logger_err.fatal(f"{agent}-Max retries reached or shutdown triggered.")
            break



if __name__ == "__main__":
    asyncio.run(connect(mssg))
