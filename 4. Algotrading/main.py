import MetaTrader5 as mt5
import json
import os
import pandas as pd
from datetime import datetime


login, password = open('credentials').read().split()
server='demo.mt5.xpi.com.br:443'

if not mt5.initialize(login=int(login), password=password, server=server):
    print("initialize() failed, error code = ", mt5.last_error())
    mt5.shutdown()

# Seleciona símbolo no MarketWatch
mt5.symbol_select("BBDC3",True)

# Obtem deals
from_date = datetime(2020,1,1)
to_date = datetime.now()
group_search = "*,!*EUR*,!*GBP*"
deals = mt5.history_deals_get(from_date, to_date, group=group_search)
positons = mt5.positions_get()  # Posições abertas
orders = mt5.orders_get()  # Ordens abertas
 
# Obtem ordens
from_date = datetime(2020,1,1)
to_date = datetime.now()
group_search = "**"
history_orders = mt5.history_orders_get(from_date, to_date, group=group_search)
history_orders[0]

# Todas as funções aqui retornaram um inteiro
mt5.orders_total()                              # Total de ordens
mt5.positions_total()                           # Total de posições abertas
mt5.history_orders_total(from_date, to_date)    # Total de ordens no histórico de negociação
mt5.history_deals_total(from_date, to_date)     # Total de transações no histórico de negociação (deals)


# ======= Sending Orders ==========
# Checking and sending orders
symbol = 'ITSA4'
symbol_info = mt5.symbol_info(symbol)
symbol_info.visible
mt5.symbol_select(symbol,True)

bid = symbol_info.bid
ask = symbol_info.ask
tick = mt5.symbol_info(symbol).point
volume = 100.0
deviation = 20

# Market Order
request = {
    "action": mt5.TRADE_ACTION_DEAL, #TRADE_ACTION_DEAL, TRADE_ACTION_PENDING
    "symbol": symbol,
    "volume": volume,
    "type": mt5.ORDER_TYPE_BUY,
    "price": bid - 10 * tick,
    "sl": bid - 100 * tick,
    "tp": bid + 100 * tick,
    "deviation": deviation,
    "magic": 234000,
    "comment": "python script open",
    "type_time": mt5.ORDER_TIME_GTC,
    "type_filling": mt5.ORDER_FILLING_RETURN,
}
result = mt5.order_check(request)
result = mt5.order_send(request)


# Pending Order
request = {
    "action": mt5.TRADE_ACTION_PENDING, #TRADE_ACTION_DEAL, TRADE_ACTION_PENDING
    "symbol": symbol,
    "volume": volume,
    "type": mt5.ORDER_TYPE_BUY_LIMIT,
    "price": bid - 10 * tick,
    # "sl": bid - 100 * tick,
    # "tp": bid + 100 * tick,
    "deviation": deviation,
    "magic": 234000,
    "comment": "python script open",
    "type_time": mt5.ORDER_TIME_GTC,
    "type_filling": mt5.ORDER_FILLING_RETURN,
}
result = mt5.order_send(request)._asdict()

# Modify Pending Order
request["action"] = mt5.TRADE_ACTION_MODIFY
request["order"] = 1513437484
request["price"] = bid - 20 * tick
result = mt5.order_send(request)._asdict()


# Cancelling Pending Order
request["action"] = mt5.TRADE_ACTION_REMOVE 
request["order"] = 1513437484
result = mt5.order_send(request)._asdict()