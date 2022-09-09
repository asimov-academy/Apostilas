import hikari
import lightbulb


bot = lightbulb.BotApp(
    token=open('token.txt', 'r').read(), 
    default_enabled_guilds=(int(open('ds_channel_id.txt', 'r').read())))

@bot.listen(hikari.StartedEvent)
async def on_started(event):
    print('Asimotron ta online!')

#Mensagem de saudação
@bot.command
@lightbulb.command('msg_asmv', 'Saudação Asimov Academy')
@lightbulb.implements(lightbulb.SlashCommand)
async def hello(ctx):
    await ctx.respond('*Olá, comunidade Asimov Academy!*')

#Calculadora
@bot.command
@lightbulb.command('calculadora', 'Calculadora')
@lightbulb.implements(lightbulb.SlashCommandGroup)
async def my_calculator(ctx):
    pass

@my_calculator.child
@lightbulb.option('n2', 'Segundo número', type=float)
@lightbulb.option('n1', 'Primeiro número', type=float)
@lightbulb.command('soma', 'Operação de Adição')
@lightbulb.implements(lightbulb.SlashSubCommand)
async def soma(ctx):
    r = ctx.options.n1 + ctx.options.n2
    await ctx.respond(f"*O resultado é  **{r}***")

@my_calculator.child
@lightbulb.option('n2', 'Segundo número', type=float)
@lightbulb.option('n1', 'Primeiro número', type=float)
@lightbulb.command('subtracao', 'Operação de Subtração')
@lightbulb.implements(lightbulb.SlashSubCommand)
async def subtracao(ctx):
    r = ctx.options.n1 - ctx.options.n2
    await ctx.respond(f"*O resultado é  **{r}***")

@my_calculator.child
@lightbulb.option('n2', 'Segundo número', type=float)
@lightbulb.option('n1', 'Primeiro número', type=float)
@lightbulb.command('multiplicacao', 'Operação de Multiplicação')
@lightbulb.implements(lightbulb.SlashSubCommand)
async def multiplicacao(ctx):
    r = ctx.options.n1 * ctx.options.n2
    await ctx.respond(f"*O resultado é  **{round(r, 1)}***")

@my_calculator.child
@lightbulb.option('n2', 'Segundo número', type=float)
@lightbulb.option('n1', 'Primeiro número', type=float)
@lightbulb.command('divisao', 'Operação de Divisão')
@lightbulb.implements(lightbulb.SlashSubCommand)
async def divisao(ctx):
    r = ctx.options.n1 / ctx.options.n2
    await ctx.respond(f"*O resultado é  **{round(r, 1)}***")


#Temperatura
import requests
import string

BASE_URL = "https://api.openweathermap.org/data/2.5/weather?"
API_KEY = open('api_weather_key.txt', 'r').read()

def kelvin_to_celsius(kelvin):
    celsius = kelvin - 273.15
    return celsius

@bot.command
@lightbulb.option('pais', 'País', type=str)
@lightbulb.option('cidade', 'Cidade', type=str)
@lightbulb.command('temperatura', 'Informe uma cidade seu país para saber a temperatura atual')
@lightbulb.implements(lightbulb.SlashCommand)

async def temperatura(ctx):
    country = ctx.options.pais
    CITY = string.capwords(ctx.options.cidade) + "," + country[0:2].lower()

    url = BASE_URL + "q=" + CITY + "&APPID=" + API_KEY 
    response = requests.get(url).json()

    temp_kelvin = response['main']['temp']
    umidade = response['main']['humidity']
    vento = response['wind']['speed']

    temp_celsius = str(round(kelvin_to_celsius(temp_kelvin)))

    await ctx.respond(f"```A temperatura atual em {string.capwords(ctx.options.cidade)} é de {temp_celsius} ºC \numidade do ar: {umidade}% \nvento: {vento} m/s```")

#Piadas
import random

