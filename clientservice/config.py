import os

APP = "WsClient"
VERSION = "1.0.0"
AUTHOR = "Omer Talha Acet"
WS_URI = os.environ.get("WS_URI","wss://stream.testnet.binance.vision/ws")
KAFKA_SERV = os.environ.get("KAFKA_SERV","localhost:9092")
TOPIC1 = os.environ.get("TOPIC1","tradesignal")
TOPIC2 = os.environ.get("TOPIC2","btc-prices")
SMA_REDIS_KEY = "sma_redis"
REDIS_HOST = os.environ.get("REDIS_HOST", "localhost")
REDIS_PORT = os.environ.get("REDIS_PORT", 6379)
RCV_TIMEOUT = 10
SND_TIMEOUT = 5
RETRY_CONN = 5
RETRY_SLEEP_SEC = 3
LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': f'%(asctime)s [{APP}] [%(levelname)s] %(name)s: %(message)s'
        },
        'custom_formatter': {
            'format': f"%(asctime)s [{APP}] [%(processName)s: %(process)d] [%(threadName)s: %(thread)d] [%(levelname)s] %(name)s: %(message)s"

        },
    },
    'handlers': {
        'default': {
            'formatter': 'standard',
            'class': 'logging.StreamHandler',
            'stream': 'ext://sys.stdout',  # Default is stderr
        },
        'stream_handler': {
            'formatter': 'custom_formatter',
            'class': 'logging.StreamHandler',
            'stream': 'ext://sys.stdout',  # Default is stderr
        },
        'file_handler': {
            'formatter': 'custom_formatter',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'app.log',
            'maxBytes': 1024 * 1024 * 1,  #1MB
            'backupCount': 3,
        },
    },
    'loggers': {
        'uvicorn': {
            'handlers': ['default', 'file_handler'],
            'level': 'INFO',
            'propagate': False
        },
        'uvicorn.access': {
            'handlers': ['stream_handler', 'file_handler'],
            'level': 'TRACE',
            'propagate': False
        },
        'uvicorn.error': {
            'handlers': ['stream_handler', 'file_handler'],
            'level': 'TRACE',
            'propagate': False
        },
        'uvicorn.asgi': {
            'handlers': ['stream_handler', 'file_handler'],
            'level': 'TRACE',
            'propagate': False
        },

    },
}
