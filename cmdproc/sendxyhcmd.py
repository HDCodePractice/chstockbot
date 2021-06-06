from telegram import Update,  BotCommand
from telegram.ext import CommandHandler,  CallbackContext
from numpy import append
import pandas as pd
import pandas_datareader as pdr
import datetime



# symbol = 'aapl'
# df = pdr.get_data_yahoo(symbol.upper(),start=start,end=end)
# print(df)

# 数据结构 High         Low        Open       Close       Volume   Adj Close

start = datetime.date.today() - datetime.timedelta(days=365)
end = datetime.date.today()

symbol = 'qqq'
df_qqq = pdr.get_data_yahoo(symbol.upper(),start=start,end=end)
qqq_today = df_qqq.iat[-1,3]
qqq_today_low = df_qqq.iat[-1,1]
qqq_today_high = df_qqq.iat[-1,0]
qqq_13d = df_qqq.loc[:,["Close"]].tail(13)["Close"].mean()
qqq_50d = df_qqq.loc[:,["Close"]].tail(50)["Close"].mean()
qqq_200d = df_qqq.loc[:,["Close"]].tail(200)["Close"].mean()

qqq_brief = f"""QQQ 今日：{format(qqq_today,'.3f')}({format(qqq_today_low,'.3f')}-{format(qqq_today_high,'.3f')})
13  周期均价：{format(qqq_13d,'.3f')}
50  周期均价：{format(qqq_50d,'.3f')}
200 周期均价：{format(qqq_200d,'.3f')}
"""

symbol = 'spy'
df_spy = pdr.get_data_yahoo(symbol.upper(),start=start,end=end)
spy_today = df_spy.iat[-1,3]
spy_today_low = df_spy.iat[-1,1]
spy_today_high = df_spy.iat[-1,0]
spy_13d = df_spy.loc[:,["Close"]].tail(13)["Close"].mean()
spy_50d = df_spy.loc[:,["Close"]].tail(50)["Close"].mean()
spy_200d = df_spy.loc[:,["Close"]].tail(200)["Close"].mean()

spy_brief = f"""SPY 今日：{format(spy_today,'.3f')}({format(spy_today_low,'.3f')}-{format(spy_today_high,'.3f')})
13  周期均价：{format(spy_13d,'.3f')}
50  周期均价：{format(spy_50d,'.3f')}
200 周期均价：{format(spy_200d,'.3f')}
"""

market_brief = f"""Market TODAY

{spy_brief}
{qqq_brief}
"""

print(market_brief)



# def senxhy_command(update: Update, _: CallbackContext) -> None:
    
# def add_dispatcher(dp):
#     dp.add_handler(CommandHandler("m", sendxhy_command))
#     return []