p1 = "O que o pato disse para a pata \nR.: Vem Quá!"
p2 = "Porque o menino estava falando ao telefone deitado? \nR.: Para não cair a ligação."
p3 = "Qual é a fórmula da água benta? \nR.: H Deus O!"
p4 = "Qual é a cidade brasileira que não tem táxi? \nR.: Uberlândia"
p5 = "Qual é a fruta que anda de trem? \nR.: O kiwiiiii."
p6 = "O que é um pontinho preto no avião? \nR.: Uma aeromosca."
p7 = "Como o Batman faz para entrar na Bat-caverna? \nR.: Ele bat-palma."
p8 = "Por que o pão não entende a batata? \nR.: Porque o pão é francês e a batata é inglesa"
p9 = "O que o zero disse para o oito? \nR.: Belo cinto!"
p10 = "Por que os elétrons nunca são convidados para festas? \nR.: Porque eles são muito negativos."

piadas=[p1, p2, p3, p4, p5, p6, p7, p8, p9, p10]

@bot.command
@lightbulb.command('piada', 'Receba uma piada')
@lightbulb.implements(lightbulb.SlashCommand)

async def joke(ctx):
    n = random.randint(1,10)
    await ctx.respond(f"*{piadas[n]}*")


#Analytics
import numpy as np
import pandas as pd
from google.oauth2 import service_account
from googleapiclient.discovery import build
import time

view_id = open('id_ga.txt', 'r').read()
ga_key = 'google_analytics_api_infos.json'


def format_summary(response):
    try:
        try: 
            row_index_names = response['reports'][0]['columnHeader']['dimensions']
            row_index = [ element['dimensions'] for element in response['reports'][0]['data']['rows'] ]
            row_index_named = pd.MultiIndex.from_arrays(np.transpose(np.array(row_index)), 
                                                        names = np.array(row_index_names))
        except:
            row_index_named = None
        
        summary_column_names = [item['name'] for item in response['reports'][0]
                                ['columnHeader']['metricHeader']['metricHeaderEntries']]
    
        summary_values = [element['metrics'][0]['values'] for element in response['reports'][0]['data']['rows']]
    
        df = pd.DataFrame(data = np.array(summary_values), 
                        index = row_index_named, 
                        columns = summary_column_names).astype('float')
    
    except:
        df = pd.DataFrame()
        
    return df

def format_pivot(response):
    try:
        pivot_values = [item['metrics'][0]['pivotValueRegions'][0]['values'] for item in response['reports'][0]
                        ['data']['rows']]
        
        top_header = [item['dimensionValues'] for item in response['reports'][0]
                    ['columnHeader']['metricHeader']['pivotHeaders'][0]['pivotHeaderEntries']]
        column_metrics = [item['metric']['name'] for item in response['reports'][0]
                        ['columnHeader']['metricHeader']['pivotHeaders'][0]['pivotHeaderEntries']]
        array = np.concatenate((np.array(top_header),
                                np.array(column_metrics).reshape((len(column_metrics),1))), 
                            axis = 1)
        column_index = pd.MultiIndex.from_arrays(np.transpose(array))
        
        try:
            row_index_names = response['reports'][0]['columnHeader']['dimensions']
            row_index = [ element['dimensions'] for element in response['reports'][0]['data']['rows'] ]
            row_index_named = pd.MultiIndex.from_arrays(np.transpose(np.array(row_index)), 
                                                        names = np.array(row_index_names))
        except: 
            row_index_named = None
        df = pd.DataFrame(data = np.array(pivot_values), 
                        index = row_index_named, 
                        columns = column_index).astype('float')
    except:
        df = pd.DataFrame()
    return df

def format_report(response):

    summary = format_summary(response)
    pivot = format_pivot(response)
    if pivot.columns.nlevels == 2:
        summary.columns = [['']*len(summary.columns), summary.columns]
    
    return(pd.concat([summary, pivot], axis = 1))

