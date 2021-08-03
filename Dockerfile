FROM python:latest

RUN cd /
COPY . /chstockbot/
RUN cd chstockbot
WORKDIR /chstockbot
RUN pip install -r requirements-dev.txt
CMD [ "python", "./sendxyh.py" ,"-c /data"]