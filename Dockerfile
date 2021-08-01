FROM python:latest

RUN cd /
COPY . /chstockbot/
RUN cd chstockbot
WORKDIR /chstockbot
RUN pip install --no-cache-dir -r requirements-dev.txt
CMD [ "python", "./sendxyh.py" ]