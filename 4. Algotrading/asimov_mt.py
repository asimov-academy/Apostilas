import MetaTrader5 as mt5
from datetime import datetime, timedelta
import pandas as pd


class AsimovMT:
    def __init__(self):
        if not mt5.initialize():
            print("initialize() failed, error code = ", mt5.last_error())
            mt5.shutdown()  
        
        print("Updating balances, positions and orders.")
        self.positons = [i._asdict() for i in mt5.positions_get()]
        self.orders = [i._asdict() for i in mt5.orders_get()]
        self.h_orders = [i._asdict() for i in mt5.history_orders_get(0, datetime.now())]
        self.h_deals = [i._asdict() for i in mt5.history_deals_get(0, datetime.now())]
        print("MetaTrader5 loaded. Ready to start.")

        self.tf_dict = {                         # o quanto cada timeframe pode representar em dias? Ver estudos na função self.read_ohlc()
            'M1': [mt5.TIMEFRAME_M1, 60],
            'M2': [mt5.TIMEFRAME_M2, 120],
            'M3': [mt5.TIMEFRAME_M3, 180],
            'M4': [mt5.TIMEFRAME_M4, 240],
            'M5': [mt5.TIMEFRAME_M5, 300],
            'M6': [mt5.TIMEFRAME_M6, 360],
            'M10': [mt5.TIMEFRAME_M10, 600],
            'M12': [mt5.TIMEFRAME_M12, 720],
            'M15': [mt5.TIMEFRAME_M15, 900],
            'M20': [mt5.TIMEFRAME_M20, 1200],
            'M30': [mt5.TIMEFRAME_M30, 1800],
            'H1': [mt5.TIMEFRAME_H1, 3600],
            'H2': [mt5.TIMEFRAME_H2, 7200],
            'H3': [mt5.TIMEFRAME_H3, 10800],
            'H4': [mt5.TIMEFRAME_H4, 14400],
            'H6': [mt5.TIMEFRAME_H6, 21600],
            'H8': [mt5.TIMEFRAME_H8, 28800],
            'H12': [mt5.TIMEFRAME_H12, 43200],
            'D1': [mt5.TIMEFRAME_D1, 86400],
            'W1': [mt5.TIMEFRAME_W1, 604800],
            'MN1' : [mt5.TIMEFRAME_MN1, 2592000],
        }


    # Market Data Functions
    def get_ohlc_range(self, symbol, timeframe, start_date, end_date=datetime.now()):
        tf = self.tf_dict[timeframe][0]
        data_raw = mt5.copy_rates_range(symbol, tf, start_date, end_date) 
        if data_raw is not None and len(data_raw) == 0:
            return
        df_data = self._format_ohlc(data_raw)
        return df_data

    def get_ohlc_pos(self, symbol, timeframe, initial_pos, number_of_bars):
        tf = self.tf_dict[timeframe][0]
        data_raw = mt5.copy_rates_from_pos(symbol, tf, initial_pos, number_of_bars)
        df_data = self._format_ohlc(data_raw)
        return df_data

    def _format_ohlc(self, data_raw):
        if data_raw is not None and len(data_raw) == 0:
            return
        df_data = pd.DataFrame(data_raw)
        df_data['time'] = pd.to_datetime(df_data['time'], unit='s')
        df_data.set_index(df_data.time, inplace=True)
        del df_data['time']
        return df_data


    # Positions and balance functions
    def check_positions_and_orders(self):
        new_positons = [i._asdict() for i in mt5.positions_get()]
        new_orders = [i._asdict() for i in mt5.orders_get()]

        check = (self.positons != new_positons) or (self.orders != new_orders)
        self.positons = new_positons
        self.orders = new_orders
        return check
    
    def check_h_positions_and_orders(self, from_date=0, 
                                     to_date=datetime.now()):
        new_h_orders = [i._asdict() for i in mt5.history_orders_get(from_date, to_date)]
        new_h_deals = [i._asdict() for i in mt5.history_deals_get(from_date, to_date)]

        check = (self.h_orders != new_h_orders) or (self.h_deals != new_h_deals)
        self.h_orders = new_h_orders
        self.h_deals = new_h_deals
        return check


    # Order management functions
    def send_market_order(self, symbol, side, volume, 
                          deviation=20, magic=1000, comment='test'):
        mt5.symbol_select(symbol,True)
        symbol_info = mt5.symbol_info(symbol)
        ticks = symbol_info.point

        if side == 'buy':
            price = symbol_info.ask + 5 * ticks 
            side = mt5.ORDER_TYPE_BUY
        elif side == 'sell':
            price = symbol_info.bid - 5 * ticks 
            side = mt5.ORDER_TYPE_SELL  
        
        if symbol_info.visible:
            request = {
                "action": mt5.TRADE_ACTION_DEAL, 
                "symbol": symbol,
                "volume": volume,
                "type": side,
                "price": price,
                "deviation": deviation,
                "magic": magic,
                "comment": comment,
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_RETURN,
            }
            return mt5.order_send(request)
        else:
            print(f"{symbol} not visible. Unable to send market order.")

    def send_limit_order(self, symbol, side, price, volume, 
                         magic=1000, comment=""):
        symbol_info = mt5.symbol_info(symbol)
        tick = symbol_info.point
        mt5.symbol_select(symbol,True)

        if symbol_info.visible:
            mt5.symbol_select(symbol,True)
            request = {
                "action": mt5.TRADE_ACTION_PENDING,
                "symbol": symbol,
                "volume": volume,
                "type": mt5.ORDER_TYPE_BUY_LIMIT if side == 'buy' else mt5.ORDER_TYPE_SELL_LIMIT,
                "price": price,
                "magic": magic,
                "comment": comment,
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_RETURN,
            }
            return mt5.order_send(request)._asdict()
        else:
            print(f"{symbol} not visible. Unable to send market order.")

    def update_limit_order(self, order, price, volume):
        request = {
            "action": mt5.TRADE_ACTION_MODIFY,
            "order": order,
            "volume": volume,
            "price": price,
        }
        return mt5.order_send(request)._asdict()

    def cancel_limit_order(self, order):
        request = {
            "action": mt5.TRADE_ACTION_REMOVE ,
            "order": order,
        }
        return mt5.order_send(request)._asdict()
    
if __name__ == "__main__":
    # Instância
    self = AsimovMT()

    # ============================
    # Testing market data methods
    start_date = datetime.today() - timedelta(days=1)
    df_data = self.get_ohlc_range('PETR4', 'M1', start_date, datetime.today())
    df_data = self.get_ohlc_pos('PETR4', 'M1', 0, 1000)


    # ============================
    # Testing balance methods
    self.check_positions_and_orders()
    self.positons
    self.orders

    self.check_h_positions_and_orders(0)
    self.h_deals
    self.h_orders

    # ============================
    # Testing order methods (LEMBRAR DE ATIVAR ALGOTRADING)

    symbol = 'ITSA4'
    side = 'buy'
    volume = 100.0  # Deve ser float!
    self.send_market_order(symbol, 'buy', volume, comment='test')
    self.send_market_order(symbol, 'sell', volume, comment='test')

    price = 7.80
    self.send_limit_order(symbol, 'buy', price, volume, comment='test')
    price = 8.00
    order = self.send_limit_order(symbol, 'sell', price, volume, comment='test')
    order

    self.update_limit_order(order["order"], 8.01, volume=100.0)
    self.cancel_limit_order(order["order"])



