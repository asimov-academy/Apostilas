import dash
import plotly.express as px
from dash import html, dcc, callback_context
from dash.dependencies import Input, Output, State, ALL
import dash_bootstrap_components as dbc

import json
import pandas as pd

from components import modal_novo_processo, modal_novo_advogado, modal_advogados
from app import app

# ========= Layout ========= #
layout = dbc.Container([
        modal_novo_processo.layout,
        modal_novo_advogado.layout,
        modal_advogados.layout,
        dbc.Container([
            dbc.Row([
                dbc.Col([
                    html.H1("ASIMOV", style={'color': 'yellow'})#, 'font-size': 'width / 1.2'})
                ])
            ]),
            dbc.Row([
                dbc.Col([
                    html.H3("ASSOCIATES", style={'color': 'white'})
                ]),
            ]),
        ], style={'padding-top': '50px', 'margin-bottom': '100px'}, className='text-center'),
        html.Hr(),
        dbc.Row([
            dbc.Col([
                dbc.Nav([
                    dbc.NavItem(dbc.NavLink([html.I(className='fa fa-home dbc'), "\tINÍCIO"], href="/home", active=True, style={'text-align': 'left'})),
                    html.Br(),
                    dbc.NavItem(dbc.NavLink([html.I(className='fa fa-plus-circle dbc'), "\tPROCESSOS"], id='processo_button', active=True, style={'text-align': 'left'})),
                    html.Br(),
                    dbc.NavItem(dbc.NavLink([html.I(className='fa fa-user-plus dbc'), "\tADVOGADOS"], id='lawyers_button', active=True, style={'text-align': 'left'})),
                ], vertical="lg", pills=True, fill=True)
            ])
        ]),
], style={'height': '100vh', 'padding': '0px', 'position':'sticky', 'top': 0, 'background-color': '#232423'})
    

# ======= Callbacks ======== #
# Abrir Modal New Lawyer
@app.callback(
    Output('modal_new_lawyer', "is_open"),
    Input('new_adv_button', 'n_clicks'),
    Input("cancel_button_novo_advogado", 'n_clicks'),
    State('modal_new_lawyer', "is_open")
)
def toggle_modal(n, n2, is_open):
    if n or n2:
        return not is_open
    return is_open

# Abrir Modal Lawyers
@app.callback(
    Output('modal_lawyers', "is_open"),
    Input('lawyers_button', 'n_clicks'),
    Input('quit_button', 'n_clicks'),
    Input('new_adv_button', 'n_clicks'),
    State('modal_lawyers', "is_open")
)
def toggle_modal(n, n2, n3, is_open):
    if n or n2 or n3:
        return not is_open
    return is_open
