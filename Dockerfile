FROM python:3.9

RUN cd /
RUN git clone https://github.com/HDCodePractice/chstockbot.git
RUN cd chstockbot
WORKDIR /chstockbot
RUN pip install --no-cache-dir -r requirements-dev.txt
CMD [ "python", "./sendxyh.py" ]