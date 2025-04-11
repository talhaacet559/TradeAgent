from contextlib import asynccontextmanager
from fastapi import FastAPI
from starlette.responses import Response
from .wsclient import connect, mssg
import asyncio
import logging.config
from .kafkaprod import start_kafka_producer, producer
from .config import LOGGING_CONFIG
from .kafkacons import consume
from .redisclient import init_redis, close_redis
from .metrics import update_system_metrics, RequestCounterMiddleware
from prometheus_client import generate_latest

logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger("uvicorn.asgi")


@asynccontextmanager
async def lifespan(app: FastAPI):
    shutdown_event = asyncio.Event()
    await init_redis()
    await start_kafka_producer()
    # asyncio.create_task(update_system_metrics(shutdown_event), name="system-metrics")
    asyncio.create_task(consume(shutdown_event), name="kafka-consumer")
    asyncio.create_task(connect(mssg, shutdown_event), name="wsclient")
    yield
    await close_redis()


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


@app.get("/liveness")
async def liveness_probe():
    return {"status": "alive"}


@app.get("/health")
async def health():
    kafka_ok = False
    if producer is not None:
        try:
            kafka_ok = await producer.bootstrap_connected()
        except Exception as e:
            logger.warning(f"Kafka health check failed: {e}")

    status = (
        "ok" if kafka_ok
        else "unavailable"
    )
    wstatus = "running" if any(map(lambda a: "wsclient" == a.get_name(), asyncio.all_tasks())) else "unavailable"

    return {
        "kafka": {
            "status": status
        },
        "wsclient":{
            "status": wstatus
        }
    }


@app.get("/restart")
async def restart():
    ws_tasks = list(filter(lambda x: x.get_name() == "wsclient", asyncio.all_tasks()))
    try:
        ws_task = ws_tasks[0]
    except IndexError:
        ws_task = asyncio.create_task(connect(mssg, asyncio.Event()), name="wsclient")

    status = "running" if not ws_task.done() else "failed"
    return {"status": status}
