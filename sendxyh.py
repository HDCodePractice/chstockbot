import pandas as pd
import pandas_datareader.data as web
import datetime

start = datetime.date.today() - datetime.timedelta(days=365)
end = datetime.date.today()

symbol = '^spx'
df = web.DataReader(symbol.upper(), 'stooq',start=start,end=end)
print(df)