import asimov_mt
from datetime import datetime, timedelta
import os
import threading
from time import time, sleep

# ===================
# Strategy Parameters
roll_window = 10
boll_size = 2
symbol = "PETR4"
bet_size = 100

# ===================
# Strategy functions
# Instanciando a classe do MetaTrader
am = asimov_mt.AsimovMT()  

# Classe de evento, responsável por controlar andamento da estratégia
status = threading.Event()
status.set()

# def rsi_model():
#     while status.is_set():
#         print("1")
#         sleep(1)
#     print("ending")

def rsi_model():
    print("Iniciando estratégia.")
    print(f"Parâmetros: roll_window: {roll_window} | boll_size: {boll_size} | symbol: {symbol}")
    close = 0
    down_band = 0
    up_band = 0

    while status.is_set():
        # Gathering data
        df_data = am.get_ohlc_pos(symbol, "M1", 0, roll_window + 10)

        # Indicator calculation
        df_data["roll_mean"] = df_data["close"].rolling(roll_window).mean()
        df_data["roll_vol_mean"] = df_data["real_volume"].rolling(roll_window).mean()
        df_data["roll_std"] = df_data["close"].rolling(roll_window).std()
        
        df_data["up_band"] = df_data["roll_mean"] + boll_size * df_data["roll_std"]
        df_data["down_band"] = df_data["roll_mean"] - boll_size * df_data["roll_std"]
        df_data["under_mean_vol"] = df_data["real_volume"] > df_data["roll_vol_mean"]

        # Printing data
        if df_data["close"].iloc[-2] != close or down_band != df_data["down_band"].iloc[-2] or df_data["up_band"].iloc[-2] != up_band:
            close = df_data["close"].iloc[-2]
            down_band = df_data["down_band"].iloc[-2]
            up_band = df_data["up_band"].iloc[-2]
            position = am.positons
            print(f"{datetime.now()} - Last close: {close} | Up: {up_band:.2f} Down: {down_band:.2f} | Position: {position}")

        # Checking position and trading
        am.check_positions_and_orders()
        if len(am.positons) == 0:
            c1 = close < down_band
            c2 = df_data["roll_vol_mean"].iloc[-2] > df_data["under_mean_vol"].iloc[-2]
            if c1 and c2:
                # Opening position
                print("Opening position")
                am.send_market_order(symbol, 'buy', bet_size, comment='Open position')
        else:
            if close > up_band:
                # Closing position
                print("Closing position")
                am.send_market_order(symbol, 'sell', bet_size, comment='Closing position')
        sleep(1)

    # Fechando estratégia a força
    if len(am.positons) > 0:
        print("Fechando posição devido ao encerramento da estratégia.")
        am.send_market_order(symbol, 'sell', bet_size, comment='Closing position')
    print("Strategy done.")


# ===================
# Main Loop
while True:
    os.system("cls")
    print("===========================")
    print("Bem vindo ao Asimov Trader.")
    print("Digite o comando desejado:")
    print("0: Sair")
    print("1: Iniciar estratégia")
    print("2: Parar estratégia")
    print("===========================")

    comm = int(input())
    if comm == 0:
        break

    elif comm == 1:
        t1 = threading.Thread(target=rsi_model)
        t1.start()

    elif comm == 2:
        status.clear()