def run_report(body, credentials_file):

    credentials = service_account.Credentials.from_service_account_file(credentials_file, 
                                scopes = ['https://www.googleapis.com/auth/analytics.readonly'])

    service = build('analyticsreporting', 'v4', credentials=credentials)


    response = service.reports().batchGet(body=body).execute()

    return(format_report(response))

@bot.command
@lightbulb.command('analytics', 'Informações Asimov do Google Analytics')
@lightbulb.implements(lightbulb.SlashCommandGroup)
async def analytics(ctx):
    pass

@analytics.child
@lightbulb.option('data_final', 'data final - insira a data no formato yyyy-mm-dd', type=str)
@lightbulb.option('data_inicial', 'data inicial - insira a data no formato yyyy-mm-dd', type=str)
@lightbulb.command('relatory', 'Relatório da data')
@lightbulb.implements(lightbulb.SlashSubCommand)
async def relatory(ctx):

    df_structure = {  "reportRequests":[{"viewId": view_id,
    "dateRanges": [{'startDate': f'{ctx.options.data_inicial}', 'endDate': f'{ctx.options.data_final}'}],
    "metrics": [{"expression": "ga:users"},
            {"expression": "ga:newUsers"},
            {"expression": "ga:timeOnPage"},
            {"expression": "ga:sessions"},
            {"expression": "ga:pageviews"}],
    'dimensions': [{'name': 'ga:country'}]
    }]}


    ga_report = run_report(df_structure, ga_key)
    ga_report.sort_values(by='ga:users', ascending=False, inplace=True)
    ga_report.reset_index(inplace=True)

    active_users = ga_report.sum()[1]
    new_users = ga_report.sum()[2]
    sessions = ga_report.sum()[4]
    page_views = ga_report.sum()[5]
    session_time_average =  time.strftime("%M:%S", time.gmtime(ga_report.sum()[3]/ga_report.sum()[4]))

    pais_1 = ga_report.iloc[0][0]
    pais_2 = ga_report.iloc[1][0]
    pais_3 = ga_report.iloc[2][0]
    acesso_pais_1 = ga_report.iloc[0][1]
    acesso_pais_2 = ga_report.iloc[1][1]
    acesso_pais_3 = ga_report.iloc[2][1]
    acesso_pais_1_porcentagem = ga_report.iloc[0][1]/ga_report.sum()[1]*100
    acesso_pais_2_porcentagem = ga_report.iloc[1][1]/ga_report.sum()[1]*100
    acesso_pais_3_porcentagem = ga_report.iloc[2][1]/ga_report.sum()[1]*100

    data_inicial = ctx.options.data_inicial
    data_final = ctx.options.data_final
    data_inicial_formatada = data_inicial[8:11] + '/' + data_inicial[5:7] + '/' + data_inicial[:4]
    data_final_formatada = data_final[8:11] + '/' + data_final[5:7] + '/' + data_final[:4]


    await ctx.respond(f" **------------------------ Relatório Asimov Academy {data_inicial_formatada} a {data_final_formatada} ------------------------**\
        \n\n- Usuários que acessaram a plataforma: **{round(active_users)}** \n- Usuários que acessaram pela 1ª vez: **{round(new_users)}**\
        \n- Número total de acessos à plataforma: **{round(sessions)}** \n- Tempo médio que cada usuário ficou na plataforma: **{session_time_average} minutos**\
        \n- Número total de páginas visualizadas no site: **{round(page_views)}** \n\n*Maiores acessos*:\
        \n- {pais_1}: {round(acesso_pais_1)} acessos (**{round(acesso_pais_1_porcentagem, 2)}%**)\
        \n- {pais_2}: {round(acesso_pais_2)} acessos (**{round(acesso_pais_2_porcentagem, 2)}%**)\
        \n- {pais_3}: {round(acesso_pais_3)} acessos (**{round(acesso_pais_3_porcentagem, 2)}%**)")

bot.run()