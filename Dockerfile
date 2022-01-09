FROM python:3-alpine

WORKDIR /usr/src/app

COPY . ./
RUN pip install -r requirements.txt
CMD python -m apexbot.main

