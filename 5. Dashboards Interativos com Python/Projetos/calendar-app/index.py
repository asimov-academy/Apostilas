import dash
from dash import Dash, Input, Output

import dash_bootstrap_components as dbc
from dash import html, dcc

import pandas as pd
import datetime
import json
import os

# from app import app
from app import *




# =========  Layout  =========== #
app.layout = dbc.Container([

        dcc.Location(id="url"),

        dbc.Row([

        ])
], fluid=True)



# =========  Callback  =========== #




if __name__ == "__main__":
    app.run_server(debug=True, port=8051)