from prometheus_client import Counter, Gauge
import psutil
from starlette.middleware.base import BaseHTTPMiddleware

request_counter = Counter(
    "http_requests_total",
    "Total number of HTTP requests",
    ["method", "status_code", "endpoint"]
)

cpu_usage_percent = Gauge("system_cpu_usage_percent", "System CPU usage percentage")
memory_usage_percent = Gauge("system_memory_usage_percent", "System memory usage percentage")
memory_used_mb = Gauge("system_memory_used_mb", "System memory used in megabytes")
memory_total_mb = Gauge("system_memory_total_mb", "Total system memory in megabytes")
ts_tr_delay_gauge = Gauge("ts_tr_delay", "Delay between sent time and received time (in ms) in clientservice WS", ["agent"])
tr_tm_delay_gauge = Gauge("tr_tm_delay", "Delay between received time and messaged time (in ms) in clientservice", ["agent"])
tms_tm_delay_gauge = Gauge("tms_tm_delay", "Delay between received in entity service and messaged time from clientservice (in ms)", ["agent"])

sent_messages_counter = Counter(
    "sent_messages_total",
    "Total number of messages sent",
    ["destination"]
)

received_messages_counter = Counter(
    "received_messages_total",
    "Total number of messages received",
    ["source"]
)

exception_counter = Counter(
    "app_exceptions_total",
    "Total number of exceptions raised",
    ["exception_type", "location"]
)


async def update_system_metrics():
    cpu = psutil.cpu_percent(interval=None)
    mem = psutil.virtual_memory()

    cpu_usage_percent.set(cpu)
    memory_usage_percent.set(mem.percent)
    memory_used_mb.set(mem.used / (1024 * 1024))
    memory_total_mb.set(mem.total / (1024 * 1024))


class RequestCounterMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)

        # Increment the request counter with method, status code, and endpoint
        request_counter.labels(
            method=request.method,
            status_code=str(response.status_code),
            endpoint=str(request.url.path)  # Track the endpoint (path)
        ).inc()

        return response
