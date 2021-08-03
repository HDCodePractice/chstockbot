FROM python:latest

RUN apt-get update && apt upgrade -y
RUN cd /
COPY . /chstockbot/
RUN cd chstockbot
WORKDIR /chstockbot
RUN pip install -r requirements-dev.txt
CMD [ "python", "bot.py" ,"-c","/data"]