import dash
from dash import html, dcc
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
import pandas as pd

from dash import dash_table
from dash.dash_table.Format import Group

from app import app
from components import home

# ======== Layout ========= #
layout = dbc.Modal([])
            


# ====== Callbacks ======= #
# Tabela com os advogados da empresa

