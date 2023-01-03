import dash
from dash import html, dcc, callback_context
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
import pandas as pd

import plotly.express as px
import plotly.graph_objects as go

from dash import dash_table
from dash.dash_table.Format import Group

from app import app
from components import modal_novo_processo, modal_novo_advogado, modal_advogados
from sql_beta import df_adv, df_proc


# ========= Styles ========= #
card_style={'height': '100%',  'margin-bottom': '12px'}


# Funções para gerar os Cards =======================
# Checar o DataFrame e gerar os icones
def gerar_icones(df_proc_aux, i):
    df_aux = df_proc_aux.iloc[i]
    if df_aux['Processo Concluído'] == 'Sim' and df_aux['Processo Vencido'] == 'Sim':
        concluido = vencido = 'fa fa-check'
        color_c = color_v = 'green'
        concluido_text = 'Concluído'
        vencido_text = 'Vencido'
    elif df_aux['Processo Concluído'] == 'Sim' and df_aux['Processo Vencido'] == 'Não':
        concluido = 'fa fa-check'
        vencido = 'fa fa-times'
        color_c = 'green'
        color_v = 'red'
        concluido_text = 'Concluído'
        vencido_text = 'Perdido'
    elif df_aux['Processo Concluído'] == 'Não':
        concluido = vencido = 'fa fa-times'
        color_c = 'red'
        color_v = 'grey'
        concluido_text = 'Andamento'
        vencido_text = 'Andamento'
    
    return df_aux, concluido, vencido, color_c, color_v, concluido_text, vencido_text

# Card padrão de contagem
def gerar_card_padrao(qnt_procs):
    card_padrao = dbc.Card([
        dbc.CardBody([
            html.H3(f"{qnt_procs} PROCESSOS ENCONTRADOS", style={'font-weight': 'bold', 'color': 'white'})
        ])
    ], style={'height': '100%', 'margin-bottom': '12px', 'background-color': '#646464'})
    return card_padrao

