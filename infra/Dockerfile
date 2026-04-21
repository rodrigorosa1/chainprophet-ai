FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip

COPY requirements.txt .

RUN python -m pip install --upgrade pip setuptools wheel && \
    python -m pip install --no-cache-dir --timeout 120 --retries 10 -r requirements.txt

COPY . .

EXPOSE 8000