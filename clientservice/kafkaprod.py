from aiokafka import AIOKafkaProducer
import logging
from .config import KAFKA_SERV
from .metrics import sent_messages_counter, exception_counter

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
        exception_counter.labels("ProducerNone", agent).inc()
        raise Exception(f"{agent}-Kafka producer is not initialized")

    await producer.send_and_wait(topic, message.encode('utf-8'))
    sent_messages_counter.labels(agent).inc()
    logger.info(f"{agent}-Message sent with {topic}: {message}")
