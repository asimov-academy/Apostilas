from dash import html, dcc
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import pandas as pd
import numpy as np
import dash
from app import *

from pages import page1, page2
import sidebar
 

# =========  Layout  =========== #

app.layout = html.Div(children=[
                dbc.Row([
                        dbc.Col([
                            dcc.Location(id="url"), 
                            sidebar.layout
                        ], md=2),

                        dbc.Col([
                            html.Div(id="page-content")
                        ]),
                    ])
            ], style={"padding": "0px"})


@app.callback(Output("page-content", "children"), [Input("url", "pathname")])
def render_page_content(pathname):
    if pathname == "/":
        return page1.layout
    
    if pathname == "/page2":
        return page2.layout


if __name__ == "__main__":
    app.run_server(port=8050, debug=True)