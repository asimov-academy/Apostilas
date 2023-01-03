import dash
from dash import html, dcc, Input, Output, State
import dash_bootstrap_components as dbc
import pandas as pd
import sqlite3

# import from folders
from app import *
from components import home, sidebar
from sql_beta import df_proc, df_adv

# Criar estrutura para Store intermediária ==============
data_int = {
        'No Processo': [], 
        'Empresa': [],
        'Tipo': [],
        'Ação': [],
        'Vara': [],
        'Fase': [],
        'Instância': [],
        'Data Inicial': [],
        'Data Final': [],
        'Processo Concluído': [],
        'Processo Vencido': [],
        'Advogados': [],
        'Cliente': [],
        'Cpf Cliente': [],
        'Descrição': [],
        'disabled': []
    }

store_int = pd.DataFrame(data_int)


# =========  Layout  =========== #
app.layout = dbc.Container(children=[
    # Store e Location 
    dcc.Location(id="url"),
    dcc.Store(id='store_intermedio', data=store_int.to_dict()),
    dcc.Store(id='store_adv', data=df_adv.to_dict(), storage_type='session'),
    dcc.Store(id='store_proc', data=df_proc.to_dict()),
    html.Div(id='div_fantasma', children=[]),
    # Layout
    dbc.Row([
        dbc.Col([
            sidebar.layout
        ], md=2, style={'padding': '0px'}),

        dbc.Col([
            dbc.Container(id="page-content", fluid=True, style={'height': '100%', 'width': '100%', 'padding-left': '14px'}) 
        ], md=10, style={'padding': '0px'}),
    ])
], fluid=True)


# ======= Callbacks ======== #
# URL callback to update page content
@app.callback(Output('page-content', 'children'), Input('url', 'pathname'))
def render_page_content(pathname):
    if pathname == '/home' or pathname == '/':
        return home.layout
    return dbc.Container([
            html.H1("404: Not found", className="text-danger"),
            html.Hr(),
            html.P(f"O caminho '{pathname}' não foi reconhecido..."),
            html.P("Use a NavBar para retornar ao sistema de maneira correta.")
        ])

# Dcc.Store back to file
@app.callback(
    Output('div_fantasma', 'children'),
    Input('store_adv', 'data'),
    Input('store_proc', 'data'),
)
def update_file(adv_data, proc_data):
    df_adv_aux = pd.DataFrame(adv_data)
    df_proc_aux = pd.DataFrame(proc_data)

    conn = sqlite3.connect('sistema.db')

    df_proc_aux.to_sql('processos', conn, if_exists='replace', index=False)
    # conn.commit()
    df_adv_aux.to_sql('advogados', conn, if_exists='replace', index=False)
    conn.commit()

    conn.close()
    return []


if __name__ == '__main__':
    app.run_server(debug=True)
