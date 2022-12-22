import MetaTrader5 as mt5

# Documentação do processo:
'''
0. Criar conta na XP
1. Fazer a requisição do MetaTrader5 na XP (https://portal.xpi.com.br/pages/etd/assinaturas.aspx) [gratuito]
2. Ao conseguir a requisilção do MetaTrader, o login, senha e servidor estarão no email
3. Para criar uma 'nova conta' no mt5 e conseguir usá-lo de fato, devemos:
    a. Clicar em arquivo na esq superior
    b. Abrir uma Conta
    c. Encontre sua Empresa -> digitar o valor do servidor que foi recebido no email -> avançar
    d. Conectar-se a uma conexão existente
    e. Nome de usuario e senha ja coletados anteriormente do email

Obs.: Nao sera possivel usar o algoritmo sem concluir esses passos anteriormente
'''

# Como encriptar os dados via Json -> não é necessário explicar
'''
dictJson = {
    'loginJson' : ##########,
    'passwordJson' : '##########',
    'severJson' : '##########'
}

with open("credentials.json", "w") as f:
    json.dump(dictJson, f)

'''

 
# Tutorial - Comandos Básicos ===============================
# print(mt5.symbols_total())

# # Como coletar os ativos que estão linkados a minha corretora
# symbols = mt5.symbols_get()
# # type(symbols) -> tuple
# for i in range(20):
#     print(str(i+1) + ". " + symbols[i].name)


# # Mapa de calor -> coleta de dados de ativos e mapa de calor da correlação desses ativos
ativos = ['GOAU4', 'WEGE3', 'VVAR3', 'PRIO3', 'MRFG3']

# request tick data
# ticks = mt5.copy_ticks_range(
#     'BOVA11', 
#     datetime(2021, 1, 1), 
#     datetime(2021, 1, 7), 
#     mt5.COPY_TICKS_TRADE
#     )
# ticks = pd.DataFrame(ticks)
# ticks.to_csv('BOVA11_ticks.csv', index = False)

# shut down connection to MetaTrader 5
mt5.shutdown()

