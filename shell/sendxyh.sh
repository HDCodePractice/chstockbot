#!/bin/bash
cd /home/pi/trade.config/chstockbot
/usr/bin/wget https://static.stooq.com/db/h/d_us_txt.zip
/usr/bin/unzip -oq d_us_txt.zip
/home/pi/py3/bin/python3 /home/pi/chstockbot/sendxyh.py -c /home/pi/trade.config/chstockbot