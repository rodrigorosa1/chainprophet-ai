FROM python:3.12-slim

WORKDIR /app

RUN pip install --upgrade pip

COPY ./requirements.txt /app

RUN pip install -r requirements.txt

COPY . /app

EXPOSE 8000