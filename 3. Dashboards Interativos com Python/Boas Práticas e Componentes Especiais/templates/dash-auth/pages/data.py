from dash import html, dcc
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
from app import *

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash_bootstrap_templates import load_figure_template

from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, current_user
from dash.exceptions import PreventUpdate

load_figure_template(["quartz"])
card_style = {
    'width': '800px',
    'min-height': '300px',
    'padding-top': '25px',
    'padding-right': '25px',
    'padding-left': '25px',
}

df = pd.DataFrame(np.random.randn(100, 1), columns=["data"])
fig = px.line(df, x=df.index, y="data", template="quartz")


# =========  Layout  =========== #
def render_layout(username):
    template = html.Div([
            dbc.Card([
                dcc.Location(id="data-url"), 
                html.Legend("Olá, {}!".format(username)),
                dcc.Graph(figure=fig),

                html.Div([
                    dbc.Button("Logout", id="logout_button"),
                ], style={"padding": "20px", "justify-content": "end", "display": "flex"})

            ], style=card_style, className="align-self-center")
        ], className="col d-flex justify-content-center", style={"height": "100vh", "vertical-align": "middle"})
    return template 


# =========  Callbacks Page1  =========== #
@app.callback(
    Output('data-url', 'pathname'),
    Input('logout_button', 'n_clicks'),
    )
def successful(n_clicks):
    if n_clicks == None:
        raise PreventUpdate
    
    if current_user.is_authenticated:
        logout_user()
        return '/login'
    else: 
        return '/login'

