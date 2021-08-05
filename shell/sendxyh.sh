#!/bin/bash
rm /data/d_us_txt.zip
/usr/bin/wget -q https://static.stooq.com/db/h/d_us_txt.zip -O /data/d_us_txt.zip
rm -rf /data/data
/usr/bin/unzip -oq /data/d_us_txt.zip -d /data
python3 /chstockbot/sendxyh.py -c /data