from app import *

import dash
from dash import dcc, html
import dash_bootstrap_components as dbc


component1 = dbc.Card([
    html.H5("Fui gerado pelo componente 1", style={"padding": "20px"})
], style={"margin": "20px"})


# Callbacks