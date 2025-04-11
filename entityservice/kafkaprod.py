from aiokafka import AIOKafkaProducer
import logging
from pymongo import DESCENDING
import asyncio
from .algo import handle_price_msg
from .config import KAFKA_SERV, TOPIC2
from .metrics import exception_counter, sent_messages_counter
from .reposervice import btc_price_collection, doc_to_model
from .schema import BtcPrice

agent = "kafkaprod"
logger = logging.getLogger("uvicorn")
producer: AIOKafkaProducer | None = None


async def start_kafka_producer():
    global producer
    producer = AIOKafkaProducer(bootstrap_servers=KAFKA_SERV)
    await producer.start()
    logger.info(f"{agent}-Kafka producer started")


async def stop_kafka_producer():
    global producer
    if producer:
        await producer.stop()
        logger.info(f"{agent}-Kafka producer stopped")


async def send_message(topic: str, message: str):
    if not producer:
        raise Exception(f"{agent}-Kafka producer is not initialized")
    await producer.send_and_wait(topic, message.encode('utf-8'))
    logger.info(f"{agent}-Message sent with {topic}: {message}")


async def send_btc_prices():
    while True:
        try:
            cursor = (
                btc_price_collection
                .find()
                .sort("opendate", DESCENDING)
                .limit(200)
            )
            docs = await cursor.to_list(length=200)
            if len(docs) < 50:
                logger.warning(f"{agent}- Waiting for klines.")
                continue
            docs_strp = [BtcPrice(**doc_to_model(doc)) for doc in docs]
            sma_result = handle_price_msg(docs_strp).json()
            await send_message(TOPIC2, str(sma_result))
            sent_messages_counter.labels(agent).inc()

        except Exception as e:
            exception_counter.labels(type(e).__name__, agent)
            logger.error(f"{agent} - Error while trying to fetch/send BTC prices: {e.args}")
        finally:
            logger.info(f"{agent} - Completed one cycle.")
            await asyncio.sleep(30)




