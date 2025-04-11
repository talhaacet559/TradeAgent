import os

APP = "EntityService"
VERSION = "1.0.0"
AUTHOR = "Omer Talha Acet"
KLINES_URI = os.environ.get("KLINES_URI", "https://api.binance.com/api/v3/klines?symbol=BTCUSDT&interval=1d&limit=200")
MONGO_USR = os.environ.get("MONGO_USR", "admin")
MONGO_PSS = os.environ.get("MONGO_PSS", "admin")
MONGO_DB = os.environ.get("MONGO_DB", "tradata")
MONGO_HOST = os.environ.get("MONGO_HOST", "localhost:27017")
KAFKA_SERV = os.environ.get("KAFKA_SERV","localhost:9092")
TOPIC1 = os.environ.get("TOPIC1","tradesignal")
TOPIC2 = os.environ.get("TOPIC2","btc-prices")
MONGO_SERV = f"mongodb://{MONGO_USR}:{MONGO_PSS}@{MONGO_HOST}/{MONGO_DB}?authSource=admin"
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
