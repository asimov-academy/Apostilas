import dash
from dash import Dash, Input, Output, State, callback_context
import dash_bootstrap_components as dbc
from dash.dependencies import ALL
from dash import html, dcc

import pandas as pd
import datetime
import json
import os
from dash_table import DataTable
import calendar

# from app import app
from app import *
import pdb


meses = ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho', 'Julho',
        'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']

df = pd.DataFrame({
    ("SEG"): [None]*6,
    ("TER"): [None]*6,
    ("QUA"): [None]*6,
    ("QUI"): [None]*6,
    ("SEX"): [None]*6,
    ("SAB"): [None]*6,
    ("DOM"): [None]*6,
})


y = datetime.datetime.today().year
m = datetime.datetime.today().month
h = datetime.datetime.today().day

anos_ = [(y+28) - i for i in range(51)]
anos = list(reversed(anos_))


def get_calendar(y, m):
    calendar_ = calendar.month(y, m)
    calendar_ = calendar_.split('\n')[2:-1]

    pos_primeiro_dia = calendar_[0].find('1')
    dict_position_to_days = {1: "SEG", 4: "TER", 7: "QUA", 10: "QUI", 
                            13: "SEX", 16: "SAB", 19:"DOM"}
    first_day = dict_position_to_days[pos_primeiro_dia]
    last_day = int(calendar_[-1].split(" ")[-1])
    return first_day, last_day


def save_file(lista_eventos):
    with open('eventos.json', 'w') as f:
        json.dump(lista_eventos, f)
if "eventos.json" in os.listdir():
    lista_de_eventos = json.load(open('eventos.json'))
else:
    lista_de_eventos = {'05/05/2005': 
                [
                    {'horario': '00:00', 'titulo': 'None', 'local': 'None', 'descricao': 'None', 'id': 0},
                ],
                'id_max': 1
            }
    save_file(lista_de_eventos)


