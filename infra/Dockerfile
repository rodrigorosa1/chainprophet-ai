FROM python:3.12-slim

WORKDIR /app

RUN pip install --upgrade pip

COPY ./requirements.txt /app

RUN python -m pip install --upgrade pip setuptools wheel && \
    python -m pip install --no-cache-dir --timeout 120 --retries 10 -r requirements.txt
COPY . /app

EXPOSE 8000