# Card qualquer de processo
def gerar_card_processo(df_aux, color_c, color_v, concluido, vencido, concluido_text, vencido_text):
    card_processo = dbc.Card([
        dbc.CardBody([
            dbc.Row([
                dbc.Col([
                    dbc.Row([
                        dbc.Col([  
                            html.H2(f"Processo nº {df_aux['No Processo']}")
                        ])
                    ]),
                    dbc.Row([
                        dbc.Col([  
                            html.P("Processo corre em segredo de justiça por questões similares.", style={'text-align': 'left'})
                        ])
                    ]),
                    dbc.Row([
                        dbc.Col([
                            html.Ul([
                                html.Li([html.B("DATA: ", style={'font-weight': 'bold'}), f"{df_aux['Data Inicial']} - {df_aux['Data Final']}"]),
                                html.Li([html.B("AÇÃO: ", style={'font-weight': 'bold'}), f"{df_aux['Ação']}"]),
                                html.Li([html.B("INSTÂNCIA: ", style={'font-weight': 'bold'}), f"{df_aux['Instância']}"]),
                                html.Li([html.B("FASE: ", style={'font-weight': 'bold'}), f"{df_aux['Fase']}"]),
                                html.Li([html.B("DESCRIÇÃO: ", style={'font-weight': 'bold'}), f"{df_aux['Descrição']}"]),
                            ]),
                        ])
                    ])
                ], sm=12, md=6, style={'border-right': '2px solid lightgrey'}),
                dbc.Col([
                    dbc.Row([
                        dbc.Col([
                            html.Ul([
                                html.Li([html.B("CLIENTE: ", style={'font-weight': 'bold'}), f"{df_aux['Cliente']}"]),
                                html.Li([html.B("EMPRESA: ", style={'font-weight': 'bold'}), f"{df_aux['Empresa']}"]),
                                html.Li([html.B("ADVOGADO: ", style={'font-weight': 'bold'}), f"{df_aux['Advogados']}"])
                            ]),
                        ])
                    ], style={'margin-bottom': '32px'}),
                    dbc.Row([
                        dbc.Col([
                            html.H5("STATUS", style={'margin-bottom': 0}),
                        ], sm=5, style={'text-align': 'right'}),
                        dbc.Col([
                            html.I(className=f'{concluido} fa-2x dbc', style={'color': f'{color_c}'}),
                        ], sm=2),
                        dbc.Col([
                            html.H5(f"{concluido_text}", style={'margin-bottom': 0}),
                        ], sm=5, style={'text-align': 'left'}),
                    ], style={'display': 'flex', 'align-items': 'center', 'justify-content': 'center'}),
                    
                    dbc.Row([
                        dbc.Col([
                            html.H5("RESULTADO", style={'margin-bottom': 0})
                        ], sm=5, style={'text-align': 'right'}),
                        dbc.Col([
                            html.I(className=f'{vencido} fa-2x dbc', style={'color': f'{color_v}'})
                        ], sm=2),
                        dbc.Col([
                            html.H5(f'{vencido_text}', style={'margin-bottom': 0})
                        ], sm=5, style={'text-align': 'left'}),
                    ], style={'display': 'flex', 'align-items': 'center', 'justify-content': 'center'}),
                    html.Br(),
                    dbc.Row([
                        dbc.Col([ #TODO REMOVER BOTÃO FAN
                            dbc.Button(["Botão fantasma, para solucionar o callback"], id={'type': 'ghost_processo', 'index': int(df_aux['No Processo'])}, style={'display': 'none'}),
                        ], md=2),
                        dbc.Col([
                          dbc.Button([html.I(className = "fa fa-pencil fa-2x")], style={'color': 'black'}, size='sm', outline=True,
                                id={'type': 'editar_processo', 'index': int(df_aux['No Processo'])})
                        ], md=2),
                        dbc.Col([
                            dbc.Button([html.I(className = "fa fa-trash fa-2x")], style={'color': 'black'}, size='sm', outline=True,
                                id={'type': 'deletar_processo', 'index': int(df_aux['No Processo'])})
                        ], md=2)
                    ], style={'display': 'flex', 'justify-content': 'flex-end'})
                ], sm=12, md=6, style={'height': '100%', 'margin-top': 'auto', 'margin-bottom': 'auto'}),
            ], style={'margin-top': '12px'})
        ])
    ], style=card_style, className='card_padrao')
    return card_processo


# ========= Layout ========= #
layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.H3("ENCONTRE O PROCESSO QUE VOCÊ PROCURA", style={'text-align': 'left', 'margin-left': '32px'})
        ], className='text-center')
    ], style={'margin-top': '14px'}),
    html.Hr(),
    dbc.Row([
        # Filtros
        dbc.Col([
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            dbc.Row([
                                dbc.Col([
                                    html.H3("Nº DO PROCESSO")
                                ], sm=12)
                            ]),
                            dbc.Row([
                                dbc.Col([
                                    dbc.Input(id='processos_filter', placeholder="Insira...", type="number")
                                ], sm=12, md=12, lg=8),
                                dbc.Col([
                                    dbc.Button([html.I(className='fa fa-search')], id="pesquisar_num_proc", color='dark')
                                ], sm=12, md=12, lg=4)
                            ], style={'margin-bottom': '32px'}),
                            dbc.Row([
                                dbc.Col([
                                    html.H3("STATUS")
                                ])
                            ], style={'margin-top': '32px'}),
                            dbc.Row([
                                dbc.Col([
                                    dbc.Checklist(
                                        options=[{"label": "Concluídos", "value": 1}, {"label": "Vencidos", "value": 2}],
                                        value=[],
                                        id="switches_input",
                                        switch=True,
                                    ),
                                ])
                            ]),
                            dbc.Row([
                                dbc.Col([
                                    html.H3("INSTÂNCIA")
                                ])
                            ], style={'margin-top': '24px'}),
                            dbc.Row([
                                dbc.Col([
                                    dbc.Checklist(
                                        options=[{"label": "1a Instância", "value": 1}, 
                                                {"label": "2a Instância", "value": 2}],
                                        value=[1, 2],
                                        id="checklist_input"
                                    ),
                                ])
                            ]),
                            dbc.Row([
                                dbc.Col([
                                    html.H3("CPF DO CLIENTE")
                                ])
                            ], style={'margin-top': '24px'}),
                            dbc.Row([
                                dbc.Col([
                                    dbc.Button([html.I(className='fa fa-search')], id="pesquisar_cpf", color='light')
                                ], sm=2),
                                dbc.Col([
                                    dbc.Input(id="input_cpf_pesquisa", placeholder="DIGITE O CPF", type="number")
                                ], sm=10)
                            ]),
                            dbc.Row([
                                dbc.Col([
                                    html.H3("ADVOGADO")
                                ])
                            ], style={'margin-top': '24px'}),
                            dbc.Row([
                                dbc.Col([
                                    dcc.Dropdown(
                                        id='advogados_filter',
                                        options=[{'label': i, 'value': i} for i in df_adv['Advogado']],
                                        placeholder='SELECIONE O ADVOGADO',
                                        className='dbc'
                                    ),
                                ])
                            ]),
                            dbc.Row([
                                dbc.Col([
                                    dbc.Button("Todos os Processos", id="todos_processos", style={'width': '100%'}, color="dark")
                                ])
                            ], style={'margin-top': '24px'})
                        ], style={'margin': '20px'})
                    ])
                ])
            ])
        ], sm=12, md=5, lg=4),
        dbc.Col([
            dbc.Container(id='card_generator', fluid=True, style={'width': '100%', 'padding': '0px 0px 0px 0px', 'margin': '0px 0px 0px 0px'}),
            html.Div(id='div_fant')
        ], sm=12, md=7, lg=8, style={'padding-left': '0px'})
    ])

], fluid=True, style={'height': '100%', 'padding': '10px', 'margin': 0, 'padding-left': 0})