# =========  Layout  =========== #
app.layout = dbc.Container([
        dcc.Location(id="url"),
        dcc.Store(id='month', data=m),
        dcc.Store(id='year', data=y),
        dcc.Store(id='lista-de-eventos', data=lista_de_eventos),

        dbc.Row([
            dbc.Col([
                dbc.Col([
                    dbc.Row([
                        dbc.Button('<', id='voltar',
                        style={'color' : 'black',
                        'background-color' : '#ffffff',
                        'border' : '1px solid black',
                        'border-radius' : '50%',
                        'width' : '35px',
                        'height': '35px',
                        'margin-top' : '60px',
                        'margin-left' : '280px',
                        'font-weight' : 'bold',
                        'font-size' : '20px',
                        'padding' : '0px 0px'
                        }),

                        dbc.Button('>',id='avancar',
                        style={'color' : 'black',
                        'background-color': '#ffffff',
                        'border' : '1px solid black',
                        'border-radius' : '50%',
                        'width' : '35px',
                        'height' : '35px',
                        'margin-top' : '60px',
                        'margin-left' : '160px',
                        'font-weight': 'bold',
                        'font-size' : '20px',
                        'padding' : '0px 12px'
                        }),

                        html.Div('Ano', 
                        style={'width' : 'fit-content',
                        'padding' : '0px',
                        'textAlign': 'center',
                        'margin-left' : '-160px', 
                        'margin-top' : '45px', 
                        'font-weight': 'bold',
                        'font-size' : '40px',
                        'background-color' : 'transparent'},
                        id='div-ano',
                        className='primary-font-color')
                    ]),
                    dbc.Row([
                        html.Div('Mês',
                        style={'width' : '130px',
                        'textAlign': 'center',
                        'margin-left' : '330px',
                        'margin-top' : '0px',
                        'font-weight': 'bold',
                        'font-size' : '26px',
                        'background-color' : 'transparent'},
                        id='div-mes',
                        className ='secundary-font-color')
                    ]),
                    dbc.Row([
                        DataTable(df.to_dict('records'), [{"name" : i, "id": i} for i in df.columns], id="calendar",
                        style_table={'border': '2px solid transparent',
                                    'height': '390px',
                                    'width' : '715px',
                                    'margin-top' : '20px',
                                    'margin-left' : '30px'},
                        style_cell={'height': '5.5rem'},
                        style_data={'border': '0px',  
                                    'backgroundColor': 'transparent', 
                                    'textAlign' : 'center'},
                        style_header={'border': '0px', 
                                        'color' : 'rgba(255,255,255, 0.4)',
                                        'backgroundColor': 'transparent', 
                                        'textAlign' : 'center', 
                                        'font-weight': 'bold'},
                        )

                    ], className='primary-font-color'),
                ], md=12, style={'margin-left' : '7.5px', 'margin-top' : '35px', 'border-top-left-radius': '2%',
                                    'border-bottom-left-radius' : '2%'},  className = 'primary-color'),
            ], md = 7, ),

            dbc.Col([
                dbc.Row([
                    dbc.Col([
                        html.Div(id='div-dia-mês-atual',
                        style={'margin-left' : '0px',
                                'margin-top' : '20px', 
                                'width' : 'fit-content',
                                'height' : 'fit-content',
                                'font-size': '150px',
                                'line-height': '0.85',
                                'background-color' : 'transparent'},
                                className='primary-font-color'
                        ),

                        html.Div(id='div-dia-semana-atual',
                                style={'margin-left' : '172px',
                                'margin-top' : '-30px', 
                                'width' : '140px',
                                'height' : '30px',
                                'font-size': '20px',
                                'background-color' : 'transparente'},
                                className='primary-font-color'
                        ),

                    ], md=8, className = 'secundary-color'),
                    dbc.Col([
                        html.Div("Adicionar nova tarefa",
                                style={'margin-left' : '20px',
                                'margin-top' : '48px', 
                                'width' : '80px',
                                'height' : '50px',
                                'text-align' : 'left'},
                                className='primary-font-color'
                        ),

                    dbc.Button([html.I(className = "fa fa-plus", style={'font-size' : '400%'})],
                                    id='open-modal-button',
                                    style={'width' : '40px',
                                            'height' : '40px',
                                            'margin-top' : '-77px',
                                            'margin-left' : '120px',
                                            'border-radius' : '50%'},
                                    
                        ),  

                        html.Div(id='div-data-concatenada',
                                hidden=True  
                        )
                    ], md=4, className = 'secundary-color', style={ 'border-top-right-radius' : '7%'}),
                ], style={'margin-top' : '35px', 'width' : '550px'}),
                dbc.Row([
                    dbc.Card(style = {'color' : '#000000',
                        'border-radius' : '0px',
                        'width' : '550px',
                        'height' : '413px',
                        'margin-left' : '0px',
                        'margin-top' : '0px',
                        'background-color': 'rgba(0,0,0)',
                        'border-bottom-right-radius' : '2%'},
                        id='card-geral')
                ])
            ], md = 5)

        ]),

            dbc.Modal([
                dbc.ModalHeader("Nova tarefa", style={'color' : '#ffffff', 'font-size' : '20px'}, className = 'modal-color'),

            dbc.ModalTitle(
                dbc.Input(id="titulo-input", 
                                        placeholder="Adicione um título", type="text", 
                                        style={'width' : '400px',
                                                'border-top' : 'transparent',
                                                'border-left' : 'transparent',
                                                'border-right' : 'transparent',
                                                'border-bottom' : '2px solid black',
                                                'border-radius' : '0px',
                                                'margin-left' : '10px',
                                                'font-weight': 'bold',
                                                'margin-top' : '20px',
                                                },
                                        className='input-modal-color'
                                        
                    ), className = 'modal-color'
            ),

            dbc.ModalBody([

                dbc.Input(id="horario-input", placeholder="Horário", type="text",
                            style={'width' : '76px',
                                    'margin-top' : '20px',
                                    'border' : '1px solid black'},
                            className='input-modal-color',
                            maxlength=7
                    ),

                dbc.Input(id="local-input", placeholder="Local", type="text", 
                            style={'width' : '450px',
                                    'margin-top' : '20px',
                                    'border' : '1px solid black'},
                            className='input-modal-color'
                    ),

                dbc.Input(id="descricao-input", placeholder="Descrição", type="text", 
                            style={'width' : '450px',
                                    'margin-top' : '20px',
                                    'border' : '1px solid black'},
                            className='input-modal-color'
                    ),

                html.Div(id="required-field-notification", 
                            style={'width' : '450px',
                                    'margin-top' : '20px'},
                            className ='secundary-font-color'
                    ),

                dbc.Button('Salvar',  color="light", className="me-1", id='submit-tarefa', n_clicks=0,
                            style={'margin-top' : '15px',
                                        'margin-left' : '390px',
                                        'font-weight': 'bold',
                                        'font-size' : '16px',}
                    )
            ], className = 'modal-color'),


            ],style={'color' : '#000000',
                    'background-color' : 'rgba(255, 255, 255, 0.4)'},
                    id="modal-tarefa",
                    is_open=False
            ),


], fluid=True, style={"display" : "flex", "justify-content" : "center"})



