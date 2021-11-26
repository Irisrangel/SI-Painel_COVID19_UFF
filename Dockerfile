FROM python:3.8

RUN mkdir /app

COPY requirements.txt /app

WORKDIR /app

RUN pip install --upgrade pip
RUN pip3 install -r requirements.txt