import pandas as pd
import pandas_datareader as pdr
import datetime

start = datetime.date.today() - datetime.timedelta(days=365)
end = datetime.date.today()

symbol = 'aapl'
df = pdr.get_data_yahoo(symbol.upper(),start=start,end=end)
print(df)