# ======= Callbacks ======== #
# Callback pra atualizar o dropdown de advogados
@app.callback(
    Output('advogados_filter', 'options'),
    Input('store_adv', 'data')
)
def atu(data):
    df = pd.DataFrame(data)
    return [{'label': i, 'value': i} for i in df['Advogado']]

# Callback pra atualizar o dropdown de clientes
@app.callback(
    Output('clientes_filter', 'options'),
    Input('store_proc', 'data')
)
def atu(data):
    df = pd.DataFrame(data)
    return [{'label': i, 'value': i} for i in df['Cliente'].unique()]

# Callback pra atualizar o dropdown de processos
@app.callback(
    Output('processos_filter', 'options'),
    Input('store_proc', 'data')
)
def atu(data):
    df = pd.DataFrame(data)
    return [{'label': i, 'value': i} for i in df['No Processo']]

# Callback pra gerar o conteudo dos cards
@app.callback(
    Output('card_generator', 'children'),
    Output('advogados_filter', 'value'),
    Output('processos_filter', 'value'),
    Output('input_cpf_pesquisa', 'value'),
    Input('pesquisar_cpf', 'n_clicks'),
    Input('todos_processos', 'n_clicks'),
    Input('advogados_filter', 'value'),
    Input('pesquisar_num_proc', 'n_clicks'),
    Input('store_proc', 'data'),
    Input('store_adv', 'data'),
    Input('switches_input', 'value'),
    Input('checklist_input', 'value'),
    State('processos_filter', 'value'),
    State('input_cpf_pesquisa', 'value')
)
def generate_cards(n, n_all, adv_filter, proc_button, proc_data, adv_data, switches, checklist, proc_filter, cpf):
    trigg_id = callback_context.triggered[0]['prop_id'].split('.')[0]

    # Iniciando os cards vazios
    cards = []

    # Iniciando os dataframes possíveis
    df_adv_aux = pd.DataFrame(adv_data)
    df_proc_aux = pd.DataFrame(proc_data)
        
    # Caso default - Todos os casos por ordem de data   
    if (trigg_id == '' or trigg_id == 'store_proc' or trigg_id == 'store_adv' or trigg_id == 'todos_processos' or trigg_id == 'switches_input' or trigg_id == 'checklist_input'):
        if trigg_id != 'todos_processos':
            # Filtrando pelos switches
            if (1 and 2) in switches:
                df_proc_aux = df_proc_aux.loc[(df_proc_aux['Processo Concluído'] == 1) & (df_proc_aux['Processo Vencido'] == 1)]
            elif switches == [1]: df_proc_aux = df_proc_aux.loc[df_proc_aux['Processo Concluído'] == 1]
            elif switches == [2]: df_proc_aux = df_proc_aux.loc[df_proc_aux['Processo Vencido'] == 1]
                

            if (1 in checklist) and (2 in checklist): pass
            elif checklist == [1]: df_proc_aux = df_proc_aux.loc[df_proc_aux['Instância'] == 1]
            elif checklist == [2]: df_proc_aux = df_proc_aux.loc[df_proc_aux['Instância'] == 2]
            
        df_proc_aux = df_proc_aux.sort_values(by='Data Inicial', ascending=False)

        df_proc_aux.loc[df_proc_aux['Processo Concluído'] == 0, 'Processo Concluído'] = 'Não'
        df_proc_aux.loc[df_proc_aux['Processo Concluído'] == 1, 'Processo Concluído'] = 'Sim'
        df_proc_aux.loc[df_proc_aux['Processo Vencido'] == 0, 'Processo Vencido'] = 'Não'
        df_proc_aux.loc[df_proc_aux['Processo Vencido'] == 1, 'Processo Vencido'] = 'Sim'
        
        df_proc_aux = df_proc_aux.fillna('-')

        # Inserido o card padrão com a quantidade de processos
        qnt_procs = len(df_proc_aux)
        cards += [gerar_card_padrao(qnt_procs)]
        
        # Iterando sobre os processos
        for i in range(len(df_proc_aux)):
            df_aux, concluido, vencido, color_c, color_v, concluido_text, vencido_text = gerar_icones(df_proc_aux, i)
            card = gerar_card_processo(df_aux, color_c, color_v, concluido, vencido, concluido_text, vencido_text)
            cards += [card]
        
        return cards, None, None, None

    # Pesquisa de texto por número de processo
    elif (trigg_id == 'pesquisar_num_proc'):
        # Dados
        df_proc_aux = df_proc_aux.loc[df_proc_aux['No Processo'] == proc_filter].sort_values(by='Data Inicial', ascending=False)
        if len(df_proc_aux) == 0:
            cards += [gerar_card_padrao(len(df_proc_aux))]
            return cards, None, proc_filter, None

        # Processos
        df_proc_aux = df_proc_aux.sort_values(by='Data Inicial', ascending=False)
        df_proc_aux.loc[df_proc_aux['Processo Concluído'] == 0, 'Processo Concluído'] = 'Não'
        df_proc_aux.loc[df_proc_aux['Processo Concluído'] == 1, 'Processo Concluído'] = 'Sim'
        df_proc_aux.loc[df_proc_aux['Processo Vencido'] == 0, 'Processo Vencido'] = 'Não'
        df_proc_aux.loc[df_proc_aux['Processo Vencido'] == 1, 'Processo Vencido'] = 'Sim'

        df_proc_aux = df_proc_aux.fillna('-')

        # Inserido o card padrão com a quantidade de processos
        qnt_procs = len(df_proc_aux)
        cards += [gerar_card_padrao(qnt_procs)]

        # Iterando sobre os processos possíveis
        for i in range(len(df_proc_aux)):
            df_aux, concluido, vencido, color_c, color_v, concluido_text, vencido_text = gerar_icones(df_proc_aux, i)
            card = gerar_card_processo(df_aux, color_c, color_v, concluido, vencido, concluido_text, vencido_text)
            cards += [card]

        return cards, None, proc_filter, None

    # Pesquisa de cliente por CPF
    elif trigg_id == 'pesquisar_cpf':
        if cpf in df_proc['Cpf Cliente'].values:

            # Dados
            df_proc_aux = df_proc_aux.loc[df_proc_aux['Cpf Cliente'] == cpf].sort_values(by='Data Inicial', ascending=False)
            nome = df_proc_aux.iloc[0]['Cliente']

            # Card do Cliente
            card_cliente = dbc.Card([
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col([
                            html.H4(f"Cliente: {nome}"),
                            html.Hr(),
                            html.H4(f"CPF: {cpf}"),
                        ]),
                    ])
                ])
            ], style=card_style)
            cards += [card_cliente]

            # Processos
            df_proc_aux = df_proc_aux.sort_values(by='Data Inicial', ascending=False)
            df_proc_aux.loc[df_proc_aux['Processo Concluído'] == 0, 'Processo Concluído'] = 'Não'
            df_proc_aux.loc[df_proc_aux['Processo Concluído'] == 1, 'Processo Concluído'] = 'Sim'
            df_proc_aux.loc[df_proc_aux['Processo Vencido'] == 0, 'Processo Vencido'] = 'Não'
            df_proc_aux.loc[df_proc_aux['Processo Vencido'] == 1, 'Processo Vencido'] = 'Sim'

            df_proc_aux = df_proc_aux.fillna('-')

            # Inserido o card padrão com a quantidade de processos
            qnt_procs = len(df_proc_aux)
            cards += [gerar_card_padrao(qnt_procs)]

            # Iterando sobre os processos
            for i in range(len(df_proc_aux)):
                df_aux, concluido, vencido, color_c, color_v, concluido_text, vencido_text = gerar_icones(df_proc_aux, i)
                card = gerar_card_processo(df_aux, color_c, color_v, concluido, vencido, concluido_text, vencido_text)
                cards += [card]

            return cards, None, None, cpf
        else:
            card = dbc.Card([
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col([
                            html.I(className='fa fa-exclamation dbc', style={'font-size': '4em'})
                        ], sm=3, className='text-center'),
                        dbc.Col([
                            html.H1("Nenhum CPF correspondente no banco de dados.")
                        ], sm=9)
                    ])
                ])
            ], style=card_style)
            cards += [card]
            return cards, None, None, cpf
    
    # Filtro DROPDOWN de advogados
    elif (trigg_id == 'advogados_filter'):
        # Dados
        df_aux = df_adv_aux.loc[df_adv_aux['Advogado'] == adv_filter]
        nome = df_aux.iloc[0]['Advogado']
        oab = df_aux.iloc[0]['OAB']
        cpf = df_aux.iloc[0]['CPF']
        
        # Card do Advogado
        card_adv = dbc.Card([
            dbc.CardBody([
                dbc.Row([
                    dbc.Col([
                        html.H4(f"Advogado: {nome}"),
                        html.Hr(),
                        html.H4(f"OAB: {oab}"),
                        html.H4(f"CPF: {cpf}"),
                    ]),
                ])
            ])
        ], style=card_style)
        cards += [card_adv]

        # Processos
        df_proc_aux = df_proc_aux[df_proc_aux['Advogados'] == nome]
        df_proc_aux = df_proc_aux.sort_values(by='Data Inicial', ascending=False)
        df_proc_aux.loc[df_proc_aux['Processo Concluído'] == 0, 'Processo Concluído'] = 'Não'
        df_proc_aux.loc[df_proc_aux['Processo Concluído'] == 1, 'Processo Concluído'] = 'Sim'
        df_proc_aux.loc[df_proc_aux['Processo Vencido'] == 0, 'Processo Vencido'] = 'Não'
        df_proc_aux.loc[df_proc_aux['Processo Vencido'] == 1, 'Processo Vencido'] = 'Sim'

        df_proc_aux = df_proc_aux.fillna('-')

        # Inserido o card padrão com a quantidade de processos
        qnt_procs = len(df_proc_aux)
        cards += [gerar_card_padrao(qnt_procs)]

        # Iterando sobre os processos
        for i in range(len(df_proc_aux)):
            df_aux, concluido, vencido, color_c, color_v, concluido_text, vencido_text = gerar_icones(df_proc_aux, i)
            card = gerar_card_processo(df_aux, color_c, color_v, concluido, vencido, concluido_text, vencido_text)
            cards += [card]
        return cards, adv_filter, None, None
