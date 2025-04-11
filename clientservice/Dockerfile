
FROM python:3.12-slim


RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    libffi-dev \
    libssl-dev \
    python3-dev \
    netcat-openbsd \
    bash \
 && rm -rf /var/lib/apt/lists/*

COPY . ./app
COPY wait-for-it.sh /wait-for-it.sh
RUN chmod +x /wait-for-it.sh
RUN python -m venv /app/venv

RUN /app/venv/bin/pip install --upgrade pip \
    && /app/venv/bin/pip install -r /app/requirements.txt


CMD /wait-for-it.sh kafka:29092 -- /wait-for-it.sh cache:6379 -- /wait-for-it.sh mongo:27017 -- /app/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000