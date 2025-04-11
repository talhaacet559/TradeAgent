import json
import time

from aiokafka import AIOKafkaConsumer
import logging
import asyncio

from .config import KAFKA_SERV, TOPIC1
from .metrics import received_messages_counter, exception_counter, ts_tr_delay_gauge, tr_tm_delay_gauge, \
    tms_tm_delay_gauge
from .reposervice import trade_signal_collection
from .schema import TradeSignal

logger = logging.getLogger("uvicorn")
agent = "kafkacons"
consumer: AIOKafkaConsumer | None = None


async def consume():
    global consumer
    consumer = AIOKafkaConsumer(
        TOPIC1,
        bootstrap_servers=KAFKA_SERV
    )
    await consumer.start()
    logger.info(f"{agent}- Consumer started")
    try:
        async for msg in consumer:
            received_messages_counter.labels(agent).inc()
            msg_dc = msg.value.decode('utf-8')
            try:
                a = json.loads(msg_dc)
                trade_signal_collection.insert_one(TradeSignal(**a).model_dump())
                tms = time.perf_counter_ns()
                ts_tr_delay = (a["tr"] - a["ts"]) / 1_000_000
                tr_tm_delay = (a["tm"] - a["tr"]) / 1_000_000
                tms_tm_delay = (tms - a["tm"]) / 1_000_000
                ts_tr_delay_gauge.labels(agent).set(ts_tr_delay)
                tr_tm_delay_gauge.labels(agent).set(tr_tm_delay)
                tms_tm_delay_gauge.labels(agent).set(tms_tm_delay)
            except Exception as e:
                exception_counter.labels(type(e).__name__, agent)
                print(e.args, e.with_traceback())
            logger.info(f"{agent}-Received: {msg_dc}")
    except asyncio.CancelledError as e:
        exception_counter.labels(type(e).__name__, agent)
        logger.info(f"{agent}-Consumer task cancelled.")
    finally:
        await consumer.stop()
        logger.info(f"{agent}-Consumer stopped.")
