import json
from aiokafka import AIOKafkaConsumer
import logging
import asyncio
from .config import KAFKA_SERV, TOPIC2, SMA_REDIS_KEY
from .metrics import received_messages_counter, exception_counter
from .schema import convert_sma
from .redisclient import get_redis
logger = logging.getLogger("uvicorn")
agent = "kafkacons"
consumer: AIOKafkaConsumer | None = None


async def consume(shutdown_event: asyncio.Event):
    global consumer

    consumer = AIOKafkaConsumer(
        TOPIC2,
        bootstrap_servers=KAFKA_SERV
    )
    await consumer.start()
    redis_client = await get_redis()
    logger.info(f"{agent} - Consumer started")
    try:
        while not shutdown_event.is_set():
            if redis_client:
                try:
                    async for msg in consumer:
                        received_messages_counter.labels(agent).inc()
                        msg_dc = msg.value.decode('utf-8')
                        try:
                            a = json.loads(msg_dc)
                            if convert_sma(a):
                                await redis_client.set(SMA_REDIS_KEY, str(a), ex=3600)
                        except Exception as e:
                            exception_counter.labels(type(e).__name__, agent).inc()
                            logger.warning(f"{agent}- {e.args}")
                        logger.info(f"{agent} - Received: {msg_dc}")
                except asyncio.CancelledError as e:
                    exception_counter.labels(type(e).__name__, agent).inc()
                    logger.info(f"{agent} - Consumer task cancelled.")
                    break
            else:
                logger.warning(f"{agent}- Waiting for redis_client.")
                await asyncio.sleep(10)
    finally:
        await consumer.stop()
        logger.info(f"{agent} - Consumer stopped.")