# =========  Callback  =========== #

@app.callback(
    Output('modal-tarefa', 'is_open'),

    Input('open-modal-button', 'n_clicks'),
    Input('submit-tarefa', 'n_clicks'),

    State('modal-tarefa', 'is_open'),
    State('horario-input', 'value'),
    prevent_initial_call=True
)
def toggle_modal(n1, n2, is_open, horario):
    changed_id = [p['prop_id'] for p in callback_context.triggered][0]

    if changed_id.split('.')[0] == 'open-modal-button':
        return not is_open

    if changed_id.split('.')[0] == 'submit-tarefa' and horario:
        return not is_open
    return is_open


@app.callback(
    Output('calendar', 'data'),
    Output('calendar', 'active_cell'),
    Output('month', 'data'),
    Output('year', 'data'),
    Output('div-mes', 'children'),
    Output('div-ano', 'children'),

    Input('avancar', 'n_clicks'),
    Input('voltar', 'n_clicks'),

    State('month', 'data'),
    State('year', 'data')
)
def render_calendar_content(botao_avanca, botao_volta, mm, yy):
    changed_id = callback_context.triggered[0]['prop_id'].split('.')[0]

    if botao_avanca != None or botao_volta != None:

        if 'avancar' in changed_id:
            mm += 1
            if mm > 12:
                mm = 1
                yy += 1

        elif 'voltar' in changed_id:
            mm -= 1
            if mm < 1:
                mm = 12
                yy -= 1

    day, last_day = get_calendar(yy, mm)
    empty_dict = df.to_dict('records')
    days_of_week = ['SEG', 'TER', 'QUA', 'QUI', 'SEX', 'SAB', 'DOM']
    c = 0

    for d in range(1, last_day+1):
        empty_dict[c][day] = d

        if d == h and meses[m-1] == meses[mm-1] and y == anos[yy-2000]:
            initial_active_cell = {'row': c, 'column' : (days_of_week.index(day)), 'column_id' : day, 'row_id' : c}
            
        elif meses[m-1] != meses[mm-1] or y != anos[yy-2000]:
            if d == 1:
                initial_active_cell = {'row': c, 'column' : (days_of_week.index(day)), 'column_id' : day, 'row_id' : c}

        day = 'SEG' if days_of_week.index(day) == 6 else days_of_week[days_of_week.index(day) + 1]
        if day == 'SEG':
            c += 1

    return empty_dict, initial_active_cell, mm, yy, meses[mm-1], yy


@app.callback(
    Output('lista-de-eventos', 'data'),
    Output('required-field-notification', 'children'),
    Output('horario-input', 'value'),
    Output('titulo-input', 'value'),
    Output('local-input', 'value'),
    Output('descricao-input', 'value'),

    Input('submit-tarefa', 'n_clicks'),
    Input({'type': 'delete_event', 'index': ALL}, 'n_clicks'),

    State('div-data-concatenada', 'children'),
    State('horario-input', 'value'),
    State('titulo-input', 'value'),
    State('local-input', 'value'),
    State('descricao-input', 'value'),
    State('lista-de-eventos', 'data')
)
def update_lista_eventos(n_clicks, n_clicks2, data_conc, horario, titulo, local, descricao, lista_de_eventos):

    changed_id = [p['prop_id'] for p in callback_context.triggered][0]
    if 'submit-tarefa' in changed_id:
        if not horario:
            notificacao = 'Insira um horário válido'
            return lista_de_eventos, notificacao, horario, titulo, local, descricao
        else:
            if data_conc not in lista_de_eventos:
                lista_de_eventos[data_conc] = []
            lista_de_eventos[data_conc].append({'horario' : horario, 'titulo' : titulo,
                                                    'local' : local, 'descricao' : descricao,
                                                    'id' : lista_de_eventos['id_max']}
                                                        )
            lista_de_eventos['id_max'] += 1

    if 'delete_event' in changed_id and any(n_clicks2):
        dict_id = json.loads(changed_id.split(".")[0])
        idx = dict_id["index"]
        lista_de_eventos[data_conc] = [i for i in lista_de_eventos[data_conc] if i["id"] != idx]
    
    horario = None
    titulo = None
    local = None
    descricao = None
    notificacao = ''

    save_file(lista_de_eventos)
    return lista_de_eventos, notificacao, horario, titulo, local, descricao


