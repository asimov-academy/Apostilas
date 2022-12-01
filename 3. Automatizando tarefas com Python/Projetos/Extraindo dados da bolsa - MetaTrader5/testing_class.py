from metatrader_class import AsimoTrader
from datetime import date, datetime
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

file_path = 'C:\\Users\\rodri\\OneDrive\\Área de Trabalho\\credentials.json'
trader = AsimoTrader(file_path=file_path)
# trader.update_ohlc(symbol='AGRO3', timeframe='TIMEFRAME_M1')
# df = trader.read_ohlc(symbol='AGRO3', timeframe='TIMEFRAME_M1', initial_date=datetime(2019, 1, 1))
# print(df.head())

# fig = px.line(df, x=df['time'], y=df['close'])
# fig.update_xaxes(dtick="M8", tickformat="%b/%Y")
# fig.show()

# fig = go.Figure(data=[go.Candlestick(x=df['time'],
#                 open=df['open'],
#                 high=df['high'],
#                 low=df['low'],
#                 close=df['close'])])
# fig.update_xaxes(dtick="M8", tickformat="%b/%Y")
# fig.show()
# # or
# fig.write_html('first_figure.html', auto_open=True)

trader.update_ticks(symbol='AGRO3')
df = trader.read_ticks(symbol='AGRO3')
print(df.head())
print(df.shape)