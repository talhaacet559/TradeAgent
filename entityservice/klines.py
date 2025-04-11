import datetime
import json
from datetime import timedelta
import asyncio
import aiohttp
import ast

from .metrics import exception_counter
from .reposervice import klines_convert, btc_price_collection
from .config import KLINES_URI
from .reposervice import btc_price_collection
from pymongo import DESCENDING
import logging

logger = logging.getLogger('uvicorn')
agent = "klines"

"""
Klines data structure.
[
  [
    1499040000000,      // Kline open time
    "0.01634790",       // Open price
    "0.80000000",       // High price
    "0.01575800",       // Low price
    "0.01577100",       // Close price
    "148976.11427815",  // Volume
    1499644799999,      // Kline Close time
    "2434.19055334",    // Quote asset volume
    308,                // Number of trades
    "1756.87402397",    // Taker buy base asset volume
    "28.46694368",      // Taker buy quote asset volume
    "0"                 // Unused field, ignore.
  ]
]
"""


async def get_klines():
    logger.info(f"{agent} - is initiated.")
    async with aiohttp.ClientSession() as session:
        while True:
            yesterday = datetime.datetime.now().date() - timedelta(days=1)
            yesterday_dt = datetime.datetime.combine(yesterday, datetime.time.min)
            api_uri = KLINES_URI + f"&endTime={int(yesterday_dt.timestamp() * 1000)}"
            try:
                latest_doc = await asyncio.wait_for(
                    btc_price_collection.find_one(sort=[("opendate", DESCENDING)]),
                    timeout=2  # seconds
                )
            except asyncio.TimeoutError:
                latest_doc = None
            logger.debug(f"{agent} latest_doc: {latest_doc}")

            if latest_doc and "opendate" in latest_doc:
                opendate = latest_doc["opendate"].date()
                if opendate < yesterday:
                    start_time = int((opendate + timedelta(days=1)).timestamp() * 1000)
                    api_uri += f"&startTime={start_time}"
                else:
                    logger.info(f"{agent} - Up to latest, sleeping 30 sec.")
                    await asyncio.sleep(30)
                    continue

            try:
                async with session.get(api_uri) as response:
                    if response.status != 200:
                        logger.warning(f"{agent} - API returned {response.status} with {api_uri}")
                        await asyncio.sleep(30)
                        continue
                    print("b")
                    logger.info(f"{agent}- Waiting for html response.")
                    html = await response.text()
                    raw_data = ast.literal_eval(html)
                    data = [d for d in map(klines_convert, raw_data) if d]
                    logger.debug(f"{agent} - data: {data}")
                    if data:
                        await btc_price_collection.insert_many(data)
                        logger.info(f"{agent} - new data inserted")
                    else:
                        logger.info(f"{agent} - no new data received")
                        await asyncio.sleep(15)
                        continue


            except Exception as e:
                exception_counter.labels(type(e).__name__, agent)
                logger.error(f"{agent} - Error fetching or inserting klines: {e}", exc_info=True)
                await asyncio.sleep(15)
                continue

            await asyncio.sleep(5)