@app.callback(
    Output('div-data-concatenada', 'children'),
    Output('div-dia-semana-atual', 'children'),
    Output('div-dia-mês-atual', 'children'),
    Output('card-geral', 'children'),

    Input('calendar', 'active_cell'),
    Input('lista-de-eventos', 'data'),

    State('calendar', 'data'), 
    State('div-mes', 'children'),
    State('div-ano', 'children'),
    prevent_initial_call=True
)
def update_card_geral(active_cell, lista_de_eventos, calendar_data, mes, ano):  

    dia = calendar_data[active_cell['row']][active_cell['column_id']]
    mes = meses.index(mes) + 1

    if dia == None:
        dia = 1
    
    data_conc = '{:02d}/{:02d}/{:02d}'.format(dia, mes, ano)

    col = active_cell['column_id']    
    if col == 'SEG':
        col = 'Segunda-Feira'
    elif col == 'TER':
        col = 'Terça-Feira'
    elif col == 'QUA':
        col = 'Quarta-Feira'
    elif col == 'QUI':
        col = 'Quinta-Feira'
    elif col == 'SEX':
        col = 'Sexta-Feira'
    elif col == 'SAB':
        col = 'Sábado'
    elif col == 'DOM':
        col = 'Domingo'

    dia_semana_atual = col
    dia_mês_atual = data_conc[:2] 


    card_tarefa = []
    num_eventos = 0 if data_conc not in lista_de_eventos.keys() else len(lista_de_eventos[data_conc])

    if num_eventos != 0:
        lista_ordenada_de_eventos = sorted(lista_de_eventos[data_conc], key=lambda d: d['horario']) 
    
    if num_eventos == 0:
        card_tarefa = dbc.Card(
            [
                dbc.Row(
                    [
                    html.H3('Não há eventos nessa data')
                    ],
                    className="g-0 d-flex align-items-center",
                    style={'margin-top' : '45px'}
                )
            ],
            className="mb-3",
            style={"maxWidth": "540px",
                    'background-color' : '#000000'},
            id='card-tarefa'
        )

    for i in range(num_eventos):
        new_card = dbc.Card([
            dbc.Row([
                dbc.Col(html.H4(lista_ordenada_de_eventos[i]['horario'],
                            style={'font-weight' : 'bold',
                                    'text-align' : 'center',
                                    'font-size' : '16px'}),),

                dbc.Col(
                    dbc.CardBody(
                                [
                                    html.H4(lista_ordenada_de_eventos[i]['titulo'],
                                    style={'font-weight' : 'bold',
                                            'margin-top' : '-10px',
                                            'font-size' : '16px'}),
                                    html.P(lista_ordenada_de_eventos[i]['local'],
                                    style={'margin-top' : '-4px',
                                            'font-size' : '12px',
                                            'color' : 'gray'}),
                                    html.P(lista_ordenada_de_eventos[i]['descricao'])
                                ]
                            ),
                            md=9
                ),

                dbc.Col(
                    dbc.Button([html.I(className = "fa fa-trash", 
                                                style={'font-size' : '200%'})],
                                    id={
                                        'type': 'delete_event',
                                        'index': lista_ordenada_de_eventos[i]['id']
                                    }     
                            ), 
                            className="col-md-1",
                ),
            ], 
            className="g-0 d-flex align-items-center",
                    style={'border-bottom': '1px solid white',}
            )
        ], className="mb-3",
            style={"maxWidth": "540px",
                    'background-color' : '#000000'},)
        card_tarefa+= [new_card]

    return data_conc, dia_semana_atual, dia_mês_atual, card_tarefa


if __name__ == "__main__":
    app.run_server(debug=False, port=8051)