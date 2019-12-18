FROM python:3.6-slim

ENV PYTHONUNBUFFERED 1

WORKDIR /auth

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY auth auth
COPY manage.py . 
