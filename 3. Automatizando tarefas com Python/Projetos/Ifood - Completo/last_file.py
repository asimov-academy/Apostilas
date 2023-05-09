from ifood_class import Isimov
from speech_class import Alicia
import sys
import keyboard
import time
from threading import Thread

def quit_check(ali):
    while True:
        time.sleep(5)
        if ali.quit:
            ali.reproduzir_audio("Encerrando")
            sys.exit()
            break
    
# Bloqueia até a tecla ser pressionada
keyboard.wait('ctrl+shift+r')

# O programa só irá começar depois da ativação da hotkey acima
ali = Alicia()

# Checando encerramento global
t = Thread(target=quit_check, args=(ali,))
t.start()

ifood = Isimov('rodrigovanzelotti@gmail.com')
print('RETORNO ALI:', ali.retorno)
try: ifood.pedido(*ali.retorno)
except Exception as e: print(e)

# checando se o valor final foi concebido
if ifood.valor_final != 0:
    ali.reproduzir_audio(f"Pedido realizado com sucesso, valor final de {ifood.valor_final} reais.")
else:
    ali.reproduzir_audio(f"Não identifiquei um valor final para repassar.")

if ifood.retorno != []:
    ali.reproduzir_audio(ifood.retorno[0])


